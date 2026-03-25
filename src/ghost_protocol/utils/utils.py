import git
import os
import json
from typing import List, Dict, Any
from src.ghost_protocol.utils.config import Config
import ast
import re


class GitUtils:
    """Utility functions for Git repository operations."""

    @staticmethod
    def get_commit_history(repo_path: str, limit: int = 100) -> List[Dict[str, str]]:
        """Extract commit messages and metadata from repository."""
        try:
            repo = git.Repo(repo_path)
            commits = list(repo.iter_commits(max_count=limit))

            commit_data = []
            for commit in commits:
                commit_data.append({
                    'hash': commit.hexsha,
                    'message': commit.message.strip(),
                    'author': commit.author.name,
                    'date': str(commit.authored_datetime),
                    'files': [item.a_path for item in commit.tree.traverse() if item.type == 'blob'][:10]  # Limit files
                })

            return commit_data
        except Exception as e:
            print(f"Error accessing git repository: {e}")
            return []

    @staticmethod
    def get_file_changes(repo_path: str, commit_hash: str) -> Dict[str, str]:
        """Get file changes for a specific commit."""
        try:
            repo = git.Repo(repo_path)
            commit = repo.commit(commit_hash)

            changes = {}
            if commit.parents:
                diff = commit.parents[0].diff(commit, create_patch=True)
                for patch in diff:
                    if patch.a_path:
                        changes[patch.a_path] = patch.diff.decode('utf-8', errors='ignore')

            return changes
        except Exception as e:
            print(f"Error getting file changes: {e}")
            return {}

    @staticmethod
    def get_blame_info(repo_path: str, file_path: str) -> Dict[str, Any]:
        """Extract blame information for a file - author history and institutional knowledge."""
        try:
            repo = git.Repo(repo_path)
            blame = repo.blame('HEAD', file_path)

            author_stats = {}
            total_lines = 0

            for commit, lines in blame:
                author = commit.author.name
                line_count = len(lines)
                total_lines += line_count

                if author not in author_stats:
                    author_stats[author] = {
                        'lines': 0,
                        'commits': set(),
                        'last_commit': commit.authored_datetime
                    }

                author_stats[author]['lines'] += line_count
                author_stats[author]['commits'].add(commit.hexsha)
                if commit.authored_datetime > author_stats[author]['last_commit']:
                    author_stats[author]['last_commit'] = commit.authored_datetime

            # Convert sets to counts
            for author in author_stats:
                author_stats[author]['commits'] = len(author_stats[author]['commits'])

            return {
                'file_path': file_path,
                'total_lines': total_lines,
                'author_stats': author_stats,
                'primary_author': max(author_stats.keys(), key=lambda x: author_stats[x]['lines']) if author_stats else None
            }
        except Exception as e:
            print(f"Error getting blame info for {file_path}: {e}")
            return {}

    @staticmethod
    def find_dead_code_comments(repo_path: str) -> List[Dict[str, Any]]:
        """Find dead code comments and technical debt indicators."""
        dead_comments = []

        try:
            # Walk through all Python files
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    if file.endswith('.py') and not file.startswith('.'):
                        file_path = os.path.join(root, file)

                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()

                            for i, line in enumerate(lines, 1):
                                stripped = line.strip()
                                if stripped.startswith('#') or '"""' in stripped or "'''" in stripped:
                                    comment_text = stripped.lower()

                                    # Look for technical debt keywords
                                    debt_indicators = ['todo', 'fixme', 'hack', 'workaround', 'temporary',
                                                     'kludge', 'debt', 'refactor', 'cleanup', 'legacy']

                                    for indicator in debt_indicators:
                                        if indicator in comment_text:
                                            dead_comments.append({
                                                'file_path': file_path,
                                                'line': i,
                                                'content': stripped,
                                                'indicator': indicator,
                                                'context': ''.join(lines[max(0, i-3):min(len(lines), i+2)]).strip()
                                            })
                                            break

                        except Exception as e:
                            print(f"Error scanning {file_path}: {e}")

        except Exception as e:
            print(f"Error finding dead code comments: {e}")

        return dead_comments

    @staticmethod
    def get_correction_patterns(repo_path: str) -> List[Dict[str, Any]]:
        """Analyze git history for patterns of correction and unwritten rules."""
        patterns = []

        try:
            repo = git.Repo(repo_path)

            # Look for revert commits
            revert_commits = []
            for commit in repo.iter_commits(max_count=200):
                if 'revert' in commit.message.lower():
                    revert_commits.append({
                        'hash': commit.hexsha,
                        'message': commit.message.strip(),
                        'author': commit.author.name,
                        'date': str(commit.authored_datetime)
                    })

            if revert_commits:
                patterns.append({
                    'type': 'revert_pattern',
                    'description': f'Found {len(revert_commits)} revert commits - indicates areas requiring careful changes',
                    'examples': revert_commits[:3],  # First 3 examples
                    'frequency': len(revert_commits)
                })

            # Look for commits with "fix", "bug", "regression"
            bug_fixes = []
            for commit in repo.iter_commits(max_count=200):
                msg_lower = commit.message.lower()
                if any(word in msg_lower for word in ['fix', 'bug', 'regression', 'hotfix']):
                    bug_fixes.append({
                        'hash': commit.hexsha,
                        'message': commit.message.strip(),
                        'author': commit.author.name
                    })

            if bug_fixes:
                patterns.append({
                    'type': 'bug_fix_pattern',
                    'description': f'Found {len(bug_fixes)} bug fix commits - indicates fragile areas',
                    'examples': bug_fixes[:3],
                    'frequency': len(bug_fixes)
                })

            # Look for commits with "review", "feedback", "as per"
            review_commits = []
            for commit in repo.iter_commits(max_count=200):
                msg_lower = commit.message.lower()
                if any(phrase in msg_lower for phrase in ['review', 'feedback', 'as per', 'addressed']):
                    review_commits.append({
                        'hash': commit.hexsha,
                        'message': commit.message.strip(),
                        'author': commit.author.name
                    })

            if review_commits:
                patterns.append({
                    'type': 'review_feedback_pattern',
                    'description': f'Found {len(review_commits)} commits addressing review feedback - indicates code review standards',
                    'examples': review_commits[:3],
                    'frequency': len(review_commits)
                })

        except Exception as e:
            print(f"Error analyzing correction patterns: {e}")

        return patterns

    @staticmethod
    def extract_emotional_keywords(text: str) -> Dict[str, Any]:
        """Extract emotional keywords and calculate resonance score."""
        text_lower = text.lower()

        # Emotional keyword categories
        emotional_words = {
            'frustration': ['garbage', 'mess', 'broken', 'sucks', 'terrible', 'awful', 'horrible'],
            'urgency': ['urgent', 'critical', 'emergency', 'hotfix', 'asap', 'immediate'],
            'technical_debt': ['hack', 'workaround', 'kludge', 'temporary', 'quick fix', 'bandaid'],
            'complexity': ['complex', 'complicated', 'tricky', 'nightmare', 'hell', 'pain'],
            'stability': ['stable', 'solid', 'robust', 'reliable', 'battle-tested'],
            'caution': ['careful', 'dangerous', 'risky', 'fragile', 'delicate']
        }

        found_words = {}
        total_score = 0

        for category, words in emotional_words.items():
            category_words = [word for word in words if word in text_lower]
            if category_words:
                found_words[category] = category_words
                # Scoring weights
                if category in ['frustration', 'technical_debt', 'complexity', 'caution']:
                    total_score += len(category_words) * 2
                elif category == 'urgency':
                    total_score += len(category_words) * 1.5
                elif category == 'stability':
                    total_score -= len(category_words) * 0.5  # Stability reduces risk

        # Cap score at 10
        resonance_score = min(total_score, 10.0)

        return {
            'found_words': found_words,
            'resonance_score': resonance_score,
            'emotional_categories': list(found_words.keys())
        }


class CodeAnalyzer:
    """Utility functions for code analysis."""

    @staticmethod
    def extract_functions_from_file(file_path: str) -> List[Dict[str, Any]]:
        """Extract function definitions from a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node) or ""
                    })

            return functions
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
            return []

    @staticmethod
    def extract_classes_from_file(file_path: str) -> List[Dict[str, Any]]:
        """Extract class definitions from a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'bases': [base.id if hasattr(base, 'id') else str(base) for base in node.bases],
                        'docstring': ast.get_docstring(node) or ""
                    })

            return classes
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
            return []


class LLMUtils:
    """Utility functions for LLM interactions with fallback support."""

    @staticmethod
    def _call_llm(provider, messages, **kwargs):
        """Call LLM for a specific provider."""
        if provider.startswith("openai/"):
            from openai import OpenAI
            model = provider.split("/", 1)[1]
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            return client.chat.completions.create(model=model, messages=messages, **kwargs)
        elif provider.startswith("grok/"):
            from openai import OpenAI
            model = provider.split("/", 1)[1]
            client = OpenAI(api_key=os.getenv("GROK_API_KEY"), base_url="https://api.x.ai/v1")
            return client.chat.completions.create(model=model, messages=messages, **kwargs)
        elif provider.startswith("mock/"):
            # Mock response for testing
            content = f"Mock response for: {messages[0]['content'][:100]}..."
            class MockMessage:
                def __init__(self):
                    self.content = content
            class MockChoice:
                def __init__(self):
                    self.message = MockMessage()
            class MockResponse:
                def __init__(self):
                    self.choices = [MockChoice()]
            return MockResponse()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def __init__(self):
        Config.validate()

    def generate_code(self, prompt: str, context: str = "") -> str:
        """Generate code using LLM with fallback support."""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        for provider in Config.LLM_PROVIDERS:
            try:
                response = self._call_llm(provider, messages=[{"role": "user", "content": full_prompt}], max_tokens=Config.MAX_TOKENS, temperature=Config.TEMPERATURE)
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Fallback: {provider} failed: {e}")
                continue

        return ""

    def analyze_code(self, code: str, task: str) -> str:
        """Analyze code for specific tasks with fallback support."""
        prompt = f"Analyze the following code for: {task}\n\nCode:\n{code}"

        for provider in Config.LLM_PROVIDERS:
            try:
                response = self._call_llm(provider, messages=[{"role": "user", "content": prompt}], max_tokens=Config.MAX_TOKENS, temperature=Config.TEMPERATURE)
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Fallback: {provider} failed: {e}")
                continue

        return ""

    def generate_with_reasoning(self, prompt: str) -> str:
        """Generate response with reasoning capabilities (simulates o1-style)."""
        # For now, use regular generation but could be enhanced with reasoning chains
        reasoning_prompt = f"""Think step by step about this problem. Provide a detailed analysis with reasoning.

{prompt}

Structure your response with:
1. Problem breakdown
2. Step-by-step reasoning
3. Conclusions
4. Innovative ideas (if applicable)"""

        return self.generate_code(reasoning_prompt)


class BehavioralAnalyzer:
    """Opt-in behavioral pattern analysis with local-only storage."""

    def __init__(self):
        self.storage_path = "behavioral_model/"  # Local directory for opt-in data
        os.makedirs(self.storage_path, exist_ok=True)

    def check_consent(self, engineer_id: str) -> bool:
        """Check if engineer has given consent for behavioral tracking."""
        consent_file = os.path.join(self.storage_path, f"{engineer_id}_consent.txt")
        return os.path.exists(consent_file)

    def grant_consent(self, engineer_id: str):
        """Grant consent for behavioral tracking."""
        import time
        consent_file = os.path.join(self.storage_path, f"{engineer_id}_consent.txt")
        with open(consent_file, 'w') as f:
            f.write(f"Consent granted at {time.time()}")

    def capture_fragment(self, activity: str, engineer_id: str):
        """Capture a behavioral fragment if consent given."""
        if not self.check_consent(engineer_id):
            return None

        from src.ghost_protocol.models.models import NoteFragment
        import time
        return NoteFragment(
            timestamp=str(time.time()),
            type='behavioral',
            content=f"Activity: {activity}",
            context={'engineer_id': engineer_id, 'activity': activity},
            emotional_weight=0.5,  # Neutral weight for behavioral data
            threshold='low'
        )

    def analyze_patterns(self, engineer_id: str) -> Dict[str, float]:
        """Analyze behavioral patterns from stored data."""
        if not self.check_consent(engineer_id):
            return {}

        # Load stored behavioral data
        data_file = os.path.join(self.storage_path, f"{engineer_id}_data.json")
        if not os.path.exists(data_file):
            return {'pause_frequency': 0.0, 'hesitation_score': 0.0, 'language_drift': 0.0}

        try:
            with open(data_file, 'r') as f:
                data = json.load(f)

            # Simple pattern analysis
            activities = data.get('activities', [])
            if not activities:
                return {'pause_frequency': 0.0, 'hesitation_score': 0.0, 'language_drift': 0.0}

            # Calculate patterns
            pauses = sum(1 for a in activities if 'pause' in a.lower())
            hesitations = sum(1 for a in activities if 'hesitat' in a.lower())
            drifts = sum(1 for a in activities if 'drift' in a.lower() or 'change' in a.lower())

            total = len(activities)
            return {
                'pause_frequency': pauses / total if total > 0 else 0.0,
                'hesitation_score': hesitations / total if total > 0 else 0.0,
                'language_drift': drifts / total if total > 0 else 0.0
            }
        except Exception as e:
            print(f"Error analyzing behavioral patterns: {e}")
            return {'pause_frequency': 0.0, 'hesitation_score': 0.0, 'language_drift': 0.0}

    def store_behavioral_data(self, engineer_id: str, activity: str):
        """Store behavioral data locally."""
        if not self.check_consent(engineer_id):
            return

        import time
        data_file = os.path.join(self.storage_path, f"{engineer_id}_data.json")

        # Load existing data
        data = {'activities': [], 'timestamps': []}
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
            except:
                pass

        # Append new activity
        data['activities'].append(activity)
        data['timestamps'].append(time.time())

        # Keep only last 1000 activities
        if len(data['activities']) > 1000:
            data['activities'] = data['activities'][-1000:]
            data['timestamps'] = data['timestamps'][-1000:]

        # Save
        with open(data_file, 'w') as f:
            json.dump(data, f)


def capture_behavioral_fragment(activity: str, engineer_id: str):
    """Global function to capture behavioral fragment."""
    analyzer = BehavioralAnalyzer()
    return analyzer.capture_fragment(activity, engineer_id)


class DiffusionForecaster:
    """Diffusion-based forecasting for code evolution and architectural changes."""

    def __init__(self):
        self.llm = LLMUtils()
        self.evolution_patterns = self._load_evolution_patterns()

    def _load_evolution_patterns(self) -> Dict[str, Any]:
        """Load common code evolution patterns."""
        return {
            "refactoring_patterns": [
                "extract_method", "rename_variable", "move_class", "split_module"
            ],
            "architecture_patterns": [
                "add_layer", "remove_dependency", "introduce_interface", "microservice_split"
            ],
            "quality_patterns": [
                "add_tests", "improve_error_handling", "optimize_performance", "enhance_security"
            ]
        }

    async def forecast_code_evolution(self, module: str, scenarios: List[str], current_state: str = "") -> Dict[str, Any]:
        """Forecast code evolution using diffusion-inspired probabilistic modeling."""
        try:
            # Generate multiple evolution scenarios
            evolution_scenarios = await self._generate_evolution_scenarios(module, scenarios, current_state)

            # Apply diffusion process (iterative refinement)
            diffused_scenarios = await self._apply_diffusion_process(evolution_scenarios)

            # Calculate probabilities and risks
            probabilistic_forecast = self._calculate_probabilistic_forecast(diffused_scenarios)

            return {
                "module": module,
                "current_state": current_state,
                "evolution_scenarios": diffused_scenarios,
                "probabilistic_forecast": probabilistic_forecast,
                "recommended_path": self._select_recommended_path(probabilistic_forecast),
                "evolution_score": self._calculate_evolution_score(probabilistic_forecast)
            }

        except Exception as e:
            print(f"Error in diffusion forecasting: {e}")
            return {
                "error": str(e),
                "module": module,
                "evolution_scenarios": [],
                "probabilistic_forecast": {},
                "recommended_path": "maintain_current",
                "evolution_score": 0.0
            }

    async def _generate_evolution_scenarios(self, module: str, scenarios: List[str], current_state: str) -> List[Dict[str, Any]]:
        """Generate initial evolution scenarios."""
        generated_scenarios = []

        for scenario in scenarios:
            prompt = f"""
Generate a detailed code evolution scenario for module: {module}

Scenario: {scenario}
Current State: {current_state[:500]}...

Describe the evolution including:
- Specific code changes
- Architectural impacts
- Benefits and risks
- Timeline estimation
- Success probability

Be specific about what code would change and why.
"""

            try:
                scenario_detail = await self.llm.generate_with_reasoning(prompt)
                generated_scenarios.append({
                    "scenario": scenario,
                    "description": scenario_detail,
                    "initial_probability": 0.5,  # Base probability
                    "complexity": self._assess_scenario_complexity(scenario_detail)
                })
            except Exception as e:
                print(f"Error generating scenario {scenario}: {e}")

        return generated_scenarios

    async def _apply_diffusion_process(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply diffusion-like iterative refinement to scenarios."""
        diffused = []

        for scenario in scenarios:
            # Diffusion step 1: Refine based on dependencies
            refinement_prompt = f"""
Refine this evolution scenario considering dependencies and constraints:

{scenario['description']}

Consider:
- External dependencies
- Breaking changes
- Migration path
- Rollback strategy
- Testing requirements

Provide a more refined and realistic scenario.
"""

            try:
                refined = await self.llm.generate_with_reasoning(refinement_prompt)

                # Diffusion step 2: Add uncertainty modeling
                uncertainty_prompt = f"""
Add uncertainty analysis to this refined scenario:

{refined}

Identify:
- Key uncertainties
- Risk mitigation strategies
- Alternative outcomes
- Confidence intervals

Provide probabilistic assessment.
"""

                uncertainty_analysis = await self.llm.generate_with_reasoning(uncertainty_prompt)

                diffused.append({
                    **scenario,
                    "refined_description": refined,
                    "uncertainty_analysis": uncertainty_analysis,
                    "diffusion_steps": 2
                })

            except Exception as e:
                print(f"Error in diffusion process for scenario: {e}")
                diffused.append(scenario)  # Keep original if diffusion fails

        return diffused

    def _calculate_probabilistic_forecast(self, diffused_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate probabilistic forecast from diffused scenarios."""
        forecast = {
            "scenarios": [],
            "total_probability_mass": 0.0,
            "risk_distribution": {"low": 0, "medium": 0, "high": 0},
            "timeline_distribution": {"short": 0, "medium": 0, "long": 0}
        }

        for scenario in diffused_scenarios:
            # Extract probability from uncertainty analysis
            probability = self._extract_probability_from_text(scenario.get('uncertainty_analysis', ''))
            risk_level = self._assess_risk_level(scenario.get('refined_description', ''))
            timeline = self._estimate_timeline(scenario.get('refined_description', ''))

            scenario_forecast = {
                "scenario": scenario['scenario'],
                "probability": probability,
                "risk_level": risk_level,
                "timeline": timeline,
                "complexity": scenario.get('complexity', 'medium')
            }

            forecast['scenarios'].append(scenario_forecast)
            forecast['total_probability_mass'] += probability
            forecast['risk_distribution'][risk_level] += 1
            forecast['timeline_distribution'][timeline] += 1

        # Normalize probabilities
        if forecast['scenarios']:
            total_mass = forecast['total_probability_mass']
            for scenario in forecast['scenarios']:
                scenario['normalized_probability'] = scenario['probability'] / total_mass if total_mass > 0 else 0

        return forecast

    def _extract_probability_from_text(self, text: str) -> float:
        """Extract probability estimate from text."""
        text_lower = text.lower()

        # Look for probability indicators
        if 'high probability' in text_lower or 'very likely' in text_lower:
            return 0.8
        elif 'medium probability' in text_lower or 'moderately likely' in text_lower:
            return 0.6
        elif 'low probability' in text_lower or 'unlikely' in text_lower:
            return 0.3
        elif 'certain' in text_lower or 'definite' in text_lower:
            return 0.9
        else:
            return 0.5  # Default

    def _assess_risk_level(self, text: str) -> str:
        """Assess risk level from scenario description."""
        text_lower = text.lower()

        high_risk_words = ['breaking', 'complex', 'risky', 'challenging', 'disruptive']
        low_risk_words = ['simple', 'safe', 'minimal', 'straightforward', 'low risk']

        high_count = sum(1 for word in high_risk_words if word in text_lower)
        low_count = sum(1 for word in low_risk_words if word in text_lower)

        if high_count > low_count:
            return 'high'
        elif low_count > high_count:
            return 'low'
        else:
            return 'medium'

    def _estimate_timeline(self, text: str) -> str:
        """Estimate timeline from scenario description."""
        text_lower = text.lower()

        if 'weeks' in text_lower or 'month' in text_lower:
            return 'long'
        elif 'days' in text_lower or 'week' in text_lower:
            return 'medium'
        elif 'hours' in text_lower or 'immediate' in text_lower:
            return 'short'
        else:
            return 'medium'

    def _assess_scenario_complexity(self, text: str) -> str:
        """Assess complexity of evolution scenario."""
        text_lower = text.lower()

        if 'complex' in text_lower or 'challenging' in text_lower or 'architectural' in text_lower:
            return 'high'
        elif 'simple' in text_lower or 'straightforward' in text_lower:
            return 'low'
        else:
            return 'medium'

    def _select_recommended_path(self, probabilistic_forecast: Dict[str, Any]) -> str:
        """Select the recommended evolution path."""
        scenarios = probabilistic_forecast.get('scenarios', [])

        if not scenarios:
            return "maintain_current"

        # Select scenario with highest normalized probability and lowest risk
        best_scenario = max(scenarios, key=lambda s: s.get('normalized_probability', 0) - (0.2 if s.get('risk_level') == 'high' else 0))

        return best_scenario['scenario']

    def _calculate_evolution_score(self, probabilistic_forecast: Dict[str, Any]) -> float:
        """Calculate overall evolution score."""
        scenarios = probabilistic_forecast.get('scenarios', [])

        if not scenarios:
            return 0.0

        # Score based on probability distribution and risk balance
        avg_probability = sum(s.get('normalized_probability', 0) for s in scenarios) / len(scenarios)
        risk_balance = probabilistic_forecast['risk_distribution']

        # Prefer balanced risk distribution
        risk_score = 1.0 - abs(risk_balance['high'] - risk_balance['low']) / max(len(scenarios), 1)

        return (avg_probability + risk_score) / 2
