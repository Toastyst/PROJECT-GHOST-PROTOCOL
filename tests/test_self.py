#!/usr/bin/env python3
"""
Self-test script for Nexus server - ingests this project and queries for riskiest parts.
"""

import asyncio
import os
from src.ghost_protocol.servers.nexus_server import NexusServer

async def test_nexus():
    """Test Nexus ingestion and constellation querying."""
    print("🔍 Starting Nexus self-test...")

    # Initialize Nexus
    nexus = NexusServer()

    # Ingest this project
    repo_path = os.getcwd()
    print(f"📥 Ingesting codebase from: {repo_path}")

    success = await nexus.ingest_codebase(repo_path)
    if not success:
        print("❌ Ingestion failed!")
        return

    print("✅ Ingestion successful!")

    # Query for riskiest part
    print("\n🔮 Querying for riskiest system component...")
    constellation = await nexus.query_nexus_constellation("What's the riskiest part of this system?")

    print(f"\n📊 CONSTELLATION ANALYSIS RESULTS:")
    print(f"Query: {constellation['query']}")
    print(f"Emotional Charge: {constellation['emotional_charge']}")
    print(f"Canonical Location: {constellation['canonical_location'] or 'Not found'}")

    if constellation['red_flags']:
        print(f"\n🚩 RED FLAGS ({len(constellation['red_flags'])}):")
        for flag in constellation['red_flags']:
            print(f"  - {flag['type'].upper()}: {flag['description']}")
            if 'location' in flag:
                print(f"    Location: {flag['location']}")

    if constellation['resonance_summary']['institutional_knowledge_gaps']:
        print(f"\n🧠 INSTITUTIONAL KNOWLEDGE GAPS:")
        for gap in constellation['resonance_summary']['institutional_knowledge_gaps']:
            print(f"  - {gap['file']}: {gap['primary_author']} ({gap['risk']})")

    if constellation['runbook_suggestions']:
        print(f"\n📋 RUNBOOK SUGGESTIONS:")
        for suggestion in constellation['runbook_suggestions']:
            print(f"  - {suggestion}")

    if constellation['related_insights']:
        print(f"\n💡 HIGH-RESONANCE INSIGHTS ({len(constellation['related_insights'])}):")
        for insight in constellation['related_insights'][:3]:
            print(f"  - {insight['type']}: {insight['content'][:100]}... (resonance: {insight['resonance']})")

    # Check if YOLO protocol is identified as high risk
    yolo_mentioned = any('yolo' in str(insight).lower() for insight in constellation['related_insights'])
    if yolo_mentioned:
        print("\n✅ SUCCESS: YOLO Protocol identified as high-risk component!")
    else:
        print("\n❌ FAILURE: YOLO Protocol not identified as high-risk component")

    print("\n🎯 Self-test complete!")

if __name__ == "__main__":
    asyncio.run(test_nexus())