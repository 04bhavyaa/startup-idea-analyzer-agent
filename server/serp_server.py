#!/usr/bin/env python3

import asyncio
import os
import logging
import json
from typing import Any, Dict, List
from serpapi import GoogleSearch
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool
import mcp.types as types
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

server = Server("serp-search")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    List available tools for web search functionality.
    """
    return [
        Tool(
            name="search",
            description="Search the web for information using Google Search API",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of search results to return (default: 10, max: 20)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "location": {
                        "type": "string",
                        "description": "Geographic location for search (optional)",
                        "default": "United States"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_news",
            description="Search for recent news articles on a specific topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "News search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of news results (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time period for news search",
                        "enum": ["hour", "day", "week", "month", "year"],
                        "default": "month"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handle tools calls for web search operation
    """
    try:
        if name == "search":
            return await handle_search(arguments)
        elif name == "search_news":
            return await handle_search_news(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"Error occurred while processing {name}: {str(e)}"})
        )]

async def handle_search(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Perform a web search using SERP API and return structured JSON.
    """
    try:
        query = arguments.get("query")
        num_results = arguments.get("num_results", 10)
        location = arguments.get("location", "United States")

        if not query:
            raise ValueError("Query parameter is required")

        api_key = os.getenv("SERP_API_KEY")
        if not api_key:
            raise ValueError("SERP_API_KEY environment variable is required")

        logger.info(f"Searching for: {query}")

        search = GoogleSearch({
            "q": query,
            "num": min(num_results, 20),
            "location": location,
            "api_key": api_key,
            "engine": "google"
        })

        results = search.get_dict()

        formatted_results = []
        organic_results = results.get("organic_results", [])

        for i, result in enumerate(organic_results[:num_results]):
            formatted_results.append({
                "position": i + 1,
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "displayed_link": result.get("displayed_link", "")
            })

        answer_box = results.get("answer_box")
        if answer_box:
            formatted_results.insert(0, {
                "type": "answer_box",
                "title": answer_box.get("title", ""),
                "link": answer_box.get("link", ""),
                "snippet": answer_box.get("snippet", "")
            })

        logger.info(f"Found {len(formatted_results)} results for: {query}")
        
        # Return results as a JSON string
        return [types.TextContent(type="text", text=json.dumps({"results": formatted_results}))]

    except Exception as e:
        logger.error(f"Error in web search: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"Error occurred while searching: {str(e)}"})
        )]

async def handle_search_news(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Perform a news search using SERP API and return structured JSON.
    """
    try:
        query = arguments.get("query")
        num_results = arguments.get("num_results", 5)
        time_period = arguments.get("time_period", "month")

        if not query:
            raise ValueError("Query parameter is required")

        api_key = os.getenv("SERP_API_KEY")
        if not api_key:
            raise ValueError("SERP_API_KEY environment variable is required")

        logger.info(f"Searching news for: {query}")

        search = GoogleSearch({
            "q": query,
            "tbm": "nws",
            "api_key": api_key,
            "num": min(num_results, 10),
            "tbs": f"qdr:{time_period[0]}",
            "engine": "google"
        })

        results = search.get_dict()
        news_results = results.get("news_results", [])

        formatted_results = []
        for i, article in enumerate(news_results[:num_results]):
            formatted_results.append({
                "position": i + 1,
                "title": article.get("title", ""),
                "link": article.get("link", ""),
                "snippet": article.get("snippet", ""),
                "date": article.get("date", ""),
                "source": article.get("source", "")
            })

        logger.info(f"Found {len(formatted_results)} news results for: {query}")

        return [types.TextContent(type="text", text=json.dumps({"news_results": formatted_results}))]

    except Exception as e:
        logger.error(f"Error in news search: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"Error occurred while searching news: {str(e)}"})
        )]

async def main():
    """
    Main function to run the SERP API search server.
    """
    try:
        from mcp.server.stdio import stdio_server

        logger.info("Starting SERP search server...")

        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="serp-server",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    except Exception as e:
        logger.error(f"Failed to start SERP server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
