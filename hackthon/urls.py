from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analyzer.urls')),
    path('api/', include(('api.urls', 'api'), namespace='api')),
    path('auth/', include(('auth_app.urls', 'auth'), namespace='auth')),
    path('chatbot/', include(('chatbot.urls', 'chatbot'), namespace='chatbot')),
    path('voice/', include(('voice_assistant.urls', 'voice_assistant'), namespace='voice_assistant')),
]
