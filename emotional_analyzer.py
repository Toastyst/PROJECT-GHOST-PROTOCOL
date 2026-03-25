#!/usr/bin/env python3
"""
Emotional Analyzer for PROJECT: GHOST PROTOCOL

Analyzes text for emotional context, developer intention, and resonance scoring.
Uses LLM integration to extract meaningful emotional metadata from development artifacts.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from models import EmotionalEntry, FeedRequest
from config import Config

class EmotionalAnalyzer:
    """LLM-powered emotional analysis engine for development artifacts."""

    def __init__(self):
        self.config = Config
        self.emotional_keywords = {
            'frustration': ['hacky', 'ugly', 'messy', 'broken', 'wtf', 'fixme', 'todo', 'sorry'],
            'urgency': ['urgent', 'critical', 'deadline', 'rush', 'asap', 'emergency'],
            'pride': ['beautiful', 'elegant', 'clean', 'perfect', 'masterpiece', 'proud'],
            'confusion': ['confused', 'lost', 'unclear', 'weird', 'strange', 'mysterious'],
            'relief': ['finally', 'thank god', 'phew', 'relieved', 'working'],
            'exhaustion': ['tired', 'late night', '3am', 'coffee', 'sleep', 'drained'],
            'curiosity': ['interesting', 'curious', 'wonder', 'explore', 'investigate'],
            'caution': ['careful', 'risky', 'dangerous', 'warning', 'be careful']
        }

    def analyze_emotion(self, text: str, context: Dict[str, Any]) -> EmotionalEntry:
        """Analyze text for emotional content and create EmotionalEntry."""
        try:
            # Extract basic emotional indicators
            emotional_hints = self._extract_emotional_hints(text)
            resonance_score = self._calculate_resonance_score(text, emotional_hints, context)
            emotional_note = self._generate_emotional_note(text, emotional_hints)
            intent_payload = self._extract_intent(text, context)
            sacred_moments = self._identify_sacred_moments(text, context)

            # Create unique ID
            entry_id = f"emotional_{context.get('timestamp', datetime.now().isoformat())}_{hash(text) % 10000}"

            return EmotionalEntry(
                id=entry_id,
                content=text,
                type=context.get('type', 'unknown'),
                metadata={
                    'author': context.get('author', 'unknown'),
                    'timestamp': context.get('timestamp', datetime.now().isoformat()),
                    'file_path': context.get('file_path', ''),
                    'source': context.get('source', 'unknown')
                },
                relationships=[],  # Will be populated by Nexus
                resonance_score=resonance_score,
                emotional_note=emotional_note,
                intent_payload=intent_payload,
                sacred_moments=sacred_moments
            )

        except Exception as e:
            print(f"Emotional analysis error: {e}")
            # Return minimal entry on error
            return EmotionalEntry(
                id=f"error_{hash(text)}",
                content=text,
                type='error',
                metadata={'error': str(e)},
                relationships=[],
                resonance_score=0.0,
                emotional_note="Analysis failed",
                intent_payload={},
                sacred_moments=[]
            )

    def _extract_emotional_hints(self, text: str) -> List[str]:
        """Extract emotional keywords and phrases from text."""
        hints = []
        text_lower = text.lower()

        for emotion, keywords in self.emotional_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    hints.append(f"{emotion}:{keyword}")

        # Look for time indicators that suggest emotional state
        if re.search(r'\d{1,2}:\d{2}', text) or 'am' in text_lower or 'pm' in text_lower:
            hints.append("timing:late_night")

        # Look for apology patterns
        if 'sorry' in text_lower or 'apologize' in text_lower:
            hints.append("apology:expressed")

        # Look for urgency indicators
        if '!' in text or 'urgent' in text_lower:
            hints.append("urgency:high")

        return hints

    def _calculate_resonance_score(self, text: str, hints: List[str], context: Dict[str, Any]) -> float:
        """Calculate emotional resonance score (0-10)."""
        base_score = 0.0

        # Base score from emotional hints
        emotional_count = len([h for h in hints if ':' in h])
        base_score += min(emotional_count * 0.5, 3.0)

        # Bonus for time context (late night commits are more resonant)
        if any('timing:' in h for h in hints):
            base_score += 2.0

        # Bonus for apologies (indicates struggle)
        if any('apology:' in h for h in hints):
            base_score += 1.5

        # Bonus for explicit emotional language
        emotional_words = ['feel', 'felt', 'feeling', 'emotion', 'heart', 'soul']
        if any(word in text.lower() for word in emotional_words):
            base_score += 1.0

        # Context bonuses
        if context.get('source') == 'commit_message':
            base_score += 0.5  # Commit messages are intentional
        elif context.get('source') == 'pr_comment':
            base_score += 1.0  # PR comments show collaboration struggle

        return min(base_score, 10.0)

    def _generate_emotional_note(self, text: str, hints: List[str]) -> str:
        """Generate human-readable emotional note."""
        if not hints:
            return "Neutral technical content"

        # Group hints by emotion
        emotion_groups = {}
        for hint in hints:
            if ':' in hint:
                emotion, trigger = hint.split(':', 1)
                if emotion not in emotion_groups:
                    emotion_groups[emotion] = []
                emotion_groups[emotion].append(trigger)

        # Create note from dominant emotions
        notes = []
        for emotion, triggers in emotion_groups.items():
            if emotion == 'frustration':
                notes.append(f"Expresses frustration with {', '.join(triggers[:2])}")
            elif emotion == 'exhaustion':
                notes.append(f"Shows signs of developer fatigue ({', '.join(triggers[:2])})")
            elif emotion == 'urgency':
                notes.append(f"Conveys time pressure ({', '.join(triggers[:2])})")
            elif emotion == 'pride':
                notes.append(f"Displays satisfaction with {', '.join(triggers[:2])}")
            elif emotion == 'apology':
                notes.append("Contains developer apology or regret")
            elif emotion == 'timing':
                notes.append("Created during off-hours")

        return "; ".join(notes[:3]) if notes else "Contains emotional indicators"

    def _extract_intent(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract developer intention from text."""
        intent = {
            'primary_goal': 'unknown',
            'emotional_state': 'neutral',
            'confidence_level': 'medium',
            'urgency_level': 'normal'
        }

        text_lower = text.lower()

        # Primary goal detection
        if any(word in text_lower for word in ['fix', 'repair', 'resolve', 'correct']):
            intent['primary_goal'] = 'fix_issue'
        elif any(word in text_lower for word in ['add', 'implement', 'create', 'build']):
            intent['primary_goal'] = 'add_feature'
        elif any(word in text_lower for word in ['refactor', 'clean', 'improve', 'optimize']):
            intent['primary_goal'] = 'improve_code'
        elif any(word in text_lower for word in ['merge', 'integrate', 'combine']):
            intent['primary_goal'] = 'integrate_changes'

        # Emotional state
        if any(word in text_lower for word in ['sorry', 'apologize', 'regret']):
            intent['emotional_state'] = 'regretful'
        elif any(word in text_lower for word in ['proud', 'excited', 'great']):
            intent['emotional_state'] = 'positive'
        elif any(word in text_lower for word in ['frustrated', 'annoyed', 'wtf']):
            intent['emotional_state'] = 'frustrated'
        elif any(word in text_lower for word in ['tired', 'exhausted', 'drained']):
            intent['emotional_state'] = 'exhausted'

        # Confidence level
        if any(word in text_lower for word in ['hacky', 'temporary', 'quick', 'dirty']):
            intent['confidence_level'] = 'low'
        elif any(word in text_lower for word in ['perfect', 'elegant', 'beautiful']):
            intent['confidence_level'] = 'high'

        # Urgency level
        if any(word in text_lower for word in ['urgent', 'critical', 'asap', 'emergency']):
            intent['urgency_level'] = 'high'
        elif any(word in text_lower for word in ['whenever', 'eventually', 'someday']):
            intent['urgency_level'] = 'low'

        return intent

    def _identify_sacred_moments(self, text: str, context: Dict[str, Any]) -> List[str]:
        """Identify sacred moments - significant emotional development events."""
        moments = []

        text_lower = text.lower()

        # Late night commits
        if re.search(r'\d{1,2}:\d{2}', text) and any(word in text_lower for word in ['am', 'late', 'night']):
            moments.append("Late night development session")

        # Apologies in code
        if 'sorry' in text_lower and context.get('source') == 'commit_message':
            moments.append("Developer apology in commit")

        # Emotional breakthroughs
        if any(phrase in text_lower for phrase in ['finally working', 'thank god', 'phew', 'relieved']):
            moments.append("Emotional breakthrough moment")

        # Technical debt acknowledgments
        if any(word in text_lower for word in ['technical debt', 'hacky but', 'temporary fix', 'will refactor']):
            moments.append("Technical debt acknowledgment")

        # Learning moments
        if any(word in text_lower for word in ['learned', 'discovered', 'realized', 'understood']):
            moments.append("Learning and growth moment")

        return moments


# Global analyzer instance
_analyzer = None

def get_emotional_analyzer() -> EmotionalAnalyzer:
    """Get or create emotional analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = EmotionalAnalyzer()
    return _analyzer

async def analyze_emotion(text: str, context: Dict[str, Any]) -> EmotionalEntry:
    """Convenience function for emotional analysis."""
    analyzer = get_emotional_analyzer()
    return analyzer.analyze_emotion(text, context)
