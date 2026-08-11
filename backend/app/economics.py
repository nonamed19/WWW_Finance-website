"""Economic news API routes."""
import html
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from . import config
from .common import model_data
from .database import get_db
from .external import get_json
from .models import News


router = APIRouter(prefix="/economics", tags=["economics"])


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value))).strip()


@router.get("/news-fetch-data/")
def news_fetch_data(
    query: str = "경제 주식",
    display: int = 10,
    start: int = 1,
    sort: str = "date",
    db: Session = Depends(get_db),
):
    if not config.NAVER_CLIENT_ID or not config.NAVER_CLIENT_SECRET:
        raise HTTPException(503, "Naver API credentials are not configured.")
    payload = get_json(
        "https://openapi.naver.com/v1/search/news.json",
        headers={
            "X-Naver-Client-Id": config.NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": config.NAVER_CLIENT_SECRET,
        },
        params={"query": query, "display": display, "start": start, "sort": sort},
    )
    items = payload.get("items", [])
    for source in items:
        title = clean_text(source["title"])
        item = db.query(News).filter_by(title=title).first()
        values = {
            "originallink": source["originallink"],
            "link": source["link"],
            "description": clean_text(source["description"]),
            "pub_date": source["pubDate"],
        }
        if item:
            for key, value in values.items():
                setattr(item, key, value)
        else:
            db.add(News(title=title, **values))
    db.commit()
    return {"message": "News fetched successfully.", "news_count": len(items)}


@router.get("/news-get-data/")
def news_get_data(db: Session = Depends(get_db)):
    news = db.query(News).order_by(desc(News.pub_date)).all()
    return [model_data(item) for item in news]
