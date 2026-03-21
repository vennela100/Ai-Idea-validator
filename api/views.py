from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction, models
from .models import BusinessIdea, MarketAnalysis
from .serializers import (
    BusinessIdeaSerializer, MarketAnalysisSerializer,
    AnalysisRequestSerializer, AnalysisResponseSerializer,
    QuickAnalysisRequestSerializer, QuickAnalysisResponseSerializer,
)
from analyzer.services.orchestrator import AIOrchestrator


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
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarketAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for MarketAnalysis model"""
    queryset = MarketAnalysis.objects.all()
    serializer_class = MarketAnalysisSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AnalyzeIdeaAPIView(APIView):
    """
    API endpoint for full business idea analysis.
    Routes through the shared AIOrchestrator for consistent behaviour
    across Web, Voice, Chat, and API surfaces.
    """
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
                        {'success': False, 'error': f'{field} is required'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Build a rich idea description for the AI
            idea_parts = [
                data.get('title', ''),
                data.get('description', ''),
                f"Industry: {data.get('industry', '')}",
            ]
            if data.get('target_market'):
                idea_parts.append(f"Target Market: {data['target_market']}")
            if data.get('revenue_model'):
                idea_parts.append(f"Revenue Model: {data['revenue_model']}")

            idea_text = ". ".join(p for p in idea_parts if p)

            # --- Route through the AI Orchestrator ---
            result = AIOrchestrator.process_request(
                command=idea_text,
                source='analyzer'   # forces full_analysis intent
            )

            # Build response
            analysis = result.get('analysis') or {}
            return Response({
                'success': result.get('success', False),
                'mode': 'full_analysis',
                'analysis': analysis,
                'idea_data': {
                    'title': data.get('title', ''),
                    'description': data.get('description', ''),
                    'industry': data.get('industry', ''),
                    'target_market': data.get('target_market', ''),
                    'revenue_model': data.get('revenue_model', ''),
                },
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuickAnalysisAPIView(APIView):
    """
    API endpoint for quick / strategic business idea analysis.
    Also routes through the AIOrchestrator; the intent router
    will classify short descriptions appropriately (clarification or analysis).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Provide quick analysis for business idea preview"""
        try:
            data = request.data
            description = data.get('description', '').strip()

            if not description:
                return Response(
                    {'success': False, 'error': 'Description is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # --- Route through the AI Orchestrator ---
            # source='web' lets the IntentRouter decide between
            # full_analysis, strategic_chat, or clarification based on input length/clues.
            result = AIOrchestrator.process_request(
                command=description,
                source='web'
            )

            # Determine friendly mode label
            if result.get('is_analysis'):
                mode = 'full_analysis'
                analysis = result.get('analysis', {})
            else:
                mode = 'strategic_chat' if len(description) > 40 else 'clarification'
                analysis = {'response': result.get('response', '')}

            return Response({
                'success': result.get('success', False),
                'mode': mode,
                'analysis': analysis,
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
