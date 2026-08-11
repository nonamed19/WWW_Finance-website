from django.db import models

class NewsList(models.Model):
    title = models.CharField(max_length=255)  # 뉴스 제목
    originallink = models.URLField()  # 원본 링크
    link = models.URLField()  # 네이버 뉴스 링크
    description = models.TextField()  # 뉴스 요약
    pub_date = models.CharField(max_length=100)  # 뉴스 발행일 (문자열로 저장)
