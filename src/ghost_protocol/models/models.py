from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


class NexusData(BaseModel):
    """Knowledge entry for the Nexus knowledge base."""
    id: str
    content: str
    type: str  # e.g., 'commit_message', 'pr_comment', 'architectural_decision'
    metadata: Dict[str, str]  # additional context like author, timestamp, file_path
    relationships: List[str]  # ids of related entries
    resonance_score: Optional[float] = None  # emotional/historical weight (0-10)


class WeaverRequest(BaseModel):
    """Request for code generation with cohesion constraints."""
    objective: str  # high-level goal
    context: Dict[str, str]  # current codebase state
    constraints: List[str]  # architectural rules
    scope: str  # affected modules
    patterns: List[str]  # code patterns to follow


class YOLOMission(BaseModel):
    """Mission specification for autonomous execution."""
    goal: str  # emotional/resonant objective
    autonomy_level: int  # 1-5 scale of independence
    checkpoints: List[str]  # decision points requiring oversight
    constraints: List[str]  # hard boundaries
    success_criteria: List[str]  # completion measures
    emotional_payload: Optional[Dict[str, Any]] = {}


class CodeDelta(BaseModel):
    """Unified code change representation."""
    files: Dict[str, str]  # file_path -> new_content
    rationale: str  # explanation
    risks: List[str]  # potential issues
    tests: List[str]  # required test cases
    cohesion_score: Optional[float] = None  # 0-1 measure of architectural cohesion
    directives_applied: List[str] = []  # Prime Directives followed
    manifest: Optional[Dict[str, Any]] = None  # full feature manifest


class CodePattern(BaseModel):
    """Extracted code pattern from lineage analysis."""
    name: str  # pattern identifier
    signature: str  # function/method signature pattern
    error_handling: str  # exception handling style
    logging_pattern: str  # logging approach
    test_style: str  # testing conventions
    frequency: int  # how often this pattern appears
    stability_score: float  # 0-1 based on age and lack of changes


class Violation(BaseModel):
    """Prime Directive violation found in generated code."""
    directive_id: str  # which Prime Directive was violated
    description: str  # what the violation is
    location: str  # where in code it occurs
    severity: str  # "high", "medium", "low"
    suggested_fix: str  # how to fix it


class GenerationConfig(BaseModel):
    """Configuration for code generation based on emotional calibration."""
    extra_validation: bool = False  # add input validation
    verbose_logging: bool = True  # detailed logging
    extra_tests: int = 1  # multiplier for test generation
    defensive_programming: bool = False  # extra error handling
    documentation_level: str = "standard"  # "minimal", "standard", "comprehensive"


class MissionPlan(BaseModel):
    """Structured plan for autonomous mission execution."""
    mission_id: str
    objective: str
    emotional_payload: Dict[str, Any]  # intent, metaphors, anti-patterns
    branches: List[Dict[str, Any]]  # execution branches with tasks
    decision_points: List[Dict[str, Any]]  # where human oversight is needed
    risk_assessment: Dict[str, float]  # overall risk scores
    estimated_duration: int  # minutes


class NarrativeEntry(BaseModel):
    """Entry in the execution narrative stream."""
    timestamp: str
    action: str
    context: str
    emotional_note: Optional[str] = None
    decision_made: Optional[str] = None
    risk_level: str = "low"  # "low", "medium", "high"


class Dilemma(BaseModel):
    """Decision point requiring human oversight."""
    description: str
    context: str
    options: List[Dict[str, Any]]  # each with text, risk, emotional_impact
    recommendation: str
    urgency: str = "medium"  # "low", "medium", "high"


class MissionMemory(BaseModel):
    """After-action report for learning and future reference."""
    mission_id: str
    objective: str
    outcome: str  # "success", "partial", "failure", "paused"
    successes: List[str]  # what worked well
    failures: List[str]  # what broke or failed
    surprises: List[str]  # unexpected discoveries
    emotional_impact: str  # how it affected the "soul" of the system
    lessons_learned: List[str]  # key takeaways
    recommendations: List[str]  # future improvements


class EmotionalEntry(BaseModel):
    """Emotional context entry extending NexusData."""
    id: str
    content: str
    type: str  # e.g., 'commit_message', 'pr_comment', 'architectural_decision'
    metadata: Dict[str, str]  # additional context like author, timestamp, file_path
    relationships: List[str]  # ids of related entries
    resonance_score: Optional[float] = None  # emotional/historical weight (0-10)
    emotional_note: str  # human-readable emotional context
    intent_payload: Dict[str, Any]  # extracted developer intention
    sacred_moments: List[str]  # significant development moments


class FeedRequest(BaseModel):
    """Request for emotional ingestion."""
    source: str  # commit, comment, pr
    content: str  # raw text
    context: Dict[str, str]  # file_path, author, timestamp
    emotional_hints: List[str]  # keywords indicating emotion


class SeedConfig(BaseModel):
    """Configuration for lightweight Ghost deployment."""
    auto_seed: bool = True  # automatic codebase ingestion
    whisper_level: int = 3  # 1-5 suggestion intrusiveness
    resonance_enabled: bool = False  # network sharing
    guide_mode: str = "passive"  # 'passive'|'proactive'


class ResonancePacket(BaseModel):
    """Anonymized wisdom packet for network sharing."""
    patterns_hash: str  # anonymized pattern fingerprint
    prime_directives: List[str]  # hashed directives
    emotional_themes: List[str]  # aggregated emotional categories
    resonance_score: float  # collective weight
    source_count: int  # number of contributing instances
    timestamp: str


class GuideSuggestion(BaseModel):
    """Proactive guidance suggestion."""
    trigger_context: str  # file/pattern that triggered
    suggestion_type: str  # 'pattern'|'directive'|'alternative'
    content: str  # suggestion text
    confidence: float  # 0-1
    resonance_sources: int  # number of matching instances
    risk_level: str  # 'low'|'medium'|'high'


class NetworkNode(BaseModel):
    """Resonance network node information."""
    instance_id: str  # unique Ghost ID
    codebase_hash: str  # repo fingerprint
    capabilities: List[str]  # 'nexus'|'weaver'|'yolo'
    resonance_level: float
    last_seen: str


class HookConfig(BaseModel):
    """Configuration for hook integration."""
    hook_type: str  # 'pre-commit'|'pr'|'deploy'
    trigger_events: List[str]  # events that trigger the hook
    reflection_mode: str  # 'mirror'|'question'|'pause'
    enabled: bool = True


class WorkflowConfig(BaseModel):
    """Configuration for workflow orchestration."""
    workflow_type: str  # 'discovery'|'dilemma'|'retrospective'
    trigger_conditions: Dict[str, Any]  # conditions that start the workflow
    participant_roles: List[str]  # roles involved in the workflow
    facilitation_mode: str  # 'guided'|'facilitated'|'observed'


class SkillConfig(BaseModel):
    """Configuration for skill-based intelligence."""
    skill_type: str  # 'listening'|'pattern'|'silence'
    activation_threshold: float  # 0-1 threshold for activation
    context_sensitivity: int  # 1-5 sensitivity level
    learning_enabled: bool = True


class RuleConfig(BaseModel):
    """Configuration for governance rules."""
    rule_type: str  # 'presence'|'memory'|'growth'
    enforcement_level: str  # 'strict'|'flexible'|'advisory'
    scope: str  # 'individual'|'team'|'organization'


class IterationEvent(BaseModel):
    """Event in the iteration protocol."""
    event_type: str  # 'hook_trigger'|'workflow_start'|'skill_activation'
    context: Dict[str, Any]  # event context data
    participants: List[str]  # involved participants
    timestamp: str
    outcome: Optional[str] = None


class NoteFragment(BaseModel):
    """Data class for raw experience fragments."""
    timestamp: str
    type: str  # 'pause'|'dilemma'|'discovery'|'apology'
    content: str
    context: Dict[str, Any]
    emotional_weight: float
    threshold: str


class TransmutationRecord(BaseModel):
    """Data class for transmutation outcomes."""
    timestamp: str
    fragments_processed: int
    generated_hook: Optional[str] = None
    generated_workflow: Optional[str] = None
    generated_skill: Optional[str] = None
    rule_update: Optional[str] = None
    review_status: str  # 'pending'|'approved'|'rejected'


class ObservationConfig(BaseModel):
    """Data class for observation triggers."""
    pause_threshold: int  # seconds
    dilemma_patterns: List[str]
    discovery_indicators: List[str]
    enabled: bool


class TransmutationTrigger(BaseModel):
    """Data class for transmutation conditions."""
    fragment_threshold: int
    mission_complete: bool
    manual_trigger: bool


class Prediction(BaseModel):
    """Data class for predictive forecasts."""
    timestamp: str
    domain: str  # 'incident'|'team_health'|'architectural_decay'|'knowledge_loss'
    target: str  # file/module/engineer/team
    probability: float  # 0-1
    time_horizon: str  # 'immediate'|'week'|'month'
    confidence: float  # 0-1
    reasoning_chain: List[Dict[str, str]]
    intervention_suggested: bool
    constitutional_review: str  # 'approved'|'flagged'|'rejected'


class BehavioralModel(BaseModel):
    """Data class for engineer behavioral patterns."""
    engineer_id: str  # hashed/anonymized
    patterns: Dict[str, float]  # pause_frequency, hesitation_score, language_drift
    burnout_risk: float  # 0-1
    productivity_trends: List[float]
    consent_given: bool
    last_updated: str


class ConstitutionalPrinciple(BaseModel):
    """Data class for ethical principles."""
    id: str
    text: str
    category: str  # 'protect_engineer'|'privacy'|'consent'|'engineer_supremacy'
    weight: float  # 0-1
    examples: List[str]


class ForecastingAgent(BaseModel):
    """Data class for forecasting agents."""
    name: str  # 'Archivist'|'Empath'|'Sentinel'|'Historian'
    domain: str
    reasoning_style: str  # 'ToT'|'CoT'|'swarm'
    accuracy_history: List[float]
    active: bool


class SwarmConsensus(BaseModel):
    """Data class for multi-agent consensus."""
    task: str
    agents_involved: List[str]
    individual_predictions: List[Prediction]
    consensus_probability: float
    debate_log: str
    confidence_interval: tuple[float, float]


class DiffusionForecast(BaseModel):
    """Data class for code evolution forecasts."""
    current_state: str  # codebase snapshot
    future_states: List[Dict[str, Any]]  # probability, code_diff, risk_score
    recommended_path: str
    evolution_score: float
