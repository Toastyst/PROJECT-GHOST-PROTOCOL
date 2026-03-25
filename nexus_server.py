#!/usr/bin/env python3
"""
Nexus Server - Knowledge Discovery and Querying MCP Server

This server provides tools for ingesting codebase knowledge and performing
semantic searches across the knowledge base.

TODO: Implement advanced pattern recognition for code evolution
HACK: Temporary workaround for ChromaDB embedding limitations
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

from models import NexusData
from utils import GitUtils, CodeAnalyzer, LLMUtils
from config import Config


class KnowledgeBase:
    """Vector database wrapper for knowledge storage and retrieval."""

    def __init__(self, db_path: str = Config.CHROMA_DB_PATH):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="nexus_knowledge",
            metadata={"description": "Codebase knowledge and insights"}
        )
        self.llm = LLMUtils()

    def add_knowledge(self, data: NexusData) -> bool:
        """Add knowledge entry to the database."""
        try:
            # Generate embedding for the content
            embedding_text = f"{data.type}: {data.content}"
            # Note: In a real implementation, you'd generate embeddings here
            # For now, we'll use simple text storage

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

            self.collection.add(
                documents=[data.content],
                metadatas=[metadata],
                ids=[data.id]
            )
            return True
        except Exception as e:
            print(f"Error adding knowledge: {e}")
            return False

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
    import mcp.server.stdio
    await mcp.server.stdio.serve(server)


if __name__ == "__main__":
    asyncio.run(main())