import logging

logger = logging.getLogger(__name__)

class IntentRouter:
    """
    Semantic classification engine for the AI Idea Validator.
    Determines the best 'mode' and 'prompt' for a given user request.
    """
    
    # 1. ANALYSIS CLUES: Verbs or nouns indicating a desire for deep evaluation.
    ANALYSIS_CLUES = [
        'analyze', 'evaluate', 'check', 'validate', 'analysis', 'report', 
        'depth', 'detailed', 'detail', 'explain', 'review', 'assessment', 
        'complete', 'full', 'deep', 'validation'
    ]
    
    # 2. TOPIC CLUES: Nouns referring to the core project entity.
    TOPIC_CLUES = [
        'idea', 'startup', 'business', 'concept', 'validator', 'project', 
        'app', 'product', 'venture', 'platform', 'model', 'solution'
    ]
    
    # 3. CHAT CLUES: Keywords for narrow, conversational follow-ups.
    CHAT_CLUES = [
        'risk', 'competitor', 'competition', 'marketing', 'growth', 
        'customer', 'user', 'monetization', 'money', 'revenue', 'price', 
        'pricing', 'how', 'who', 'what', 'why', 'suggest', 'improve', 
        'mvp', 'lean', 'cost', 'build', 'start'
    ]

    @classmethod
    def classify(cls, command: str, source: str = 'web', has_context: bool = False) -> str:
        """
        Main routing logic. Returns one of: 
        'full_analysis', 'strategic_chat', 'clarification', 'voice_analysis', 'voice_chat'
        """
        cmd = command.lower().strip()
        
        # Immediate Overrides
        if source == 'analyzer':
            return 'full_analysis'
            
        has_analysis_clue = any(w in cmd for w in cls.ANALYSIS_CLUES)
        has_topic_clue = any(w in cmd for w in cls.TOPIC_CLUES)
        has_chat_clue = any(w in cmd for w in cls.CHAT_CLUES)
        is_question = '?' in cmd
        
        # LOGIC 1: VOICE SPECIFIC ROUTING
        if source == 'voice':
            if (has_analysis_clue and has_topic_clue) or (has_topic_clue and len(cmd) > 20):
                return 'voice_analysis'
            if has_analysis_clue or any(p in cmd for p in ['my idea is', 'i am building', 'explain my']):
                return 'voice_analysis'
            if has_context and (has_chat_clue or is_question):
                return 'voice_chat'
            # Default voice to analysis if it sounds like an idea start
            if any(cmd.startswith(v) for v in ['i want', 'i am', 'this is']):
                return 'voice_analysis'
            return 'voice_chat'

        # LOGIC 2: CHATBOT / WEB ROUTING
        
        # A. Explicit Analysis Request
        if any(cmd.startswith(v) for v in ['analyze', 'evaluate', 'validate', 'check']):
            return 'full_analysis'
        
        # B. Deep Idea Description (Even without "analyze")
        if has_analysis_clue and has_topic_clue:
            if is_question and has_chat_clue and not any(w in cmd for w in ['full', 'detailed', 'report']):
                return 'strategic_chat'
            return 'full_analysis'
            
        # C. Narrow Follow-up (Context dependent)
        if has_context and (has_chat_clue or is_question):
            return 'strategic_chat'
            
        # D. Seeds/Clarification
        if has_topic_clue and len(cmd) < 40 and not has_context:
            return 'clarification'
            
        # E. Broad Descriptions
        if has_topic_clue or len(cmd) > 60:
            return 'full_analysis'

        # Catch-all
        return 'strategic_chat' if has_context else 'clarification'

    @classmethod
    def get_debug_info(cls, command: str, source: str, has_context: bool) -> dict:
        intent = cls.classify(command, source, has_context)
        return {
            "command": command,
            "source": source,
            "has_context": has_context,
            "intent": intent,
            "clues": {
                "analysis": [w for w in cls.ANALYSIS_CLUES if w in command.lower()],
                "topic": [w for w in cls.TOPIC_CLUES if w in command.lower()],
                "chat": [w for w in cls.CHAT_CLUES if w in command.lower()]
            }
        }
