from rest_framework import serializers
from .models import BusinessIdea, MarketAnalysis


class BusinessIdeaSerializer(serializers.ModelSerializer):
    """Serializer for BusinessIdea model"""
    class Meta:
        model = BusinessIdea
        fields = ['id', 'title', 'description', 'industry', 'target_market', 
                 'revenue_model', 'created_at', 'updated_at', 'user']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']


class MarketAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for MarketAnalysis model"""
    business_idea_title = serializers.CharField(source='business_idea.title', read_only=True)
    
    class Meta:
        model = MarketAnalysis
        fields = ['id', 'business_idea', 'business_idea_title', 'market_size', 
                 'market_growth_rate', 'target_audience', 'market_demand_score', 
                 'competition_level', 'created_at']
        read_only_fields = ['id', 'created_at']


class AnalysisRequestSerializer(serializers.Serializer):
    """Serializer for analysis requests"""
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    industry = serializers.CharField(max_length=100)
    target_market = serializers.CharField(required=False, allow_blank=True)
    revenue_model = serializers.CharField(required=False, allow_blank=True)


class AnalysisResponseSerializer(serializers.Serializer):
    """Serializer for analysis responses"""
    success = serializers.BooleanField()
    analysis = serializers.DictField()
    idea_data = AnalysisRequestSerializer(required=False)


class QuickAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for quick analysis requests"""
    description = serializers.CharField()


class QuickAnalysisResponseSerializer(serializers.Serializer):
    """Serializer for quick analysis responses"""
    success = serializers.BooleanField()
    analysis = serializers.DictField()
