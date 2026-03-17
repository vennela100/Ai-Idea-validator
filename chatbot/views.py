from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from .models import Conversation, Message
from analyzer.business_analyzer import analyze_business_idea
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def chat_interface(request):
    """ChatGPT-style chatbot interface"""
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'chatbot/chat.html', {
        'conversations': conversations
    })


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def send_message(request):
    """Handle chat message sending"""
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not message_text:
            return JsonResponse({
                'success': False,
                'error': 'Message is required'
            }, status=400)
        
        # Get or create conversation
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        else:
            # Create new conversation with title from first message
            title = message_text[:50] + '...' if len(message_text) > 50 else message_text
            conversation = Conversation.objects.create(
                user=request.user,
                title=title
            )
        
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            sender='user',
            message_text=message_text,
            message_type='text'
        )
        
        # Generate AI response
        ai_response = generate_ai_response(message_text)
        
        # Save AI message
        ai_message = Message.objects.create(
            conversation=conversation,
            sender='ai',
            message_text=ai_response,
            message_type='text'
        )
        
        # Update conversation timestamp
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'id': user_message.id,
                'message': user_message.message_text,
                'sender': 'user',
                'timestamp': user_message.created_at.isoformat()
            },
            'ai_response': {
                'id': ai_message.id,
                'message': ai_message.message_text,
                'sender': 'ai',
                'timestamp': ai_message.created_at.isoformat()
            },
            'conversation_id': conversation.id,
            'conversation_title': conversation.title
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        logger.error(f"Send message error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_conversation(request):
    """Create a new conversation"""
    try:
        conversation = Conversation.objects.create(
            user=request.user,
            title="New Conversation"
        )
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'title': conversation.title
        })
    except Exception as e:
        logger.error(f"Create conversation error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to create conversation'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_conversation(request):
    """Delete a conversation"""
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        conversation.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Conversation deleted successfully'
        })
    except Exception as e:
        logger.error(f"Delete conversation error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to delete conversation'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_conversation(request, conversation_id):
    """Get conversation messages"""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        messages = conversation.messages.all().order_by('created_at')
        
        message_list = []
        for message in messages:
            message_list.append({
                'id': message.id,
                'sender': message.sender,
                'message': message.message_text,
                'message_type': message.message_type,
                'timestamp': message.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'messages': message_list,
            'conversation_title': conversation.title
        })
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to load conversation'
        }, status=500)


def generate_ai_response(message):
    """Generate AI response for business advisor chatbot"""
    message_lower = message.lower()
    
    # Market demand questions
    if any(keyword in message_lower for keyword in ['market demand', 'market size', 'demand', 'market potential']):
        return """**Market Demand Analysis**

Based on current market trends, I can help you analyze market demand. To provide accurate insights, I'll need more specific information about your business idea.

**Key Factors I Consider:**
- Target market size and growth rate
- Current market trends and projections
- Customer pain points and needs
- Competitive landscape
- Economic factors affecting demand

Could you please describe your specific business idea so I can provide a detailed market demand analysis?"""
    
    # Competitor questions
    elif any(keyword in message_lower for keyword in ['competitors', 'competition', 'competitive', 'rivals']):
        return """**Competitor Analysis**

I can help you identify and analyze competitors in your industry. Let me provide a framework for competitor analysis:

**Types of Competitors to Consider:**
- **Direct Competitors**: Companies offering similar products/services
- **Indirect Competitors**: Companies solving the same problem differently
- **Potential Competitors**: Companies that could enter your market
- **Substitute Products**: Alternative solutions customers might choose

**Analysis Framework:**
1. Market positioning
2. Pricing strategies
3. Product features
4. Market share
5. Strengths and weaknesses

What specific industry or business idea are you analyzing? This will help me provide more targeted competitor insights."""
    
    # Risk questions
    elif any(keyword in message_lower for keyword in ['risk', 'risks', 'danger', 'challenges', 'obstacles']):
        return """**Risk Assessment Framework**

I can help you identify and assess risks for your business idea. Here's a comprehensive risk analysis approach:

**Risk Categories:**
1. **Market Risks**
   - Market acceptance
   - Competition intensity
   - Economic downturns
   - Regulatory changes

2. **Operational Risks**
   - Supply chain issues
   - Technology failures
   - Staffing challenges
   - Quality control

3. **Financial Risks**
   - Cash flow problems
   - Funding requirements
   - Revenue uncertainty
   - Cost overruns

4. **Strategic Risks**
   - Business model viability
   - Technology obsolescence
   - Market timing
   - Scalability issues

What specific type of business are you planning? This will help me provide more targeted risk analysis."""
    
    # Feasibility questions
    elif any(keyword in message_lower for keyword in ['feasibility', 'viable', 'possible', 'achievable']):
        return """**Feasibility Assessment**

I can help you evaluate the feasibility of your business idea. Here's what I consider:

**Feasibility Factors:**

**1. Technical Feasibility**
- Required technology availability
- Development complexity
- Technical expertise needed
- Infrastructure requirements

**2. Financial Feasibility**
- Startup costs and funding needs
- Revenue potential
- Break-even analysis
- Profit margins

**3. Market Feasibility**
- Target market size
- Customer willingness to pay
- Market entry barriers
- Growth potential

**4. Operational Feasibility**
- Resource requirements
- Team capabilities
- Process complexity
- Scalability potential

To provide a detailed feasibility assessment, please describe your business idea and I'll evaluate it against these factors."""
    
    # General business advice
    elif any(keyword in message_lower for keyword in ['business idea', 'startup', 'entrepreneur', 'help']):
        return """**AI Startup Assistant**

Hello! I'm your AI business advisor, here to help you with:

**🎯 Core Services:**
- Business idea validation
- Market demand analysis
- Competitor research
- Risk assessment
- Feasibility evaluation
- Strategic recommendations

**💡 How I Can Help:**
- Analyze market trends and opportunities
- Identify potential competitors
- Assess business model viability
- Provide improvement suggestions
- Calculate feasibility scores
- Offer strategic guidance

**🚀 Getting Started:**
Just ask me questions like:
- "What's the market demand for [your idea]?"
- "Who are the competitors in [your industry]?"
- "What risks should I consider for [your business]?"
- "Is [your idea] feasible?"

What business idea would you like to explore today?"""
    
    # Default response
    else:
        return """**AI Business Advisor**

I'm here to help with your business idea! I can provide insights on:

📊 **Market Analysis** - Demand, trends, and opportunities
🏢 **Competitor Research** - Key players and market positioning
⚠️ **Risk Assessment** - Potential challenges and mitigation strategies
✅ **Feasibility Evaluation** - Technical, financial, and operational viability
💡 **Strategic Advice** - Growth strategies and improvement suggestions

Please ask me a specific question about your business idea, or describe what you'd like to explore, and I'll provide detailed analysis and recommendations.

For example: "What's the market demand for an AI fitness app?" or "What competitors exist in the online tutoring space?"""
