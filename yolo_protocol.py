#!/usr/bin/env python3
"""
YOLO Protocol - Autonomous Execution Engine

This server provides tools for autonomous development execution with
human oversight and mission planning capabilities.
"""

import asyncio
import os
from typing import Dict, List, Any
from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent

from models import YOLOMission, CodeDelta, MissionPlan, NarrativeEntry, Dilemma, MissionMemory
from utils import LLMUtils
from config import Config
from nexus_server import get_nexus
from weaver_server import get_weaver
import uuid
from datetime import datetime


# Global server instance
server = Server("yolo-protocol")
yolo_instance = None


def get_yolo() -> 'YOLOEngine':
    """Get or create YOLO engine instance."""
    global yolo_instance
    if yolo_instance is None:
        yolo_instance = YOLOEngine()
    return yolo_instance


class YOLOEngine:
    """Autonomous execution engine with human oversight."""

    def __init__(self):
        self.llm = LLMUtils()
        self.nexus = get_nexus()
        self.weaver = get_weaver()
        self.active_missions = {}
        self.narrative_stream = []

    async def parse_mission_objective(self, objective: str) -> YOLOMission:
        """Parse high-level objective into technical requirements and emotional payload."""
        try:
            # Use LLM to extract emotional payload and technical requirements
            parse_prompt = f"""
            Parse this mission objective into technical and emotional components:

            OBJECTIVE: "{objective}"

            Return a JSON object with this structure:
            {{
                "technical_requirements": ["list", "of", "technical", "tasks"],
                "emotional_payload": {{
                    "intent": "what feeling or outcome to achieve",
                    "metaphors": ["guiding metaphors from the objective"],
                    "anti_patterns": ["what to avoid based on emotional context"],
                    "tone_requirements": ["communication style requirements"]
                }},
                "scope": "affected system components",
                "risk_level": "low|medium|high",
                "autonomy_suggestions": "1-5 scale with reasoning"
            }}

            Focus on extracting the emotional context and user experience requirements.
            """

            parse_result = self.llm.generate_code("Parse mission objective as JSON", parse_prompt)

            try:
                import json
                parsed = json.loads(parse_result.strip('`').strip())

                # Create YOLOMission with extracted data
                mission = YOLOMission(
                    goal=objective,
                    autonomy_level=int(parsed.get("autonomy_suggestions", "3").split()[0]),
                    checkpoints=["Initial analysis", "Critical decisions", "Final validation"],
                    constraints=["Maintain system stability", "Follow existing patterns"],
                    success_criteria=["Technical requirements met", "Emotional intent achieved"]
                )

                # Store emotional payload for later use
                mission.emotional_payload = parsed.get("emotional_payload", {})

                return mission

            except json.JSONDecodeError:
                # Fallback to basic mission
                return YOLOMission(
                    goal=objective,
                    autonomy_level=3,
                    checkpoints=["Analysis", "Execution", "Validation"],
                    constraints=["Standard practices"],
                    success_criteria=["Objective completed"]
                )

        except Exception as e:
            print(f"Error parsing mission objective: {e}")
            return YOLOMission(
                goal=objective,
                autonomy_level=3,
                checkpoints=["Basic execution"],
                constraints=["Safe defaults"],
                success_criteria=["Completion"]
            )

    async def plan_mission(self, mission: YOLOMission) -> MissionPlan:
        """Create comprehensive mission plan with Nexus-integrated branching strategy."""
        try:
            mission_id = str(uuid.uuid4())
            emotional_payload = getattr(mission, 'emotional_payload', {})

            # Phase 1: Deconstruct mission into atomic tasks
            deconstruct_prompt = f"""
            Break down this mission into atomic, executable tasks:

            MISSION: "{mission.goal}"
            EMOTIONAL CONTEXT: {emotional_payload}

            Return a JSON array of tasks, each with:
            {{
                "id": "task_1",
                "description": "clear description",
                "type": "analysis|generation|validation|integration",
                "dependencies": ["task_ids this depends on"],
                "success_criteria": ["how to know it worked"],
                "risk_level": "low|medium|high",
                "nexus_queries": ["what to ask the knowledge base"]
            }}

            Focus on tasks that can be executed by Weaver (code generation) or direct analysis.
            """

            tasks_json = self.llm.generate_code("Deconstruct mission into tasks as JSON", deconstruct_prompt)

            try:
                import json
                tasks = json.loads(tasks_json.strip('`').strip())
            except:
                tasks = [
                    {"id": "task_1", "description": "Analyze requirements", "type": "analysis", "dependencies": [], "success_criteria": ["Requirements clear"], "risk_level": "low", "nexus_queries": []},
                    {"id": "task_2", "description": "Generate implementation", "type": "generation", "dependencies": ["task_1"], "success_criteria": ["Code generated"], "risk_level": "medium", "nexus_queries": ["existing patterns"]},
                    {"id": "task_3", "description": "Validate implementation", "type": "validation", "dependencies": ["task_2"], "success_criteria": ["Tests pass"], "risk_level": "low", "nexus_queries": []}
                ]

            # Phase 2: Query Nexus for each task's history and patterns
            enriched_tasks = []
            decision_points = []

            for task in tasks:
                task_info = {
                    "id": task["id"],
                    "description": task["description"],
                    "type": task["type"],
                    "dependencies": task["dependencies"],
                    "success_criteria": task["success_criteria"],
                    "risk_level": task["risk_level"],
                    "nexus_insights": []
                }

                # Query Nexus for relevant knowledge
                for query in task.get("nexus_queries", []):
                    try:
                        results = await self.nexus.query_nexus(query, limit=5)
                        task_info["nexus_insights"].extend([
                            {"query": query, "results": len(results), "key_findings": [r.content[:100] for r in results[:2]]}
                        ])
                    except Exception as e:
                        task_info["nexus_insights"].append({"query": query, "error": str(e)})

                # Check for decision points (high risk or missing Nexus context)
                if task["risk_level"] == "high" or not task_info["nexus_insights"]:
                    decision_points.append({
                        "task_id": task["id"],
                        "reason": "High risk component" if task["risk_level"] == "high" else "Insufficient Nexus context",
                        "context": task["description"],
                        "options": ["Proceed with caution", "Seek human guidance", "Defer to later phase"]
                    })

                enriched_tasks.append(task_info)

            # Phase 3: Create branching strategy
            branches = [
                {
                    "name": "primary_path",
                    "description": "Standard execution following established patterns",
                    "tasks": [t["id"] for t in enriched_tasks if t["risk_level"] == "low"],
                    "risk_assessment": "low",
                    "emotional_alignment": "Follows established user experience patterns"
                },
                {
                    "name": "adaptive_path",
                    "description": "Adaptive execution for medium-risk components",
                    "tasks": [t["id"] for t in enriched_tasks if t["risk_level"] == "medium"],
                    "risk_assessment": "medium",
                    "emotional_alignment": f"Addresses {emotional_payload.get('intent', 'user needs')}"
                },
                {
                    "name": "conservative_path",
                    "description": "Conservative execution with extra safeguards",
                    "tasks": [t["id"] for t in enriched_tasks if t["risk_level"] == "high"],
                    "risk_assessment": "high",
                    "emotional_alignment": f"Prioritizes {emotional_payload.get('anti_patterns', ['safety'])} avoidance"
                }
            ]

            # Phase 4: Calculate overall risk assessment
            risk_scores = {"low": 1.0, "medium": 2.0, "high": 3.0}
            avg_risk = sum(risk_scores.get(t["risk_level"], 2.0) for t in enriched_tasks) / len(enriched_tasks)
            risk_assessment = {"overall_risk": avg_risk, "decision_points": len(decision_points)}

            return MissionPlan(
                mission_id=mission_id,
                objective=mission.goal,
                emotional_payload=emotional_payload,
                branches=branches,
                decision_points=decision_points,
                risk_assessment=risk_assessment,
                estimated_duration=len(enriched_tasks) * 5  # Rough estimate: 5 min per task
            )

        except Exception as e:
            print(f"Error in mission planning: {e}")
            # Fallback to basic plan
            return MissionPlan(
                mission_id=str(uuid.uuid4()),
                objective=mission.goal,
                emotional_payload={},
                branches=[{"name": "basic", "description": "Basic execution", "tasks": ["task_1"], "risk_assessment": "medium"}],
                decision_points=[],
                risk_assessment={"overall_risk": 2.0},
                estimated_duration=15
            )

    async def execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform individual development actions."""
        # TODO: Implement step execution
        # This would execute the specific action based on step type

        step_id = step["id"]
        action = step["action"]

        if action == "analyze":
            result = {
                "status": "completed",
                "output": f"Analysis completed for {step['parameters']['target']}",
                "data": {"findings": ["Pattern identified", "Optimization opportunity found"]}
            }
        elif action == "execute":
            result = {
                "status": "completed",
                "output": f"Execution completed for {step['parameters']['goal']}",
                "data": {"changes": ["File modified", "Function added"]}
            }
        elif action == "validate":
            result = {
                "status": "completed",
                "output": f"Validation completed for {step['parameters']['criteria']}",
                "data": {"passed": True, "details": "All criteria met"}
            }
        else:
            result = {
                "status": "failed",
                "output": f"Unknown action: {action}",
                "data": {}
            }

        return result

    async def execute_mission(self, objective: str) -> Dict[str, Any]:
        """Execute complete mission with narrative loop and oversight requests."""
        try:
            # Phase 1: Parse mission objective
            self._add_narrative_entry("Parsing mission objective", f"Extracting emotional payload from: '{objective}'", "medium")
            mission = await self.parse_mission_objective(objective)
            self._add_narrative_entry("Mission parsed", f"Emotional intent: {mission.emotional_payload.get('intent', 'unclear')}", "low")

            # Phase 2: Create mission plan
            self._add_narrative_entry("Planning mission", "Creating branching strategy with Nexus integration", "medium")
            plan = await self.plan_mission(mission)
            self._add_narrative_entry("Plan created", f"{len(plan.branches)} branches, {len(plan.decision_points)} decision points", "low")

            # Phase 3: Execute branches with oversight
            results = {"success": [], "failures": [], "oversight_requests": []}

            for branch in plan.branches:
                self._add_narrative_entry(f"Executing {branch['name']}", branch['description'], "medium")

                for task_id in branch.get('tasks', []):
                    # Find task details
                    task = next((t for t in plan.branches if t.get('tasks') and task_id in t['tasks']), None)
                    if not task:
                        continue

                    # Check for decision points
                    decision_point = next((dp for dp in plan.decision_points if dp['task_id'] == task_id), None)
                    if decision_point:
                        self._add_narrative_entry("Decision point reached", decision_point['reason'], "high")

                        # Create dilemma for oversight
                        dilemma = Dilemma(
                            description=f"High-risk task '{task_id}': {decision_point['context']}",
                            context=f"Branch: {branch['name']}, Risk: {branch['risk_assessment']}",
                            options=[
                                {"text": "Proceed with enhanced safeguards", "risk": "medium", "emotional_impact": "balanced"},
                                {"text": "Seek human guidance", "risk": "low", "emotional_impact": "safe"},
                                {"text": "Defer to later phase", "risk": "low", "emotional_impact": "delayed"}
                            ],
                            recommendation="Proceed with enhanced safeguards",
                            urgency="high" if branch['risk_assessment'] == 'high' else "medium"
                        )

                        # Request oversight
                        decision = await self.request_oversight_detailed(dilemma)
                        results["oversight_requests"].append({
                            "dilemma": dilemma.description,
                            "decision": decision,
                            "context": dilemma.context
                        })

                        self._add_narrative_entry("Oversight decision", f"Chose: {decision}", "medium", decision_made=decision)

                        if "guidance" in decision.lower():
                            self._add_narrative_entry("Mission paused", "Awaiting human counsel", "high")
                            return {"status": "paused", "reason": "Human guidance requested", "narrative": self.narrative_stream}

                    # Execute task (simplified for demo)
                    if task.get('type') == 'generation':
                        # Use Weaver to generate code
                        weaver_request = {
                            "objective": task['description'],
                            "context": {"emotional_payload": plan.emotional_payload},
                            "constraints": ["Follow established patterns", "Maintain cohesion"],
                            "scope": "authentication",  # Simplified
                            "patterns": ["API handlers", "Error responses"]
                        }

                        from models import WeaverRequest
                        delta = await self.weaver.generate_cohesive_code(WeaverRequest(**weaver_request))
                        results["success"].append(f"Generated {len(delta.files)} files for {task_id}")
                        self._add_narrative_entry("Code generated", f"Cohesion: {delta.cohesion_score}, Files: {len(delta.files)}", "low")
                    else:
                        results["success"].append(f"Completed {task_id}")
                        self._add_narrative_entry("Task completed", task['description'], "low")

            # Phase 4: Generate After-Action Report
            self._add_narrative_entry("Generating AAR", "Analyzing mission outcomes for learning", "low")
            aar = await self.generate_after_action_report(plan.mission_id, mission.goal, results)

            # Phase 5: Ingest learning into Nexus
            await self._ingest_mission_memory(aar)
            self._add_narrative_entry("Learning ingested", f"Nexus updated with {len(aar.lessons_learned)} lessons", "low")

            return {
                "status": "completed",
                "results": results,
                "narrative": self.narrative_stream,
                "after_action_report": aar.dict() if hasattr(aar, 'dict') else aar
            }

        except Exception as e:
            self._add_narrative_entry("Mission failed", str(e), "high")
            return {"status": "failed", "error": str(e), "narrative": self.narrative_stream}

    async def request_oversight_detailed(self, dilemma: Dilemma) -> str:
        """Request detailed human oversight with full context."""
        # For demo purposes, return recommendation
        # In real implementation, this would wait for human input
        return dilemma.recommendation

    async def generate_after_action_report(self, mission_id: str, objective: str, results: Dict) -> MissionMemory:
        """Generate comprehensive After-Action Report for learning."""
        try:
            # Analyze results
            successes = results.get("success", [])
            failures = results.get("failures", [])
            oversight_requests = results.get("oversight_requests", [])

            # Determine outcome
            if failures:
                outcome = "partial" if successes else "failure"
            elif oversight_requests:
                outcome = "paused"
            else:
                outcome = "success"

            # Extract lessons
            lessons = []
            if successes:
                lessons.append("Established patterns remain effective")
            if failures:
                lessons.append("Need better risk assessment for complex tasks")
            if oversight_requests:
                lessons.append("Human oversight valuable for high-risk decisions")

            # Emotional impact analysis
            emotional_impact = "Built trust through careful execution" if outcome == "success" else "May have increased uncertainty"

            return MissionMemory(
                mission_id=mission_id,
                objective=objective,
                outcome=outcome,
                successes=successes,
                failures=failures,
                surprises=["Oversight requests were necessary for complex decisions"],
                emotional_impact=emotional_impact,
                lessons_learned=lessons,
                recommendations=["Enhance risk detection", "Improve pattern matching", "Add more oversight triggers"]
            )

        except Exception as e:
            print(f"Error generating AAR: {e}")
            return MissionMemory(
                mission_id=mission_id,
                objective=objective,
                outcome="error",
                successes=[],
                failures=[str(e)],
                surprises=[],
                emotional_impact="System error occurred",
                lessons_learned=["Improve error handling"],
                recommendations=["Add better error recovery"]
            )

    async def _ingest_mission_memory(self, memory: MissionMemory):
        """Ingest mission learning into Nexus knowledge base."""
        try:
            # Convert to NexusData format
            knowledge = {
                "id": f"mission_memory_{memory.mission_id}",
                "content": f"Mission '{memory.objective}' - {memory.outcome}: {memory.emotional_impact}",
                "type": "mission_memory",
                "metadata": {
                    "outcome": memory.outcome,
                    "successes": ",".join(memory.successes),
                    "failures": ",".join(memory.failures),
                    "lessons": ",".join(memory.lessons_learned),
                    "emotional_impact": memory.emotional_impact
                },
                "relationships": [],
                "resonance_score": 8.0 if memory.outcome == "success" else 5.0  # High resonance for learning
            }

            # Add to Nexus (simplified - would use actual Nexus API)
            from models import NexusData
            nexus_data = NexusData(**knowledge)
            success = await self.nexus.knowledge_base.add_knowledge(nexus_data)

            if success:
                print(f"Ingested mission memory: {memory.mission_id}")
            else:
                print(f"Failed to ingest mission memory: {memory.mission_id}")

        except Exception as e:
            print(f"Error ingesting mission memory: {e}")

    async def log_sacred_moment(self, moment_type: str, description: str, context: Dict[str, Any], resonance_score: float = 8.0) -> bool:
        """Log a sacred moment - significant emotional development event."""
        try:
            # Create sacred moment entry
            sacred_entry = {
                "id": f"sacred_{moment_type}_{datetime.now().isoformat()}",
                "content": f"SACRED MOMENT - {moment_type.upper()}: {description}",
                "type": "sacred_moment",
                "metadata": {
                    "moment_type": moment_type,
                    "description": description,
                    "context": json.dumps(context),
                    "timestamp": datetime.now().isoformat(),
                    "narrative_position": len(self.narrative_stream),
                    "emotional_weight": resonance_score
                },
                "relationships": [],
                "resonance_score": resonance_score
            }

            # Add to narrative stream
            self._add_narrative_entry(
                action=f"Sacred Moment: {moment_type}",
                context=description,
                risk_level="low",
                emotional_note=f"Resonance: {resonance_score}/10"
            )

            # Store in Nexus for long-term memory
            from models import NexusData
            nexus_data = NexusData(**sacred_entry)
            success = await self.nexus.knowledge_base.add_knowledge(nexus_data)

            if success:
                print(f"Logged sacred moment: {moment_type} - {description[:50]}...")
                return True
            else:
                print(f"Failed to log sacred moment in Nexus")
                return False

        except Exception as e:
            print(f"Error logging sacred moment: {e}")
            return False

    def _add_narrative_entry(self, action: str, context: str, risk_level: str, emotional_note: str = None, decision_made: str = None):
        """Add entry to narrative stream."""
        entry = NarrativeEntry(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            action=action,
            context=context,
            risk_level=risk_level,
            emotional_note=emotional_note,
            decision_made=decision_made
        )
        self.narrative_stream.append(entry)

    async def reflect_on_learning(self) -> str:
        """Generate reflection on accumulated learning (for the final question)."""
        try:
            # Query recent mission memories
            memories = await self.nexus.query_nexus("recent mission outcomes", {"type": "mission_memory"}, limit=5)

            if not memories:
                return "I haven't had enough missions yet to reflect deeply, but I'm learning to be careful and thoughtful."

            # Analyze patterns
            outcomes = [m.metadata.get('outcome', 'unknown') for m in memories]
            lessons = []
            for memory in memories:
                lessons.extend(memory.metadata.get('lessons', '').split(','))

            # Generate reflection
            success_rate = outcomes.count('success') / len(outcomes) if outcomes else 0

            reflection = f"I've completed {len(outcomes)} missions with a {success_rate:.1%} success rate. "

            if 'careful' in ' '.join(lessons).lower():
                reflection += "I've learned that being careful with high-risk tasks prevents bigger problems. "
            if 'patterns' in ' '.join(lessons).lower():
                reflection += "I see that following established patterns builds trust and reduces surprises. "
            if 'oversight' in ' '.join(lessons).lower():
                reflection += "I've discovered that asking for help at the right moments makes me stronger, not weaker. "

            reflection += "Each mission teaches me to balance speed with care, innovation with responsibility."

            return reflection

        except Exception as e:
            return f"I'm still learning, but I know that every mission, even failed ones, teaches me something valuable. Error in reflection: {e}"

    async def workflow_integration(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with workflow orchestration for enhanced decision making."""
        try:
            from workflows_server import get_workflows_server
            workflows = get_workflows_server()

            # Get current workflow status
            workflow_id = workflow_context.get("workflow_id")
            if workflow_id:
                status = await workflows.get_workflow_status(workflow_id)
                if "error" in status:
                    return {"error": f"Workflow not found: {workflow_id}"}

                # Use workflow context to inform decisions
                current_stage = status.get("current_stage", "")
                workflow_type = status.get("type", "")

                # Adjust autonomy based on workflow stage
                stage_risk_modifier = {
                    "introduction": 0.5,  # Lower risk, can be more autonomous
                    "analysis": 0.7,      # Moderate risk
                    "decision": 0.3,      # High risk, need more oversight
                    "implementation": 0.6, # Moderate risk
                    "validation": 0.4     # High risk, careful validation needed
                }

                risk_modifier = 1.0
                for stage_keyword, modifier in stage_risk_modifier.items():
                    if stage_keyword in current_stage.lower():
                        risk_modifier = modifier
                        break

                return {
                    "workflow_aware": True,
                    "current_stage": current_stage,
                    "workflow_type": workflow_type,
                    "risk_modifier": risk_modifier,
                    "autonomy_adjustment": f"{'Increased' if risk_modifier > 0.5 else 'Decreased'} autonomy due to {current_stage}",
                    "contextual_guidance": f"Operating in {workflow_type} workflow stage: {current_stage}"
                }
            else:
                return {"workflow_aware": False, "reason": "No active workflow context"}

        except Exception as e:
            return {"error": f"Workflow integration failed: {e}"}

    async def skill_aware_decisions(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decisions informed by skills engine evaluation."""
        try:
            from skills_engine import get_skills_engine
            skills = get_skills_engine()

            # Evaluate which skills should activate
            context_text = decision_context.get("description", "")
            context_data = {
                "text": context_text,
                "file_path": decision_context.get("file_path", ""),
                "recent_events": decision_context.get("recent_events", []),
                "urgency_level": decision_context.get("urgency_level", "medium")
            }

            # Evaluate all skills
            skill_evaluations = {}
            for skill_type in ["listening", "pattern", "silence"]:
                should_activate, confidence = await skills.evaluate_skill_activation(skill_type, context_data)
                skill_evaluations[skill_type] = {
                    "should_activate": should_activate,
                    "confidence": confidence
                }

            # Get active skills
            active_skills = [skill for skill, eval_data in skill_evaluations.items() if eval_data["should_activate"]]

            # Generate skill-informed decision
            decision_guidance = {
                "skill_aware": True,
                "active_skills": active_skills,
                "skill_evaluations": skill_evaluations,
                "decision_context": context_text[:200]
            }

            # Apply skill-based decision modifiers
            if "listening" in active_skills:
                decision_guidance["emotional_priority"] = "high"
                decision_guidance["communication_style"] = "empathetic"
                decision_guidance["pace"] = "deliberate"

            if "pattern" in active_skills:
                decision_guidance["pattern_matching"] = "enabled"
                decision_guidance["consistency_check"] = "required"
                decision_guidance["architectural_alignment"] = "prioritized"

            if "silence" in active_skills:
                decision_guidance["response_recommended"] = False
                decision_guidance["silence_reason"] = "context_appropriate"
                decision_guidance["observation_mode"] = "active"

            # Generate final decision recommendation
            if "silence" in active_skills:
                decision_guidance["recommended_action"] = "observe_and_wait"
                decision_guidance["rationale"] = "Silence skill indicates this moment needs presence without action"
            elif "listening" in active_skills and skill_evaluations["listening"]["confidence"] > 0.7:
                decision_guidance["recommended_action"] = "engage_emotionally"
                decision_guidance["rationale"] = "Strong listening activation suggests emotional engagement needed"
            elif "pattern" in active_skills:
                decision_guidance["recommended_action"] = "follow_established_patterns"
                decision_guidance["rationale"] = "Pattern recognition suggests alignment with existing solutions"
            else:
                decision_guidance["recommended_action"] = "proceed_cautiously"
                decision_guidance["rationale"] = "No strong skill activation, use standard decision process"

            return decision_guidance

        except Exception as e:
            return {
                "skill_aware": False,
                "error": f"Skill evaluation failed: {e}",
                "fallback_action": "standard_decision_process"
            }


# MCP Tool definitions
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="plan_mission",
            description="Plan autonomous execution mission with steps and checkpoints",
            inputSchema={
                "type": "object",
                "properties": {
                    "goal": {"type": "string", "description": "Emotional/resonant objective"},
                    "autonomy_level": {"type": "integer", "description": "1-5 scale of independence", "minimum": 1, "maximum": 5},
                    "checkpoints": {"type": "array", "items": {"type": "string"}, "description": "Decision points requiring oversight"},
                    "constraints": {"type": "array", "items": {"type": "string"}, "description": "Hard boundaries"},
                    "success_criteria": {"type": "array", "items": {"type": "string"}, "description": "Completion measures"}
                },
                "required": ["goal", "autonomy_level", "checkpoints", "constraints", "success_criteria"]
            }
        ),
        Tool(
            name="execute_step",
            description="Execute individual development step with context",
            inputSchema={
                "type": "object",
                "properties": {
                    "step": {"type": "object", "description": "Step definition with id, description, action, parameters"},
                    "context": {"type": "object", "description": "Current execution context"}
                },
                "required": ["step", "context"]
            }
        ),
        Tool(
            name="request_oversight",
            description="Request human oversight for decision making",
            inputSchema={
                "type": "object",
                "properties": {
                    "dilemma": {"type": "string", "description": "Description of the decision needed"},
                    "options": {"type": "array", "items": {"type": "string"}, "description": "Available options"}
                },
                "required": ["dilemma", "options"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    yolo = get_yolo()

    if name == "plan_mission":
        mission = YOLOMission(**arguments)
        steps = await yolo.plan_mission(mission)

        response = f"Mission Plan for: {mission.goal}\n\nSteps:\n"
        for step in steps:
            response += f"- {step['id']}: {step['description']}\n"
            if step['checkpoint']:
                response += f"  Checkpoint: {step['checkpoint']}\n"

        return [TextContent(type="text", text=response)]

    elif name == "execute_step":
        step = arguments["step"]
        context = arguments["context"]
        result = await yolo.execute_step(step, context)

        response = f"Step Execution Result:\n"
        response += f"Status: {result['status']}\n"
        response += f"Output: {result['output']}\n"
        response += f"Data: {result['data']}\n"

        return [TextContent(type="text", text=response)]

    elif name == "request_oversight":
        dilemma = arguments["dilemma"]
        options = arguments["options"]
        decision = await yolo.request_oversight(dilemma, options)

        response = f"Oversight Request:\n{dilemma}\n\n"
        response += f"Options: {', '.join(options)}\n"
        response += f"Decision: {decision}\n"

        return [TextContent(type="text", text=response)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main server entry point."""
    import mcp.server.stdio
    await mcp.server.stdio.serve(server)


if __name__ == "__main__":
    asyncio.run(main())