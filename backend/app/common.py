"""Shared helpers used by the feature routers."""
from datetime import datetime

from fastapi import HTTPException, Request


async def body(request: Request) -> dict:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        return await request.json()
    form = await request.form()
    return dict(form)


def model_data(item, exclude=()) -> dict:
    result = {}
    for column in item.__table__.columns:
        if column.name not in exclude:
            value = getattr(item, column.name)
            result[column.name] = (
                value.isoformat()
                if isinstance(value, datetime)
                else float(value)
                if hasattr(value, "as_tuple")
                else value
            )
    return result


def get_or_404(db, model, object_id: int):
    item = db.get(model, object_id)
    if not item:
        raise HTTPException(404, "Not found.")
    return item
