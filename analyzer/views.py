import json
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib import messages
from .business_analyzer import analyze_business_idea

logger = logging.getLogger(__name__)

def test_view(request):
    """Simple test view"""
    return HttpResponse("Test view working - AI Idea Validator URLs are loaded")

def home(request):
    """Unified Home Page - Renders the modern landing page for the AI Validator."""
    return render(request, 'analyzer/home.html')

def about(request):
    """About page details."""
    return render(request, 'analyzer/about.html')





def idea_detail(request, idea_id):
    """Stub for viewing a specifically saved idea."""
    return render(request, 'analyzer/idea_detail.html', {'idea_id': idea_id})

def save_idea(request):
    """Stub API endpoint for saving an idea."""
    if request.method == "POST":
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

@csrf_exempt
@require_http_methods(["POST"])
def analyze_idea_api(request):
    """
    Unified API endpoint for deep business idea analysis.
    Uses the new Gemini Service.
    """
    try:
        data = json.loads(request.body)
        
        # Consolidate input fields
        idea_text = data.get('idea', '')
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        industry = data.get('industry', '').strip()
        revenue_model = data.get('revenue_model', '').strip()
        target_market = data.get('target_market', '').strip()
        
        # Reconstruct the idea context for the AI
        if not idea_text:
            idea_parts = [p for p in [title, description, industry, revenue_model, target_market] if p]
            idea_text = " ".join(idea_parts)
            
        if not idea_text:
            return JsonResponse({'success': False, 'error': 'Idea text or description is required'}, status=400)
            
        logger.info(f"API executing analyze_idea for: {idea_text[:30]}...")

        # Deep structured analysis via Gemini + Heuristic wrapper
        analysis_result = analyze_business_idea(idea_text)
        
        if not analysis_result:
             return JsonResponse({
                'success': False,
                'error': 'AI failed to process the idea. Please try again with more details.'
            }, status=500)
            
        # Enrich the output with standard frontend expectations
        analysis_result.update({
            'title': title or "Startup Analysis",
            'description': description,
            'industry': industry,
            'timestamp': timezone.now().isoformat()
        })
        
        # The frontend Javascript specifically looks for `result.analysis` and `result.success`
        return JsonResponse({
            'success': True,
            'analysis': analysis_result
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        logger.error(f"Analyze Idea API crashed: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'}, status=500)

@csrf_exempt
def results_dashboard(request):
    """
    Renders the detailed results dashboard.
    Accepts POST data directly from the frontend JS navigation to load the AI context.
    """
    analysis = None
    if request.method == 'POST':
        try:
            analysis_json = request.POST.get('analysis_data')
            if analysis_json:
                analysis = json.loads(analysis_json)
        except Exception as e:
            logger.error(f"Error parsing analysis data: {e}")
    
    return render(request, 'analyzer/results_dashboard.html', {'analysis': analysis})
