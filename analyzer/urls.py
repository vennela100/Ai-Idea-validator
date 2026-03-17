from django.urls import path
from . import views

app_name = 'analyzer'

urlpatterns = [
    path('', views.modern_home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('results/', views.results_dashboard, name='results_dashboard'),
    path('voice-assistant/', views.voice_assistant, name='voice_assistant'),
    path('demo/', views.demo_mode, name='demo_mode'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('about/', views.about, name='about'),
    path('quick-analysis/', views.quick_analysis, name='quick_analysis'),
    path('analyze/', views.analyze_idea, name='analyze_idea'),
    path('analyze-api/', views.analyze_idea_api, name='analyze_idea_api'),
    path('save-idea/', views.save_idea, name='save_idea'),
    path('idea/<int:idea_id>/', views.idea_detail, name='idea_detail'),
]
