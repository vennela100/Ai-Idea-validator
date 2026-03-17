import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from analyzer.business_analyzer import analyze_business_idea, detect_industry_competitors


class AIChatbot:
    """
    AI-powered chatbot for business idea assistance.
    Combines OpenAI API with rule-based NLP for comprehensive responses.
    """
    
    def __init__(self):
        self.intents = self._initialize_intents()
        self.quick_responses = self._initialize_quick_responses()
        self.conversation_context = {}
        
    def _initialize_intents(self) -> Dict[str, Dict[str, Any]]:
        """Initialize chat intents with keywords and responses"""
        return {
            'idea_evaluation': {
                'keywords': [
                    'good idea', 'bad idea', 'evaluate', 'assess', 'is my idea good',
                    'what do you think', 'opinion', 'feedback', 'review'
                ],
                'response_template': self._generate_idea_evaluation_response,
                'requires_analysis': True,
                'priority': 1
            },
            'competitor_analysis': {
                'keywords': [
                    'competitors', 'competition', 'competitor analysis', 'who are competitors',
                    'market players', 'rivals', 'alternatives', 'similar companies'
                ],
                'response_template': self._generate_competitor_response,
                'requires_analysis': True,
                'priority': 2
            },
            'improvement_suggestions': {
                'keywords': [
                    'improve', 'better', 'enhance', 'optimize', 'fix', 'upgrade',
                    'how can i improve', 'suggestions', 'recommendations', 'advice'
                ],
                'response_template': self._generate_improvement_response,
                'requires_analysis': True,
                'priority': 2
            },
            'market_research': {
                'keywords': [
                    'market research', 'market size', 'market analysis', 'demand',
                    'target market', 'customer base', 'market trends'
                ],
                'response_template': self._generate_market_response,
                'requires_analysis': True,
                'priority': 3
            },
            'business_model': {
                'keywords': [
                    'business model', 'revenue model', 'monetization', 'how to make money',
                    'pricing', 'subscription', 'freemium', 'marketplace'
                ],
                'response_template': self._generate_business_model_response,
                'requires_analysis': True,
                'priority': 3
            },
            'funding_advice': {
                'keywords': [
                    'funding', 'investment', 'investors', 'venture capital',
                    'seed funding', 'angel investors', 'pitch deck', 'raise money'
                ],
                'response_template': self._generate_funding_response,
                'requires_analysis': False,
                'priority': 4
            },
            'startup_basics': {
                'keywords': [
                    'startup', 'entrepreneur', 'business', 'company',
                    'how to start', 'getting started', 'first steps'
                ],
                'response_template': self._generate_startup_response,
                'requires_analysis': False,
                'priority': 5
            },
            'risk_assessment': {
                'keywords': [
                    'risk', 'risks', 'danger', 'challenges', 'obstacles',
                    'what could go wrong', 'failure', 'pitfalls'
                ],
                'response_template': self._generate_risk_response,
                'requires_analysis': True,
                'priority': 2
            },
            'technical_help': {
                'keywords': [
                    'how to use', 'help', 'tutorial', 'guide', 'instructions',
                    'feature', 'functionality', 'how does it work'
                ],
                'response_template': self._generate_help_response,
                'requires_analysis': False,
                'priority': 6
            },
            'greeting': {
                'keywords': [
                    'hello', 'hi', 'hey', 'good morning', 'good afternoon',
                    'good evening', 'thanks', 'thank you'
                ],
                'response_template': self._generate_greeting_response,
                'requires_analysis': False,
                'priority': 7
            }
        }
    
    def _initialize_quick_responses(self) -> Dict[str, str]:
        """Initialize quick responses for common questions"""
        return {
            'what_is_this': "I'm an AI Business Idea Validator chatbot designed to help entrepreneurs analyze and improve their startup ideas. I can evaluate your business concepts, suggest improvements, and provide market insights.",
            
            'capabilities': "I can help you with:\n• Business idea evaluation\n• Competitor analysis\n• Market research insights\n• Improvement suggestions\n• Business model recommendations\n• Funding advice\n• Risk assessment\n• Startup guidance",
            
            'how_to_use': "Simply describe your business idea or ask me questions about entrepreneurship. For example: 'I want to create an AI-powered fitness app' or 'What competitors exist in the food delivery space?'",
            
            'privacy': "Your conversations are private and secure. I don't store personal information beyond what's necessary for providing better responses.",
            
            'limitations': "I provide business guidance based on industry patterns and analysis. For legal, financial, or specific professional advice, please consult qualified experts.",
            
            'success_stories': "Many successful startups have used AI analysis to refine their ideas. Common success factors include clear problem-solving, strong market demand, and scalable business models."
        }
    
    def detect_intent(self, message: str) -> Tuple[str, float]:
        """Detect user intent from message using keyword matching"""
        message_lower = message.lower()
        best_intent = 'unknown'
        best_score = 0.0
        
        for intent_name, intent_data in self.intents.items():
            score = 0.0
            keywords = intent_data['keywords']
            
            for keyword in keywords:
                if keyword in message_lower:
                    # Weight by keyword length and exact match
                    weight = len(keyword) / len(message_lower)
                    if keyword == message_lower.strip():
                        weight *= 2.0  # Boost exact matches
                    score += weight
            
            if score > best_score:
                best_score = score
                best_intent = intent_name
        
        return best_intent, min(best_score * 100, 100.0)
    
    def extract_business_idea(self, message: str) -> Optional[str]:
        """Extract business idea from user message"""
        # Look for business idea patterns
        patterns = [
            r'(?:i want to|i have|i\'m creating|my idea is|startup|business|app|service|product)\s+(.+?)(?:\.|\?|$)',
            r'(?:create|build|develop|launch)\s+(.+?)(?:\.|\?|$)',
            r'(?:business idea|startup concept|product idea):\s+(.+?)(?:\.|\?|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def process_message(self, message: str, user_id: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        Process user message and generate AI response
        
        Args:
            message: User input message
            user_id: User identifier for context
            session_id: Session identifier for conversation tracking
            
        Returns:
            Dictionary containing response and metadata
        """
        start_time = time.time()
        
        # Extract and store business idea for conversation memory
        business_idea = self.extract_business_idea(message)
        
        # Load previous context if no business idea in current message
        if not business_idea and session_id:
            context = self.get_conversation_context(session_id)
            business_idea = context.get("business_idea", "")
        
        # Save business idea to memory for future messages
        if business_idea and session_id:
            self.update_conversation_context(session_id, {
                "business_idea": business_idea,
                "last_message": message,
                "timestamp": time.time()
            })
        
        # Detect intent
        intent, confidence = self.detect_intent(message)
        
        # Generate response based on intent
        responses = []
        
        # Check for multiple intents in the message
        message_lower = message.lower()
        
        if "competitor" in message_lower or "competition" in message_lower:
            responses.append(self._generate_competitor_response(message, business_idea, analysis))
        
        if "risk" in message_lower or "danger" in message_lower or "challenge" in message_lower:
            responses.append(self._generate_risk_response(message, business_idea, analysis))
            
        if "improve" in message_lower or "better" in message_lower or "enhance" in message_lower:
            responses.append(self._generate_improvement_response(message, business_idea, analysis))
            
        if "market" in message_lower or "demand" in message_lower or "research" in message_lower:
            responses.append(self._generate_market_response(message, business_idea, analysis))
            
        if "evaluate" in message_lower or "good idea" in message_lower or "assess" in message_lower:
            responses.append(self._generate_idea_evaluation_response(message, business_idea, analysis))
            
        # If no specific intent detected, use fallback
        if not responses:
            responses.append(self._generate_fallback_response(message))
        
        # Combine multiple responses
        if len(responses) > 1:
            response = "\n\n".join(responses)
        else:
            response = responses[0] if responses else self._generate_fallback_response(message)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        return {
            'response': response,
            'intent': intent,
            'confidence': confidence,
            'response_time': response_time,
            'business_idea': business_idea,
            'suggestions': self._generate_followup_suggestions(intent)
        }
    
    def _generate_idea_evaluation_response(self, message: str, business_idea: str, analysis: Dict[str, Any]) -> str:
        """Generate response for idea evaluation"""
        if not analysis:
            return "I'd be happy to evaluate your business idea! Please describe your concept in detail, including what problem it solves and who your target customers are."
        
        score = (analysis['market_demand_score'] + analysis['feasibility_score']) / 2
        
        response = f"📊 **Evaluation of: {business_idea}**\n\n"
        response += f"**Overall Score: {score:.1f}/100**\n\n"
        
        if score >= 75:
            response += "🎉 **Excellent!** Your idea shows strong potential with high market demand and feasibility.\n\n"
        elif score >= 60:
            response += "👍 **Good!** Your idea has solid potential with some areas for improvement.\n\n"
        elif score >= 40:
            response += "⚠️ **Moderate.** Your idea has potential but needs refinement in key areas.\n\n"
        else:
            response += "🔧 **Needs Work.** Consider significant revisions to improve viability.\n\n"
        
        response += f"**Key Metrics for '{business_idea}':**\n"
        response += f"• Market Demand: {analysis['market_demand_score']}/100\n"
        response += f"• Competition Level: {analysis['competition_level']}\n"
        response += f"• Risk Score: {analysis['risk_score']}/100\n"
        response += f"• Success Probability: {analysis['success_probability']}%\n\n"
        
        response += "**Next Steps:**\n"
        response += "1. Validate with target customers\n"
        response += "2. Research competitors in detail\n"
        response += "3. Create a minimum viable product\n"
        response += "4. Test market response\n\n"
        
        response += f"Based on your idea about '{business_idea}', would you like me to suggest specific improvements or analyze competitors in more detail?"
        
        return response
    
    def _generate_competitor_response(self, message: str, business_idea: str, analysis: Dict[str, Any]) -> str:
        """Generate response for competitor analysis"""
        if not analysis:
            return "I can help you analyze competitors! Tell me about your business idea or industry, and I'll identify key players and market dynamics."
        
        response = f"🏢 **Competitor Analysis for: {business_idea}**\n\n"
        response += f"**Industry:** {analysis.get('industry_detected', 'General')}\n"
        response += f"**Competition Level:** {analysis['competition_level']}\n\n"
        
        response += "**Key Insights:**\n"
        
        # Get industry-specific competitors
        competitors = detect_industry_competitors(business_idea)
        
        response += "**Major Competitors:**\n"
        for i, competitor in enumerate(competitors[:5], 1):
            response += f"{i}. {competitor}\n"
        
        response += "\n**Key Insights:**\n"
        
        if analysis['competition_level'] in ['High', 'Very High']:
            response += "• This is a competitive market with established players\n"
            response += "• Focus on differentiation and unique value proposition\n"
            response += "• Consider underserved niches within the market\n"
            response += "• Build strong brand identity and customer loyalty\n\n"
        elif analysis['competition_level'] == 'Medium':
            response += "• Moderate competition with room for new entrants\n"
            response += "• Focus on innovation and customer experience\n"
            response += "• Build partnerships to accelerate market entry\n\n"
        else:
            response += "• Low competition indicates market opportunity\n"
            response += "• First-mover advantage potential\n"
            response += "• Focus on building barriers to entry\n\n"
        
        response += "**Competitive Strategy Recommendations:**\n"
        response += f"1. **Differentiation:** What makes your '{business_idea}' unique?\n"
        response += "2. **Niche Focus:** Target specific customer segments\n"
        response += "3. **Innovation:** Technology or business model innovation\n"
        response += "4. **Customer Experience:** Superior service or user experience\n\n"
        
        response += f"Would you like me to analyze specific competitors for '{business_idea}' or suggest differentiation strategies?\n\n"
        
        return response
    
    def _generate_improvement_response(self, message: str, business_idea: str, analysis: Dict[str, Any]) -> str:
        """Generate response with improvement suggestions"""
        if not analysis:
            return "I can provide specific improvement suggestions! Please describe your business idea, and I'll analyze it and recommend actionable improvements."
        
        response = f"🚀 **Improvement Suggestions for: {business_idea}**\n\n"
        
        suggestions = analysis.get('improvement_suggestions', [])
        if suggestions:
            response += "**Top Priority Improvements:**\n"
            for i, suggestion in enumerate(suggestions[:3], 1):
                priority_emoji = "🔴" if suggestion['priority'] == 'High' else "🟡" if suggestion['priority'] == 'Medium' else "🟢"
                response += f"{i}. {priority_emoji} **{suggestion['type']}**: {suggestion['suggestion']}\n"
                response += f"   *Difficulty: {suggestion['difficulty']} | Impact: {suggestion['impact']}\n\n"
        
        # Add general improvement areas
        response += "**Key Improvement Areas for '{business_idea}':**\n"
        response += "💡 **Product/Service:**\n"
        response += "• Refine core value proposition\n"
        response += "• Enhance user experience\n"
        response += "• Add unique features\n\n"
        
        response += "📈 **Business Model:**\n"
        response += "• Diversify revenue streams\n"
        response += "• Optimize pricing strategy\n"
        response += "• Explore subscription models\n\n"
        
        response += "🎯 **Market Strategy:**\n"
        response += "• Define clear target audience\n"
        response += "• Develop strong brand identity\n"
        response += "• Create effective marketing channels\n\n"
        
        response += f"Which improvement area would you like to explore for '{business_idea}'?"
        
        return response
    
    def _generate_market_response(self, message: str, business_idea: str, analysis: Dict[str, Any]) -> str:
        """Generate market research response"""
        if not analysis:
            return "I can provide market research insights! Tell me about your business idea or industry, and I'll analyze market potential, trends, and opportunities."
        
        response = f"📊 **Market Research for: {business_idea}**\n\n"
        
        target_customers = analysis.get('target_customers', {})
        response += f"**Market Demand Score:** {analysis['market_demand_score']}/100\n\n"
        
        response += f"**Target Customer Profile for '{business_idea}':**\n"
        response += f"• Segment: {target_customers.get('primary_segment', 'General')}\n"
        response += f"• Demographics: {target_customers.get('demographics', 'Adults 25-65')}\n"
        response += f"• Geography: {target_customers.get('geography', 'Regional to national')}\n\n"
        
        response += "**Market Opportunities:**\n"
        swot = analysis.get('swot_analysis', {})
        if swot.get('opportunities'):
            response += f"• {swot['opportunities']}\n\n"
        
        response += f"**Market Size & Growth for '{business_idea}':**\n"
        response += f"• Current demand indicates {'Large' if analysis['market_demand_score'] > 70 else 'Medium' if analysis['market_demand_score'] > 50 else 'Small'} market potential\n"
        response += "• Growth trajectory based on industry trends\n"
        response += f"• Success probability: {analysis['success_probability']}%\n\n"
        
        response += "**Next Steps:**\n"
        response += "1. Conduct customer interviews\n"
        response += "2. Analyze market size quantitatively\n"
        response += "3. Study industry trends and forecasts\n"
        response += "4. Identify untapped segments\n\n"
        
        response += f"Would you like me to help you create a detailed market research plan for '{business_idea}'?"
        
        return response
    
    def _generate_business_model_response(self, message: str, business_idea: str, analysis: Dict[str, Any]) -> str:
        """Generate business model recommendations"""
        response = "💼 **Business Model Recommendations**\n\n"
        
        if analysis:
            business_models = analysis.get('business_models', [])
            if business_models:
                response += "**Recommended Models for Your Idea:**\n"
                for i, model in enumerate(business_models, 1):
                    response += f"{i}. **{model['model']}** (Viability: {model['viability']}%)\n"
                    response += f"   • {model['description']}\n"
                    response += f"   • Revenue: {model['revenue_streams']}\n"
                    response += f"   • Why: {model['match_reason']}\n\n"
        
        response += "**Popular Business Models:**\n"
        response += "🔄 **Subscription Model:**\n"
        response += "• Predictable recurring revenue\n"
        response += "• High customer lifetime value\n"
        response += "• Best for SaaS, content, services\n\n"
        
        response += "🏪 **Marketplace Model:**\n"
        response += "• Commission-based revenue\n"
        response += "• Network effects create moats\n"
        response += "• Best for platforms, aggregators\n\n"
        
        response += "🆓 **Freemium Model:**\n"
        response += "• Large user base acquisition\n"
        response += "• Conversion to paid tiers\n"
        response += "• Best for apps, digital services\n\n"
        
        response += "💰 **Revenue Stream Ideas:**\n"
        response += "• Primary: Core product/service sales\n"
        response += "• Secondary: Premium features, add-ons\n"
        response += "• Tertiary: Data, advertising, partnerships\n\n"
        
        response += "Which business model interests you most for your idea?"
        
        return response
    
    def _generate_funding_response(self, message: str, business_idea: str, analysis: Dict[str, Any]) -> str:
        """Generate funding advice response"""
        response = "💰 **Funding Strategy Guide**\n\n"
        
        response += "**Funding Stages:**\n"
        response += "🌱 **Pre-Seed ($10K-$100K):**\n"
        response += "• Friends, family, personal savings\n"
        response += "• Bootstrapping, customer revenue\n"
        response += "• Grants, competitions\n\n"
        
        response += "🌱 **Seed ($100K-$1M):**\n"
        response += "• Angel investors, accelerators\n"
        response += "• Early-stage VCs\n"
        response += "• Crowdfunding platforms\n\n"
        
        response += "🚀 **Series A ($1M-$10M):**\n"
        response += "• Venture capital firms\n"
        response += "• Corporate venture arms\n"
        response += "• Strategic investors\n\n"
        
        response += "**Pitch Deck Essentials:**\n"
        response += "📋 **Problem:** Clear pain point\n"
        response += "💡 **Solution:** Your unique approach\n"
        response += "📊 **Market:** Size and growth\n"
        response += "👥 **Team:** Key team members\n"
        response += "💵 **Financials:** Projections, metrics\n"
        response += "🎯 **Ask:** Specific amount and use\n\n"
        
        response += "**Investor Red Flags:**\n"
        response += "❌ Unrealistic financial projections\n"
        response += "❌ No clear competitive advantage\n"
        response += "❌ Large team with no traction\n"
        response += "❌ Unclear business model\n\n"
        
        response += "**Action Steps:**\n"
        response += "1. Build MVP/prototype\n"
        response += "2. Get initial customers/traction\n"
        response += "3. Research target investors\n"
        response += "4. Practice pitch extensively\n"
        response += "5. Network and get introductions\n\n"
        
        response += "What stage of funding are you currently exploring?"
        
        return response
    
    def _generate_risk_response(self, message: str, business_idea: str, analysis: Dict[str, Any]) -> str:
        """Generate risk assessment response"""
        if not analysis:
            return "I can help you assess risks! Tell me about your business idea, and I'll identify potential challenges and mitigation strategies."
        
        response = f"⚠️ **Risk Assessment**\n\n"
        response += f"**Overall Risk Score:** {analysis['risk_score']}/100\n\n"
        
        swot = analysis.get('swot_analysis', {})
        response += "**Key Risk Areas:**\n"
        
        if swot.get('threats'):
            response += f"🎯 **Market Threats:**\n{swot['threats']}\n\n"
        
        response += "**Common Startup Risks:**\n"
        response += "💸 **Market Risks:**\n"
        response += "• Insufficient market demand\n"
        response += "• Strong competition\n"
        response += "• Market timing issues\n\n"
        
        response += "💰 **Financial Risks:**\n"
        response += "• Running out of cash\n"
        response += "• Poor unit economics\n"
        response += "• High customer acquisition cost\n\n"
        
        response += "⚙️ **Operational Risks:**\n"
        response += "• Scaling challenges\n"
        response += "• Team execution issues\n"
        response += "• Supply chain problems\n\n"
        
        response += "⚖️ **Legal Risks:**\n"
        response += "• Regulatory compliance\n"
        response += "• IP protection\n"
        response += "• Contract disputes\n\n"
        
        response += "**Risk Mitigation Strategies:**\n"
        response += "🛡️ **Prevention:**\n"
        response += "• Thorough market research\n"
        response += "• Financial planning and buffers\n"
        response += "• Legal compliance reviews\n\n"
        
        response += "🔄 **Monitoring:**\n"
        response += "• Regular risk assessments\n"
        response += "• Key metrics tracking\n"
        response += "• Customer feedback loops\n\n"
        
        response += "🚀 **Contingency:**\n"
        response += "• Backup plans for key risks\n"
        response += "• Insurance where applicable\n"
        response += "• Diversification strategies\n\n"
        
        response += "Which risk area concerns you most?"
        
        return response
    
    def _generate_startup_response(self, message: str, business_idea: str, analysis: Dict[str, Any]) -> str:
        """Generate startup guidance response"""
        response = "🚀 **Startup Success Guide**\n\n"
        
        response += "**Essential First Steps:**\n"
        response += "1️⃣ **Problem Validation:**\n"
        response += "• Talk to 50+ potential customers\n"
        response += "• Identify real pain points\n"
        response += "• Confirm willingness to pay\n\n"
        
        response += "2️⃣ **Solution Development:**\n"
        response += "• Build minimum viable product\n"
        response += "• Focus on core features only\n"
        response += "• Iterate based on feedback\n\n"
        
        response += "3️⃣ **Market Entry:**\n"
        response += "• Beta testing with early adopters\n"
        response += "• Launch in specific niche first\n"
        response += "• Build community around product\n\n"
        
        response += "4️⃣ **Growth Strategy:**\n"
        response += "• Measure key metrics obsessively\n"
        response += "• Optimize conversion funnel\n"
        response += "• Scale what works, kill what doesn't\n\n"
        
        response += "**Success Factors:**\n"
        response += "✅ **Strong Team:** Complementary skills\n"
        response += "✅ **Market Need:** Real problem solving\n"
        response += "✅ **Scalable Model:** Can grow exponentially\n"
        response += "✅ **Timing:** Right market entry moment\n"
        response += "✅ **Execution:** Ability to deliver\n\n"
        
        response += "**Common Mistakes to Avoid:**\n"
        response += "❌ Building product nobody wants\n"
        response += "❌ Running out of cash\n"
        response += "❌ Ignoring competition\n"
        response += "❌ Perfection over progress\n"
        response += "❌ Hiring too fast\n\n"
        
        response += "What specific aspect of starting up would you like help with?"
        
        return response
    
    def _generate_help_response(self, message: str, business_idea: str, analysis: Dict[str, Any]) -> str:
        """Generate help/support response"""
        response = "🤖 **How I Can Help You**\n\n"
        response += self.quick_responses['capabilities'] + "\n\n"
        response += "💡 **Pro Tips:**\n"
        response += "• Be specific about your business idea\n"
        response += "• Ask follow-up questions for deeper insights\n"
        response += "• Provide context about your industry\n"
        response += "• Mention your target customers\n\n"
        response += "📞 **Getting Started:**\n" + self.quick_responses['how_to_use'] + "\n\n"
        response += "Type your business idea or question, and I'll provide personalized guidance!"
        
        return response
    
    def _generate_greeting_response(self, message: str, business_idea: str, analysis: Dict[str, Any]) -> str:
        """Generate greeting response"""
        greetings = {
            'hello': f"Hello! 👋 I'm excited to help you with your business idea! What entrepreneurial challenge can I assist with today?",
            'hi': f"Hi there! 🚀 Ready to explore your startup idea? Tell me what you're working on!",
            'thanks': "You're welcome! 😊 Is there anything else about your business idea I can help with?",
            'good_morning': "Good morning! ☀️ Let's make today productive for your startup. What's on your mind?",
            'good_afternoon': "Good afternoon! 🌤 Ready to tackle some business challenges? What can I help with?",
            'good_evening': "Good evening! 🌙 Perfect time for strategic thinking. What business ideas are you exploring?"
        }
        
        message_lower = message.lower()
        for greeting, response in greetings.items():
            if greeting in message_lower:
                return response
        
        return f"Hello! 👋 I'm here to help with your business ideas and startup questions. I noticed you mentioned '{message}' - what specific aspect can I assist you with today?"
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate fallback response for unknown intents"""
        response = f"🤔 I'm not sure I understood that completely. Let me help you better!\n\n"
        response += f"**I can assist with:**\n"
        response += "• Business idea evaluation 📊\n"
        response += "• Competitor analysis 🏢\n"
        response += "• Market research 📈\n"
        response += "• Improvement suggestions 🚀\n"
        response += "• Business model advice 💼\n"
        response += "• Funding guidance 💰\n"
        response += "• Risk assessment ⚠️\n\n"
        response += f"**Try asking:**\n"
        response += f"• Tell me about your business idea\n"
        response += f"• Ask me to analyze competitors\n"
        response += f"• Request market research\n"
        response += f"• Say 'improve my idea: [your idea]'\n\n"
        response += f"Based on your message '{message}', what specific business topic would you like help with?"
        
        return response
    
    def _generate_followup_suggestions(self, intent: str) -> List[str]:
        """Generate follow-up question suggestions"""
        suggestions = {
            'idea_evaluation': [
                "What competitors exist in this space?",
                "How can I improve this idea?",
                "What business model would work best?"
            ],
            'competitor_analysis': [
                "How can I differentiate from competitors?",
                "What's the market size?",
                "What are the risks involved?"
            ],
            'improvement_suggestions': [
                "Is this idea viable now?",
                "Who are target customers?",
                "What funding do I need?"
            ],
            'market_research': [
                "How to validate the market?",
                "What are the growth trends?",
                "Who are the key players?"
            ],
            'business_model': [
                "How to price this product?",
                "What revenue streams exist?",
                "How to scale this business?"
            ],
            'funding_advice': [
                "How to create a pitch deck?",
                "Where to find investors?",
                "What metrics do investors care about?"
            ],
            'risk_assessment': [
                "How to mitigate these risks?",
                "What are the success factors?",
                "How to test the idea first?"
            ],
            'startup_basics': [
                "How to validate my idea?",
                "What are the first steps?",
                "How to find co-founders?"
            ]
        }
        
        return suggestions.get(intent, [
            "Tell me more about your business idea",
            "What's your target market?",
            "What problem are you solving?"
        ])
    
    def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for session"""
        return self.conversation_context.get(session_id, {})
    
    def update_conversation_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """Update conversation context for session"""
        self.conversation_context[session_id] = context
    
    def clear_conversation_context(self, session_id: str) -> None:
        """Clear conversation context for session"""
        if session_id in self.conversation_context:
            del self.conversation_context[session_id]


# Singleton instance for easy access
ai_chatbot = AIChatbot()
