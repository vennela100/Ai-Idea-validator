from django.db import models


class VoiceCommand(models.Model):
    session_id = models.CharField(max_length=255, blank=True, null=True)
    command = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'voice_assistant'
        ordering = ['-timestamp']


class VoiceSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True, primary_key=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'voice_assistant'
        ordering = ['-updated_at']
