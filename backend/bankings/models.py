from django.db import models
from django.conf import settings


class DepositBaseList(models.Model):
    dcls_month = models.CharField(max_length=6)     # 공시 제출 월 (YYYYMM 형식)
    fin_co_no = models.CharField(max_length=20)    # 금융 회사 번호
    fin_prdt_cd = models.CharField(max_length=20)    # 금융 상품 코드
    kor_co_nm = models.CharField(max_length=100)    # 금융 회사명
    fin_prdt_nm = models.CharField(max_length=100)    # 금융 상품명
    join_way = models.TextField()    # 가입 방법 (예: 인터넷, 스마트폰 등)
    mtrt_int = models.TextField()    # 만기 후 이자율 정보
    spcl_cnd = models.TextField()    # 우대 조건
    join_deny = models.IntegerField()    # 가입 제한 (1: 제한 없음, 2: 서민전용, 3: 일부제한)
    join_member = models.TextField()    # 가입 대상 (예: 개인, 사업자 등)
    etc_note = models.TextField(null=True, blank=True)    # 기타 정보
    max_limit = models.BigIntegerField(null=True, blank=True)    # 최대 한도 금액 (없을 경우 null 허용)
    dcls_strt_day = models.CharField(max_length=8)    # 공시 시작일 (YYYYMMDD 형식)
    dcls_end_day = models.CharField(max_length=8, null=True, blank=True)    # 공시 종료일 (YYYYMMDD 형식, null 허용)
    fin_co_subm_day = models.CharField(max_length=14)    # 금융 회사의 데이터 제출일 (YYYYMMDDHHMM 형식)


class DepositOptionList(models.Model):
    product = models.ForeignKey(DepositBaseList, on_delete=models.CASCADE, related_name="deposit_options")
    save_trm = models.CharField(max_length=10)
    intr_rate = models.FloatField(null=True, blank=True)  # 허용 설정
    intr_rate2 = models.FloatField(null=True, blank=True)  # 허용 설정
    intr_rate_type = models.CharField(max_length=10, null=True, blank=True)
    intr_rate_type_nm = models.CharField(max_length=20, null=True, blank=True)
    dcls_month = models.CharField(max_length=6)


class SavingBaseList(models.Model):
    dcls_month = models.CharField(max_length=6)     # 공시 제출 월 (YYYYMM 형식)
    fin_co_no = models.CharField(max_length=20)    # 금융 회사 번호
    fin_prdt_cd = models.CharField(max_length=20)    # 금융 상품 코드
    kor_co_nm = models.CharField(max_length=100)    # 금융 회사명
    fin_prdt_nm = models.CharField(max_length=100)    # 금융 상품명
    join_way = models.TextField()    # 가입 방법 (예: 인터넷, 스마트폰 등)
    mtrt_int = models.TextField()    # 만기 후 이자율 정보
    spcl_cnd = models.TextField()    # 우대 조건
    join_deny = models.IntegerField()    # 가입 제한 (1: 제한 없음, 2: 서민전용, 3: 일부제한)
    join_member = models.TextField()    # 가입 대상 (예: 개인, 사업자 등)
    etc_note = models.TextField(null=True, blank=True)    # 기타 정보
    max_limit = models.BigIntegerField(null=True, blank=True)    # 최대 한도 금액 (없을 경우 null 허용)
    dcls_strt_day = models.CharField(max_length=8)    # 공시 시작일 (YYYYMMDD 형식)
    dcls_end_day = models.CharField(max_length=8, null=True, blank=True)    # 공시 종료일 (YYYYMMDD 형식, null 허용)
    fin_co_subm_day = models.CharField(max_length=14)    # 금융 회사의 데이터 제출일 (YYYYMMDDHHMM 형식)


class SavingOptionList(models.Model):
    product = models.ForeignKey(SavingBaseList, on_delete=models.CASCADE, related_name="saving_options")
    save_trm = models.CharField(max_length=10)
    intr_rate = models.FloatField(null=True, blank=True)  # 허용 설정
    intr_rate2 = models.FloatField(null=True, blank=True)  # 허용 설정
    intr_rate_type = models.CharField(max_length=10, null=True, blank=True)
    intr_rate_type_nm = models.CharField(max_length=20, null=True, blank=True)
    dcls_month = models.CharField(max_length=6)


class ProductReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=10)
    product_name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField()
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_reviews', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def like_count(self):
        return self.likes.count()


class ReviewComment(models.Model):
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)