#!/usr/bin/env python3
"""
FRAGMENT HARVESTER: Automatic Fragment Collection Network

This module implements pervasive fragment harvesting across multiple sources:
- Cline chat conversations
- VSCode activity (edits, pauses, switches)
- Git operations (commits, diffs)
- Test executions (failures, successes)
- Error logs and stack traces
"""

import os
import re
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from autopoiesis import get_autopoiesis_engine
from models import NoteFragment


@dataclass
class HarvestSource:
    """Configuration for a fragment harvesting source."""
    name: str
    enabled: bool
    patterns: List[str]
    context_extractors: List[Callable]
    emotional_weights: Dict[str, float]
    cooldown_seconds: int = 60  # Prevent spam


class FragmentHarvester:
    """Pervasive fragment harvesting across development ecosystem."""

    def __init__(self):
        self.sources = self._initialize_sources()
        self.last_harvest = {}  # source -> timestamp
        self.engine = get_autopoiesis_engine()

    def _initialize_sources(self) -> Dict[str, HarvestSource]:
        """Initialize all harvesting sources."""
        return {
            "cline_chat": HarvestSource(
                name="cline_chat",
                enabled=True,
                patterns=[
                    r"should I (?:use|implement|try)",
                    r"what (?:if|about|would happen)",
                    r"but (?:then|what about|however)",
                    r"I'm (?:confused|stuck|unsure)",
                    r"this (?:feels|seems) (?:wrong|right|hacky)",
                ],
                context_extractors=[self._extract_chat_context],
                emotional_weights={"dilemma": 0.7, "pause": 0.4}
            ),

            "vscode_edits": HarvestSource(
                name="vscode_edits",
                enabled=True,
                patterns=[
                    r"TODO|FIXME|XXX|HACK",
                    r"// .* (?:temporary|hack|quick fix)",
                    r"# .* (?:temporary|hack|quick fix)",
                ],
                context_extractors=[self._extract_file_context],
                emotional_weights={"dilemma": 0.6, "discovery": 0.8}
            ),

            "git_commits": HarvestSource(
                name="git_commits",
                enabled=True,
                patterns=[
                    r"fix|Fix|FIX",
                    r"hack|Hack|HACK",
                    r"temporar|quick|fast",
                    r"oops|Oops|OOPS",
                    r"sorry|Sorry|SORRY",
                ],
                context_extractors=[self._extract_git_context],
                emotional_weights={"apology": 0.6, "discovery": 0.7}
            ),

            "test_failures": HarvestSource(
                name="test_failures",
                enabled=True,
                patterns=[
                    r"FAILED|ERROR|AssertionError",
                    r"expected .* but got",
                    r"test.*failed",
                ],
                context_extractors=[self._extract_test_context],
                emotional_weights={"discovery": 0.8, "apology": 0.5}
            ),

            "error_logs": HarvestSource(
                name="error_logs",
                enabled=True,
                patterns=[
                    r"Exception|Error|Traceback",
                    r"failed to|could not|unable to",
                    r"unexpected|unknown|strange",
                ],
                context_extractors=[self._extract_error_context],
                emotional_weights={"discovery": 0.7, "apology": 0.4}
            )
        }

    def harvest_from_chat(self, message: str, context: Dict[str, Any]) -> Optional[NoteFragment]:
        """Harvest fragments from Cline chat messages."""
        return self._harvest_from_source("cline_chat", message, context)

    def harvest_from_file_edit(self, file_path: str, content: str, edit_type: str) -> Optional[NoteFragment]:
        """Harvest fragments from file edits."""
        context = {"file": file_path, "edit_type": edit_type}
        return self._harvest_from_source("vscode_edits", content, context)

    def harvest_from_git_commit(self, commit_message: str, diff_stats: Dict[str, Any]) -> Optional[NoteFragment]:
        """Harvest fragments from git commits."""
        context = {"diff_stats": diff_stats}
        return self._harvest_from_source("git_commits", commit_message, context)

    def harvest_from_test_failure(self, test_name: str, error_message: str, traceback: str) -> Optional[NoteFragment]:
        """Harvest fragments from test failures."""
        content = f"{test_name}: {error_message}\n{traceback}"
        context = {"test_name": test_name}
        return self._harvest_from_source("test_failures", content, context)

    def harvest_from_error_log(self, log_entry: str, source: str) -> Optional[NoteFragment]:
        """Harvest fragments from error logs."""
        context = {"log_source": source}
        return self._harvest_from_source("error_logs", log_entry, context)

    def _harvest_from_source(self, source_name: str, content: str, context: Dict[str, Any]) -> Optional[NoteFragment]:
        """Generic harvesting from a configured source."""
        if not self.sources[source_name].enabled:
            return None

        # Check cooldown
        now = time.time()
        if source_name in self.last_harvest:
            if now - self.last_harvest[source_name] < self.sources[source_name].cooldown_seconds:
                return None

        source = self.sources[source_name]

        # Check patterns
        for pattern in source.patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Determine fragment type based on pattern and content
                fragment_type = self._classify_content(content, pattern)

                # Extract enhanced context
                enhanced_context = context.copy()
                for extractor in source.context_extractors:
                    try:
                        enhanced_context.update(extractor(content, context))
                    except Exception:
                        pass  # Ignore extractor failures

                # Get emotional weight
                emotional_weight = source.emotional_weights.get(fragment_type, 0.5)

                fragment = NoteFragment(
                    timestamp=datetime.now().isoformat(),
                    type=fragment_type,
                    content=content[:500],  # Limit content length
                    context=enhanced_context,
                    emotional_weight=emotional_weight,
                    threshold=f"{source_name}_pattern"
                )

                # Capture the fragment
                self.engine.capture_fragment(fragment.type, fragment.content, fragment.context)
                self.last_harvest[source_name] = now

                return fragment

        return None

    def _classify_content(self, content: str, matched_pattern: str) -> str:
        """Classify content into fragment type based on patterns and content analysis."""
        content_lower = content.lower()

        # Question patterns -> dilemma
        if any(word in content_lower for word in ["should", "what if", "how", "why", "when"]):
            return "dilemma"

        # Insight patterns -> discovery
        if any(word in content_lower for word in ["aha", "realized", "eureka", "discovered", "found"]):
            return "discovery"

        # Error/apology patterns -> apology
        if any(word in content_lower for word in ["sorry", "mistake", "failed", "error", "oops"]):
            return "apology"

        # Pause/reflection patterns -> pause
        if any(word in content_lower for word in ["pause", "reflect", "think", "consider", "wait"]):
            return "pause"

        # Default based on source pattern type
        if "dilemma" in matched_pattern or "what" in matched_pattern:
            return "dilemma"
        elif "fix" in matched_pattern or "error" in matched_pattern:
            return "discovery"
        else:
            return "pause"

    def _extract_chat_context(self, content: str, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context from chat messages."""
        context = {}

        # Detect if this is a question
        if "?" in content:
            context["has_question"] = True
            context["question_count"] = content.count("?")

        # Detect code references
        code_patterns = [r"`[^`]+`", r"```[\s\S]*?```"]
        code_refs = []
        for pattern in code_patterns:
            matches = re.findall(pattern, content)
            code_refs.extend(matches)

        if code_refs:
            context["code_references"] = len(code_refs)
            context["code_samples"] = code_refs[:3]  # First 3 samples

        # Detect file references
        file_patterns = [r"\b\w+\.(py|js|ts|java|cpp|go|rs|md)\b"]
        file_matches = re.findall("|".join(file_patterns), content)
        if file_matches:
            context["referenced_files"] = list(set(file_matches))

        return context

    def _extract_file_context(self, content: str, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context from file edit content."""
        context = {}

        file_path = base_context.get("file", "")
        if file_path:
            context["file_extension"] = Path(file_path).suffix
            context["file_name"] = Path(file_path).name

        # Count lines and complexity indicators
        lines = content.split('\n')
        context["line_count"] = len(lines)

        # Detect technical debt markers
        debt_markers = ["TODO", "FIXME", "XXX", "HACK", "temporary", "hack"]
        debt_count = sum(1 for marker in debt_markers if marker.upper() in content.upper())
        context["technical_debt_markers"] = debt_count

        return context

    def _extract_git_context(self, content: str, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context from git commit messages."""
        context = {}

        # Analyze commit message sentiment
        negative_words = ["fix", "hack", "oops", "sorry", "temporary", "quick"]
        positive_words = ["implement", "add", "improve", "refactor", "clean"]

        negative_count = sum(1 for word in negative_words if word in content.lower())
        positive_count = sum(1 for word in positive_words if word in content.lower())

        context["sentiment_negative"] = negative_count
        context["sentiment_positive"] = positive_count

        # Extract diff stats if available
        diff_stats = base_context.get("diff_stats", {})
        context.update(diff_stats)

        return context

    def _extract_test_context(self, content: str, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context from test failure content."""
        context = {}

        # Parse test name
        test_name = base_context.get("test_name", "")
        if test_name:
            context["test_module"] = test_name.split("::")[0] if "::" in test_name else test_name
            context["test_function"] = test_name.split("::")[-1] if "::" in test_name else ""

        # Analyze error type
        if "AssertionError" in content:
            context["error_type"] = "assertion"
        elif "ValueError" in content or "TypeError" in content:
            context["error_type"] = "type_value"
        elif "ImportError" in content or "ModuleNotFoundError" in content:
            context["error_type"] = "import"
        else:
            context["error_type"] = "other"

        # Extract stack trace depth
        stack_lines = [line for line in content.split('\n') if 'File "' in line]
        context["stack_depth"] = len(stack_lines)

        return context

    def _extract_error_context(self, content: str, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context from error log entries."""
        context = {}

        # Determine log level
        if "ERROR" in content or "Exception" in content:
            context["log_level"] = "error"
        elif "WARNING" in content or "Warn" in content:
            context["log_level"] = "warning"
        else:
            context["log_level"] = "info"

        # Extract source information
        source = base_context.get("log_source", "")
        context["error_source"] = source

        # Analyze error patterns
        if "database" in content.lower():
            context["error_domain"] = "database"
        elif "network" in content.lower() or "connection" in content.lower():
            context["error_domain"] = "network"
        elif "file" in content.lower() or "io" in content.lower():
            context["error_domain"] = "filesystem"
        else:
            context["error_domain"] = "application"

        return context

    def get_harvest_stats(self) -> Dict[str, Any]:
        """Get harvesting statistics."""
        return {
            "sources_enabled": sum(1 for s in self.sources.values() if s.enabled),
            "total_sources": len(self.sources),
            "last_harvest_times": self.last_harvest.copy(),
            "fragments_captured": self.engine.get_fragment_count()
        }


# Global harvester instance
_harvester = None

def get_fragment_harvester() -> FragmentHarvester:
    """Get the global fragment harvester instance."""
    global _harvester
    if _harvester is None:
        _harvester = FragmentHarvester()
    return _harvester