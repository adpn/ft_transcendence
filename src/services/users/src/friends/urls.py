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
from django.urls import path
from . import views

urlpatterns = [
    path('friend_list/', views.get_friend_list, name='get_friend_list'),
    path('friend_requests_list/', views.get_friend_requests_list, name='get_friend_request_list'),
    path('accept_friend/<int:request_id>/', views.accept_friend, name='accept_friend'),
    path('decline_friend/<int:request_id>/', views.decline_friend, name='decline_friend'),
    path('cancel_friend_request/<int:request_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('remove_friend/<int:request_id>/', views.remove_friend, name='remove_friend'),
    path('add_friend/<int:friend_id>/', views.add_friend, name='add_friend')
]
