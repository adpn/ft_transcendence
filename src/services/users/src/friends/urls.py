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
    path('friend_list/', views.get_friend_list, name='get_friend_list'),
    path('friend_requests_list/', views.get_friend_requests_list, name='get_friend_request_list'),
    path('accept_friend/<int:request_id>', views.accept_friend, name='accept_friend'),
    path('refuse_friend/<int:request_id>', views.refuse_friend, name='refuse_friend')
]
