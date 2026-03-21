"""
Comprehensive test suite for the AI Orchestration Layer.
Tests intent routing, JSON parsing resilience, voice session continuity,
API response schema compliance, and the new standardized response contract.

Run:
    python manage.py test tests.test_orchestration --verbosity=2
"""
import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory

from analyzer.services.intent_router import IntentRouter
from analyzer.services.orchestrator import AIOrchestrator, safe_extract_json, normalize_analysis_response


# ---------------------------------------------------------------------------
# 1. Intent Router Tests
# ---------------------------------------------------------------------------
class TestIntentRouter(TestCase):
    """Verify intent classification for all three modes and both sources."""

    def test_analyzer_source_always_full_analysis(self):
        self.assertEqual(IntentRouter.classify("hello world", source='analyzer'), 'full_analysis')
        self.assertEqual(IntentRouter.classify("what is risk?", source='analyzer'), 'full_analysis')

    def test_web_full_analysis_from_explicit_verb(self):
        for verb in ['analyze', 'evaluate', 'validate', 'check']:
            intent = IntentRouter.classify(f"{verb} my AI startup idea for mental health", source='web')
            self.assertEqual(intent, 'full_analysis', f"'{verb}' should trigger full_analysis")

    def test_web_strategic_chat_with_context(self):
        intent = IntentRouter.classify("what are the risks?", source='web', has_context=True)
        self.assertEqual(intent, 'strategic_chat')

    def test_web_clarification_for_short_seed(self):
        intent = IntentRouter.classify("food app", source='web', has_context=False)
        self.assertEqual(intent, 'clarification')

    def test_voice_analysis_with_topic(self):
        intent = IntentRouter.classify("analyze my startup idea about health", source='voice')
        self.assertEqual(intent, 'voice_analysis')

    def test_voice_chat_with_context(self):
        intent = IntentRouter.classify("what about competitors?", source='voice', has_context=True)
        self.assertEqual(intent, 'voice_chat')

    def test_voice_idea_start(self):
        intent = IntentRouter.classify("I want to build a fintech dashboard", source='voice')
        self.assertEqual(intent, 'voice_analysis')

    def test_debug_info_structure(self):
        info = IntentRouter.get_debug_info("analyze startup", source='web', has_context=False)
        self.assertIn('intent', info)
        self.assertIn('clues', info)


# ---------------------------------------------------------------------------
# 2. safe_extract_json Tests
# ---------------------------------------------------------------------------
class TestSafeExtractJson(TestCase):
    """Test the JSON extraction helper."""

    def test_raw_json(self):
        result = safe_extract_json('{"score": 80}')
        self.assertEqual(result['score'], 80)

    def test_markdown_fenced(self):
        result = safe_extract_json('```json\n{"score": 70}\n```')
        self.assertEqual(result['score'], 70)

    def test_plain_markdown_fence(self):
        result = safe_extract_json('```\n{"score": 60}\n```')
        self.assertEqual(result['score'], 60)

    def test_embedded_json(self):
        result = safe_extract_json('Here is the analysis:\n{"score": 50}\nDone.')
        self.assertEqual(result['score'], 50)

    def test_plain_text_returns_none(self):
        result = safe_extract_json('This is just plain text with no JSON.')
        self.assertIsNone(result)

    def test_partial_json_returns_none(self):
        result = safe_extract_json('{"score": 80, "incom')
        self.assertIsNone(result)

    def test_empty_input_returns_none(self):
        self.assertIsNone(safe_extract_json(''))
        self.assertIsNone(safe_extract_json(None))


# ---------------------------------------------------------------------------
# 3. normalize_analysis_response Tests
# ---------------------------------------------------------------------------
class TestNormalizeAnalysis(TestCase):
    """Test analysis normalization fills missing fields."""

    def test_fills_missing_fields(self):
        partial = {"market_demand_score": 85, "final_verdict": "Go."}
        result = normalize_analysis_response(partial)
        self.assertEqual(result['market_demand_score'], 85)
        self.assertEqual(result['risk_score'], 50)  # default
        self.assertIsInstance(result['swot_analysis']['strengths'], list)
        self.assertEqual(result['source_engine'], 'gemini')

    def test_preserves_existing_fields(self):
        full = {
            "market_demand_score": 90,
            "uniqueness_score": 70,
            "risk_score": 30,
            "swot_analysis": {"strengths": ["a"], "weaknesses": ["b"], "opportunities": ["c"], "threats": ["d"]},
            "source_engine": "heuristic"
        }
        result = normalize_analysis_response(full)
        self.assertEqual(result['risk_score'], 30)
        self.assertEqual(result['source_engine'], 'heuristic')


# ---------------------------------------------------------------------------
# 4. Orchestrator Response Contract Tests
# ---------------------------------------------------------------------------
class TestOrchestratorContract(TestCase):
    """Test that _format_response always returns the standardized contract."""

    def _check_contract(self, result):
        """Every response must have these keys."""
        for key in ['success', 'mode', 'is_analysis', 'response', 'reply', 'source_engine', 'errors', 'timestamp']:
            self.assertIn(key, result, f"Missing key: {key}")

    def test_valid_analysis_response(self):
        sample = json.dumps({"market_demand_score": 85, "final_verdict": "Go."})
        result = AIOrchestrator._format_response('full_analysis', sample, 'test')
        self._check_contract(result)
        self.assertTrue(result['success'])
        self.assertTrue(result['is_analysis'])
        self.assertEqual(result['mode'], 'full_analysis')
        self.assertIsNotNone(result['analysis'])

    def test_malformed_json_degrades(self):
        result = AIOrchestrator._format_response('full_analysis', 'Not JSON at all', 'test')
        self._check_contract(result)
        self.assertTrue(result['success'])
        self.assertFalse(result['is_analysis'])
        self.assertEqual(result['mode'], 'strategic_chat')
        self.assertIsNone(result['analysis'])
        self.assertIn('analysis_json_parse_failed', result['errors'])

    def test_chat_response(self):
        result = AIOrchestrator._format_response('strategic_chat', 'Great question!', 'test')
        self._check_contract(result)
        self.assertEqual(result['mode'], 'strategic_chat')
        self.assertFalse(result['is_analysis'])
        self.assertEqual(result['reply'], 'Great question!')

    def test_clarification_response(self):
        result = AIOrchestrator._format_response('clarification', 'Tell me more.', 'test')
        self._check_contract(result)
        self.assertEqual(result['mode'], 'clarification')

    def test_error_response(self):
        result = AIOrchestrator._error_response("Something broke")
        self._check_contract(result)
        self.assertFalse(result['success'])
        self.assertEqual(result['mode'], 'error')
        self.assertIn('Something broke', result['errors'])


# ---------------------------------------------------------------------------
# 5. Voice Session Continuity
# ---------------------------------------------------------------------------
class TestVoiceSessionContinuity(TestCase):

    def setUp(self):
        from voice_assistant.views import VOICE_SESSIONS
        VOICE_SESSIONS.clear()

    @patch('analyzer.services.orchestrator.gemini_service')
    def test_session_created_on_first_request(self, mock_gemini):
        mock_gemini.generate_content.return_value = json.dumps({
            "market_demand_score": 80, "idea_summary": "AI Health", "final_verdict": "Go."
        })
        factory = RequestFactory()
        request = factory.post(
            '/voice/',
            data=json.dumps({"command": "analyze my health startup"}),
            content_type='application/json'
        )
        from voice_assistant.views import voice_interface, VOICE_SESSIONS
        response = voice_interface(request)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('session_id', data)
        self.assertIn(data['session_id'], VOICE_SESSIONS)

    @patch('analyzer.services.orchestrator.gemini_service')
    def test_context_maintained_across_turns(self, mock_gemini):
        mock_gemini.generate_content.side_effect = [
            json.dumps({"market_demand_score": 80, "idea_summary": "AI Health", "final_verdict": "Go."}),
            "Focus on user retention."
        ]
        factory = RequestFactory()
        from voice_assistant.views import voice_interface, VOICE_SESSIONS

        req1 = factory.post('/voice/', data=json.dumps({"command": "analyze my health startup"}), content_type='application/json')
        resp1 = json.loads(voice_interface(req1).content)
        sid = resp1['session_id']

        req2 = factory.post('/voice/', data=json.dumps({"command": "what about competition?", "session_id": sid}), content_type='application/json')
        resp2 = json.loads(voice_interface(req2).content)

        self.assertTrue(resp2['success'])
        self.assertEqual(VOICE_SESSIONS[sid]['idea_context'], 'AI Health')


# ---------------------------------------------------------------------------
# 6. API Response Schema
# ---------------------------------------------------------------------------
class TestAPIResponseSchema(TestCase):

    @patch('analyzer.services.orchestrator.gemini_service')
    def test_analyze_idea_api_schema(self, mock_gemini):
        mock_gemini.generate_content.return_value = json.dumps({
            "market_demand_score": 75, "final_verdict": "Build it."
        })
        factory = RequestFactory()
        from api.views import AnalyzeIdeaAPIView
        request = factory.post(
            '/api/analyze/',
            data=json.dumps({"title": "Test", "description": "A health AI app", "industry": "HealthTech"}),
            content_type='application/json'
        )
        response = AnalyzeIdeaAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertTrue(data['success'])
        self.assertEqual(data['mode'], 'full_analysis')
        self.assertIn('analysis', data)

    @patch('analyzer.services.orchestrator.gemini_service')
    def test_quick_analysis_api_schema(self, mock_gemini):
        mock_gemini.generate_content.return_value = json.dumps({
            "market_demand_score": 60, "final_verdict": "Interesting."
        })
        factory = RequestFactory()
        from api.views import QuickAnalysisAPIView
        request = factory.post(
            '/api/quick-analysis/',
            data=json.dumps({"description": "An AI tool for business analysis that helps founders validate ideas quickly"}),
            content_type='application/json'
        )
        response = QuickAnalysisAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertTrue(data['success'])
        self.assertIn('mode', data)

    def test_analyze_idea_missing_fields(self):
        factory = RequestFactory()
        from api.views import AnalyzeIdeaAPIView
        request = factory.post(
            '/api/analyze/',
            data=json.dumps({"title": "Test"}),
            content_type='application/json'
        )
        response = AnalyzeIdeaAPIView.as_view()(request)
        self.assertEqual(response.status_code, 400)
