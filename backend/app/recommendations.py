"""Financial product recommendation API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, desc, func
from sqlalchemy.orm import Session

from .database import get_db
from .models import (
    DepositBase, DepositOption, SavingBase, SavingOption, User, UserSurvey,
)
from .security import current_user


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/recommend/")
def recommendations(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    survey = db.query(UserSurvey).filter_by(user_id=user.id).order_by(
        desc(UserSurvey.created_at)
    ).first()
    if not survey:
        raise HTTPException(404, {"error": "No survey data found for the user."})

    def top_products(model, option_model):
        # Calculate and limit in MySQL instead of loading every product and
        # option into Python just to discard all but five records.
        option_rate = case(
            (option_model.intr_rate2 > 0, option_model.intr_rate2),
            else_=func.coalesce(option_model.intr_rate, 0),
        )
        max_rate = func.max(option_rate).label("intr_rate2")
        ranked = (
            db.query(
                model.fin_prdt_cd, model.fin_prdt_nm, model.kor_co_nm, max_rate
            )
            .outerjoin(option_model, model.options)
            .group_by(model.id, model.fin_prdt_cd, model.fin_prdt_nm, model.kor_co_nm)
            .order_by(max_rate.desc())
            .limit(5)
            .all()
        )
        return [
            {
                "fin_prdt_cd": item.fin_prdt_cd,
                "fin_prdt_nm": item.fin_prdt_nm,
                "kor_co_nm": item.kor_co_nm,
                "intr_rate2": float(item.intr_rate2 or 0),
            }
            for item in ranked
        ]

    return {
        "deposit_recommendations": top_products(DepositBase, DepositOption),
        "saving_recommendations": top_products(SavingBase, SavingOption),
    }
