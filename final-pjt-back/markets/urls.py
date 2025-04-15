from django.urls import path
from .views import get_indices_data

urlpatterns = [
    path("indices/", get_indices_data, name="get_indices_data"),
]
