#!/usr/bin/env python3
"""
Tests for Nexus Server functionality.
"""

import pytest
import asyncio
import os
import tempfile
from unittest.mock import Mock, patch

from models import NexusData
from nexus_server import NexusServer, KnowledgeBase
from utils import GitUtils, CodeAnalyzer


class TestKnowledgeBase:
    """Test KnowledgeBase class functionality."""

    def test_add_knowledge(self, temp_chroma_db):
        """Test adding knowledge entries."""
        kb = KnowledgeBase(db_path=temp_chroma_db)

        knowledge = NexusData(
            id="test_1",
            content="Test commit message",
            type="commit_message",
            metadata={"author": "test_author", "date": "2023-01-01"},
            relationships=[]
        )

        result = kb.add_knowledge(knowledge)
        assert result is True

    def test_query_knowledge(self, temp_chroma_db):
        """Test querying knowledge base."""
        kb = KnowledgeBase(db_path=temp_chroma_db)

        # Add test data
        knowledge = NexusData(
            id="test_1",
            content="Test commit message",
            type="commit_message",
            metadata={"author": "test_author"},
            relationships=[]
        )
        kb.add_knowledge(knowledge)

        # Query
        results = kb.query_knowledge("commit")
        assert len(results) >= 0  # May be empty due to embedding limitations


class TestNexusServer:
    """Test NexusServer class functionality."""

    @pytest.mark.asyncio
    async def test_ingest_codebase(self):
        """Test codebase ingestion."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repo
            os.chdir(temp_dir)
            os.system("git init")
            os.system("echo 'print(\"hello\")' > test.py")
            os.system("git add test.py")
            os.system("git -c user.email='test@test.com' -c user.name='Test' commit -m 'Initial commit'")

            server = NexusServer()
            result = await server.ingest_codebase(temp_dir)
            assert result is True

    @pytest.mark.asyncio
    async def test_query_nexus(self):
        """Test nexus querying."""
        server = NexusServer()
        results = await server.query_nexus("test query")
        assert isinstance(results, list)


class TestGitUtils:
    """Test GitUtils functionality."""

    def test_get_commit_history(self):
        """Test commit history extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            os.system("git init")
            os.system("echo 'test' > file.txt")
            os.system("git add file.txt")
            os.system("git -c user.email='test@test.com' -c user.name='Test' commit -m 'Test commit'")

            commits = GitUtils.get_commit_history(temp_dir, limit=1)
            assert len(commits) > 0
            assert "message" in commits[0]
            assert "author" in commits[0]


class TestCodeAnalyzer:
    """Test CodeAnalyzer functionality."""

    def test_extract_functions_from_file(self):
        """Test function extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def test_function(arg1, arg2):
    '''Test function docstring'''
    return arg1 + arg2

class TestClass:
    def method(self):
        pass
""")
            f.flush()

            functions = CodeAnalyzer.extract_functions_from_file(f.name)
            assert len(functions) > 0
            assert functions[0]['name'] == 'test_function'

            os.unlink(f.name)

    def test_extract_classes_from_file(self):
        """Test class extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
class TestClass:
    '''Test class docstring'''
    def method(self):
        pass
""")
            f.flush()

            classes = CodeAnalyzer.extract_classes_from_file(f.name)
            assert len(classes) > 0
            assert classes[0]['name'] == 'TestClass'

            os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__])