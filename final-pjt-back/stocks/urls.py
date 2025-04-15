from django.urls import path
from . import views


urlpatterns = [
    path('stock-fetch-data/', views.stock_fetch_data, name='stock_fetch_data'),  # 국내 증시 정보 저장
    path('stock-get-data/', views.stock_get_data, name='stock_get_data'),  # 국내 증시 정보 조회
]
