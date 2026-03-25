#!/usr/bin/env python3
"""
Tests for YOLO Protocol functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from src.ghost_protocol.models.models import YOLOMission
from src.ghost_protocol.servers.yolo_protocol import YOLOEngine


class TestYOLOEngine:
    """Test YOLOEngine class functionality."""

    @pytest.mark.asyncio
    async def test_plan_mission(self):
        """Test mission planning."""
        engine = YOLOEngine()

        mission = YOLOMission(
            goal="Implement user authentication system",
            autonomy_level=3,
            checkpoints=["Design review", "Security audit"],
            constraints=["Use secure hashing", "Follow OWASP guidelines"],
            success_criteria=["Users can login", "Passwords are hashed", "Sessions are managed"]
        )

        steps = await engine.plan_mission(mission)

        assert isinstance(steps, list)
        assert len(steps) > 0
        assert "id" in steps[0]
        assert "description" in steps[0]
        assert "action" in steps[0]

    @pytest.mark.asyncio
    async def test_execute_step(self):
        """Test step execution."""
        engine = YOLOEngine()

        step = {
            "id": "step_1",
            "description": "Analyze requirements",
            "action": "analyze",
            "parameters": {"target": "authentication"},
            "checkpoint": None
        }

        context = {"current_phase": "planning"}

        result = await engine.execute_step(step, context)

        assert isinstance(result, dict)
        assert "status" in result
        assert "output" in result
        assert "data" in result

    @pytest.mark.asyncio
    async def test_request_oversight(self):
        """Test oversight request."""
        engine = YOLOEngine()

        dilemma = "Multiple authentication methods available"
        options = ["JWT tokens", "Session cookies", "API keys"]

        decision = await engine.request_oversight(dilemma, options)

        assert decision in options

    @pytest.mark.asyncio
    async def test_execute_step_analyze_action(self):
        """Test analyze action execution."""
        engine = YOLOEngine()

        step = {
            "id": "step_1",
            "description": "Analyze codebase",
            "action": "analyze",
            "parameters": {"target": "auth_module"},
            "checkpoint": None
        }

        context = {}
        result = await engine.execute_step(step, context)

        assert result["status"] == "completed"
        assert "auth_module" in result["output"]

    @pytest.mark.asyncio
    async def test_execute_step_execute_action(self):
        """Test execute action execution."""
        engine = YOLOEngine()

        step = {
            "id": "step_2",
            "description": "Implement authentication",
            "action": "execute",
            "parameters": {"goal": "user login"},
            "checkpoint": None
        }

        context = {}
        result = await engine.execute_step(step, context)

        assert result["status"] == "completed"
        assert "user login" in result["output"]

    @pytest.mark.asyncio
    async def test_execute_step_validate_action(self):
        """Test validate action execution."""
        engine = YOLOEngine()

        step = {
            "id": "step_3",
            "description": "Validate implementation",
            "action": "validate",
            "parameters": {"criteria": ["login works", "security ok"]},
            "checkpoint": None
        }

        context = {}
        result = await engine.execute_step(step, context)

        assert result["status"] == "completed"
        assert "criteria" in result["output"]


if __name__ == "__main__":
    pytest.main([__file__])