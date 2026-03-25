"""
Comprehensive tests for AUTOPOIESIS system.

Tests the complete cycle from fragment observation to transmutation,
review workflow, and repository integration.
"""

import asyncio
import json
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.ghost_protocol.models.models import NoteFragment, TransmutationRecord, ObservationConfig, TransmutationTrigger
from src.ghost_protocol.engines.autopoiesis import AutopoiesisEngine, FragmentObserver, TransmutationForge, get_autopoiesis_engine
from src.ghost_protocol.utils.review_workflow import ReviewWorkflow, get_review_workflow
from src.ghost_protocol.engines.skills_engine import get_skills_engine
from src.ghost_protocol.engines.rules_engine import get_rules_engine
from src.ghost_protocol.servers.weaver_server import get_weaver


class TestFragmentObserver:
    """Test fragment observation and capture."""

    def test_observer_initialization(self):
        """Test observer initializes with config."""
        config = ObservationConfig(
            pause_threshold=300,
            dilemma_patterns=["should I", "what if"],
            discovery_indicators=["aha", "realized"],
            enabled=True
        )
        observer = FragmentObserver(config)

        assert observer.config == config
        assert observer.session_start is None
        assert observer.pause_count == 0

    def test_pause_fragment_capture(self):
        """Test pause fragment capture after threshold."""
        config = ObservationConfig(
            pause_threshold=1,  # 1 second for testing
            dilemma_patterns=[],
            discovery_indicators=[],
            enabled=True
        )
        observer = FragmentObserver(config)

        # Start session
        observer.start_session({"test": "context"})

        # Simulate pause by directly setting last_activity to past
        import time
        observer.last_activity = time.time() - 2  # 2 seconds ago

        # Record activity - should capture pause fragment
        fragment = observer.record_activity("test", "test content", {"file": "test.py"})

        assert fragment is not None
        assert fragment.type == "pause"
        assert "pause detected" in fragment.content
        assert fragment.emotional_weight == 0.3

    def test_dilemma_fragment_capture(self):
        """Test dilemma pattern detection."""
        config = ObservationConfig(
            pause_threshold=300,
            dilemma_patterns=["should I", "what if"],
            discovery_indicators=[],
            enabled=True
        )
        observer = FragmentObserver(config)

        observer.start_session({"test": "context"})

        # Test dilemma detection
        fragment = observer.record_activity("message", "should I refactor this code?", {"file": "test.py"})

        assert fragment is not None
        assert fragment.type == "dilemma"
        assert "should I refactor this code?" in fragment.content
        assert fragment.emotional_weight == 0.7

    def test_discovery_fragment_capture(self):
        """Test discovery indicator detection."""
        config = ObservationConfig(
            pause_threshold=300,
            dilemma_patterns=[],
            discovery_indicators=["aha", "realized", "insight"],
            enabled=True
        )
        observer = FragmentObserver(config)

        observer.start_session({"test": "context"})

        # Test discovery detection
        fragment = observer.record_activity("message", "Aha! I realized the issue.", {"file": "test.py"})

        assert fragment is not None
        assert fragment.type == "discovery"
        assert "Aha! I realized the issue." in fragment.content
        assert fragment.emotional_weight == 0.9


class TestTransmutationForge:
    """Test structure generation from fragments."""

    def test_hook_generation_from_pauses(self):
        """Test hook generation from pause fragments."""
        forge = TransmutationForge()

        # Create pause fragments
        fragments = [
            NoteFragment(
                timestamp="2026-03-25T06:00:00",
                type="pause",
                content="Extended pause detected",
                context={"file": "test.py"},
                emotional_weight=0.5,
                threshold="pause_threshold"
            ),
            NoteFragment(
                timestamp="2026-03-25T06:01:00",
                type="pause",
                content="Another pause",
                context={"file": "test.py"},
                emotional_weight=0.6,
                threshold="pause_threshold"
            ),
            NoteFragment(
                timestamp="2026-03-25T06:02:00",
                type="pause",
                content="Third pause",
                context={"file": "test.py"},
                emotional_weight=0.4,
                threshold="pause_threshold"
            )
        ]

        hook = forge.generate_hook_from_fragments(fragments)

        assert hook is not None
        assert "reflection_hook_" in hook
        assert "import time" in hook
        assert "time.sleep" in hook
        assert "fragments_processed\": 3" in hook

    def test_workflow_generation_from_dilemmas(self):
        """Test workflow generation from dilemma fragments."""
        forge = TransmutationForge()

        fragments = [
            NoteFragment(
                timestamp="2026-03-25T06:00:00",
                type="dilemma",
                content="Should I use async or sync?",
                context={"file": "test.py"},
                emotional_weight=0.8,
                threshold="dilemma_pattern"
            ),
            NoteFragment(
                timestamp="2026-03-25T06:01:00",
                type="dilemma",
                content="What if I refactor this differently?",
                context={"file": "test.py"},
                emotional_weight=0.7,
                threshold="dilemma_pattern"
            )
        ]

        workflow = forge.weave_workflow_from_dilemmas(fragments)

        assert workflow is not None
        assert "dilemma_resolution_" in workflow
        assert "pattern_recognition" in workflow
        assert "option_analysis" in workflow
        assert "generated_from_fragments\": 2" in workflow

    def test_skill_generation_from_questions(self):
        """Test skill generation from question fragments."""
        forge = TransmutationForge()

        fragments = [
            NoteFragment(
                timestamp="2026-03-25T06:00:00",
                type="dilemma",
                content="How does this work?",
                context={"file": "test.py"},
                emotional_weight=0.6,
                threshold="question_pattern"
            ),
            NoteFragment(
                timestamp="2026-03-25T06:01:00",
                type="dilemma",
                content="What is the best approach?",
                context={"file": "test.py"},
                emotional_weight=0.7,
                threshold="question_pattern"
            ),
            NoteFragment(
                timestamp="2026-03-25T06:02:00",
                type="dilemma",
                content="Why does this happen?",
                context={"file": "test.py"},
                emotional_weight=0.5,
                threshold="question_pattern"
            ),
            NoteFragment(
                timestamp="2026-03-25T06:03:00",
                type="dilemma",
                content="When should I use this?",
                context={"file": "test.py"},
                emotional_weight=0.8,
                threshold="question_pattern"
            ),
            NoteFragment(
                timestamp="2026-03-25T06:04:00",
                type="dilemma",
                content="Where is the documentation?",
                context={"file": "test.py"},
                emotional_weight=0.6,
                threshold="question_pattern"
            )
        ]

        skill = forge.sculpt_skill_from_questions(fragments)

        assert skill is not None
        assert "QuestionListeningSkill_" in skill
        assert "activation_patterns" in skill
        assert "question_count = 5" in skill

    def test_rule_generation_from_discoveries(self):
        """Test rule generation from discovery fragments."""
        forge = TransmutationForge()

        fragments = [
            NoteFragment(
                timestamp="2026-03-25T06:00:00",
                type="discovery",
                content="Aha! This pattern always works for async code",
                context={"file": "async_utils.py"},
                emotional_weight=0.9,
                threshold="discovery_indicator"
            ),
            NoteFragment(
                timestamp="2026-03-25T06:01:00",
                type="discovery",
                content="Realized that error handling should be consistent",
                context={"file": "error_handler.py"},
                emotional_weight=0.8,
                threshold="discovery_indicator"
            ),
            NoteFragment(
                timestamp="2026-03-25T06:02:00",
                type="discovery",
                content="Insight: Tests should mirror production structure",
                context={"file": "test_structure.py"},
                emotional_weight=0.7,
                threshold="discovery_indicator"
            )
        ]

        rule = forge.evolve_rule_from_discoveries(fragments)

        assert rule is not None
        assert "discovery_rule_" in rule
        assert "generated_from_fragments\": 3" in rule
        assert "amplification_factor" in rule


class TestAutopoiesisEngine:
    """Test the complete autopoiesis engine."""

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        config = ObservationConfig(
            pause_threshold=300,
            dilemma_patterns=["test"],
            discovery_indicators=["test"],
            enabled=True
        )
        trigger = TransmutationTrigger(
            fragment_threshold=5,
            mission_complete=False,
            manual_trigger=False
        )

        engine = AutopoiesisEngine(config, trigger)

        assert engine.observer.config == config
        assert engine.trigger == trigger
        assert len(engine.fragments) == 0
        assert len(engine.transmutation_history) == 0

    def test_fragment_capture(self):
        """Test fragment capture and storage."""
        config = ObservationConfig(
            pause_threshold=300,
            dilemma_patterns=["should I"],
            discovery_indicators=[],
            enabled=True
        )
        trigger = TransmutationTrigger(
            fragment_threshold=10,
            mission_complete=False,
            manual_trigger=False
        )

        engine = AutopoiesisEngine(config, trigger)

        # Capture a fragment
        fragment = engine.capture_fragment(
            "test_fragment",
            "Test content",
            {"file": "test.py"}
        )

        assert fragment.type == "test_fragment"
        assert fragment.content == "Test content"
        assert len(engine.fragments) == 1

    def test_transmutation_trigger_logic(self):
        """Test when transmutation should trigger."""
        config = ObservationConfig(
            pause_threshold=300,
            dilemma_patterns=[],
            discovery_indicators=[],
            enabled=True
        )

        # Test manual trigger
        trigger = TransmutationTrigger(
            fragment_threshold=10,
            mission_complete=False,
            manual_trigger=True
        )
        engine = AutopoiesisEngine(config, trigger)

        assert engine._should_transmute() == True

        # Test fragment threshold
        trigger = TransmutationTrigger(
            fragment_threshold=2,
            mission_complete=False,
            manual_trigger=False
        )
        engine = AutopoiesisEngine(config, trigger)

        # Add fragments to meet threshold
        engine.capture_fragment("test", "content1", {})
        engine.capture_fragment("test", "content2", {})

        assert engine._should_transmute() == True

        # Test mission complete
        trigger = TransmutationTrigger(
            fragment_threshold=10,
            mission_complete=True,
            manual_trigger=False
        )
        engine = AutopoiesisEngine(config, trigger)

        assert engine._should_transmute() == True

    @patch('autopoiesis.get_review_workflow')
    def test_transmutation_cycle(self, mock_get_review_workflow):
        """Test complete transmutation cycle."""
        # Mock review workflow
        mock_workflow = Mock()
        mock_review_id = "test_review_123"
        mock_workflow.submit_for_review.return_value = mock_review_id
        mock_get_review_workflow.return_value = mock_workflow

        config = ObservationConfig(
            pause_threshold=300,
            dilemma_patterns=["should I"],
            discovery_indicators=["aha"],
            enabled=True
        )
        trigger = TransmutationTrigger(
            fragment_threshold=1,  # Low threshold for testing
            mission_complete=False,
            manual_trigger=True
        )

        engine = AutopoiesisEngine(config, trigger)

        # Add some test fragments
        engine.capture_fragment("dilemma", "should I use this approach?", {"file": "test.py"})
        engine.capture_fragment("discovery", "Aha! This is the solution", {"file": "test.py"})

        # Trigger transmutation
        record = engine.trigger_transmutation()

        assert record is not None
        assert record.fragments_processed == 2
        assert record.review_status == "pending"

        # Verify review workflow was called
        mock_workflow.submit_for_review.assert_called_once()
        call_args = mock_workflow.submit_for_review.call_args
        assert call_args[0][0] == record  # First arg is the record
        assert isinstance(call_args[0][1], dict)  # Second arg is generated structures

        # Verify fragments were cleared
        assert len(engine.fragments) == 0

        # Verify record was added to history
        assert len(engine.transmutation_history) == 1


class TestReviewWorkflow:
    """Test the review workflow system."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.workflow = ReviewWorkflow(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_submit_for_review(self):
        """Test submitting transmutation for review."""
        record = TransmutationRecord(
            timestamp="2026-03-25T06:00:00",
            fragments_processed=5,
            generated_hook="test hook code",
            generated_workflow="test workflow json",
            review_status="pending"
        )

        generated_structures = {
            "hook": "test hook code",
            "workflow": "test workflow json"
        }

        review_id = self.workflow.submit_for_review(record, generated_structures)

        assert review_id.startswith("review_")
        assert len(review_id) > 10  # Should be reasonably long

        # Check that review was saved
        pending_reviews = self.workflow.get_pending_reviews()
        assert len(pending_reviews) == 1
        assert pending_reviews[0]["review_id"] == review_id

        # Check that files were created
        review_dir = os.path.join(self.temp_dir, ".autopoiesis", "approved", "pending", review_id)
        assert os.path.exists(review_dir)
        assert os.path.exists(os.path.join(review_dir, "generated_hook_test_review_123.py"))
        assert os.path.exists(os.path.join(review_dir, "generated_workflow_test_review_123.json"))

    def test_approve_review(self):
        """Test approving a review."""
        # First submit a review
        record = TransmutationRecord(
            timestamp="2026-03-25T06:00:00",
            fragments_processed=3,
            generated_hook="hook code",
            review_status="pending"
        )

        generated_structures = {"hook": "hook code"}
        review_id = self.workflow.submit_for_review(record, generated_structures)

        # Approve the review
        success = self.workflow.approve_review(review_id, "test_user", "Looks good")

        assert success == True

        # Check that review moved from pending to approved
        pending_reviews = self.workflow.get_pending_reviews()
        assert len(pending_reviews) == 0

        # Check review details
        review_details = self.workflow.get_review_details(review_id)
        assert review_details["status"] == "approved"
        assert review_details["reviewer"] == "test_user"
        assert review_details["review_notes"] == "Looks good"

    def test_reject_review(self):
        """Test rejecting a review."""
        # Submit and reject a review
        record = TransmutationRecord(
            timestamp="2026-03-25T06:00:00",
            fragments_processed=2,
            generated_skill="skill code",
            review_status="pending"
        )

        generated_structures = {"skill": "skill code"}
        review_id = self.workflow.submit_for_review(record, generated_structures)

        success = self.workflow.reject_review(review_id, "test_user", "Needs improvement")

        assert success == True

        # Check review details
        review_details = self.workflow.get_review_details(review_id)
        assert review_details["status"] == "rejected"
        assert review_details["reviewer"] == "test_user"


class TestIntegration:
    """Test integration between autopoiesis components."""

    @patch('autopoiesis.get_review_workflow')
    @patch('skills_engine.get_skills_engine')
    async def test_observation_skill_integration(self, mock_get_skills, mock_get_review):
        """Test observation skill integration with autopoiesis."""
        # Mock dependencies
        mock_review_workflow = Mock()
        mock_get_review.return_value = mock_review_workflow

        mock_skills_engine = Mock()
        mock_get_skills.return_value = mock_skills_engine

        # Create autopoiesis engine
        config = ObservationConfig(
            pause_threshold=300,
            dilemma_patterns=["should I"],
            discovery_indicators=["aha"],
            enabled=True
        )
        trigger = TransmutationTrigger(
            fragment_threshold=10,
            mission_complete=False,
            manual_trigger=False
        )

        engine = AutopoiesisEngine(config, trigger)

        # Test observation skill activation
        from src.ghost_protocol.engines.skills_engine import SkillsEngine
        skills_engine = SkillsEngine()

        # Simulate skill activation context
        context = {
            "text": "should I refactor this code?",
            "skill_type": "observation",
            "file_path": "test.py"
        }

        result = await skills_engine.observation_skill(context)

        # Should capture a fragment
        assert result is not None
        assert "fragment_captured" in result
        assert result["fragment_captured"] == "dilemma"

    @patch('rules_engine.get_rules_engine')
    async def test_rule_validation_integration(self, mock_get_rules):
        """Test rule validation integration."""
        mock_rules_engine = Mock()
        mock_get_rules.return_value = mock_rules_engine

        # Mock validation response
        mock_validation_result = {
            "overall_compliant": True,
            "structure_validations": {},
            "rule_violations": [],
            "recommendations": [],
            "severity": "none"
        }
        mock_rules_engine.transmutation_rule_validation.return_value = mock_validation_result

        from src.ghost_protocol.engines.rules_engine import RulesEngine
        rules_engine = RulesEngine()

        # Test transmutation validation
        transmutation_record = {
            "timestamp": "2026-03-25T06:00:00",
            "fragments_processed": 5
        }

        generated_structures = {
            "hook": "test hook code",
            "workflow": "test workflow json"
        }

        result = await rules_engine.transmutation_rule_validation(
            transmutation_record,
            generated_structures
        )

        assert result["overall_compliant"] == True
        assert result["severity"] == "none"

        # Verify the mock was called correctly
        mock_rules_engine.transmutation_rule_validation.assert_called_once_with(
            transmutation_record,
            generated_structures
        )


class TestEndToEnd:
    """End-to-end tests for the complete AUTOPOIESIS cycle."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('autopoiesis.get_review_workflow')
    def test_complete_cycle(self, mock_get_review_workflow):
        """Test complete AUTOPOIESIS cycle from observation to commit."""
        # Mock review workflow
        mock_workflow = Mock()
        mock_review_id = "test_review_complete"
        mock_workflow.submit_for_review.return_value = mock_review_id
        mock_workflow.approve_review.return_value = True
        mock_workflow.commit_approved_structures.return_value = True
        mock_get_review_workflow.return_value = mock_workflow

        # Create autopoiesis engine
        config = ObservationConfig(
            pause_threshold=300,
            dilemma_patterns=["should I", "what if"],
            discovery_indicators=["aha", "realized"],
            enabled=True
        )
        trigger = TransmutationTrigger(
            fragment_threshold=3,
            mission_complete=False,
            manual_trigger=True
        )

        engine = AutopoiesisEngine(config, trigger)

        # Phase 1: Capture fragments through observation
        engine.capture_fragment("dilemma", "should I use async here?", {"file": "test.py"})
        engine.capture_fragment("discovery", "Aha! This pattern works perfectly", {"file": "test.py"})
        engine.capture_fragment("pause", "Extended pause detected", {"file": "test.py"})

        assert len(engine.fragments) == 3

        # Phase 2: Trigger transmutation
        record = engine.trigger_transmutation()

        assert record is not None
        assert record.fragments_processed == 3
        assert record.review_status == "pending"

        # Verify review workflow was called
        mock_workflow.submit_for_review.assert_called_once()

        # Phase 3: Simulate review approval
        # (In real scenario, this would be done through CLI commands)
        approved = mock_workflow.approve_review(mock_review_id, "test_user")
        assert approved == True

        # Phase 4: Simulate commit
        committed = mock_workflow.commit_approved_structures(mock_review_id)
        assert committed == True

        # Verify fragments were cleared and history updated
        assert len(engine.fragments) == 0
        assert len(engine.transmutation_history) == 1

        print("✅ Complete AUTOPOIESIS cycle test passed!")


if __name__ == "__main__":
    # Run basic tests
    print("Running AUTOPOIESIS tests...")

    # Test fragment observer
    observer = FragmentObserver(ObservationConfig(
        pause_threshold=1,
        dilemma_patterns=["should I"],
        discovery_indicators=["aha"],
        enabled=True
    ))

    observer.start_session({})
    fragment = observer.record_activity("test", "should I continue?", {})
    assert fragment is not None and fragment.type == "dilemma"
    print("✅ FragmentObserver test passed")

    # Test forge
    forge = TransmutationForge()
    fragments = [
        NoteFragment(
            timestamp="2026-03-25T06:00:00",
            type="pause",
            content="Extended pause detected",
            context={"file": "test.py"},
            emotional_weight=0.5,
            threshold="pause_threshold"
        ),
        NoteFragment(
            timestamp="2026-03-25T06:01:00",
            type="pause",
            content="Another pause",
            context={"file": "test.py"},
            emotional_weight=0.6,
            threshold="pause_threshold"
        ),
        NoteFragment(
            timestamp="2026-03-25T06:02:00",
            type="pause",
            content="Third pause",
            context={"file": "test.py"},
            emotional_weight=0.4,
            threshold="pause_threshold"
        )
    ]
    hook = forge.generate_hook_from_fragments(fragments)
    assert hook is not None and "reflection_hook_" in hook
    print("✅ TransmutationForge test passed")

    # Test engine
    config = ObservationConfig(
        pause_threshold=300,
        dilemma_patterns=["test"],
        discovery_indicators=[],
        enabled=True
    )
    trigger = TransmutationTrigger(
        fragment_threshold=5,
        mission_complete=False,
        manual_trigger=True
    )
    engine = AutopoiesisEngine(config, trigger)

    engine.capture_fragment("test", "content", {})
    assert len(engine.fragments) == 1
    print("✅ AutopoiesisEngine test passed")

    print("🎉 All AUTOPOIESIS tests passed!")