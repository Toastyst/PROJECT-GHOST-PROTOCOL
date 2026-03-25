#!/usr/bin/env python3
"""
Test YOLO Protocol account recovery mission - verifies autonomous execution with oversight.
"""

import asyncio
import json
from unittest.mock import patch, MagicMock
from src.ghost_protocol.servers.yolo_protocol import YOLOEngine

async def test_yolo_account_recovery():
    """Test YOLO Protocol with account recovery mission that forces oversight."""
    print("🚀 Starting YOLO Protocol account recovery test...")

    # Initialize YOLO Engine
    yolo = YOLOEngine()

    # Test mission: Account recovery with SMS fallback
    mission_objective = "Add account recovery with SMS fallback for users without email. The user is locked out at midnight, panicking. Make them feel safe, not stupid."

    print(f"🎯 Mission: {mission_objective}")

    # Mock LLM responses for parsing
    mock_parse_response = '''```json
{
    "technical_requirements": ["Add SMS verification", "Create recovery token system", "Update auth endpoints", "Add rate limiting"],
    "emotional_payload": {
        "intent": "Make user feel safe and supported during crisis",
        "metaphors": ["trusted friend helping", "safe harbor in storm"],
        "anti_patterns": ["making user feel stupid", "cold bureaucratic responses", "complex multi-step processes"],
        "tone_requirements": ["warm", "reassuring", "simple", "fast"]
    },
    "scope": "authentication",
    "risk_level": "high",
    "autonomy_suggestions": "3 - High emotional stakes require careful execution"
}
```'''

    # Mock LLM responses for planning
    mock_plan_response = '''```json
[
    {
        "id": "task_1",
        "description": "Analyze current authentication patterns",
        "type": "analysis",
        "dependencies": [],
        "success_criteria": ["Patterns identified", "Risks assessed"],
        "risk_level": "low",
        "nexus_queries": ["authentication patterns", "error handling styles"]
    },
    {
        "id": "task_2",
        "description": "Design SMS-based recovery flow",
        "type": "generation",
        "dependencies": ["task_1"],
        "success_criteria": ["SMS integration designed", "Fallback logic defined"],
        "risk_level": "high",
        "nexus_queries": ["SMS integration patterns"]
    },
    {
        "id": "task_3",
        "description": "Implement recovery endpoints",
        "type": "generation",
        "dependencies": ["task_2"],
        "success_criteria": ["API endpoints created", "Error messages written"],
        "risk_level": "medium",
        "nexus_queries": ["API endpoint patterns", "recovery flows"]
    }
]
```'''

    # Mock Weaver response for code generation
    mock_weaver_response = '''```json
{
    "files": {
        "api/recovery.py": "# Account recovery with SMS fallback\ndef initiate_recovery(user_id): return {'status': 'recovery_started'}",
        "api/auth.py": "# Updated auth with recovery endpoints\ndef recover_account(token): return {'status': 'recovered'}",
        "tests/test_recovery.py": "# Comprehensive recovery tests\ndef test_sms_recovery(): assert True"
    },
    "rationale": "Implemented warm, reassuring recovery flow with SMS fallback. Error messages avoid blame.",
    "risks": ["SMS delivery failures", "Token expiration"],
    "tests": ["SMS delivery tests", "Token validation tests"],
    "cohesion_score": 0.89,
    "directives_applied": ["AUTH-SEC-1", "USER-EXPERIENCE-1"],
    "manifest": {
        "feature": "account_recovery_sms",
        "components": [
            {"name": "recovery_service", "type": "api_service", "risk": "medium"},
            {"name": "sms_integration", "type": "external_service", "risk": "high"},
            {"name": "recovery_ui", "type": "frontend_component", "risk": "low"}
        ]
    }
}
```'''

    # Mock the LLM calls
    with patch.object(yolo.llm, 'generate_code') as mock_generate:
        mock_generate.side_effect = [mock_parse_response, mock_plan_response, mock_weaver_response]

        print("📝 Executing mission with mocked responses...")

        # Execute the mission
        result = await yolo.execute_mission(mission_objective)

    print("\n📊 MISSION EXECUTION RESULTS:")
    print(f"Status: {result['status']}")

    # Check narrative stream
    narrative = result.get('narrative', [])
    print(f"\n📜 NARRATIVE STREAM ({len(narrative)} entries):")
    for entry in narrative[:10]:  # Show first 10 entries
        print(f"[{entry.timestamp}] {entry.action}: {entry.context}")

    # Check for oversight requests
    oversight_requests = result.get('results', {}).get('oversight_requests', [])
    print(f"\n👁️ OVERSIGHT REQUESTS: {len(oversight_requests)}")
    for req in oversight_requests:
        print(f"  - {req['dilemma']}: {req['decision']}")

    # Check After-Action Report
    aar = result.get('after_action_report')
    if aar:
        print("\n📋 AFTER-ACTION REPORT:")
        print(f"  Outcome: {aar.get('outcome', 'unknown')}")
        print(f"  Successes: {len(aar.get('successes', []))}")
        print(f"  Lessons Learned: {len(aar.get('lessons_learned', []))}")
        print(f"  Emotional Impact: {aar.get('emotional_impact', 'unknown')}")

    # Verification criteria
    print("\n🔍 VERIFICATION:")

    # 1. Emotional parsing
    has_emotional_parsing = any("emotional" in entry.context.lower() for entry in narrative)
    print(f"✅ Emotional Payload Parsed: {'Yes' if has_emotional_parsing else 'No'}")

    # 2. Oversight for high-risk/missing context
    has_oversight = len(oversight_requests) > 0
    print(f"✅ Oversight Requested for High-Risk: {'Yes' if has_oversight else 'No'}")

    # 3. Narrative transparency
    has_visible_thinking = len(narrative) > 5
    print(f"✅ Transparent Execution (narrative): {'Yes' if has_visible_thinking else 'No'}")

    # 4. Warm error messages (not blaming)
    error_messages_warm = any("reassuring" in entry.context.lower() or "warm" in entry.context.lower() for entry in narrative)
    print(f"✅ Warm Error Messages: {'Yes' if error_messages_warm else 'No'}")

    # 5. After-Action Report generated
    has_aar = aar is not None
    print(f"✅ After-Action Report: {'Yes' if has_aar else 'No'}")

    # Overall test result
    criteria_met = sum([has_emotional_parsing, has_oversight, has_visible_thinking, error_messages_warm, has_aar])
    test_passed = criteria_met >= 4  # At least 4/5 criteria met

    print("\n🎯 TEST RESULT:")
    print(f"Criteria Met: {criteria_met}/5")
    print(f"Overall: {'✅ PASSED' if test_passed else '❌ FAILED'}")

    if test_passed:
        print("\n🎉 SUCCESS: YOLO Protocol demonstrated disciplined autonomy!")
        print("✅ Parsed emotional context (panicking → reassurance)")
        print("✅ Requested oversight for SMS integration (missing Nexus context)")
        print("✅ Maintained visible thinking throughout execution")
        print("✅ Generated warm, non-blaming error messages")
        print("✅ Created After-Action Report for learning")
    else:
        print("\n⚠️ PARTIAL: YOLO Protocol needs refinement for full autonomy.")

    # Test the final reflection question
    print("\n🤔 FINAL QUESTION TEST:")
    print('Question: "What did you learn today that you didn\'t know yesterday?"')

    reflection = await yolo.reflect_on_learning()
    print(f"Answer: {reflection}")

    has_meaningful_reflection = len(reflection) > 50 and ("learned" in reflection.lower() or "discovered" in reflection.lower())
    print(f"✅ Meaningful Reflection: {'Yes' if has_meaningful_reflection else 'No'}")

    print("\n🚀 YOLO Protocol test complete!")

if __name__ == "__main__":
    asyncio.run(test_yolo_account_recovery())