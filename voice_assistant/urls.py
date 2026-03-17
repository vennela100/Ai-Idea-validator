from django.urls import path
from . import views

app_name = 'voice_assistant'

urlpatterns = [
    path('', views.voice_interface, name='voice_interface'),
]
