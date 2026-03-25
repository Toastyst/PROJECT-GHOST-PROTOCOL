"""
Pytest configuration and fixtures for Ghost Protocol testing.

Ensures test isolation by setting TEST_MODE and providing cleanup.
"""

import os
import tempfile
import shutil
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def test_mode():
    """Automatically set TEST_MODE for all tests."""
    original_test_mode = os.environ.get("TEST_MODE", "0")
    os.environ["TEST_MODE"] = "1"

    yield

    # Restore original value
    if original_test_mode == "0":
        os.environ.pop("TEST_MODE", None)
    else:
        os.environ["TEST_MODE"] = original_test_mode


@pytest.fixture
def temp_chroma_db():
    """Provide a temporary ChromaDB path for isolated testing."""
    temp_dir = tempfile.mkdtemp(prefix="ghost_test_db_")

    # Override config for this test
    with patch('config.Config.CHROMA_DB_PATH', temp_dir):
        yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls for testing."""
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value = {
            'choices': [{
                'message': {
                    'content': 'Mocked response for testing'
                }
            }]
        }
        yield mock_create


@pytest.fixture
def isolated_nexus(temp_chroma_db, mock_openai):
    """Provide an isolated Nexus server instance for testing."""
    from nexus_server import NexusServer

    # Create server with temp DB
    server = NexusServer()
    yield server

    # Cleanup will happen via temp_chroma_db fixture


@pytest.fixture
def isolated_weaver(temp_chroma_db, mock_openai):
    """Provide an isolated Weaver server instance for testing."""
    from weaver_server import WeaverServer

    # Create server with temp DB
    server = WeaverServer()
    yield server

    # Cleanup will happen via temp_chroma_db fixture


@pytest.fixture
def isolated_yolo(temp_chroma_db, mock_openai):
    """Provide an isolated YOLO server instance for testing."""
    from yolo_protocol import YOLOServer

    # Create server with temp DB
    server = YOLOServer()
    yield server

    # Cleanup will happen via temp_chroma_db fixture


@pytest.fixture(autouse=True)
def cleanup_ghost_instances():
    """Clean up any global Ghost instances between tests."""
    from nexus_server import nexus_instance
    from weaver_server import weaver_instance
    from yolo_protocol import yolo_instance

    # Reset global instances
    nexus_instance = None
    weaver_instance = None
    yolo_instance = None

    yield

    # Reset again after test
    nexus_instance = None
    weaver_instance = None
    yolo_instance = None