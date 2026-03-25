import git
import os
from typing import List, Dict, Any
from config import Config
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
