from django.contrib import admin
from django.urls import include, path

#todo: instead of routing to urls, call views directly, the views make api calls to corresponding backend services.
urlpatterns = [
	path('', include("authentication.urls")),
	path('admin/', admin.site.urls),
]
