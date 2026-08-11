from django.db import models

class StockList(models.Model):
    bas_dt = models.CharField(max_length=10)  # 기준 일자
    idx_nm = models.CharField(max_length=100)  # 지수 이름
    idx_csf = models.CharField(max_length=100, blank=True, null=True)  # 지수 분류
    epy_itms_cnt = models.IntegerField(default=0)  # 구성 종목 수
    clpr = models.FloatField(default=0.0)  # 종가
    vs = models.FloatField(default=0.0)  # 전일 대비
    flt_rt = models.FloatField(default=0.0)  # 등락률
    mkp = models.FloatField(default=0.0)  # 시가
    hipr = models.FloatField(default=0.0)  # 고가
    lopr = models.FloatField(default=0.0)  # 저가
    trqu = models.BigIntegerField(default=0)  # 거래량
    tr_prc = models.BigIntegerField(default=0)  # 거래대금
    lstg_mrkt_tot_amt = models.BigIntegerField(default=0)  # 상장 시가총액
