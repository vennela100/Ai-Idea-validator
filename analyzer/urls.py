from django.urls import path
from . import views

app_name = 'analyzer'

urlpatterns = [
    # Main App Entry Points
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # Unified Advanced Dashboard (Only real source of truth)
    path('results/', views.results_dashboard, name='results_dashboard'),
    
    # Analysis Endpoints (API)
    path('api/analyze/', views.analyze_idea_api, name='analyze_idea_api'),
    
    # Utilities & Features
    
    # Saved Ideas (TBD integration in future)
    path('save-idea/', views.save_idea, name='save_idea'),
    path('idea/<int:idea_id>/', views.idea_detail, name='idea_detail'),
    
    # Test
    path('test/', views.test_view, name='test_view'),
]
