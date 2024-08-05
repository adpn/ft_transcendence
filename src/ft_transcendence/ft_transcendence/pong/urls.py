from django.contrib import admin
from django.urls import include, path

from . import views
from .views import ItemListView

urlpatterns = [
	path('', views.index, name="index"),
	path('items/', ItemListView.as_view(), name='item-list'),
	path('login/', views.login_view, name='login'),
	path('logout/', views.logout_view, name='logout'),
	path('signup/', views.signup_view, name='signup')
]
