from django.urls import path, re_path
from . import views
from django.views.static import serve
from django.conf import settings

urlpatterns = [
	path('', views.index, name="index"),
	re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
	re_path(r'^.*$', views.index)
]
