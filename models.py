from pydantic import BaseModel
from typing import Dict, List, Optional
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