from django.contrib import admin
from django.urls import include, path

from . import views
from .views import ItemListView

urlpatterns = [
	path('', views.index, name="index"),
	path('items/', ItemListView.as_view(), name='item-list')
]
