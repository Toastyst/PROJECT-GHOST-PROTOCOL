#!/usr/bin/env python3
"""
Workflows Server - Workflow Orchestration for the Iteration Protocol

Provides MCP server for facilitating team workflows that build memory and connection
rather than enforcing processes.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent

from models import WorkflowConfig, IterationEvent
from skills_engine import get_skills_engine
from rules_engine import get_rules_engine


# Global server instance
server = Server("workflows-server")
workflows_instance = None


def get_workflows_server() -> 'WorkflowsServer':
    """Get or create workflows server instance."""
    global workflows_instance
    if workflows_instance is None:
        workflows_instance = WorkflowsServer()
    return workflows_instance


class WorkflowsServer:
    """MCP server for workflow orchestration and facilitation."""

    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.ghost_dir = self.project_root / ".ghost"
        self.workflows_dir = self.project_root / "workflow_templates"
        self.config_file = self.ghost_dir / "config.json"
        self.active_workflows = {}
        self.skills_engine = get_skills_engine()
        self.rules_engine = get_rules_engine()

    def load_config(self) -> Dict[str, Any]:
        """Load workflow configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"workflow_config": {"enabled": True, "facilitation_mode": "guided"}}

    async def load_workflow_template(self, workflow_type: str) -> Optional[Dict[str, Any]]:
        """Load a workflow template from file."""
        template_file = self.workflows_dir / f"{workflow_type}_workflow.json"
        if template_file.exists():
            try:
                with open(template_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    async def start_workflow(self, workflow_type: str, participants: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Start a workflow instance."""
        # Check rules compliance
        rule_check = await self.rules_engine.evaluate_rule_compliance(
            "presence", "workflow_start", context
        )

        if not rule_check["compliant"] and rule_check["severity"] == "high":
            return {
                "started": False,
                "reason": "Workflow blocked by presence rule violation",
                "rule_violation": rule_check["reasoning"]
            }

        # Load template
        template = await self.load_workflow_template(workflow_type)
        if not template:
            return {
                "started": False,
                "reason": f"Workflow template '{workflow_type}' not found"
            }

        # Check trigger conditions
        trigger_conditions = template.get("trigger_conditions", {})
        if not self._check_trigger_conditions(trigger_conditions, context):
            return {
                "started": False,
                "reason": "Trigger conditions not met"
            }

        # Create workflow instance
        workflow_id = f"{workflow_type}_{datetime.now().isoformat()}"
        workflow_instance = {
            "id": workflow_id,
            "type": workflow_type,
            "template": template,
            "participants": participants,
            "context": context,
            "current_stage": 0,
            "stage_history": [],
            "started_at": datetime.now().isoformat(),
            "status": "active"
        }

        self.active_workflows[workflow_id] = workflow_instance

        # Log event
        await self._log_workflow_event(workflow_id, "started", context)

        return {
            "started": True,
            "workflow_id": workflow_id,
            "initial_stage": template["stages"][0]["name"] if template.get("stages") else "Introduction"
        }

    def _check_trigger_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if workflow trigger conditions are met."""
        for condition, expected in conditions.items():
            if condition == "new_contributor":
                if not context.get("is_new_contributor", False):
                    return False
            elif condition == "first_commit":
                if not context.get("is_first_commit", False):
                    return False
            elif condition == "manual_activation":
                # Manual activation always passes
                continue
            # Add more conditions as needed

        return True

    async def advance_workflow(self, workflow_id: str, participant_input: Dict[str, Any]) -> Dict[str, Any]:
        """Advance workflow to next stage based on participant input."""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}

        workflow = self.active_workflows[workflow_id]
        template = workflow["template"]
        stages = template.get("stages", [])

        current_stage_idx = workflow["current_stage"]
        current_stage = stages[current_stage_idx] if current_stage_idx < len(stages) else None

        if not current_stage:
            return {"completed": True, "message": "Workflow completed"}

        # Process current stage
        stage_result = await self._process_stage(current_stage, participant_input, workflow)

        # Determine next stage
        transitions = current_stage.get("transitions", {})
        next_stage_name = None

        if "next" in transitions:
            next_stage_name = transitions["next"]
        elif "alternative" in transitions and stage_result.get("alternative_path"):
            next_stage_name = transitions["alternative"]
        elif "complete" in transitions and stage_result.get("completed"):
            workflow["status"] = "completed"
            await self._log_workflow_event(workflow_id, "completed", {})
            return {"completed": True, "message": "Workflow completed successfully"}

        # Find next stage index
        if next_stage_name:
            for i, stage in enumerate(stages):
                if stage["name"] == next_stage_name:
                    workflow["current_stage"] = i
                    workflow["stage_history"].append({
                        "stage": current_stage["name"],
                        "completed_at": datetime.now().isoformat(),
                        "result": stage_result
                    })
                    break

        return {
            "advanced": True,
            "current_stage": next_stage_name,
            "stage_result": stage_result
        }

    async def _process_stage(self, stage: Dict[str, Any], participant_input: Dict[str, Any], workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Process a workflow stage."""
        stage_name = stage["name"]
        activities = stage.get("activities", [])

        results = {}

        for activity in activities:
            activity_type = activity.get("type")

            if activity_type == "reflection":
                results["reflection"] = await self._facilitate_reflection(activity, participant_input)
            elif activity_type == "nexus_query":
                results["nexus_query"] = await self._perform_nexus_query(activity, workflow)
            elif activity_type == "story_sharing":
                results["story_sharing"] = await self._facilitate_story_sharing(activity, workflow)
            elif activity_type == "pattern_recognition":
                results["pattern_recognition"] = await self._facilitate_pattern_recognition(activity, workflow)
            elif activity_type == "role_discovery":
                results["role_discovery"] = await self._facilitate_role_discovery(activity, workflow)
            elif activity_type == "first_contribution_guidance":
                results["first_contribution_guidance"] = await self._provide_contribution_guidance(activity, workflow)

        return results

    async def _facilitate_reflection(self, activity: Dict[str, Any], participant_input: Dict[str, Any]) -> str:
        """Facilitate a reflection activity."""
        prompt = activity.get("prompt", "Take a moment to reflect...")

        # Use skills engine for deeper listening if appropriate
        context = {"text": participant_input.get("response", ""), "recent_events": []}
        skill_response = await self.skills_engine.activate_skill("listening", context)

        if skill_response and skill_response.get("response"):
            return skill_response["response"]
        else:
            return prompt

    async def _perform_nexus_query(self, activity: Dict[str, Any], workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a Nexus query as part of workflow."""
        query = activity.get("query", "")
        purpose = activity.get("purpose", "")

        # This would integrate with the Nexus server
        # For now, return a placeholder
        return {
            "query": query,
            "purpose": purpose,
            "results": ["Placeholder: Nexus integration would go here"],
            "insights": ["Key patterns from codebase history"]
        }

    async def _facilitate_story_sharing(self, activity: Dict[str, Any], workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Facilitate sharing of relevant stories."""
        stories = activity.get("stories", [])
        reflection = activity.get("reflection", "")

        return {
            "stories_presented": stories,
            "reflection_prompt": reflection,
            "shared_insights": ["Stories help us learn from the past"]
        }

    async def _facilitate_pattern_recognition(self, activity: Dict[str, Any], workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Facilitate pattern recognition activity."""
        focus = activity.get("focus", "")
        question = activity.get("question", "")

        # Use pattern skill
        context = {"text": focus, "file_path": ""}
        skill_response = await self.skills_engine.activate_skill("pattern", context)

        return {
            "focus": focus,
            "question": question,
            "pattern_insights": skill_response.get("response") if skill_response else "Patterns recognized"
        }

    async def _facilitate_role_discovery(self, activity: Dict[str, Any], workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Facilitate role discovery for new team members."""
        assessment = activity.get("assessment", "")
        mentorship = activity.get("mentorship_pairing", False)

        return {
            "assessment_focus": assessment,
            "mentorship_available": mentorship,
            "suggested_roles": ["contributor", "reviewer", "facilitator"],
            "strengths_identified": ["analytical thinking", "empathy", "technical skills"]
        }

    async def _provide_contribution_guidance(self, activity: Dict[str, Any], workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance for first contributions."""
        focus = activity.get("focus", "")
        emotional_context = activity.get("emotional_context", "")

        return {
            "focus_area": focus,
            "emotional_context": emotional_context,
            "suggested_contributions": ["documentation", "tests", "small features"],
            "support_available": ["code review", "pair programming", "mentorship"]
        }

    async def get_workflow_status(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of workflows."""
        if workflow_id:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                return {"error": "Workflow not found"}

            template = workflow["template"]
            stages = template.get("stages", [])
            current_stage = stages[workflow["current_stage"]] if workflow["current_stage"] < len(stages) else None

            return {
                "workflow_id": workflow_id,
                "type": workflow["type"],
                "status": workflow["status"],
                "current_stage": current_stage["name"] if current_stage else "Completed",
                "participants": workflow["participants"],
                "started_at": workflow["started_at"],
                "progress": f"{workflow['current_stage'] + 1}/{len(stages)}"
            }
        else:
            return {
                "active_workflows": len(self.active_workflows),
                "workflow_types": list(set(w["type"] for w in self.active_workflows.values())),
                "workflows": [
                    {
                        "id": wid,
                        "type": w["type"],
                        "status": w["status"],
                        "participants": len(w["participants"])
                    }
                    for wid, w in self.active_workflows.items()
                ]
            }

    async def _log_workflow_event(self, workflow_id: str, event_type: str, context: Dict[str, Any]):
        """Log workflow event."""
        event = IterationEvent(
            event_type=f"workflow_{event_type}",
            context={"workflow_id": workflow_id, **context},
            participants=["facilitator"],
            timestamp=datetime.now().isoformat(),
            outcome=event_type
        )

        # Would save to events file, but simplified for now
        pass


# MCP Tool definitions
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="start_workflow",
            description="Start a guided workflow for team processes",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_type": {
                        "type": "string",
                        "description": "Type of workflow to start",
                        "enum": ["discovery", "dilemma", "retrospective"]
                    },
                    "participants": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of participants"
                    },
                    "context": {
                        "type": "object",
                        "description": "Context for workflow initiation"
                    }
                },
                "required": ["workflow_type", "participants", "context"]
            }
        ),
        Tool(
            name="advance_workflow",
            description="Advance workflow to next stage",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID of workflow to advance"
                    },
                    "participant_input": {
                        "type": "object",
                        "description": "Input from participants"
                    }
                },
                "required": ["workflow_id", "participant_input"]
            }
        ),
        Tool(
            name="get_workflow_status",
            description="Get status of active workflows",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Specific workflow ID (optional)"
                    }
                }
            }
        ),
        Tool(
            name="list_workflow_templates",
            description="List available workflow templates",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    workflows = get_workflows_server()

    if name == "start_workflow":
        workflow_type = arguments["workflow_type"]
        participants = arguments["participants"]
        context = arguments.get("context", {})
        result = await workflows.start_workflow(workflow_type, participants, context)

        if result["started"]:
            response = f"🚀 **Workflow Started**\n\n"
            response += f"• Type: {workflow_type}\n"
            response += f"• ID: {result['workflow_id']}\n"
            response += f"• Initial Stage: {result['initial_stage']}\n"
            response += f"• Participants: {', '.join(participants)}\n"
        else:
            response = f"❌ **Workflow Failed to Start**\n\n{result['reason']}"

        return [TextContent(type="text", text=response)]

    elif name == "advance_workflow":
        workflow_id = arguments["workflow_id"]
        participant_input = arguments.get("participant_input", {})
        result = await workflows.advance_workflow(workflow_id, participant_input)

        if "error" in result:
            return [TextContent(type="text", text=f"❌ {result['error']}")]

        if result.get("completed"):
            response = f"✅ **Workflow Completed**\n\n{result['message']}"
        else:
            response = f"➡️ **Workflow Advanced**\n\n"
            response += f"• Current Stage: {result['current_stage']}\n"
            response += f"• Stage Result: {result['stage_result']}\n"

        return [TextContent(type="text", text=response)]

    elif name == "get_workflow_status":
        workflow_id = arguments.get("workflow_id")
        status = await workflows.get_workflow_status(workflow_id)

        if "error" in status:
            return [TextContent(type="text", text=f"❌ {status['error']}")]

        if workflow_id:
            response = f"📊 **Workflow Status**\n\n"
            response += f"• ID: {status['workflow_id']}\n"
            response += f"• Type: {status['type']}\n"
            response += f"• Status: {status['status']}\n"
            response += f"• Current Stage: {status['current_stage']}\n"
            response += f"• Progress: {status['progress']}\n"
            response += f"• Participants: {', '.join(status['participants'])}\n"
        else:
            response = f"📊 **Active Workflows: {status['active_workflows']}**\n\n"
            for wf in status['workflows']:
                response += f"• {wf['id']} ({wf['type']}) - {wf['status']} - {wf['participants']} participants\n"

        return [TextContent(type="text", text=response)]

    elif name == "list_workflow_templates":
        # List available templates
        templates = []
        if workflows.workflows_dir.exists():
            for template_file in workflows.workflows_dir.glob("*_workflow.json"):
                try:
                    with open(template_file, 'r') as f:
                        template = json.load(f)
                        templates.append({
                            "type": template.get("workflow_type"),
                            "name": template.get("name"),
                            "description": template.get("description")
                        })
                except Exception:
                    continue

        response = "📋 **Available Workflow Templates**\n\n"
        for template in templates:
            response += f"• **{template['type']}**: {template['name']}\n"
            response += f"  {template['description']}\n\n"

        return [TextContent(type="text", text=response)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main server entry point."""
    import mcp.server.stdio
    await mcp.server.stdio.serve(server)


if __name__ == "__main__":
    asyncio.run(main())