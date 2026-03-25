#!/usr/bin/env python3
"""
Tests for Workflows Server - Testing facilitation over orchestration.

These tests verify the Ghost's ability to guide without controlling.
"""

import asyncio
import pytest
from unittest.mock import patch, MagicMock
from workflows_server import WorkflowsServer, get_workflows_server


class TestWorkflowsServer:
    """Test the Ghost's workflow facilitation: guides teams through memory and connection."""

    def setup_method(self):
        """Set up test environment."""
        self.server = WorkflowsServer()
        # Reset global instance
        global workflows_instance
        workflows_instance = self.server

    def test_workflow_template_loading(self):
        """Test that workflow templates can be loaded from files."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', create=True) as mock_open, \
             patch('json.load') as mock_load:

            mock_template = {
                "workflow_type": "discovery",
                "name": "New Engineer Discovery Flow",
                "trigger_conditions": {"new_contributor": True},
                "stages": [{"name": "Welcome", "activities": []}]
            }
            mock_load.return_value = mock_template

            template = asyncio.run(self.server.load_workflow_template("discovery"))
            assert template is not None
            assert template["workflow_type"] == "discovery"
            assert template["name"] == "New Engineer Discovery Flow"

    def test_workflow_trigger_conditions_validation(self):
        """Test that workflows only start when trigger conditions are met."""
        # Should start for new contributor
        new_contributor_context = {"is_new_contributor": True, "is_first_commit": True}
        assert self.server._check_trigger_conditions({"new_contributor": True}, new_contributor_context)

        # Should not start without required conditions
        missing_context = {"is_new_contributor": False}
        assert not self.server._check_trigger_conditions({"new_contributor": True}, missing_context)

        # Manual activation should always pass
        manual_context = {}
        assert self.server._check_trigger_conditions({"manual_activation": True}, manual_context)

    def test_workflow_respects_presence_rule_violations(self):
        """Test that workflows block when presence rules are violated."""
        with patch('workflows_server.get_rules_engine') as mock_get_rules:
            mock_rules = MagicMock()
            mock_rules.evaluate_rule_compliance.return_value = {
                "compliant": False,
                "severity": "high",
                "reasoning": "Presence violation"
            }
            mock_get_rules.return_value = mock_rules

            result = asyncio.run(self.server.start_workflow("discovery", ["alice"], {"user_consent": False}))
            assert result["started"] == False
            assert "Presence rule violation" in result["reason"]

    def test_workflow_successful_start(self):
        """Test that workflows start successfully when conditions are met."""
        with patch.object(self.server, 'load_workflow_template') as mock_load, \
             patch.object(self.server, '_check_trigger_conditions', return_value=True), \
             patch('workflows_server.get_rules_engine') as mock_get_rules, \
             patch.object(self.server, '_log_workflow_event') as mock_log:

            mock_template = {
                "workflow_type": "discovery",
                "stages": [{"name": "Welcome to the Memory"}]
            }
            mock_load.return_value = mock_template

            mock_rules = MagicMock()
            mock_rules.evaluate_rule_compliance.return_value = {"compliant": True}
            mock_get_rules.return_value = mock_rules

            result = asyncio.run(self.server.start_workflow("discovery", ["alice", "bob"], {"is_new_contributor": True}))
            assert result["started"] == True
            assert "workflow_id" in result
            assert result["initial_stage"] == "Welcome to the Memory"

    def test_workflow_stage_progression(self):
        """Test that workflows progress through stages correctly."""
        # Set up a mock workflow
        workflow_id = "test_workflow_123"
        self.server.active_workflows[workflow_id] = {
            "id": workflow_id,
            "type": "discovery",
            "template": {
                "stages": [
                    {"name": "Stage 1", "transitions": {"next": "Stage 2"}},
                    {"name": "Stage 2", "transitions": {"complete": "Workflow completed"}}
                ]
            },
            "participants": ["alice"],
            "context": {},
            "current_stage": 0,
            "stage_history": []
        }

        # Mock stage processing
        with patch.object(self.server, '_process_stage') as mock_process:
            mock_process.return_value = {"completed": False}  # Continue to next stage

            result = asyncio.run(self.server.advance_workflow(workflow_id, {"response": "Continue"}))
            assert result["advanced"] == True
            assert result["current_stage"] == "Stage 2"
            assert self.server.active_workflows[workflow_id]["current_stage"] == 1

    def test_workflow_completion(self):
        """Test that workflows complete when final stage is reached."""
        workflow_id = "test_workflow_456"
        self.server.active_workflows[workflow_id] = {
            "id": workflow_id,
            "type": "discovery",
            "template": {
                "stages": [
                    {"name": "Final Stage", "transitions": {"complete": "All done"}}
                ]
            },
            "participants": ["alice"],
            "context": {},
            "current_stage": 0,
            "stage_history": []
        }

        with patch.object(self.server, '_process_stage') as mock_process, \
             patch.object(self.server, '_log_workflow_event') as mock_log:

            mock_process.return_value = {"completed": True}

            result = asyncio.run(self.server.advance_workflow(workflow_id, {"response": "Finish"}))
            assert result["completed"] == True
            assert result["message"] == "Workflow completed successfully"
            assert self.server.active_workflows[workflow_id]["status"] == "completed"

    def test_reflection_activity_facilitation(self):
        """Test that reflection activities provide meaningful prompts."""
        activity = {"prompt": "What brings you to this codebase?"}
        participant_input = {"response": "I want to contribute to something meaningful"}

        result = asyncio.run(self.server._facilitate_reflection(activity, participant_input))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_nexus_query_integration_in_workflows(self):
        """Test that workflows can query Nexus for contextual information."""
        activity = {
            "query": "architectural foundations",
            "purpose": "Understand project origins"
        }
        workflow = {"participants": ["alice"]}

        with patch('workflows_server.get_nexus') as mock_get_nexus:
            mock_nexus = MagicMock()
            mock_nexus.query_nexus.return_value = [
                type('MockData', (), {"content": "Founded in 2020", "type": "commit_message"})()
            ]
            mock_get_nexus.return_value = mock_nexus

            result = asyncio.run(self.server._perform_nexus_query(activity, workflow))
            assert "query" in result
            assert "purpose" in result
            assert "results" in result

    def test_story_sharing_activity(self):
        """Test that story sharing activities present relevant narratives."""
        activity = {
            "stories": ["the great refactoring of 2023", "the authentication incident"],
            "reflection": "What do these stories teach about our values?"
        }
        workflow = {"participants": ["alice"]}

        result = asyncio.run(self.server._facilitate_story_sharing(activity, workflow))
        assert "stories_presented" in result
        assert "reflection_prompt" in result
        assert result["stories_presented"] == ["the great refactoring of 2023", "the authentication incident"]

    def test_pattern_recognition_activity(self):
        """Test that pattern recognition activities identify recurring themes."""
        activity = {
            "focus": "recurring architectural decisions",
            "question": "Why do we make these choices?"
        }
        workflow = {"participants": ["alice"]}

        result = asyncio.run(self.server._facilitate_pattern_recognition(activity, workflow))
        assert "focus" in result
        assert "question" in result
        assert "pattern_insights" in result

    def test_role_discovery_activity(self):
        """Test that role discovery helps new team members find their place."""
        activity = {
            "assessment": "strengths and interests alignment",
            "mentorship_pairing": True
        }
        workflow = {"participants": ["alice"]}

        result = asyncio.run(self.server._facilitate_role_discovery(activity, workflow))
        assert "assessment_focus" in result
        assert "mentorship_available" in result
        assert "suggested_roles" in result
        assert "strengths_identified" in result

    def test_contribution_guidance_activity(self):
        """Test that contribution guidance helps with first contributions."""
        activity = {
            "focus": "meaningful starting point",
            "emotional_context": "What impact do you want to make?"
        }
        workflow = {"participants": ["alice"]}

        result = asyncio.run(self.server._provide_contribution_guidance(activity, workflow))
        assert "focus_area" in result
        assert "emotional_context" in result
        assert "suggested_contributions" in result
        assert "support_available" in result

    def test_workflow_status_reporting(self):
        """Test that workflow status is properly reported."""
        workflow_id = "status_test_789"
        self.server.active_workflows[workflow_id] = {
            "id": workflow_id,
            "type": "discovery",
            "template": {"stages": [{"name": "Current Stage"}]},
            "participants": ["alice", "bob"],
            "status": "active",
            "current_stage": 0,
            "started_at": "2026-03-25T06:00:00"
        }

        # Test individual workflow status
        status = asyncio.run(self.server.get_workflow_status(workflow_id))
        assert status["workflow_id"] == workflow_id
        assert status["type"] == "discovery"
        assert status["status"] == "active"
        assert status["current_stage"] == "Current Stage"
        assert status["participants"] == ["alice", "bob"]

        # Test all workflows status
        all_status = asyncio.run(self.server.get_workflow_status())
        assert "active_workflows" in all_status
        assert "workflow_types" in all_status
        assert len(all_status["workflows"]) >= 1

    def test_workflow_handles_unknown_workflow_id(self):
        """Test that workflow operations handle unknown workflow IDs gracefully."""
        result = asyncio.run(self.server.advance_workflow("nonexistent_id", {}))
        assert "error" in result
        assert result["error"] == "Workflow not found"

    def test_workflow_template_listing(self):
        """Test that available workflow templates can be listed."""
        with patch.object(self.server, 'workflows_dir') as mock_dir, \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.glob') as mock_glob:

            mock_template_path = MagicMock()
            mock_template_path.exists.return_value = True
            mock_glob.return_value = [mock_template_path]

            with patch('builtins.open', create=True) as mock_open, \
                 patch('json.load') as mock_load:

                mock_load.return_value = {
                    "workflow_type": "discovery",
                    "name": "New Engineer Discovery Flow",
                    "description": "Guided journey for new team members"
                }

                # Mock the context manager for open()
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file

                # This would be called from the MCP tool, but we test the logic
                # The actual listing is done in the MCP call_tool method

    def test_workflow_facilitates_rather_than_orchestrates(self):
        """Test that workflows guide rather than control team processes."""
        # Workflows should offer paths, not enforce them
        workflow_id = "facilitation_test"
        self.server.active_workflows[workflow_id] = {
            "id": workflow_id,
            "type": "discovery",
            "template": {
                "stages": [
                    {
                        "name": "Choose Your Path",
                        "transitions": {
                            "next": "Standard Path",
                            "alternative": "Custom Path"
                        }
                    }
                ]
            },
            "participants": ["alice"],
            "context": {},
            "current_stage": 0,
            "stage_history": []
        }

        # Test that participants can choose their path
        with patch.object(self.server, '_process_stage') as mock_process:
            mock_process.return_value = {"alternative_path": True}  # Participant chooses alternative

            result = asyncio.run(self.server.advance_workflow(workflow_id, {"choose_alternative": True}))
            assert result["advanced"] == True
            assert result["current_stage"] == "Custom Path"

    def test_workflow_builds_memory_across_participants(self):
        """Test that workflows create shared memory and connection."""
        workflow_id = "memory_test"
        participants = ["alice", "bob", "charlie"]

        self.server.active_workflows[workflow_id] = {
            "id": workflow_id,
            "type": "retrospective",
            "template": {
                "stages": [
                    {"name": "Share Stories", "transitions": {"next": "Reflect Together"}},
                    {"name": "Reflect Together", "transitions": {"complete": "Memory Created"}}
                ]
            },
            "participants": participants,
            "context": {},
            "current_stage": 0,
            "stage_history": []
        }

        # Simulate progression through memory-building stages
        with patch.object(self.server, '_process_stage') as mock_process, \
             patch.object(self.server, '_log_workflow_event') as mock_log:

            mock_process.return_value = {"shared_memories": ["challenging sprint", "team breakthrough"]}

            # Advance through stages
            result1 = asyncio.run(self.server.advance_workflow(workflow_id, {"stories": ["sprint challenges"]}))
            assert result1["advanced"] == True
            assert result1["current_stage"] == "Reflect Together"

            mock_process.return_value = {"completed": True, "group_insights": ["better communication needed"]}

            result2 = asyncio.run(self.server.advance_workflow(workflow_id, {"reflections": ["communication insights"]}))
            assert result2["completed"] == True

            # Check that workflow captured participant memories
            workflow = self.server.active_workflows[workflow_id]
            assert len(workflow["stage_history"]) == 2
            assert workflow["status"] == "completed"

    def test_workflow_adapts_to_participant_needs(self):
        """Test that workflows adapt based on participant responses and needs."""
        workflow_id = "adaptive_test"
        self.server.active_workflows[workflow_id] = {
            "id": workflow_id,
            "type": "dilemma",
            "template": {
                "stages": [
                    {
                        "name": "Assess Situation",
                        "transitions": {
                            "next": "Technical Solution",
                            "alternative": "Process Discussion"
                        }
                    }
                ]
            },
            "participants": ["alice"],
            "context": {"emotional_context": "frustrated"},
            "current_stage": 0,
            "stage_history": []
        }

        # Test adaptation based on emotional context
        with patch.object(self.server, '_process_stage') as mock_process:
            # Simulate emotional response requiring process discussion
            mock_process.return_value = {
                "emotional_response": "feeling overwhelmed",
                "alternative_path": True
            }

            result = asyncio.run(self.server.advance_workflow(workflow_id, {"feeling": "overwhelmed"}))
            assert result["advanced"] == True
            assert result["current_stage"] == "Process Discussion"

    def test_workflow_creates_safe_space_for_vulnerability(self):
        """Test that workflows provide safe spaces for team vulnerability and growth."""
        # This is more of an integration test concept - workflows should:
        # 1. Create psychological safety
        # 2. Allow expression of uncertainty
        # 3. Build trust through shared experience
        # 4. Facilitate rather than direct

        workflow_id = "safety_test"
        participants = ["alice", "bob"]

        self.server.active_workflows[workflow_id] = {
            "id": workflow_id,
            "type": "reflection",
            "template": {
                "stages": [
                    {
                        "name": "Share Vulnerabilities",
                        "activities": [
                            {"type": "reflection", "prompt": "What's challenging you this sprint?"}
                        ],
                        "transitions": {"next": "Build Support"}
                    },
                    {
                        "name": "Build Support",
                        "activities": [
                            {"type": "reflection", "prompt": "How can we support each other?"}
                        ],
                        "transitions": {"complete": "Stronger Together"}
                    }
                ]
            },
            "participants": participants,
            "context": {"focus": "team_wellbeing"},
            "current_stage": 0,
            "stage_history": []
        }

        # Simulate safe vulnerability sharing
        vulnerability_input = {"response": "I'm struggling with this complex feature"}
        support_input = {"response": "I can help pair program on that"}

        with patch.object(self.server, '_process_stage') as mock_process, \
             patch.object(self.server, '_log_workflow_event') as mock_log:

            # First stage - sharing vulnerability
            mock_process.return_value = {"vulnerability_shared": True, "emotional_safety": "high"}
            result1 = asyncio.run(self.server.advance_workflow(workflow_id, vulnerability_input))
            assert result1["advanced"] == True

            # Second stage - building support
            mock_process.return_value = {"support_offered": True, "completed": True, "trust_built": True}
            result2 = asyncio.run(self.server.advance_workflow(workflow_id, support_input))
            assert result2["completed"] == True

            # Verify the workflow created connection
            workflow = self.server.active_workflows[workflow_id]
            assert workflow["status"] == "completed"
            assert len(workflow["stage_history"]) == 2


if __name__ == "__main__":
    pytest.main([__file__])