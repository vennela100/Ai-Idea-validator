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
        
        # Generate AI response using the AIChatbot class
        from .ai_chatbot import ai_chatbot
        try:
            chatbot_response = ai_chatbot.process_message(message_text, session_id=str(conversation.id))
            ai_response_text = chatbot_response.get('response', '')
        except Exception as ai_err:
            logger.error(f"AI processing error: {ai_err}", exc_info=True)
            ai_response_text = "I'm having difficulty processing that right now. Could you try rephrasing your question?"
        
        # Ensure we always have a non-empty response
        if not ai_response_text or not ai_response_text.strip():
            ai_response_text = "I received your message but couldn't generate a response. Please try again."
        
        # Save AI message
        ai_message = Message.objects.create(
            conversation=conversation,
            sender='ai',
            message_text=ai_response_text,
            message_type='text'
        )
        
        # Update conversation timestamp
        conversation.save()
        
        # Standardized response contract — frontend reads 'response' directly
        return JsonResponse({
            'success': True,
            'mode': 'strategic_chat',
            'response': ai_response_text,
            'conversation_id': conversation.id,
            'conversation_title': conversation.title,
            'errors': []
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        logger.error(f"Send message error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'mode': 'error',
            'response': 'Something went wrong on our end. Please try again in a moment.',
            'errors': [str(e)]
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


