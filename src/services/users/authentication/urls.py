from django.contrib import admin
from django.urls import path, include

import views

path('authenticate/', views.authenticate),
path('create_user/', views.create_user),
path('get_user/', views.get_user)
