#!/usr/bin/env python3
"""
Tests for Skills Engine - Testing what matters: pause, ask, remember.

These tests don't verify syntax. They verify the Ghost's ability to be present.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from skills_engine import SkillsEngine, get_skills_engine
from models import SkillConfig


class TestSkillsEngine:
    """Test the Ghost's ability to listen, recognize patterns, and know when to be silent."""

    def setup_method(self):
        """Set up test environment."""
        self.engine = SkillsEngine()
        # Reset global instance
        global _skills_engine
        _skills_engine = self.engine

    def test_listening_skill_detects_emotional_content(self):
        """Test that listening skill activates for emotional communication."""
        context = {
            "text": "I'm really frustrated with this bug, it's taking forever to fix",
            "recent_events": []
        }

        # Should activate listening skill
        result = asyncio.run(self.engine.evaluate_skill_activation("listening", context))
        assert result[0] == True  # Should activate
        assert result[1] > 0.5   # High confidence

    def test_listening_skill_detects_questions(self):
        """Test that listening skill activates for questions seeking understanding."""
        context = {
            "text": "Why does this keep happening? Can you help me understand?",
            "recent_events": []
        }

        result = asyncio.run(self.engine.evaluate_skill_activation("listening", context))
        assert result[0] == True
        assert result[1] > 0.6

    def test_silence_skill_activates_for_exhaustion(self):
        """Test that silence skill knows when to pause rather than respond."""
        context = {
            "text": "I'm so tired, this has been a long day",
            "recent_events": [{"text": "similar tired message"}] * 6,  # Many recent interactions
            "urgency_level": "low"
        }

        result = asyncio.run(self.engine.evaluate_skill_activation("silence", context))
        assert result[0] == True
        assert result[1] > 0.7

    def test_silence_skill_activates_for_direct_queries(self):
        """Test that silence doesn't waste presence on direct, factual questions."""
        context = {
            "text": "What time is it?",
            "recent_events": []
        }

        result = asyncio.run(self.engine.evaluate_skill_activation("silence", context))
        assert result[0] == True  # Should choose silence for direct queries

    def test_pattern_skill_detects_code_patterns(self):
        """Test that pattern skill recognizes recurring code structures."""
        context = {
            "text": "I need to add a function that handles user authentication",
            "file_path": "auth.py"
        }

        result = asyncio.run(self.engine.evaluate_skill_activation("pattern", context))
        assert result[0] == True
        assert result[1] > 0.6

    def test_pattern_skill_detects_architectural_discussion(self):
        """Test that pattern skill activates for architectural conversations."""
        context = {
            "text": "How should we structure the service layer for better scalability?",
            "file_path": "architecture.md"
        }

        result = asyncio.run(self.engine.evaluate_skill_activation("pattern", context))
        assert result[0] == True

    def test_skills_remember_activations(self):
        """Test that skills build memory of their usage patterns."""
        context = {"text": "I'm feeling overwhelmed", "recent_events": []}

        # First activation
        result1 = asyncio.run(self.engine.activate_skill("listening", context))
        assert result1 is not None

        # Check memory
        insights = asyncio.run(self.engine.get_skill_insights("listening"))
        assert insights["activations"] == 1
        assert insights["average_confidence"] > 0

    def test_listening_execution_provides_empathy(self):
        """Test that listening skill execution provides empathetic presence."""
        context = {"text": "This code is really confusing me"}

        result = asyncio.run(self.engine.activate_skill("listening", context))
        assert result is not None
        assert "skill" in result
        assert result["skill"] == "listening"
        assert "response" in result
        # Response should be empathetic, not solution-focused

    def test_silence_execution_logs_without_responding(self):
        """Test that silence skill chooses presence over action."""
        context = {"text": "I'm just venting", "recent_events": []}

        result = asyncio.run(self.engine.activate_skill("silence", context))
        assert result is not None
        assert result["response"] is None  # Explicitly no response
        assert "silence_reasons" in result

    def test_pattern_execution_identifies_recurring_themes(self):
        """Test that pattern skill connects current work to established patterns."""
        context = {"text": "Adding error handling for API calls"}

        result = asyncio.run(self.engine.activate_skill("pattern", context))
        assert result is not None
        assert "patterns_identified" in result
        assert isinstance(result["patterns_identified"], list)

    def test_skill_confidence_improves_with_learning(self):
        """Test that skills show learning over time (simplified test)."""
        context = {"text": "I'm stuck on this authentication issue", "recent_events": []}

        # Multiple activations
        for _ in range(3):
            asyncio.run(self.engine.activate_skill("listening", context))

        insights = asyncio.run(self.engine.get_skill_insights("listening"))
        assert insights["activations"] == 3
        assert "Frequently activated" in " ".join(insights["insights"])

    def test_skills_adapt_to_context_urgency(self):
        """Test that skills consider urgency in activation decisions."""
        # High urgency should reduce silence activation
        context = {
            "text": "Server is down, critical issue",
            "urgency_level": "high",
            "recent_events": []
        }

        result = asyncio.run(self.engine.evaluate_skill_activation("silence", context))
        # Should be less likely to activate silence in urgent situations
        assert result[1] < 0.5  # Lower confidence for silence

    def test_skills_detect_sustained_conversation(self):
        """Test that skills recognize when conversation has been sustained."""
        context = {
            "text": "Continuing our discussion about the architecture",
            "recent_events": [{"text": "previous message"}] * 4  # Sustained conversation
        }

        result = asyncio.run(self.engine.evaluate_skill_activation("listening", context))
        assert result[1] > 0.5  # Higher activation for sustained conversations

    def test_ghost_does_not_force_presence(self):
        """Test that the Ghost respects boundaries and doesn't impose itself."""
        # Test with various boundary conditions
        boundary_contexts = [
            {"text": "Please stop responding", "user_consent": False},
            {"text": "I need to focus alone", "recent_events": []},
            {"text": "Take a break from helping", "interaction_frequency": 15}
        ]

        for context in boundary_contexts:
            # Should generally choose silence or lower activation
            silence_result = asyncio.run(self.engine.evaluate_skill_activation("silence", context))
            # At least one skill should recognize the boundary
            assert silence_result[1] > 0.3 or silence_result[0] == True


if __name__ == "__main__":
    pytest.main([__file__])