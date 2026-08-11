"""Banking product and product-review API routes."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import desc, tuple_
from sqlalchemy.orm import Session, selectinload

from . import config
from .common import body, get_or_404, model_data
from .database import get_db
from .external import get_json
from .models import (
    DepositBase, DepositOption, ProductReview, ReviewComment, SavingBase,
    SavingOption, User,
)
from .security import current_user


router = APIRouter(prefix="/bankings", tags=["bankings"])


def product_data(product) -> dict:
    result = model_data(product)
    key = "deposit_options" if isinstance(product, DepositBase) else "saving_options"
    result[key] = [model_data(option) for option in product.options]
    return result


def fetch_product_data(
    db: Session, product_model, option_model, endpoint: str, params: dict[str, str]
) -> None:
    """Upsert one Finlife response without issuing a query per row."""
    result = get_json(endpoint, params=params).get("result", {})
    bases = result.get("baseList", [])
    options = result.get("optionList", [])
    product_keys = {
        (item.get("fin_co_no"), item.get("fin_prdt_cd"))
        for item in bases
        if item.get("fin_co_no") and item.get("fin_prdt_cd")
    }
    existing_products = (
        db.query(product_model)
        .filter(tuple_(product_model.fin_co_no, product_model.fin_prdt_cd).in_(product_keys))
        .all()
        if product_keys else []
    )
    products = {
        (item.fin_co_no, item.fin_prdt_cd): item for item in existing_products
    }

    for base in bases:
        key = (base.get("fin_co_no"), base.get("fin_prdt_cd"))
        if not all(key):
            continue
        item = products.get(key)
        values = {
            key: base.get(key)
            for key in (
                "dcls_month", "kor_co_nm", "fin_prdt_nm", "join_way", "mtrt_int",
                "spcl_cnd", "join_deny", "join_member", "etc_note", "max_limit",
                "dcls_strt_day", "dcls_end_day", "fin_co_subm_day",
            )
        }
        if item:
            for key, value in values.items():
                setattr(item, key, value)
        else:
            item = product_model(fin_co_no=key[0], fin_prdt_cd=key[1], **values)
            db.add(item)
            products[key] = item
    db.flush()

    product_ids = [item.id for item in products.values()]
    existing_options = (
        db.query(option_model).filter(option_model.product_id.in_(product_ids)).all()
        if product_ids else []
    )
    option_by_key = {(item.product_id, item.save_trm): item for item in existing_options}
    for option in options:
        product = products.get((option.get("fin_co_no"), option.get("fin_prdt_cd")))
        if not product:
            continue
        save_trm = option.get("save_trm")
        if save_trm is None:
            continue
        item = option_by_key.get((product.id, save_trm))
        values = {
            key: option.get(key)
            for key in ("dcls_month", "intr_rate_type", "intr_rate_type_nm", "save_trm")
        }
        values["intr_rate"] = option.get("intr_rate") or 0
        values["intr_rate2"] = option.get("intr_rate2") or 0
        if item:
            for key, value in values.items():
                setattr(item, key, value)
        else:
            db.add(option_model(product_id=product.id, **values))
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


@router.get("/deposit-fetch-data/")
def deposit_fetch_data(db: Session = Depends(get_db)):
    if not config.BANKINGS_KEY:
        raise HTTPException(503, "BANKINGS_KEY is not configured.")
    fetch_product_data(
        db, DepositBase, DepositOption,
        "https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json",
        {"auth": config.BANKINGS_KEY, "topFinGrpNo": "020000", "pageNo": "1"},
    )
    return {"message": "Data fetched and stored successfully."}


@router.get("/deposit-get-products/")
def deposit_get_products(db: Session = Depends(get_db)):
    products = db.query(DepositBase).options(selectinload(DepositBase.options)).all()
    return [product_data(item) for item in products]


@router.get("/saving-fetch-data/")
def saving_fetch_data(db: Session = Depends(get_db)):
    if not config.BANKINGS_KEY:
        raise HTTPException(503, "BANKINGS_KEY is not configured.")
    fetch_product_data(
        db, SavingBase, SavingOption,
        "https://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json",
        {"auth": config.BANKINGS_KEY, "topFinGrpNo": "020000", "pageNo": "1"},
    )
    return {"message": "Data fetched and stored successfully."}


@router.get("/saving-get-products/")
def saving_get_products(db: Session = Depends(get_db)):
    products = db.query(SavingBase).options(selectinload(SavingBase.options)).all()
    return [product_data(item) for item in products]


def review_data(review: ProductReview, user: User) -> dict:
    result = {
        field: getattr(review, field)
        for field in ("id", "product_type", "product_name", "title", "content", "rating")
    }
    result.update(
        created_at=review.created_at.isoformat(),
        updated_at=review.updated_at.isoformat(),
        username=review.user.username,
        like_count=len(review.likes),
        is_liked=any(like.id == user.id for like in review.likes),
        is_owner=review.user_id == user.id,
    )
    result["comments"] = [
        {
            "id": comment.id,
            "content": comment.content,
            "username": comment.user.username,
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat(),
            "is_owner": comment.user_id == user.id,
        }
        for comment in review.comments
    ]
    return result


@router.get("/reviews/")
def reviews(user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = db.query(ProductReview).options(
        selectinload(ProductReview.user),
        selectinload(ProductReview.likes),
        selectinload(ProductReview.comments).selectinload(ReviewComment.user),
    ).order_by(desc(ProductReview.created_at)).all()
    return [review_data(item, user) for item in data]


@router.post("/reviews/", status_code=201)
async def create_review(
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    data = await body(request)
    try:
        review = ProductReview(
            user_id=user.id,
            product_type=data["product_type"],
            product_name=data["product_name"],
            title=data["title"],
            content=data["content"],
            rating=int(data["rating"]),
        )
    except KeyError as error:
        raise HTTPException(400, {"error": f"Missing field: {error.args[0]}"}) from error
    db.add(review)
    db.commit()
    db.refresh(review)
    return review_data(review, user)


@router.put("/reviews/{review_id}/")
async def update_review(
    review_id: int,
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    review = get_or_404(db, ProductReview, review_id)
    if review.user_id != user.id:
        raise HTTPException(403)
    for field, value in (await body(request)).items():
        if field in {"product_type", "product_name", "title", "content", "rating"}:
            setattr(review, field, int(value) if field == "rating" else value)
    db.commit()
    db.refresh(review)
    return review_data(review, user)


@router.delete("/reviews/{review_id}/", status_code=204)
def delete_review(
    review_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    review = get_or_404(db, ProductReview, review_id)
    if review.user_id != user.id:
        raise HTTPException(403)
    db.delete(review)
    db.commit()
    return Response(status_code=204)


@router.post("/reviews/{review_id}/like/")
def like_review(
    review_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    review = get_or_404(db, ProductReview, review_id)
    if any(like.id == user.id for like in review.likes):
        review.likes = [like for like in review.likes if like.id != user.id]
    else:
        review.likes.append(user)
    db.commit()
    return {"likes_count": len(review.likes)}


@router.post("/reviews/{review_id}/comments/", status_code=201)
async def create_comment(
    review_id: int,
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    review = get_or_404(db, ProductReview, review_id)
    data = await body(request)
    comment = ReviewComment(
        review_id=review.id, user_id=user.id, content=data.get("content", "")
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "content": comment.content,
        "username": user.username,
        "created_at": comment.created_at.isoformat(),
        "updated_at": comment.updated_at.isoformat(),
        "is_owner": True,
    }


@router.put("/reviews/{review_id}/comments/")
async def update_comment(
    review_id: int,
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    data = await body(request)
    comment = get_or_404(db, ReviewComment, int(data.get("comment_id", 0)))
    if comment.review_id != review_id or comment.user_id != user.id:
        raise HTTPException(403)
    comment.content = data.get("content", comment.content)
    db.commit()
    return {
        "id": comment.id,
        "content": comment.content,
        "username": user.username,
        "created_at": comment.created_at.isoformat(),
        "updated_at": comment.updated_at.isoformat(),
        "is_owner": True,
    }


@router.delete("/reviews/{review_id}/comments/", status_code=204)
async def delete_comment(
    review_id: int,
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    data = await body(request)
    comment = get_or_404(db, ReviewComment, int(data.get("comment_id", 0)))
    if comment.review_id != review_id or comment.user_id != user.id:
        raise HTTPException(403)
    db.delete(comment)
    db.commit()
    return Response(status_code=204)


@router.get("/bank-products/{bank_name}/")
def bank_products(bank_name: str, db: Session = Depends(get_db)):
    deposits = db.query(DepositBase).options(
        selectinload(DepositBase.options)
    ).filter_by(kor_co_nm=bank_name).all()
    savings = db.query(SavingBase).options(
        selectinload(SavingBase.options)
    ).filter_by(kor_co_nm=bank_name).all()
    return {
        "deposit_products": [product_data(item) for item in deposits],
        "saving_products": [product_data(item) for item in savings],
    }
