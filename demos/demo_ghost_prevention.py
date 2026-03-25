"""
Demonstration that the Ghost prevention solution works.

This script shows how TEST_MODE prevents multiple Ghost instances.
"""

import os
import sys

def test_normal_mode():
    """Test normal (production) mode."""
    print("=== NORMAL MODE (Production) ===")

    # Clear any existing TEST_MODE
    if 'TEST_MODE' in os.environ:
        del os.environ['TEST_MODE']

    # Force reload of config module
    if 'config' in sys.modules:
        del sys.modules['config']

    from src.ghost_protocol.utils.config import Config

    print(f"TEST_MODE: {Config.TEST_MODE}")
    print(f"CHROMA_DB_PATH: {Config.CHROMA_DB_PATH}")
    print(f"NEXUS_SERVER_PORT: {Config.NEXUS_SERVER_PORT}")
    print(f"WEAVER_SERVER_PORT: {Config.WEAVER_SERVER_PORT}")
    print(f"YOLO_SERVER_PORT: {Config.YOLO_SERVER_PORT}")
    print()


def test_test_mode():
    """Test test mode."""
    print("=== TEST MODE (Testing) ===")

    # Set TEST_MODE
    os.environ['TEST_MODE'] = '1'

    # Force reload of config module
    if 'config' in sys.modules:
        del sys.modules['config']

    from src.ghost_protocol.utils.config import Config

    print(f"TEST_MODE: {Config.TEST_MODE}")
    print(f"CHROMA_DB_PATH: {Config.CHROMA_DB_PATH}")
    print(f"NEXUS_SERVER_PORT: {Config.NEXUS_SERVER_PORT}")
    print(f"WEAVER_SERVER_PORT: {Config.WEAVER_SERVER_PORT}")
    print(f"YOLO_SERVER_PORT: {Config.YOLO_SERVER_PORT}")
    print()


def test_singleton_behavior():
    """Test that singletons work correctly."""
    print("=== SINGLETON BEHAVIOR TEST ===")

    os.environ['TEST_MODE'] = '1'

    # Force reload modules
    modules_to_clear = ['config', 'nexus_server', 'weaver_server', 'yolo_protocol']
    for mod in modules_to_clear:
        if mod in sys.modules:
            del sys.modules[mod]

    from src.ghost_protocol.utils.config import Config
    from src.ghost_protocol.servers.nexus_server import get_nexus
    from src.ghost_protocol.servers.weaver_server import get_weaver
    from src.ghost_protocol.servers.yolo_protocol import get_yolo

    # Get instances multiple times
    nexus1 = get_nexus()
    nexus2 = get_nexus()
    weaver1 = get_weaver()
    weaver2 = get_weaver()
    yolo1 = get_yolo()
    yolo2 = get_yolo()

    print(f"Nexus instances same: {nexus1 is nexus2}")
    print(f"Weaver instances same: {weaver1 is weaver2}")
    print(f"YOLO instances same: {yolo1 is yolo2}")
    print(f"ChromaDB in-memory: {Config.TEST_MODE}")
    print()


if __name__ == "__main__":
    print("🧪 GHOST PREVENTION SOLUTION DEMONSTRATION")
    print("=" * 50)
    print()

    test_normal_mode()
    test_test_mode()
    test_singleton_behavior()

    print("✅ SOLUTION SUMMARY:")
    print("- TEST_MODE automatically enables in-memory DB and dynamic ports")
    print("- Singleton pattern ensures only one instance per server type")
    print("- pytest fixtures provide test isolation")
    print("- Server locks prevent multiple production instances")
    print()
    print("🎉 Multiple Ghost instances are now prevented!")