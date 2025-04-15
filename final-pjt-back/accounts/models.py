from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name="닉네임")    # 닉네임 필드
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="나이")    # 나이 필드
    money = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="자산")    # 자산 필드
    salary = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="연봉")    # 연봉 필드
    desire_amount_deposit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="예금 희망 금액")    # 예금 희망 금액
    deposit_period = models.PositiveIntegerField(null=True, blank=True, verbose_name="예금 희망 기간 (월)")    # 예금 희망 기간 (월)
    desire_amount_saving = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="월 적금 희망 금액")    # 월 적금 희망 금액
    saving_period = models.PositiveIntegerField(null=True, blank=True, verbose_name="적금 희망 기간 (월)")    # 적금 희망 기간 (월)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        verbose_name="프로필 이미지"
    )
    def __str__(self):
        return self.username
