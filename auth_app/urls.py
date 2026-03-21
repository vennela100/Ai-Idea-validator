from django.urls import path
from . import views
from . import api_views

app_name = 'auth'

urlpatterns = [
    path('login/', views.mock_login, name='login'),
    path('', views.mock_login, name='mock_login'),
    path('logout/', views.logout_view, name='logout_view'),
    path('api/google-login/', api_views.GoogleLoginAPIView.as_view(), name='google_login'),
]
