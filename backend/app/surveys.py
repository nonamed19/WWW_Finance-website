"""Financial survey API routes."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .common import body
from .database import get_db
from .models import User, UserSurvey
from .security import current_user


router = APIRouter(prefix="/surveys", tags=["surveys"])


@router.post("/submit-survey/")
async def submit_survey(
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    data = await body(request)
    required = (
        "age_group", "income_source", "asset_size", "financial_purpose",
        "important_factor", "recent_investment", "financial_products",
        "preferred_bank",
    )
    missing = [field for field in required if field not in data]
    if missing:
        raise HTTPException(400, {"error": f"Missing fields: {', '.join(missing)}"})

    fields = (
        "age_group", "income_source", "asset_size", "financial_purpose",
        "important_factor", "expected_return", "investment_period",
        "financial_products", "preferred_bank", "banking_channel",
        "risk_tolerance", "preferred_product", "preferred_method",
        "monthly_investment", "preferred_benefit", "service_priority",
    )
    payload = {field: data.get(field, "") for field in fields}
    recent = data["recent_investment"]
    payload["recent_investment"] = (
        recent if isinstance(recent, bool) else str(recent).lower() == "true"
    )
    db.add(UserSurvey(user_id=user.id, **payload))
    db.commit()
    return {"message": "Survey submitted successfully."}
