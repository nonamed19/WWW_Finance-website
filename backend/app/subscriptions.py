"""Product subscription API routes."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .common import body, model_data
from .database import get_db
from .models import Subscription, User
from .security import current_user


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/subscribe/", status_code=201)
async def toggle_subscription(
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    data = await body(request)
    product_id = data.get("product_id")
    product_name = data.get("product_name")
    if not product_id or not product_name:
        raise HTTPException(400, {"error": "Product ID and name are required."})
    item = db.query(Subscription).filter_by(
        user_id=user.id, product_id=str(product_id)
    ).first()
    if item:
        db.delete(item)
        db.commit()
        return {"message": f"'{product_name}' 구독이 취소되었습니다."}
    item = Subscription(
        user_id=user.id,
        product_id=str(product_id),
        product_name=product_name,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return model_data(item)


@router.get("/my-subscriptions/")
def my_subscriptions(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    items = db.query(Subscription).filter_by(user_id=user.id).all()
    return [model_data(item, exclude=("user_id",)) for item in items]
