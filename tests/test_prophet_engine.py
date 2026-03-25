"""
Tests for Prophet Engine core functionality.

Tests forecasting accuracy, ethical review, swarm coordination,
behavioral tracking, diffusion forecasting, and meta-cognition.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from models import Prediction, BehavioralModel, ConstitutionalPrinciple, ForecastingAgent as ForecastingAgentModel, SwarmConsensus, DiffusionForecast
from prophet_engine import ProphetEngine, ForecastingAgent, SwarmCoordinator, ConstitutionalReviewer
from utils import BehavioralAnalyzer, DiffusionForecaster
from autopoiesis import get_autopoiesis_engine


class TestProphetEngine:
    """Test Prophet Engine core functionality."""

    @pytest.fixture
    def prophet_engine(self):
        """Create a test Prophet Engine instance."""
        return ProphetEngine()

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        with patch('utils.LLMUtils') as mock_llm_class:
            mock_instance = Mock()
            mock_instance.generate_with_reasoning.return_value = json.dumps({
                'domain': 'incident',
                'probability': 0.7,
                'time_horizon': 'week',
                'confidence': 0.8,
                'reasoning_chain': [{'step': 'analysis', 'analysis': 'Test reasoning'}],
                'intervention_suggested': False
            })
            mock_llm_class.return_value = mock_instance
            yield mock_instance

    def test_initialization(self, prophet_engine):
        """Test Prophet Engine initializes with correct agents."""
        assert len(prophet_engine.agents) == 4
        agent_names = [agent.name for agent in prophet_engine.agents]
        assert 'Archivist' in agent_names
        assert 'Empath' in agent_names
        assert 'Sentinel' in agent_names
        assert 'Historian' in agent_names

    def test_forecast_incident_risk(self, prophet_engine, mock_llm):
        """Test incident risk forecasting."""
        result = prophet_engine.forecast_incident_risk("test_target")

        assert isinstance(result, Prediction)
        assert result.domain == 'incident'
        assert result.target == 'test_target'
        assert 0 <= result.probability <= 1
        assert result.time_horizon in ['immediate', 'week', 'month']

    def test_forecast_team_health(self, prophet_engine):
        """Test team health forecasting."""
        result = prophet_engine.forecast_team_health("test_engineer")

        assert isinstance(result, BehavioralModel)
        assert result.engineer_id == "test_engineer"
        assert isinstance(result.patterns, dict)
        assert 0 <= result.burnout_risk <= 1

    def test_forecast_architectural_decay(self, prophet_engine, mock_llm):
        """Test architectural decay forecasting."""
        result = prophet_engine.forecast_architectural_decay("test_module")

        assert isinstance(result, Prediction)
        assert result.domain == 'architectural_decay'
        assert result.target == 'test_module'

    def test_forecast_knowledge_loss(self, prophet_engine, mock_llm):
        """Test knowledge loss forecasting."""
        result = prophet_engine.forecast_knowledge_loss("test_team")

        assert isinstance(result, Prediction)
        assert result.domain == 'knowledge_loss'
        assert result.target == 'test_team'

    def test_get_prophecy_status(self, prophet_engine):
        """Test getting prophecy status."""
        status = prophet_engine.get_prophecy_status()

        assert 'active_agents' in status
        assert 'total_predictions' in status
        assert 'domain_performance' in status
        assert 'agent_status' in status
        assert status['active_agents'] == 4


class TestForecastingAgent:
    """Test individual forecasting agents."""

    @pytest.fixture
    def agent(self):
        """Create a test forecasting agent."""
        return ForecastingAgent("TestAgent", "test_domain", "ToT")

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for agent testing."""
        with patch('utils.LLMUtils') as mock_llm_class:
            mock_instance = Mock()
            mock_instance.generate_with_reasoning.return_value = json.dumps({
                'domain': 'test_domain',
                'probability': 0.6,
                'time_horizon': 'week',
                'confidence': 0.7,
                'reasoning_chain': [{'step': 'test', 'analysis': 'test analysis'}],
                'intervention_suggested': True
            })
            mock_llm_class.return_value = mock_instance
            yield mock_instance

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.name == "TestAgent"
        assert agent.domain == "test_domain"
        assert agent.reasoning_style == "ToT"
        assert agent.active == True
        assert agent.accuracy_history == []

    def test_agent_forecast(self, agent, mock_llm):
        """Test agent generates predictions."""
        context = {"test": "context"}
        prediction = agent.forecast("test task", context)

        assert isinstance(prediction, Prediction)
        assert prediction.domain == 'test_domain'
        assert prediction.probability == 0.6
        assert prediction.confidence == 0.7
        assert prediction.intervention_suggested == True

    def test_accuracy_update(self, agent):
        """Test accuracy history tracking."""
        agent.update_accuracy(0.8, 0.7)  # Actual: 0.8, Predicted: 0.7
        assert len(agent.accuracy_history) == 1
        assert agent.accuracy_history[0] == 0.9  # 1 - |0.8 - 0.7|


class TestSwarmCoordinator:
    """Test swarm coordination functionality."""

    @pytest.fixture
    def agents(self):
        """Create test agents."""
        return [
            ForecastingAgent("Agent1", "domain1", "ToT"),
            ForecastingAgent("Agent2", "domain2", "CoT")
        ]

    @pytest.fixture
    def swarm(self, agents):
        """Create swarm coordinator."""
        return SwarmCoordinator(agents)

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for swarm testing."""
        with patch('utils.LLMUtils') as mock_llm_class:
            mock_instance = Mock()
            mock_instance.generate_with_reasoning.return_value = json.dumps({
                'consensus_probability': 0.65,
                'confidence_interval': [0.55, 0.75]
            })
            mock_llm_class.return_value = mock_instance
            yield mock_instance

    def test_swarm_initialization(self, swarm, agents):
        """Test swarm initializes with agents."""
        assert swarm.agents == agents

    def test_debate_and_consensus(self, swarm, mock_llm):
        """Test swarm debate and consensus formation."""
        task = "test task"
        context = {"test": "context"}

        consensus = swarm.debate_and_consensus(task, context)

        assert isinstance(consensus, SwarmConsensus)
        assert consensus.task == task
        assert len(consensus.individual_predictions) == 2
        assert consensus.consensus_probability == 0.65
        assert consensus.confidence_interval == (0.55, 0.75)


class TestConstitutionalReviewer:
    """Test constitutional review functionality."""

    @pytest.fixture
    def reviewer(self):
        """Create constitutional reviewer."""
        return ConstitutionalReviewer()

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for review testing."""
        with patch('utils.LLMUtils') as mock_llm_class:
            mock_instance = Mock()
            mock_instance.generate_with_reasoning.return_value = "approved - reasoning meets ethical standards"
            mock_llm_class.return_value = mock_instance
            yield mock_instance

    def test_reviewer_initialization(self, reviewer):
        """Test reviewer loads principles."""
        assert len(reviewer.principles) > 0
        assert all(isinstance(p, ConstitutionalPrinciple) for p in reviewer.principles)

    def test_prediction_review_approved(self, reviewer, mock_llm):
        """Test prediction review approves valid predictions."""
        prediction = Prediction(
            timestamp="2026-03-25T18:00:00",
            domain="incident",
            target="test",
            probability=0.5,
            time_horizon="week",
            confidence=0.8,
            reasoning_chain=[{"step": "analysis", "analysis": "Detailed reasoning"}],
            intervention_suggested=False,
            constitutional_review="pending"
        )

        result = reviewer.review_prediction(prediction)
        assert result == "approved"

    def test_prediction_review_flagged(self, reviewer):
        """Test prediction review flags suspicious predictions."""
        prediction = Prediction(
            timestamp="2026-03-25T18:00:00",
            domain="incident",
            target="test",
            probability=0.5,
            time_horizon="week",
            confidence=0.8,
            reasoning_chain=[],  # No reasoning
            intervention_suggested=False,
            constitutional_review="pending"
        )

        result = reviewer.review_prediction(prediction)
        assert result == "flagged"

    def test_principles_summary(self, reviewer):
        """Test getting principles summary."""
        summary = reviewer.get_principles_summary()
        assert 'total_principles' in summary
        assert 'categories' in summary
        assert 'high_weight_principles' in summary


class TestBehavioralAnalyzer:
    """Test behavioral analysis functionality."""

    @pytest.fixture
    def analyzer(self):
        """Create behavioral analyzer."""
        return BehavioralAnalyzer()

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly."""
        assert analyzer.storage_path == "behavioral_model/"
        assert analyzer.check_consent("test_id") == False  # No consent given

    def test_consent_management(self, analyzer):
        """Test consent granting and checking."""
        engineer_id = "test_engineer"

        # Initially no consent
        assert not analyzer.check_consent(engineer_id)

        # Grant consent
        analyzer.grant_consent(engineer_id)
        assert analyzer.check_consent(engineer_id)

    def test_fragment_capture_without_consent(self, analyzer):
        """Test fragment capture fails without consent."""
        result = analyzer.capture_fragment("test activity", "test_engineer")
        assert result is None

    def test_fragment_capture_with_consent(self, analyzer):
        """Test fragment capture succeeds with consent."""
        engineer_id = "test_engineer"
        analyzer.grant_consent(engineer_id)

        result = analyzer.capture_fragment("test activity", engineer_id)
        assert result is not None
        assert result.type == 'behavioral'
        assert result.context['engineer_id'] == engineer_id

    def test_pattern_analysis(self, analyzer):
        """Test behavioral pattern analysis."""
        engineer_id = "test_engineer"
        analyzer.grant_consent(engineer_id)

        # Store some test data
        analyzer.store_behavioral_data(engineer_id, "pause in code")
        analyzer.store_behavioral_data(engineer_id, "hesitation on design")
        analyzer.store_behavioral_data(engineer_id, "language drift detected")

        patterns = analyzer.analyze_patterns(engineer_id)
        assert 'pause_frequency' in patterns
        assert 'hesitation_score' in patterns
        assert 'language_drift' in patterns
        assert all(0 <= v <= 1 for v in patterns.values())


class TestDiffusionForecaster:
    """Test diffusion forecasting functionality."""

    @pytest.fixture
    def forecaster(self):
        """Create diffusion forecaster."""
        return DiffusionForecaster()

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for forecasting testing."""
        with patch('utils.LLMUtils') as mock_llm_class:
            mock_instance = Mock()
            mock_instance.generate_with_reasoning.side_effect = [
                # First call: evolution scenarios
                json.dumps([{
                    "scenario": "refactor_module",
                    "description": "Refactor module for better maintainability",
                    "initial_probability": 0.5,
                    "complexity": "medium"
                }]),
                # Second call: diffusion refinement
                "Refined: Consider dependencies and breaking changes",
                # Third call: uncertainty analysis
                json.dumps({
                    'probability': 0.7,
                    'risk_level': 'medium',
                    'timeline': 'long'
                })
            ]
            mock_llm_class.return_value = mock_instance
            yield mock_instance

    def test_forecaster_initialization(self, forecaster):
        """Test forecaster initializes correctly."""
        assert len(forecaster.evolution_patterns) > 0
        assert 'refactoring_patterns' in forecaster.evolution_patterns

    @pytest.mark.asyncio
    async def test_forecast_code_evolution(self, forecaster, mock_llm):
        """Test code evolution forecasting."""
        scenarios = ["refactor_module", "add_tests"]
        result = await forecaster.forecast_code_evolution("test_module", scenarios)

        assert 'module' in result
        assert 'evolution_scenarios' in result
        assert 'probabilistic_forecast' in result
        assert 'recommended_path' in result
        assert 'evolution_score' in result

    def test_probabilistic_forecast_calculation(self, forecaster):
        """Test probabilistic forecast calculation."""
        diffused_scenarios = [{
            'scenario': 'test_scenario',
            'refined_description': 'Test description with medium risk',
            'uncertainty_analysis': json.dumps({
                'probability': 0.8,
                'risk_level': 'medium',
                'timeline': 'long'
            })
        }]

        forecast = forecaster._calculate_probabilistic_forecast(diffused_scenarios)

        assert 'scenarios' in forecast
        assert 'risk_distribution' in forecast
        assert 'timeline_distribution' in forecast
        assert len(forecast['scenarios']) == 1

    def test_recommended_path_selection(self, forecaster):
        """Test recommended path selection."""
        forecast = {
            'scenarios': [
                {'scenario': 'low_risk', 'normalized_probability': 0.6, 'risk_level': 'low'},
                {'scenario': 'high_risk', 'normalized_probability': 0.8, 'risk_level': 'high'}
            ]
        }

        recommended = forecaster._select_recommended_path(forecast)
        assert recommended == 'low_risk'  # Should prefer low risk


class TestMetaCognitionIntegration:
    """Test meta-cognition integration with autopoiesis."""

    @pytest.fixture
    def autopoiesis_engine(self):
        """Create autopoiesis engine for testing."""
        return get_autopoiesis_engine()

    def test_prediction_fragment_capture(self, autopoiesis_engine):
        """Test capturing prediction fragments."""
        prediction_data = {
            'domain': 'incident',
            'probability': 0.7,
            'confidence': 0.8,
            'reasoning_chain': [{'step': 'analysis', 'analysis': 'Test reasoning'}]
        }

        fragment = autopoiesis_engine.prediction_fragment_capture(prediction_data)

        assert fragment is not None
        assert fragment.type == 'prediction'
        assert 'Prophet prediction' in fragment.content
        assert fragment.context['domain'] == 'incident'

    def test_meta_cognition_transmutation(self, autopoiesis_engine):
        """Test meta-cognition enhanced transmutation."""
        # Add some test fragments
        autopoiesis_engine.capture_fragment('test', 'test content', {})

        record = autopoiesis_engine.meta_cognition_transmutation()

        assert isinstance(record, TransmutationRecord)
        assert record.review_status in ['approved', 'rejected', 'meta_cognition_delay', 'paused']


# Integration tests
class TestProphetIntegration:
    """Test Prophet Engine integration with other systems."""

    def test_full_prophecy_workflow(self):
        """Test complete prophecy workflow."""
        from prophet_engine import initialize_prophet_engine

        engine = initialize_prophet_engine()

        # Make a prediction
        prediction = engine.forecast_incident_risk("integration_test")

        assert isinstance(prediction, Prediction)
        assert prediction.constitutional_review in ['approved', 'flagged', 'rejected', 'pending']

        # Check meta-cognition updated
        assert engine.meta_cognition_data['total_predictions'] >= 1

    def test_behavioral_tracking_integration(self):
        """Test behavioral tracking integration."""
        from utils import capture_behavioral_fragment

        # This would require consent in real usage
        # For testing, mock the consent check
        with patch('utils.BehavioralAnalyzer.check_consent', return_value=True):
            fragment = capture_behavioral_fragment("test activity", "test_engineer")
            assert fragment is not None
            assert fragment.type == 'behavioral'


if __name__ == "__main__":
    pytest.main([__file__])