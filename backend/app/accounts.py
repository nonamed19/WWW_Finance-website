"""Account and profile API routes."""
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from . import config
from .common import body
from .database import get_db
from .models import ApiToken, User
from .security import create_token, current_user, hash_password, verify_password


router = APIRouter(prefix="/accounts", tags=["accounts"])


def user_data(user: User, request: Request) -> dict:
    fields = (
        "id", "username", "name", "email", "age", "money", "salary",
        "desire_amount_deposit", "deposit_period", "desire_amount_saving",
        "saving_period",
    )
    result = {
        field: float(getattr(user, field))
        if hasattr(getattr(user, field), "as_tuple")
        else getattr(user, field)
        for field in fields
    }
    result["profile_image"] = (
        str(request.base_url).rstrip("/") + "/media/" + user.profile_image
        if user.profile_image
        else None
    )
    return result


@router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def signup(request: Request, db: Session = Depends(get_db)):
    data = await body(request)
    username = data.get("username", "")
    password1 = data.get("password1", "")
    password2 = data.get("password2", "")
    if not username or not password1:
        raise HTTPException(400, "username and password are required.")
    if password1 != password2:
        raise HTTPException(400, "Passwords do not match.")
    if db.query(User).filter_by(username=username).first():
        raise HTTPException(400, {"username": ["A user with that username already exists."]})
    user = User(
        username=username,
        password=hash_password(password1),
        email=data.get("email", ""),
        name=data.get("name") or "",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"key": create_token(db, user)}


@router.post("/login/")
async def login(request: Request, db: Session = Depends(get_db)):
    data = await body(request)
    user = db.query(User).filter_by(username=data.get("username", "")).first()
    if not user or not verify_password(data.get("password", ""), user.password):
        raise HTTPException(400, {"non_field_errors": ["Unable to log in with provided credentials."]})
    user.last_login = datetime.utcnow()
    db.commit()
    return {"key": create_token(db, user)}


@router.post("/logout/", status_code=204)
def logout(user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.query(ApiToken).filter_by(user_id=user.id).delete()
    db.commit()
    return Response(status_code=204)


@router.get("/user_all/")
def user_all(request: Request, db: Session = Depends(get_db)):
    return [user_data(user, request) for user in db.query(User).all()]


@router.get("/user_info/")
def user_info(request: Request, user: User = Depends(current_user)):
    return {
        "user_info": user_data(user, request),
        "message": "User information retrieved successfully.",
    }


@router.patch("/user_update/")
async def user_update(
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    data = await body(request)
    allowed = {
        "username", "name", "email", "age", "money", "salary",
        "desire_amount_deposit", "deposit_period", "desire_amount_saving",
        "saving_period",
    }
    for field in allowed & data.keys():
        if field in {"age", "deposit_period", "saving_period"} and data[field] not in (None, ""):
            if int(data[field]) < 0:
                raise HTTPException(400, {field: ["Must be non-negative."]})
            setattr(user, field, int(data[field]))
        elif field in {"money", "salary", "desire_amount_deposit", "desire_amount_saving"} and data[field] not in (None, ""):
            if float(data[field]) < 0:
                raise HTTPException(400, {field: ["Must be non-negative."]})
            setattr(user, field, float(data[field]))
        else:
            setattr(user, field, data[field])

    image = data.get("profile_image")
    if image and hasattr(image, "filename") and image.filename:
        file_name = f"profile_images/{user.id}_{Path(image.filename).name}"
        target = config.MEDIA_ROOT / file_name
        target.parent.mkdir(exist_ok=True)
        with target.open("wb") as destination:
            shutil.copyfileobj(image.file, destination)
        user.profile_image = file_name

    db.commit()
    db.refresh(user)
    return {
        "message": "User fields updated successfully.",
        "updated_data": user_data(user, request),
    }


@router.delete("/user_delete/", status_code=204)
def user_delete(user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(user)
    db.commit()
    return Response(status_code=204)
