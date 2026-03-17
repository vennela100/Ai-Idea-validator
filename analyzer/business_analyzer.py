import re
import json
from typing import Dict, List, Any


class BusinessIdeaAnalyzer:
    """
    Keyword-based AI reasoning system for business idea analysis.
    Uses pattern matching and industry heuristics to generate insights.
    """
    
    def __init__(self):
        # Industry keywords and their associated metrics
        self.industry_keywords = {
            'ai': {
                'keywords': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'neural', 'automation', 'chatbot', 'computer vision'],
                'base_demand': 85,
                'demand_modifier': 15,
                'competition': 'High',
                'risk_level': 'Medium',
                'feasibility': 65,
                'success_probability': 72
            },
            'healthcare': {
                'keywords': ['health', 'medical', 'healthcare', 'hospital', 'clinic', 'pharma', 'wellness', 'fitness'],
                'base_demand': 75,
                'demand_modifier': 10,
                'competition': 'High',
                'risk_level': 'High',
                'feasibility': 55,
                'success_probability': 68
            },
            'fintech': {
                'keywords': ['finance', 'banking', 'payment', 'fintech', 'crypto', 'investment', 'trading', 'insurance'],
                'base_demand': 80,
                'demand_modifier': 12,
                'competition': 'Very High',
                'risk_level': 'High',
                'feasibility': 60,
                'success_probability': 65
            },
            'ecommerce': {
                'keywords': ['ecommerce', 'shop', 'store', 'marketplace', 'retail', 'shopping', 'cart', 'delivery'],
                'base_demand': 70,
                'demand_modifier': 5,
                'competition': 'Very High',
                'risk_level': 'Medium',
                'feasibility': 75,
                'success_probability': 70
            },
            'education': {
                'keywords': ['education', 'learning', 'school', 'course', 'training', 'tutoring', 'student', 'academic'],
                'base_demand': 65,
                'demand_modifier': 8,
                'competition': 'Medium',
                'risk_level': 'Low',
                'feasibility': 80,
                'success_probability': 75
            },
            'food': {
                'keywords': ['food', 'restaurant', 'delivery', 'catering', 'meal', 'kitchen', 'cooking'],
                'base_demand': 60,
                'demand_modifier': 5,
                'competition': 'High',
                'risk_level': 'Medium',
                'feasibility': 70,
                'success_probability': 68
            },
            'transportation': {
                'keywords': ['transport', 'transportation', 'logistics', 'delivery', 'mobility', 'vehicle', 'fleet'],
                'base_demand': 55,
                'demand_modifier': 10,
                'competition': 'High',
                'risk_level': 'High',
                'feasibility': 50,
                'success_probability': 60
            },
            'realestate': {
                'keywords': ['real estate', 'property', 'housing', 'rental', 'mortgage', 'brokerage'],
                'base_demand': 50,
                'demand_modifier': 5,
                'competition': 'High',
                'risk_level': 'Medium',
                'feasibility': 65,
                'success_probability': 62
            },
            'entertainment': {
                'keywords': ['entertainment', 'gaming', 'streaming', 'music', 'video', 'media', 'content'],
                'base_demand': 60,
                'demand_modifier': 8,
                'competition': 'Very High',
                'risk_level': 'Medium',
                'feasibility': 70,
                'success_probability': 65
            },
            'saas': {
                'keywords': ['saas', 'software', 'subscription', 'cloud', 'platform', 'b2b', 'enterprise'],
                'base_demand': 75,
                'demand_modifier': 15,
                'competition': 'High',
                'risk_level': 'Medium',
                'feasibility': 70,
                'success_probability': 73
            }
        }
        
        # Business model modifiers
        self.business_models = {
            'subscription': {
                'keywords': ['subscription', 'recurring', 'monthly', 'annual', 'membership'],
                'viability': 85
            },
            'marketplace': {
                'keywords': ['marketplace', 'platform', 'commission', 'two-sided', 'network'],
                'viability': 75
            },
            'freemium': {
                'keywords': ['freemium', 'free', 'premium', 'basic', 'pro'],
                'viability': 70
            },
            'advertising': {
                'keywords': ['advertising', 'ads', 'revenue', 'monetization', 'impressions'],
                'viability': 60
            },
            'licensing': {
                'keywords': ['licensing', 'license', 'royalty', 'ip', 'patent'],
                'viability': 65
            }
        }
        
        # Risk indicators
        self.risk_keywords = {
            'high_risk': ['regulated', 'compliance', 'legal', 'high capital', 'inventory', 'physical'],
            'medium_risk': ['technology', 'competition', 'scaling', 'hiring'],
            'low_risk': ['digital', 'service', 'consulting', 'software']
        }
        
        # Target customer indicators
        self.customer_segments = {
            'b2b': ['business', 'enterprise', 'corporate', 'company'],
            'b2c': ['consumer', 'individual', 'personal', 'customer'],
            'enterprise': ['large', 'fortune', 'corporate', 'scale'],
            'sme': ['small', 'medium', 'local', 'regional']
        }

    def _detect_industry(self, idea_text: str) -> str:
        """Detect industry based on business idea content"""
        idea_lower = idea_text.lower()
        
        industry_patterns = {
            'saas': ['saas', 'software as a service', 'subscription', 'cloud', 'platform', 'app', 'software'],
            'retail': ['shop', 'store', 'retail', 'ecommerce', 'shopping', 'marketplace', 'online store'],
            'fintech': ['finance', 'banking', 'payment', 'crypto', 'investment', 'trading', 'insurance', 'lending'],
            'healthtech': ['health', 'medical', 'healthcare', 'hospital', 'clinic', 'pharma', 'wellness', 'fitness'],
            'edtech': ['education', 'school', 'learning', 'course', 'student', 'teaching', 'university', 'college'],
            'foodtech': ['food', 'restaurant', 'delivery', 'cooking', 'catering', 'grocery', 'meal'],
            'transport': ['transport', 'delivery', 'logistics', 'shipping', 'car', 'vehicle', 'mobility'],
            'realestate': ['real estate', 'property', 'rental', 'housing', 'apartment', 'building', 'construction'],
            'entertainment': ['entertainment', 'gaming', 'media', 'streaming', 'music', 'video', 'content'],
            'travel': ['travel', 'hotel', 'booking', 'tourism', 'vacation', 'flight', 'trip'],
            'energy': ['energy', 'solar', 'renewable', 'power', 'electric', 'battery', 'green'],
            'manufacturing': ['manufacturing', 'factory', 'production', 'industrial', 'machinery', 'equipment'],
            'agritech': ['agriculture', 'farming', 'crops', 'livestock', 'irrigation', 'harvest'],
            'consulting': ['consulting', 'advisory', 'services', 'professional', 'expert', 'consultancy'],
            'social': ['social', 'network', 'community', 'dating', 'friends', 'social media'],
            'iot': ['iot', 'internet of things', 'smart', 'connected', 'device', 'sensor'],
            'blockchain': ['blockchain', 'crypto', 'bitcoin', 'nft', 'web3', 'decentralized'],
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'automation', 'chatbot', 'robot'],
            'sustainability': ['sustainable', 'green', 'eco', 'environment', 'climate', 'carbon', 'recycle']
        }
        
        # Check for industry matches
        for industry, keywords in industry_patterns.items():
            if any(keyword in idea_lower for keyword in keywords):
                return industry.title()
        
        # Default to startup if no specific industry detected
        return "Startup"

    def _detect_business_model(self, idea_text: str) -> str:
        """Detect the business model based on keywords"""
        idea_lower = idea_text.lower()
        
        for model, data in self.business_models.items():
            for keyword in data['keywords']:
                if keyword in idea_lower:
                    return model
        return 'unknown'

    def _assess_competition(self, idea_text: str, industry: str) -> str:
        """Assess competition level based on industry and idea content"""
        idea_lower = idea_text.lower()
        
        # Industry-specific competition levels
        industry_competition = {
            'saas': 'High',
            'fintech': 'Very High', 
            'healthtech': 'High',
            'edtech': 'Medium',
            'ecommerce': 'Very High',
            'fintech': 'Very High',
            'ai': 'Very High',
            'retail': 'High',
            'foodtech': 'Medium',
            'transport': 'High',
            'realestate': 'Medium',
            'entertainment': 'Very High',
            'travel': 'High',
            'energy': 'Medium',
            'manufacturing': 'High',
            'consulting': 'Medium'
        }
        
        base_level = industry_competition.get(industry, 'Medium')
        
        # Adjust based on specific keywords
        high_comp_words = ['established', 'mature', 'saturated', 'crowded', 'dominant', 'market leader']
        low_comp_words = ['niche', 'underserved', 'emerging', 'new market', 'blue ocean', 'opportunity']
        
        if any(word in idea_lower for word in high_comp_words):
            return 'Very High'
        elif any(word in idea_lower for word in low_comp_words):
            return 'Low'
        
        return base_level

    def _calculate_demand_score(self, idea_text: str, industry: str) -> int:
        """Calculate market demand score"""
        base_score = self.industry_keywords.get(industry, {}).get('base_demand', 50)
        
        # Demand boosters
        demand_boosters = [
            ('innovative', 10), ('revolutionary', 15), ('first-mover', 12),
            ('problem-solving', 8), ('efficiency', 6), ('cost-saving', 7),
            ('growing market', 10), ('untapped', 12), ('emerging', 8)
        ]
        
        idea_lower = idea_text.lower()
        boost_score = sum(score for keyword, score in demand_boosters if keyword in idea_lower)
        
        # Industry modifier
        industry_modifier = self.industry_keywords.get(industry, {}).get('demand_modifier', 0)
        
        total_score = base_score + boost_score + industry_modifier
        return min(max(total_score, 20), 100)  # Cap between 20-100

    def _calculate_risk_score(self, idea_text: str, industry: str) -> int:
        """Calculate risk score"""
        base_risk = self.industry_keywords.get(industry, {}).get('risk_level', 'Medium')
        
        risk_scores = {'Low': 25, 'Medium': 50, 'High': 75}
        base_score = risk_scores.get(base_risk, 50)
        
        # Risk modifiers
        idea_lower = idea_text.lower()
        
        risk_increase_keywords = [
            ('regulated', 15), ('compliance', 12), ('legal', 10),
            ('high capital', 15), ('inventory', 8), ('physical', 10),
            ('complex', 8), ('r&d', 12), ('patent', 5)
        ]
        
        risk_decrease_keywords = [
            ('digital', 10), ('software', 8), ('service', 5),
            ('low overhead', 8), ('scalable', 10), ('recurring', 5)
        ]
        
        increase_score = sum(score for keyword, score in risk_increase_keywords if keyword in idea_lower)
        decrease_score = sum(score for keyword, score in risk_decrease_keywords if keyword in idea_lower)
        
        final_score = base_score + increase_score - decrease_score
        return min(max(final_score, 15), 90)  # Cap between 15-90

    def _calculate_feasibility_score(self, idea_text: str, industry: str) -> int:
        """Calculate feasibility score"""
        base_feasibility = self.industry_keywords.get(industry, {}).get('feasibility', 60)
        
        idea_lower = idea_text.lower()
        
        # Feasibility boosters
        feasibility_boosters = [
            ('simple', 10), ('proven', 8), ('tested', 6),
            ('mvp', 8), ('prototype', 5), ('beta', 3),
            ('low-cost', 10), ('quick', 8), ('easy', 12)
        ]
        
        # Feasibility reducers
        feasibility_reducers = [
            ('complex', 10), ('breakthrough', 8), ('research', 12),
            ('infrastructure', 8), ('hardware', 10), ('manufacturing', 15),
            ('global', 5), ('enterprise', 3)
        ]
        
        boost_score = sum(score for keyword, score in feasibility_boosters if keyword in idea_lower)
        reduce_score = sum(score for keyword, score in feasibility_reducers if keyword in idea_lower)
        
        final_score = base_feasibility + boost_score - reduce_score
        return min(max(final_score, 25), 95)  # Cap between 25-95

    def _calculate_success_probability(self, idea_text: str, industry: str) -> float:
        """Calculate success probability"""
        base_probability = self.industry_keywords.get(industry, {}).get('success_probability', 60)
        
        idea_lower = idea_text.lower()
        
        # Success boosters
        success_boosters = [
            ('unique', 8), ('patented', 6), ('first-mover', 10),
            ('experienced team', 8), ('funded', 12), ('traction', 15),
            ('validated', 10), ('proven', 6), ('scalable', 8)
        ]
        
        # Success reducers
        success_reducers = [
            ('me-too', 15), ('copycat', 12), ('saturated', 10),
            ('no experience', 8), ('solo founder', 5), ('pre-revenue', 8),
            ('high risk', 10), ('unproven', 8), ('concept stage', 5)
        ]
        
        boost_score = sum(score for keyword, score in success_boosters if keyword in idea_lower)
        reduce_score = sum(score for keyword, score in success_reducers if keyword in idea_lower)
        
        final_probability = base_probability + boost_score - reduce_score
        return min(max(final_probability, 25), 95)  # Cap between 25-95

    def _generate_swot_analysis(self, idea_text: str, industry: str) -> Dict[str, str]:
        """Generate SWOT analysis"""
        idea_lower = idea_text.lower()
        
        # Strengths
        strengths = []
        if any(word in idea_lower for word in ['innovative', 'unique', 'patented', 'experienced', 'first-mover']):
            strengths.append("Innovative approach with unique value proposition")
        if any(word in idea_lower for word in ['ai', 'technology', 'automation', 'efficiency']):
            strengths.append("Advanced technology integration and automation capabilities")
        if any(word in idea_lower for word in ['low cost', 'affordable', 'cost-effective']):
            strengths.append("Cost-effective solution with clear economic advantages")
        
        # Weaknesses
        weaknesses = []
        if any(word in idea_lower for word in ['new', 'startup', 'early stage', 'concept']):
            weaknesses.append("Early stage concept requiring market validation")
        if any(word in idea_lower for word in ['complex', 'complicated', 'infrastructure']):
            weaknesses.append("Complex implementation requiring significant resources")
        if any(word in idea_lower for word in ['solo', 'single founder', 'small team']):
            weaknesses.append("Limited team size and resources for rapid scaling")
        
        # Opportunities
        opportunities = []
        if any(word in idea_lower for word in ['growing', 'expanding', 'emerging', 'trending']):
            opportunities.append("Expanding market with increasing demand and adoption")
        if any(word in idea_lower for word in ['digital', 'online', 'remote', 'global']):
            opportunities.append("Global scalability through digital delivery channels")
        if industry == 'healthcare':
            opportunities.append("Aging population and increasing health consciousness create market opportunities")
        elif industry == 'fintech':
            opportunities.append("Digital transformation and financial inclusion driving market growth")
        
        # Threats
        threats = []
        if any(word in idea_lower for word in ['competitive', 'crowded', 'saturated']):
            threats.append("Highly competitive market with established players")
        if any(word in idea_lower for word in ['regulated', 'compliance', 'legal']):
            threats.append("Regulatory challenges and compliance requirements")
        if any(word in idea_lower for word in ['technology', 'ai', 'software']):
            threats.append("Rapid technological changes requiring continuous innovation")
        
        return {
            'strengths': '; '.join(strengths) if strengths else "Innovative concept with market potential",
            'weaknesses': '; '.join(weaknesses) if weaknesses else "Early stage requiring validation and resources",
            'opportunities': '; '.join(opportunities) if opportunities else "Market growth and digital expansion opportunities",
            'threats': '; '.join(threats) if threats else "Competitive landscape and regulatory challenges"
        }

    def _identify_target_customers(self, idea_text: str) -> Dict[str, Any]:
        """Identify target customer segments"""
        idea_lower = idea_text.lower()
        
        # B2B vs B2C
        is_b2b = any(word in idea_lower for word in ['business', 'enterprise', 'b2b', 'corporate'])
        is_b2c = any(word in idea_lower for word in ['consumer', 'individual', 'personal', 'b2c'])
        
        # Demographics
        demographics = []
        if any(word in idea_lower for word in ['young', 'students', 'gen z', 'millennials']):
            demographics.append("Young professionals and students (18-35)")
        elif any(word in idea_lower for word in ['families', 'parents', 'children', 'household']):
            demographics.append("Families and middle-aged adults (35-55)")
        elif any(word in idea_lower for word in ['seniors', 'elderly', 'retired', 'baby boomers']):
            demographics.append("Seniors and retirees (55+)")
        else:
            demographics.append("Broad adult audience (25-65)")
        
        # Psychographics
        psychographics = []
        if any(word in idea_lower for word in ['tech', 'digital', 'online', 'smart']):
            psychographics.append("Tech-savvy early adopters")
        if any(word in idea_lower for word in ['health', 'wellness', 'fitness', 'organic']):
            psychographics.append("Health-conscious consumers")
        if any(word in idea_lower for word in ['luxury', 'premium', 'high-end']):
            psychographics.append("Affluent customers seeking premium solutions")
        
        # Geography
        geography = []
        if any(word in idea_lower for word in ['local', 'community', 'neighborhood']):
            geography.append("Local community focus")
        elif any(word in idea_lower for word in ['global', 'international', 'worldwide']):
            geography.append("Global market reach")
        elif any(word in idea_lower for word in ['urban', 'city', 'metropolitan']):
            geography.append("Urban metropolitan areas")
        else:
            geography.append("Regional to national coverage")
        
        return {
            'primary_segment': 'B2B' if is_b2b else 'B2C',
            'demographics': '; '.join(demographics) if demographics else "Adults 25-65",
            'psychographics': '; '.join(psychographics) if psychographics else "General consumers",
            'geography': '; '.join(geography) if geography else "Regional to national",
            'estimated_tam': "Large" if is_b2b else "Medium",
            'customer_pain_points': self._extract_pain_points(idea_lower)
        }

    def _extract_pain_points(self, idea_text: str) -> List[str]:
        """Extract customer pain points from the idea"""
        pain_points = []
        
        pain_point_keywords = {
            'inefficiency': ['inefficient', 'slow', 'manual', 'time-consuming', 'complicated'],
            'cost': ['expensive', 'costly', 'budget', 'affordable', 'cheap'],
            'accessibility': ['accessible', 'available', 'convenient', 'easy'],
            'quality': ['quality', 'reliable', 'consistent', 'standard'],
            'communication': ['communication', 'collaboration', 'sharing', 'visibility']
        }
        
        for pain_point, keywords in pain_point_keywords.items():
            if any(keyword in idea_text for keyword in keywords):
                pain_points.append(f"Addressing {pain_point} challenges")
        
        return pain_points if pain_points else ["Improving existing solutions"]

    def _suggest_business_models(self, idea_text: str, industry: str) -> List[Dict[str, Any]]:
        """Suggest suitable business models"""
        idea_lower = idea_text.lower()
        detected_model = self._detect_business_model(idea_text)
        
        suggestions = []
        
        # Always suggest the detected model first
        if detected_model != 'unknown':
            model_data = self.business_models.get(detected_model, {})
            suggestions.append({
                'model': detected_model.title(),
                'description': self._get_model_description(detected_model),
                'viability': model_data.get('viability', 70),
                'revenue_streams': self._get_revenue_streams(detected_model),
                'match_reason': 'Detected from your business description'
            })
        
        # Suggest complementary models
        complementary_models = {
            'subscription': ['marketplace', 'freemium'],
            'marketplace': ['saas', 'advertising'],
            'freemium': ['subscription', 'advertising'],
            'saas': ['marketplace', 'licensing'],
            'ecommerce': ['subscription', 'marketplace']
        }
        
        for model in complementary_models.get(detected_model, []):
            if model not in [s.get('model', '').lower() for s in suggestions]:
                model_data = self.business_models.get(model, {})
                suggestions.append({
                    'model': model.title(),
                    'description': self._get_model_description(model),
                    'viability': model_data.get('viability', 65),
                    'revenue_streams': self._get_revenue_streams(model),
                    'match_reason': f'Complementary to {detected_model.title()} model'
                })
        
        return suggestions[:3]  # Return top 3 suggestions

    def _get_model_description(self, model: str) -> str:
        """Get description for business model"""
        descriptions = {
            'subscription': 'Recurring revenue through periodic subscription fees',
            'marketplace': 'Platform connecting buyers and sellers with commission revenue',
            'freemium': 'Basic free services with premium paid features',
            'advertising': 'Revenue through advertisements and sponsored content',
            'licensing': 'Revenue through licensing intellectual property'
        }
        return descriptions.get(model, 'Revenue generation through business operations')

    def _get_revenue_streams(self, model: str) -> str:
        """Get revenue streams for business model"""
        streams = {
            'subscription': 'Monthly/annual subscription fees, tiered pricing',
            'marketplace': 'Commission on transactions, listing fees, premium features',
            'freemium': 'Free tier with premium upgrades, advertising revenue',
            'advertising': 'Ad impressions, click-through rates, sponsored content',
            'licensing': 'License fees, royalties, intellectual property revenue'
        }
        return streams.get(model, 'Direct sales and service fees')

    def _generate_improvement_suggestions(self, idea_text: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate improvement suggestions"""
        suggestions = []
        
        demand_score = analysis.get('market_demand_score', 50)
        risk_score = analysis.get('risk_score', 50)
        feasibility_score = analysis.get('feasibility_score', 50)
        
        # Low demand suggestions
        if demand_score < 60:
            suggestions.append({
                'type': 'Market',
                'suggestion': 'Conduct market research to validate demand and identify target customer segments',
                'priority': 'High',
                'difficulty': 'Medium',
                'impact': 'High'
            })
        
        # High competition suggestions
        if analysis.get('competition_level') in ['High', 'Very High']:
            suggestions.append({
                'type': 'Competitive Strategy',
                'suggestion': 'Develop unique differentiation strategy and focus on underserved niches',
                'priority': 'High',
                'difficulty': 'Hard',
                'impact': 'High'
            })
        
        # High risk suggestions
        if risk_score > 70:
            suggestions.append({
                'type': 'Risk Mitigation',
                'suggestion': 'Develop comprehensive risk management plan and consider phased approach',
                'priority': 'High',
                'difficulty': 'Hard',
                'impact': 'High'
            })
        
        # Low feasibility suggestions
        if feasibility_score < 50:
            suggestions.append({
                'type': 'Feasibility',
                'suggestion': 'Start with MVP approach to validate concept with minimal resources',
                'priority': 'High',
                'difficulty': 'Medium',
                'impact': 'High'
            })
        
        # General suggestions
        suggestions.extend([
            {
                'type': 'Business Model',
                'suggestion': 'Explore multiple revenue streams and diversification opportunities',
                'priority': 'Medium',
                'difficulty': 'Medium',
                'impact': 'Medium'
            },
            {
                'type': 'Go-to-Market',
                'suggestion': 'Develop detailed marketing strategy and customer acquisition plan',
                'priority': 'Medium',
                'difficulty': 'Medium',
                'impact': 'Medium'
            },
            {
                'type': 'Technology',
                'suggestion': 'Leverage digital transformation and automation for scalability',
                'priority': 'Low',
                'difficulty': 'Hard',
                'impact': 'Medium'
            }
        ])
        
        return suggestions[:5]  # Return top 5 suggestions

    def analyze_business_idea(self, idea_text: str) -> Dict[str, Any]:
        """
        Main function to analyze business idea using keyword-based AI reasoning.
        
        Args:
            idea_text: The business idea description
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        
        # Detect industry
        industry = self._detect_industry(idea_text)
        
        # Calculate core metrics
        market_demand_score = self._calculate_demand_score(idea_text, industry)
        competition_level = self._assess_competition(idea_text, industry)
        risk_score = self._calculate_risk_score(idea_text, industry)
        feasibility_score = self._calculate_feasibility_score(idea_text, industry)
        success_probability = self._calculate_success_probability(idea_text, industry)
        
        # Generate detailed analysis
        swot_analysis = self._generate_swot_analysis(idea_text, industry)
        target_customers = self._identify_target_customers(idea_text)
        business_models = self._suggest_business_models(idea_text, industry)
        
        # Create base analysis results first
        base_analysis = {
            'market_demand_score': market_demand_score,
            'competition_level': competition_level,
            'risk_score': risk_score,
            'feasibility_score': feasibility_score,
            'success_probability': success_probability,
            'swot_analysis': swot_analysis,
            'target_customers': target_customers,
            'business_models': business_models,
            'industry_detected': industry,
            'method': 'keyword-based analysis',
            'confidence_score': self._calculate_confidence(idea_text, industry)
        }
        
        # Now generate improvement suggestions using the base analysis
        improvement_suggestions = self._generate_improvement_suggestions(idea_text, base_analysis)
        
        # Compile final analysis results
        analysis_results = {
            'market_demand_score': market_demand_score,
            'competition_level': competition_level,
            'risk_score': risk_score,
            'feasibility_score': feasibility_score,
            'success_probability': success_probability,
            'swot_analysis': swot_analysis,
            'target_customers': target_customers,
            'business_models': business_models,
            'improvement_suggestions': improvement_suggestions,
            'industry_detected': industry,
            'method': 'keyword-based analysis',
            'confidence_score': self._calculate_confidence(idea_text, industry)
        }
        
        return analysis_results
    
    def _calculate_confidence(self, idea_text: str, industry: str) -> int:
        """Calculate confidence score based on keyword matches"""
        idea_lower = idea_text.lower()
        industry_data = self.industry_keywords.get(industry, {})
        
        if not industry_data:
            return 60  # Default confidence for unknown industries
        
        keyword_matches = 0
        total_keywords = len(industry_data['keywords'])
        
        for keyword in industry_data['keywords']:
            if keyword in idea_lower:
                keyword_matches += 1
        
        # Calculate confidence based on keyword density
        confidence = min((keyword_matches / total_keywords) * 100, 95)
        return max(confidence, 30)  # Minimum confidence of 30


# Singleton instance for easy access
business_analyzer = BusinessIdeaAnalyzer()


def analyze_business_idea(idea_text: str) -> Dict[str, Any]:
    """
    Convenience function to analyze business idea.
    
    Args:
        idea_text: The business idea description
        
    Returns:
        Dictionary containing comprehensive analysis results with exact structure:
        {
            market_demand_score,
            competition_level,
            risk_score,
            feasibility_score,
            success_probability,
            swot_analysis,
            target_customers,
            business_models,
            improvement_suggestions
        }
    """
    analysis = business_analyzer.analyze_business_idea(idea_text)
    
    # Return exact structure requested
    return {
        'market_demand_score': analysis.get('market_demand_score', 75),
        'competition_level': analysis.get('competition_level', 'Medium'),
        'risk_score': analysis.get('risk_score', 50),
        'feasibility_score': analysis.get('feasibility_score', 70),
        'success_probability': analysis.get('success_probability', 68),
        'swot_analysis': analysis.get('swot_analysis', {}),
        'target_customers': analysis.get('target_customers', {}),
        'business_models': analysis.get('business_models', []),
        'improvement_suggestions': analysis.get('improvement_suggestions', [])
    }

def detect_industry_competitors(business_idea: str) -> List[str]:
    """Detect industry-specific competitors"""
    idea = business_idea.lower()
    
    if "study" in idea or "education" in idea or "learning" in idea:
        return [
            "Notion AI",
            "Motion AI", 
            "MyStudyLife",
            "StudySmarter",
            "Quizlet",
            "Coursera"
        ]
    elif "food" in idea or "restaurant" in idea or "delivery" in idea:
        return [
            "Uber Eats",
            "DoorDash",
            "Swiggy",
            "Zomato",
            "Grubhub"
        ]
    elif "inventory" in idea or "shop" in idea or "retail" in idea:
        return [
            "Zoho Inventory",
            "QuickBooks Commerce",
            "Vyapar App",
            "Marg ERP",
            "Shopify"
        ]
    elif "finance" in idea or "banking" in idea or "payment" in idea:
        return [
            "Stripe",
            "Square",
            "PayPal",
            "Razorpay",
            "Wise"
        ]
    elif "fitness" in idea or "health" in idea or "workout" in idea:
        return [
            "MyFitnessPal",
            "Fitbit",
            "Nike Training Club",
            "Strava",
            "Peloton"
        ]
    elif "saas" in idea or "software" in idea or "platform" in idea:
        return [
            "Salesforce",
            "HubSpot",
            "Zoho",
            "Microsoft 365",
            "Slack"
        ]
    elif "transport" in idea or "delivery" in idea or "logistics" in idea:
        return [
            "Uber",
            "Lyft",
            "DoorDash",
            "FedEx",
            "DHL"
        ]
    else:
        return [
            "Local startups",
            "Emerging SaaS tools",
            "Industry incumbents",
            "Regional competitors"
        ]
    return business_analyzer.analyze_business_idea(idea_text)
