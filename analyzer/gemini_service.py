import os
import json
import logging
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Advanced AI engine for the Business Idea Validator platform.
    Provides deep strategic analysis and conversational reasoning via Google Gemini.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.model_name = "gemini-2.0-flash"
        self.is_configured = False
        
        if self.api_key and self.api_key != 'your-google-api-key-here':
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                # Chat model instance for ongoing conversations
                self.chat_model = genai.GenerativeModel(self.model_name)
                self.is_configured = True
                logger.info(f"✅ GeminiService configured with {self.model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to configure Gemini: {e}")

    def analyze_idea(self, idea_text: str) -> Optional[Dict[str, Any]]:
        """
        Perform a deep, structured analysis of a startup/business idea.
        Returns a rich JSON object adhering to the strict application schema.
        """
        if not self.is_configured:
            logger.warning("⚠️ Gemini not configured. System will fallback to heuristic engine.")
            return None

        prompt = f"""
You are an elite Silicon Valley Venture Capitalist, Product Strategist, and Startup Advisor.
Perform a deep, brutal, but constructive validation of the following business idea.

BUSINESS IDEA / CONCEPT:
"{idea_text}"

Return YOUR ENTIRE ANALYSIS strictly as a deeply-reasoned JSON object that matches EXACTLY the schema below. 
Do not wrap it in markdown blockquotes, do not add introductory text. Just the raw JSON.
All string fields should be highly professional, specific, and actionable. Avoid generic fluff.

SCHEMA REQUIRED:
{{
    "idea_summary": "A sharp, 1-2 sentence elevator pitch of what this actually is.",
    "problem_statement": "What specific user pain point does this solve?",
    "target_audience": "Who precisely is going to pay for this?",
    "market_demand_score": <int 0-100 indicating real-world market need>,
    "uniqueness_score": <int 0-100 indicating defensive moat and differentiation>,
    "competition_level": "Low", "Medium", "High", or "Very High",
    "revenue_potential": <int 0-100 indicating financial upside and scaling potential>,
    "feasibility_score": <int 0-100 indicating ease of initial execution/MVP>,
    "scalability_score": <int 0-100 indicating ease of 100x growth>,
    "risk_score": <int 0-100 indicating overall founder risk (higher means more dangerous)>,
    "swot_analysis": {{
        "strengths": ["List of 3 concrete strengths"],
        "weaknesses": ["List of 3 immediate weaknesses"],
        "opportunities": ["List of 3 market opportunities"],
        "threats": ["List of 3 external threats/competitors"]
    }},
    "target_customers": [
        "Specific Segment 1 (e.g., 'B2B SaaS Founders with >$1M ARR')",
        "Specific Segment 2"
    ],
    "business_models": [
        "Specific Revenue Model 1 (e.g., 'Tiered B2B Seat License')",
        "Specific Revenue Model 2"
    ],
    "implementation_roadmap": [
        "Phase 1: Validation (Specific action)",
        "Phase 2: MVP Build (Specific action)",
        "Phase 3: Go To Market (Specific action)"
    ],
    "improvement_suggestions": [
        "Brutally honest feedback on what must change to succeed",
        "Strategic pivot suggestion"
    ],
    "final_verdict": "A 2-3 sentence final ruling: Should they build it, pivot, or abandon?",
    "source_engine": "gemini"
}}
"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean up potential markdown formatting from Gemini
            if text.startswith("```json"):
                text = text.split("```json")[1]
            elif text.startswith("```"):
                text = text.split("```")[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
                
            data = json.loads(text.strip())
            
            # Ensure engine is marked correctly
            data['source_engine'] = 'gemini'
            logger.info("✅ Gemini successfully generated deep analysis.")
            return data
            
        except json.JSONDecodeError as je:
            logger.error(f"❌ Gemini returned invalid JSON: {je}. Raw output snippet: {text[:200]}")
            return None
        except Exception as e:
            logger.error(f"❌ Gemini analysis API failed: {e}")
            return None

    def generate_content(self, prompt: str, context: str = "") -> str:
        """
        Generalized content generation for the AI Orchestrator.
        Directly executes the provided prompt while maintaining fallback resilience.
        """
        try:
            response = self.chat_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"❌ Gemini API failed: {e}")
            # Use the smart heuristic engine as a fallback
            return self._smart_heuristic_chat(prompt, context)

    def generate_chat_response(self, user_message: str, idea_context: str = "", chat_history: List[Dict] = None) -> str:
        """
        Maintains backward compatibility for simple chat requests.
        """
        prompt = f"Idea Context: {idea_context}\nChat History: {chat_history}\nUser: {user_message}"
        return self.generate_content(prompt, idea_context)

    def _smart_heuristic_chat(self, message: str, context: str) -> str:
        """
        Sophisticated local reasoning engine that provides context-aware startup advice
        when the Gemini API is hit by rate limits (429) or other outages.
        """
        msg = message.lower()
        ctx = context.lower()
        
        # Determine Industry Context
        industry = "your industry"
        if any(w in ctx or w in msg for w in ['health', 'medical', 'doctor', 'patient']): industry = "HealthTech"
        elif any(w in ctx or w in msg for w in ['bank', 'money', 'finance', 'payment', 'fintech']): industry = "FinTech"
        elif any(w in ctx or w in msg for w in ['software', 'saas', 'enterprise', 'b2b']): industry = "B2B SaaS"
        elif any(w in ctx or w in msg for w in ['ai', 'gpt', 'llm', 'intelligence']): industry = "Generative AI"
        elif any(w in ctx or w in msg for w in ['edu', 'learn', 'school', 'teach']): industry = "EdTech"
        
        # 1. SPECIAL CASE: "In-Depth Analysis" Request
        if any(w in msg for w in ['depth', 'analyze', 'analysis', 'evaluate', 'report', 'brutal']):
            
            # Safely grab the context
            idea_snippet = context.strip() if context else "your startup concept"
            if len(idea_snippet) > 80:
                idea_snippet = idea_snippet[:80] + "..."
                
            report = f"""
### 📊 In-Depth Strategic Report: {industry} Concept
**Analysis built for:** "{idea_snippet}"

#### 🚀 Execution Architecture
To succeed with this **{industry}** idea, you must move beyond the pitch. The current market demand for this specific solution appears high on the surface, but the underlying execution requires navigating a deeply integrated competitive landscape. 

Your first priority must be crystalizing your Unique Value Proposition (UVP). Why would a customer switch from their current workflow to this?

#### ⚖️ SWOT Breakdown
**Strengths:**
* **Pioneer Advantage:** Deep focus on this specific niche pain point.
* **Scalable Logic:** Clean digital architecture allows for fast business model pivots.

**Weaknesses:**
* **Distribution Lag:** High Customer Acquisition Cost (CAC) compared to potential Lifetime Value (LTV).
* **Validation Gaps:** Requires immediate real-world testing before writing code.

**Opportunities / Threats:**
* **Market Expansion:** High growth potential if you can lock in early B2B/B2C evangelists.
* **Market Noise:** Intense competition from well-funded incumbents who can copy features quickly.

#### 🗺️ Strategic Roadmap
1. **Validation:** Avoid building yet. Conduct 10 'Jobs to be Done' user interviews this week to prove they actually have this problem.
2. **MVP (Minimum Viable Product):** Build a functional prototype focusing *strictly* on the core user loop. Cut every other feature.
3. **Go-To-Market:** Target your first 10-20 "Friendly Beta" users for harsh, honest feedback.

#### 💡 Expert Verdict
Your primary focus should be optimizing your **Customer Acquisition Cost (CAC)**. In the {industry} space, the most frequent failure point isn't failing to build the tech—it's failing to survive the sales cycle. If you can prove people will pay for this today, you have a viable business.
"""
            return report

        # 2. Intent Recognition & Strategy Generation
        if any(w in msg for w in ['competitor', 'competition', 'rival']):
            strategy = f"In the **{industry}** space, you're competing against both established incumbents and nimble startups. I recommend mapping out your **uniqueness moat**: Is it proprietary data, a 10x better UX, or a specific niche integration that others ignore?"
        elif any(w in msg for w in ['monetization', 'money', 'revenue', 'price', 'pricing']):
            strategy = f"For a **{industry}** venture, recurring revenue is key. Consider a **tiered subscription model** or a **usage-based fee**. Focus on capturing value where the customer feels the most pain; don't underprice your solution early on."
        elif any(w in msg for w in ['risk', 'fail', 'danger', 'threat']):
            strategy = f"The biggest risk in **{industry}** is usually **product-market fit**—building something nobody actually wants to pay for. Conduct 10-20 deep user interviews before writing a single line of production code. Watch out for regulatory shifts too."
        elif any(w in msg for w in ['marketing', 'growth', 'customer', 'user', 'get']):
            strategy = f"To grow your **{industry}** startup, focus on **Founder-Led Sales** initially. Don't spend on ads yet. Go where your users hang out (LinkedIn, specialized forums, or industry conferences) and solve their problems manually first."
        else:
            strategy = f"That's an interesting point regarding your **{industry}** concept. As you iterate on this idea, keep the **MVP (Minimum Viable Product)** as lean as possible. What is the one 'atomic' feature that delivers 80% of the value?"

        return strategy

# Singleton instance
gemini_service = GeminiService()
