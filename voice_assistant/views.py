import json
import logging
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from analyzer.services.orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)

# Temporary in-memory session tracking for voice (use Redis/DB in prod)
VOICE_SESSIONS = {}


@csrf_exempt
@require_http_methods(["GET", "POST"])
def voice_interface(request):
    """
    Voice assistant interface powered by the centralized AI Orchestrator.
    Handles semantic intent detection (analysis vs chat vs clarification) automatically.
    The view is thin: it only manages sessions and delegates all AI logic to the Orchestrator.
    """
    if request.method == 'GET':
        return render(request, 'voice_assistant/voice.html')

    # --- POST: Process a voice command ---
    try:
        data = json.loads(request.body)
        command = data.get('command', '').strip()

        if not command:
            return JsonResponse({'success': False, 'error': 'Command is required'}, status=400)

        # --- Session Management ---
        session_id = data.get('session_id') or str(uuid.uuid4())

        if session_id not in VOICE_SESSIONS:
            VOICE_SESSIONS[session_id] = {"idea_context": "", "history": []}

        session = VOICE_SESSIONS[session_id]

        # --- Delegate to AI Orchestrator ---
        result = AIOrchestrator.process_request(
            command=command,
            source='voice',
            context={
                'idea_context': session["idea_context"],
                'chat_history': session["history"]
            }
        )

        # --- Update Session Based on Response Mode ---
        if result.get('is_analysis') and result.get('analysis'):
            # New analysis performed: update context, reset chat history for new topic
            session["idea_context"] = result['analysis'].get('idea_summary', command)
            session["history"] = []
        else:
            # Conversational turn: append to history for continuity
            session["history"].append({"sender": "user", "message": command})
            session["history"].append({"sender": "ai", "message": result.get('response', '')})
            # Keep history bounded
            if len(session["history"]) > 20:
                session["history"] = session["history"][-20:]

        # --- Build Response ---
        result['session_id'] = session_id
        # Ensure reply field exists for frontend compat
        if 'reply' not in result:
            result['reply'] = result.get('response', '')

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        logger.error(f"Voice interface error: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': f'Voice API error: {str(e)}'}, status=500)
