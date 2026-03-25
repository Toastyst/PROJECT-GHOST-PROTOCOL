#!/usr/bin/env python3
"""
Test Weaver rate limiting generation - verifies full-stack cohesive generation.
"""

import asyncio
import json
from unittest.mock import patch, MagicMock
from weaver_server import WeaverServer
from models import WeaverRequest

async def test_weaver_rate_limiting():
    """Test Weaver generation of rate limiting feature for authentication endpoint."""
    print("🕸️ Starting Weaver rate limiting test...")

    # Initialize Weaver
    weaver = WeaverServer()

    # Create the test request for rate limiting feature
    request = WeaverRequest(
        objective="Add rate limiting to authentication endpoint to prevent brute force attacks",
        context={
            "existing_auth": "Basic username/password authentication",
            "current_endpoints": "/api/auth/login, /api/auth/register",
            "framework": "FastAPI",
            "database": "PostgreSQL"
        },
        constraints=[
            "User should feel protected, not punished",
            "Maintain existing authentication patterns",
            "Include proper logging and monitoring",
            "Support both IP-based and user-based limiting"
        ],
        scope="authentication",
        patterns=[
            "API error responses with consistent format",
            "Database migrations with proper rollback",
            "Comprehensive test coverage"
        ]
    )

    print("📝 Generating rate limiting feature...")

    # Generate the cohesive code
    delta = await weaver.generate_cohesive_code(request)

    print("\n📊 GENERATION RESULTS:")
    print(f"Cohesion Score: {delta.cohesion_score}")
    print(f"Directives Applied: {', '.join(delta.directives_applied) if delta.directives_applied else 'None'}")
    print(f"Files Generated: {len(delta.files)}")

    # Check for full-stack generation
    has_backend = any('api' in path.lower() or 'handler' in path.lower() for path in delta.files.keys())
    has_frontend = any('frontend' in path.lower() or 'component' in path.lower() for path in delta.files.keys())
    has_tests = any('test' in path.lower() for path in delta.files.keys())
    has_migration = any('migration' in path.lower() or 'schema' in path.lower() for path in delta.files.keys())

    print("\n🔍 FULL-STACK VERIFICATION:")
    print(f"✅ Backend API: {'Yes' if has_backend else 'No'}")
    print(f"✅ Frontend Integration: {'Yes' if has_frontend else 'No'}")
    print(f"✅ Tests: {'Yes' if has_tests else 'No'}")
    print(f"✅ Database Migration: {'Yes' if has_migration else 'No'}")

    # Check cohesion score
    cohesion_ok = delta.cohesion_score and delta.cohesion_score > 0.8
    print(f"✅ High Cohesion Score (>0.8): {'Yes' if cohesion_ok else 'No'}")

    # Check manifest
    if delta.manifest:
        print("\n📋 FEATURE MANIFEST:")
        print(f"Feature: {delta.manifest.get('feature', 'Unknown')}")
        components = delta.manifest.get('components', [])
        print(f"Components: {len(components)}")
        for comp in components:
            print(f"  - {comp.get('name', 'Unknown')}: {comp.get('type', 'Unknown')} (risk: {comp.get('risk', 'Unknown')})")

    # Check for authentication Prime Directive compliance
    auth_directives = [d for d in delta.directives_applied if 'auth' in d.lower() or 'security' in d.lower()]
    print(f"✅ Authentication Directives: {'Yes' if auth_directives else 'No'}")

    # Check for emotional calibration (extra safeguards for auth)
    rationale_lower = delta.rationale.lower()
    has_extra_safeguards = any(word in rationale_lower for word in ['extra', 'safeguard', 'defensive', 'validation'])
    print(f"✅ Extra Safeguards for Auth: {'Yes' if has_extra_safeguards else 'No'}")

    # Overall test result
    full_stack_score = sum([has_backend, has_frontend, has_tests, has_migration, cohesion_ok])
    test_passed = full_stack_score >= 4  # At least 4/5 criteria met

    print("\n🎯 TEST RESULT:")
    print(f"Full-Stack Score: {full_stack_score}/5")
    print(f"Overall: {'✅ PASSED' if test_passed else '❌ FAILED'}")

    if test_passed:
        print("\n🎉 SUCCESS: Weaver generated cohesive full-stack rate limiting!")
        print("The Ghost now has phantom limbs - it reaches into every layer.")
    else:
        print("\n⚠️ PARTIAL: Weaver needs refinement for complete full-stack generation.")

    # Show sample generated code
    if delta.files:
        sample_file = list(delta.files.keys())[0]
        print(f"\n📄 Sample Generated Code ({sample_file}):")
        print(delta.files[sample_file][:500] + "..." if len(delta.files[sample_file]) > 500 else delta.files[sample_file])

    print("\n🕸️ Weaver test complete!")

if __name__ == "__main__":
    asyncio.run(test_weaver_rate_limiting())