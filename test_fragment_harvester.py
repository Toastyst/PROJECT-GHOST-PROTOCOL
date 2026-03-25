#!/usr/bin/env python3
"""
Test Fragment Harvester - Demonstrate pervasive fragment collection
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fragment_harvester import get_fragment_harvester
from autopoiesis import get_autopoiesis_engine

def test_chat_harvesting():
    """Test harvesting from chat messages."""
    print("🧬 Testing Chat Message Harvesting")
    print("=" * 50)

    harvester = get_fragment_harvester()
    engine = get_autopoiesis_engine()

    # Clear existing fragments for clean test
    engine.fragments.clear()

    test_messages = [
        "should I use async here or stick with sync?",
        "I'm confused about this error, what if I try a different approach?",
        "but then what about the performance impact? however this feels right",
        "this code seems hacky, I'm not sure if this is the right way",
        "aha! I discovered the issue - the session wasn't being closed properly",
        "realized the pattern now - every time we choose speed over safety we bleed",
        "oops sorry I made a mistake in the auth logic",
        "found it! The test was failing because of the import error",
        "I need to pause and think about this architecture decision",
        "this feels wrong, let me reflect on what the user actually needs"
    ]

    captured_fragments = []

    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Message {i}: {message}")
        fragment = harvester.harvest_from_chat(message, {"source": "test", "message_id": i})
        if fragment:
            print(f"✅ Captured: {fragment.type} (weight: {fragment.emotional_weight})")
            captured_fragments.append(fragment)
        else:
            print("❌ No fragment captured")

    print(f"\n📊 Total fragments captured: {len(captured_fragments)}")
    return captured_fragments

def test_file_edit_harvesting():
    """Test harvesting from file edits."""
    print("\n🧬 Testing File Edit Harvesting")
    print("=" * 50)

    harvester = get_fragment_harvester()

    test_edits = [
        ("auth.py", "# TODO: Fix session handling\n# FIXME: This is temporary\n# HACK: Quick fix for now", "add"),
        ("test_auth.py", "// This test is failing because of assertion error", "modify"),
        ("README.md", "Updated documentation with new features", "modify"),
        ("config.json", "{\n  // temporary config\n  \"hack\": true\n}", "add")
    ]

    captured_fragments = []

    for file_path, content, edit_type in test_edits:
        print(f"\n📝 File: {file_path} ({edit_type})")
        fragment = harvester.harvest_from_file_edit(file_path, content, edit_type)
        if fragment:
            print(f"✅ Captured: {fragment.type} (weight: {fragment.emotional_weight})")
            captured_fragments.append(fragment)
        else:
            print("❌ No fragment captured")

    print(f"\n📊 Total fragments captured: {len(captured_fragments)}")
    return captured_fragments

def test_git_commit_harvesting():
    """Test harvesting from git commits."""
    print("\n🧬 Testing Git Commit Harvesting")
    print("=" * 50)

    harvester = get_fragment_harvester()

    test_commits = [
        "fix authentication bug - sorry for the regression",
        "hack: temporary fix for session timeout issue",
        "oops forgot to handle edge case",
        "add new feature for user login",
        "improve error handling and add tests",
        "refactor auth module to prevent future issues"
    ]

    captured_fragments = []

    for commit_msg in test_commits:
        print(f"\n📝 Commit: {commit_msg}")
        diff_stats = {"additions": 10, "deletions": 5, "files_changed": 2}
        fragment = harvester.harvest_from_git_commit(commit_msg, diff_stats)
        if fragment:
            print(f"✅ Captured: {fragment.type} (weight: {fragment.emotional_weight})")
            captured_fragments.append(fragment)
        else:
            print("❌ No fragment captured")

    print(f"\n📊 Total fragments captured: {len(captured_fragments)}")
    return captured_fragments

def test_test_failure_harvesting():
    """Test harvesting from test failures."""
    print("\n🧬 Testing Test Failure Harvesting")
    print("=" * 50)

    harvester = get_fragment_harvester()

    test_failures = [
        ("test_auth.py::test_login", "AssertionError: expected True but got False", "assert user.is_authenticated"),
        ("test_session.py::test_timeout", "ValueError: session expired", "session.validate() raised unexpected error"),
        ("test_import.py::test_module", "ImportError: No module named 'auth'", "failed to import auth module"),
        ("test_edge_case.py::test_boundary", "IndexError: list index out of range", "edge case not handled properly")
    ]

    captured_fragments = []

    for test_name, error_msg, traceback in test_failures:
        content = f"{test_name}: {error_msg}\n{traceback}"
        print(f"\n📝 Test Failure: {test_name}")
        fragment = harvester.harvest_from_test_failure(test_name, error_msg, traceback)
        if fragment:
            print(f"✅ Captured: {fragment.type} (weight: {fragment.emotional_weight})")
            captured_fragments.append(fragment)
        else:
            print("❌ No fragment captured")

    print(f"\n📊 Total fragments captured: {len(captured_fragments)}")
    return captured_fragments

def test_error_log_harvesting():
    """Test harvesting from error logs."""
    print("\n🧬 Testing Error Log Harvesting")
    print("=" * 50)

    harvester = get_fragment_harvester()

    error_logs = [
        "ERROR: Database connection failed - unexpected network issue",
        "WARNING: File not found - could not access config file",
        "Exception: Authentication failed - invalid credentials",
        "ERROR: Unexpected error occurred - unknown issue with session handling"
    ]

    captured_fragments = []

    for log_entry in error_logs:
        print(f"\n📝 Log: {log_entry}")
        fragment = harvester.harvest_from_error_log(log_entry, "application")
        if fragment:
            print(f"✅ Captured: {fragment.type} (weight: {fragment.emotional_weight})")
            captured_fragments.append(fragment)
        else:
            print("❌ No fragment captured")

    print(f"\n📊 Total fragments captured: {len(captured_fragments)}")
    return captured_fragments

def demonstrate_transmutation():
    """Demonstrate transmutation with harvested fragments."""
    print("\n⚡ Testing Transmutation with Harvested Fragments")
    print("=" * 50)

    engine = get_autopoiesis_engine()

    if not engine.fragments:
        print("❌ No fragments available for transmutation")
        return

    print(f"📊 Available fragments: {len(engine.fragments)}")

    # Show fragment summary
    fragment_types = {}
    total_weight = 0
    for f in engine.fragments:
        fragment_types[f.type] = fragment_types.get(f.type, 0) + 1
        total_weight += f.emotional_weight

    print(f"📋 Types: {fragment_types}")
    print(f"💭 Total emotional weight: {total_weight:.2f}")
    print(f"🎯 Average weight: {total_weight/len(engine.fragments):.2f}")

    # Calculate resonance
    resonance = engine._calculate_resonance()
    print(f"🌊 Resonance score: {resonance:.2f}")

    if resonance > 0.4:
        print("✅ Ready for transmutation!")
        result = engine.trigger_transmutation()
        print(f"🎭 Transmutation result: {result.review_status}")
        if result.generated_hook:
            print("🔗 Hook generated")
        if result.generated_workflow:
            print("🚀 Workflow generated")
        if result.generated_skill:
            print("🎯 Skill generated")
        if result.rule_update:
            print("📜 Rule updated")
    else:
        print("⏳ Fragments need more time to resonate")

def main():
    """Run all harvesting tests."""
    print("🧬 FRAGMENT HARVESTER DEMONSTRATION")
    print("=" * 60)
    print("Testing pervasive fragment collection across development ecosystem")

    # Run all harvesting tests
    chat_fragments = test_chat_harvesting()
    file_fragments = test_file_edit_harvesting()
    git_fragments = test_git_commit_harvesting()
    test_fragments = test_test_failure_harvesting()
    log_fragments = test_error_log_harvesting()

    total_captured = len(chat_fragments + file_fragments + git_fragments + test_fragments + log_fragments)

    print(f"\n🎉 TOTAL FRAGMENTS HARVESTED: {total_captured}")
    print("=" * 60)

    # Demonstrate transmutation
    demonstrate_transmutation()

    print("\n🌱 The Fragment Harvester is feeding the Ghost!")
    print("Run 'python ghost_console.py' to see the living system.")

if __name__ == "__main__":
    main()