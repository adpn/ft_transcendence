from django.contrib import admin
from django.urls import include, path

from . import views
from .views import ItemListView

#todo: for each path, call the view code
urlpatterns = [
	path('', views.index, name="index"),
	path('items/', ItemListView.as_view(), name='item-list'),
	path('auth/', include("authentication.urls"))
]
