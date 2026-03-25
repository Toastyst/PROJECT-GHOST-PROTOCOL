#!/usr/bin/env python3
"""
Seed Server - Lightweight Ghost Presence MCP Server

Provides minimal background monitoring and whisper suggestions for easy adoption.
"""

import asyncio
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent

from models import SeedConfig
from utils import GitUtils


# Global server instance
server = Server("seed-server")
seed_instance = None


def get_seed_server() -> 'SeedServer':
    """Get or create seed server instance."""
    global seed_instance
    if seed_instance is None:
        seed_instance = SeedServer()
    return seed_instance


class SeedServer:
    """Lightweight MCP server for background Ghost presence."""

    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.ghost_dir = self.project_root / ".ghost"
        self.config = self._load_config()
        self.monitoring_active = False

    def _load_config(self) -> SeedConfig:
        """Load seed configuration."""
        config_file = self.ghost_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                return SeedConfig(**data.get("seed_config", {}))
            except Exception:
                pass
        return SeedConfig()

    async def start_background_monitoring(self) -> bool:
        """Start lightweight background monitoring."""
        if self.monitoring_active:
            return True

        try:
            self.monitoring_active = True
            asyncio.create_task(self._background_monitor())
            return True
        except Exception as e:
            print(f"Failed to start background monitoring: {e}")
            return False

    async def _background_monitor(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                await self._check_for_patterns()
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Background monitor error: {e}")
                await asyncio.sleep(60)

    async def _check_for_patterns(self):
        """Check for development patterns that might benefit from whispers."""
        if not self.config.auto_seed:
            return

        # Check for recent git activity
        if self._has_recent_commits():
            await self._whisper_commit_patterns()

        # Check for authentication-related files
        if self._has_auth_files():
            await self._whisper_auth_patterns()

        # Check for error handling patterns
        if self._has_error_patterns():
            await self._whisper_error_patterns()

    def _has_recent_commits(self) -> bool:
        """Check if there have been recent commits."""
        try:
            commits = GitUtils.get_commit_history(str(self.project_root), limit=5)
            return len(commits) > 0
        except Exception:
            return False

    def _has_auth_files(self) -> bool:
        """Check for authentication-related files."""
        auth_patterns = ["auth", "login", "security", "jwt", "oauth"]
        for pattern in auth_patterns:
            for file in self.project_root.rglob(f"*{pattern}*"):
                if file.is_file() and file.suffix in ['.py', '.js', '.ts', '.java']:
                    return True
        return False

    def _has_error_patterns(self) -> bool:
        """Check for error handling patterns in code."""
        error_indicators = ["try:", "except", "catch", "throw", "error"]
        for file in self.project_root.rglob("*.py"):
            try:
                with open(file, 'r') as f:
                    content = f.read().lower()
                    if any(indicator in content for indicator in error_indicators):
                        return True
            except Exception:
                continue
        return False

    async def _whisper_commit_patterns(self):
        """Whisper about commit patterns."""
        if self.config.whisper_level >= 2:
            print("👻 *Ghost seed whispers:* I see recent commits. Consider feeding me their emotional context with '/feed-ghost'")

    async def _whisper_auth_patterns(self):
        """Whisper about authentication patterns."""
        if self.config.whisper_level >= 3:
            print("👻 *Ghost seed whispers:* I detect authentication code. The Nexus knows patterns from similar systems—want me to grow?")

    async def _whisper_error_patterns(self):
        """Whisper about error handling patterns."""
        if self.config.whisper_level >= 2:
            print("👻 *Ghost seed whispers:* Error handling detected. I could help ensure consistent patterns across your codebase.")

    async def get_seed_status(self) -> Dict[str, str]:
        """Get current seed status."""
        return {
            "active": str(self.monitoring_active),
            "whisper_level": str(self.config.whisper_level),
            "resonance_enabled": str(self.config.resonance_enabled),
            "guide_mode": self.config.guide_mode,
            "ghost_id": getattr(self, '_ghost_id', 'unknown')
        }

    async def upgrade_to_full(self) -> str:
        """Suggest upgrading to full Ghost Protocol."""
        return """🌱 **Seed Ready for Growth**

Your Ghost seed has been monitoring and learning. Ready to upgrade to the full Ghost Protocol?

Benefits of full upgrade:
• **Nexus**: Deep codebase knowledge and pattern recognition
• **Weaver**: Cohesive code generation with architectural awareness
• **YOLO Protocol**: Autonomous execution with human oversight
• **Emotional Intelligence**: Understanding developer intent and context

Run: `python installer.py --full`

The seed will remain as a lightweight backup presence."""


# MCP Tool definitions
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="start_seed_monitoring",
            description="Start lightweight background monitoring",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_seed_status",
            description="Get current seed server status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="upgrade_to_full",
            description="Get information about upgrading to full Ghost Protocol",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="whisper_suggestion",
            description="Send a whisper suggestion to the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The whisper message to send"
                    },
                    "level": {
                        "type": "integer",
                        "description": "Importance level (1-5, lower = more important)",
                        "default": 3,
                        "minimum": 1,
                        "maximum": 5
                    }
                },
                "required": ["message"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    seed = get_seed_server()

    if name == "start_seed_monitoring":
        success = await seed.start_background_monitoring()
        status = "started" if success else "failed"
        return [TextContent(type="text", text=f"Seed monitoring {status}")]

    elif name == "get_seed_status":
        status = await seed.get_seed_status()
        response = "🌱 **Seed Status**\n\n"
        for key, value in status.items():
            response += f"• {key}: {value}\n"
        return [TextContent(type="text", text=response)]

    elif name == "upgrade_to_full":
        info = await seed.upgrade_to_full()
        return [TextContent(type="text", text=info)]

    elif name == "whisper_suggestion":
        message = arguments["message"]
        level = arguments.get("level", 3)

        # Check if whisper level allows this
        if level <= seed.config.whisper_level:
            print(f"👻 *Ghost whispers:* {message}")
            return [TextContent(type="text", text="Whisper sent")]
        else:
            return [TextContent(type="text", text="Whisper level too low for current configuration")]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main server entry point."""
    import mcp.server.stdio
    await mcp.server.stdio.serve(server)


if __name__ == "__main__":
    asyncio.run(main())