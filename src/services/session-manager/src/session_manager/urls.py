from django.urls import path
from .views import SessionView

urlpatterns = [
    path('session/', SessionView.as_view(), name='create_session'),
    path('session/<str:session_id>/', SessionView.as_view(), name='session_detail'),
]
