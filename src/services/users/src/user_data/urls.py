"""
URL configuration for src project.

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
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('create_user/', views.create_user, name='create_user'),
    path('get_picture/<int:user_id>/', views.get_picture_url, name='get_picture_url'),
    path('profile_pictures/<str:filename>', views.get_image, name='get_image'),
    path('change_profile_picture/', views.change_profile_picture, name='change_profile_picture'),
    path('game_stats/<int:user_id>/', views.game_stats_view, name='game_stats_view'),
    path('personal_stats/', views.personal_stats, name='personal_stats')
]