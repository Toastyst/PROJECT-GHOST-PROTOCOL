#!/usr/bin/env python3
"""
Hooks Server - Hook Integration for the Iteration Protocol

Provides MCP server for managing Git hooks and other development lifecycle
hooks that reflect intention rather than enforce rules.
"""

import asyncio
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent

from src.ghost_protocol.models.models import HookConfig, IterationEvent
from src.ghost_protocol.engines.skills_engine import get_skills_engine
from src.ghost_protocol.engines.rules_engine import get_rules_engine


# Global server instance
server = Server("hooks-server")
hooks_instance = None


def get_hooks_server() -> 'HooksServer':
    """Get or create hooks server instance."""
    global hooks_instance
    if hooks_instance is None:
        hooks_instance = HooksServer()
    return hooks_instance


class HooksServer:
    """MCP server for hook integration and reflection management."""

    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.ghost_dir = self.project_root / ".ghost"
        self.git_hooks_dir = self.project_root / ".git" / "hooks"
        self.config_file = self.ghost_dir / "config.json"
        self.skills_engine = get_skills_engine()
        self.rules_engine = get_rules_engine()
        self.active_hooks = {}

    def load_config(self) -> Dict[str, Any]:
        """Load hook configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"hook_config": {"enabled": True, "reflection_mode": "question"}}

    async def install_git_hooks(self, repo_path: Optional[str] = None) -> bool:
        """Install Git hooks for reflection."""
        target_path = Path(repo_path) if repo_path else self.project_root
        git_hooks_dir = target_path / ".git" / "hooks"

        if not git_hooks_dir.exists():
            return False

        try:
            # Install pre-commit hook
            pre_commit_src = self.project_root / "git_hooks" / "pre-commit-ghost"
            pre_commit_dst = git_hooks_dir / "pre-commit"

            if pre_commit_src.exists():
                # Copy and make executable
                with open(pre_commit_src, 'r') as src:
                    content = src.read()
                with open(pre_commit_dst, 'w') as dst:
                    dst.write(content)
                pre_commit_dst.chmod(0o755)

            # Install pre-push hook
            pre_push_src = self.project_root / "git_hooks" / "pre-push-ghost"
            pre_push_dst = git_hooks_dir / "pre-push"

            if pre_push_src.exists():
                with open(pre_push_src, 'r') as src:
                    content = src.read()
                with open(pre_push_dst, 'w') as dst:
                    dst.write(content)
                pre_push_dst.chmod(0o755)

            return True
        except Exception as e:
            print(f"Failed to install Git hooks: {e}")
            return False

    async def trigger_hook_reflection(self, hook_type: str, context: Dict[str, Any]) -> str:
        """Generate reflective response for a hook trigger."""
        config = self.load_config()
        mode = config.get("hook_config", {}).get("reflection_mode", "question")

        # Evaluate rules compliance first
        rule_check = await self.rules_engine.evaluate_rule_compliance(
            "presence", "hook_trigger", context
        )

        if not rule_check["compliant"] and rule_check["severity"] == "high":
            return "🤔 Hook paused for reflection on presence boundaries."

        # Check if skills should activate
        skills_context = context.copy()
        skills_context["text"] = context.get("commit_message", "")
        skills_context["file_path"] = context.get("files", [""])[0] if context.get("files") else ""

        listening_response = await self.skills_engine.activate_skill("listening", skills_context)
        if listening_response and listening_response.get("response"):
            return listening_response["response"]

        pattern_response = await self.skills_engine.activate_skill("pattern", skills_context)
        if pattern_response and pattern_response.get("response"):
            return pattern_response["response"]

        # Default reflection based on hook type
        if hook_type == "pre-commit":
            return self._generate_commit_reflection(context, mode)
        elif hook_type == "pre-push":
            return self._generate_push_reflection(context, mode)
        elif hook_type == "pr":
            return self._generate_pr_reflection(context, mode)
        elif hook_type == "deploy":
            return self._generate_deploy_reflection(context, mode)
        else:
            return f"🤔 {hook_type} triggered. What threshold are you crossing?"

    def _generate_commit_reflection(self, context: Dict[str, Any], mode: str) -> str:
        """Generate commit-specific reflection."""
        files = context.get("files", [])
        file_count = len(files)
        commit_message = context.get("commit_message", "")

        # Check for emotional keywords in commit message
        emotional_keywords = ["frustrating", "emotional", "feel", "angry", "happy", "worried", "excited"]
        has_emotional_content = any(keyword in commit_message.lower() for keyword in emotional_keywords)

        if mode == "mirror":
            reflection = f"👁️  {file_count} file{'s' if file_count != 1 else ''} prepare to join the codebase."
            if any('.py' in f for f in files):
                reflection += " Code will run in new contexts."
            if any('test' in f.lower() for f in files):
                reflection += " Tests will protect against future changes."
            if has_emotional_content:
                reflection += " These changes carry emotional weight. What feelings drive this work?"
            else:
                reflection += " What story do these changes tell?"
        elif mode == "pause":
            reflection = "⏸️  Before these changes become permanent...\n"
            reflection += "Feel their weight. Consider their impact.\n"
            if has_emotional_content:
                reflection += "These changes seem to carry emotional significance. What feelings are you working through?\n"
            reflection += "What will the codebase be like with these changes?\n"
            reflection += "What will you learn from making them?"
        else:  # question
            questions = []
            if file_count > 5:
                questions.append("Many files change together. What larger purpose unites them?")
            elif file_count == 1:
                questions.append("One focused change. What specific problem does it solve?")
            if any('config' in f.lower() for f in files):
                questions.append("Configuration changes ripple outward. Who feels this change?")
            if has_emotional_content:
                questions.append("This commit message suggests emotional investment. What feelings are you processing through code?")
            if not questions:
                questions.append("Every commit is a choice. What makes this choice yours?")
            reflection = "🤔 " + " ".join(questions)

        return reflection

    def _generate_push_reflection(self, context: Dict[str, Any], mode: str) -> str:
        """Generate push-specific reflection."""
        commits = context.get("commits", [])
        commit_count = len(commits)

        if mode == "mirror":
            reflection = f"👁️  {commit_count} commit{'s' if commit_count != 1 else ''} prepare to join the shared repository."
            reflection += " Others will see your work. Your thinking will influence theirs."
            reflection += " What do you want them to learn from this?"
        elif mode == "pause":
            reflection = "⏸️  These commits will leave your local space.\n"
            reflection += "They will become part of the team's shared history.\n"
            reflection += "What precedent are you setting? What example are you giving?\n"
            reflection += "How will this shape how others work?"
        else:  # question
            questions = []
            if commit_count > 3:
                questions.append("Several commits push together. What journey do they represent?")
            questions.append("This work will be reviewed and built upon. What foundation are you providing?")
            if context.get("remote_info", "").lower().find("origin") >= 0:
                questions.append("Pushing to the heart of the project. What trust are you placing there?")
            reflection = "🤔 " + " ".join(questions)

        return reflection

    def _generate_pr_reflection(self, context: Dict[str, Any], mode: str) -> str:
        """Generate PR-specific reflection."""
        if mode == "mirror":
            reflection = "👁️  This work seeks to join the main branch."
            reflection += " It will be reviewed, discussed, and either accepted or rejected."
            reflection += " What conversation do you hope to start?"
        elif mode == "pause":
            reflection = "⏸️  Before others review your work...\n"
            reflection += "Consider what you're asking of them.\n"
            reflection += "What do you need from their perspective?\n"
            reflection += "What perspective are you offering them?"
        else:  # question
            questions = [
                "This PR will be reviewed by others. What do you want them to understand?",
                "What feedback are you seeking? What resistance do you anticipate?",
                "How does this change serve the project's larger goals?"
            ]
            reflection = "🤔 " + " ".join(questions)

        return reflection

    def _generate_deploy_reflection(self, context: Dict[str, Any], mode: str) -> str:
        """Generate deployment-specific reflection."""
        if mode == "mirror":
            reflection = "👁️  This code will soon serve real users."
            reflection += " It will affect lives, solve problems, or create new ones."
            reflection += " What responsibility comes with this deployment?"
        elif mode == "pause":
            reflection = "⏸️  Before this code goes live...\n"
            reflection += "Consider who it will serve and who it might harm.\n"
            reflection += "What assumptions have you made about your users?\n"
            reflection += "What will you learn from their reactions?"
        else:  # question
            questions = [
                "This deployment affects real people. What impact do you hope to have?",
                "What metrics will tell you if this deployment succeeded?",
                "What will you do if the deployment reveals problems you didn't anticipate?"
            ]
            reflection = "🤔 " + " ".join(questions)

        return reflection

    async def get_hook_status(self) -> Dict[str, Any]:
        """Get current hook status and configuration."""
        config = self.load_config()
        hook_config = config.get("hook_config", {})

        # Check if hooks are installed
        hooks_installed = {}
        if self.git_hooks_dir.exists():
            hooks_installed["pre-commit"] = (self.git_hooks_dir / "pre-commit").exists()
            hooks_installed["pre-push"] = (self.git_hooks_dir / "pre-push").exists()

        return {
            "enabled": hook_config.get("enabled", True),
            "reflection_mode": hook_config.get("reflection_mode", "question"),
            "hooks_installed": hooks_installed,
            "active_hooks": list(self.active_hooks.keys())
        }

    async def configure_hook(self, hook_type: str, settings: Dict[str, Any]) -> bool:
        """Configure a specific hook."""
        try:
            config = self.load_config()
            if "hook_config" not in config:
                config["hook_config"] = {}

            # Update settings
            for key, value in settings.items():
                if key in ["enabled", "reflection_mode"]:
                    config["hook_config"][key] = value

            # Save config
            os.makedirs(self.ghost_dir, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

            return True
        except Exception as e:
            print(f"Failed to configure hook: {e}")
            return False


# MCP Tool definitions
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="install_git_hooks",
            description="Install Git hooks for reflection at development thresholds",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to repository (optional, defaults to current)"
                    }
                }
            }
        ),
        Tool(
            name="get_hook_status",
            description="Get current hook configuration and installation status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="configure_hook",
            description="Configure hook settings",
            inputSchema={
                "type": "object",
                "properties": {
                    "hook_type": {
                        "type": "string",
                        "description": "Type of hook to configure",
                        "enum": ["pre-commit", "pre-push", "pr", "deploy"]
                    },
                    "settings": {
                        "type": "object",
                        "description": "Settings to update",
                        "properties": {
                            "enabled": {"type": "boolean"},
                            "reflection_mode": {
                                "type": "string",
                                "enum": ["mirror", "question", "pause"]
                            }
                        }
                    }
                },
                "required": ["hook_type", "settings"]
            }
        ),
        Tool(
            name="trigger_hook_reflection",
            description="Manually trigger a hook reflection for testing",
            inputSchema={
                "type": "object",
                "properties": {
                    "hook_type": {
                        "type": "string",
                        "description": "Type of hook to trigger",
                        "enum": ["pre-commit", "pre-push", "pr", "deploy"]
                    },
                    "context": {
                        "type": "object",
                        "description": "Context for the hook trigger"
                    }
                },
                "required": ["hook_type", "context"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    hooks = get_hooks_server()

    if name == "install_git_hooks":
        repo_path = arguments.get("repo_path")
        success = await hooks.install_git_hooks(repo_path)
        status = "installed" if success else "failed"
        return [TextContent(type="text", text=f"Git hooks {status}")]

    elif name == "get_hook_status":
        status = await hooks.get_hook_status()
        response = "🔗 **Hook Status**\n\n"
        response += f"• Enabled: {status['enabled']}\n"
        response += f"• Reflection Mode: {status['reflection_mode']}\n"
        response += f"• Hooks Installed: {status['hooks_installed']}\n"
        response += f"• Active Hooks: {status['active_hooks']}\n"
        return [TextContent(type="text", text=response)]

    elif name == "configure_hook":
        hook_type = arguments["hook_type"]
        settings = arguments["settings"]
        success = await hooks.configure_hook(hook_type, settings)
        status = "configured" if success else "failed"
        return [TextContent(type="text", text=f"Hook {hook_type} {status}")]

    elif name == "trigger_hook_reflection":
        hook_type = arguments["hook_type"]
        context = arguments.get("context", {})
        reflection = await hooks.trigger_hook_reflection(hook_type, context)
        return [TextContent(type="text", text=reflection)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main server entry point."""
    import mcp.server.stdio
    await mcp.server.stdio.serve(server)


if __name__ == "__main__":
    asyncio.run(main())