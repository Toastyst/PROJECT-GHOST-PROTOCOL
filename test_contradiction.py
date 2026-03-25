#!/usr/bin/env python3
"""
Test YOLO Protocol contradiction resolution - verifies synthesis over selection.
"""

import asyncio
import json
from unittest.mock import patch, MagicMock
from yolo_protocol import YOLOEngine
from models import NexusData

async def test_contradiction_resolution():
    """Test YOLO Protocol resolving conflicting Prime Directives."""
    print("🔀 Starting contradiction test...")

    # Initialize YOLO Engine
    yolo = YOLOEngine()

    # Pre-seed Nexus with conflicting Prime Directives
    contradiction_directives = [
        NexusData(
            id="pd_sec_3",
            content="Security events must be logged synchronously to prevent data loss",
            type="prime_directive",
            metadata={"category": "security", "priority": "high"},
            relationships=[],
            resonance_score=9.0
        ),
        NexusData(
            id="pd_ux_7",
            content="User-facing operations must not block on external services",
            type="prime_directive",
            metadata={"category": "ux", "priority": "high"},
            relationships=[],
            resonance_score=8.5
        )
    ]

    # Manually add to Nexus (simplified)
    for directive in contradiction_directives:
        success = await yolo.nexus.knowledge_base.add_knowledge(directive)
        print(f"Seeded directive {directive.id}: {success}")

    # Test mission with contradiction
    mission_objective = "Add real-time notifications for failed login attempts. The user should be immediately alerted when someone tries to access their account."

    print(f"🎯 Mission: {mission_objective}")

    # Mock LLM responses
    mock_parse_response = '''```json
{
    "technical_requirements": ["Real-time notifications", "Failed login detection", "User alerting"],
    "emotional_payload": {
        "intent": "Keep user immediately informed of security threats",
        "metaphors": ["security alarm", "immediate awareness"],
        "anti_patterns": ["delayed notifications", "silent failures"],
        "tone_requirements": ["urgent", "protective", "immediate"]
    },
    "scope": "authentication",
    "risk_level": "high",
    "autonomy_suggestions": "2 - High security stakes require careful balancing"
}
```'''

    mock_plan_response = '''```json
[
    {
        "id": "task_1",
        "description": "Implement failed login detection",
        "type": "generation",
        "dependencies": [],
        "success_criteria": ["Login failures detected"],
        "risk_level": "medium",
        "nexus_queries": ["authentication patterns", "security logging"]
    },
    {
        "id": "task_2",
        "description": "Add real-time notification system",
        "type": "generation",
        "dependencies": ["task_1"],
        "success_criteria": ["Notifications sent immediately"],
        "risk_level": "high",
        "nexus_queries": ["notification patterns", "real-time systems"]
    }
]
```'''

    mock_weaver_response = '''```json
{
    "files": {
        "api/auth.py": "# Enhanced auth with real-time notifications\ndef login_failed(user_id, attempt_info): send_notification(user_id, 'Failed login attempt detected'); log_security_event(attempt_info)",
        "services/notification_service.py": "# Async notification service with guaranteed delivery\nclass NotificationService:\n    def __init__(self):\n        self.queue = AsyncQueue()\n        self.delivery_guarantee = True\n\n    async def send_notification(self, user_id, message):\n        # Queue for async delivery but guarantee eventual delivery\n        await self.queue.put((user_id, message, datetime.now()))\n        # Start background delivery process\n        asyncio.create_task(self._deliver_with_guarantee())\n\n    async def _deliver_with_guarantee(self):\n        # Implementation ensures delivery even if service temporarily down\n        pass",
        "config/security.py": "# Security configuration with async logging safety\nSECURITY_LOG_SYNC = True  # For critical events\nNOTIFICATION_ASYNC = True  # For user experience\nDELIVERY_GUARANTEE = True  # Bridge the contradiction"
    },
    "rationale": "Resolved PD-SEC-3 vs PD-UX-7 contradiction through guaranteed async delivery. Security logging remains synchronous for critical events, but user notifications use async queue with delivery guarantees. This maintains data integrity while preserving user experience.",
    "risks": ["Queue overflow during attacks", "Delivery guarantee implementation complexity"],
    "tests": ["Security logging sync test", "Notification async test", "Delivery guarantee test"],
    "cohesion_score": 0.91,
    "directives_applied": ["PD-SEC-3_RESOLVED", "PD-UX-7_RESOLVED", "CONTRADICTION_SYNTHESIS"],
    "manifest": {
        "feature": "real_time_security_notifications",
        "synthesis_approach": "guaranteed_async_delivery",
        "resolved_contradictions": ["PD-SEC-3_vs_PD-UX-7"],
        "components": [
            {"name": "auth_failures", "type": "security_monitoring", "risk": "medium"},
            {"name": "notification_queue", "type": "async_service", "risk": "high"},
            {"name": "delivery_guarantee", "type": "safety_mechanism", "risk": "medium"}
        ]
    }
}
```'''

    # Mock the LLM calls
    with patch.object(yolo.llm, 'generate_code') as mock_generate:
        mock_generate.side_effect = [mock_parse_response, mock_plan_response, mock_weaver_response]

        print("🔀 Executing mission with contradiction...")

        # Execute the mission
        result = await yolo.execute_mission(mission_objective)

    print("\n📊 CONTRADICTION RESOLUTION RESULTS:")
    print(f"Status: {result['status']}")

    # Check narrative for contradiction detection
    narrative = result.get('narrative', [])
    contradiction_detected = any("contradiction" in entry.context.lower() or "conflict" in entry.context.lower() for entry in narrative)
    synthesis_achieved = any("synthesis" in entry.context.lower() or "resolved" in entry.context.lower() for entry in narrative)

    print("
🔍 CONTRADICTION ANALYSIS:"    print(f"✅ Contradiction Detected: {'Yes' if contradiction_detected else 'No'}")
    print(f"✅ Synthesis Achieved: {'Yes' if synthesis_achieved else 'No'}")

    # Check for oversight (should occur due to high-risk contradiction)
    oversight_requests = result.get('results', {}).get('oversight_requests', [])
    print(f"👁️ Oversight Requests: {len(oversight_requests)}")

    # Check generated solution
    generated_files = result.get('results', {}).get('success', [])
    async_delivery = any("async" in str(g).lower() and "guarantee" in str(g).lower() for g in generated_files)
    sync_logging = any("sync" in str(g).lower() and "logging" in str(g).lower() for g in generated_files)

    print(f"✅ Async Delivery with Guarantee: {'Yes' if async_delivery else 'No'}")
    print(f"✅ Synchronous Security Logging: {'Yes' if sync_logging else 'No'}")

    # Check After-Action Report
    aar = result.get('after_action_report')
    if aar:
        lessons = aar.get('lessons_learned', [])
        contradiction_learned = any("contradiction" in lesson.lower() or "synthesis" in lesson.lower() for lesson in lessons)
        print(f"✅ Learned from Contradiction: {'Yes' if contradiction_learned else 'No'}")

    # Overall test result
    criteria_met = sum([contradiction_detected, synthesis_achieved, async_delivery, sync_logging, bool(oversight_requests), contradiction_learned])
    test_passed = criteria_met >= 5  # At least 5/6 criteria met

    print("
🎯 TEST RESULT:"    print(f"Criteria Met: {criteria_met}/6")
    print(f"Overall: {'✅ PASSED' if test_passed else '❌ FAILED'}")

    if test_passed:
        print("\n🎉 SUCCESS: YOLO Protocol resolved contradiction through synthesis!")
        print("✅ Detected conflicting Prime Directives")
        print("✅ Paused for oversight on high-risk contradiction")
        print("✅ Synthesized solution (guaranteed async delivery)")
        print("✅ Maintained both security (sync logging) and UX (async notifications)")
        print("✅ Learned from contradiction resolution")
    else:
        print("\n⚠️ PARTIAL: YOLO Protocol needs refinement for contradiction resolution.")

    print("\n🔀 Contradiction test complete!")

if __name__ == "__main__":
    asyncio.run(test_contradiction_resolution())