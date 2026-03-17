from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    """Conversation model for chat sessions"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'chatbot'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation {self.id} - {self.title or 'Untitled'}"


class Message(models.Model):
    """Message model for individual chat messages"""
    id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('ai', 'AI')])
    message_text = models.TextField()
    message_type = models.CharField(max_length=10, default='text', choices=[('text', 'Text'), ('voice', 'Voice')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'chatbot'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender}: {self.message_text[:50]}..."
