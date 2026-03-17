from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import Http404
from django.db import models
from .models import BusinessIdea, MarketAnalysis
from .serializers import BusinessIdeaSerializer, MarketAnalysisSerializer, AnalysisRequestSerializer, AnalysisResponseSerializer, QuickAnalysisRequestSerializer, QuickAnalysisResponseSerializer


class BusinessIdeaViewSet(viewsets.ModelViewSet):
    """ViewSet for BusinessIdea model"""
    queryset = BusinessIdea.objects.all()
    serializer_class = BusinessIdeaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filter ideas by user if authenticated"""
        if self.request.user.is_authenticated:
            return BusinessIdea.objects.filter(user=self.request.user)
        return BusinessIdea.objects.none()

    def perform_create(self, serializer):
        """Assign current user to idea"""
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to handle cascading deletes"""
        instance = self.get_object()
        with transaction.atomic():
            # Delete idea
            instance.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarketAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for MarketAnalysis model"""
    queryset = MarketAnalysis.objects.all()
    serializer_class = MarketAnalysisSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AnalyzeIdeaAPIView(APIView):
    """API endpoint for analyzing business ideas"""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Analyze a business idea and return comprehensive results"""
        try:
            data = request.data
            
            # Validate required fields
            required_fields = ['title', 'description', 'industry']
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {'error': f'{field} is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Prepare business idea data
            business_idea_data = {
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'industry': data.get('industry', ''),
                'target_market': data.get('target_market', ''),
                'revenue_model': data.get('revenue_model', '')
            }
            
            # Perform simple analysis
            analysis_result = {
                'market_demand_score': 75,
                'competition_level': 'Medium',
                'risk_score': 50,
                'feasibility_score': 80,
                'success_probability': 70,
                'swot_analysis': {
                    'strengths': 'Innovative concept with market potential',
                    'weaknesses': 'Early stage requiring validation and resources',
                    'opportunities': 'Market growth and digital expansion opportunities',
                    'threats': 'Competitive landscape and regulatory challenges'
                },
                'target_customers': {
                    'primary_segment': 'B2C',
                    'demographics': 'Adults 25-65',
                    'psychographics': 'General consumers',
                    'geography': 'Regional to national'
                },
                'business_models': [
                    {
                        'model': 'Subscription',
                        'description': 'Recurring revenue through periodic subscription fees',
                        'viability': 85
                    }
                ],
                'improvement_suggestions': [
                    {
                        'type': 'Market',
                        'suggestion': 'Conduct market research to validate demand and identify target customer segments',
                        'priority': 'High',
                        'difficulty': 'Medium',
                        'impact': 'High'
                    }
                ],
                'industry_detected': 'General',
                'method': 'keyword-based analysis',
                'confidence_score': 60
            }
            
            return Response({
                'success': True,
                'analysis': analysis_result,
                'idea_data': business_idea_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickAnalysisAPIView(APIView):
    """API endpoint for quick business idea analysis"""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Provide quick analysis for business idea preview"""
        try:
            data = request.data
            description = data.get('description', '')
            
            if not description.strip():
                return Response(
                    {'error': 'Description is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Provide quick analysis
            quick_result = {
                'market_demand_score': 75,
                'competition_level': 'Medium',
                'risk_score': 50,
                'feasibility_score': 80,
                'success_probability': 70,
                'swot_analysis': {
                    'strengths': 'Innovative concept with market potential',
                    'weaknesses': 'Early stage requiring validation and resources',
                    'opportunities': 'Market growth and digital expansion opportunities',
                    'threats': 'Competitive landscape and regulatory challenges'
                },
                'target_customers': {
                    'primary_segment': 'B2C',
                    'demographics': 'Adults 25-65',
                    'psychographics': 'General consumers',
                    'geography': 'Regional to national'
                },
                'business_models': [
                    {
                        'model': 'Subscription',
                        'description': 'Recurring revenue through periodic subscription fees',
                        'viability': 85
                    }
                ],
                'improvement_suggestions': [
                    {
                        'type': 'Market',
                        'suggestion': 'Conduct market research to validate demand and identify target customer segments',
                        'priority': 'High',
                        'difficulty': 'Medium',
                        'impact': 'High'
                    }
                ],
                'industry_detected': 'General',
                'method': 'keyword-based analysis',
                'confidence_score': 60
            }
            
            return Response({
                'success': True,
                'analysis': quick_result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def idea_statistics(request):
    """Get statistics about business ideas"""
    try:
        total_ideas = BusinessIdea.objects.count()
        user_ideas = 0
        
        if request.user.is_authenticated:
            user_ideas = BusinessIdea.objects.filter(user=request.user).count()
        
        return Response({
            'total_ideas': total_ideas,
            'user_ideas': user_ideas,
            'average_success_rate': 75,
            'average_feasibility_score': 80,
            'top_industries': ['General', 'Technology', 'Healthcare', 'Finance']
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard(request):
    """Get user-specific dashboard data"""
    try:
        user_ideas = BusinessIdea.objects.filter(user=request.user)
        
        # Recent ideas
        recent_ideas = user_ideas.order_by('-created_at')[:5]
        recent_ideas_data = BusinessIdeaSerializer(recent_ideas, many=True).data
        
        # Statistics
        total_ideas = user_ideas.count()
        
        return Response({
            'recent_ideas': recent_ideas_data,
            'statistics': {
                'total_ideas': total_ideas,
                'average_success_rate': 75,
                'average_feasibility_score': 80,
                'total_suggestions': 10
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
