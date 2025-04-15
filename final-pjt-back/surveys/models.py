from django.db import models
from django.conf import settings


class UserSurvey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # 기본 정보
    age_group = models.CharField(max_length=20)  # 연령대
    income_source = models.CharField(max_length=20)  # 소득원
    asset_size = models.CharField(max_length=20)  # 자산 규모
    
    # 금융 목표
    financial_purpose = models.CharField(max_length=20)  # 금융 목적
    important_factor = models.CharField(max_length=20)  # 중요 요소
    expected_return = models.CharField(max_length=20)  # 기대 수익률
    investment_period = models.CharField(max_length=20)  # 투자 기간
    
    # 금융 이용 경험
    financial_products = models.CharField(max_length=100)  # 이용 금융상품
    preferred_bank = models.CharField(max_length=20)  # 선호 은행
    banking_channel = models.CharField(max_length=20)  # 이용 채널
    recent_investment = models.BooleanField(null=True, blank=True)  # 최근 투자 여부
    
    # 금융 선호도
    risk_tolerance = models.CharField(max_length=20)  # 위험 감수성향
    preferred_product = models.CharField(max_length=20)  # 선호 상품유형
    preferred_method = models.CharField(max_length=20)  # 선호 가입방법
    
    # 맞춤 데이터
    monthly_investment = models.CharField(max_length=20)  # 월 투자금액
    preferred_benefit = models.CharField(max_length=20)  # 선호 우대조건
    service_priority = models.CharField(max_length=20)  # 주요 이용서비스

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']