#!/usr/bin/env python3
"""
Tests for Hooks Server - Testing reflection at development thresholds.

These tests verify the Ghost's ability to pause at meaningful moments.
"""

import asyncio
import pytest
from unittest.mock import patch, MagicMock
from src.ghost_protocol.core.hooks_server import HooksServer, get_hooks_server


class TestHooksServer:
    """Test the Ghost's reflection at development lifecycle thresholds."""

    def setup_method(self):
        """Set up test environment."""
        self.server = HooksServer()
        # Reset global instance
        global hooks_instance
        hooks_instance = self.server

    def test_hook_installation_creates_git_hooks(self):
        """Test that hooks can be installed in git repository."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', create=True) as mock_open, \
             patch('pathlib.Path.chmod'):

            # Mock file operations
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = asyncio.run(self.server.install_git_hooks())
            assert result == True

    def test_pre_commit_hook_provides_reflection(self):
        """Test that pre-commit hook offers meaningful reflection."""
        context = {
            "files": ["auth.py", "test_auth.py", "config.json"],
            "commit_message": "Add authentication system"
        }

        reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", context))
        assert isinstance(reflection, str)
        assert len(reflection) > 0
        # Should contain reflective language
        assert any(word in reflection.lower() for word in ["prepare", "join", "story", "feel", "learn"])

    def test_pre_push_hook_provides_relationship_reflection(self):
        """Test that pre-push hook reflects on sharing work with others."""
        context = {
            "commits": ["commit1", "commit2", "commit3"],
            "remote_info": "origin/main"
        }

        reflection = asyncio.run(self.server.trigger_hook_reflection("pre-push", context))
        assert isinstance(reflection, str)
        assert len(reflection) > 0
        # Should address sharing with others
        assert any(word in reflection.lower() for word in ["others", "see", "share", "trust", "influence"])

    def test_pr_hook_provides_conversation_reflection(self):
        """Test that PR hook reflects on the conversation being started."""
        context = {
            "pr_title": "Implement user authentication",
            "reviewers": ["alice", "bob"]
        }

        reflection = asyncio.run(self.server.trigger_hook_reflection("pr", context))
        assert isinstance(reflection, str)
        assert len(reflection) > 0
        # Should address conversation and feedback
        assert any(word in reflection.lower() for word in ["conversation", "review", "feedback", "understand"])

    def test_deploy_hook_provides_impact_reflection(self):
        """Test that deploy hook reflects on real-world impact."""
        context = {
            "environment": "production",
            "affected_users": 10000
        }

        reflection = asyncio.run(self.server.trigger_hook_reflection("deploy", context))
        assert isinstance(reflection, str)
        assert len(reflection) > 0
        # Should address real-world impact
        assert any(word in reflection.lower() for word in ["users", "affect", "serve", "impact", "responsibility"])

    def test_hook_respects_presence_rule_violations(self):
        """Test that hooks pause when presence rules are violated."""
        context = {
            "user_consent": False,
            "files": ["test.py"]
        }

        reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", context))
        assert "presence boundaries" in reflection.lower()

    def test_hook_activates_skills_based_on_context(self):
        """Test that hooks activate appropriate skills based on context."""
        # Emotional context should trigger listening skill
        emotional_context = {
            "commit_message": "This is so frustrating, the bug won't go away",
            "files": ["debug.py"]
        }

        with patch('hooks_server.get_skills_engine') as mock_get_skills:
            mock_skills = MagicMock()
            mock_listening_response = {
                "skill": "listening",
                "response": "I hear your frustration",
                "emotional_context": "frustration"
            }
            mock_skills.activate_skill.return_value = mock_listening_response
            mock_get_skills.return_value = mock_skills

            reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", emotional_context))
            assert "frustration" in reflection

    def test_hook_config_persisted_and_loaded(self):
        """Test that hook configuration is properly saved and loaded."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', create=True) as mock_open, \
             patch('json.load') as mock_load, \
             patch('json.dump') as mock_dump:

            # Mock existing config
            mock_load.return_value = {"hook_config": {"enabled": True, "reflection_mode": "question"}}

            config = self.server.load_config()
            assert config["hook_config"]["enabled"] == True
            assert config["hook_config"]["reflection_mode"] == "question"

    def test_hook_configuration_update(self):
        """Test that hook settings can be updated."""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', create=True) as mock_open, \
             patch('json.load') as mock_load, \
             patch('json.dump') as mock_dump, \
             patch('os.makedirs'):

            # Mock existing config
            mock_load.return_value = {"hook_config": {"enabled": True, "reflection_mode": "question"}}

            success = asyncio.run(self.server.configure_hook("pre-commit", {
                "enabled": False,
                "reflection_mode": "pause"
            }))

            assert success == True
            # Verify dump was called with updated config
            assert mock_dump.called

    def test_different_reflection_modes_produce_different_responses(self):
        """Test that different reflection modes produce different types of responses."""
        context = {"files": ["auth.py"], "commit_message": "Add login"}

        # Test question mode
        with patch.object(self.server, 'load_config', return_value={"hook_config": {"reflection_mode": "question"}}):
            question_reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", context))
            assert "?" in question_reflection  # Questions end with ?

        # Test mirror mode
        with patch.object(self.server, 'load_config', return_value={"hook_config": {"reflection_mode": "mirror"}}):
            mirror_reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", context))
            assert any(word in mirror_reflection.lower() for word in ["👁️", "prepare", "join"])

        # Test pause mode
        with patch.object(self.server, 'load_config', return_value={"hook_config": {"reflection_mode": "pause"}}):
            pause_reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", context))
            assert any(word in pause_reflection.lower() for word in ["⏸️", "before", "feel", "consider"])

    def test_hook_handles_missing_context_gracefully(self):
        """Test that hooks handle missing or incomplete context gracefully."""
        # Empty context
        reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", {}))
        assert isinstance(reflection, str)
        assert len(reflection) > 0

        # Unknown hook type
        reflection = asyncio.run(self.server.trigger_hook_reflection("unknown_hook", {"files": ["test.py"]}))
        assert "threshold" in reflection.lower()

    def test_hook_status_reporting(self):
        """Test that hook status is properly reported."""
        with patch('pathlib.Path.exists', side_effect=lambda: True), \
             patch.object(self.server, 'load_config', return_value={
                 "hook_config": {"enabled": True, "reflection_mode": "question"}
             }):

            status = asyncio.run(self.server.get_hook_status())
            assert status["enabled"] == True
            assert status["reflection_mode"] == "question"
            assert "hooks_installed" in status
            assert "active_hooks" in status

    def test_hook_adapts_to_file_types_and_counts(self):
        """Test that hooks provide different reflections based on file types and counts."""
        # Many files
        many_files_context = {
            "files": ["file1.py", "file2.py", "file3.py", "file4.py", "file5.py", "file6.py"],
            "commit_message": "Refactor authentication"
        }

        many_files_reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", many_files_context))
        assert any(word in many_files_reflection.lower() for word in ["many", "purpose", "unites"])

        # Single file
        single_file_context = {
            "files": ["auth.py"],
            "commit_message": "Fix typo"
        }

        single_file_reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", single_file_context))
        assert any(word in single_file_reflection.lower() for word in ["focused", "specific", "solve"])

        # Config files
        config_context = {
            "files": ["config.json", "settings.py"],
            "commit_message": "Update configuration"
        }

        config_reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", config_context))
        assert any(word in config_reflection.lower() for word in ["ripple", "feels", "change"])

    def test_hook_preserves_git_workflow_integrity(self):
        """Test that hooks don't break the git workflow when they fail."""
        # Even if hook logic fails, git operation should continue
        with patch.object(self.server, 'load_config', side_effect=Exception("Config error")):
            # Should not raise exception, should handle gracefully
            reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", {}))
            assert isinstance(reflection, str)  # Still returns a string

    def test_hook_creates_opportunity_for_presence(self):
        """Test that hooks create genuine opportunities for meaningful presence."""
        # Hooks should offer reflection, not demand action
        context = {"files": ["important.py"], "commit_message": "Critical security fix"}

        reflection = asyncio.run(self.server.trigger_hook_reflection("pre-commit", context))

        # Should be invitational, not imperative
        imperative_words = ["must", "should", "need to", "have to"]
        invitational_words = ["what", "how", "feel", "consider", "think about"]

        has_invitational = any(word in reflection.lower() for word in invitational_words)
        has_imperative = any(word in reflection.lower() for word in imperative_words)

        # Should favor invitation over command
        assert has_invitational or not has_imperative


if __name__ == "__main__":
    pytest.main([__file__])