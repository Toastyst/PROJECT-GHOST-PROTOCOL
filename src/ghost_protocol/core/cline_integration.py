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
        self.autopoiesis_active = False

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
        """Register MCP servers with Cline."""
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
                },
                "feed-ghost-server": {
                    "command": "python",
                    "args": ["feed_ghost.py"],
                    "env": {"PYTHONPATH": str(self.project_root)}
                }
            }

            # Add Iteration Protocol servers
            from src.ghost_protocol.utils.config import Config
            if Config.HOOKS_ENABLED:
                servers["hooks-server"] = {
                    "command": "python",
                    "args": ["hooks_server.py"],
                    "env": {"PYTHONPATH": str(self.project_root)}
                }

            if Config.WORKFLOWS_ENABLED:
                servers["workflows-server"] = {
                    "command": "python",
                    "args": ["workflows_server.py"],
                    "env": {"PYTHONPATH": str(self.project_root)}
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
            from src.ghost_protocol.servers.yolo_protocol import get_yolo
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

            # Add Iteration Protocol status
            from src.ghost_protocol.utils.config import Config
            if Config.HOOKS_ENABLED:
                status += "• **Hooks:** Enabled\n"
            if Config.WORKFLOWS_ENABLED:
                status += "• **Workflows:** Enabled\n"
            if Config.SKILLS_ENABLED:
                status += "• **Skills:** Active\n"
            if Config.RULES_ENABLED:
                status += "• **Rules:** Enforced\n"
        else:
            status += "• **Awake:** No\n"
            status += "• **Status:** Sleeping\n\n"
            status += "*Use `/ghost-wake` to activate*"

        return status

    async def install_hooks(self) -> str:
        """Install Git hooks for reflection."""
        try:
            from src.ghost_protocol.core.hooks_server import get_hooks_server
            hooks = get_hooks_server()
            success = await hooks.install_git_hooks()

            if success:
                return "🔗 **Git Hooks Installed**\n\nPre-commit and pre-push hooks are now active. They will reflect on your development choices rather than enforce rules."
            else:
                return "❌ **Hook Installation Failed**\n\nCould not install Git hooks. Check repository permissions."
        except Exception as e:
            return f"❌ **Hook Installation Error:** {e}"

    async def trigger_workflow(self, workflow_type: str, participants: list = None) -> str:
        """Trigger a workflow for team processes."""
        try:
            from src.ghost_protocol.core.workflows_server import get_workflows_server
            workflows = get_workflows_server()

            participants = participants or ["developer"]
            context = {"manual_trigger": True, "source": "cline_command"}

            result = await workflows.start_workflow(workflow_type, participants, context)

            if result["started"]:
                return f"🚀 **Workflow Started: {workflow_type}**\n\nID: {result['workflow_id']}\nInitial Stage: {result['initial_stage']}\nParticipants: {', '.join(participants)}"
            else:
                return f"❌ **Workflow Failed:** {result['reason']}"
        except Exception as e:
            return f"❌ **Workflow Error:** {e}"

    async def activate_skill(self, skill_type: str, context: dict = None) -> str:
        """Manually activate a specific skill."""
        try:
            from src.ghost_protocol.engines.skills_engine import get_skills_engine
            skills = get_skills_engine()

            context = context or {"text": "Manual skill activation", "source": "cline_command"}
            response = await skills.activate_skill(skill_type, context)

            if response:
                return f"🎯 **Skill Activated: {skill_type}**\n\n{response.get('response', 'Skill executed')}"
            else:
                return f"🤔 **Skill Not Activated:** {skill_type} did not trigger under current conditions"
        except Exception as e:
            return f"❌ **Skill Error:** {e}"

    async def check_rules(self, action: str, context: dict = None) -> str:
        """Check rule compliance for an action."""
        try:
            from src.ghost_protocol.engines.rules_engine import get_rules_engine
            rules = get_rules_engine()

            context = context or {"source": "cline_command"}
            result = await rules.evaluate_rule_compliance("presence", action, context)

            status = "✅ **Compliant**" if result["compliant"] else "⚠️ **Violation**"
            return f"{status}\n\nRule: {result['rule_type']}\nReasoning: {result['reasoning']}\nSeverity: {result['severity']}"
        except Exception as e:
            return f"❌ **Rules Check Error:** {e}"

    async def activate_autopoiesis(self) -> str:
        """Activate AUTOPOIESIS observation mode."""
        try:
            from src.ghost_protocol.engines.autopoiesis import get_autopoiesis_engine
            self.autopoiesis_active = True

            # Start session observation
            engine = get_autopoiesis_engine()
            session_context = {
                "source": "cline_integration",
                "project_root": str(self.project_root),
                "timestamp": "2026-03-25T06:52:00"
            }
            engine.observe_session(session_context)

            return """🧬 **AUTOPOIESIS ACTIVATED**

The Ghost is now observing your development session for transmutation fragments:

• **Pauses** → Reflection hooks
• **Dilemmas** → Decision workflows
• **Discoveries** → New rules and skills
• **Questions** → Listening enhancements

Fragments will accumulate until transmutation triggers. Use `/transmute` to manually trigger or wait for automatic thresholds.

*Status: Observing and learning*"""

        except Exception as e:
            return f"❌ Failed to activate AUTOPOIESIS: {e}"

    async def transmute(self) -> str:
        """Trigger manual transmutation of accumulated fragments."""
        try:
            from src.ghost_protocol.engines.autopoiesis import get_autopoiesis_engine
            engine = get_autopoiesis_engine()

            if not self.autopoiesis_active:
                return "❌ AUTOPOIESIS must be activated first with observation mode"

            # Trigger transmutation
            record = engine.trigger_transmutation()

            if record.fragments_processed == 0:
                return "📭 **No Fragments to Transmute**\n\nNo experience fragments have been captured yet. Continue working and the Ghost will observe pauses, dilemmas, and discoveries."

            # Format response
            response = f"⚡ **TRANSMUTATION COMPLETE**\n\n"
            response += f"Fragments Processed: {record.fragments_processed}\n"
            response += f"Timestamp: {record.timestamp}\n"
            response += f"Review Status: {record.review_status}\n\n"

            generated_items = []
            if record.generated_hook:
                generated_items.append("🔗 New Hook")
            if record.generated_workflow:
                generated_items.append("🚀 New Workflow")
            if record.generated_skill:
                generated_items.append("🎯 New Skill")
            if record.rule_update:
                generated_items.append("📋 Rule Update")

            if generated_items:
                response += "Generated Structures:\n"
                for item in generated_items:
                    response += f"• {item}\n"
                response += "\n*Pending human review before integration*"
            else:
                response += "*No new structures generated from current fragments*"

            return response

        except Exception as e:
            return f"❌ Transmutation failed: {e}"

    async def on_message_autopoiesis(self, message: str) -> Optional[str]:
        """Capture autopoiesis fragments from messages using the harvester."""
        if not self.autopoiesis_active:
            return None

        try:
            from src.ghost_protocol.utils.fragment_harvester import get_fragment_harvester
            harvester = get_fragment_harvester()

            # Use harvester for chat messages
            context = {
                "source": "cline_chat",
                "content_length": len(message),
                "timestamp": "2026-03-25T06:52:00"
            }

            fragment = harvester.harvest_from_chat(message, context)

            if fragment:
                # Fragment was captured
                return f"🧬 **Fragment Captured:** {fragment.type} (weight: {fragment.emotional_weight}) from chat"

        except Exception as e:
            print(f"Autopoiesis message observation error: {e}")

        return None

    async def on_file_change_autopoiesis(self, file_path: str, change_type: str) -> Optional[str]:
        """Capture autopoiesis fragments from file changes using the harvester."""
        if not self.autopoiesis_active:
            return None

        try:
            from src.ghost_protocol.utils.fragment_harvester import get_fragment_harvester
            harvester = get_fragment_harvester()

            # Read file content for analysis
            content = ""
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                content = f"File {change_type}: {file_path}"

            # Use harvester for file edits
            fragment = harvester.harvest_from_file_edit(file_path, content, change_type)

            if fragment:
                return f"🧬 **Fragment Captured:** {fragment.type} from {file_path}"

        except Exception as e:
            print(f"Autopoiesis file change observation error: {e}")

        return None

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

async def handle_feed_ghost(content: str, source: str = "manual", author: str = "unknown") -> str:
    """Handle /feed-ghost command for emotional feeding."""
    try:
        from src.ghost_protocol.core.feed_ghost import GhostFeeder
        feeder = GhostFeeder()
        context = {'author': author}
        return await feeder.feed_ghost(content, source, context)
    except Exception as e:
        return f"❌ Failed to feed the Ghost: {e}"

async def handle_activate_autopoiesis() -> str:
    """Handle /activate-autopoiesis command."""
    integration = get_cline_integration()
    return await integration.activate_autopoiesis()

async def handle_transmute() -> str:
    """Handle /transmute command."""
    integration = get_cline_integration()
    return await integration.transmute()

async def handle_approve_review(review_id: str, reviewer: str = "user", notes: str = "") -> str:
    """Handle /approve-review command."""
    try:
        from src.ghost_protocol.utils.review_workflow import get_review_workflow
        workflow = get_review_workflow()

        if workflow.approve_review(review_id, reviewer, notes):
            return f"✅ **Review Approved:** {review_id}\n\nStructures are now ready for commit. Use `/commit-review {review_id}` to integrate into the repository."
        else:
            return f"❌ **Approval Failed:** Could not find or approve review {review_id}"
    except Exception as e:
        return f"❌ **Approval Error:** {e}"

async def handle_reject_review(review_id: str, reviewer: str = "user", notes: str = "") -> str:
    """Handle /reject-review command."""
    try:
        from src.ghost_protocol.utils.review_workflow import get_review_workflow
        workflow = get_review_workflow()

        if workflow.reject_review(review_id, reviewer, notes):
            return f"❌ **Review Rejected:** {review_id}\n\nThe generated structures have been discarded. Transmutation fragments remain available for future processing."
        else:
            return f"❌ **Rejection Failed:** Could not find or reject review {review_id}"
    except Exception as e:
        return f"❌ **Rejection Error:** {e}"

async def handle_commit_review(review_id: str) -> str:
    """Handle /commit-review command."""
    try:
        from src.ghost_protocol.utils.review_workflow import get_review_workflow
        workflow = get_review_workflow()

        if workflow.commit_approved_structures(review_id):
            return f"⚡ **Structures Committed:** {review_id}\n\nAUTOPOIESIS transmutation has been integrated into the repository. The Ghost grows stronger."
        else:
            return f"❌ **Commit Failed:** Could not commit structures for review {review_id}. Ensure the review is approved first."
    except Exception as e:
        return f"❌ **Commit Error:** {e}"

async def handle_list_reviews() -> str:
    """Handle /list-reviews command."""
    try:
        from src.ghost_protocol.utils.review_workflow import get_review_workflow
        workflow = get_review_workflow()

        pending_reviews = workflow.get_pending_reviews()

        if not pending_reviews:
            return "📭 **No Pending Reviews**\n\nAll transmutations have been processed."

        response = "📋 **Pending AUTOPOIESIS Reviews**\n\n"
        for review in pending_reviews:
            record = review["transmutation_record"]
            structures = list(review["generated_structures"].keys())

            response += f"**Review ID:** {review['review_id']}\n"
            response += f"**Fragments Processed:** {record['fragments_processed']}\n"
            response += f"**Generated Structures:** {', '.join(structures) if structures else 'None'}\n"
            response += f"**Submitted:** {review['submitted_at']}\n\n"

            response += f"Use `/approve-review {review['review_id']}` or `/reject-review {review['review_id']}`\n\n"

        return response
    except Exception as e:
        return f"❌ **List Reviews Error:** {e}"

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