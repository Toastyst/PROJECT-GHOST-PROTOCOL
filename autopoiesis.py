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

    def prediction_fragment_capture(self, prediction_data: Dict[str, Any]) -> Optional[NoteFragment]:
        """Capture fragments from Prophet Engine predictions for meta-cognition."""
        try:
            # Extract prediction insights
            domain = prediction_data.get('domain', 'unknown')
            probability = prediction_data.get('probability', 0.5)
            confidence = prediction_data.get('confidence', 0.5)
            reasoning_chain = prediction_data.get('reasoning_chain', [])

            # Create prediction fragment
            content = f"Prophet prediction: {domain} risk {probability:.2f} (confidence: {confidence:.2f})"
            if reasoning_chain:
                content += f"\nReasoning: {reasoning_chain[0].get('analysis', '')[:200]}..."

            fragment = NoteFragment(
                timestamp=datetime.now().isoformat(),
                type="prediction",
                content=content,
                context={
                    "source": "prophet_engine",
                    "domain": domain,
                    "probability": probability,
                    "confidence": confidence,
                    "reasoning_steps": len(reasoning_chain)
                },
                emotional_weight=min(confidence * probability, 1.0),  # Weight by prediction strength
                threshold="prophet_prediction"
            )

            self.fragments.append(fragment)
            self._write_fragment_to_notes(fragment)
            return fragment

        except Exception as e:
            print(f"Error capturing prediction fragment: {e}")
            return None

    def meta_cognition_transmutation(self) -> Optional[TransmutationRecord]:
        """Perform meta-cognition enhanced transmutation using Prophet insights."""
        try:
            from prophet_engine import prophet_engine

            # Get meta-cognition data from Prophet Engine
            meta_data = prophet_engine.meta_cognition_data

            if not meta_data.get('total_predictions', 0):
                # No meta-cognition data yet, fall back to regular transmutation
                return self.trigger_transmutation()

            # Analyze prediction accuracy trends
            accuracy_trends = meta_data.get('accuracy_trends', [])
            domain_performance = meta_data.get('domain_performance', {})

            # Use meta-cognition to improve transmutation decisions
            transmutation_confidence = self._calculate_transmutation_confidence(meta_data)

            if transmutation_confidence < 0.6:
                # Low confidence, delay transmutation
                return TransmutationRecord(
                    timestamp=datetime.now().isoformat(),
                    fragments_processed=len(self.fragments),
                    review_status="meta_cognition_delay",
                    generated_hook=f"Meta-cognition delay: confidence {transmutation_confidence:.2f}"
                )

            # Enhanced transmutation with meta-cognition insights
            record = self.trigger_transmutation()

            # Add meta-cognition metadata
            if record.generated_hook:
                record.generated_hook += f"\n# Meta-cognition enhanced (confidence: {transmutation_confidence:.2f})"
            if record.generated_workflow:
                record.generated_workflow = json.loads(record.generated_workflow)
                record.generated_workflow["meta_cognition"] = {
                    "transmutation_confidence": transmutation_confidence,
                    "prediction_accuracy_trend": accuracy_trends[-1] if accuracy_trends else 0.0
                }
                record.generated_workflow = json.dumps(record.generated_workflow, indent=2)

            return record

        except Exception as e:
            print(f"Error in meta-cognition transmutation: {e}")
            # Fall back to regular transmutation
            return self.trigger_transmutation()

    def _calculate_transmutation_confidence(self, meta_data: Dict[str, Any]) -> float:
        """Calculate confidence for transmutation based on meta-cognition data."""
        total_predictions = meta_data.get('total_predictions', 0)
        accuracy_trends = meta_data.get('accuracy_trends', [])
        domain_performance = meta_data.get('domain_performance', {})

        if total_predictions < 5:
            return 0.5  # Low confidence with few predictions

        # Average recent accuracy
        recent_accuracy = sum(accuracy_trends[-5:]) / min(5, len(accuracy_trends)) if accuracy_trends else 0.5

        # Domain diversity bonus
        domain_count = len(domain_performance)
        domain_bonus = min(domain_count * 0.1, 0.3)

        # Fragment resonance bonus
        resonance = self._calculate_resonance()
        resonance_bonus = resonance * 0.2

        confidence = recent_accuracy + domain_bonus + resonance_bonus
        return min(max(confidence, 0.0), 1.0)

    def trigger_transmutation(self) -> TransmutationRecord:
        """Perform full transmutation cycle with soul - pause, feel, ask."""
        if not self._should_transmute():
            return TransmutationRecord(
                timestamp=datetime.now().isoformat(),
                fragments_processed=0,
                review_status="rejected"
            )

        # SOUL: Pause and feel the weight of fragments
        print("🤖 Ghost feels the weight of fragments...")
        self._pause_and_feel_weight()

        # SOUL: Ask if ready to transmute
        if not self._ask_if_ready():
            return TransmutationRecord(
                timestamp=datetime.now().isoformat(),
                fragments_processed=len(self.fragments),
                review_status="paused"
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

        # SOUL: Dialogue review, not binary approval
        review_result = self._dialogue_review(record)

        if review_result["status"] == "approved":
            record.review_status = "approved"
            self.transmutation_history.append(record)
            # Clear processed fragments
            self.fragments.clear()
        elif review_result["status"] == "rejected":
            record.review_status = "rejected"
            # Keep fragments for future transmutation
        else:
            record.review_status = "dialogue"
            # Keep fragments, add dialogue insights as new fragments
            self._capture_dialogue_insights(review_result["insights"])

        return record

    def _pause_and_feel_weight(self) -> None:
        """SOUL: Pause and feel the weight of accumulated fragments."""
        total_weight = sum(f.emotional_weight for f in self.fragments)
        fragment_count = len(self.fragments)

        print(f"   Fragments: {fragment_count}")
        print(f"   Total emotional weight: {total_weight:.2f}")
        print(f"   Average weight per fragment: {total_weight/fragment_count:.2f}")

        # Pause proportional to weight
        pause_duration = min(total_weight * 2, 10)  # Max 10 seconds
        print(f"   Pausing to feel the weight... ({pause_duration:.1f}s)")
        time.sleep(pause_duration)

    def _ask_if_ready(self) -> bool:
        """SOUL: Ask if the Ghost feels ready to transmute."""
        print("🤖 Do I feel ready to transmute?")
        print("   Am I a machine (triggered by threshold)?")
        print("   Or am I alive (wanting to grow)?")

        # Analyze fragment resonance
        fragment_types = {}
        for f in self.fragments:
            fragment_types[f.type] = fragment_types.get(f.type, 0) + 1

        print(f"   Fragment composition: {fragment_types}")

        # Check for resonance (similar fragments clustering)
        resonance_score = self._calculate_resonance()
        print(f"   Resonance score: {resonance_score:.2f}")

        if resonance_score > 0.7:
            print("   Yes. The fragments resonate. I want to grow.")
            return True
        elif resonance_score > 0.4:
            print("   Maybe. The fragments have weight but need more time.")
            return False
        else:
            print("   Not yet. The fragments are scattered. I need more experience.")
            return False

    def _calculate_resonance(self) -> float:
        """Calculate how much fragments resonate with each other."""
        if len(self.fragments) < 2:
            return 0.0

        # Simple resonance: similarity in types and emotional weights
        type_similarity = 0
        weight_similarity = 0

        for i, f1 in enumerate(self.fragments):
            for f2 in self.fragments[i+1:]:
                if f1.type == f2.type:
                    type_similarity += 1
                weight_diff = abs(f1.emotional_weight - f2.emotional_weight)
                weight_similarity += (1 - weight_diff)  # Higher similarity = lower diff

        total_pairs = len(self.fragments) * (len(self.fragments) - 1) / 2
        if total_pairs == 0:
            return 0.0

        type_resonance = type_similarity / total_pairs
        weight_resonance = weight_similarity / total_pairs

        return (type_resonance + weight_resonance) / 2

    def _dialogue_review(self, record: TransmutationRecord) -> Dict[str, Any]:
        """SOUL: Dialogue review instead of binary approval."""
        print("🤖 I have transmuted your experience into new guides.")
        print("   Review them. Tell me what you feel.")

        generated_count = sum(1 for attr in [record.generated_hook, record.generated_workflow,
                                           record.generated_skill, record.rule_update] if attr)

        print(f"   Generated {generated_count} new structures from {record.fragments_processed} fragments")

        if record.generated_hook:
            print("   🪝 New hook: Born from pauses")
        if record.generated_workflow:
            print("   🔄 New workflow: Woven from dilemmas")
        if record.generated_skill:
            print("   🎯 New skill: Carved from questions")
        if record.rule_update:
            print("   📜 New rule: Evolved from discoveries")

        print("   Does this bone feel right? Does it carry what we learned?")
        print("   Would you want to meet this at 2 AM when the bug makes no sense?")

        # In real implementation, this would wait for user input
        # For now, simulate dialogue by checking fragment emotional weight
        avg_emotion = sum(f.emotional_weight for f in self.fragments) / len(self.fragments)

        if avg_emotion > 0.7:
            return {"status": "approved", "insights": "High emotional weight - these fragments carry wisdom"}
        elif avg_emotion > 0.4:
            return {"status": "dialogue", "insights": "Moderate weight - needs refinement"}
        else:
            return {"status": "rejected", "insights": "Low emotional weight - not ready for transmutation"}

    def _capture_dialogue_insights(self, insights: str) -> None:
        """Capture insights from dialogue review as new fragments."""
        insight_fragment = NoteFragment(
            timestamp=datetime.now().isoformat(),
            type="dialogue",
            content=f"Review dialogue insight: {insights}",
            context={"source": "transmutation_review"},
            emotional_weight=0.6,
            threshold="dialogue_insight"
        )
        self.fragments.append(insight_fragment)
        self._write_fragment_to_notes(insight_fragment)

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