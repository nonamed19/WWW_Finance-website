"""Currency exchange API routes."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from . import config
from .common import body, model_data
from .database import get_db
from .external import get_json
from .models import Exchange


router = APIRouter(prefix="/currencies", tags=["currencies"])


@router.get("/exchange-fetch-data/")
def exchange_fetch_data(db: Session = Depends(get_db)):
    if not config.CURRENCIES_KEY:
        raise HTTPException(503, "CURRENCIES_KEY is not configured.")
    sources = get_json(
        "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON",
        params={"authkey": config.CURRENCIES_KEY, "data": "AP01"},
    )
    currency_units = [source.get("cur_unit") for source in sources if source.get("cur_unit")]
    existing = (
        db.query(Exchange).filter(Exchange.cur_unit.in_(currency_units)).all()
        if currency_units else []
    )
    exchanges = {item.cur_unit: item for item in existing}
    for source in sources:
        currency_unit = source.get("cur_unit")
        if not currency_unit:
            continue
        item = exchanges.get(currency_unit)
        values = {
            key: source.get(key, "")
            for key in (
                "ttb", "tts", "deal_bas_r", "bkpr", "yy_efee_r",
                "ten_dd_efee_r", "kftc_bkpr", "kftc_deal_bas_r", "cur_nm",
            )
        }
        if item:
            for key, value in values.items():
                setattr(item, key, value)
        else:
            db.add(Exchange(cur_unit=currency_unit, **values))
    db.commit()
    return {"message": "Exchange rates fetched and stored successfully."}


@router.get("/exchange-get-data/")
def exchange_get_data(db: Session = Depends(get_db)):
    return [model_data(item) for item in db.query(Exchange).all()]


@router.post("/exchange-calculate/")
async def exchange_calculate(request: Request, db: Session = Depends(get_db)):
    data = await body(request)
    try:
        amount = float(data.get("amount", 0))
    except (ValueError, TypeError) as error:
        raise HTTPException(400, {"error": "Invalid amount"}) from error
    source = data.get("from_currency")
    target = data.get("to_currency")
    if not amount or not source or not target:
        raise HTTPException(400, {"error": "Required parameters missing"})
    exchanges = {
        item.cur_unit: item
        for item in db.query(Exchange).filter(Exchange.cur_unit.in_((source, target))).all()
    }
    from_item = exchanges.get(source)
    to_item = exchanges.get(target)
    if not from_item or not to_item:
        raise HTTPException(400, {"error": "Invalid currency"})
    try:
        converted = (
            amount
            * float(from_item.deal_bas_r.replace(",", ""))
            / float(to_item.deal_bas_r.replace(",", ""))
        )
    except ValueError as error:
        raise HTTPException(400, {"error": "Invalid currency rate"}) from error
    return {
        "from_amount": amount,
        "from_currency": source,
        "to_currency": target,
        "converted_amount": round(converted, 2),
    }
