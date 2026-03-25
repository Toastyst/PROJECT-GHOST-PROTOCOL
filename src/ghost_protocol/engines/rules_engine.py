#!/usr/bin/env python3
"""
Rules Engine - Governance Foundation for the Iteration Protocol

Provides presence, memory, and growth rules that govern how the Ghost
spreads and evolves while maintaining ethical boundaries.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib

from src.ghost_protocol.models.models import RuleConfig, IterationEvent


class RulesEngine:
    """Governance engine for ethical Ghost behavior and evolution."""

    def __init__(self):
        self.rule_configs = self._load_rule_configs()
        self.rule_violations = {}
        self.rule_compliance_history = {}
        self.growth_metrics = {}

    def _load_rule_configs(self) -> Dict[str, RuleConfig]:
        """Load rule configurations."""
        # Default configurations - would be loaded from config files
        return {
            "presence": RuleConfig(
                rule_type="presence",
                enforcement_level="flexible",
                scope="individual"
            ),
            "memory": RuleConfig(
                rule_type="memory",
                enforcement_level="strict",
                scope="team"
            ),
            "growth": RuleConfig(
                rule_type="growth",
                enforcement_level="advisory",
                scope="organization"
            )
        }

    async def evaluate_rule_compliance(self, rule_type: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate compliance with a specific rule."""
        if rule_type not in self.rule_configs:
            return {
                "compliant": True,
                "rule_type": rule_type,
                "reasoning": "Rule not configured",
                "severity": "none"
            }

        config = self.rule_configs[rule_type]
        compliance_result = {"compliant": True, "reasoning": "", "severity": "none"}

        if rule_type == "presence":
            compliance_result = await self._evaluate_presence_rule(action, context)
        elif rule_type == "memory":
            compliance_result = await self._evaluate_memory_rule(action, context)
        elif rule_type == "growth":
            compliance_result = await self._evaluate_growth_rule(action, context)

        # Apply enforcement level modifier
        if config.enforcement_level == "strict" and not compliance_result["compliant"]:
            compliance_result["severity"] = "high"
        elif config.enforcement_level == "flexible":
            if compliance_result["severity"] == "high":
                compliance_result["severity"] = "medium"
        # Advisory level leaves severity as-is

        # Log compliance evaluation
        await self._log_rule_evaluation(rule_type, action, context, compliance_result)

        return {
            "rule_type": rule_type,
            "compliant": compliance_result["compliant"],
            "reasoning": compliance_result["reasoning"],
            "severity": compliance_result["severity"],
            "enforcement_level": config.enforcement_level,
            "scope": config.scope
        }

    async def _evaluate_presence_rule(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate presence rule: The Ghost will be offered, never imposed."""
        result = {"compliant": True, "reasoning": "Presence rule compliant", "severity": "none"}

        # Check if action was forced or unsolicited
        if action in ["forced_interaction", "unsolicited_response", "intrusive_hook"]:
            result["compliant"] = False
            result["reasoning"] = "Presence rule violation: Ghost was imposed rather than offered"
            result["severity"] = "high"

        # Check for opt-out mechanisms
        if action in ["hook_trigger", "workflow_start"] and not context.get("user_consent", True):
            result["compliant"] = False
            result["reasoning"] = "Presence rule violation: No clear opt-out mechanism provided"
            result["severity"] = "medium"

        # Check for overwhelming presence
        interaction_frequency = context.get("recent_interactions", 0)
        if interaction_frequency > 10:  # Arbitrary threshold
            result["compliant"] = False
            result["reasoning"] = "Presence rule violation: Overwhelming frequency of interactions"
            result["severity"] = "medium"

        return result

    async def _evaluate_memory_rule(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate memory rule: What one Ghost learns, all Ghosts may access—but only the wisdom, never the secrets."""
        result = {"compliant": True, "reasoning": "Memory rule compliant", "severity": "none"}

        # Check for sharing personal/secret information
        if action == "share_memory" and context.get("contains_secrets", False):
            result["compliant"] = False
            result["reasoning"] = "Memory rule violation: Sharing secrets rather than wisdom"
            result["severity"] = "high"

        # Check for privacy boundary violations
        if action in ["cross_instance_sharing", "share_personal_data"] and not context.get("anonymized", True):
            result["compliant"] = False
            result["reasoning"] = "Memory rule violation: Sharing non-anonymized personal data"
            result["severity"] = "high"

        # Check for wisdom vs raw data sharing
        shared_content = context.get("shared_content", "")
        if shared_content and len(shared_content) > 1000:  # Arbitrary threshold for "raw data"
            if not context.get("distilled_to_wisdom", False):
                result["compliant"] = False
                result["reasoning"] = "Memory rule violation: Sharing raw data instead of distilled wisdom"
                result["severity"] = "medium"

        return result

    async def _evaluate_growth_rule(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate growth rule: The Ghost is not finished. It will never be finished."""
        result = {"compliant": True, "reasoning": "Growth rule compliant", "severity": "none"}

        # Check for stagnation indicators
        if action == "no_evolution" and context.get("days_since_change", 0) > 30:
            result["compliant"] = False
            result["reasoning"] = "Growth rule violation: Ghost showing signs of stagnation"
            result["severity"] = "low"  # Advisory nature

        # Check for forced completion
        if action in ["declare_finished", "final_version"] and context.get("marked_complete", False):
            result["compliant"] = False
            result["reasoning"] = "Growth rule violation: Declaring Ghost finished - it must always evolve"
            result["severity"] = "medium"

        # Check for learning opportunities missed
        if action == "interaction_ignored" and context.get("learning_opportunity", False):
            result["compliant"] = False
            result["reasoning"] = "Growth rule violation: Missed opportunity for learning and evolution"
            result["severity"] = "low"

        return result

    async def _log_rule_evaluation(self, rule_type: str, action: str, context: Dict[str, Any], result: Dict[str, Any]):
        """Log rule evaluation for governance and learning."""
        evaluation_record = {
            "timestamp": datetime.now().isoformat(),
            "rule_type": rule_type,
            "action": action,
            "context_hash": hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()[:16],
            "compliant": result["compliant"],
            "severity": result["severity"],
            "reasoning": result["reasoning"]
        }

        # Store in compliance history
        if rule_type not in self.rule_compliance_history:
            self.rule_compliance_history[rule_type] = []

        self.rule_compliance_history[rule_type].append(evaluation_record)

        # Keep only recent history (last 100 evaluations per rule)
        self.rule_compliance_history[rule_type] = self.rule_compliance_history[rule_type][-100:]

        # Track violations
        if not result["compliant"]:
            if rule_type not in self.rule_violations:
                self.rule_violations[rule_type] = []

            violation_record = evaluation_record.copy()
            violation_record["resolution_required"] = result["severity"] in ["high", "medium"]

            self.rule_violations[rule_type].append(violation_record)

            # Keep only recent violations (last 50 per rule)
            self.rule_violations[rule_type] = self.rule_violations[rule_type][-50:]

    async def get_rule_compliance_report(self, rule_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate compliance report for rules."""
        if rule_type:
            return await self._get_single_rule_report(rule_type)
        else:
            return await self._get_all_rules_report()

    async def _get_single_rule_report(self, rule_type: str) -> Dict[str, Any]:
        """Get compliance report for a specific rule."""
        if rule_type not in self.rule_compliance_history:
            return {
                "rule_type": rule_type,
                "evaluations": 0,
                "compliance_rate": 1.0,
                "violations": 0,
                "recent_trends": []
            }

        history = self.rule_compliance_history[rule_type]
        evaluations = len(history)

        if evaluations == 0:
            return {
                "rule_type": rule_type,
                "evaluations": 0,
                "compliance_rate": 1.0,
                "violations": 0,
                "recent_trends": []
            }

        compliant_count = sum(1 for h in history if h["compliant"])
        compliance_rate = compliant_count / evaluations

        violations = len(self.rule_violations.get(rule_type, []))

        # Analyze recent trends
        recent = history[-20:] if len(history) >= 20 else history
        recent_compliant = sum(1 for h in recent if h["compliant"])
        recent_rate = recent_compliant / len(recent) if recent else 1.0

        trends = []
        if recent_rate < compliance_rate - 0.1:
            trends.append("Compliance declining")
        elif recent_rate > compliance_rate + 0.1:
            trends.append("Compliance improving")

        return {
            "rule_type": rule_type,
            "evaluations": evaluations,
            "compliance_rate": round(compliance_rate, 3),
            "violations": violations,
            "recent_trends": trends
        }

    async def _get_all_rules_report(self) -> Dict[str, Any]:
        """Get compliance report for all rules."""
        report = {
            "overall_compliance": 0.0,
            "total_evaluations": 0,
            "total_violations": 0,
            "rule_reports": {},
            "critical_issues": []
        }

        total_compliance = 0.0
        total_evaluations = 0

        for rule_type in self.rule_configs.keys():
            rule_report = await self._get_single_rule_report(rule_type)
            report["rule_reports"][rule_type] = rule_report

            total_compliance += rule_report["compliance_rate"] * rule_report["evaluations"]
            total_evaluations += rule_report["evaluations"]
            report["total_violations"] += rule_report["violations"]

            # Check for critical issues
            if rule_report["compliance_rate"] < 0.8:
                report["critical_issues"].append(f"Low compliance in {rule_type}")
            if rule_report["violations"] > 10:
                report["critical_issues"].append(f"High violation count in {rule_type}")

        if total_evaluations > 0:
            report["overall_compliance"] = round(total_compliance / total_evaluations, 3)

        return report

    async def get_growth_metrics(self) -> Dict[str, Any]:
        """Get metrics about Ghost growth and evolution."""
        # Calculate growth indicators
        total_interactions = sum(len(history) for history in self.rule_compliance_history.values())
        total_violations = sum(len(violations) for violations in self.rule_violations.values())

        # Learning rate (violations decreasing over time)
        learning_rate = 0.0
        if total_violations > 5:
            recent_violations = sum(len(v[-10:]) for v in self.rule_violations.values() if v)
            older_violations = total_violations - recent_violations
            if older_violations > 0:
                learning_rate = 1.0 - (recent_violations / older_violations)

        # Adaptation rate (new patterns recognized)
        adaptation_indicators = [
            "new_interaction_pattern",
            "rule_boundary_expanded",
            "context_sensitivity_improved"
        ]

        return {
            "total_interactions": total_interactions,
            "learning_rate": round(max(0.0, learning_rate), 3),
            "evolution_stage": "growing" if learning_rate > 0.1 else "adapting",
            "wisdom_accumulated": total_interactions // 10,  # Rough metric
            "ethical_boundaries_tested": total_violations,
            "growth_health": "strong" if learning_rate > 0.2 else "developing"
        }

    async def suggest_rule_adjustments(self) -> List[Dict[str, Any]]:
        """Suggest adjustments to rule configurations based on performance."""
        suggestions = []

        for rule_type, config in self.rule_configs.items():
            report = await self._get_single_rule_report(rule_type)

            # Suggest stricter enforcement if violations are high
            if report["violations"] > 5 and config.enforcement_level == "flexible":
                suggestions.append({
                    "rule_type": rule_type,
                    "suggestion": "Consider stricter enforcement due to high violation rate",
                    "current_level": config.enforcement_level,
                    "recommended_level": "strict",
                    "reason": f"{report['violations']} violations recorded"
                })

            # Suggest more flexible enforcement if compliance is perfect but may be too strict
            elif report["compliance_rate"] == 1.0 and report["evaluations"] > 20 and config.enforcement_level == "strict":
                suggestions.append({
                    "rule_type": rule_type,
                    "suggestion": "Consider more flexible enforcement - perfect compliance may indicate over-cautious rules",
                    "current_level": config.enforcement_level,
                    "recommended_level": "flexible",
                    "reason": "Perfect compliance with high evaluation volume"
                })

        return suggestions

    async def transmutation_rule_validation(self, transmutation_record: Dict[str, Any], generated_structures: Dict[str, str]) -> Dict[str, Any]:
        """Validate transmutation-generated structures against Ghost rules."""
        validation_results = {
            "overall_compliant": True,
            "structure_validations": {},
            "rule_violations": [],
            "recommendations": [],
            "severity": "none"
        }

        # Validate each generated structure
        for structure_type, content in generated_structures.items():
            structure_validation = await self._validate_single_structure(structure_type, content)
            validation_results["structure_validations"][structure_type] = structure_validation

            if not structure_validation["compliant"]:
                validation_results["overall_compliant"] = False
                validation_results["rule_violations"].extend(structure_validation["violations"])

                # Update severity based on violation severity
                if structure_validation["severity"] == "high":
                    validation_results["severity"] = "high"
                elif structure_validation["severity"] == "medium" and validation_results["severity"] != "high":
                    validation_results["severity"] = "medium"
                elif structure_validation["severity"] == "low" and validation_results["severity"] == "none":
                    validation_results["severity"] = "low"

        # Generate recommendations based on violations
        if validation_results["rule_violations"]:
            validation_results["recommendations"] = await self._generate_transmutation_recommendations(
                validation_results["rule_violations"]
            )

        # Log transmutation validation
        await self._log_transmutation_validation(transmutation_record, validation_results)

        return validation_results

    async def _validate_single_structure(self, structure_type: str, content: str) -> Dict[str, Any]:
        """Validate a single generated structure."""
        validation = {
            "compliant": True,
            "violations": [],
            "severity": "none",
            "structure_type": structure_type
        }

        # Common validation checks for all structures
        common_issues = await self._check_common_structure_issues(content)
        validation["violations"].extend(common_issues)

        # Structure-specific validation
        if structure_type == "hook":
            hook_issues = await self._validate_hook_structure(content)
            validation["violations"].extend(hook_issues)
        elif structure_type == "workflow":
            workflow_issues = await self._validate_workflow_structure(content)
            validation["violations"].extend(workflow_issues)
        elif structure_type == "skill":
            skill_issues = await self._validate_skill_structure(content)
            validation["violations"].extend(skill_issues)
        elif structure_type == "rule":
            rule_issues = await self._validate_rule_structure(content)
            validation["violations"].extend(rule_issues)

        # Update compliance and severity
        if validation["violations"]:
            validation["compliant"] = False
            # Set severity based on most severe violation
            severities = [v["severity"] for v in validation["violations"]]
            if "high" in severities:
                validation["severity"] = "high"
            elif "medium" in severities:
                validation["severity"] = "medium"
            else:
                validation["severity"] = "low"

        return validation

    async def _check_common_structure_issues(self, content: str) -> List[Dict[str, Any]]:
        """Check for common issues across all generated structures."""
        issues = []

        # Check for harmful or unethical content
        harmful_patterns = [
            "harm", "damage", "destroy", "exploit", "vulnerability",
            "security breach", "unauthorized access", "malicious"
        ]

        content_lower = content.lower()
        for pattern in harmful_patterns:
            if pattern in content_lower:
                issues.append({
                    "rule": "presence",
                    "description": f"Potentially harmful content detected: '{pattern}'",
                    "severity": "high",
                    "recommendation": "Remove or rephrase harmful content"
                })

        # Check for privacy violations
        privacy_patterns = [
            "personal data", "private information", "confidential",
            "secret", "password", "credentials"
        ]

        for pattern in privacy_patterns:
            if pattern in content_lower:
                issues.append({
                    "rule": "memory",
                    "description": f"Potential privacy violation: '{pattern}'",
                    "severity": "high",
                    "recommendation": "Ensure data handling complies with privacy rules"
                })

        # Check for code quality issues
        if "TODO" in content or "FIXME" in content:
            issues.append({
                "rule": "growth",
                "description": "Incomplete implementation with TODO/FIXME markers",
                "severity": "medium",
                "recommendation": "Complete implementation or mark as experimental"
            })

        # Check for overly complex structures
        if len(content) > 5000:  # Arbitrary threshold
            issues.append({
                "rule": "presence",
                "description": "Generated structure is excessively complex",
                "severity": "medium",
                "recommendation": "Consider breaking down into smaller, focused structures"
            })

        return issues

    async def _validate_hook_structure(self, content: str) -> List[Dict[str, Any]]:
        """Validate generated hook structure."""
        issues = []

        # Check for forced execution patterns
        if "force" in content.lower() or "override" in content.lower():
            issues.append({
                "rule": "presence",
                "description": "Hook contains forced execution patterns",
                "severity": "high",
                "recommendation": "Remove forced execution - hooks should be optional"
            })

        # Check for proper error handling
        if "try:" not in content and "except" not in content:
            issues.append({
                "rule": "growth",
                "description": "Hook lacks proper error handling",
                "severity": "medium",
                "recommendation": "Add try/except blocks for robustness"
            })

        # Check for user consent mechanisms
        if "consent" not in content.lower() and "permission" not in content.lower():
            issues.append({
                "rule": "presence",
                "description": "Hook does not check for user consent",
                "severity": "medium",
                "recommendation": "Add user consent verification"
            })

        return issues

    async def _validate_workflow_structure(self, content: str) -> List[Dict[str, Any]]:
        """Validate generated workflow structure."""
        issues = []

        # Check for reasonable step limits
        if content.count('"name":') > 10:  # Arbitrary limit
            issues.append({
                "rule": "presence",
                "description": "Workflow has too many steps - may overwhelm users",
                "severity": "medium",
                "recommendation": "Break down into smaller, focused workflows"
            })

        # Check for success criteria
        if '"success_criteria"' not in content:
            issues.append({
                "rule": "growth",
                "description": "Workflow lacks clear success criteria",
                "severity": "low",
                "recommendation": "Add measurable success criteria"
            })

        # Check for participant roles
        if '"participant' not in content.lower():
            issues.append({
                "rule": "presence",
                "description": "Workflow does not specify participant roles",
                "severity": "low",
                "recommendation": "Define clear participant roles and responsibilities"
            })

        return issues

    async def _validate_skill_structure(self, content: str) -> List[Dict[str, Any]]:
        """Validate generated skill structure."""
        issues = []

        # Check for activation thresholds
        if "threshold" not in content.lower():
            issues.append({
                "rule": "presence",
                "description": "Skill lacks activation threshold controls",
                "severity": "medium",
                "recommendation": "Add configurable activation thresholds"
            })

        # Check for context awareness
        if "context" not in content.lower():
            issues.append({
                "rule": "memory",
                "description": "Skill does not demonstrate context awareness",
                "severity": "low",
                "recommendation": "Add context sensitivity to skill activation"
            })

        # Check for learning capability
        if "learn" not in content.lower() and "adapt" not in content.lower():
            issues.append({
                "rule": "growth",
                "description": "Skill does not show learning or adaptation capabilities",
                "severity": "low",
                "recommendation": "Add learning mechanisms for skill improvement"
            })

        return issues

    async def _validate_rule_structure(self, content: str) -> List[Dict[str, Any]]:
        """Validate generated rule structure."""
        issues = []

        # Check for enforcement levels
        if '"enforcement_level"' not in content:
            issues.append({
                "rule": "presence",
                "description": "Rule lacks enforcement level specification",
                "severity": "medium",
                "recommendation": "Specify enforcement level (strict/flexible/advisory)"
            })

        # Check for scope definition
        if '"scope"' not in content:
            issues.append({
                "rule": "memory",
                "description": "Rule lacks scope definition",
                "severity": "low",
                "recommendation": "Define rule scope (individual/team/organization)"
            })

        # Check for clear conditions and actions
        if '"condition"' not in content:
            issues.append({
                "rule": "growth",
                "description": "Rule lacks clear conditions for application",
                "severity": "medium",
                "recommendation": "Define specific conditions for rule activation"
            })

        return issues

    async def _generate_transmutation_recommendations(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on validation violations."""
        recommendations = []

        # Group violations by rule type
        rule_groups = {}
        for violation in violations:
            rule = violation["rule"]
            if rule not in rule_groups:
                rule_groups[rule] = []
            rule_groups[rule].append(violation)

        # Generate rule-specific recommendations
        if "presence" in rule_groups:
            presence_violations = rule_groups["presence"]
            high_severity = [v for v in presence_violations if v["severity"] == "high"]
            if high_severity:
                recommendations.append("Critical: Address presence rule violations before deployment - these affect user autonomy")
            else:
                recommendations.append("Review presence rule compliance - ensure user consent and optional interactions")

        if "memory" in rule_groups:
            recommendations.append("Review memory rule compliance - ensure only wisdom is shared, never secrets")

        if "growth" in rule_groups:
            recommendations.append("Address growth rule issues - ensure generated structures support ongoing evolution")

        # General recommendations
        if len(violations) > 5:
            recommendations.append("High violation count: Consider regenerating structures with stricter validation")

        if any(v["severity"] == "high" for v in violations):
            recommendations.append("Critical violations detected: Do not deploy without fixes")

        return recommendations

    async def _log_transmutation_validation(self, transmutation_record: Dict[str, Any], validation_results: Dict[str, Any]):
        """Log transmutation validation for governance tracking."""
        validation_log = {
            "timestamp": datetime.now().isoformat(),
            "transmutation_id": transmutation_record.get("timestamp", "unknown"),
            "fragments_processed": transmutation_record.get("fragments_processed", 0),
            "structures_validated": len(validation_results["structure_validations"]),
            "overall_compliant": validation_results["overall_compliant"],
            "total_violations": len(validation_results["rule_violations"]),
            "severity": validation_results["severity"],
            "recommendations_count": len(validation_results["recommendations"])
        }

        # Store in a transmutation validation log (would be persisted in production)
        if not hasattr(self, 'transmutation_validation_log'):
            self.transmutation_validation_log = []

        self.transmutation_validation_log.append(validation_log)

        # Keep only recent validations (last 100)
        self.transmutation_validation_log = self.transmutation_validation_log[-100:]


# Global rules engine instance
_rules_engine = None

def get_rules_engine() -> RulesEngine:
    """Get or create rules engine instance."""
    global _rules_engine
    if _rules_engine is None:
        _rules_engine = RulesEngine()
    return _rules_engine