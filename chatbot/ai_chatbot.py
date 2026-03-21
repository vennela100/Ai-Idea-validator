import time
import logging
from typing import Dict, Any, Optional
from analyzer.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class AIChatbot:
    """
    True AI-powered chatbot for business idea assistance.
    Uses Google Gemini for deep conversational reasoning, maintaining the context
    of the user's business idea and previous messages.
    """
    
    def __init__(self):
        # We store conversation contexts in memory for simplicity,
        # but in a production environment this should use Redis or the Django DB.
        self.conversation_memory = {}
        
    def extract_business_idea(self, message: str) -> Optional[str]:
        """Simple extraction to grab the idea if they state it directly in chat."""
        message_lower = message.lower()
        if 'my idea is' in message_lower:
            return message[message_lower.find('my idea is') + 10:].strip()
        elif 'i want to build' in message_lower:
            return message[message_lower.find('i want to build') + 15:].strip()
        return None

    def process_message(self, message: str, session_id: str, chat_history: list = None) -> Dict[str, Any]:
        """
        Process user message and generate a true AI response using Gemini.
        
        Args:
            message: User input message
            session_id: Unique conversation ID
            chat_history: Optional list of previous messages [{'sender': 'user/ai', 'message': '...'}]
            
        Returns:
            Dict containing the AI's response text.
        """
        start_time = time.time()
        
        # Initialize session memory if doesn't exist
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = {
                "business_idea": "",
                "history": []
            }
            
        context = self.conversation_memory[session_id]
        
        # Did the user just tell us a new business idea?
        new_idea = self.extract_business_idea(message)
        if new_idea:
            context["business_idea"] = new_idea
            
        # Ensure chat history is formatted
        if chat_history is None:
            chat_history = context["history"]
            
        # 1. Generate the response via the Centralized AI Orchestrator
        # The orchestrator handles intent detection and chooses the optimal prompt.
        from analyzer.services.orchestrator import AIOrchestrator
        
        result = AIOrchestrator.process_request(
            command=message,
            source='chatbot',
            context={
                'idea_context': context["business_idea"],
                'chat_history': chat_history
            }
        )
        
        ai_text = result.get('response', 'I encountered an issue processing that.')
        
        # If the orchestrator performed a full analysis, capture the idea summary
        if result.get('is_analysis') and result.get('analysis'):
            context["business_idea"] = result['analysis'].get('idea_summary', message)
            
        is_fallback = result.get('source_engine') == 'heuristic'
            
        # Update local memory
        context["history"].append({"sender": "user", "message": message})
        context["history"].append({"sender": "ai", "message": ai_text})
        
        # Keep history from growing unbounded 
        if len(context["history"]) > 20:
            context["history"] = context["history"][-20:]
            
        processing_time = round(time.time() - start_time, 2)
        
        return {
            'response': ai_text,
            'intent': 'conversational_ai', # Legacy field for compatibility
            'confidence': 95.0 if not is_fallback else 50.0,
            'processing_time': processing_time,
            'requires_analysis': False
        }



# Singleton
ai_chatbot = AIChatbot()
