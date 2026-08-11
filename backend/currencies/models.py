from django.db import models

class ExchangeList(models.Model):
    cur_unit = models.CharField(max_length=100)  ## 통화 단위 (예: AED, USD 등)
    ttb = models.CharField(max_length=100)  ## 전신환(송금) 받으실 때
    tts = models.CharField(max_length=100)  ## 전신환(송금) 보내실 때
    deal_bas_r = models.CharField(max_length=100)  ## 매매기준율
    bkpr = models.CharField(max_length=100)  ## 장부가격
    yy_efee_r = models.CharField(max_length=100)  ## 연이율 수수료율
    ten_dd_efee_r = models.CharField(max_length=100)  ## 10일 수수료율
    kftc_bkpr = models.CharField(max_length=100)  ## KFTC 장부가격
    kftc_deal_bas_r = models.CharField(max_length=100)  ## KFTC 매매기준율
    cur_nm = models.CharField(max_length=100)  ## 통화명 (예: 미국 달러)
