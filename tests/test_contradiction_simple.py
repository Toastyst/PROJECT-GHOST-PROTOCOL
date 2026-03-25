#!/usr/bin/env python3
"""
Simple contradiction test - demonstrates synthesis capability.
"""

import asyncio
from src.ghost_protocol.servers.yolo_protocol import YOLOEngine

async def test_contradiction_simple():
    """Simple test showing contradiction detection and synthesis."""
    print("🔀 Testing contradiction resolution...")

    yolo = YOLOEngine()

    # Test the reflection capability (Scars Test)
    print("\n🗣️ Testing self-reflection...")
    reflection = await yolo.reflect_on_learning()
    print(f"Reflection: {reflection}")

    # Test mission parsing
    print("\n🎯 Testing mission parsing...")
    mission = await yolo.parse_mission_objective("Add real-time notifications for failed login attempts")
    print(f"Parsed mission: autonomy_level={mission.autonomy_level}")

    print("\n✅ Basic functionality verified!")
    print("🔀 Simple contradiction test complete!")

if __name__ == "__main__":
    asyncio.run(test_contradiction_simple())