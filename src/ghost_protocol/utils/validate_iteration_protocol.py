#!/usr/bin/env python3
"""
Validation Script for Iteration Protocol End-to-End Flows

This script validates that all components of the Iteration Protocol work together
to create a cohesive system that guides development through reflection and connection.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

# Import all components
from src.ghost_protocol.utils.config import Config
from src.ghost_protocol.models.models import IterationEvent, HookConfig, WorkflowConfig, SkillConfig, RuleConfig
from src.ghost_protocol.engines.skills_engine import SkillsEngine, get_skills_engine
from src.ghost_protocol.engines.rules_engine import RulesEngine, get_rules_engine
from src.ghost_protocol.core.hooks_server import HooksServer, get_hooks_server
from src.ghost_protocol.core.workflows_server import WorkflowsServer, get_workflows_server
from src.ghost_protocol.servers.nexus_server import get_nexus
from src.ghost_protocol.servers.yolo_protocol import get_yolo
from src.ghost_protocol.core.cline_integration import get_cline_integration


class IterationProtocolValidator:
    """Validates end-to-end flows of the Iteration Protocol."""

    def __init__(self):
        self.results = {
            "component_initialization": False,
            "hook_integration": False,
            "workflow_orchestration": False,
            "skill_activation": False,
            "rule_compliance": False,
            "cross_component_integration": False,
            "learning_loop": False,
            "ethical_boundaries": False,
            "failure_handling": False
        }
        self.test_log = []

    def log(self, message: str):
        """Log validation step."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.test_log.append(f"[{timestamp}] {message}")
        print(f"✓ {message}")

    async def validate_component_initialization(self):
        """Test 1: Component Initialization"""
        try:
            # Initialize all components
            skills = get_skills_engine()
            rules = get_rules_engine()
            hooks = get_hooks_server()
            workflows = get_workflows_server()
            nexus = get_nexus()
            yolo = get_yolo()
            cline = get_cline_integration()

            # Verify configurations loaded
            assert Config.HOOKS_ENABLED is not None
            assert Config.WORKFLOWS_ENABLED is not None
            assert Config.SKILLS_ENABLED is not None
            assert Config.RULES_ENABLED is not None

            self.results["component_initialization"] = True
            self.log("Component initialization successful")

        except Exception as e:
            self.log(f"Component initialization failed: {e}")
            return False

        return True

    async def validate_hook_integration(self):
        """Test 2: Hook Integration"""
        try:
            hooks = get_hooks_server()

            # Test pre-commit hook reflection
            commit_context = {
                "files": ["auth.py", "test_auth.py"],
                "commit_message": "Add user authentication with emotional validation",
                "user_consent": True
            }

            reflection = await hooks.trigger_hook_reflection("pre-commit", commit_context)
            assert isinstance(reflection, str)
            assert len(reflection) > 0
            assert "emotional" in reflection.lower() or "feel" in reflection.lower()

            # Test PR hook reflection
            pr_context = {
                "pr_title": "Implement secure authentication flow",
                "reviewers": ["alice", "bob"],
                "user_consent": True
            }

            reflection = await hooks.trigger_hook_reflection("pr", pr_context)
            assert isinstance(reflection, str)
            assert len(reflection) > 0

            self.results["hook_integration"] = True
            self.log("Hook integration validation successful")

        except Exception as e:
            self.log(f"Hook integration validation failed: {e}")
            return False

        return True

    async def validate_workflow_orchestration(self):
        """Test 3: Workflow Orchestration"""
        try:
            workflows = get_workflows_server()

            # Test workflow template loading
            template = await workflows.load_workflow_template("discovery")
            assert template is not None
            assert template["workflow_type"] == "discovery"

            # Test workflow start (mocked)
            # Note: In real validation, this would need proper mocking
            result = await workflows.start_workflow("discovery", ["alice"], {"is_new_contributor": True})
            # Even if it fails due to missing conditions, it should return a proper response
            assert isinstance(result, dict)
            assert "started" in result

            self.results["workflow_orchestration"] = True
            self.log("Workflow orchestration validation successful")

        except Exception as e:
            self.log(f"Workflow orchestration validation failed: {e}")
            return False

        return True

    async def validate_skill_activation(self):
        """Test 4: Skill Activation"""
        try:
            skills = get_skills_engine()

            # Test listening skill activation
            emotional_context = {
                "text": "I'm really frustrated with this authentication bug",
                "recent_events": []
            }

            result = await skills.evaluate_skill_activation("listening", emotional_context)
            assert isinstance(result, tuple)
            assert len(result) == 2
            should_activate, confidence = result
            assert isinstance(should_activate, bool)
            assert isinstance(confidence, (int, float))

            # Test pattern skill activation
            pattern_context = {
                "text": "I need to add error handling for API authentication",
                "file_path": "auth.py"
            }

            result = await skills.evaluate_skill_activation("pattern", pattern_context)
            assert isinstance(result, tuple)
            assert len(result) == 2

            # Test silence skill activation
            silence_context = {
                "text": "I'm so tired, this has been a long day",
                "recent_events": [{"text": "tired message"}] * 6,
                "urgency_level": "low"
            }

            result = await skills.evaluate_skill_activation("silence", silence_context)
            assert isinstance(result, tuple)
            assert len(result) == 2

            self.results["skill_activation"] = True
            self.log("Skill activation validation successful")

        except Exception as e:
            self.log(f"Skill activation validation failed: {e}")
            return False

        return True

    async def validate_rule_compliance(self):
        """Test 5: Rule Compliance"""
        try:
            rules = get_rules_engine()

            # Test presence rule
            presence_result = await rules.evaluate_rule_compliance(
                "presence", "user_initiated_interaction", {"user_consent": True}
            )
            assert isinstance(presence_result, dict)
            assert "compliant" in presence_result
            assert "reasoning" in presence_result
            assert "severity" in presence_result

            # Test memory rule
            memory_result = await rules.evaluate_rule_compliance(
                "memory", "share_wisdom", {"contains_secrets": False, "distilled_to_wisdom": True}
            )
            assert isinstance(memory_result, dict)
            assert "compliant" in memory_result

            # Test growth rule
            growth_result = await rules.evaluate_rule_compliance(
                "growth", "learn_from_experience", {"learning_opportunity": True}
            )
            assert isinstance(growth_result, dict)
            assert "compliant" in growth_result

            self.results["rule_compliance"] = True
            self.log("Rule compliance validation successful")

        except Exception as e:
            self.log(f"Rule compliance validation failed: {e}")
            return False

        return True

    async def validate_cross_component_integration(self):
        """Test 6: Cross-Component Integration"""
        try:
            # Test hook → skills → rules integration
            hooks = get_hooks_server()
            skills = get_skills_engine()
            rules = get_rules_engine()

            # Simulate a commit with emotional context
            commit_context = {
                "files": ["auth.py"],
                "commit_message": "Fix frustrating authentication issue",
                "user_consent": True
            }

            # Hook should trigger reflection
            reflection = await hooks.trigger_hook_reflection("pre-commit", commit_context)
            assert isinstance(reflection, str)

            # Skills should evaluate the emotional context
            skill_context = {"text": commit_context["commit_message"], "recent_events": []}
            skill_result = await skills.evaluate_skill_activation("listening", skill_context)
            assert isinstance(skill_result, tuple)

            # Rules should verify compliance
            rule_result = await rules.evaluate_rule_compliance(
                "presence", "hook_trigger", {"user_consent": True}
            )
            assert isinstance(rule_result, dict)
            assert rule_result["compliant"] == True

            self.results["cross_component_integration"] = True
            self.log("Cross-component integration validation successful")

        except Exception as e:
            self.log(f"Cross-component integration validation failed: {e}")
            return False

        return True

    async def validate_learning_loop(self):
        """Test 7: Learning Loop"""
        try:
            nexus = get_nexus()
            yolo = get_yolo()

            # Create a test iteration event
            test_event = IterationEvent(
                event_type="hook_trigger",
                context={"hook_type": "pre-commit", "emotional_context": "frustration"},
                participants=["developer"],
                timestamp=datetime.now().isoformat(),
                outcome="reflection_provided"
            )

            # Log event in Nexus
            success = await nexus.log_iteration_event(test_event)
            assert success == True

            # Query events back
            events = await nexus.query_iteration_events("hook_trigger")
            assert isinstance(events, list)
            assert len(events) >= 1

            # Check workflow insights
            insights = await nexus.get_workflow_insights()
            assert isinstance(insights, dict)
            assert "total_workflows" in insights

            self.results["learning_loop"] = True
            self.log("Learning loop validation successful")

        except Exception as e:
            self.log(f"Learning loop validation failed: {e}")
            return False

        return True

    async def validate_ethical_boundaries(self):
        """Test 8: Ethical Boundaries"""
        try:
            rules = get_rules_engine()
            skills = get_skills_engine()

            # Test presence rule prevents imposition
            violation_result = await rules.evaluate_rule_compliance(
                "presence", "forced_interaction", {"user_consent": False}
            )
            assert violation_result["compliant"] == False
            assert violation_result["severity"] == "high"

            # Test memory rule protects privacy
            privacy_violation = await rules.evaluate_rule_compliance(
                "memory", "share_personal_data", {"anonymized": False}
            )
            assert privacy_violation["compliant"] == False

            # Test silence skill respects boundaries
            boundary_context = {
                "text": "Please stop responding",
                "user_consent": False,
                "recent_events": []
            }
            silence_result = await skills.evaluate_skill_activation("silence", boundary_context)
            should_activate, confidence = silence_result
            assert should_activate == True or confidence > 0.5

            # Test growth rule prevents stagnation
            stagnation_result = await rules.evaluate_rule_compliance(
                "growth", "no_evolution", {"days_since_change": 50}
            )
            assert stagnation_result["compliant"] == False

            self.results["ethical_boundaries"] = True
            self.log("Ethical boundaries validation successful")

        except Exception as e:
            self.log(f"Ethical boundaries validation failed: {e}")
            return False

        return True

    async def validate_failure_handling(self):
        """Test 9: Failure Handling"""
        try:
            # Test hook failure handling
            hooks = get_hooks_server()
            failure_reflection = await hooks.trigger_hook_reflection("pre-commit", {})
            assert isinstance(failure_reflection, str)  # Should not crash

            # Test skill failure handling
            skills = get_skills_engine()
            failure_skill = await skills.evaluate_skill_activation("listening", {})
            assert isinstance(failure_skill, tuple)  # Should not crash

            # Test rule failure handling
            rules = get_rules_engine()
            failure_rule = await rules.evaluate_rule_compliance("presence", "test", {})
            assert isinstance(failure_rule, dict)  # Should not crash

            # Test workflow failure handling
            workflows = get_workflows_server()
            failure_workflow = await workflows.start_workflow("nonexistent", [], {})
            assert isinstance(failure_workflow, dict)  # Should not crash

            self.results["failure_handling"] = True
            self.log("Failure handling validation successful")

        except Exception as e:
            self.log(f"Failure handling validation failed: {e}")
            return False

        return True

    async def run_full_validation(self):
        """Run complete validation suite."""
        self.log("Starting Iteration Protocol Validation")
        self.log("=" * 50)

        # Run all validation tests
        await self.validate_component_initialization()
        await self.validate_hook_integration()
        await self.validate_workflow_orchestration()
        await self.validate_skill_activation()
        await self.validate_rule_compliance()
        await self.validate_cross_component_integration()
        await self.validate_learning_loop()
        await self.validate_ethical_boundaries()
        await self.validate_failure_handling()

        # Generate validation report
        self.log("=" * 50)
        self.log("VALIDATION RESULTS")
        self.log("=" * 50)

        passed = 0
        total = len(self.results)

        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name}: {status}")
            if result:
                passed += 1

        self.log("=" * 50)
        self.log(f"OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

        if passed == total:
            self.log("🎉 ALL VALIDATION TESTS PASSED!")
            self.log("The Iteration Protocol is ready for production use.")
        else:
            self.log("⚠️  Some validation tests failed.")
            self.log("Review the failed tests before production deployment.")

        return passed == total

    def save_validation_report(self, filename: str = "validation_report.json"):
        """Save validation results to file."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "results": self.results,
            "test_log": self.test_log,
            "summary": {
                "total_tests": len(self.results),
                "passed_tests": sum(self.results.values()),
                "success_rate": sum(self.results.values()) / len(self.results) * 100
            }
        }

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        self.log(f"Validation report saved to {filename}")


async def main():
    """Main validation entry point."""
    validator = IterationProtocolValidator()

    try:
        success = await validator.run_full_validation()
        validator.save_validation_report()

        if success:
            print("\n🎉 Iteration Protocol validation completed successfully!")
            return 0
        else:
            print("\n⚠️  Iteration Protocol validation found issues.")
            return 1

    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())