"""
Review Workflow for AUTOPOIESIS Transmutations

Handles human review and approval of generated structures before repository integration.
"""

import os
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.ghost_protocol.models.models import TransmutationRecord


class ReviewWorkflow:
    """Manages the review and approval process for autopoiesis transmutations."""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.pending_reviews_file = self.project_root / ".autopoiesis" / "pending_reviews.json"
        self.approved_structures_dir = self.project_root / ".autopoiesis" / "approved"
        self.review_history_file = self.project_root / ".autopoiesis" / "review_history.json"

        # Create directories
        self.pending_reviews_file.parent.mkdir(exist_ok=True)
        self.approved_structures_dir.mkdir(exist_ok=True)

    def submit_for_review(self, record: TransmutationRecord, generated_structures: Dict[str, str]) -> str:
        """Submit a transmutation record and its generated structures for review."""
        review_id = f"review_{record.timestamp.replace(':', '').replace('-', '').replace('.', '')}"

        review_data = {
            "review_id": review_id,
            "transmutation_record": record.dict(),
            "generated_structures": generated_structures,
            "submitted_at": datetime.now().isoformat(),
            "status": "pending",
            "reviewer": None,
            "review_notes": "",
            "approved_at": None
        }

        # Save to pending reviews
        pending_reviews = self._load_pending_reviews()
        pending_reviews[review_id] = review_data
        self._save_pending_reviews(pending_reviews)

        # Save generated structures for review
        review_dir = self.approved_structures_dir / "pending" / review_id
        review_dir.mkdir(exist_ok=True)

        for structure_type, content in generated_structures.items():
            if structure_type in ["hook", "skill"]:
                # Save as Python file
                filename = f"generated_{structure_type}_{review_id}.py"
                (review_dir / filename).write_text(content)
            elif structure_type in ["workflow", "rule"]:
                # Save as JSON file
                filename = f"generated_{structure_type}_{review_id}.json"
                (review_dir / filename).write_text(content)

        return review_id

    def approve_review(self, review_id: str, reviewer: str = "unknown", notes: str = "") -> bool:
        """Approve a pending review and prepare structures for commit."""
        pending_reviews = self._load_pending_reviews()

        if review_id not in pending_reviews:
            return False

        review_data = pending_reviews[review_id]
        review_data["status"] = "approved"
        review_data["reviewer"] = reviewer
        review_data["review_notes"] = notes
        review_data["approved_at"] = datetime.now().isoformat()

        # Move from pending to approved
        pending_reviews.pop(review_id)

        # Save updated pending reviews
        self._save_pending_reviews(pending_reviews)

        # Add to review history
        review_history = self._load_review_history()
        review_history[review_id] = review_data
        self._save_review_history(review_history)

        # Move structures to approved directory
        pending_dir = self.approved_structures_dir / "pending" / review_id
        approved_dir = self.approved_structures_dir / "approved" / review_id
        approved_dir.mkdir(parents=True, exist_ok=True)

        if pending_dir.exists():
            for file_path in pending_dir.glob("*"):
                if file_path.is_file():
                    file_path.rename(approved_dir / file_path.name)

            # Remove empty pending directory
            try:
                pending_dir.rmdir()
            except:
                pass  # Directory not empty, that's ok

        return True

    def reject_review(self, review_id: str, reviewer: str = "unknown", notes: str = "") -> bool:
        """Reject a pending review."""
        pending_reviews = self._load_pending_reviews()

        if review_id not in pending_reviews:
            return False

        review_data = pending_reviews[review_id]
        review_data["status"] = "rejected"
        review_data["reviewer"] = reviewer
        review_data["review_notes"] = notes
        review_data["rejected_at"] = datetime.now().isoformat()

        # Move from pending to rejected
        pending_reviews.pop(review_id)

        # Add to review history
        review_history = self._load_review_history()
        review_history[review_id] = review_data
        self._save_review_history(review_history)

        # Clean up pending structures
        pending_dir = self.approved_structures_dir / "pending" / review_id
        if pending_dir.exists():
            import shutil
            shutil.rmtree(pending_dir, ignore_errors=True)

        return True

    def commit_approved_structures(self, review_id: str) -> bool:
        """Commit approved structures to the repository."""
        try:
            review_history = self._load_review_history()

            if review_id not in review_history:
                return False

            review_data = review_history[review_id]
            if review_data["status"] != "approved":
                return False

            approved_dir = self.approved_structures_dir / "approved" / review_id
            if not approved_dir.exists():
                return False

            # Determine target directories based on structure types
            transmutation_record = review_data["transmutation_record"]
            generated_structures = review_data["generated_structures"]

            commit_files = []

            for structure_type in generated_structures.keys():
                if structure_type == "hook":
                    # Hooks go to git_hooks directory
                    target_dir = self.project_root / "git_hooks"
                    target_dir.mkdir(exist_ok=True)

                    hook_files = list(approved_dir.glob("generated_hook_*.py"))
                    for hook_file in hook_files:
                        target_file = target_dir / f"autopoiesis_{hook_file.name}"
                        hook_file.copy(target_file)
                        commit_files.append(str(target_file))

                elif structure_type == "workflow":
                    # Workflows go to workflow_templates directory
                    target_dir = self.project_root / "workflow_templates"
                    target_dir.mkdir(exist_ok=True)

                    workflow_files = list(approved_dir.glob("generated_workflow_*.json"))
                    for workflow_file in workflow_files:
                        target_file = target_dir / f"autopoiesis_{workflow_file.name}"
                        workflow_file.copy(target_file)
                        commit_files.append(str(target_file))

                elif structure_type == "skill":
                    # Skills go to project root or skills directory
                    target_dir = self.project_root / "skills"
                    target_dir.mkdir(exist_ok=True)

                    skill_files = list(approved_dir.glob("generated_skill_*.py"))
                    for skill_file in skill_files:
                        target_file = target_dir / f"autopoiesis_{skill_file.name}"
                        skill_file.copy(target_file)
                        commit_files.append(str(target_file))

                elif structure_type == "rule":
                    # Rules go to project root
                    rule_files = list(approved_dir.glob("generated_rule_*.json"))
                    for rule_file in rule_files:
                        target_file = self.project_root / f"autopoiesis_{rule_file.name}"
                        rule_file.copy(target_file)
                        commit_files.append(str(target_file))

            if not commit_files:
                return False

            # Create commit message
            commit_message = f"AUTOPOIESIS: Integrate transmutation {review_id}\n\n"
            commit_message += f"Generated from {transmutation_record['fragments_processed']} fragments\n"
            commit_message += f"Approved by: {review_data.get('reviewer', 'unknown')}\n"
            commit_message += f"Structures: {', '.join(generated_structures.keys())}\n\n"
            commit_message += "This commit was automatically generated by the AUTOPOIESIS system."

            # Stage and commit files
            self._git_add(commit_files)
            self._git_commit(commit_message)

            # Mark as committed
            review_data["committed_at"] = datetime.now().isoformat()
            review_data["committed_files"] = commit_files
            self._save_review_history(review_history)

            return True

        except Exception as e:
            print(f"Error committing approved structures: {e}")
            return False

    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """Get all pending reviews."""
        pending_reviews = self._load_pending_reviews()
        return list(pending_reviews.values())

    def get_review_details(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific review."""
        # Check pending first
        pending_reviews = self._load_pending_reviews()
        if review_id in pending_reviews:
            return pending_reviews[review_id]

        # Check history
        review_history = self._load_review_history()
        if review_id in review_history:
            return review_history[review_id]

        return None

    def _load_pending_reviews(self) -> Dict[str, Any]:
        """Load pending reviews from file."""
        if self.pending_reviews_file.exists():
            try:
                with open(self.pending_reviews_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_pending_reviews(self, reviews: Dict[str, Any]) -> None:
        """Save pending reviews to file."""
        with open(self.pending_reviews_file, 'w') as f:
            json.dump(reviews, f, indent=2)

    def _load_review_history(self) -> Dict[str, Any]:
        """Load review history from file."""
        if self.review_history_file.exists():
            try:
                with open(self.review_history_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_review_history(self, history: Dict[str, Any]) -> None:
        """Save review history to file."""
        with open(self.review_history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def _git_add(self, files: List[str]) -> None:
        """Stage files for commit."""
        try:
            cmd = ["git", "add"] + files
            subprocess.run(cmd, cwd=self.project_root, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Git add failed: {e}")

    def _git_commit(self, message: str) -> None:
        """Commit staged files."""
        try:
            cmd = ["git", "commit", "-m", message]
            subprocess.run(cmd, cwd=self.project_root, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Git commit failed: {e}")


# Global review workflow instance
_review_workflow = None

def get_review_workflow() -> ReviewWorkflow:
    """Get the global review workflow instance."""
    global _review_workflow
    if _review_workflow is None:
        _review_workflow = ReviewWorkflow()
    return _review_workflow