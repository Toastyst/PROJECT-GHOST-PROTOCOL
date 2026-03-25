#!/usr/bin/env python3
"""
Nexus Server - Knowledge Discovery and Querying MCP Server

This server provides tools for ingesting codebase knowledge and performing
semantic searches across the knowledge base.
"""

import asyncio
import json
import os
from typing import Any, Dict, Sequence
from mcp import Tool
from mcp.server import Server
from mcp.types import TextContent, PromptMessage
import chromadb
from chromadb.config import Settings

from src.ghost_protocol.models.models import NexusData, EmotionalEntry, NoteFragment, TransmutationRecord
from src.ghost_protocol.utils.utils import GitUtils, CodeAnalyzer, LLMUtils
from src.ghost_protocol.utils.config import Config

# Cross-platform lock mechanism
def check_existing_instance(lock_file: str) -> bool:
    """Check if another instance is already running."""
    if not os.path.exists(lock_file):
        return False

    try:
        with open(lock_file, 'r') as f:
            pid_str = f.read().strip()
            pid = int(pid_str)

        # Check if process is still running (cross-platform)
        try:
            import psutil
            if psutil.pid_exists(pid):
                return True
        except ImportError:
            # psutil not available, use basic check
            try:
                os.kill(pid, 0)  # Signal 0 just checks if process exists
                return True
            except (OSError, ProcessLookupError):
                pass  # Process doesn't exist

    except (ValueError, IOError):
        pass  # Invalid lock file

    # Clean up stale lock file
    try:
        os.remove(lock_file)
    except OSError:
        pass

    return False


class KnowledgeBase:
    """Vector database wrapper for knowledge storage and retrieval."""

    def __init__(self, db_path: str = Config.CHROMA_DB_PATH):
        if Config.TEST_MODE and db_path == ":memory:":
            # Use in-memory client for tests
            self.client = chromadb.Client(Settings(anonymized_telemetry=False))
        else:
            # Use persistent client for production
            self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name="nexus_knowledge",
            metadata={"description": "Codebase knowledge and insights"}
        )
        self.llm = LLMUtils()

    def add_knowledge(self, data: NexusData) -> bool:
        """Add knowledge entry to the database with semantic embeddings."""
        try:
            # Generate rich embedding text that captures semantic meaning
            embedding_text = self._generate_embedding_text(data)

            metadata = {
                "id": data.id,
                "type": data.type,
                **data.metadata
            }

            # Add resonance score if present
            if data.resonance_score is not None:
                metadata["resonance_score"] = str(data.resonance_score)

            # Add relationships as comma-separated string
            if data.relationships:
                metadata["relationships"] = ",".join(data.relationships)

            # ChromaDB will automatically generate embeddings using sentence-transformers
            # The embedding_text provides rich semantic context for better similarity search
            self.collection.add(
                documents=[embedding_text],
                metadatas=[metadata],
                ids=[data.id]
            )
            return True
        except Exception as e:
            print(f"Error adding knowledge: {e}")
            return False

    def _generate_embedding_text(self, data: NexusData) -> str:
        """Generate rich embedding text that captures semantic meaning for better similarity search."""
        # Base content
        embedding_parts = [data.content]

        # Add type-specific semantic context
        if data.type == "commit_message":
            embedding_parts.append("git commit software development change")
            # Add emotional context if available
            emotional_categories = data.metadata.get('emotional_categories', '')
            if emotional_categories:
                embedding_parts.append(f"emotional context: {emotional_categories}")

        elif data.type == "function_definition":
            embedding_parts.append("programming function code definition")
            file_path = data.metadata.get('file_path', '')
            if file_path:
                embedding_parts.append(f"located in {file_path}")

        elif data.type == "class_definition":
            embedding_parts.append("programming class object oriented design")
            bases = data.metadata.get('bases', '')
            if bases:
                embedding_parts.append(f"inherits from {bases}")

        elif data.type == "technical_debt":
            embedding_parts.append("code quality issue maintenance problem")
            indicator = data.metadata.get('indicator', '')
            if indicator:
                embedding_parts.append(f"marked with {indicator}")

        elif data.type == "blame_annotation":
            embedding_parts.append("code ownership authorship contribution")
            author_count = data.metadata.get('author_count', '1')
            embedding_parts.append(f"contributed by {author_count} developers")

        elif data.type == "prime_directive":
            embedding_parts.append("coding standard unwritten rule best practice")
            frequency = data.metadata.get('frequency', '0')
            embedding_parts.append(f"observed {frequency} times")

        elif data.type.startswith("emotional_"):
            embedding_parts.append("developer emotion sentiment feeling")
            emotional_note = data.metadata.get('emotional_note', '')
            if emotional_note:
                embedding_parts.append(f"emotional context: {emotional_note}")

        elif data.type.startswith("autopoiesis_fragment"):
            embedding_parts.append("experience learning observation pattern")
            fragment_type = data.metadata.get('fragment_type', '')
            if fragment_type:
                embedding_parts.append(f"fragment type: {fragment_type}")

        # Add resonance score context
        if data.resonance_score is not None:
            if data.resonance_score > 7.0:
                embedding_parts.append("highly significant important critical")
            elif data.resonance_score > 4.0:
                embedding_parts.append("moderately important notable")
            else:
                embedding_parts.append("minor significance routine")

        # Add relationship context
        if data.relationships:
            embedding_parts.append(f"related to {len(data.relationships)} other items")

        # Combine all parts for rich semantic embedding
        return " | ".join(embedding_parts)

    def query_knowledge(self, query: str, filters: dict = None, limit: int = 10) -> list[NexusData]:
        """Query the knowledge base."""
        try:
            where_clause = None
            if filters:
                where_clause = filters

            results = self.collection.query(
                query_texts=[query],
                where=where_clause,
                n_results=limit
            )

            knowledge_results = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    knowledge_results.append(NexusData(
                        id=metadata.get('id', f"result_{i}"),
                        content=doc,
                        type=metadata.get('type', 'unknown'),
                        metadata={k: v for k, v in metadata.items() if k != 'id' and k != 'type'},
                        relationships=[]
                    ))

            return knowledge_results
        except Exception as e:
            print(f"Error querying knowledge: {e}")
            return []


# Global server instance
server = Server("nexus-server")
nexus_instance = None


def get_nexus() -> 'NexusServer':
    """Get or create Nexus server instance."""
    global nexus_instance
    if nexus_instance is None:
        nexus_instance = NexusServer()
    return nexus_instance


class NexusServer:
    """MCP Server for knowledge discovery and querying."""

    def __init__(self):
        self.knowledge_base = KnowledgeBase()

    async def ingest_codebase(self, repo_path: str) -> bool:
        """Ingest codebase knowledge from git repository with archeological depth."""
        try:
            # Get commit history with emotional analysis
            commits = GitUtils.get_commit_history(repo_path)

            for commit in commits:
                # Calculate resonance score for commit messages
                emotional_data = GitUtils.extract_emotional_keywords(commit['message'])
                resonance_score = emotional_data['resonance_score']

                knowledge = NexusData(
                    id=f"commit_{commit['hash']}",
                    content=commit['message'],
                    type="commit_message",
                    metadata={
                        "author": commit['author'],
                        "date": commit['date'],
                        "hash": commit['hash'],
                        "emotional_categories": ",".join(emotional_data['emotional_categories'])
                    },
                    relationships=[],
                    resonance_score=resonance_score
                )
                self.knowledge_base.add_knowledge(knowledge)

            # Get correction patterns (Prime Directives)
            correction_patterns = GitUtils.get_correction_patterns(repo_path)
            for pattern in correction_patterns:
                knowledge = NexusData(
                    id=f"pattern_{pattern['type']}",
                    content=pattern['description'],
                    type="prime_directive",
                    metadata={
                        "pattern_type": pattern['type'],
                        "frequency": str(pattern['frequency']),
                        "examples_count": str(len(pattern['examples']))
                    },
                    relationships=[],
                    resonance_score=7.0  # High resonance for unwritten rules
                )
                self.knowledge_base.add_knowledge(knowledge)

            # Get dead code comments
            dead_comments = GitUtils.find_dead_code_comments(repo_path)
            for comment in dead_comments:
                knowledge = NexusData(
                    id=f"debt_{comment['file_path']}_{comment['line']}",
                    content=f"{comment['indicator'].upper()}: {comment['content']}",
                    type="technical_debt",
                    metadata={
                        "file_path": comment['file_path'],
                        "line": str(comment['line']),
                        "indicator": comment['indicator'],
                        "context": comment['context'][:200]  # Limit context length
                    },
                    relationships=[],
                    resonance_score=6.0  # Medium-high resonance for technical debt
                )
                self.knowledge_base.add_knowledge(knowledge)

            # Get code structure with blame information
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)

                        # Get blame information for institutional knowledge
                        blame_info = GitUtils.get_blame_info(repo_path, file_path)
                        if blame_info:
                            # Calculate ownership risk score
                            primary_author = blame_info.get('primary_author')
                            author_count = len(blame_info.get('author_stats', {}))
                            ownership_risk = 3.0 if author_count <= 2 else 0.0  # High risk if few authors

                            knowledge = NexusData(
                                id=f"blame_{file_path}",
                                content=f"File owned primarily by {primary_author} with {author_count} contributors",
                                type="blame_annotation",
                                metadata={
                                    "file_path": file_path,
                                    "primary_author": primary_author or "unknown",
                                    "author_count": str(author_count),
                                    "total_lines": str(blame_info.get('total_lines', 0))
                                },
                                relationships=[],
                                resonance_score=ownership_risk
                            )
                            self.knowledge_base.add_knowledge(knowledge)

                        # Extract functions
                        functions = CodeAnalyzer.extract_functions_from_file(file_path)
                        for func in functions:
                            knowledge = NexusData(
                                id=f"func_{file_path}_{func['name']}",
                                content=f"Function: {func['name']} - {func['docstring']}",
                                type="function_definition",
                                metadata={
                                    "file_path": file_path,
                                    "line": str(func['line']),
                                    "args": ",".join(func['args'])
                                },
                                relationships=[f"blame_{file_path}"] if blame_info else []
                            )
                            self.knowledge_base.add_knowledge(knowledge)

                        # Extract classes
                        classes = CodeAnalyzer.extract_classes_from_file(file_path)
                        for cls in classes:
                            knowledge = NexusData(
                                id=f"class_{file_path}_{cls['name']}",
                                content=f"Class: {cls['name']} - {cls['docstring']}",
                                type="class_definition",
                                metadata={
                                    "file_path": file_path,
                                    "line": str(cls['line']),
                                    "bases": ",".join(cls['bases'])
                                },
                                relationships=[f"blame_{file_path}"] if blame_info else []
                            )
                            self.knowledge_base.add_knowledge(knowledge)

            return True
        except Exception as e:
            print(f"Error ingesting codebase: {e}")
            return False

    async def query_nexus(self, query: str, filters: dict = None) -> list[NexusData]:
        """Query the knowledge base with constellation mapping and resonance scoring."""
        return self.knowledge_base.query_knowledge(query, filters)

    async def query_nexus_constellation(self, query: str) -> Dict[str, Any]:
        """Query with full constellation map - returns emotional, historical context."""
        try:
            # Get base results
            results = self.knowledge_base.query_knowledge(query, limit=20)

            # Build constellation map
            constellation = {
                "query": query,
                "canonical_location": None,
                "red_flags": [],
                "emotional_charge": "neutral",
                "runbook_suggestions": [],
                "resonance_summary": {
                    "high_risk_items": [],
                    "institutional_knowledge_gaps": [],
                    "technical_debt_hotspots": []
                },
                "related_insights": []
            }

            # Analyze results for constellation mapping
            high_resonance_items = []
            technical_debt_items = []
            blame_items = []

            for result in results:
                resonance_score = float(result.metadata.get('resonance_score', '0'))

                if result.type == 'function_definition' or result.type == 'class_definition':
                    if constellation["canonical_location"] is None:
                        constellation["canonical_location"] = result.metadata.get('file_path')

                elif result.type == 'prime_directive':
                    constellation["red_flags"].append({
                        "type": "unwritten_rule",
                        "description": result.content,
                        "severity": "high"
                    })

                elif result.type == 'technical_debt':
                    technical_debt_items.append(result)
                    constellation["red_flags"].append({
                        "type": "technical_debt",
                        "description": result.content,
                        "location": f"{result.metadata.get('file_path')}:{result.metadata.get('line')}",
                        "severity": "medium"
                    })

                elif result.type == 'blame_annotation':
                    blame_items.append(result)
                    author_count = int(result.metadata.get('author_count', '0'))
                    if author_count <= 2:
                        constellation["resonance_summary"]["institutional_knowledge_gaps"].append({
                            "file": result.metadata.get('file_path'),
                            "primary_author": result.metadata.get('primary_author'),
                            "risk": "single_point_of_failure"
                        })

                elif result.type == 'commit_message':
                    emotional_categories = result.metadata.get('emotional_categories', '').split(',')
                    if any(cat in ['frustration', 'complexity', 'technical_debt'] for cat in emotional_categories):
                        high_resonance_items.append(result)

                # Collect related insights
                if resonance_score > 5.0:
                    constellation["related_insights"].append({
                        "type": result.type,
                        "content": result.content[:150],
                        "resonance": resonance_score,
                        "metadata": result.metadata
                    })

            # Determine emotional charge
            total_high_resonance = len(high_resonance_items) + len(technical_debt_items)
            if total_high_resonance > 5:
                constellation["emotional_charge"] = "high_tension"
            elif total_high_resonance > 2:
                constellation["emotional_charge"] = "caution_advised"
            else:
                constellation["emotional_charge"] = "stable"

            # Generate runbook suggestions
            if constellation["red_flags"]:
                constellation["runbook_suggestions"].append("Review flagged areas with senior engineer before changes")

            if constellation["resonance_summary"]["institutional_knowledge_gaps"]:
                constellation["runbook_suggestions"].append("Document knowledge transfer plan for single-author files")

            if technical_debt_items:
                constellation["runbook_suggestions"].append("Schedule technical debt cleanup session")

            return constellation

        except Exception as e:
            print(f"Error in constellation query: {e}")
            return {
                "query": query,
                "error": str(e),
                "canonical_location": None,
                "red_flags": [],
                "emotional_charge": "error",
                "runbook_suggestions": ["Investigate system error"],
                "resonance_summary": {"high_risk_items": [], "institutional_knowledge_gaps": [], "technical_debt_hotspots": []},
                "related_insights": []
            }

    async def store_emotional_entry(self, emotional_entry: EmotionalEntry) -> bool:
        """Store an emotional entry in the knowledge base."""
        try:
            # Convert EmotionalEntry to NexusData for storage
            nexus_data = NexusData(
                id=emotional_entry.id,
                content=emotional_entry.content,
                type=emotional_entry.type,
                metadata={
                    **emotional_entry.metadata,
                    "emotional_note": emotional_entry.emotional_note,
                    "intent_payload": json.dumps(emotional_entry.intent_payload),
                    "sacred_moments": json.dumps(emotional_entry.sacred_moments)
                },
                relationships=emotional_entry.relationships,
                resonance_score=emotional_entry.resonance_score
            )

            return self.knowledge_base.add_knowledge(nexus_data)
        except Exception as e:
            print(f"Error storing emotional entry: {e}")
            return False

    async def get_emotional_stats(self) -> Dict[str, Any]:
        """Get statistics about emotional entries."""
        try:
            # Query all emotional entries
            results = self.knowledge_base.collection.get(
                where={"type": {"$in": ["emotional_commit", "emotional_pr_comment", "emotional_unknown"]}}
            )

            if not results['metadatas']:
                return {
                    "total_entries": 0,
                    "avg_resonance": 0.0,
                    "sacred_moments": 0,
                    "emotion_types": 0
                }

            total_entries = len(results['metadatas'])
            resonance_scores = []
            sacred_moments = 0
            emotion_types = set()

            for metadata in results['metadatas']:
                # Parse resonance score
                resonance_str = metadata.get('resonance_score', '0')
                try:
                    resonance_scores.append(float(resonance_str))
                except ValueError:
                    resonance_scores.append(0.0)

                # Count sacred moments
                sacred_str = metadata.get('sacred_moments', '[]')
                try:
                    sacred_list = json.loads(sacred_str)
                    sacred_moments += len(sacred_list)
                except (json.JSONDecodeError, TypeError):
                    pass

                # Track emotion types from emotional_note
                emotional_note = metadata.get('emotional_note', '')
                if emotional_note:
                    # Extract emotion types from notes
                    if 'frustration' in emotional_note.lower():
                        emotion_types.add('frustration')
                    if 'exhaustion' in emotional_note.lower():
                        emotion_types.add('exhaustion')
                    if 'relief' in emotional_note.lower():
                        emotion_types.add('relief')
                    if 'pride' in emotional_note.lower():
                        emotion_types.add('pride')

            avg_resonance = sum(resonance_scores) / len(resonance_scores) if resonance_scores else 0.0

            return {
                "total_entries": total_entries,
                "avg_resonance": avg_resonance,
                "sacred_moments": sacred_moments,
                "emotion_types": len(emotion_types)
            }

        except Exception as e:
            print(f"Error getting emotional stats: {e}")
            return {
                "total_entries": 0,
                "avg_resonance": 0.0,
                "sacred_moments": 0,
                "emotion_types": 0
            }

    async def query_emotional_resonance(self, query: str, min_resonance: float = 5.0) -> list[EmotionalEntry]:
        """Query emotional entries by content and minimum resonance score."""
        try:
            # Query the knowledge base with filters
            filters = {
                "resonance_score": {"$gte": str(min_resonance)},
                "type": {"$in": ["emotional_commit", "emotional_pr_comment", "emotional_unknown"]}
            }

            results = self.knowledge_base.collection.query(
                query_texts=[query],
                where=filters,
                n_results=20
            )

            emotional_results = []
            if results['documents'] and results['metadatas']:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]

                    # Reconstruct EmotionalEntry from metadata
                    emotional_entry = EmotionalEntry(
                        id=metadata.get('id', f"result_{i}"),
                        content=doc,
                        type=metadata.get('type', 'unknown').replace('emotional_', ''),
                        metadata={k: v for k, v in metadata.items()
                                if k not in ['id', 'type', 'emotional_note', 'intent_payload', 'sacred_moments']},
                        relationships=metadata.get('relationships', '').split(',') if metadata.get('relationships') else [],
                        resonance_score=float(metadata.get('resonance_score', '0')),
                        emotional_note=metadata.get('emotional_note', ''),
                        intent_payload=json.loads(metadata.get('intent_payload', '{}')),
                        sacred_moments=json.loads(metadata.get('sacred_moments', '[]'))
                    )
                    emotional_results.append(emotional_entry)

            return emotional_results

        except Exception as e:
            print(f"Error querying emotional resonance: {e}")
            return []

    async def log_iteration_event(self, event: 'IterationEvent') -> bool:
        """Log an iteration protocol event for analysis and learning."""
        try:
            # Convert event to knowledge entry
            event_data = NexusData(
                id=f"iteration_event_{event.event_type}_{event.timestamp}",
                content=f"{event.event_type}: {json.dumps(event.context)}",
                type="iteration_event",
                metadata={
                    "event_type": event.event_type,
                    "participants": ",".join(event.participants),
                    "timestamp": event.timestamp,
                    "outcome": event.outcome or "unknown"
                },
                relationships=[],
                resonance_score=4.0  # Medium resonance for protocol events
            )

            return self.knowledge_base.add_knowledge(event_data)
        except Exception as e:
            print(f"Error logging iteration event: {e}")
            return False

    async def store_workflow_memory(self, workflow_id: str, memory_data: Dict[str, Any]) -> bool:
        """Store workflow execution memory for future reference."""
        try:
            # Store workflow completion data
            memory_entry = NexusData(
                id=f"workflow_memory_{workflow_id}",
                content=f"Workflow {workflow_id} memory: {json.dumps(memory_data)}",
                type="workflow_memory",
                metadata={
                    "workflow_id": workflow_id,
                    "completion_time": memory_data.get("completed_at", ""),
                    "outcome": memory_data.get("outcome", "unknown"),
                    "lessons_learned": json.dumps(memory_data.get("lessons_learned", [])),
                    "successes": json.dumps(memory_data.get("successes", [])),
                    "failures": json.dumps(memory_data.get("failures", []))
                },
                relationships=[],
                resonance_score=6.0  # High resonance for workflow learnings
            )

            return self.knowledge_base.add_knowledge(memory_entry)
        except Exception as e:
            print(f"Error storing workflow memory: {e}")
            return False

    async def query_iteration_events(self, event_type: str = None, limit: int = 20) -> list[Dict[str, Any]]:
        """Query iteration events for pattern analysis."""
        try:
            # ChromaDB doesn't support multiple conditions in where clause
            # So we query for all iteration events and filter afterwards
            results = self.knowledge_base.collection.query(
                query_texts=["iteration protocol events"],
                where={"type": "iteration_event"},
                n_results=limit * 2  # Get more to filter
            )

            events = []
            if results['metadatas']:
                for metadata in results['metadatas'][0]:
                    # Filter by event_type if specified
                    if event_type and metadata.get("event_type") != event_type:
                        continue

                    events.append({
                        "event_type": metadata.get("event_type"),
                        "participants": metadata.get("participants", "").split(","),
                        "timestamp": metadata.get("timestamp"),
                        "outcome": metadata.get("outcome"),
                        "context": json.loads(metadata.get("context", "{}"))
                    })

                    if len(events) >= limit:
                        break

            return events
        except Exception as e:
            print(f"Error querying iteration events: {e}")
            return []

    async def get_workflow_insights(self, workflow_type: str = None) -> Dict[str, Any]:
        """Get insights from workflow memories."""
        try:
            filters = {"type": "workflow_memory"}
            if workflow_type:
                # This would need more sophisticated filtering in a real implementation
                pass

            results = self.knowledge_base.collection.query(
                query_texts=["workflow execution memories"],
                where=filters,
                n_results=50
            )

            insights = {
                "total_workflows": 0,
                "success_rate": 0.0,
                "common_successes": [],
                "common_failures": [],
                "lessons_learned": []
            }

            if results['metadatas']:
                total_workflows = len(results['metadatas'][0])
                insights["total_workflows"] = total_workflows

                successful_workflows = 0
                all_successes = []
                all_failures = []
                all_lessons = []

                for metadata in results['metadatas'][0]:
                    outcome = metadata.get("outcome", "")
                    if outcome == "success":
                        successful_workflows += 1

                    # Aggregate successes, failures, lessons
                    successes = json.loads(metadata.get("successes", "[]"))
                    failures = json.loads(metadata.get("failures", "[]"))
                    lessons = json.loads(metadata.get("lessons_learned", "[]"))

                    all_successes.extend(successes)
                    all_failures.extend(failures)
                    all_lessons.extend(lessons)

                insights["success_rate"] = successful_workflows / total_workflows if total_workflows > 0 else 0.0

                # Find most common items (simplified)
                from collections import Counter
                insights["common_successes"] = [item for item, _ in Counter(all_successes).most_common(3)]
                insights["common_failures"] = [item for item, _ in Counter(all_failures).most_common(3)]
                insights["lessons_learned"] = [item for item, _ in Counter(all_lessons).most_common(5)]

            return insights
        except Exception as e:
            print(f"Error getting workflow insights: {e}")
            return {
                "total_workflows": 0,
                "success_rate": 0.0,
                "common_successes": [],
                "common_failures": [],
                "lessons_learned": []
            }

    async def note_fragment_ingestion(self, fragments: list[NoteFragment]) -> bool:
        """Ingest note fragments from autopoiesis observation into the knowledge base."""
        try:
            for fragment in fragments:
                # Convert NoteFragment to NexusData for storage
                fragment_data = NexusData(
                    id=f"fragment_{fragment.timestamp}_{fragment.type}",
                    content=fragment.content,
                    type=f"autopoiesis_fragment_{fragment.type}",
                    metadata={
                        "fragment_type": fragment.type,
                        "timestamp": fragment.timestamp,
                        "emotional_weight": str(fragment.emotional_weight),
                        "threshold": fragment.threshold,
                        "context": json.dumps(fragment.context)
                    },
                    relationships=[],
                    resonance_score=fragment.emotional_weight * 2  # Scale emotional weight to resonance
                )

                success = self.knowledge_base.add_knowledge(fragment_data)
                if not success:
                    print(f"Failed to store fragment: {fragment.timestamp}")
                    return False

            return True
        except Exception as e:
            print(f"Error ingesting note fragments: {e}")
            return False

    async def transmutation_memory_storage(self, record: TransmutationRecord) -> bool:
        """Store transmutation record and generated structures in the knowledge base."""
        try:
            # Store the transmutation record itself
            record_data = NexusData(
                id=f"transmutation_{record.timestamp}",
                content=f"Transmutation processed {record.fragments_processed} fragments",
                type="autopoiesis_transmutation",
                metadata={
                    "timestamp": record.timestamp,
                    "fragments_processed": str(record.fragments_processed),
                    "review_status": record.review_status,
                    "generated_hook": record.generated_hook or "",
                    "generated_workflow": record.generated_workflow or "",
                    "generated_skill": record.generated_skill or "",
                    "rule_update": record.rule_update or ""
                },
                relationships=[],
                resonance_score=8.0  # High resonance for transmutation events
            )

            success = self.knowledge_base.add_knowledge(record_data)
            if not success:
                return False

            # Store generated structures as separate knowledge entries
            generated_items = []

            if record.generated_hook:
                hook_data = NexusData(
                    id=f"generated_hook_{record.timestamp}",
                    content=record.generated_hook,
                    type="autopoiesis_generated_hook",
                    metadata={
                        "generation_timestamp": record.timestamp,
                        "transmutation_id": f"transmutation_{record.timestamp}",
                        "structure_type": "hook"
                    },
                    relationships=[f"transmutation_{record.timestamp}"],
                    resonance_score=7.0
                )
                generated_items.append(hook_data)

            if record.generated_workflow:
                workflow_data = NexusData(
                    id=f"generated_workflow_{record.timestamp}",
                    content=record.generated_workflow,
                    type="autopoiesis_generated_workflow",
                    metadata={
                        "generation_timestamp": record.timestamp,
                        "transmutation_id": f"transmutation_{record.timestamp}",
                        "structure_type": "workflow"
                    },
                    relationships=[f"transmutation_{record.timestamp}"],
                    resonance_score=7.0
                )
                generated_items.append(workflow_data)

            if record.generated_skill:
                skill_data = NexusData(
                    id=f"generated_skill_{record.timestamp}",
                    content=record.generated_skill,
                    type="autopoiesis_generated_skill",
                    metadata={
                        "generation_timestamp": record.timestamp,
                        "transmutation_id": f"transmutation_{record.timestamp}",
                        "structure_type": "skill"
                    },
                    relationships=[f"transmutation_{record.timestamp}"],
                    resonance_score=7.0
                )
                generated_items.append(skill_data)

            if record.rule_update:
                rule_data = NexusData(
                    id=f"generated_rule_{record.timestamp}",
                    content=record.rule_update,
                    type="autopoiesis_generated_rule",
                    metadata={
                        "generation_timestamp": record.timestamp,
                        "transmutation_id": f"transmutation_{record.timestamp}",
                        "structure_type": "rule"
                    },
                    relationships=[f"transmutation_{record.timestamp}"],
                    resonance_score=7.0
                )
                generated_items.append(rule_data)

            # Store all generated items
            for item in generated_items:
                success = self.knowledge_base.add_knowledge(item)
                if not success:
                    print(f"Failed to store generated item: {item.id}")
                    return False

            return True
        except Exception as e:
            print(f"Error storing transmutation memory: {e}")
            return False

    async def query_autopoiesis_fragments(self, fragment_type: str = None, limit: int = 20) -> list[NoteFragment]:
        """Query stored autopoiesis fragments."""
        try:
            filters = {"type": {"$regex": "^autopoiesis_fragment"}}
            if fragment_type:
                filters["fragment_type"] = fragment_type

            results = self.knowledge_base.collection.query(
                query_texts=["autopoiesis fragments"],
                where=filters,
                n_results=limit
            )

            fragments = []
            if results['metadatas']:
                for metadata in results['metadatas'][0]:
                    # Reconstruct NoteFragment from metadata
                    fragment = NoteFragment(
                        timestamp=metadata.get('timestamp', ''),
                        type=metadata.get('fragment_type', 'unknown'),
                        content=results['documents'][0][len(fragments)] if results['documents'] else '',
                        context=json.loads(metadata.get('context', '{}')),
                        emotional_weight=float(metadata.get('emotional_weight', '0')),
                        threshold=metadata.get('threshold', 'unknown')
                    )
                    fragments.append(fragment)

            return fragments
        except Exception as e:
            print(f"Error querying autopoiesis fragments: {e}")
            return []

    async def get_transmutation_history(self, limit: int = 10) -> list[TransmutationRecord]:
        """Get transmutation history from the knowledge base."""
        try:
            results = self.knowledge_base.collection.query(
                query_texts=["autopoiesis transmutation records"],
                where={"type": "autopoiesis_transmutation"},
                n_results=limit
            )

            records = []
            if results['metadatas']:
                for metadata in results['metadatas'][0]:
                    # Reconstruct TransmutationRecord from metadata
                    record = TransmutationRecord(
                        timestamp=metadata.get('timestamp', ''),
                        fragments_processed=int(metadata.get('fragments_processed', '0')),
                        generated_hook=metadata.get('generated_hook') or None,
                        generated_workflow=metadata.get('generated_workflow') or None,
                        generated_skill=metadata.get('generated_skill') or None,
                        rule_update=metadata.get('rule_update') or None,
                        review_status=metadata.get('review_status', 'unknown')
                    )
                    records.append(record)

            return records
        except Exception as e:
            print(f"Error getting transmutation history: {e}")
            return []


# MCP Tool definitions
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="ingest_codebase",
            description="Ingest knowledge from a git repository into the Nexus knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the git repository to ingest"
                    }
                },
                "required": ["repo_path"]
            }
        ),
        Tool(
            name="query_nexus",
            description="Query the Nexus knowledge base for relevant information",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for knowledge retrieval"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional filters for the query (e.g., {'type': 'commit_message'})"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="query_constellation",
            description="Query with full constellation map - returns emotional, historical context and risk assessment",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for constellation mapping"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    nexus = get_nexus()

    if name == "ingest_codebase":
        repo_path = arguments["repo_path"]
        success = await nexus.ingest_codebase(repo_path)
        return [TextContent(
            type="text",
            text=f"Codebase ingestion {'successful' if success else 'failed'} for {repo_path}"
        )]

    elif name == "query_nexus":
        query = arguments["query"]
        filters = arguments.get("filters")
        results = await nexus.query_nexus(query, filters)

        response = f"Found {len(results)} knowledge entries:\n\n"
        for result in results:
            response += f"- {result.type}: {result.content[:100]}...\n"

        return [TextContent(type="text", text=response)]

    elif name == "query_constellation":
        query = arguments["query"]
        constellation = await nexus.query_nexus_constellation(query)

        response = f"Constellation Map for: '{query}'\n\n"
        response += f"Canonical Location: {constellation['canonical_location'] or 'Not found'}\n"
        response += f"Emotional Charge: {constellation['emotional_charge']}\n\n"

        if constellation['red_flags']:
            response += "🚩 RED FLAGS:\n"
            for flag in constellation['red_flags']:
                response += f"- {flag['type'].upper()}: {flag['description']}\n"
                if 'location' in flag:
                    response += f"  Location: {flag['location']}\n"
            response += "\n"

        if constellation['resonance_summary']['institutional_knowledge_gaps']:
            response += "🧠 INSTITUTIONAL KNOWLEDGE GAPS:\n"
            for gap in constellation['resonance_summary']['institutional_knowledge_gaps']:
                response += f"- {gap['file']}: {gap['primary_author']} ({gap['risk']})\n"
            response += "\n"

        if constellation['runbook_suggestions']:
            response += "📋 RUNBOOK SUGGESTIONS:\n"
            for suggestion in constellation['runbook_suggestions']:
                response += f"- {suggestion}\n"
            response += "\n"

        if constellation['related_insights']:
            response += "💡 HIGH-RESONANCE INSIGHTS:\n"
            for insight in constellation['related_insights'][:5]:  # Limit to top 5
                response += f"- {insight['type']}: {insight['content']} (resonance: {insight['resonance']})\n"

        return [TextContent(type="text", text=response)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main server entry point."""
    # Prevent multiple instances in production
    if not Config.TEST_MODE:
        lock_file = ".ghost_nexus.lock"
        if check_existing_instance(lock_file):
            print("Another Nexus server instance is already running. Exiting.")
            return

        # Write our PID to the lock file
        try:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            print("Nexus server lock acquired - starting...")
        except IOError:
            print("Failed to create lock file. Exiting.")
            return

    import mcp.server.stdio
    await mcp.server.stdio.serve(server)


if __name__ == "__main__":
    asyncio.run(main())