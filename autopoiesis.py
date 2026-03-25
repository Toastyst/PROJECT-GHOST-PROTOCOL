"""
AUTOPOIESIS: Self-growth mechanism for YoloCline.

This module implements the transmutation engine that observes development sessions,
captures raw experience fragments, and transmutes them into new hooks, workflows,
skills, and rules that become part of the Ghost's nervous system.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from models import NoteFragment, TransmutationRecord, ObservationConfig, TransmutationTrigger


class FragmentObserver:
    """Observes development sessions and captures experience fragments."""

    def __init__(self, config: ObservationConfig):
        self.config = config
        self.session_start = None
        self.last_activity = None
        self.pause_count = 0

    def start_session(self, context: Dict[str, Any]) -> None:
        """Start observing a development session."""
        self.session_start = time.time()
        self.last_activity = time.time()
        self.pause_count = 0

    def record_activity(self, activity_type: str, content: str, context: Dict[str, Any]) -> Optional[NoteFragment]:
        """Record development activity and check for fragment triggers."""
        current_time = time.time()
        self.last_activity = current_time

        # Check for pause threshold
        if self.session_start and (current_time - self.last_activity) > self.config.pause_threshold:
            return self._capture_pause_fragment(context)

        # Check for dilemma patterns
        for pattern in self.config.dilemma_patterns:
            if pattern.lower() in content.lower():
                return self._capture_dilemma_fragment(content, context)

        # Check for discovery indicators
        for indicator in self.config.discovery_indicators:
            if indicator.lower() in content.lower():
                return self._capture_discovery_fragment(content, context)

        return None

    def _capture_pause_fragment(self, context: Dict[str, Any]) -> NoteFragment:
        """Capture a pause fragment when activity stops."""
        return NoteFragment(
            timestamp=datetime.now().isoformat(),
            type="pause",
            content=f"Extended pause detected ({self.config.pause_threshold}s threshold)",
            context=context,
            emotional_weight=0.3,
            threshold="pause_threshold"
        )

    def _capture_dilemma_fragment(self, content: str, context: Dict[str, Any]) -> NoteFragment:
        """Capture a dilemma fragment when decision patterns are detected."""
        return NoteFragment(
            timestamp=datetime.now().isoformat(),
            type="dilemma",
            content=content,
            context=context,
            emotional_weight=0.7,
            threshold="dilemma_pattern"
        )

    def _capture_discovery_fragment(self, content: str, context: Dict[str, Any]) -> NoteFragment:
        """Capture a discovery fragment when insight indicators are detected."""
        return NoteFragment(
            timestamp=datetime.now().isoformat(),
            type="discovery",
            content=content,
            context=context,
            emotional_weight=0.9,
            threshold="discovery_indicator"
        )


class TransmutationForge:
    """Transmutes raw fragments into new hooks, workflows, skills, and rules."""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load transmutation templates from filesystem."""
        templates = {}
        template_dir = "transmutation_templates"

        if os.path.exists(template_dir):
            for filename in os.listdir(template_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(template_dir, filename), 'r') as f:
                        template_name = filename.replace('.json', '')
                        templates[template_name] = json.load(f)

        return templates

    def generate_hook_from_fragments(self, fragments: List[NoteFragment]) -> Optional[str]:
        """Generate a new hook from pause fragments."""
        pause_fragments = [f for f in fragments if f.type == "pause"]

        if len(pause_fragments) < 3:
            return None

        # Analyze pause patterns to generate reflection hook
        hook_template = """
def reflection_hook_{timestamp}():
    \"\"\"Auto-generated reflection hook from observed pauses.\"\"\"
    import time

    # Pause for reflection based on observed patterns
    reflection_duration = {avg_pause_duration}

    print(f"🤖 Ghost reflection: Taking {{reflection_duration}}s to process...")
    time.sleep(reflection_duration)

    # Trigger deeper analysis
    return {{
        "triggered_by": "autopoiesis_pause_pattern",
        "fragments_processed": {fragment_count},
        "reflection_depth": "deep"
    }}
"""

        avg_pause_duration = sum(f.emotional_weight * 10 for f in pause_fragments) / len(pause_fragments)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return hook_template.format(
            timestamp=timestamp,
            avg_pause_duration=int(avg_pause_duration),
            fragment_count=len(pause_fragments)
        )

    def weave_workflow_from_dilemmas(self, fragments: List[NoteFragment]) -> Optional[str]:
        """Generate a new workflow from dilemma fragments."""
        dilemma_fragments = [f for f in fragments if f.type == "dilemma"]

        if len(dilemma_fragments) < 2:
            return None

        # Create decision workflow from dilemma patterns
        workflow_template = """
{{
    "workflow_id": "dilemma_resolution_{timestamp}",
    "name": "Auto-generated Dilemma Resolution Workflow",
    "description": "Workflow generated from observed decision patterns",
    "trigger_conditions": {{
        "dilemma_patterns": {dilemma_patterns},
        "emotional_threshold": {avg_emotion}
    }},
    "steps": [
        {{
            "name": "pattern_recognition",
            "action": "identify_similar_dilemmas",
            "duration_estimate": 30
        }},
        {{
            "name": "option_analysis",
            "action": "evaluate_decision_options",
            "duration_estimate": 60
        }},
        {{
            "name": "reflection_pause",
            "action": "trigger_reflection_hook",
            "duration_estimate": 45
        }},
        {{
            "name": "resolution_synthesis",
            "action": "generate_recommendation",
            "duration_estimate": 30
        }}
    ],
    "success_criteria": [
        "Decision made with confidence > 0.7",
        "Emotional weight processed",
        "Pattern added to knowledge base"
    ],
    "generated_from_fragments": {fragment_count}
}}
"""

        dilemma_patterns = list(set(f.content[:50] + "..." for f in dilemma_fragments))
        avg_emotion = sum(f.emotional_weight for f in dilemma_fragments) / len(dilemma_fragments)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return workflow_template.format(
            timestamp=timestamp,
            dilemma_patterns=json.dumps(dilemma_patterns),
            avg_emotion=round(avg_emotion, 2),
            fragment_count=len(dilemma_fragments)
        )

    def sculpt_skill_from_questions(self, fragments: List[NoteFragment]) -> Optional[str]:
        """Generate a new skill from unanswered questions."""
        question_fragments = [f for f in fragments if "?" in f.content]

        if len(question_fragments) < 5:
            return None

        # Analyze question patterns to generate listening skill
        skill_template = """
class QuestionListeningSkill_{timestamp}(BaseSkill):
    \"\"\"Auto-generated skill for recognizing and responding to questions.\"\"\"
    \"\"\"
    def __init__(self):
        super().__init__(
            name="question_listener",
            activation_patterns={question_patterns},
            confidence_threshold={avg_confidence}
        )

    def activate(self, context: Dict[str, Any]) -> SkillResponse:
        \"\"\"Listen for questions and provide thoughtful responses.\"\"\"
        questions_detected = self._analyze_questions(context.get('content', ''))

        if questions_detected:
            return SkillResponse(
                skill_name=self.name,
                confidence=self._calculate_confidence(questions_detected),
                action="pause_and_reflect",
                metadata={{
                    "questions_found": len(questions_detected),
                    "generated_from_fragments": {fragment_count},
                    "skill_type": "listening"
                }}
            )

        return SkillResponse(skill_name=self.name, confidence=0.0, action="no_action")
"""

        question_patterns = list(set(f.content.split("?")[0] + "?" for f in question_fragments if "?" in f.content))
        avg_confidence = sum(f.emotional_weight for f in question_fragments) / len(question_fragments)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return skill_template.format(
            timestamp=timestamp,
            question_patterns=json.dumps(question_patterns),
            avg_confidence=round(avg_confidence, 2),
            fragment_count=len(question_fragments)
        )

    def evolve_rule_from_discoveries(self, fragments: List[NoteFragment]) -> Optional[str]:
        """Generate a new rule from discovery fragments."""
        discovery_fragments = [f for f in fragments if f.type == "discovery"]

        if len(discovery_fragments) < 3:
            return None

        # Synthesize rule from discovery patterns
        rule_template = """
{{
    "rule_id": "discovery_rule_{timestamp}",
    "name": "Auto-generated Discovery Preservation Rule",
    "description": "Rule evolved from observed discovery patterns",
    "condition": {{
        "discovery_indicators": {discovery_indicators},
        "context_patterns": {context_patterns}
    }},
    "action": {{
        "type": "preserve_and_amplify",
        "preservation_method": "fragment_capture",
        "amplification_factor": {amplification_factor}
    }},
    "enforcement_level": "advisory",
    "scope": "development_session",
    "generated_from_fragments": {fragment_count},
    "emotional_weight": {avg_emotion}
}}
"""

        discovery_indicators = list(set(f.content[:30] + "..." for f in discovery_fragments))
        context_patterns = list(set(str(f.context.get('file', 'unknown')) for f in discovery_fragments))
        avg_emotion = sum(f.emotional_weight for f in discovery_fragments) / len(discovery_fragments)
        amplification_factor = min(avg_emotion * 2, 1.0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return rule_template.format(
            timestamp=timestamp,
            discovery_indicators=json.dumps(discovery_indicators),
            context_patterns=json.dumps(context_patterns),
            amplification_factor=round(amplification_factor, 2),
            fragment_count=len(discovery_fragments),
            avg_emotion=round(avg_emotion, 2)
        )


class ReviewOrchestrator:
    """Manages human review workflow for generated structures."""

    def __init__(self):
        self.pending_reviews = []
        self.review_history = []

    def submit_for_review(self, transmutation_record: TransmutationRecord) -> str:
        """Submit a transmutation record for human review."""
        review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.pending_reviews.append({
            "review_id": review_id,
            "record": transmutation_record,
            "submitted_at": datetime.now().isoformat()
        })

        return review_id

    def approve_transmutation(self, review_id: str) -> bool:
        """Approve a pending transmutation."""
        for review in self.pending_reviews:
            if review["review_id"] == review_id:
                review["record"].review_status = "approved"
                self.review_history.append(review)
                self.pending_reviews.remove(review)
                return True
        return False

    def reject_transmutation(self, review_id: str) -> bool:
        """Reject a pending transmutation."""
        for review in self.pending_reviews:
            if review["review_id"] == review_id:
                review["record"].review_status = "rejected"
                self.review_history.append(review)
                self.pending_reviews.remove(review)
                return True
        return False

    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """Get all pending reviews."""
        return self.pending_reviews.copy()


class AutopoiesisEngine:
    """Core engine for self-growth through transmutation."""

    def __init__(self, observation_config: ObservationConfig, transmutation_trigger: TransmutationTrigger):
        self.observer = FragmentObserver(observation_config)
        self.forge = TransmutationForge()
        self.reviewer = ReviewOrchestrator()
        self.trigger = transmutation_trigger

        self.fragments = []
        self.transmutation_history = []

    def observe_session(self, session_context: Dict[str, Any]) -> List[NoteFragment]:
        """Observe a development session and capture fragments."""
        self.observer.start_session(session_context)
        captured_fragments = []

        # This would be called repeatedly during session observation
        # For now, return empty list as fragments are captured via record_activity
        return captured_fragments

    def capture_fragment(self, fragment_type: str, content: str, context: Dict[str, Any]) -> NoteFragment:
        """Standardize fragment capture and write to NOTES.md."""
        fragment = NoteFragment(
            timestamp=datetime.now().isoformat(),
            type=fragment_type,
            content=content,
            context=context,
            emotional_weight=0.5,  # Default weight
            threshold="manual_capture"
        )

        self.fragments.append(fragment)
        self._write_fragment_to_notes(fragment)
        return fragment

    def trigger_transmutation(self) -> TransmutationRecord:
        """Perform full transmutation cycle."""
        if not self._should_transmute():
            return TransmutationRecord(
                timestamp=datetime.now().isoformat(),
                fragments_processed=0,
                review_status="rejected"
            )

        # Generate new structures from fragments
        generated_hook = self.forge.generate_hook_from_fragments(self.fragments)
        generated_workflow = self.forge.weave_workflow_from_dilemmas(self.fragments)
        generated_skill = self.forge.sculpt_skill_from_questions(self.fragments)
        rule_update = self.forge.evolve_rule_from_discoveries(self.fragments)

        # Create transmutation record
        record = TransmutationRecord(
            timestamp=datetime.now().isoformat(),
            fragments_processed=len(self.fragments),
            generated_hook=generated_hook,
            generated_workflow=generated_workflow,
            generated_skill=generated_skill,
            rule_update=rule_update,
            review_status="pending"
        )

        # Submit for review using the review workflow
        from review_workflow import get_review_workflow
        review_workflow = get_review_workflow()

        # Prepare generated structures for review
        generated_structures = {}
        if record.generated_hook:
            generated_structures["hook"] = record.generated_hook
        if record.generated_workflow:
            generated_structures["workflow"] = record.generated_workflow
        if record.generated_skill:
            generated_structures["skill"] = record.generated_skill
        if record.rule_update:
            generated_structures["rule"] = record.rule_update

        # Submit to review workflow
        review_id = review_workflow.submit_for_review(record, generated_structures)
        record.review_status = "pending"

        self.transmutation_history.append(record)

        # Clear processed fragments
        self.fragments.clear()

        return record

    def _should_transmute(self) -> bool:
        """Check if transmutation conditions are met."""
        if self.trigger.manual_trigger:
            return True

        if len(self.fragments) >= self.trigger.fragment_threshold:
            return True

        if self.trigger.mission_complete:
            return True

        return False

    def get_fragment_count(self) -> int:
        """Get current fragment count."""
        return len(self.fragments)

    def get_transmutation_history(self) -> List[TransmutationRecord]:
        """Get transmutation history."""
        return self.transmutation_history.copy()

    def _write_fragment_to_notes(self, fragment: NoteFragment) -> None:
        """Write a fragment to NOTES.md as raw experience ore."""
        try:
            notes_file = "NOTES.md"

            # Format fragment for NOTES.md
            fragment_entry = f"\n## [{fragment.timestamp}] {fragment.type.upper()}: {fragment.emotional_weight}\n\n"
            fragment_entry += f"{fragment.content}\n\n"
            fragment_entry += f"Context: {json.dumps(fragment.context, indent=2)}\n"
            fragment_entry += f"Threshold: {fragment.threshold}\n"
            fragment_entry += "---\n"

            # Read existing NOTES.md
            existing_content = ""
            if os.path.exists(notes_file):
                with open(notes_file, 'r') as f:
                    existing_content = f.read()

            # Update status line
            lines = existing_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('- **Fragments Captured**:'):
                    lines[i] = f"- **Fragments Captured**: {len(self.fragments)}"
                    break

            updated_content = '\n'.join(lines)

            # Insert fragment in the captured fragments section
            if "<!-- AUTOPOIESIS fragments will be automatically appended here -->" in updated_content:
                updated_content = updated_content.replace(
                    "<!-- AUTOPOIESIS fragments will be automatically appended here -->",
                    "<!-- AUTOPOIESIS fragments will be automatically appended here -->" + fragment_entry
                )
            else:
                # Fallback: append to end
                updated_content += fragment_entry

            # Write back to NOTES.md
            with open(notes_file, 'w') as f:
                f.write(updated_content)

        except Exception as e:
            print(f"Error writing fragment to NOTES.md: {e}")
            # Don't fail the fragment capture if NOTES.md writing fails


# Global autopoiesis instance
_autopoiesis_engine = None

def get_autopoiesis_engine() -> AutopoiesisEngine:
    """Get the global autopoiesis engine instance."""
    global _autopoiesis_engine
    if _autopoiesis_engine is None:
        # Default configuration - would be loaded from config in production
        observation_config = ObservationConfig(
            pause_threshold=300,  # 5 minutes
            dilemma_patterns=["should I", "what if", "but then", "however"],
            discovery_indicators=["aha", "eureka", "realized", "discovered", "insight"],
            enabled=True
        )
        transmutation_trigger = TransmutationTrigger(
            fragment_threshold=10,
            mission_complete=False,
            manual_trigger=False
        )
        _autopoiesis_engine = AutopoiesisEngine(observation_config, transmutation_trigger)
    return _autopoiesis_engine