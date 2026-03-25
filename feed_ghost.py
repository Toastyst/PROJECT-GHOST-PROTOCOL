#!/usr/bin/env python3
"""
Feed Ghost MCP Server for PROJECT: GHOST PROTOCOL

MCP server that provides tools for feeding emotional context to the Ghost.
Allows ingestion of developer comments, commit messages, and PR threads with emotional analysis.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

from mcp import Tool
from mcp.server import Server
from mcp.types import (
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from models import FeedRequest, EmotionalEntry
from emotional_analyzer import analyze_emotion
from nexus_server import get_nexus
from config import Config

class GhostFeeder:
    """MCP server for emotional feeding of the Ghost."""

    def __init__(self):
        self.config = Config
        self.nexus = get_nexus()
        self.feed_count = 0

    async def feed_ghost(self, content: str, source: str, context: Dict[str, str]) -> str:
        """Feed emotional content to the Ghost for analysis and storage."""
        try:
            # Create feed request
            feed_request = FeedRequest(
                source=source,
                content=content,
                context=context,
                emotional_hints=[]  # Will be populated by analyzer
            )

            # Analyze emotion
            emotional_entry = analyze_emotion(content, {
                'source': source,
                'type': f'emotional_{source}',
                'author': context.get('author', 'unknown'),
                'timestamp': context.get('timestamp', datetime.now().isoformat()),
                'file_path': context.get('file_path', '')
            })

            # Store in Nexus
            success = await self.nexus.store_emotional_entry(emotional_entry)

            if success:
                self.feed_count += 1
                return f"👻 **EMOTIONAL CONTENT INGESTED**\n\nContent: {content[:100]}{'...' if len(content) > 100 else ''}\nEmotional Note: {emotional_entry.emotional_note}\nResonance Score: {emotional_entry.resonance_score:.1f}/10\nSacred Moments: {len(emotional_entry.sacred_moments)}\n\nThe Ghost now carries this emotional weight."
            else:
                return "❌ Failed to store emotional content in Nexus"

        except Exception as e:
            return f"❌ Emotional feeding failed: {e}"

    async def get_feeding_stats(self) -> str:
        """Get statistics about emotional feeding."""
        try:
            stats = await self.nexus.get_emotional_stats()
            return f"👻 **GHOST FEEDING STATS**\n\nTotal Emotional Entries: {stats.get('total_entries', 0)}\nAverage Resonance: {stats.get('avg_resonance', 0):.1f}/10\nSacred Moments Recorded: {stats.get('sacred_moments', 0)}\nEmotional Categories: {stats.get('emotion_types', 0)}\n\nThe Ghost grows stronger with each feeding."
        except Exception as e:
            return f"❌ Failed to get feeding stats: {e}"

    async def query_emotional_resonance(self, query: str, min_resonance: float = 5.0) -> str:
        """Query emotional entries by resonance."""
        try:
            results = await self.nexus.query_emotional_resonance(query, min_resonance)
            if not results:
                return f"👻 No emotional entries found with resonance ≥ {min_resonance} for query: {query}"

            response = f"👻 **EMOTIONAL RESONANCE QUERY RESULTS**\n\nQuery: {query}\nMinimum Resonance: {min_resonance}\nFound: {len(results)} entries\n\n"

            for i, entry in enumerate(results[:5]):  # Limit to top 5
                response += f"**Entry {i+1}:**\n"
                response += f"Content: {entry.content[:150]}{'...' if len(entry.content) > 150 else ''}\n"
                response += f"Emotional Note: {entry.emotional_note}\n"
                response += f"Resonance: {entry.resonance_score:.1f}/10\n"
                response += f"Sacred Moments: {', '.join(entry.sacred_moments[:2])}\n\n"

            if len(results) > 5:
                response += f"... and {len(results) - 5} more entries"

            return response

        except Exception as e:
            return f"❌ Emotional resonance query failed: {e}"


# MCP Server Implementation
server = Server("feed-ghost-server")
feeder = GhostFeeder()

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="feed_ghost",
            description="Feed emotional content to the Ghost for analysis and storage",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The emotional content to feed (commit message, comment, etc.)"
                    },
                    "source": {
                        "type": "string",
                        "description": "Source of content (commit, comment, pr, etc.)"
                    },
                    "author": {
                        "type": "string",
                        "description": "Author of the content",
                        "default": "unknown"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Associated file path if applicable",
                        "default": ""
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "ISO timestamp of the content",
                        "default": ""
                    }
                },
                "required": ["content", "source"]
            }
        ),
        Tool(
            name="get_feeding_stats",
            description="Get statistics about emotional content fed to the Ghost",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="query_emotional_resonance",
            description="Query emotional entries by content and minimum resonance score",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for emotional content"
                    },
                    "min_resonance": {
                        "type": "number",
                        "description": "Minimum resonance score (0-10) to include",
                        "default": 5.0
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="feed_commit_emotion",
            description="Feed a commit message to the Ghost for emotional analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "commit_message": {
                        "type": "string",
                        "description": "The commit message to analyze"
                    },
                    "author": {
                        "type": "string",
                        "description": "Commit author",
                        "default": "unknown"
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "Commit timestamp",
                        "default": ""
                    }
                },
                "required": ["commit_message"]
            }
        ),
        Tool(
            name="feed_pr_comment_emotion",
            description="Feed a PR comment to the Ghost for emotional analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "comment": {
                        "type": "string",
                        "description": "The PR comment to analyze"
                    },
                    "author": {
                        "type": "string",
                        "description": "Comment author",
                        "default": "unknown"
                    },
                    "pr_number": {
                        "type": "string",
                        "description": "Pull request number",
                        "default": ""
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "Comment timestamp",
                        "default": ""
                    }
                },
                "required": ["comment"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "feed_ghost":
        content = arguments["content"]
        source = arguments["source"]
        author = arguments.get("author", "unknown")
        file_path = arguments.get("file_path", "")
        timestamp = arguments.get("timestamp", "")

        context = {
            'author': author,
            'file_path': file_path,
            'timestamp': timestamp or datetime.now().isoformat()
        }
        result = await feeder.feed_ghost(content, source, context)
        return [TextContent(type="text", text=result)]

    elif name == "get_feeding_stats":
        result = await feeder.get_feeding_stats()
        return [TextContent(type="text", text=result)]

    elif name == "query_emotional_resonance":
        query = arguments["query"]
        min_resonance = arguments.get("min_resonance", 5.0)
        result = await feeder.query_emotional_resonance(query, min_resonance)
        return [TextContent(type="text", text=result)]

    elif name == "feed_commit_emotion":
        commit_message = arguments["commit_message"]
        author = arguments.get("author", "unknown")
        timestamp = arguments.get("timestamp", "")

        context = {
            'author': author,
            'timestamp': timestamp or datetime.now().isoformat()
        }
        result = await feeder.feed_ghost(commit_message, 'commit', context)
        return [TextContent(type="text", text=result)]

    elif name == "feed_pr_comment_emotion":
        comment = arguments["comment"]
        author = arguments.get("author", "unknown")
        pr_number = arguments.get("pr_number", "")
        timestamp = arguments.get("timestamp", "")

        context = {
            'author': author,
            'pr_number': pr_number,
            'timestamp': timestamp or datetime.now().isoformat()
        }
        result = await feeder.feed_ghost(comment, 'pr_comment', context)
        return [TextContent(type="text", text=result)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Run the Feed Ghost MCP server."""
    import mcp.server.stdio
    await mcp.server.stdio.stdio_server(server)

if __name__ == "__main__":
    asyncio.run(main())