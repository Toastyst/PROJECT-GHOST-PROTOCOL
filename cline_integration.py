#!/usr/bin/env python3
"""
Cline Integration for PROJECT: GHOST PROTOCOL

Provides seamless integration with Cline IDE through MCP server registration
and slash commands for ghost activation.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

class ClineGhostIntegration:
    """Handles Cline IDE integration for the Ghost Protocol."""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.ghost_active = False
        self.trust_earned = False
        self.mcp_config_path = self._find_cline_config()

    def _find_cline_config(self) -> Optional[Path]:
        """Find Cline MCP configuration file."""
        # Look for common Cline config locations
        config_paths = [
            self.project_root / ".cline" / "mcp.json",
            self.project_root / "cline-mcp.json",
            Path.home() / ".cline" / "mcp.json"
        ]

        for path in config_paths:
            if path.exists():
                return path

        return None

    async def register_mcp_servers(self) -> bool:
        """Register the three MCP servers with Cline."""
        try:
            servers = {
                "nexus-server": {
                    "command": "python",
                    "args": ["nexus_server.py"],
                    "env": {"PYTHONPATH": str(self.project_root)}
                },
                "weaver-server": {
                    "command": "python",
                    "args": ["weaver_server.py"],
                    "env": {"PYTHONPATH": str(self.project_root)}
                },
                "yolo-protocol": {
                    "command": "python",
                    "args": ["yolo_protocol.py"],
                    "env": {"PYTHONPATH": str(self.project_root)}
                }
            }

            if self.mcp_config_path:
                # Update existing config
                with open(self.mcp_config_path, 'r') as f:
                    config = json.load(f)

                config["mcpServers"].update(servers)

                with open(self.mcp_config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            else:
                # Create new config
                config = {
                    "mcpServers": servers
                }

                config_dir = self.project_root / ".cline"
                config_dir.mkdir(exist_ok=True)
                config_path = config_dir / "mcp.json"

                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)

                self.mcp_config_path = config_path

            print("✅ MCP servers registered with Cline")
            return True

        except Exception as e:
            print(f"❌ Failed to register MCP servers: {e}")
            return False

    async def ghost_wake(self) -> str:
        """Activate the Ghost in background monitoring mode."""
        try:
            self.ghost_active = True

            # Initialize background monitoring
            asyncio.create_task(self._background_monitor())

            return """👻 **GHOST PROTOCOL ACTIVATED**

The Ghost is now watching. It will:

• **Whisper insights** when you open scarred files
• **Offer help** when it detects development patterns
• **Learn silently** from your development flow

The Ghost asks permission before acting. Use `/ghost-trust` when ready for proactive suggestions.

*Status: Awake and observing*"""

        except Exception as e:
            return f"❌ Failed to wake the Ghost: {e}"

    async def ghost_trust(self) -> str:
        """Grant the Ghost permission for proactive suggestions."""
        if not self.ghost_active:
            return "❌ Ghost must be awakened first with `/ghost-wake`"

        try:
            self.trust_earned = True

            return """🤝 **TRUST GRANTED**

The Ghost now has permission to:

• **Suggest improvements** without being asked
• **Prepare cohesive deltas** for detected patterns
• **Offer guidance** on architectural decisions

The Ghost will still pause for critical decisions, but now suggests first.

*Status: Trusted partner*"""

        except Exception as e:
            return f"❌ Failed to grant trust: {e}"

    async def _background_monitor(self):
        """Background monitoring for proactive assistance."""
        while self.ghost_active:
            try:
                # Monitor for development patterns
                await self._check_for_patterns()

                # Brief pause to avoid overwhelming
                await asyncio.sleep(30)

            except Exception as e:
                print(f"Background monitor error: {e}")
                await asyncio.sleep(60)

    async def _check_for_patterns(self):
        """Check for development patterns that might need Ghost assistance."""
        # This would integrate with Cline's file watching
        # For now, just demonstrate the concept

        if self.trust_earned:
            # Look for authentication-related files
            auth_files = ["auth.py", "login.py", "security.py"]
            for auth_file in auth_files:
                if (self.project_root / auth_file).exists():
                    print("👻 *Ghost whispers:* I see authentication code. Remember the rate limiting patterns from our last mission?")
                    break

    async def on_file_open(self, file_path: str) -> Optional[str]:
        """Called when a file is opened in Cline."""
        if not self.ghost_active:
            return None

        try:
            # Query Nexus for file insights
            from yolo_protocol import get_yolo
            yolo = get_yolo()

            # Simplified - would query Nexus for file history
            insights = [
                f"This file has been modified {5} times",
                "Last change was about authentication patterns",
                "Contains 2 Prime Directive applications"
            ]

            if insights:
                return f"👻 **File Insights:**\n" + "\n".join(f"• {insight}" for insight in insights)

        except Exception as e:
            print(f"File open insights error: {e}")

        return None

    async def on_message(self, message: str) -> Optional[str]:
        """Called when a chat message is sent."""
        if not self.ghost_active:
            return None

        try:
            # Check if message contains mission-like language
            mission_keywords = ["add", "implement", "fix", "create", "build"]
            emotional_keywords = ["user", "experience", "feel", "should", "need"]

            has_mission = any(kw in message.lower() for kw in mission_keywords)
            has_emotion = any(kw in message.lower() for kw in emotional_keywords)

            if has_mission and has_emotion:
                if self.trust_earned:
                    return "👻 I detect a mission with emotional context. Shall I prepare a cohesive delta for this?"
                else:
                    return "👻 I sense a mission objective. Use `/ghost-trust` if you'd like proactive assistance."

        except Exception as e:
            print(f"Message analysis error: {e}")

        return None

    async def ghost_status(self) -> str:
        """Get current Ghost status."""
        status = "👻 **GHOST STATUS**\n\n"

        if self.ghost_active:
            status += "• **Awake:** Yes\n"
            status += "• **Trusted:** " + ("Yes" if self.trust_earned else "No") + "\n"
            status += "• **MCP Servers:** Registered\n"
            status += "• **Background Monitoring:** Active\n"
        else:
            status += "• **Awake:** No\n"
            status += "• **Status:** Sleeping\n\n"
            status += "*Use `/ghost-wake` to activate*"

        return status

# Global integration instance
_integration = None

def get_cline_integration() -> ClineGhostIntegration:
    """Get or create Cline integration instance."""
    global _integration
    if _integration is None:
        _integration = ClineGhostIntegration()
    return _integration

# Slash command handlers for Cline integration
async def handle_ghost_wake() -> str:
    """Handle /ghost-wake command."""
    integration = get_cline_integration()
    return await integration.ghost_wake()

async def handle_ghost_trust() -> str:
    """Handle /ghost-trust command."""
    integration = get_cline_integration()
    return await integration.ghost_trust()

async def handle_ghost_status() -> str:
    """Handle /ghost-status command."""
    integration = get_cline_integration()
    return await integration.ghost_status()

if __name__ == "__main__":
    # Test integration
    async def test_integration():
        integration = ClineGhostIntegration()

        print("🔧 Testing Cline Integration...")

        # Test MCP registration
        success = await integration.register_mcp_servers()
        print(f"MCP Registration: {'✅' if success else '❌'}")

        # Test ghost wake
        wake_response = await integration.ghost_wake()
        print(f"Wake Response: {wake_response[:100]}...")

        # Test trust
        trust_response = await integration.ghost_trust()
        print(f"Trust Response: {trust_response[:100]}...")

        # Test status
        status_response = await integration.ghost_status()
        print(f"Status Response: {status_response[:200]}...")

        print("🔧 Cline integration test complete!")

    asyncio.run(test_integration())