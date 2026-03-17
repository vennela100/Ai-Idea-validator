from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'ideas', views.BusinessIdeaViewSet)
router.register(r'market-analysis', views.MarketAnalysisViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('analyze/', views.AnalyzeIdeaAPIView.as_view(), name='api_analyze_idea'),
    path('quick-analysis/', views.QuickAnalysisAPIView.as_view(), name='api_quick_analysis'),
]
