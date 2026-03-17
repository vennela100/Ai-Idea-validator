from django.db import models
from django.contrib.auth.models import User


class BusinessIdea(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    industry = models.CharField(max_length=100)
    target_market = models.CharField(max_length=200, blank=True)
    revenue_model = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_ideas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class MarketAnalysis(models.Model):
    business_idea = models.ForeignKey(BusinessIdea, on_delete=models.CASCADE)
    market_size = models.CharField(max_length=100)
    market_growth_rate = models.FloatField()
    target_audience = models.CharField(max_length=200)
    market_demand_score = models.IntegerField()
    competition_level = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Market Analysis for {self.business_idea.title}"
