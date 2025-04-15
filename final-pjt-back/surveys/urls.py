from django.urls import path
from . import views


urlpatterns = [
    path('submit-survey/', views.submit_survey, name='submit-survey'),  # 설문 제출

]
