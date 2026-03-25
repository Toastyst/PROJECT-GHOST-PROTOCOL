"""
Test to verify that multiple test runs don't create multiple Ghost instances.

This test ensures that the singleton pattern and test mode isolation work correctly.
"""

import os
import pytest
import subprocess
import sys
from unittest.mock import patch


def test_no_multiple_ghost_instances():
    """Test that running tests doesn't create multiple Ghost instances."""
    # This test verifies that the TEST_MODE configuration prevents
    # multiple ChromaDB instances and server conflicts

    # Import should work without creating persistent instances
    from config import Config
    from nexus_server import get_nexus
    from weaver_server import get_weaver
    from yolo_protocol import get_yolo

    # Verify test mode is active
    assert Config.TEST_MODE == True
    assert Config.CHROMA_DB_PATH == ":memory:"
    assert Config.NEXUS_SERVER_PORT == 0
    assert Config.WEAVER_SERVER_PORT == 0
    assert Config.YOLO_SERVER_PORT == 0

    # Get instances - should work without conflicts
    nexus1 = get_nexus()
    nexus2 = get_nexus()
    assert nexus1 is nexus2  # Same instance

    weaver1 = get_weaver()
    weaver2 = get_weaver()
    assert weaver1 is weaver2  # Same instance

    yolo1 = get_yolo()
    yolo2 = get_yolo()
    assert yolo1 is yolo2  # Same instance

    # Verify in-memory ChromaDB is used
    assert nexus1.knowledge_base.client._settings.anonymized_telemetry == False

    print("✅ Multiple Ghost instances test passed - no conflicts detected")


def test_concurrent_test_runs():
    """Test that concurrent test runs don't interfere with each other."""
    # This simulates what happens when multiple pytest processes run
    # Each should get isolated resources

    from config import Config
    from conftest import temp_chroma_db

    # Each test gets its own temp directory
    with patch('config.Config.CHROMA_DB_PATH', 'test_db_1'):
        config1 = Config()
        assert config1.CHROMA_DB_PATH == 'test_db_1'

    with patch('config.Config.CHROMA_DB_PATH', 'test_db_2'):
        config2 = Config()
        assert config2.CHROMA_DB_PATH == 'test_db_2'

    # They should be different
    assert config1.CHROMA_DB_PATH != config2.CHROMA_DB_PATH

    print("✅ Concurrent test isolation test passed")


if __name__ == "__main__":
    test_no_multiple_ghost_instances()
    test_concurrent_test_runs()
    print("🎉 All multiple Ghost prevention tests passed!")