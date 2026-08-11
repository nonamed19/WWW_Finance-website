"""FastAPI application preserving the public API formerly served by Django REST."""
import html
import re
import shutil
from datetime import datetime
from pathlib import Path

import requests
import xmltodict
import yfinance as yf
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from sqlalchemy import desc
from sqlalchemy.orm import Session, selectinload

from . import config
from .database import Base, engine, get_db
from .models import (ApiToken, Conversation, DepositBase, DepositOption, Exchange,
                     Message, News, ProductReview, ReviewComment, SavingBase,
                     SavingOption, Stock, Subscription, User, UserSurvey)
from .security import create_token, current_user, hash_password, verify_password


app = FastAPI(title="Financial Recommendation API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/media", StaticFiles(directory=config.MEDIA_ROOT), name="media")


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def model_data(item, exclude=()):
    result = {}
    for column in item.__table__.columns:
        if column.name not in exclude:
            value = getattr(item, column.name)
            result[column.name] = value.isoformat() if isinstance(value, datetime) else float(value) if hasattr(value, "as_tuple") else value
    return result


def user_data(user: User, request: Request) -> dict:
    fields = ("id", "username", "name", "email", "age", "money", "salary", "desire_amount_deposit", "deposit_period", "desire_amount_saving", "saving_period")
    result = {field: (float(getattr(user, field)) if hasattr(getattr(user, field), "as_tuple") else getattr(user, field)) for field in fields}
    result["profile_image"] = str(request.base_url).rstrip("/") + "/media/" + user.profile_image if user.profile_image else None
    return result


async def body(request: Request) -> dict:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        return await request.json()
    form = await request.form()
    return dict(form)


def get_or_404(db: Session, model, object_id: int):
    item = db.get(model, object_id)
    if not item:
        raise HTTPException(404, "Not found.")
    return item


# Accounts -----------------------------------------------------------------
@app.post("/accounts/signup/", status_code=status.HTTP_201_CREATED)
async def signup(request: Request, db: Session = Depends(get_db)):
    data = await body(request)
    username, password1, password2 = data.get("username", ""), data.get("password1", ""), data.get("password2", "")
    if not username or not password1:
        raise HTTPException(400, "username and password are required.")
    if password1 != password2:
        raise HTTPException(400, "Passwords do not match.")
    if db.query(User).filter_by(username=username).first():
        raise HTTPException(400, {"username": ["A user with that username already exists."]})
    user = User(username=username, password=hash_password(password1), email=data.get("email", ""), name=data.get("name") or "")
    db.add(user); db.commit(); db.refresh(user)
    return {"key": create_token(db, user)}


@app.post("/accounts/login/")
async def login(request: Request, db: Session = Depends(get_db)):
    data = await body(request)
    user = db.query(User).filter_by(username=data.get("username", "")).first()
    if not user or not verify_password(data.get("password", ""), user.password):
        raise HTTPException(400, {"non_field_errors": ["Unable to log in with provided credentials."]})
    user.last_login = datetime.utcnow(); db.commit()
    return {"key": create_token(db, user)}


@app.post("/accounts/logout/", status_code=204)
def logout(user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.query(ApiToken).filter_by(user_id=user.id).delete(); db.commit()
    return Response(status_code=204)


@app.get("/accounts/user_all/")
def user_all(request: Request, db: Session = Depends(get_db)):
    return [user_data(user, request) for user in db.query(User).all()]


@app.get("/accounts/user_info/")
def user_info(request: Request, user: User = Depends(current_user)):
    return {"user_info": user_data(user, request), "message": "User information retrieved successfully."}


@app.patch("/accounts/user_update/")
async def user_update(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = await body(request)
    allowed = {"username", "name", "email", "age", "money", "salary", "desire_amount_deposit", "deposit_period", "desire_amount_saving", "saving_period"}
    for field in allowed & data.keys():
        if field in {"age", "deposit_period", "saving_period"} and data[field] not in (None, ""):
            if int(data[field]) < 0: raise HTTPException(400, {field: ["Must be non-negative."]})
            setattr(user, field, int(data[field]))
        elif field in {"money", "salary", "desire_amount_deposit", "desire_amount_saving"} and data[field] not in (None, ""):
            if float(data[field]) < 0: raise HTTPException(400, {field: ["Must be non-negative."]})
            setattr(user, field, float(data[field]))
        else: setattr(user, field, data[field])
    image = data.get("profile_image")
    if image and hasattr(image, "filename") and image.filename:
        file_name = f"profile_images/{user.id}_{Path(image.filename).name}"
        target = config.MEDIA_ROOT / file_name; target.parent.mkdir(exist_ok=True)
        with target.open("wb") as destination: shutil.copyfileobj(image.file, destination)
        user.profile_image = file_name
    db.commit(); db.refresh(user)
    return {"message": "User fields updated successfully.", "updated_data": user_data(user, request)}


@app.delete("/accounts/user_delete/", status_code=204)
def user_delete(user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(user); db.commit(); return Response(status_code=204)


# Banking products and community -------------------------------------------
def product_data(product):
    result = model_data(product)
    result["deposit_options" if isinstance(product, DepositBase) else "saving_options"] = [model_data(option) for option in product.options]
    return result


def fetch_product_data(db: Session, product_model, option_model, endpoint: str):
    response = requests.get(endpoint, timeout=20); response.raise_for_status()
    result = response.json().get("result", {})
    for base in result.get("baseList", []):
        item = db.query(product_model).filter_by(fin_co_no=base["fin_co_no"], fin_prdt_cd=base["fin_prdt_cd"]).first()
        values = {key: base.get(key) for key in ("dcls_month", "kor_co_nm", "fin_prdt_nm", "join_way", "mtrt_int", "spcl_cnd", "join_deny", "join_member", "etc_note", "max_limit", "dcls_strt_day", "dcls_end_day", "fin_co_subm_day")}
        if item:
            for key, value in values.items(): setattr(item, key, value)
        else: db.add(product_model(fin_co_no=base["fin_co_no"], fin_prdt_cd=base["fin_prdt_cd"], **values))
    db.flush()
    for option in result.get("optionList", []):
        product = db.query(product_model).filter_by(fin_co_no=option["fin_co_no"], fin_prdt_cd=option["fin_prdt_cd"]).first()
        if not product: continue
        item = db.query(option_model).filter_by(product_id=product.id, save_trm=option["save_trm"]).first()
        values = {key: option.get(key) for key in ("dcls_month", "intr_rate_type", "intr_rate_type_nm", "save_trm")}
        values["intr_rate"] = option.get("intr_rate") or 0; values["intr_rate2"] = option.get("intr_rate2") or 0
        if item:
            for key, value in values.items(): setattr(item, key, value)
        else: db.add(option_model(product_id=product.id, **values))
    db.commit()


@app.get("/bankings/deposit-fetch-data/")
def deposit_fetch_data(db: Session = Depends(get_db)):
    if not config.BANKINGS_KEY: raise HTTPException(503, "BANKINGS_KEY is not configured.")
    fetch_product_data(db, DepositBase, DepositOption, f"https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={config.BANKINGS_KEY}&topFinGrpNo=020000&pageNo=1")
    return {"message": "Data fetched and stored successfully."}


@app.get("/bankings/deposit-get-products/")
def deposit_get_products(db: Session = Depends(get_db)):
    return [product_data(item) for item in db.query(DepositBase).options(selectinload(DepositBase.options)).all()]


@app.get("/bankings/saving-fetch-data/")
def saving_fetch_data(db: Session = Depends(get_db)):
    if not config.BANKINGS_KEY: raise HTTPException(503, "BANKINGS_KEY is not configured.")
    fetch_product_data(db, SavingBase, SavingOption, f"https://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json?auth={config.BANKINGS_KEY}&topFinGrpNo=020000&pageNo=1")
    return {"message": "Data fetched and stored successfully."}


@app.get("/bankings/saving-get-products/")
def saving_get_products(db: Session = Depends(get_db)):
    return [product_data(item) for item in db.query(SavingBase).options(selectinload(SavingBase.options)).all()]


def review_data(review: ProductReview, user: User):
    result = {field: getattr(review, field) for field in ("id", "product_type", "product_name", "title", "content", "rating")}
    result.update(created_at=review.created_at.isoformat(), updated_at=review.updated_at.isoformat(), username=review.user.username, like_count=len(review.likes), is_liked=any(like.id == user.id for like in review.likes), is_owner=review.user_id == user.id)
    result["comments"] = [{"id": c.id, "content": c.content, "username": c.user.username, "created_at": c.created_at.isoformat(), "updated_at": c.updated_at.isoformat(), "is_owner": c.user_id == user.id} for c in review.comments]
    return result


@app.get("/bankings/reviews/")
def reviews(user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = db.query(ProductReview).options(selectinload(ProductReview.user), selectinload(ProductReview.likes), selectinload(ProductReview.comments).selectinload(ReviewComment.user)).order_by(desc(ProductReview.created_at)).all()
    return [review_data(item, user) for item in data]


@app.post("/bankings/reviews/", status_code=201)
async def create_review(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = await body(request)
    try: review = ProductReview(user_id=user.id, product_type=data["product_type"], product_name=data["product_name"], title=data["title"], content=data["content"], rating=int(data["rating"]))
    except KeyError as error: raise HTTPException(400, {"error": f"Missing field: {error.args[0]}"})
    db.add(review); db.commit(); db.refresh(review)
    return review_data(review, user)


@app.put("/bankings/reviews/{review_id}/")
async def update_review(review_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    review = get_or_404(db, ProductReview, review_id)
    if review.user_id != user.id: raise HTTPException(403)
    for field, value in (await body(request)).items():
        if field in {"product_type", "product_name", "title", "content", "rating"}: setattr(review, field, int(value) if field == "rating" else value)
    db.commit(); db.refresh(review); return review_data(review, user)


@app.delete("/bankings/reviews/{review_id}/", status_code=204)
def delete_review(review_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    review = get_or_404(db, ProductReview, review_id)
    if review.user_id != user.id: raise HTTPException(403)
    db.delete(review); db.commit(); return Response(status_code=204)


@app.post("/bankings/reviews/{review_id}/like/")
def like_review(review_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    review = get_or_404(db, ProductReview, review_id)
    if any(like.id == user.id for like in review.likes): review.likes = [like for like in review.likes if like.id != user.id]
    else: review.likes.append(user)
    db.commit(); return {"likes_count": len(review.likes)}


@app.post("/bankings/reviews/{review_id}/comments/", status_code=201)
async def create_comment(review_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    review = get_or_404(db, ProductReview, review_id); data = await body(request)
    comment = ReviewComment(review_id=review.id, user_id=user.id, content=data.get("content", "")); db.add(comment); db.commit(); db.refresh(comment)
    return {"id": comment.id, "content": comment.content, "username": user.username, "created_at": comment.created_at.isoformat(), "updated_at": comment.updated_at.isoformat(), "is_owner": True}


@app.put("/bankings/reviews/{review_id}/comments/")
async def update_comment(review_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = await body(request); comment = get_or_404(db, ReviewComment, int(data.get("comment_id", 0)))
    if comment.review_id != review_id or comment.user_id != user.id: raise HTTPException(403)
    comment.content = data.get("content", comment.content); db.commit(); return {"id": comment.id, "content": comment.content, "username": user.username, "created_at": comment.created_at.isoformat(), "updated_at": comment.updated_at.isoformat(), "is_owner": True}


@app.delete("/bankings/reviews/{review_id}/comments/", status_code=204)
async def delete_comment(review_id: int, request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    comment = get_or_404(db, ReviewComment, int((await body(request)).get("comment_id", 0)))
    if comment.review_id != review_id or comment.user_id != user.id: raise HTTPException(403)
    db.delete(comment); db.commit(); return Response(status_code=204)


@app.get("/bankings/bank-products/{bank_name}/")
def bank_products(bank_name: str, db: Session = Depends(get_db)):
    deposits = db.query(DepositBase).options(selectinload(DepositBase.options)).filter_by(kor_co_nm=bank_name).all()
    savings = db.query(SavingBase).options(selectinload(SavingBase.options)).filter_by(kor_co_nm=bank_name).all()
    return {"deposit_products": [product_data(item) for item in deposits], "saving_products": [product_data(item) for item in savings]}


# Exchange, stocks, news and markets ---------------------------------------
@app.get("/currencies/exchange-fetch-data/")
def exchange_fetch_data(db: Session = Depends(get_db)):
    if not config.CURRENCIES_KEY: raise HTTPException(503, "CURRENCIES_KEY is not configured.")
    url = "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"
    response = requests.get(url, params={"authkey": config.CURRENCIES_KEY, "data": "AP01"}, timeout=20)
    response.raise_for_status()
    for source in response.json():
        item = db.query(Exchange).filter_by(cur_unit=source.get("cur_unit", "")).first()
        values = {key: source.get(key, "") for key in ("ttb", "tts", "deal_bas_r", "bkpr", "yy_efee_r", "ten_dd_efee_r", "kftc_bkpr", "kftc_deal_bas_r", "cur_nm")}
        if item:
            for key, value in values.items(): setattr(item, key, value)
        else: db.add(Exchange(cur_unit=source.get("cur_unit", ""), **values))
    db.commit(); return {"message": "Exchange rates fetched and stored successfully."}


@app.get("/currencies/exchange-get-data/")
def exchange_get_data(db: Session = Depends(get_db)):
    return [model_data(item) for item in db.query(Exchange).all()]


@app.post("/currencies/exchange-calculate/")
async def exchange_calculate(request: Request, db: Session = Depends(get_db)):
    data = await body(request)
    try: amount = float(data.get("amount", 0))
    except (ValueError, TypeError): raise HTTPException(400, {"error": "Invalid amount"})
    source, target = data.get("from_currency"), data.get("to_currency")
    if not amount or not source or not target: raise HTTPException(400, {"error": "Required parameters missing"})
    from_item, to_item = db.query(Exchange).filter_by(cur_unit=source).first(), db.query(Exchange).filter_by(cur_unit=target).first()
    if not from_item or not to_item: raise HTTPException(400, {"error": "Invalid currency"})
    try: converted = amount * float(from_item.deal_bas_r.replace(",", "")) / float(to_item.deal_bas_r.replace(",", ""))
    except ValueError: raise HTTPException(400, {"error": "Invalid currency rate"})
    return {"from_amount": amount, "from_currency": source, "to_currency": target, "converted_amount": round(converted, 2)}


@app.get("/stocks/stock-fetch-data/")
def stock_fetch_data(db: Session = Depends(get_db)):
    if not config.STOCKS_KEY: raise HTTPException(503, "STOCKS_KEY is not configured.")
    url = "http://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getStockMarketIndex"
    response = requests.get(url, params={"serviceKey": config.STOCKS_KEY}, timeout=20)
    response.raise_for_status(); items = xmltodict.parse(response.content).get("response", {}).get("body", {}).get("items", {}).get("item", [])
    if isinstance(items, dict): items = [items]
    for source in items:
        item = db.query(Stock).filter_by(bas_dt=source.get("basDt"), idx_nm=source.get("idxNm")).first()
        values = {"idx_csf": source.get("idxCsf"), "epy_itms_cnt": int(source.get("epyItmsCnt") or 0), "clpr": float(source.get("clpr") or 0), "vs": float(source.get("vs") or 0), "flt_rt": float(source.get("fltRt") or 0), "mkp": float(source.get("mkp") or 0), "hipr": float(source.get("hipr") or 0), "lopr": float(source.get("lopr") or 0), "trqu": int(source.get("trqu") or 0), "tr_prc": int(source.get("trPrc") or 0), "lstg_mrkt_tot_amt": int(source.get("lstgMrktTotAmt") or 0)}
        if item:
            for key, value in values.items(): setattr(item, key, value)
        else: db.add(Stock(bas_dt=source.get("basDt"), idx_nm=source.get("idxNm"), **values))
    db.commit(); return {"message": "Data fetched and saved successfully."}


@app.get("/stocks/stock-get-data/")
def stock_get_data(db: Session = Depends(get_db)):
    return [model_data(item) for item in db.query(Stock).all()]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value))).strip()


@app.get("/economics/news-fetch-data/")
def news_fetch_data(query: str = "경제 주식", display: int = 10, start: int = 1, sort: str = "date", db: Session = Depends(get_db)):
    if not config.NAVER_CLIENT_ID or not config.NAVER_CLIENT_SECRET: raise HTTPException(503, "Naver API credentials are not configured.")
    response = requests.get("https://openapi.naver.com/v1/search/news.json", headers={"X-Naver-Client-Id": config.NAVER_CLIENT_ID, "X-Naver-Client-Secret": config.NAVER_CLIENT_SECRET}, params={"query": query, "display": display, "start": start, "sort": sort}, timeout=20)
    response.raise_for_status(); items = response.json().get("items", [])
    for source in items:
        title = clean_text(source["title"]); item = db.query(News).filter_by(title=title).first()
        values = {"originallink": source["originallink"], "link": source["link"], "description": clean_text(source["description"]), "pub_date": source["pubDate"]}
        if item:
            for key, value in values.items(): setattr(item, key, value)
        else: db.add(News(title=title, **values))
    db.commit(); return {"message": "News fetched successfully.", "news_count": len(items)}


@app.get("/economics/news-get-data/")
def news_get_data(db: Session = Depends(get_db)):
    return [model_data(item) for item in db.query(News).order_by(desc(News.pub_date)).all()]


@app.get("/markets/indices/")
def market_indices():
    data = {}
    try:
        for name, ticker in {"S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Dow Jones": "^DJI", "Kospi": "^KS11"}.items():
            history = yf.Ticker(ticker).history(period="5d")
            if history.empty or len(history) < 2: data[name] = {"current_price": "N/A", "percentage_change": 0.0}; continue
            current, previous = history["Close"].iloc[-1], history["Close"].iloc[-2]
            data[name] = {"current_price": round(float(current), 2), "percentage_change": round(float((current - previous) / previous * 100), 2)}
    except Exception as error: raise HTTPException(500, {"error": str(error)})
    return data


# Surveys, recommendations, subscriptions ----------------------------------
@app.post("/surveys/submit-survey/")
async def submit_survey(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = await body(request)
    required = ("age_group", "income_source", "asset_size", "financial_purpose", "important_factor", "recent_investment", "financial_products", "preferred_bank")
    missing = [field for field in required if field not in data]
    if missing: raise HTTPException(400, {"error": f"Missing fields: {', '.join(missing)}"})
    # The prior client submits eight questions.  Fields from the longer original model
    # deliberately retain empty defaults so historic schema and recommendations work.
    payload = {field: data.get(field, "") for field in ("age_group", "income_source", "asset_size", "financial_purpose", "important_factor", "expected_return", "investment_period", "financial_products", "preferred_bank", "banking_channel", "risk_tolerance", "preferred_product", "preferred_method", "monthly_investment", "preferred_benefit", "service_priority")}
    recent = data["recent_investment"]
    payload["recent_investment"] = recent if isinstance(recent, bool) else str(recent).lower() == "true"
    db.add(UserSurvey(user_id=user.id, **payload)); db.commit()
    return {"message": "Survey submitted successfully."}


@app.get("/recommendations/recommend/")
def recommendations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    survey = db.query(UserSurvey).filter_by(user_id=user.id).order_by(desc(UserSurvey.created_at)).first()
    if not survey: raise HTTPException(404, {"error": "No survey data found for the user."})
    def top_products(model, option):
        products = db.query(model).options(selectinload(model.options)).all()
        ranked = sorted(products, key=lambda product: max((item.intr_rate2 or item.intr_rate or 0 for item in product.options), default=0), reverse=True)[:5]
        return [{"fin_prdt_cd": item.fin_prdt_cd, "fin_prdt_nm": item.fin_prdt_nm, "kor_co_nm": item.kor_co_nm, "intr_rate2": max((option.intr_rate2 or option.intr_rate or 0 for option in item.options), default=0)} for item in ranked]
    return {"deposit_recommendations": top_products(DepositBase, DepositOption), "saving_recommendations": top_products(SavingBase, SavingOption)}


@app.post("/subscriptions/subscribe/", status_code=201)
async def toggle_subscription(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = await body(request); product_id, product_name = data.get("product_id"), data.get("product_name")
    if not product_id or not product_name: raise HTTPException(400, {"error": "Product ID and name are required."})
    item = db.query(Subscription).filter_by(user_id=user.id, product_id=str(product_id)).first()
    if item:
        db.delete(item); db.commit(); return {"message": f"'{product_name}' 구독이 취소되었습니다."}
    item = Subscription(user_id=user.id, product_id=str(product_id), product_name=product_name); db.add(item); db.commit(); db.refresh(item)
    return model_data(item)


@app.get("/subscriptions/my-subscriptions/")
def my_subscriptions(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [model_data(item, exclude=("user_id",)) for item in db.query(Subscription).filter_by(user_id=user.id).all()]


# Chat ---------------------------------------------------------------------
@app.post("/chats/chat-message/")
async def chat_message(request: Request, user: User = Depends(current_user), db: Session = Depends(get_db)):
    data = await body(request); message = data.get("message")
    if not message: raise HTTPException(400, {"error": "메시지를 입력해주세요."})
    conversation_id = data.get("conversation_id")
    conversation = get_or_404(db, Conversation, int(conversation_id)) if conversation_id else Conversation(user_id=user.id)
    if conversation_id and conversation.user_id != user.id: raise HTTPException(403)
    if not conversation_id: db.add(conversation); db.flush()
    db.add(Message(conversation_id=conversation.id, role="user", content=message))
    if not config.CHATS_KEY: raise HTTPException(503, {"error": "CHATS_KEY is not configured."})
    try:
        answer = OpenAI(api_key=config.CHATS_KEY).chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "당신은 금융 상품 추천과 금융 관련 상담을 해주는 전문가입니다."}, {"role": "user", "content": message}]).choices[0].message.content
    except Exception as error: db.rollback(); raise HTTPException(500, {"error": str(error)})
    db.add(Message(conversation_id=conversation.id, role="assistant", content=answer)); conversation.updated_at = datetime.utcnow(); db.commit()
    return {"conversation_id": conversation.id, "message": answer}


@app.get("/chats/chat-history/")
def chat_history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    conversations = db.query(Conversation).options(selectinload(Conversation.messages)).filter_by(user_id=user.id).order_by(desc(Conversation.created_at)).all()
    return [{"id": item.id, "created_at": item.created_at.isoformat(), "updated_at": item.updated_at.isoformat(), "messages": [model_data(message) for message in item.messages]} for item in conversations]


@app.get("/health/")
def health():
    return {"status": "ok"}
