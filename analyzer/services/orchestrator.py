import json
import logging
import re
from django.utils import timezone
from .intent_router import IntentRouter
from . import prompt_registry
from analyzer.gemini_service import gemini_service

logger = logging.getLogger(__name__)


def safe_extract_json(text: str) -> dict | None:
    """
    Robustly extract a JSON object from AI model output.
    Handles: raw JSON, markdown-fenced JSON, partial fences, and embedded JSON.
    Returns None if no valid JSON can be extracted.
    """
    if not text or not text.strip():
        return None

    cleaned = text.strip()

    # 1. Strip markdown code fences
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # 2. Try direct parse
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        pass

    # 3. Try to find JSON object within the text using regex
    match = re.search(r'\{[\s\S]*\}', cleaned)
    if match:
        try:
            return json.loads(match.group())
        except (json.JSONDecodeError, ValueError):
            pass

    return None


def normalize_analysis_response(analysis: dict) -> dict:
    """Ensure all expected analysis keys exist with sensible defaults."""
    defaults = {
        "idea_summary": "Analysis completed.",
        "problem_statement": "",
        "target_audience": "",
        "target_customers": [],
        "market_demand_score": 0,
        "uniqueness_score": 0,
        "competition_level": "Unknown",
        "revenue_potential": 0,
        "feasibility_score": 0,
        "scalability_score": 0,
        "risk_score": 50,
        "swot_analysis": {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        },
        "business_models": [],
        "implementation_roadmap": [],
        "improvement_suggestions": [],
        "final_verdict": "Pending further analysis.",
        "source_engine": "gemini"
    }
    for key, default in defaults.items():
        if key not in analysis or analysis[key] is None:
            analysis[key] = default
    # Ensure SWOT sub-keys exist
    swot = analysis.get("swot_analysis", {})
    if not isinstance(swot, dict):
        analysis["swot_analysis"] = defaults["swot_analysis"]
    else:
        for k in ["strengths", "weaknesses", "opportunities", "threats"]:
            if k not in swot or not isinstance(swot[k], list):
                swot[k] = []
    return analysis


class AIOrchestrator:
    """
    The central coordinator for all AI interactions.
    Unifies Web, Voice, and Chatbot logic into a single intelligent flow.
    Every response follows a standardized contract.
    """

    @classmethod
    def process_request(cls, command: str, source: str = 'web', context: dict = None) -> dict:
        """
        Main entry point for any AI request.

        Args:
            command: The raw user input.
            source: 'analyzer', 'voice', or 'chatbot'.
            context: dict containing 'idea_context', 'chat_history', etc.
        """
        context = context or {}
        idea_context = context.get('idea_context', '')
        chat_history = context.get('chat_history', [])
        has_context = bool(idea_context)

        # 1. Identify Intent
        intent = IntentRouter.classify(command, source, has_context)

        # Debug logging
        debug = IntentRouter.get_debug_info(command, source, has_context)
        logger.info(f"[ORCHESTRATOR] Intent: {intent} | Source: {source} | Command: {command[:60]}...")
        print(f"\n[ORCHESTRATOR DEBUG]\n{json.dumps(debug, indent=2)}\n")

        # 2. Select Prompt Template
        try:
            prompt = cls._select_prompt(intent, command, idea_context, chat_history)
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Prompt template error: {e}", exc_info=True)
            return cls._error_response(f"Failed to build prompt: {e}")

        # 3. Execute AI Request
        try:
            raw_response = gemini_service.generate_content(prompt, context=command)
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] AI execution error: {e}", exc_info=True)
            return cls._error_response(f"AI engine unreachable: {e}")

        if not raw_response or not raw_response.strip():
            logger.warning("[ORCHESTRATOR] Empty AI response received.")
            return cls._error_response("AI returned an empty response.")

        # 4. Format Output Based on Intent
        return cls._format_response(intent, raw_response, command)

    @classmethod
    def _select_prompt(cls, intent, command, idea_context, chat_history):
        """Select and format the prompt template based on intent."""
        if intent == 'full_analysis':
            return prompt_registry.FULL_ANALYSIS_PROMPT.format(idea_text=command)
        elif intent == 'voice_analysis':
            return prompt_registry.VOICE_ANALYSIS_PROMPT.format(voice_input=command)
        elif intent == 'voice_chat':
            return prompt_registry.VOICE_CHAT_PROMPT.format(
                analysis_context=idea_context or "No prior analysis.",
                user_message=command
            )
        elif intent == 'strategic_chat':
            return prompt_registry.STRATEGIC_CHAT_PROMPT.format(
                analysis_context=idea_context or "No prior analysis.",
                user_message=command
            )
        elif intent == 'clarification':
            return prompt_registry.CLARIFICATION_PROMPT.format(user_input=command)
        else:
            return prompt_registry.CHATBOT_MEMORY_PROMPT.format(
                chat_history=chat_history,
                idea_context=idea_context or "None yet.",
                user_message=command
            )

    @classmethod
    def _format_response(cls, intent, raw_response, original_command) -> dict:
        """
        Structural normalization of the AI response.
        Every response follows the standardized contract:
        {success, mode, is_analysis, response, reply, analysis, source_engine, errors, timestamp}
        """
        is_analysis = intent in ['full_analysis', 'voice_analysis']

        # --- Analysis Intent: try to parse structured JSON ---
        if is_analysis:
            analysis_data = safe_extract_json(raw_response)

            if analysis_data and isinstance(analysis_data, dict):
                analysis_data = normalize_analysis_response(analysis_data)
                source = analysis_data.get('source_engine', 'gemini')
                summary = f"Analysis Complete. Score: {analysis_data.get('market_demand_score', 0)}/100."
                verdict = analysis_data.get('final_verdict', '')

                return {
                    "success": True,
                    "mode": intent,
                    "is_analysis": True,
                    "response": f"{summary} {verdict}".strip(),
                    "reply": verdict,
                    "analysis": analysis_data,
                    "source_engine": source,
                    "errors": [],
                    "timestamp": timezone.now().isoformat()
                }
            else:
                # JSON parse failed — graceful degradation to chat-like response
                logger.warning(f"[ORCHESTRATOR] Analysis JSON parse failed. Responding as text. Raw[:200]: {raw_response[:200]}")
                return {
                    "success": True,
                    "mode": "strategic_chat",
                    "is_analysis": False,
                    "response": raw_response,
                    "reply": raw_response,
                    "analysis": None,
                    "source_engine": "gemini",
                    "errors": ["analysis_json_parse_failed"],
                    "timestamp": timezone.now().isoformat()
                }

        # --- Conversational / Clarification Intent ---
        return {
            "success": True,
            "mode": intent,
            "is_analysis": False,
            "response": raw_response,
            "reply": raw_response,
            "analysis": None,
            "source_engine": "gemini",
            "errors": [],
            "timestamp": timezone.now().isoformat()
        }

    @classmethod
    def _error_response(cls, detail: str) -> dict:
        """Build a standardized error response."""
        return {
            "success": False,
            "mode": "error",
            "is_analysis": False,
            "response": "I'm having difficulty processing that right now. Please try again.",
            "reply": "I'm having difficulty processing that right now. Please try again.",
            "analysis": None,
            "source_engine": "none",
            "errors": [detail],
            "timestamp": timezone.now().isoformat()
        }
