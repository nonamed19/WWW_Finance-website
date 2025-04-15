from django.urls import path
from . import views


urlpatterns = [
    path('subscribe/', views.toggle_subscribed_product, name='toggle_subscribed_product'),
    path('my-subscriptions/', views.my_subscribed_products, name='my_subscribed_products'),
]
