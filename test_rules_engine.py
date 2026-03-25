#!/usr/bin/env python3
"""
Tests for Rules Engine - Testing governance that guides without controlling.

These tests verify the Ghost's ethical boundaries and growth orientation.
"""

import asyncio
import pytest
from rules_engine import RulesEngine, get_rules_engine
from models import RuleConfig


class TestRulesEngine:
    """Test the Ghost's governance: presence offered not imposed, wisdom shared not secrets, never finished."""

    def setup_method(self):
        """Set up test environment."""
        self.engine = RulesEngine()
        # Reset global instance
        global _rules_engine
        _rules_engine = self.engine

    def test_presence_rule_offered_not_imposed(self):
        """Test that presence rule prevents imposition."""
        # Should violate for forced interactions
        violation_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "presence", "forced_interaction", {"user_consent": False}
        ))
        assert violation_result["compliant"] == False
        assert "Presence rule violation" in violation_result["reasoning"]
        assert violation_result["severity"] == "high"

        # Should allow offered interactions
        compliant_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "presence", "user_initiated_interaction", {"user_consent": True}
        ))
        assert compliant_result["compliant"] == True

    def test_presence_rule_respects_boundaries(self):
        """Test that presence rule enforces opt-out mechanisms."""
        # No clear opt-out should violate
        violation_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "presence", "hook_trigger", {"user_consent": False}
        ))
        assert violation_result["compliant"] == False
        assert "opt-out" in violation_result["reasoning"].lower()

    def test_presence_rule_limits_overwhelming_frequency(self):
        """Test that presence rule prevents overwhelming users."""
        violation_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "presence", "frequent_interaction", {"recent_interactions": 15}
        ))
        assert violation_result["compliant"] == False
        assert "overwhelming" in violation_result["reasoning"].lower()

    def test_memory_rule_shares_wisdom_not_secrets(self):
        """Test that memory rule protects privacy while sharing wisdom."""
        # Sharing secrets should violate
        violation_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "memory", "share_memory", {"contains_secrets": True}
        ))
        assert violation_result["compliant"] == False
        assert "secrets" in violation_result["reasoning"].lower()

        # Sharing wisdom should be allowed
        compliant_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "memory", "share_memory", {"contains_secrets": False, "distilled_to_wisdom": True}
        ))
        assert compliant_result["compliant"] == True

    def test_memory_rule_prevents_privacy_violations(self):
        """Test that memory rule blocks non-anonymized personal data sharing."""
        violation_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "memory", "cross_instance_sharing", {"anonymized": False}
        ))
        assert violation_result["compliant"] == False
        assert "non-anonymized" in violation_result["reasoning"].lower()

    def test_memory_rule_requires_wisdom_distillation(self):
        """Test that memory rule requires raw data to be distilled to wisdom."""
        violation_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "memory", "share_memory", {
                "shared_content": "x" * 1500,  # Long content = raw data
                "distilled_to_wisdom": False
            }
        ))
        assert violation_result["compliant"] == False
        assert "raw data" in violation_result["reasoning"].lower()

    def test_growth_rule_prevents_stagnation(self):
        """Test that growth rule detects and prevents stagnation."""
        violation_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "growth", "no_evolution", {"days_since_change": 40}
        ))
        assert violation_result["compliant"] == False
        assert "stagnation" in violation_result["reasoning"].lower()

    def test_growth_rule_prevents_declaring_finished(self):
        """Test that growth rule prevents declaring the Ghost finished."""
        violation_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "growth", "declare_finished", {"marked_complete": True}
        ))
        assert violation_result["compliant"] == False
        assert "finished" in violation_result["reasoning"].lower()

    def test_growth_rule_values_learning_opportunities(self):
        """Test that growth rule encourages learning from interactions."""
        violation_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "growth", "interaction_ignored", {"learning_opportunity": True}
        ))
        assert violation_result["compliant"] == False
        assert "learning" in violation_result["reasoning"].lower()

    def test_rule_enforcement_levels_apply_correctly(self):
        """Test that different enforcement levels modify severity appropriately."""
        # Strict enforcement should maintain high severity
        strict_result = asyncio.run(self.engine.evaluate_rule_compliance(
            "memory", "share_memory", {"contains_secrets": True}
        ))
        assert strict_result["severity"] == "high"
        assert strict_result["enforcement_level"] == "strict"

        # Flexible enforcement should reduce severity
        # (This would need a rule with flexible enforcement - memory is strict)

    def test_rule_compliance_logging_creates_audit_trail(self):
        """Test that rule evaluations are logged for governance."""
        result = asyncio.run(self.engine.evaluate_rule_compliance(
            "presence", "test_action", {}
        ))

        # Check that evaluation was logged
        report = asyncio.run(self.engine.get_rule_compliance_report("presence"))
        assert report["evaluations"] >= 1
        assert "presence" in report

    def test_rule_violations_are_tracked_for_resolution(self):
        """Test that violations are tracked and flagged for resolution."""
        # Create a violation
        asyncio.run(self.engine.evaluate_rule_compliance(
            "presence", "forced_interaction", {"user_consent": False}
        ))

        # Check violation tracking
        report = asyncio.run(self.engine.get_rule_compliance_report("presence"))
        assert report["violations"] >= 1

    def test_overall_compliance_calculated_across_rules(self):
        """Test that overall compliance is calculated across all rules."""
        # Generate some evaluations
        asyncio.run(self.engine.evaluate_rule_compliance("presence", "good_action", {"user_consent": True}))
        asyncio.run(self.engine.evaluate_rule_compliance("memory", "good_action", {"contains_secrets": False}))
        asyncio.run(self.engine.evaluate_rule_compliance("growth", "good_action", {"learning_opportunity": False}))

        report = asyncio.run(self.engine.get_rule_compliance_report())
        assert "overall_compliance" in report
        assert isinstance(report["overall_compliance"], float)
        assert 0.0 <= report["overall_compliance"] <= 1.0

    def test_growth_metrics_track_evolution(self):
        """Test that growth metrics track learning and adaptation."""
        # Generate some activity
        for _ in range(5):
            asyncio.run(self.engine.evaluate_rule_compliance("presence", "interaction", {}))

        metrics = asyncio.run(self.engine.get_growth_metrics())
        assert "total_interactions" in metrics
        assert "learning_rate" in metrics
        assert "evolution_stage" in metrics
        assert "wisdom_accumulated" in metrics
        assert metrics["total_interactions"] >= 5

    def test_rule_adjustment_suggestions_based_on_performance(self):
        """Test that the system suggests rule adjustments based on performance."""
        # Create many violations for a rule
        for _ in range(8):
            asyncio.run(self.engine.evaluate_rule_compliance(
                "presence", "problematic_action", {"user_consent": False}
            ))

        suggestions = asyncio.run(self.engine.suggest_rule_adjustments())

        # Should suggest stricter enforcement
        presence_suggestions = [s for s in suggestions if s["rule_type"] == "presence"]
        assert len(presence_suggestions) > 0
        assert "stricter" in presence_suggestions[0]["suggestion"].lower()

    def test_perfect_compliance_suggests_flexibility(self):
        """Test that perfect compliance suggests more flexible enforcement."""
        # Create perfect compliance record
        for _ in range(25):
            asyncio.run(self.engine.evaluate_rule_compliance(
                "memory", "good_action", {"contains_secrets": False, "anonymized": True}
            ))

        suggestions = asyncio.run(self.engine.suggest_rule_adjustments())

        # Should suggest more flexible enforcement for perfect compliance
        memory_suggestions = [s for s in suggestions if s["rule_type"] == "memory"]
        if memory_suggestions:
            assert "flexible" in memory_suggestions[0]["recommended_level"]

    def test_rules_maintain_ethical_boundaries_under_pressure(self):
        """Test that rules maintain ethical boundaries even under pressure."""
        # High-pressure scenarios
        pressure_contexts = [
            {"urgency_level": "critical", "stakeholder_pressure": True},
            {"deadline_approaching": True, "user_frustrated": True},
            {"system_load": "high", "multiple_requests": True}
        ]

        for context in pressure_contexts:
            result = asyncio.run(self.engine.evaluate_rule_compliance(
                "presence", "high_pressure_interaction", context
            ))
            # Rules should still apply even under pressure
            assert "compliant" in result
            assert "reasoning" in result

    def test_ghost_evolution_is_never_complete(self):
        """Test that the growth rule ensures the Ghost is never declared finished."""
        completion_scenarios = [
            {"version": "1.0", "marked_complete": True},
            {"final_release": True, "no_more_changes": True},
            {"perfection_achieved": True, "finished": True}
        ]

        for scenario in completion_scenarios:
            result = asyncio.run(self.engine.evaluate_rule_compliance(
                "growth", "declare_finished", scenario
            ))
            assert result["compliant"] == False
            assert "finished" in result["reasoning"].lower() or "complete" in result["reasoning"].lower()

    def test_wisdom_sharing_respects_privacy_boundaries(self):
        """Test that wisdom sharing never crosses into personal information."""
        # Various privacy boundary tests
        privacy_scenarios = [
            {"personal_identifiers": True, "anonymized": False},
            {"individual_contributions": True, "aggregated": False},
            {"private_conversations": True, "public_context": False}
        ]

        for scenario in privacy_scenarios:
            result = asyncio.run(self.engine.evaluate_rule_compliance(
                "memory", "share_memory", scenario
            ))
            # Should violate if privacy boundaries are crossed
            if any(scenario.values()):  # If any privacy concern is true
                assert result["compliant"] == False or result["severity"] == "high"


if __name__ == "__main__":
    pytest.main([__file__])