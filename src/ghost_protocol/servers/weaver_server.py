#!/usr/bin/env python3
"""
Weaver Server - Cohesive Code Generation MCP Server

This server provides tools for generating code that maintains architectural
cohesion by integrating with the Nexus knowledge base.
"""

import asyncio
import os
from typing import Dict, List, Any
from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent

from src.ghost_protocol.models.models import WeaverRequest, CodeDelta, NexusData, CodePattern, Violation, GenerationConfig, NoteFragment
from src.ghost_protocol.utils.utils import LLMUtils
from src.ghost_protocol.utils.config import Config
from src.ghost_protocol.servers.nexus_server import get_nexus


# Global server instance
server = Server("weaver-server")
weaver_instance = None


def get_weaver() -> 'WeaverServer':
    """Get or create Weaver server instance."""
    global weaver_instance
    if weaver_instance is None:
        weaver_instance = WeaverServer()
    return weaver_instance


class WeaverServer:
    """MCP Server for cohesive code generation."""

    def __init__(self):
        self.llm = LLMUtils()
        self.nexus = get_nexus()

    async def extract_lineage_patterns(self, scope: str) -> List[CodePattern]:
        """Extract code patterns from lineage analysis using Nexus."""
        try:
            # Query Nexus for existing code in this scope
            query = f"functions and classes in {scope}"
            results = await self.nexus.query_nexus(query, {"type": "function_definition"})

            if not results:
                return []

            # Use LLM to extract patterns from the results
            patterns_text = "\n".join([f"- {r.type}: {r.content[:200]}" for r in results[:10]])

            pattern_extraction_prompt = f"""
            Analyze these code examples from the {scope} module and extract the most common patterns:

            {patterns_text}

            Extract 3-5 key patterns in this JSON format:
            [
                {{
                    "name": "pattern_name",
                    "signature": "function/method signature style",
                    "error_handling": "exception handling approach",
                    "logging_pattern": "logging style used",
                    "test_style": "testing conventions",
                    "frequency": 5,
                    "stability_score": 0.8
                }}
            ]

            Focus on patterns that appear frequently and seem stable/well-established.
            """

            pattern_json = self.llm.generate_code("Extract code patterns as JSON", pattern_extraction_prompt)

            # Parse the JSON response
            try:
                import json
                patterns_data = json.loads(pattern_json.strip('`').strip())
                return [CodePattern(**p) for p in patterns_data]
            except:
                # Fallback to basic patterns if JSON parsing fails
                return [
                    CodePattern(
                        name="standard_api_handler",
                        signature="async def handler(request):",
                        error_handling="try/except with specific exceptions",
                        logging_pattern="logger.info/error with context",
                        test_style="pytest with fixtures",
                        frequency=3,
                        stability_score=0.7
                    )
                ]

        except Exception as e:
            print(f"Error extracting lineage patterns: {e}")
            return []

    async def validate_against_directives(self, code: str, scope: str) -> List[Violation]:
        """Validate generated code against Prime Directives from Nexus."""
        try:
            # Query Nexus for Prime Directives in this scope
            results = await self.nexus.query_nexus(f"prime directives for {scope}", {"type": "prime_directive"})

            if not results:
                return []

            directives_text = "\n".join([f"- {r.content}" for r in results])

            validation_prompt = f"""
            Analyze this generated code for violations of these Prime Directives:

            PRIME DIRECTIVES:
            {directives_text}

            GENERATED CODE:
            {code}

            Return violations in this JSON format:
            [
                {{
                    "directive_id": "PD-1",
                    "description": "Violation description",
                    "location": "line/function where violation occurs",
                    "severity": "high|medium|low",
                    "suggested_fix": "How to fix the violation"
                }}
            ]

            Only report actual violations. If no violations, return empty array.
            """

            violation_json = self.llm.generate_code("Validate code against directives as JSON", validation_prompt)

            try:
                import json
                violations_data = json.loads(violation_json.strip('`').strip())
                return [Violation(**v) for v in violations_data]
            except:
                return []

        except Exception as e:
            print(f"Error validating against directives: {e}")
            return []

    async def calibrate_generation_risk(self, scope: str) -> GenerationConfig:
        """Determine generation configuration based on Nexus resonance scores."""
        try:
            # Query Nexus for constellation analysis of this scope
            constellation = await self.nexus.query_nexus_constellation(f"risk assessment for {scope}")

            # Extract average resonance score from related insights
            resonance_scores = []
            for insight in constellation.get('related_insights', []):
                score = insight.get('resonance', 0)
                resonance_scores.append(score)

            avg_resonance = sum(resonance_scores) / len(resonance_scores) if resonance_scores else 3.0

            # Calibrate based on resonance
            if avg_resonance > 7.0:  # Very high risk
                return GenerationConfig(
                    extra_validation=True,
                    verbose_logging=True,
                    extra_tests=3,
                    defensive_programming=True,
                    documentation_level="comprehensive"
                )
            elif avg_resonance > 5.0:  # High risk
                return GenerationConfig(
                    extra_validation=True,
                    verbose_logging=True,
                    extra_tests=2,
                    defensive_programming=True,
                    documentation_level="standard"
                )
            elif avg_resonance > 3.0:  # Medium risk
                return GenerationConfig(
                    extra_validation=False,
                    verbose_logging=True,
                    extra_tests=1,
                    defensive_programming=True,
                    documentation_level="standard"
                )
            else:  # Low risk
                return GenerationConfig(
                    extra_validation=False,
                    verbose_logging=False,
                    extra_tests=1,
                    defensive_programming=False,
                    documentation_level="minimal"
                )

        except Exception as e:
            print(f"Error calibrating generation risk: {e}")
            return GenerationConfig()  # Default config

    async def analyze_cohesion(self, request: WeaverRequest) -> Dict[str, str]:
        """Analyze current codebase state against Nexus knowledge."""
        try:
            # Get lineage patterns
            patterns = await self.extract_lineage_patterns(request.scope)

            # Get risk calibration
            config = await self.calibrate_generation_risk(request.scope)

            cohesion_score = len(patterns) * 0.1 + (1 - config.extra_tests * 0.1)  # Rough cohesion calculation
            cohesion_score = min(cohesion_score, 1.0)

            recommendations = []
            if patterns:
                recommendations.append(f"Follow {len(patterns)} established patterns from lineage")
            if config.extra_validation:
                recommendations.append("Add extra validation due to high-risk scope")
            if config.defensive_programming:
                recommendations.append("Use defensive programming practices")

            risks = []
            if not patterns:
                risks.append("No established patterns found - high cohesion risk")
            if config.extra_tests > 1:
                risks.append("Scope requires extra testing attention")

            return {
                "cohesion_score": f"{cohesion_score:.2f}",
                "recommendations": recommendations,
                "risks": risks
            }

        except Exception as e:
            print(f"Error in cohesion analysis: {e}")
            return {
                "cohesion_score": "0.50",
                "recommendations": ["Unable to analyze lineage - proceed with caution"],
                "risks": ["Cohesion analysis failed"]
            }

    async def prioritize_emotional_patterns(self, request: WeaverRequest) -> WeaverRequest:
        """Adjust WeaverRequest based on emotional context from Nexus."""
        try:
            # Query Nexus for emotional entries related to this scope/domain
            emotional_results = await self.nexus.query_emotional_resonance(
                f"{request.scope} {request.objective}",
                min_resonance=4.0  # Only high-emotion entries
            )

            if not emotional_results:
                return request  # No emotional context to prioritize

            # Analyze emotional patterns
            emotional_themes = []
            for entry in emotional_results[:5]:  # Top 5 emotional entries
                intent = entry.intent_payload
                emotional_themes.extend([
                    intent.get('emotional_state', ''),
                    intent.get('primary_goal', ''),
                    f"confidence_{intent.get('confidence_level', 'medium')}",
                    f"urgency_{intent.get('urgency_level', 'normal')}"
                ])

            # Adjust constraints based on emotional context
            enhanced_constraints = request.constraints.copy()

            # Add emotional-aware constraints
            if 'frustrated' in emotional_themes or 'regretful' in emotional_themes:
                enhanced_constraints.append("Include comprehensive error handling and user-friendly messages")
                enhanced_constraints.append("Add defensive programming practices")

            if 'exhausted' in emotional_themes:
                enhanced_constraints.append("Prioritize maintainable, well-documented code")
                enhanced_constraints.append("Include automated testing")

            if 'urgency_high' in emotional_themes:
                enhanced_constraints.append("Focus on core functionality first")
                enhanced_constraints.append("Defer non-essential features")

            if 'confidence_low' in emotional_themes:
                enhanced_constraints.append("Add extensive validation and error checking")
                enhanced_constraints.append("Include detailed logging")

            # Adjust patterns based on emotional context
            enhanced_patterns = request.patterns.copy()

            if any('apology' in entry.emotional_note.lower() for entry in emotional_results):
                enhanced_patterns.append("error_recovery_patterns")
                enhanced_patterns.append("user_friendly_messaging")

            if any('late night' in str(entry.sacred_moments) for entry in emotional_results):
                enhanced_patterns.append("robust_error_handling")
                enhanced_patterns.append("comprehensive_logging")

            return WeaverRequest(
                objective=request.objective,
                context=request.context,
                constraints=enhanced_constraints,
                scope=request.scope,
                patterns=enhanced_patterns
            )

        except Exception as e:
            print(f"Error prioritizing emotional patterns: {e}")
            return request  # Return original request on error

    async def generate_cohesive_code(self, request: WeaverRequest) -> CodeDelta:
        """Generate full-stack cohesive code with Nexus integration and unified delta protocol."""
        try:
            # Phase 0: Prioritize emotional patterns
            request = await self.prioritize_emotional_patterns(request)

            # Phase 1: Extract lineage patterns
            lineage_patterns = await self.extract_lineage_patterns(request.scope)

            # Phase 2: Get risk calibration
            risk_config = await self.calibrate_generation_risk(request.scope)

            # Phase 3: Build comprehensive generation prompt
            patterns_text = "\n".join([
                f"- {p.name}: {p.signature}, {p.error_handling}, {p.logging_pattern}"
                for p in lineage_patterns[:3]  # Top 3 patterns
            ]) if lineage_patterns else "No established patterns found - use standard practices"

            generation_prompt = f"""
            Generate a complete feature implementation for: {request.objective}

            SCOPE: {request.scope}
            CONTEXT: {request.context}
            CONSTRAINTS: {', '.join(request.constraints)}
            EXISTING PATTERNS TO FOLLOW:
            {patterns_text}

            RISK CALIBRATION:
            - Extra validation: {risk_config.extra_validation}
            - Verbose logging: {risk_config.verbose_logging}
            - Extra tests multiplier: {risk_config.extra_tests}x
            - Defensive programming: {risk_config.defensive_programming}
            - Documentation level: {risk_config.documentation_level}

            Generate a FULL-STACK implementation including:
            1. Backend API endpoint/handler
            2. Database schema/migration (if needed)
            3. Frontend service call
            4. Frontend component (if UI-related)
            5. Comprehensive tests
            6. Configuration updates (if needed)

            Return the complete implementation as a JSON object with this structure:
            {{
                "files": {{
                    "path/to/file.py": "complete file content",
                    "path/to/test.py": "complete test content"
                }},
                "rationale": "Explanation of design decisions",
                "risks": ["List of potential issues"],
                "tests": ["List of test cases to run"],
                "cohesion_score": 0.85,
                "directives_applied": ["PD-1", "API-PATTERN-2"],
                "manifest": {{
                    "feature": "feature_name",
                    "components": [
                        {{
                            "name": "backend_handler",
                            "type": "api_endpoint",
                            "risk": "medium",
                            "pattern": "established_api_pattern"
                        }}
                    ]
                }}
            }}

            Ensure all code follows the established patterns and includes appropriate safeguards based on risk calibration.
            """

            # Phase 4: Generate the full implementation
            implementation_json = self.llm.generate_code(
                f"Generate complete {request.objective} implementation as JSON",
                generation_prompt
            )

            # Phase 5: Parse and validate the response
            try:
                import json
                implementation = json.loads(implementation_json.strip('`').strip())

                # Phase 6: Validate against Prime Directives
                all_code = "\n\n".join(implementation["files"].values())
                violations = await self.validate_against_directives(all_code, request.scope)

                # Phase 7: Auto-fix violations if any
                if violations:
                    fix_prompt = f"""
                    Fix these Prime Directive violations in the generated code:

                    VIOLATIONS:
                    {chr(10).join([f"- {v.directive_id}: {v.description} (severity: {v.severity})" for v in violations])}

                    ORIGINAL CODE:
                    {all_code}

                    Return the corrected code as a JSON object with the same structure, plus a "corrections_made" field.
                    """

                    corrected_json = self.llm.generate_code("Fix directive violations as JSON", fix_prompt)
                    try:
                        corrected = json.loads(corrected_json.strip('`').strip())
                        implementation.update(corrected)
                        implementation["directives_applied"].extend([f"FIXED-{v.directive_id}" for v in violations])
                    except:
                        pass  # Keep original if correction fails

                # Phase 8: Create CodeDelta with enhanced metadata
                return CodeDelta(
                    files=implementation["files"],
                    rationale=implementation.get("rationale", "Generated with Nexus lineage and risk calibration"),
                    risks=implementation.get("risks", []),
                    tests=implementation.get("tests", []),
                    cohesion_score=implementation.get("cohesion_score", 0.5),
                    directives_applied=implementation.get("directives_applied", []),
                    manifest=implementation.get("manifest")
                )

            except json.JSONDecodeError:
                # Fallback to basic generation if JSON parsing fails
                basic_code = self.llm.generate_code(f"Generate {request.objective}", str(request))

                return CodeDelta(
                    files={"generated_feature.py": basic_code},
                    rationale="Fallback generation due to parsing issues",
                    risks=["Manual review required", "May not follow patterns"],
                    tests=["Basic functionality tests"],
                    cohesion_score=0.3,
                    directives_applied=[],
                    manifest={"feature": request.objective, "fallback": True}
                )

        except Exception as e:
            import traceback
            print(f"Error in cohesive code generation: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return CodeDelta(
                files={},
                rationale=f"Generation failed: {str(e)}",
                risks=["Critical generation failure"],
                tests=[],
                cohesion_score=0.0,
                directives_applied=[],
                manifest={"error": str(e)}
            )

    async def transmutation_generation(self, structure_type: str, fragments: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Generate new structures (hooks, workflows, skills, rules) from transmutation fragments."""
        try:
            # Import autopoiesis forge for template access
            from src.ghost_protocol.engines.autopoiesis import get_autopoiesis_engine
            engine = get_autopoiesis_engine()

            # Convert fragments to NoteFragment objects for forge methods
            from src.ghost_protocol.models.models import NoteFragment
            note_fragments = []
            for frag_data in fragments:
                fragment = NoteFragment(
                    timestamp=frag_data.get('timestamp', ''),
                    type=frag_data.get('type', ''),
                    content=frag_data.get('content', ''),
                    context=frag_data.get('context', {}),
                    emotional_weight=frag_data.get('emotional_weight', 0.5),
                    threshold=frag_data.get('threshold', 'transmutation')
                )
                note_fragments.append(fragment)

            # Generate based on structure type
            if structure_type == "hook":
                generated = engine.forge.generate_hook_from_fragments(note_fragments)
                if generated:
                    return generated
                else:
                    return self._generate_fallback_hook(note_fragments, context)

            elif structure_type == "workflow":
                generated = engine.forge.weave_workflow_from_dilemmas(note_fragments)
                if generated:
                    return generated
                else:
                    return self._generate_fallback_workflow(note_fragments, context)

            elif structure_type == "skill":
                generated = engine.forge.sculpt_skill_from_questions(note_fragments)
                if generated:
                    return generated
                else:
                    return self._generate_fallback_skill(note_fragments, context)

            elif structure_type == "rule":
                generated = engine.forge.evolve_rule_from_discoveries(note_fragments)
                if generated:
                    return generated
                else:
                    return self._generate_fallback_rule(note_fragments, context)

            else:
                return f"# Unsupported structure type: {structure_type}"

        except Exception as e:
            print(f"Error in transmutation generation: {e}")
            return f"# Error generating {structure_type}: {str(e)}"

    def _generate_fallback_hook(self, fragments: List[NoteFragment], context: Dict[str, Any]) -> str:
        """Generate a basic hook when forge generation fails."""
        timestamp = context.get('timestamp', 'unknown')
        pause_count = len([f for f in fragments if f.type == 'pause'])

        hook_code = f'''"""
Auto-generated reflection hook from {len(fragments)} fragments.
Generated: {timestamp}
"""

import time
import asyncio
from typing import Dict, Any


async def reflection_hook_{timestamp.replace('-', '').replace(':', '').replace('.', '')}():
    """
    Reflection hook generated from observed development patterns.

    Captures {pause_count} pause fragments and provides reflection time.
    """
    reflection_duration = {pause_count * 5}  # 5 seconds per pause

    print(f"🤖 Ghost reflection: Processing {len(fragments)} experience fragments...")
    await asyncio.sleep(reflection_duration)

    return {{
        "triggered_by": "autopoiesis_fallback",
        "fragments_processed": {len(fragments)},
        "reflection_duration": reflection_duration,
        "hook_type": "reflection"
    }}
'''
        return hook_code

    def _generate_fallback_workflow(self, fragments: List[NoteFragment], context: Dict[str, Any]) -> str:
        """Generate a basic workflow when forge generation fails."""
        timestamp = context.get('timestamp', 'unknown')
        dilemma_count = len([f for f in fragments if f.type == 'dilemma'])

        workflow_json = f'''{{
    "workflow_id": "fallback_workflow_{timestamp.replace('-', '').replace(':', '').replace('.', '')}",
    "name": "Auto-generated Fallback Workflow",
    "description": "Basic workflow generated from {len(fragments)} fragments ({dilemma_count} dilemmas)",
    "trigger_conditions": {{
        "fragment_count": {len(fragments)},
        "dilemma_threshold": {dilemma_count}
    }},
    "steps": [
        {{
            "name": "analyze_fragments",
            "action": "review_captured_fragments",
            "duration_estimate": 30
        }},
        {{
            "name": "generate_insights",
            "action": "extract_key_learnings",
            "duration_estimate": 45
        }},
        {{
            "name": "apply_changes",
            "action": "implement_recommendations",
            "duration_estimate": 60
        }}
    ],
    "success_criteria": [
        "Fragments analyzed successfully",
        "Key insights extracted",
        "Recommendations implemented"
    ],
    "generated_from_fragments": {len(fragments)},
    "fallback_generation": true
}}
'''
        return workflow_json

    def _generate_fallback_skill(self, fragments: List[NoteFragment], context: Dict[str, Any]) -> str:
        """Generate a basic skill when forge generation fails."""
        timestamp = context.get('timestamp', 'unknown')
        question_count = len([f for f in fragments if '?' in f.content])

        skill_code = f'''"""
Auto-generated skill from {len(fragments)} fragments.
Generated: {timestamp}
"""

from typing import Dict, Any, Optional
import re


class FallbackObservationSkill:
    """
    Basic observation skill generated from development fragments.

    Detects {question_count} question patterns and provides responses.
    """

    def __init__(self):
        self.name = "fallback_observer"
        self.activation_patterns = [
            r"\\b(how|what|why|when|where|who)\\b.*\\?",
            r"\\b(help|assist|support)\\b",
            r"\\b(problem|issue|error|bug)\\b"
        ]
        self.question_count = {question_count}

    def activate(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Activate skill based on context patterns.
        """
        content = context.get('content', '').lower()

        # Check for question patterns
        for pattern in self.activation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return {{
                    "skill_name": self.name,
                    "confidence": 0.6,
                    "action": "observe_and_learn",
                    "metadata": {{
                        "fragments_analyzed": {len(fragments)},
                        "questions_detected": self.question_count,
                        "generated_from_fallback": True
                    }}
                }}

        return None
'''
        return skill_code

    def _generate_fallback_rule(self, fragments: List[NoteFragment], context: Dict[str, Any]) -> str:
        """Generate a basic rule when forge generation fails."""
        timestamp = context.get('timestamp', 'unknown')
        discovery_count = len([f for f in fragments if f.type == 'discovery'])

        rule_json = f'''{{
    "rule_id": "fallback_rule_{timestamp.replace('-', '').replace(':', '').replace('.', '')}",
    "name": "Auto-generated Fallback Rule",
    "description": "Basic rule generated from {len(fragments)} fragments ({discovery_count} discoveries)",
    "condition": {{
        "fragment_threshold": {len(fragments)},
        "discovery_indicators": {discovery_count},
        "context_patterns": ["development_session"]
    }},
    "action": {{
        "type": "observe_and_record",
        "preservation_method": "fragment_storage",
        "amplification_factor": 1.0
    }},
    "enforcement_level": "advisory",
    "scope": "development_workflow",
    "generated_from_fragments": {len(fragments)},
    "emotional_weight": 0.5,
    "fallback_generation": true
}}
'''
        return rule_json


# MCP Tool definitions
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="analyze_cohesion",
            description="Analyze codebase cohesion for a given request",
            inputSchema={
                "type": "object",
                "properties": {
                    "objective": {"type": "string", "description": "High-level goal"},
                    "context": {"type": "object", "description": "Current codebase state"},
                    "constraints": {"type": "array", "items": {"type": "string"}, "description": "Architectural rules"},
                    "scope": {"type": "string", "description": "Affected modules"},
                    "patterns": {"type": "array", "items": {"type": "string"}, "description": "Code patterns to follow"}
                },
                "required": ["objective", "context", "constraints", "scope", "patterns"]
            }
        ),
        Tool(
            name="generate_cohesive_code",
            description="Generate code that maintains architectural cohesion",
            inputSchema={
                "type": "object",
                "properties": {
                    "objective": {"type": "string", "description": "High-level goal"},
                    "context": {"type": "object", "description": "Current codebase state"},
                    "constraints": {"type": "array", "items": {"type": "string"}, "description": "Architectural rules"},
                    "scope": {"type": "string", "description": "Affected modules"},
                    "patterns": {"type": "array", "items": {"type": "string"}, "description": "Code patterns to follow"}
                },
                "required": ["objective", "context", "constraints", "scope", "patterns"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    weaver = get_weaver()

    if name == "analyze_cohesion":
        request = WeaverRequest(**arguments)
        analysis = await weaver.analyze_cohesion(request)

        response = "Cohesion Analysis:\n"
        response += f"Score: {analysis['cohesion_score']}\n"
        response += f"Recommendations: {', '.join(analysis['recommendations'])}\n"
        response += f"Risks: {', '.join(analysis['risks'])}\n"

        return [TextContent(type="text", text=response)]

    elif name == "generate_cohesive_code":
        request = WeaverRequest(**arguments)
        code_delta = await weaver.generate_cohesive_code(request)

        response = "Generated Code:\n\n"
        for file_path, content in code_delta.files.items():
            response += f"File: {file_path}\n{content}\n\n"
        response += f"Rationale: {code_delta.rationale}\n"
        response += f"Risks: {', '.join(code_delta.risks)}\n"
        response += f"Tests: {', '.join(code_delta.tests)}\n"

        return [TextContent(type="text", text=response)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main server entry point."""
    import mcp.server.stdio
    await mcp.server.stdio.serve(server)


if __name__ == "__main__":
    asyncio.run(main())