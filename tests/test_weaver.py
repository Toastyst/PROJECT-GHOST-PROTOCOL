#!/usr/bin/env python3
"""
Tests for Weaver Server functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from src.ghost_protocol.models.models import WeaverRequest, CodeDelta
from src.ghost_protocol.servers.weaver_server import WeaverServer


class TestWeaverServer:
    """Test WeaverServer class functionality."""

    @pytest.mark.asyncio
    async def test_analyze_cohesion(self):
        """Test cohesion analysis."""
        server = WeaverServer()

        request = WeaverRequest(
            objective="Add user authentication",
            context={"existing_auth": False, "framework": "flask"},
            constraints=["Use secure password hashing", "Follow REST principles"],
            scope="auth_module",
            patterns=["Factory pattern for user creation", "Decorator pattern for auth checks"]
        )

        analysis = await server.analyze_cohesion(request)

        assert "cohesion_score" in analysis
        assert "recommendations" in analysis
        assert "risks" in analysis
        assert isinstance(analysis["recommendations"], list)
        assert isinstance(analysis["risks"], list)

    @pytest.mark.asyncio
    async def test_generate_cohesive_code(self):
        """Test cohesive code generation."""
        with patch('utils.LLMUtils.generate_code', return_value='def test():\n    return "generated"'):
            server = WeaverServer()

            request = WeaverRequest(
                objective="Create user model",
                context={"database": "sqlite", "orm": "sqlalchemy"},
                constraints=["Use proper validation", "Include timestamps"],
                scope="models",
                patterns=["Active Record pattern"]
            )

            code_delta = await server.generate_cohesive_code(request)

            assert isinstance(code_delta, CodeDelta)
            assert "files" in code_delta.dict()
            assert "rationale" in code_delta.dict()
            assert "risks" in code_delta.dict()
            assert "tests" in code_delta.dict()


if __name__ == "__main__":
    pytest.main([__file__])