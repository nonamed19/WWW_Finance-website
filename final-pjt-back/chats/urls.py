# chat/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('chat-message/', views.chat_message, name='chat_message'),  # ChatGPT 대화 데이터 저장
    path('chat-history/', views.chat_history, name='chat_history'),  # ChatGPT 대화 데이터 조회
]