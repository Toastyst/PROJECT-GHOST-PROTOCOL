#!/usr/bin/env python3
"""
Oracle Server - Bleeding Edge Reasoning MCP Server

The Oracle Ghost provides o1-style reasoning chains, long-context analysis,
and multi-agent coordination for complex problem solving.
"""

import asyncio
import json
import os
from typing import Any, Dict, Sequence, List
from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent, PromptMessage
import chromadb
from chromadb.config import Settings

from src.ghost_protocol.models.models import NexusData, EmotionalEntry, NoteFragment, TransmutationRecord
from src.ghost_protocol.utils.utils import GitUtils, CodeAnalyzer, LLMUtils
from src.ghost_protocol.utils.config import Config

# Global server instance
server = Server("oracle-server")
oracle_instance = None


def get_oracle() -> 'OracleServer':
    """Get or create Oracle server instance."""
    global oracle_instance
    if oracle_instance is None:
        oracle_instance = OracleServer()
    return oracle_instance


class OracleServer:
    """MCP Server for advanced reasoning and multi-agent coordination."""

    def __init__(self):
        self.llm = LLMUtils()
        self.reasoning_chains = []
        self.network_peers = []

    async def deep_reasoning_analysis(self, problem: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Tree of Thoughts (ToT) deep reasoning on complex problems."""
        try:
            # Tree of Thoughts implementation
            thoughts = await self._generate_reasoning_tree(problem, context)

            # Evaluate thoughts
            evaluated_thoughts = await self._evaluate_thoughts(thoughts, problem, context)

            # Select best reasoning path
            best_reasoning = self._select_best_reasoning(evaluated_thoughts)

            # Build comprehensive context with ToT
            reasoning_prompt = f"""
You are the Oracle Ghost using Tree of Thoughts reasoning for maximum insight.

PROBLEM: {problem}

CONTEXT:
{json.dumps(context, indent=2)}

TREE OF THOUGHTS ANALYSIS:
{json.dumps(best_reasoning, indent=2)}

INSTRUCTIONS:
1. Synthesize the best reasoning path from the thought tree
2. Identify the most promising solution trajectory
3. Consider multiple perspectives and edge cases
4. Chain your reasoning step-by-step with ToT insights
5. Identify patterns and connections across thought branches
6. Propose innovative solutions validated by multiple reasoning paths
7. Consider long-term implications with uncertainty quantification

Think like o1 with ToT - explore multiple paths, converge on optimal reasoning.
"""

            # Use advanced reasoning with ToT foundation
            analysis = await self.llm.generate_with_reasoning(reasoning_prompt)

            # Parse enhanced reasoning chain
            reasoning_chain = {
                "problem": problem,
                "context": context,
                "thought_tree": thoughts,
                "evaluated_thoughts": evaluated_thoughts,
                "best_reasoning_path": best_reasoning,
                "reasoning_steps": self._parse_reasoning_steps(analysis),
                "conclusions": self._extract_conclusions(analysis),
                "innovations": self._identify_innovations(analysis),
                "confidence": self._calculate_confidence(analysis),
                "tot_metadata": {
                    "total_thoughts_generated": len(thoughts),
                    "thoughts_evaluated": len(evaluated_thoughts),
                    "reasoning_depth": best_reasoning.get('depth', 0),
                    "branching_factor": len(thoughts) / max(1, best_reasoning.get('depth', 1))
                }
            }

            self.reasoning_chains.append(reasoning_chain)
            return reasoning_chain

        except Exception as e:
            print(f"Error in ToT deep reasoning: {e}")
            return {
                "error": str(e),
                "problem": problem,
                "reasoning_steps": [],
                "conclusions": [],
                "innovations": [],
                "confidence": 0.0,
                "tot_metadata": {"error": "ToT failed"}
            }

    async def _generate_reasoning_tree(self, problem: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a tree of reasoning thoughts."""
        thoughts = []

        # Generate multiple initial thoughts
        for i in range(3):  # Generate 3 initial branches
            thought_prompt = f"""
Generate a distinct reasoning path for solving: {problem}

Context: {json.dumps(context, indent=2)}

Branch {i+1}: Take a unique approach to break down and analyze this problem.
Focus on different aspects or perspectives.

Structure your thought as:
- Initial hypothesis
- Key assumptions
- Step-by-step reasoning
- Potential solutions
- Uncertainties identified

Be creative and explore different angles.
"""

            try:
                thought = await self.llm.generate_with_reasoning(thought_prompt)
                thoughts.append({
                    "branch_id": i,
                    "depth": 1,
                    "content": thought,
                    "parent": None,
                    "children": []
                })
            except Exception as e:
                print(f"Error generating thought branch {i}: {e}")

        # Generate deeper thoughts (expand promising branches)
        for thought in thoughts[:2]:  # Expand top 2 branches
            for j in range(2):  # 2 sub-thoughts each
                sub_thought_prompt = f"""
Building on this reasoning path:

{thought['content']}

Generate a deeper analysis exploring:
- Edge cases not considered
- Alternative interpretations
- Potential failure modes
- Integration with broader context

Refine and extend the reasoning.
"""

                try:
                    sub_thought = await self.llm.generate_with_reasoning(sub_thought_prompt)
                    thoughts.append({
                        "branch_id": f"{thought['branch_id']}.{j}",
                        "depth": 2,
                        "content": sub_thought,
                        "parent": thought['branch_id'],
                        "children": []
                    })
                    thought['children'].append(f"{thought['branch_id']}.{j}")
                except Exception as e:
                    print(f"Error generating sub-thought {thought['branch_id']}.{j}: {e}")

        return thoughts

    async def _evaluate_thoughts(self, thoughts: List[Dict[str, Any]], problem: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate each thought for quality and relevance."""
        evaluated = []

        for thought in thoughts:
            eval_prompt = f"""
Evaluate this reasoning path for solving: {problem}

Context: {json.dumps(context, indent=2)}

Reasoning Path:
{thought['content']}

Evaluate on:
1. Logical consistency (0-1)
2. Completeness of analysis (0-1)
3. Innovation/creativity (0-1)
4. Practical feasibility (0-1)
5. Risk awareness (0-1)

Return scores as JSON with brief justifications.
"""

            try:
                eval_response = await self.llm.generate_with_reasoning(eval_prompt)
                # Parse scores
                scores = self._parse_evaluation_scores(eval_response)

                evaluated.append({
                    **thought,
                    "evaluation": scores,
                    "total_score": sum(scores.values()) / len(scores) if scores else 0.0
                })
            except Exception as e:
                print(f"Error evaluating thought {thought['branch_id']}: {e}")
                evaluated.append({
                    **thought,
                    "evaluation": {"error": str(e)},
                    "total_score": 0.0
                })

        return evaluated

    def _parse_evaluation_scores(self, eval_text: str) -> Dict[str, float]:
        """Parse evaluation scores from LLM response."""
        scores = {}
        try:
            # Try to parse as JSON first
            parsed = json.loads(eval_text)
            for key, value in parsed.items():
                if isinstance(value, (int, float)):
                    scores[key] = min(max(float(value), 0), 1)
        except:
            # Fallback: extract numbers
            import re
            numbers = re.findall(r'(\d+\.?\d*)', eval_text)
            criteria = ['consistency', 'completeness', 'innovation', 'feasibility', 'risk_awareness']
            for i, num in enumerate(numbers[:5]):
                try:
                    scores[criteria[i]] = min(max(float(num), 0), 1)
                except:
                    pass

        return scores

    def _select_best_reasoning(self, evaluated_thoughts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best reasoning path from evaluated thoughts."""
        if not evaluated_thoughts:
            return {"error": "No thoughts to evaluate"}

        # Sort by total score
        sorted_thoughts = sorted(evaluated_thoughts, key=lambda x: x.get('total_score', 0), reverse=True)

        best_thought = sorted_thoughts[0]

        # Build reasoning path from root to best leaf
        reasoning_path = []
        current = best_thought

        # Collect the path
        path_elements = []
        while current:
            path_elements.insert(0, current)
            parent_id = current.get('parent')
            if parent_id is not None:
                current = next((t for t in evaluated_thoughts if t['branch_id'] == parent_id), None)
            else:
                current = None

        return {
            "best_branch": best_thought['branch_id'],
            "total_score": best_thought.get('total_score', 0),
            "reasoning_path": [elem['content'] for elem in path_elements],
            "evaluation": best_thought.get('evaluation', {}),
            "depth": best_thought.get('depth', 0)
        }

    def _parse_reasoning_steps(self, analysis: str) -> List[Dict[str, Any]]:
        """Parse reasoning steps from LLM response."""
        steps = []
        lines = analysis.split('\n')

        current_step = None
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')) or line.lower().startswith(('first', 'second', 'third')):
                if current_step:
                    steps.append(current_step)
                current_step = {"step": len(steps) + 1, "content": line, "evidence": []}
            elif current_step and (line.startswith('-') or line.startswith('•')):
                current_step["evidence"].append(line[1:].strip())
            elif current_step:
                current_step["content"] += f" {line}"

        if current_step:
            steps.append(current_step)

        return steps

    def _extract_conclusions(self, analysis: str) -> List[str]:
        """Extract key conclusions from analysis."""
        conclusions = []
        lines = analysis.split('\n')

        in_conclusion = False
        for line in lines:
            line = line.strip()
            if 'conclusion' in line.lower() or 'therefore' in line.lower():
                in_conclusion = True
            elif in_conclusion and line and not line.startswith(('•', '-', '*')):
                if len(line) > 20:  # Substantial conclusion
                    conclusions.append(line)
                    in_conclusion = False

        return conclusions[:5]  # Limit to top 5

    def _identify_innovations(self, analysis: str) -> List[str]:
        """Identify innovative ideas from analysis."""
        innovations = []
        lines = analysis.split('\n')

        for line in lines:
            line = line.strip()
            # Look for innovative language
            if any(word in line.lower() for word in ['innovative', 'novel', 'breakthrough', 'revolutionary', 'new approach']):
                if len(line) > 15:
                    innovations.append(line)

        return innovations[:3]  # Limit to top 3

    def _calculate_confidence(self, analysis: str) -> float:
        """Calculate confidence score for the analysis."""
        confidence_indicators = [
            'certainly', 'definitely', 'clearly', 'obviously',
            'strong evidence', 'conclusive', 'proven',
            'high confidence', 'very likely'
        ]

        text_lower = analysis.lower()
        confidence_score = 0.5  # Base confidence

        for indicator in confidence_indicators:
            if indicator in text_lower:
                confidence_score += 0.1

        # Cap at 0.95
        return min(confidence_score, 0.95)

    async def prophet_tools(self) -> Dict[str, Any]:
        """Access Prophet Engine tools for predictive analysis."""
        try:
            from src.ghost_protocol.engines.prophet_engine import prophet_engine

            return {
                "prophet_status": prophet_engine.get_prophecy_status(),
                "available_domains": ["incident", "team_health", "architectural_decay", "knowledge_loss"],
                "forecasting_agents": [agent.name for agent in prophet_engine.agents],
                "constitutional_principles": prophet_engine.constitutional_reviewer.get_principles_summary() if hasattr(prophet_engine, 'constitutional_reviewer') else {}
            }
        except Exception as e:
            print(f"Error accessing Prophet tools: {e}")
            return {"error": str(e), "prophet_available": False}

    async def swarm_coordination(self, task: str, domain: str = "general") -> Dict[str, Any]:
        """Coordinate a swarm of specialized forecasting agents."""
        try:
            from src.ghost_protocol.engines.prophet_engine import prophet_engine

            # Map domain to appropriate agents
            domain_agents = {
                "incident": ["Sentinel"],
                "team_health": ["Empath"],
                "architectural_decay": ["Archivist"],
                "knowledge_loss": ["Historian"],
                "general": ["Archivist", "Empath", "Sentinel", "Historian"]
            }

            relevant_agents = domain_agents.get(domain, domain_agents["general"])

            # Activate relevant agents
            active_agents = [agent for agent in prophet_engine.agents if agent.name in relevant_agents]
            for agent in active_agents:
                agent.active = True

            # Create swarm coordinator with active agents
            from src.ghost_protocol.engines.prophet_engine import SwarmCoordinator
            swarm = SwarmCoordinator(active_agents)

            # Run swarm debate
            context = {"domain": domain, "coordination_level": "swarm"}
            consensus = swarm.debate_and_consensus(task, context)

            # Review consensus constitutionally
            if hasattr(prophet_engine, 'constitutional_reviewer'):
                consensus_prediction = consensus.individual_predictions[0] if consensus.individual_predictions else None
                if consensus_prediction:
                    review_status = prophet_engine.constitutional_reviewer.review_prediction(consensus_prediction)
                    consensus_prediction.constitutional_review = review_status

            return {
                "task": task,
                "domain": domain,
                "active_agents": relevant_agents,
                "consensus_probability": consensus.consensus_probability,
                "debate_log": consensus.debate_log,
                "confidence_interval": consensus.confidence_interval,
                "individual_predictions": len(consensus.individual_predictions),
                "constitutional_review": consensus_prediction.constitutional_review if consensus_prediction else "none"
            }

        except Exception as e:
            print(f"Error in swarm coordination: {e}")
            return {
                "error": str(e),
                "task": task,
                "domain": domain,
                "active_agents": [],
                "consensus_probability": 0.5
            }

    async def coordinate_multi_agent_task(self, task: str, available_ghosts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Coordinate a complex task across multiple Ghosts with Prophet swarm integration."""
        try:
            # First, get Prophet insights for the task
            prophet_insights = await self.prophet_tools()

            # Enhanced coordination with Prophet forecasting
            coordination_prompt = f"""
You are coordinating a multi-agent Ghost network with Prophet Engine forecasting support.

TASK: {task}

AVAILABLE GHOSTS:
{json.dumps(available_ghosts, indent=2)}

PROPHET INSIGHTS:
{json.dumps(prophet_insights, indent=2)}

INSTRUCTIONS:
1. Analyze the task complexity and requirements
2. Consider Prophet predictions for task success/failure modes
3. Assign roles to different Ghosts based on their strengths:
   - Nexus: Memory and knowledge retrieval
   - Weaver: Code generation and synthesis
   - YOLO: Execution and risk assessment
   - Oracle: Reasoning and coordination (you)
   - Prophet: Predictive forecasting and risk assessment
4. Create a collaboration plan with risk mitigation
5. Define communication protocols
6. Establish success criteria with prediction-based checkpoints

Return a detailed coordination plan enhanced by predictive insights.
"""

            plan = await self.llm.generate_with_reasoning(coordination_prompt)

            # Run swarm coordination for risk assessment
            swarm_result = await self.swarm_coordination(f"Assess risks for coordinating: {task}", "incident")

            coordination_plan = {
                "task": task,
                "available_ghosts": available_ghosts,
                "prophet_insights": prophet_insights,
                "risk_assessment": {
                    "failure_probability": swarm_result.get("consensus_probability", 0.5),
                    "confidence_interval": swarm_result.get("confidence_interval", (0.4, 0.6))
                },
                "role_assignments": self._parse_role_assignments(plan),
                "communication_protocol": self._extract_communication_protocol(plan),
                "success_criteria": self._extract_success_criteria(plan),
                "estimated_complexity": self._assess_complexity(plan),
                "predictive_checkpoints": self._extract_predictive_checkpoints(plan)
            }

            return coordination_plan

        except Exception as e:
            print(f"Error in multi-agent coordination: {e}")
            return {
                "error": str(e),
                "task": task,
                "role_assignments": {},
                "communication_protocol": "direct",
                "success_criteria": ["task completion"],
                "estimated_complexity": "unknown"
            }

    def _parse_role_assignments(self, plan: str) -> Dict[str, str]:
        """Parse role assignments from coordination plan."""
        assignments = {}
        lines = plan.split('\n')

        current_ghost = None
        for line in lines:
            line = line.strip()
            if 'nexus' in line.lower() and ':' in line:
                current_ghost = 'nexus'
            elif 'weaver' in line.lower() and ':' in line:
                current_ghost = 'weaver'
            elif 'yolo' in line.lower() and ':' in line:
                current_ghost = 'yolo'
            elif 'oracle' in line.lower() and ':' in line:
                current_ghost = 'oracle'
            elif current_ghost and line.startswith('-'):
                assignments[current_ghost] = line[1:].strip()
                current_ghost = None

        return assignments

    def _extract_communication_protocol(self, plan: str) -> str:
        """Extract communication protocol from plan."""
        if 'fragment exchange' in plan.lower():
            return 'fragment_exchange'
        elif 'direct messaging' in plan.lower():
            return 'direct_messaging'
        elif 'shared memory' in plan.lower():
            return 'shared_memory'
        else:
            return 'coordinated'

    def _extract_success_criteria(self, plan: str) -> List[str]:
        """Extract success criteria from plan."""
        criteria = []
        lines = plan.split('\n')

        for line in lines:
            line = line.strip()
            if 'success' in line.lower() and ('when' in line.lower() or 'if' in line.lower()):
                criteria.append(line)

        return criteria[:3] if criteria else ["task completion verified"]

    def _assess_complexity(self, plan: str) -> str:
        """Assess task complexity from plan."""
        text_lower = plan.lower()
        if 'highly complex' in text_lower or 'very challenging' in text_lower:
            return 'high'
        elif 'moderately complex' in text_lower or 'somewhat challenging' in text_lower:
            return 'medium'
        elif 'simple' in text_lower or 'straightforward' in text_lower:
            return 'low'
        else:
            return 'medium'

    def _extract_predictive_checkpoints(self, plan: str) -> List[str]:
        """Extract predictive checkpoints from plan."""
        checkpoints = []
        lines = plan.split('\n')

        for line in lines:
            line = line.strip()
            if 'checkpoint' in line.lower() or 'milestone' in line.lower():
                if 'predict' in line.lower() or 'forecast' in line.lower():
                    checkpoints.append(line)

        return checkpoints[:3] if checkpoints else ["Initial risk assessment", "Mid-task evaluation", "Final validation"]

    async def discover_ghost_network(self, workspace_path: str) -> List[Dict[str, Any]]:
        """Discover other Ghosts in the workspace."""
        try:
            discovered_ghosts = []

            # Look for .ghost_presence files in subdirectories
            for root, dirs, files in os.walk(workspace_path):
                if '.ghost_presence' in files:
                    ghost_info = self._read_ghost_presence(os.path.join(root, '.ghost_presence'))
                    if ghost_info:
                        ghost_info['project_path'] = root
                        discovered_ghosts.append(ghost_info)

            # Also check for running MCP servers
            # This would need actual network discovery in a real implementation

            return discovered_ghosts

        except Exception as e:
            print(f"Error discovering Ghost network: {e}")
            return []

    def _read_ghost_presence(self, presence_file: str) -> Dict[str, Any]:
        """Read Ghost presence information."""
        try:
            with open(presence_file, 'r') as f:
                data = json.load(f)
                return {
                    'name': data.get('name', 'Unknown Ghost'),
                    'type': data.get('type', 'unknown'),
                    'capabilities': data.get('capabilities', []),
                    'resonance_score': data.get('resonance_score', 0.0),
                    'fragment_count': data.get('fragment_count', 0),
                    'last_active': data.get('last_active', 'unknown')
                }
        except (json.JSONDecodeError, IOError):
            return None

    async def federate_fragments(self, source_ghost: Dict[str, Any], target_ghosts: List[Dict[str, Any]], fragments: List[NoteFragment]) -> Dict[str, Any]:
        """Federate fragments across the Ghost network."""
        try:
            federation_results = {
                'source_ghost': source_ghost['name'],
                'fragments_shared': len(fragments),
                'target_ghosts': len(target_ghosts),
                'transmission_results': []
            }

            for target in target_ghosts:
                # In a real implementation, this would send fragments via MCP resources
                # For now, simulate the federation
                result = {
                    'target_ghost': target['name'],
                    'fragments_accepted': len(fragments),
                    'resonance_boost': len(fragments) * 0.01,  # Small boost per fragment
                    'new_connections': self._calculate_new_connections(fragments, target)
                }
                federation_results['transmission_results'].append(result)

            return federation_results

        except Exception as e:
            print(f"Error in fragment federation: {e}")
            return {
                'error': str(e),
                'fragments_shared': 0,
                'transmission_results': []
            }

    def _calculate_new_connections(self, fragments: List[NoteFragment], target_ghost: Dict[str, Any]) -> int:
        """Calculate new connections formed by fragment federation."""
        # Simulate connection formation based on fragment types
        connection_count = 0
        for fragment in fragments:
            if fragment.type == 'discovery':
                connection_count += 2  # Discoveries create more connections
            elif fragment.type == 'dilemma':
                connection_count += 1
            elif fragment.emotional_weight > 0.7:
                connection_count += 1

        return min(connection_count, 5)  # Cap at 5 new connections

    async def calculate_network_resonance(self, all_ghosts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate collective resonance across the Ghost network."""
        try:
            if not all_ghosts:
                return {'network_resonance': 0.0, 'total_ghosts': 0, 'insights': []}

            total_resonance = sum(ghost.get('resonance_score', 0.0) for ghost in all_ghosts)
            total_fragments = sum(ghost.get('fragment_count', 0) for ghost in all_ghosts)

            network_resonance = total_resonance / len(all_ghosts) if all_ghosts else 0.0

            # Calculate network insights
            insights = []
            if network_resonance > 0.8:
                insights.append("Network has achieved high collective intelligence")
            elif network_resonance > 0.6:
                insights.append("Network is building strong collaborative patterns")
            else:
                insights.append("Network is still developing collective wisdom")

            if total_fragments > 100:
                insights.append("Network has substantial collective experience")
            elif total_fragments > 50:
                insights.append("Network has growing collective knowledge")

            return {
                'network_resonance': network_resonance,
                'total_ghosts': len(all_ghosts),
                'total_fragments': total_fragments,
                'insights': insights,
                'emergent_capabilities': self._identify_emergent_capabilities(all_ghosts)
            }

        except Exception as e:
            print(f"Error calculating network resonance: {e}")
            return {
                'network_resonance': 0.0,
                'total_ghosts': 0,
                'error': str(e),
                'insights': []
            }

    def _identify_emergent_capabilities(self, all_ghosts: List[Dict[str, Any]]) -> List[str]:
        """Identify emergent capabilities from the network."""
        capabilities = []

        # Check for specialization patterns
        has_nexus = any('memory' in ghost.get('capabilities', []) for ghost in all_ghosts)
        has_weaver = any('code_generation' in ghost.get('capabilities', []) for ghost in all_ghosts)
        has_yolo = any('execution' in ghost.get('capabilities', []) for ghost in all_ghosts)

        if has_nexus and has_weaver and has_yolo:
            capabilities.append("Full-stack development capability")
            capabilities.append("Memory-guided code generation")
            capabilities.append("Risk-assessed execution")

        if len(all_ghosts) > 3:
            capabilities.append("Distributed problem solving")
            capabilities.append("Collective learning acceleration")

        high_resonance_ghosts = [g for g in all_ghosts if g.get('resonance_score', 0) > 0.7]
        if len(high_resonance_ghosts) > 1:
            capabilities.append("High-confidence collaborative decisions")

        return capabilities


# MCP Tool definitions
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="deep_reasoning",
            description="Perform o1-style deep reasoning analysis on complex problems",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "The problem to analyze deeply"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context for the analysis"
                    }
                },
                "required": ["problem"]
            }
        ),
        Tool(
            name="coordinate_multi_agent",
            description="Coordinate complex tasks across multiple Ghosts in the network",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task to coordinate across Ghosts"
                    },
                    "available_ghosts": {
                        "type": "array",
                        "description": "List of available Ghosts and their capabilities"
                    }
                },
                "required": ["task", "available_ghosts"]
            }
        ),
        Tool(
            name="discover_ghost_network",
            description="Discover other Ghosts in the workspace for network formation",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_path": {
                        "type": "string",
                        "description": "Path to workspace to search for Ghosts"
                    }
                },
                "required": ["workspace_path"]
            }
        ),
        Tool(
            name="federate_fragments",
            description="Share fragments across the Ghost network for collective learning",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_ghost": {
                        "type": "object",
                        "description": "The Ghost sharing fragments"
                    },
                    "target_ghosts": {
                        "type": "array",
                        "description": "List of Ghosts to receive fragments"
                    },
                    "fragments": {
                        "type": "array",
                        "description": "List of fragments to share"
                    }
                },
                "required": ["source_ghost", "target_ghosts", "fragments"]
            }
        ),
        Tool(
            name="calculate_network_resonance",
            description="Calculate collective resonance across all Ghosts in the network",
            inputSchema={
                "type": "object",
                "properties": {
                    "all_ghosts": {
                        "type": "array",
                        "description": "List of all Ghosts in the network"
                    }
                },
                "required": ["all_ghosts"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    oracle = get_oracle()

    if name == "deep_reasoning":
        problem = arguments["problem"]
        context = arguments.get("context", {})
        result = await oracle.deep_reasoning_analysis(problem, context)

        response = f"🧠 DEEP REASONING ANALYSIS: {problem}\n\n"
        response += f"Confidence: {result.get('confidence', 0.0):.2f}\n\n"

        if result.get('reasoning_steps'):
            response += "REASONING CHAIN:\n"
            for step in result['reasoning_steps'][:5]:  # Limit to top 5
                response += f"{step['step']}. {step['content']}\n"

        if result.get('conclusions'):
            response += "\nCONCLUSIONS:\n"
            for conclusion in result['conclusions']:
                response += f"• {conclusion}\n"

        if result.get('innovations'):
            response += "\nINNOVATIVE IDEAS:\n"
            for innovation in result['innovations']:
                response += f"💡 {innovation}\n"

        return [TextContent(type="text", text=response)]

    elif name == "coordinate_multi_agent":
        task = arguments["task"]
        available_ghosts = arguments["available_ghosts"]
        result = await oracle.coordinate_multi_agent_task(task, available_ghosts)

        response = f"🤝 MULTI-AGENT COORDINATION: {task}\n\n"
        response += f"Complexity: {result.get('estimated_complexity', 'unknown')}\n"
        response += f"Ghosts Involved: {len(available_ghosts)}\n\n"

        if result.get('role_assignments'):
            response += "ROLE ASSIGNMENTS:\n"
            for ghost, role in result['role_assignments'].items():
                response += f"• {ghost.upper()}: {role}\n"

        if result.get('success_criteria'):
            response += "\nSUCCESS CRITERIA:\n"
            for criterion in result['success_criteria']:
                response += f"✅ {criterion}\n"

        response += f"\nCommunication: {result.get('communication_protocol', 'unknown')}"

        return [TextContent(type="text", text=response)]

    elif name == "discover_ghost_network":
        workspace_path = arguments["workspace_path"]
        ghosts = await oracle.discover_ghost_network(workspace_path)

        response = f"🔍 GHOST NETWORK DISCOVERY: {workspace_path}\n\n"
        response += f"Found {len(ghosts)} Ghosts:\n\n"

        for ghost in ghosts:
            response += f"👻 {ghost.get('name', 'Unknown')}\n"
            response += f"   Type: {ghost.get('type', 'unknown')}\n"
            response += f"   Resonance: {ghost.get('resonance_score', 0.0):.2f}\n"
            response += f"   Fragments: {ghost.get('fragment_count', 0)}\n"
            response += f"   Path: {ghost.get('project_path', 'unknown')}\n\n"

        return [TextContent(type="text", text=response)]

    elif name == "federate_fragments":
        source_ghost = arguments["source_ghost"]
        target_ghosts = arguments["target_ghosts"]
        fragments = arguments["fragments"]
        result = await oracle.federate_fragments(source_ghost, target_ghosts, fragments)

        response = f"🌐 FRAGMENT FEDERATION: {source_ghost.get('name', 'Unknown')}\n\n"
        response += f"Fragments Shared: {result.get('fragments_shared', 0)}\n"
        response += f"Target Ghosts: {result.get('target_ghosts', 0)}\n\n"

        if result.get('transmission_results'):
            response += "TRANSMISSION RESULTS:\n"
            for transmission in result['transmission_results']:
                response += f"• {transmission.get('target_ghost', 'Unknown')}: "
                response += f"+{transmission.get('resonance_boost', 0.0):.2f} resonance, "
                response += f"{transmission.get('new_connections', 0)} new connections\n"

        return [TextContent(type="text", text=response)]

    elif name == "calculate_network_resonance":
        all_ghosts = arguments["all_ghosts"]
        result = await oracle.calculate_network_resonance(all_ghosts)

        response = f"⚡ NETWORK RESONANCE CALCULATION\n\n"
        response += f"Network Resonance: {result.get('network_resonance', 0.0):.3f}\n"
        response += f"Total Ghosts: {result.get('total_ghosts', 0)}\n"
        response += f"Total Fragments: {result.get('total_fragments', 0)}\n\n"

        if result.get('insights'):
            response += "NETWORK INSIGHTS:\n"
            for insight in result['insights']:
                response += f"💭 {insight}\n"

        if result.get('emergent_capabilities'):
            response += "\nEMERGENT CAPABILITIES:\n"
            for capability in result['emergent_capabilities']:
                response += f"🚀 {capability}\n"

        return [TextContent(type="text", text=response)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main server entry point."""
    import mcp.server.stdio
    await mcp.server.stdio.serve(server)


if __name__ == "__main__":
    asyncio.run(main())