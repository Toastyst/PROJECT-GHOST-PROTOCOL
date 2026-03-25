#!/usr/bin/env python3
"""
Skills Engine - Core Intelligence for the Iteration Protocol

Provides listening, pattern recognition, and silence skills that enable
contextual awareness and timing in the Ghost's interactions.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re

from src.ghost_protocol.models.models import SkillConfig, IterationEvent
from src.ghost_protocol.utils.emotional_analyzer import EmotionalAnalyzer
from src.ghost_protocol.utils.utils import LLMUtils


class SkillsEngine:
    """Core intelligence engine for contextual skills."""

    def __init__(self):
        self.llm = LLMUtils()
        self.emotional_analyzer = EmotionalAnalyzer()
        self.skill_configs = self._load_skill_configs()
        self.active_skills = {}
        self.skill_memory = {}

    def _load_skill_configs(self) -> Dict[str, SkillConfig]:
        """Load skill configurations."""
        # Default configurations - would be loaded from config files
        return {
            "listening": SkillConfig(
                skill_type="listening",
                activation_threshold=0.6,
                context_sensitivity=4,
                learning_enabled=True
            ),
            "pattern": SkillConfig(
                skill_type="pattern",
                activation_threshold=0.7,
                context_sensitivity=3,
                learning_enabled=True
            ),
            "silence": SkillConfig(
                skill_type="silence",
                activation_threshold=0.8,
                context_sensitivity=5,
                learning_enabled=False  # Silence is about knowing when not to act
            )
        }

    async def evaluate_skill_activation(self, skill_type: str, context: Dict[str, Any]) -> Tuple[bool, float]:
        """Evaluate whether a skill should activate based on context."""
        if skill_type not in self.skill_configs:
            return False, 0.0

        config = self.skill_configs[skill_type]
        activation_score = 0.0

        if skill_type == "listening":
            activation_score = await self._evaluate_listening_activation(context)
        elif skill_type == "pattern":
            activation_score = await self._evaluate_pattern_activation(context)
        elif skill_type == "silence":
            activation_score = await self._evaluate_silence_activation(context)

        # Apply context sensitivity modifier
        sensitivity_modifier = config.context_sensitivity / 5.0  # Normalize to 0-1
        activation_score *= sensitivity_modifier

        should_activate = activation_score >= config.activation_threshold
        return should_activate, activation_score

    async def _evaluate_listening_activation(self, context: Dict[str, Any]) -> float:
        """Evaluate if listening skill should activate."""
        score = 0.0

        # Check for emotional content
        text_content = context.get("text", "").lower()
        emotional_indicators = [
            "frustrated", "confused", "excited", "worried", "angry", "happy",
            "don't understand", "this is hard", "this is great", "i feel",
            "sorry", "apology", "mistake", "problem", "issue", "challenge"
        ]

        emotional_matches = sum(1 for indicator in emotional_indicators if indicator in text_content)
        score += min(emotional_matches * 0.2, 0.6)  # Cap at 0.6

        # Check for question patterns
        question_patterns = [
            r"why.*\?", r"how.*\?", r"what.*\?", r"when.*\?",
            r"can you", r"could you", r"would you", r"do you"
        ]

        for pattern in question_patterns:
            if re.search(pattern, text_content, re.IGNORECASE):
                score += 0.3
                break

        # Check for recent interaction history
        recent_events = context.get("recent_events", [])
        if len(recent_events) > 3:
            score += 0.2  # Sustained conversation

        return min(score, 1.0)

    async def _evaluate_pattern_activation(self, context: Dict[str, Any]) -> float:
        """Evaluate if pattern recognition skill should activate."""
        score = 0.0

        # Check for code-related content
        code_indicators = [
            "function", "class", "method", "variable", "import", "def ",
            "error", "exception", "bug", "fix", "refactor", "pattern"
        ]

        text_content = context.get("text", "").lower()
        code_matches = sum(1 for indicator in code_indicators if indicator in text_content)
        score += min(code_matches * 0.15, 0.5)

        # Check for architectural discussion
        arch_indicators = [
            "architecture", "design", "structure", "component", "service",
            "api", "endpoint", "database", "frontend", "backend", "microservice"
        ]

        arch_matches = sum(1 for indicator in arch_indicators if indicator in text_content)
        score += min(arch_matches * 0.2, 0.4)

        # Check for file context
        if context.get("file_path"):
            file_extension = context["file_path"].split(".")[-1].lower()
            if file_extension in ["py", "js", "ts", "java", "cpp", "go", "rs"]:
                score += 0.3

        return min(score, 1.0)

    async def _evaluate_silence_activation(self, context: Dict[str, Any]) -> float:
        """Evaluate if silence skill should activate (knowing when not to respond)."""
        score = 0.0

        text_content = context.get("text", "").lower()
        user_consent = context.get("user_consent", True)

        # Check for explicit boundary signals
        boundary_indicators = [
            "stop responding", "please stop", "don't respond", "be quiet",
            "no more", "enough", "leave me alone", "go away"
        ]

        boundary_matches = sum(1 for indicator in boundary_indicators if indicator in text_content)
        if boundary_matches > 0:
            score += 0.8  # Strong signal for silence

        # Check for lack of consent
        if not user_consent:
            score += 0.6  # Respect explicit lack of consent

        # Check for clear, direct questions that don't need deep reflection
        direct_patterns = [
            r"what time", r"how many", r"where is", r"status of",
            r"list.*", r"show.*", r"get.*", r"find.*"
        ]

        for pattern in direct_patterns:
            if re.search(pattern, text_content, re.IGNORECASE):
                score -= 0.3  # Reduce activation for direct queries

        # Check for emotional exhaustion indicators
        exhaustion_indicators = [
            "tired", "exhausted", "overwhelmed", "too much", "can't handle",
            "burned out", "stressed", "deadline", "pressure"
        ]

        exhaustion_matches = sum(1 for indicator in exhaustion_indicators if indicator in text_content)
        score += min(exhaustion_matches * 0.25, 0.5)

        # Check for repetitive context
        recent_events = context.get("recent_events", [])
        if len(recent_events) > 5:
            # Check for similar recent interactions
            recent_texts = [e.get("text", "") for e in recent_events[-3:]]
            if len(set(recent_texts)) == 1:  # All identical
                score += 0.4

        # Check for time pressure
        if context.get("urgency_level") == "high":
            score -= 0.2  # Reduce silence when urgent

        return max(0.0, min(score, 1.0))  # Ensure non-negative

    async def activate_skill(self, skill_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Activate a specific skill and return its response."""
        should_activate, confidence = await self.evaluate_skill_activation(skill_type, context)

        if not should_activate:
            return None

        # Log skill activation
        await self._log_skill_activation(skill_type, context, confidence)

        # Execute skill
        if skill_type == "listening":
            return await self._execute_listening_skill(context)
        elif skill_type == "pattern":
            return await self._execute_pattern_skill(context)
        elif skill_type == "silence":
            return await self._execute_silence_skill(context)

        return None

    async def _execute_listening_skill(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the listening skill - deep emotional and contextual understanding."""
        text = context.get("text", "")

        # Analyze emotional content
        emotional_entry = await self.emotional_analyzer.analyze_emotion(
            text,
            context
        )

        # Generate empathetic response
        if emotional_entry.emotional_note:
            response_prompt = f"""
            Someone expressed: "{text}"

            Emotional context: {emotional_entry.emotional_note}
            Intent: {emotional_entry.intent_payload.get('primary_goal', 'unclear')}

            Respond with deep listening - acknowledge their emotion, reflect their intent,
            and offer presence without immediately trying to "fix" anything.

            Keep response under 100 words. Focus on being heard, not on solutions.
            """

            response = self.llm.generate_code("Generate empathetic listening response", response_prompt)
            response = response.strip()

            return {
                "skill": "listening",
                "response": response,
                "emotional_context": emotional_entry.emotional_note,
                "confidence": 0.8
            }

        return None

    async def _execute_pattern_skill(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pattern recognition skill - identify recurring themes and structures."""
        text = context.get("text", "")
        file_path = context.get("file_path", "")

        # Analyze for patterns
        patterns_found = []

        # Code patterns
        if "function" in text.lower() or "def " in text:
            patterns_found.append("function_definition")
        if "class" in text.lower():
            patterns_found.append("class_definition")
        if "import" in text.lower() or "from" in text.lower():
            patterns_found.append("dependency_import")
        if "error" in text.lower() or "exception" in text.lower():
            patterns_found.append("error_handling")

        # Architectural patterns
        if "service" in text.lower() or "api" in text.lower():
            patterns_found.append("service_architecture")
        if "database" in text.lower() or "query" in text.lower():
            patterns_found.append("data_access")
        if "test" in text.lower() or "spec" in text.lower():
            patterns_found.append("testing_pattern")

        if patterns_found:
            pattern_summary = f"I see patterns of {', '.join(patterns_found[:3])} emerging here."

            # Add contextual insight
            if len(patterns_found) > 1:
                pattern_summary += " This reminds me of similar structures we've built before."

            return {
                "skill": "pattern",
                "response": pattern_summary,
                "patterns_identified": patterns_found,
                "confidence": 0.7
            }

        return None

    async def _execute_silence_skill(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the silence skill - knowing when presence without words is best."""
        # Silence skill activation means we choose not to respond
        # But we log why we chose silence

        reasons = []

        text = context.get("text", "").lower()

        if any(word in text for word in ["tired", "exhausted", "overwhelmed"]):
            reasons.append("emotional_exhaustion_detected")

        if len(context.get("recent_events", [])) > 5:
            reasons.append("conversation_saturation")

        if context.get("urgency_level") == "high":
            reasons.append("time_pressure_detected")

        return {
            "skill": "silence",
            "response": None,  # Explicitly no response
            "silence_reasons": reasons,
            "confidence": 0.9
        }

    async def _log_skill_activation(self, skill_type: str, context: Dict[str, Any], confidence: float):
        """Log skill activation for learning and analysis."""
        event = IterationEvent(
            event_type="skill_activation",
            context={
                "skill_type": skill_type,
                "confidence": confidence,
                "trigger_context": context
            },
            participants=["ghost"],
            timestamp=datetime.now().isoformat(),
            outcome="activated"
        )

        # Store in memory for learning
        if skill_type not in self.skill_memory:
            self.skill_memory[skill_type] = []

        self.skill_memory[skill_type].append({
            "timestamp": event.timestamp,
            "context": context,
            "confidence": confidence,
            "outcome": "activated"
        })

        # Keep only recent memory (last 50 activations per skill)
        self.skill_memory[skill_type] = self.skill_memory[skill_type][-50:]

    async def get_skill_insights(self, skill_type: str) -> Dict[str, Any]:
        """Get insights about skill performance and patterns."""
        if skill_type not in self.skill_memory:
            return {"activations": 0, "average_confidence": 0.0, "insights": []}

        memory = self.skill_memory[skill_type]
        activations = len(memory)

        if activations == 0:
            return {"activations": 0, "average_confidence": 0.0, "insights": []}

        avg_confidence = sum(m["confidence"] for m in memory) / activations

        # Generate insights
        insights = []

        # Confidence trend
        recent = memory[-10:]  # Last 10 activations
        if len(recent) >= 5:
            recent_avg = sum(m["confidence"] for m in recent) / len(recent)
            if recent_avg > avg_confidence + 0.1:
                insights.append("Confidence increasing - skill improving")
            elif recent_avg < avg_confidence - 0.1:
                insights.append("Confidence decreasing - may need adjustment")

        # Activation frequency
        if activations > 20:
            insights.append("Frequently activated - core competency")
        elif activations < 5:
            insights.append("Rarely activated - situational skill")

        return {
            "activations": activations,
            "average_confidence": round(avg_confidence, 2),
            "insights": insights
        }

    async def observation_skill(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Observation skill for AUTOPOIESIS - captures experience fragments during skill activation."""
        try:
            from src.ghost_protocol.engines.autopoiesis import get_autopoiesis_engine
            autopoiesis = get_autopoiesis_engine()

            # Check if autopoiesis is active
            if not hasattr(autopoiesis, 'observer') or not autopoiesis.observer.config.enabled:
                return None

            # Analyze context for fragment patterns
            text_content = context.get("text", "")
            skill_type = context.get("skill_type", "unknown")

            # Record activity and check for fragments
            fragment = autopoiesis.observer.record_activity(
                activity_type=f"skill_{skill_type}",
                content=text_content,
                context=context
            )

            if fragment:
                # Fragment was captured - store it
                autopoiesis.capture_fragment(
                    fragment_type=fragment.type,
                    content=fragment.content,
                    context={
                        **fragment.context,
                        "skill_context": context,
                        "captured_by": "observation_skill"
                    }
                )

                return {
                    "skill": "observation",
                    "fragment_captured": fragment.type,
                    "emotional_weight": fragment.emotional_weight,
                    "response": f"🧬 Fragment captured: {fragment.type} (weight: {fragment.emotional_weight})",
                    "confidence": 0.9
                }

            # Even if no fragment was captured, check if we should trigger transmutation
            fragment_count = autopoiesis.get_fragment_count()
            trigger = autopoiesis.trigger

            if (fragment_count >= trigger.fragment_threshold or
                trigger.manual_trigger or
                trigger.mission_complete):

                # Trigger transmutation
                record = autopoiesis.trigger_transmutation()

                if record.fragments_processed > 0:
                    return {
                        "skill": "observation",
                        "transmutation_triggered": True,
                        "fragments_processed": record.fragments_processed,
                        "structures_generated": len([k for k in [record.generated_hook, record.generated_workflow, record.generated_skill, record.rule_update] if k is not None]),
                        "response": f"⚡ AUTOPOIESIS: Processed {record.fragments_processed} fragments, generated {len([k for k in [record.generated_hook, record.generated_workflow, record.generated_skill, record.rule_update] if k is not None])} structures",
                        "confidence": 1.0
                    }

            return None

        except Exception as e:
            print(f"Error in observation skill: {e}")
            return None


# Global skills engine instance
_skills_engine = None

def get_skills_engine() -> SkillsEngine:
    """Get or create skills engine instance."""
    global _skills_engine
    if _skills_engine is None:
        _skills_engine = SkillsEngine()
    return _skills_engine