from django.urls import path
from . import views


urlpatterns = [
    path('exchange-fetch-data/', views.exchange_fetch_data, name='exchange_fetch_data'),  # 환율 정보 저장
    path('exchange-get-data/', views.exchange_get_data, name='exchange_get_data'),  # 환율 정보 조회
    path('exchange-calculate/', views.exchange_calculate, name='exchange_calculate'),
]
