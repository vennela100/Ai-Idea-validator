from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_interface, name='chat_interface'),
    path('send/', views.send_message, name='send_message'),
    path('create/', views.create_conversation, name='create_conversation'),
    path('delete/', views.delete_conversation, name='delete_conversation'),
    path('conversation/<int:conversation_id>/', views.get_conversation, name='get_conversation'),
]
