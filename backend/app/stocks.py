"""Stock market data API routes."""
import xmltodict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import tuple_
from sqlalchemy.orm import Session

from . import config
from .common import model_data
from .database import get_db
from .external import get_content
from .models import Stock


router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/stock-fetch-data/")
def stock_fetch_data(db: Session = Depends(get_db)):
    if not config.STOCKS_KEY:
        raise HTTPException(503, "STOCKS_KEY is not configured.")
    content = get_content(
        "http://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getStockMarketIndex",
        params={"serviceKey": config.STOCKS_KEY},
    )
    items = xmltodict.parse(content).get("response", {}).get("body", {}).get("items", {}).get("item", [])
    if isinstance(items, dict):
        items = [items]
    stock_keys = {
        (source.get("basDt"), source.get("idxNm"))
        for source in items
        if source.get("basDt") and source.get("idxNm")
    }
    existing = (
        db.query(Stock)
        .filter(tuple_(Stock.bas_dt, Stock.idx_nm).in_(list(stock_keys)))
        .all()
        if stock_keys else []
    )
    stocks = {(item.bas_dt, item.idx_nm): item for item in existing}
    for source in items:
        key = (source.get("basDt"), source.get("idxNm"))
        if not all(key):
            continue
        item = stocks.get(key)
        values = {
            "idx_csf": source.get("idxCsf"),
            "epy_itms_cnt": int(source.get("epyItmsCnt") or 0),
            "clpr": float(source.get("clpr") or 0),
            "vs": float(source.get("vs") or 0),
            "flt_rt": float(source.get("fltRt") or 0),
            "mkp": float(source.get("mkp") or 0),
            "hipr": float(source.get("hipr") or 0),
            "lopr": float(source.get("lopr") or 0),
            "trqu": int(source.get("trqu") or 0),
            "tr_prc": int(source.get("trPrc") or 0),
            "lstg_mrkt_tot_amt": int(source.get("lstgMrktTotAmt") or 0),
        }
        if item:
            for key, value in values.items():
                setattr(item, key, value)
        else:
            db.add(Stock(bas_dt=key[0], idx_nm=key[1], **values))
    db.commit()
    return {"message": "Data fetched and saved successfully."}


@router.get("/stock-get-data/")
def stock_get_data(db: Session = Depends(get_db)):
    return [model_data(item) for item in db.query(Stock).all()]
