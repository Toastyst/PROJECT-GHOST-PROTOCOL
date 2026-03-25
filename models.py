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
