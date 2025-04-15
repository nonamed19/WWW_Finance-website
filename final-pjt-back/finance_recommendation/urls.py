"""
URL configuration for finance_recommendation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.generic import TemplateView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('myadmin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="index.html")),  ## TemplateView가 뭔지 ??
    path('accounts/', include('dj_rest_auth.urls')),  # accounts/login, accounts/logout 기능 사용 가능 
    path('accounts/signup/', include('dj_rest_auth.registration.urls')),  # 계정 회원가입
    path('accounts/', include('accounts.urls')),
    path('bankings/', include('bankings.urls')),
    path('currencies/', include('currencies.urls')),
    path('surveys/', include('surveys.urls')),
    path('stocks/', include('stocks.urls')),
    path('economics/', include('economics.urls')),
    path('chats/', include('chats.urls')),
    path("markets/", include("markets.urls")),
    path('recommendations/', include('recommendations.urls')),
    path('subscriptions/', include('subscriptions.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
