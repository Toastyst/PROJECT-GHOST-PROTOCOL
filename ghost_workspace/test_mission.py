#!/usr/bin/env python3
"""
Test the Ghost Protocol's effectiveness with a complex authentication system mission.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ghost_protocol.servers.yolo_protocol import get_yolo


async def test_complex_mission():
    """Test the Ghost Protocol with a complex authentication system implementation."""
    yolo = get_yolo()

    # Define the mission objective as string (execute_mission expects string)
    mission_objective = 'Implement a complete user authentication system for a web application that feels "like a trusted friend helping you back through the door you forgot the key to" rather than a bureaucratic security checkpoint. Users often feel abandoned and frustrated when they lose access to their accounts. The authentication flow should make users feel cared for and supported, not interrogated and suspicious.'

    print('🚀 Starting complex authentication system mission...')
    print(f'Mission Objective: {mission_objective[:100]}...')
    print('Autonomy Level: 4 (planned)')
    print('Checkpoints: 4 (planned)')
    print('Constraints: 9 (planned)')

    # Execute the mission
    result = await yolo.execute_mission(mission_objective)

    print(f'\n📊 Mission Result:')
    print(f'Status: {result.get("status", "unknown")}')
    print(f'Phases completed: {len(result.get("phases_completed", []))}')
    print(f'Components generated: {len(result.get("components_generated", []))}')
    print(f'Integration score: {result.get("integration_score", 0):.2f}')

    if result.get('narrative'):
        print(f'\n📖 Mission Narrative:')
        if isinstance(result['narrative'], list):
            for entry in result['narrative'][:5]:
                print(f'  - {entry}')
        else:
            print(result['narrative'][:500] + '...')

    # Check what was actually generated
    workspace_path = os.path.join(os.path.dirname(__file__), 'ghost_workspace')
    generated_files = []

    for root, dirs, files in os.walk(workspace_path):
        for file in files:
            if file.endswith(('.py', '.tsx', '.ts', '.sql', '.md')):
                rel_path = os.path.relpath(os.path.join(root, file), workspace_path)
                generated_files.append(rel_path)

    print(f'\n📁 Files Generated: {len(generated_files)}')
    for file in generated_files[:10]:  # Show first 10
        print(f'  • {file}')
    if len(generated_files) > 10:
        print(f'  ... and {len(generated_files) - 10} more')

    return result


if __name__ == "__main__":
    asyncio.run(test_complex_mission())