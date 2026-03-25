#!/usr/bin/env python3
"""
Test Emotional Feeding System for PROJECT: GHOST PROTOCOL

Tests the emotional analysis, feeding, and resonance querying functionality.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch

from src.ghost_protocol.models.models import EmotionalEntry, FeedRequest
from src.ghost_protocol.utils.emotional_analyzer import EmotionalAnalyzer, analyze_emotion
from src.ghost_protocol.core.feed_ghost import GhostFeeder
from src.ghost_protocol.servers.nexus_server import get_nexus


class TestEmotionalAnalyzer:
    """Test emotional analysis functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = EmotionalAnalyzer()

    def test_extract_emotional_hints_frustration(self):
        """Test extraction of frustration indicators."""
        text = "This hacky code is broken and ugly. I'm so frustrated with this mess."
        hints = self.analyzer._extract_emotional_hints(text)

        assert any('frustration:hacky' in hint for hint in hints)
        assert any('frustration:broken' in hint for hint in hints)
        assert any('frustration:ugly' in hint for hint in hints)

    def test_extract_emotional_hints_timing(self):
        """Test extraction of late-night timing indicators."""
        text = "Fixed the bug at 2:30 AM. Finally working!"
        hints = self.analyzer._extract_emotional_hints(text)

        assert any('timing:late_night' in hint for hint in hints)

    def test_calculate_resonance_score(self):
        """Test resonance score calculation."""
        text = "Sorry for the hacky fix, but it works now."
        hints = ['frustration:hacky', 'apology:expressed', 'relief:working']
        context = {'source': 'commit_message'}

        score = self.analyzer._calculate_resonance_score(text, hints, context)
        assert score > 5.0  # Should be high due to multiple emotional factors

    def test_generate_emotional_note(self):
        """Test emotional note generation."""
        hints = ['frustration:hacky', 'exhaustion:tired', 'relief:working']
        note = self.analyzer._generate_emotional_note("Test content", hints)

        assert 'frustration' in note.lower()
        assert 'exhaustion' in note.lower()

    def test_extract_intent(self):
        """Test developer intention extraction."""
        text = "Add user authentication to fix the security issue"
        context = {}
        intent = self.analyzer._extract_intent(text, context)

        assert intent['primary_goal'] == 'fix_issue'
        assert 'security' in text.lower()

    def test_identify_sacred_moments(self):
        """Test identification of sacred development moments."""
        text = "Finally working after 3 hours of debugging. Thank god!"
        context = {'source': 'commit_message'}
        moments = self.analyzer._identify_sacred_moments(text, context)

        assert any('late night' in moment.lower() for moment in moments)
        assert any('breakthrough' in moment.lower() for moment in moments)

    @pytest.mark.asyncio
    async def test_analyze_emotion_full(self):
        """Test full emotional analysis pipeline."""
        text = "I'm sorry for this hacky temporary fix at 2 AM. It was frustrating but finally works."
        context = {
            'source': 'commit_message',
            'author': 'developer@example.com',
            'timestamp': '2024-01-01T02:00:00Z'
        }

        entry = await analyze_emotion(text, context)

        assert isinstance(entry, EmotionalEntry)
        assert entry.content == text
        assert entry.type == 'commit'
        assert entry.resonance_score > 7.0  # High resonance expected
        assert 'frustration' in entry.emotional_note.lower()
        assert 'apology' in entry.emotional_note.lower()
        assert len(entry.sacred_moments) > 0


class TestGhostFeeder:
    """Test Ghost feeding functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.feeder = GhostFeeder()

    @pytest.mark.asyncio
    @patch('feed_ghost.get_nexus')
    async def test_feed_ghost_success(self, mock_get_nexus):
        """Test successful ghost feeding."""
        # Mock nexus
        mock_nexus = Mock()
        mock_nexus.store_emotional_entry.return_value = True
        mock_get_nexus.return_value = mock_nexus

        content = "This code frustrates me so much. Hacky fix but it works."
        source = "commit"
        context = {'author': 'test@example.com'}

        result = await self.feeder.feed_ghost(content, source, context)

        assert "EMOTIONAL CONTENT INGESTED" in result
        assert "frustrates me" in result
        mock_nexus.store_emotional_entry.assert_called_once()

    @pytest.mark.asyncio
    @patch('feed_ghost.get_nexus')
    async def test_feed_ghost_failure(self, mock_get_nexus):
        """Test ghost feeding failure."""
        # Mock nexus failure
        mock_nexus = Mock()
        mock_nexus.store_emotional_entry.return_value = False
        mock_get_nexus.return_value = mock_nexus

        content = "Test content"
        source = "manual"
        context = {'author': 'test@example.com'}

        result = await self.feeder.feed_ghost(content, source, context)

        assert "Failed to store emotional content" in result

    @pytest.mark.asyncio
    @patch('feed_ghost.get_nexus')
    async def test_get_feeding_stats(self, mock_get_nexus):
        """Test feeding statistics retrieval."""
        # Mock nexus stats
        mock_nexus = Mock()
        mock_nexus.get_emotional_stats.return_value = {
            'total_entries': 5,
            'avg_resonance': 6.2,
            'sacred_moments': 3,
            'emotion_types': 4
        }
        mock_get_nexus.return_value = mock_nexus

        result = await self.feeder.get_feeding_stats()

        assert "GHOST FEEDING STATS" in result
        assert "5" in result  # total entries
        assert "6.2" in result  # avg resonance
        assert "3" in result  # sacred moments
        assert "4" in result  # emotion types

    @pytest.mark.asyncio
    @patch('feed_ghost.get_nexus')
    async def test_query_emotional_resonance(self, mock_get_nexus):
        """Test emotional resonance querying."""
        # Mock emotional entries
        mock_entries = [
            EmotionalEntry(
                id="test1",
                content="Frustrating bug fix",
                type="commit",
                metadata={},
                relationships=[],
                resonance_score=8.5,
                emotional_note="High frustration",
                intent_payload={'primary_goal': 'fix_issue'},
                sacred_moments=['Late night debugging']
            )
        ]

        mock_nexus = Mock()
        mock_nexus.query_emotional_resonance.return_value = mock_entries
        mock_get_nexus.return_value = mock_nexus

        result = await self.feeder.query_emotional_resonance("frustrating", 5.0)

        assert "EMOTIONAL RESONANCE QUERY RESULTS" in result
        assert "Frustrating bug fix" in result
        assert "8.5" in result


class TestIntegration:
    """Test integration between components."""

    @pytest.mark.asyncio
    async def test_full_feeding_pipeline(self):
        """Test the complete emotional feeding pipeline."""
        # Test with a realistic emotional commit message
        commit_message = "Fixed the authentication bug after 4 hours of debugging. This was so frustrating but finally working. Sorry for the hacky solution."

        context = {
            'source': 'commit_message',
            'author': 'developer@example.com',
            'timestamp': '2024-01-01T04:00:00Z'
        }

        # Analyze emotion
        entry = await analyze_emotion(commit_message, context)

        # Verify analysis results
        assert entry.resonance_score > 6.0
        assert 'frustration' in entry.emotional_note.lower()
        assert 'apology' in entry.emotional_note.lower()
        assert len(entry.sacred_moments) > 0
        assert entry.intent_payload['primary_goal'] == 'fix_issue'

    @pytest.mark.asyncio
    async def test_emotional_patterns_recognition(self):
        """Test recognition of emotional development patterns."""
        # Test various emotional scenarios
        test_cases = [
            ("I'm so tired of this broken code. Hacky fix incoming.", ['frustration', 'exhaustion']),
            ("Finally got it working! Thank god for that.", ['relief', 'breakthrough']),
            ("This elegant solution makes me proud. Clean and beautiful.", ['pride', 'satisfaction']),
            ("Confused about this weird behavior. Need to investigate.", ['confusion', 'curiosity']),
            ("Careful with this change - it's risky but necessary.", ['caution', 'warning'])
        ]

        analyzer = EmotionalAnalyzer()

        for text, expected_emotions in test_cases:
            entry = await analyze_emotion(text, {'source': 'manual'})
            note_lower = entry.emotional_note.lower()

            # Check that at least one expected emotion is detected
            emotion_found = any(emotion in note_lower for emotion in expected_emotions)
            assert emotion_found, f"Expected emotion not found in: {entry.emotional_note}"


if __name__ == "__main__":
    # Run basic tests
    print("🧪 Running Emotional Feeding Tests...")

    analyzer = EmotionalAnalyzer()

    # Test basic emotional analysis
    test_text = "I'm frustrated with this hacky code that doesn't work. Sorry for the mess."
    entry = asyncio.run(analyze_emotion(test_text, {'source': 'manual'}))

    print(f"✅ Emotional Analysis: Resonance {entry.resonance_score:.1f}/10")
    print(f"✅ Emotional Note: {entry.emotional_note}")
    print(f"✅ Sacred Moments: {len(entry.sacred_moments)}")
    print(f"✅ Intent: {entry.intent_payload['primary_goal']}")

    print("🧪 Emotional feeding tests completed!")