from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('login/', views.mock_login, name='login'),
    path('', views.mock_login, name='mock_login'),
    path('logout/', views.logout_view, name='logout_view'),
]
