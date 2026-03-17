from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib import messages
from .business_analyzer import analyze_business_idea, detect_industry_competitors
import json


def home(request):
    """Home page for analyzer"""
    return render(request, 'analyzer/home.html')


def demo_mode(request):
    """Demo mode page"""
    return render(request, 'analyzer/demo_mode.html')


def about(request):
    """About page"""
    return render(request, 'analyzer/about.html')


@csrf_exempt
@require_http_methods(["POST"])
def quick_analysis(request):
    """Quick analysis API endpoint"""
    try:
        data = json.loads(request.body)
        description = data.get('description', '')
        
        if not description.strip():
            return JsonResponse({
                'success': False,
                'error': 'Description is required'
            })
        
        # Perform quick analysis
        analysis = analyze_business_idea({
            'title': 'Quick Analysis',
            'description': description,
            'industry': 'General'
        })
        
        return JsonResponse({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def modern_home(request):
    """Modern AI startup home page"""
    return render(request, 'analyzer/modern_home.html')


@login_required
def home(request):
    """Home page"""
    return render(request, 'analyzer/home.html')


@login_required
def dashboard(request):
    """Dashboard page"""
    return render(request, 'analyzer/dashboard.html')


@login_required
def analytics_dashboard(request):
    """Analytics dashboard"""
    return render(request, 'analyzer/analytics_dashboard.html')


@login_required
def idea_detail(request, idea_id):
    """Idea detail page"""
    # This is a placeholder - you'll need to implement the actual logic
    # to fetch the idea from the database
    return render(request, 'analyzer/idea_detail.html', {'idea_id': idea_id})


@login_required
def voice_assistant(request):
    """Voice assistant page"""
    return render(request, 'analyzer/voice_assistant.html')


@login_required
def results_dashboard(request):
    """Results dashboard page"""
    return render(request, 'analyzer/results_dashboard.html')


def analyze_idea(request):
    """
    Business idea analysis view with proper error handling and variable management.
    
    Handles both GET (display form) and POST (process analysis) requests.
    """
    # Initialize analysis variable to ensure it's always defined
    analysis = None
    form_data = {}
    
    if request.method == 'POST':
        try:
            # Get form data with validation
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            industry = request.POST.get('industry', '').strip()
            target_audience = request.POST.get('target_audience', '').strip()
            revenue_model = request.POST.get('revenue_model', '').strip()
            location = request.POST.get('location', '').strip()
            
            # Validate required fields
            if not title or not description:
                messages.error(request, 'Title and description are required fields.')
                return render(request, 'analyzer/analyze_idea.html', {
                    'form_data': {
                        'title': title,
                        'description': description,
                        'industry': industry,
                        'target_audience': target_audience,
                        'revenue_model': revenue_model,
                        'location': location
                    }
                })
            
            # Store form data for template
            form_data = {
                'title': title,
                'description': description,
                'industry': industry or 'Not specified',
                'target_audience': target_audience or 'Not specified',
                'revenue_model': revenue_model or 'Not specified',
                'location': location or 'Global'
            }
            
            # Combine all text for analysis
            full_text = f"{title} {description} {industry} {target_audience} {revenue_model} {location}"
            
            # Perform AI analysis with proper error handling
            try:
                from .business_analyzer import analyze_business_idea
                analysis_result = analyze_business_idea(full_text)
                
                # Ensure analysis_result is a dictionary
                if not isinstance(analysis_result, dict):
                    analysis_result = {}
                
                # Add form data and metadata to analysis
                analysis = analysis_result.copy()
                analysis.update({
                    'title': title,
                    'description': description,
                    'industry': industry or 'Not specified',
                    'target_audience': target_audience or 'Not specified',
                    'revenue_model': revenue_model or 'Not specified',
                    'location': location or 'Global',
                    'timestamp': timezone.now().isoformat(),
                    'analysis_successful': True,
                    'error': None
                })
                
                # Ensure required fields exist with defaults
                analysis.setdefault('market_demand_score', 75)
                analysis.setdefault('competition_level', 'Medium')
                analysis.setdefault('risk_score', 50)
                analysis.setdefault('feasibility_score', 70)
                analysis.setdefault('success_probability', 68)
                analysis.setdefault('swot_analysis', {})
                analysis.setdefault('target_customers', {})
                analysis.setdefault('business_models', [])
                analysis.setdefault('improvement_suggestions', [])
                
                messages.success(request, 'Analysis completed successfully!')
                
                # Render results page with analysis
                return render(request, 'analyzer/analyze_results.html', {
                    'analysis': analysis,
                    'form_data': form_data,
                    'success': True
                })
                
            except ImportError as e:
                messages.error(request, 'Analysis service unavailable. Please try again later.')
                return render(request, 'analyzer/analyze_idea.html', {
                    'form_data': form_data,
                    'error': 'Analysis service unavailable'
                })
                
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            
            # Create fallback analysis to prevent page crashes
            analysis = {
                'title': title if 'title' in locals() else 'Unknown',
                'description': description if 'description' in locals() else 'Analysis failed',
                'industry': industry if 'industry' in locals() else 'Not specified',
                'target_audience': target_audience if 'target_audience' in locals() else 'Not specified',
                'revenue_model': revenue_model if 'revenue_model' in locals() else 'Not specified',
                'location': location if 'location' in locals() else 'Global',
                'timestamp': timezone.now().isoformat(),
                'market_demand_score': 50,
                'competition_level': 'Unknown',
                'risk_score': 50,
                'feasibility_score': 50,
                'success_probability': 50,
                'swot_analysis': {
                    'strengths': ['Unable to analyze due to technical issues'],
                    'weaknesses': ['Analysis service temporarily unavailable'],
                    'opportunities': ['Try again later'],
                    'threats': ['Technical difficulties']
                },
                'target_customers': {'primary': 'Analysis failed'},
                'business_models': ['Unable to determine'],
                'improvement_suggestions': ['Please try again later'],
                'analysis_successful': False,
                'error': str(e)
            }
            
            messages.warning(request, f'Analysis encountered an issue: {str(e)}. Showing limited results.')
            
            # Still render results page with fallback analysis
            return render(request, 'analyzer/analyze_results.html', {
                'analysis': analysis,
                'form_data': form_data,
                'success': False,
                'error': str(e)
            })
    
    # GET request - show the form
    return render(request, 'analyzer/analyze_idea.html', {
        'form_data': {},
        'analysis': None
    })


@login_required
def dashboard(request):
    """Analytics dashboard page"""
    return render(request, 'analyzer/dashboard.html')


def save_idea(request):
    """Save idea endpoint"""
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        industry = request.POST.get("industry")
        target_market = request.POST.get("target_market")
        revenue_model = request.POST.get("revenue_model")
        analysis_data = request.POST.get("analysis_data")

        # You can save to DB later
        print(title, description)

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})


@csrf_exempt
def analyze_idea_api(request):
    """API endpoint for business idea analysis"""
    print(f"DEBUG: analyze_idea_api called with method: {request.method}")
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"DEBUG: Received data: {data}")
            
            idea_text = data.get('idea', '')
            title = data.get('title', '')
            description = data.get('description', '')
            industry = data.get('industry', '')
            revenue_model = data.get('revenue_model', '')
            target_market = data.get('target_market', '')
            quick = data.get('quick', False)
            
            print(f"DEBUG: Extracted fields - title: {title}, description: {description}, industry: {industry}")
            print(f"DEBUG: User message (idea): {idea_text}")
            
            # Combine all text for analysis
            full_text = f"{title} {description} {industry} {revenue_model} {target_market}"
            print(f"DEBUG: Full text for analysis: {full_text}")
            
            # Use the business analyzer service
            from .business_analyzer import analyze_business_idea
            print("DEBUG: Calling analyze_business_idea function...")
            analysis_result = analyze_business_idea(full_text)
            print(f"DEBUG: Analysis result: {analysis_result}")
            print(f"DEBUG: Analysis result type: {type(analysis_result)}")
            
            # Check if analysis_result is valid
            if analysis_result is None:
                print("DEBUG: Analysis result is None, creating fallback")
                analysis_result = {
                    'market_demand_score': 75,
                    'competition_level': 'Medium',
                    'risk_score': 50,
                    'feasibility_score': 70,
                    'success_probability': 73,
                    'recommendations': 'Your business idea has potential. Consider market research and validation.'
                }
            
            print(f"DEBUG: Final analysis result: {analysis_result}")
            
            # Add additional metadata
            analysis_result.update({
                'title': title,
                'description': description,
                'industry': industry,
                'revenue_model': revenue_model,
                'target_market': target_market,
                'quick_mode': quick,
                'timestamp': timezone.now().isoformat()
            })
            
            response_data = {
                'success': True,
                'analysis': analysis_result,
                'validation_report': {
                    'overall_score': analysis_result.get('success_probability', 75),
                    'recommendation': 'Proceed' if analysis_result.get('success_probability', 75) > 70 else 'Reconsider'
                }
            }
            print(f"DEBUG: Response data: {response_data}")
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            print("DEBUG: JSON decode error")
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON format'
            })
        except Exception as e:
            print(f"DEBUG: General exception: {e}")
            print(f"DEBUG: Exception type: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Only POST method allowed'
    })
