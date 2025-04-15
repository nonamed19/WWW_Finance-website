from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .utils import (
    get_or_create_model,
    generate_dummy_survey_data,
    generate_training_data,
    fetch_products
)
from surveys.models import UserSurvey
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def map_survey_responses(survey_data):
    mappings = {
        "age_group": {"20대": "20대", "30대": "30대", "40대": "40대", "50대": "50대", "60대_이상": "60대 이상"},
        "asset_size": {"1000만원_이하": "1000만원 이하", "1000만원_5000만원": "1000만원 ~ 5000만원", "5000만원_이상": "5000만원 이상"},
    }
    for key, mapping in mappings.items():
        if key in survey_data:
            survey_data[key] = mapping.get(survey_data[key], survey_data[key])
    return survey_data


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    try:
        user_id = request.user.id

        # 최신 설문 데이터 가져오기
        user_survey = UserSurvey.objects.filter(user=request.user).latest('created_at')
        user_survey_data = {
            "age_group": user_survey.age_group,
            "income_source": user_survey.income_source,
            "asset_size": user_survey.asset_size,
            "financial_purpose": user_survey.financial_purpose,
            "important_factor": user_survey.important_factor,
            "recent_investment": user_survey.recent_investment,
            "financial_products": user_survey.financial_products,
            "preferred_bank": user_survey.preferred_bank,
        }

        user_survey_data = map_survey_responses(user_survey_data)
        logger.debug(f"User survey data: {user_survey_data}")
        user_survey_df = pd.DataFrame([user_survey_data])

        # 상품 데이터 및 학습
        deposit_df, saving_df = fetch_products()
        survey_data = generate_dummy_survey_data()
        product_data = pd.concat([deposit_df, saving_df])
        training_data = generate_training_data(survey_data, product_data)

        # 추천 모델 가져오기 또는 생성
        recommender = get_or_create_model(user_id, training_data, product_data)

        # 예금 상품 추천
        deposit_recommendations = recommender.predict(user_survey_df, deposit_df)
        serialized_deposits = [
            {
                "fin_prdt_cd": row["fin_prdt_cd"],
                "fin_prdt_nm": row["fin_prdt_nm"],
                "kor_co_nm": row["kor_co_nm"],
                "intr_rate2": row["intr_rate2"]
            }
            for _, row in deposit_df.iterrows()
            if row["fin_prdt_nm"] in deposit_recommendations
        ]

        # 적금 상품 추천
        saving_recommendations = recommender.predict(user_survey_df, saving_df)
        serialized_savings = [
            {
                "fin_prdt_cd": row["fin_prdt_cd"],
                "fin_prdt_nm": row["fin_prdt_nm"],
                "kor_co_nm": row["kor_co_nm"],
                "intr_rate2": row["intr_rate2"]
            }
            for _, row in saving_df.iterrows()
            if row["fin_prdt_nm"] in saving_recommendations
        ]

        return JsonResponse({
            "deposit_recommendations": serialized_deposits,
            "saving_recommendations": serialized_savings
        }, status=200)

    except UserSurvey.DoesNotExist:
        return JsonResponse({"error": "No survey data found for the user."}, status=404)
    except Exception as e:
        logger.error(f"Error in get_recommendations: {e}")
        return JsonResponse({"error": str(e)}, status=400)
