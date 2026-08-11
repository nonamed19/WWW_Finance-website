from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserSurvey
import logging

# 디버깅 로그 설정
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_survey(request):
    try:
        # 요청 데이터 디버깅
        print("Raw body:", request.body)  # 요청 본문 출력
        print("Parsed data:", request.data)  # 파싱된 데이터 출력

        data = request.data
        required_fields = [
            "age_group", "income_source", "asset_size", "financial_purpose",
            "important_factor", "recent_investment", "financial_products", "preferred_bank"
        ]

        # 누락된 필드 확인
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return Response(
                {"error": f"Missing fields: {', '.join(missing_fields)}"},
                status=400,
            )

        # 데이터 저장
        UserSurvey.objects.create(
            user=request.user,
            age_group=data.get("age_group"),
            income_source=data.get("income_source"),
            asset_size=data.get("asset_size"),
            financial_purpose=data.get("financial_purpose"),
            important_factor=data.get("important_factor"),
            recent_investment=data.get("recent_investment"),
            financial_products=data.get("financial_products"),
            preferred_bank=data.get("preferred_bank"),
        )

        return Response({"message": "Survey submitted successfully."}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)
