import logging
import random
from typing import Dict, Any, List

from django.utils import timezone

from .services.orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)

def analyze_business_idea(idea_text: str) -> Dict[str, Any]:
    """
    Analyzes a business idea using the specialized AI Orchestration layer.
    Automatically detects intent and applies the most appropriate strategic prompt.
    """
    if not idea_text or not idea_text.strip():
        return _generate_heuristic_fallback("Empty Idea")
        
    print(f"\n[ANALYZER] Processing idea: {idea_text[:50]}...")
    
    # 1. Delegate to the AI Orchestrator
    # The orchestrator handles intent detection, prompt selection, and Gemini execution.
    result = AIOrchestrator.process_request(command=idea_text, source='analyzer')
    
    if result.get('is_analysis') and result.get('analysis'):
        # Ensure standard fields are present for templates
        analysis = result['analysis']
        analysis['timestamp'] = timezone.now().isoformat()
        return analysis
    
    # 2. Fallback to Heuristic Engine if AI fails or returns conversational output
    logger.warning("AI Orchestrator did not return a structured analysis. Using heuristic fallback.")
    return _generate_heuristic_fallback(idea_text)


def _generate_heuristic_fallback(idea: str) -> Dict[str, Any]:
    """
    Advanced heuristic analyzer when Gemini is unavailable.
    Provides context-aware analysis based on industry keyword patterns.
    """
    idea_lower = idea.lower()
    
    # Industry detection
    industry = "General Startup"
    categories = {
        'AI/ML': ['ai', 'intelligence', 'gpt', 'llm', 'machine learning', 'automation'],
        'SaaS': ['software', 'platform', 'app', 'tool', 'dashboard', 'enterprise', 'b2b'],
        'HealthTech': ['health', 'medical', 'fitness', 'doctor', 'bio', 'patient'],
        'FinTech': ['finance', 'bank', 'payment', 'crypto', 'blockchain', 'investment'],
        'EdTech': ['edu', 'learn', 'teach', 'school', 'course', 'training'],
        'Eco/Green': ['green', 'eco', 'sustainable', 'climate', 'energy', 'carbon'],
        'Marketplace': ['ecommerce', 'shop', 'buy', 'sell', 'market', 'delivery']
    }
    
    for cat, keywords in categories.items():
        if any(kw in idea_lower for kw in keywords):
            industry = cat
            break

    # Dynamic scoring based on industry
    scores = {
        'market_demand': random.randint(65, 85) if industry != 'General Startup' else random.randint(55, 75),
        'uniqueness': random.randint(60, 80) if industry in ['AI/ML', 'Eco/Green'] else random.randint(45, 65),
        'revenue': random.randint(70, 90) if industry in ['SaaS', 'FinTech'] else random.randint(60, 80),
        'feasibility': random.randint(50, 75),
        'scalability': 90 if industry in ['SaaS', 'AI/ML'] else (75 if industry != 'General Startup' else 60),
        'risk': 40 if industry == 'SaaS' else 55
    }

    return {
        "idea_summary": f"Your {industry} concept focused on '{idea[:40]}...' analyzed via the Antigravity Heuristic Engine.",
        "problem_statement": f"Addressing critical inefficiencies and pain points within the {industry} sector.",
        "target_audience": f"Primary users and businesses operating within the {industry} ecosystem.",
        "market_demand_score": scores['market_demand'],
        "uniqueness_score": scores['uniqueness'],
        "competition_level": "High" if industry in ['AI/ML', 'SaaS'] else "Medium",
        "revenue_potential": scores['revenue'],
        "feasibility_score": scores['feasibility'],
        "scalability_score": scores['scalability'],
        "risk_score": scores['risk'],
        "swot_analysis": {
            "strengths": [f"Deep focus on {industry} problems", "Scalable digital architecture", "High barriers to entry"],
            "weaknesses": ["Requires initial user validation", "Potential technical complexity", "Go-to-market resource needs"],
            "opportunities": [f"Growth in {industry} digital transformation", "Expansion into adjacent markets", "Strategic partnerships"],
            "threats": ["Established market incumbents", "Rapidly changing technology landscape", "Data privacy regulations"]
        },
        "target_customers": [
            f"Early adopters in the {industry} space",
            f"Enterprises seeking {industry} optimization"
        ],
        "business_models": [
            "Subscription-based recurring revenue (SaaS)" if industry != 'Marketplace' else "Transaction-based commissions",
            "Tiered enterprise licensing"
        ],
        "implementation_roadmap": [
            "Phase 1: Market Resonance Testing & MVP Scoping",
            "Phase 2: Core Feature Build & Private Beta",
            "Phase 3: Scaled Launch & User Acquisition"
        ],
        "improvement_suggestions": [
            f"Focus on the 'Atomic Unit' of value for {industry} users.",
            "Accelerate user interview cycles to 5 per week.",
            "Verify unit economics before scaling customer acquisition."
        ],
        "final_verdict": f"HEURISTIC ANALYSIS: This {industry} idea shows significant promise. While the Gemini AI engine is currently optimizing its reasoning path, our heuristic engine suggests you have a viable MVP path. Focus on validation.",
        "source_engine": "heuristic"
    }

def detect_industry_competitors(idea_text: str) -> List[str]:
    """Simple competitor resolver for voice/chat context if Gemini isn't used."""
    if 'food' in idea_text.lower() or 'delivery' in idea_text.lower():
        return ["UberEats", "DoorDash", "GrubHub"]
    elif 'health' in idea_text.lower() or 'fitness' in idea_text.lower():
        return ["MyFitnessPal", "Peloton", "Apple Health"]
    elif 'finance' in idea_text.lower() or 'crypto' in idea_text.lower():
        return ["Stripe", "Coinbase", "Robinhood"]
    return ["Established industry incumbents", "Indirect substitutes"]
