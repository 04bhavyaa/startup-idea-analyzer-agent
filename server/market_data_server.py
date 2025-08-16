#!/usr/bin/env python3

import asyncio
import os
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent
import mcp.types as types
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

server = Server("market-data")

class PolygonAPI:
    """Wrapper for Polygon.io API calls"""
    
    def __init__(self):
        self.api_key = os.getenv("POLYGON_API_KEY")
        if not self.api_key:
            logger.warning("POLYGON_API_KEY not found - market data features will be limited")
        self.base_url = "https://api.polygon.io"
    
    def _make_request(self, url: str, params: Dict) -> Optional[Dict]:
        """Make a request to Polygon API with error handling"""
        if not self.api_key:
            return None
            
        try:
            params["apikey"] = self.api_key
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Polygon API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Polygon API response: {e}")
            return None
    
    def get_stock_financials(self, ticker: str) -> Optional[Dict]:
        """Get financial data for a stock ticker"""
        url = f"{self.base_url}/vX/reference/financials"
        params = {
            "ticker": ticker,
            "limit": 4  # Get last 4 quarters
        }
        return self._make_request(url, params)
    
    def get_market_data(self, ticker: str, days: int = 365) -> Optional[Dict]:
        """Get market data for a ticker"""
        # Get current date and date from X days ago
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
        params = {}
        
        return self._make_request(url, params)
    
    def get_ticker_details(self, ticker: str) -> Optional[Dict]:
        """Get company details for a ticker"""
        url = f"{self.base_url}/v3/reference/tickers/{ticker}"
        params = {}
        
        return self._make_request(url, params)
    
    def search_tickers(self, query: str, limit: int = 10) -> Optional[Dict]:
        """Search for tickers by company name"""
        url = f"{self.base_url}/v3/reference/tickers"
        params = {
            "search": query,
            "market": "stocks",
            "active": "true",
            "limit": limit
        }
        
        return self._make_request(url, params)


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    List available tools for market data functionality.
    """
    return [
        Tool(
            name="get_market_size",
            description="Get market size information for a specific industry or sector",
            inputSchema={
                "type": "object",
                "properties": {
                    "industry": {
                        "type": "string",
                        "description": "Industry or market sector name"
                    },
                    "region": {
                        "type": "string",
                        "description": "Geographic region (default: Global)",
                        "default": "Global"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Year for market data (default: current year)",
                        "minimum": 2020,
                        "maximum": 2030
                    }
                },
                "required": ["industry"]
            }
        ),
        Tool(
            name="get_growth_trends",
            description="Get market growth trends and projections",
            inputSchema={
                "type": "object",
                "properties": {
                    "industry": {
                        "type": "string",
                        "description": "Industry or market sector name"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Timeframe for growth analysis",
                        "enum": ["1-year", "3-year", "5-year", "10-year"],
                        "default": "5-year"
                    }
                },
                "required": ["industry"]
            }
        ),
        Tool(
            name="get_competitor_financials",
            description="Get financial information about public companies in a sector",
            inputSchema={
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "Name of the public company"
                    },
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (optional)"
                    },
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["revenue", "growth_rate", "market_cap", "valuation", "funding"]
                        },
                        "description": "Financial metrics to retrieve",
                        "default": ["revenue", "growth_rate", "market_cap"]
                    }
                },
                "required": ["company_name"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handle tool calls for market data operations.
    """
    try:
        if name == "get_market_size":
            return await handle_market_size(arguments)
        elif name == "get_growth_trends":
            return await handle_growth_trends(arguments)
        elif name == "get_competitor_financials":
            return await handle_competitor_financials(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error occurred while processing {name}: {str(e)}"
        )]


async def handle_market_size(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Get market size information by analyzing relevant public companies.
    """
    try:
        industry = arguments.get("industry", "")
        region = arguments.get("region", "Global")
        year = arguments.get("year", 2024)
        
        if not industry:
            return [types.TextContent(
                type="text",
                text="Industry parameter is required"
            )]
        
        logger.info(f"Analyzing market size for: {industry}")
        
        polygon = PolygonAPI()
        
        # Search for relevant companies in the industry
        search_results = polygon.search_tickers(industry, limit=10)
        
        if not search_results or not search_results.get("results"):
            return [types.TextContent(
                type="text",
                text=f"No public companies found for industry: {industry}. Market data may be limited for this sector."
            )]
        
        market_analysis = f"Market Size Analysis for {industry} ({region}, {year}):\n\n"
        total_market_cap = 0
        companies_analyzed = 0
        
        for ticker_info in search_results["results"][:5]:  # Analyze top 5 companies
            ticker = ticker_info.get("ticker")
            name = ticker_info.get("name", "Unknown")
            
            # Get company details
            details = polygon.get_ticker_details(ticker)
            if details and details.get("results"):
                company_data = details["results"]
                market_cap = company_data.get("market_cap")
                
                if market_cap:
                    total_market_cap += market_cap
                    companies_analyzed += 1
                    
                    market_analysis += f"\n{name} ({ticker}):\n"
                    market_analysis += f"  - Market Cap: ${market_cap:,.0f}\n"
                    description = company_data.get('description', 'N/A')
                    if description and len(description) > 100:
                        description = description[:100] + "..."
                    market_analysis += f"  - Description: {description}\n"
        
        # Calculate market insights
        if companies_analyzed > 0:
            avg_market_cap = total_market_cap / companies_analyzed
            market_analysis += f"\n📊 Market Insights:\n"
            market_analysis += f"- Total Market Cap (Top {companies_analyzed} companies): ${total_market_cap:,.0f}\n"
            market_analysis += f"- Average Market Cap: ${avg_market_cap:,.0f}\n"
            market_analysis += f"- Companies Analyzed: {companies_analyzed}\n"
            
            # Estimate total addressable market (rough approximation)
            estimated_tam = total_market_cap * 2.5  # Rough multiplier for private companies
            market_analysis += f"- Estimated Total Addressable Market: ${estimated_tam:,.0f}\n"
        else:
            market_analysis += "\n📊 Limited market data available for this industry.\n"
            market_analysis += "Consider researching private companies and market reports for more comprehensive analysis.\n"
        
        logger.info(f"Market analysis completed for {industry}")
        return [types.TextContent(type="text", text=market_analysis)]
        
    except Exception as e:
        logger.error(f"Error in market size analysis: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error analyzing market size: {str(e)}"
        )]


async def handle_growth_trends(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Get market growth trends by analyzing stock performance and financials.
    """
    try:
        industry = arguments.get("industry", "")
        timeframe = arguments.get("timeframe", "5-year")
        
        if not industry:
            return [types.TextContent(
                type="text",
                text="Industry parameter is required"
            )]
        
        logger.info(f"Analyzing growth trends for: {industry}")
        
        polygon = PolygonAPI()
        
        # Map timeframe to days
        days_mapping = {
            "1-year": 365,
            "3-year": 1095,
            "5-year": 1825,
            "10-year": 3650
        }
        days = days_mapping.get(timeframe, 1825)
        
        # Search for relevant companies
        search_results = polygon.search_tickers(industry, limit=5)
        
        if not search_results or not search_results.get("results"):
            return [types.TextContent(
                type="text",
                text=f"No companies found for growth analysis: {industry}"
            )]
        
        growth_analysis = f"Growth Trends Analysis for {industry} ({timeframe} outlook):\n\n"
        
        total_growth = 0
        companies_with_data = 0
        
        for ticker_info in search_results["results"][:3]:  # Analyze top 3 companies
            ticker = ticker_info.get("ticker")
            name = ticker_info.get("name", "Unknown")
            
            # Get historical market data (limited to 1 year for free tier)
            market_data = polygon.get_market_data(ticker, days=min(days, 365))
            
            if market_data and market_data.get("results") and len(market_data["results"]) > 1:
                results = market_data["results"]
                start_price = results[0].get("c")  # First closing price
                end_price = results[-1].get("c")   # Last closing price
                
                if start_price and end_price and start_price > 0:
                    growth_rate = ((end_price - start_price) / start_price) * 100
                    total_growth += growth_rate
                    companies_with_data += 1
                    
                    growth_analysis += f"\n{name} ({ticker}):\n"
                    growth_analysis += f"  - Price Growth (1-year): {growth_rate:.2f}%\n"
                    growth_analysis += f"  - Start Price: ${start_price:.2f}\n"
                    growth_analysis += f"  - Current Price: ${end_price:.2f}\n"
        
        # Calculate sector trends
        if companies_with_data > 0:
            avg_growth = total_growth / companies_with_data
            growth_analysis += f"\n📈 Sector Growth Trends:\n"
            growth_analysis += f"- Average Stock Growth (1-year): {avg_growth:.2f}%\n"
            growth_analysis += f"- Companies Analyzed: {companies_with_data}\n"
            
            # Provide growth assessment
            if avg_growth > 20:
                assessment = "High Growth - Strong sector momentum"
            elif avg_growth > 5:
                assessment = "Moderate Growth - Stable sector performance"
            elif avg_growth > 0:
                assessment = "Low Growth - Limited sector expansion"
            else:
                assessment = "Declining - Sector facing headwinds"
            
            growth_analysis += f"- Growth Assessment: {assessment}\n"
            
            # Add note about timeframe limitation
            if timeframe != "1-year":
                growth_analysis += f"\nNote: Analysis limited to 1-year data. For {timeframe} trends, consider premium market data sources.\n"
        else:
            growth_analysis += "\n📈 Limited growth data available for this industry.\n"
        
        logger.info(f"Growth trends analysis completed for {industry}")
        return [types.TextContent(type="text", text=growth_analysis)]
        
    except Exception as e:
        logger.error(f"Error in growth trends analysis: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error analyzing growth trends: {str(e)}"
        )]


async def handle_competitor_financials(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Get detailed financial information about public companies.
    """
    try:
        company_name = arguments.get("company_name", "")
        ticker = arguments.get("ticker", "")
        metrics = arguments.get("metrics", ["revenue", "growth_rate", "market_cap"])
        
        if not company_name and not ticker:
            return [types.TextContent(
                type="text",
                text="Either company_name or ticker is required"
            )]
        
        logger.info(f"Analyzing competitor financials for: {company_name or ticker}")
        
        polygon = PolygonAPI()
        
        # If no ticker provided, search for it
        if not ticker and company_name:
            search_results = polygon.search_tickers(company_name, limit=1)
            if search_results and search_results.get("results"):
                ticker = search_results["results"][0].get("ticker")
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Could not find ticker for company: {company_name}"
                )]
        
        if not ticker:
            return [types.TextContent(
                type="text",
                text="Unable to identify company ticker for analysis"
            )]
        
        # Get company details
        details = polygon.get_ticker_details(ticker)
        financials = polygon.get_stock_financials(ticker)
        market_data = polygon.get_market_data(ticker, days=30)  # Last 30 days
        
        financial_analysis = f"Financial Analysis for {company_name or ticker} ({ticker}):\n\n"
        
        # Company overview
        if details and details.get("results"):
            company_info = details["results"]
            financial_analysis += f"📊 Company Overview:\n"
            financial_analysis += f"- Name: {company_info.get('name', 'N/A')}\n"
            
            market_cap = company_info.get('market_cap')
            if market_cap:
                financial_analysis += f"- Market Cap: ${market_cap:,.0f}\n"
            
            employees = company_info.get('total_employees')
            if employees:
                financial_analysis += f"- Employees: {employees:,}\n"
            
            financial_analysis += f"- Industry: {company_info.get('sic_description', 'N/A')}\n"
            financial_analysis += f"- Website: {company_info.get('homepage_url', 'N/A')}\n\n"
        
        # Financial metrics
        if financials and financials.get("results"):
            financial_analysis += f"💰 Financial Metrics:\n"
            
            for result in financials["results"][:2]:  # Show last 2 periods
                period = result.get("end_date", "Unknown")
                financials_data = result.get("financials", {})
                
                financial_analysis += f"\nPeriod: {period}\n"
                
                if "revenue" in metrics:
                    income_statement = financials_data.get("income_statement", {})
                    revenues = income_statement.get("revenues", {})
                    revenue = revenues.get("value") if revenues else None
                    if revenue:
                        financial_analysis += f"  - Revenue: ${revenue:,.0f}\n"
                
                if "market_cap" in metrics and details:
                    market_cap = details["results"].get("market_cap")
                    if market_cap:
                        financial_analysis += f"  - Market Cap: ${market_cap:,.0f}\n"
        
        # Recent stock performance
        if market_data and market_data.get("results"):
            results = market_data["results"]
            if len(results) > 1:
                start_price = results[0].get("c")
                current_price = results[-1].get("c")
                if start_price and current_price:
                    price_change = ((current_price - start_price) / start_price) * 100
                    
                    financial_analysis += f"\n📈 Recent Performance (30 days):\n"
                    financial_analysis += f"- Price Change: {price_change:.2f}%\n"
                    financial_analysis += f"- Current Price: ${current_price:.2f}\n"
                    
                    last_volume = results[-1].get('v', 0)
                    if last_volume:
                        financial_analysis += f"- Volume: {last_volume:,} shares\n"
        
        # Add limitations note
        financial_analysis += f"\nNote: Analysis limited by API tier. For comprehensive financials, consider premium data sources.\n"
        
        logger.info(f"Competitor financials analysis completed for {ticker}")
        return [types.TextContent(type="text", text=financial_analysis)]
        
    except Exception as e:
        logger.error(f"Error in competitor financials analysis: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error analyzing competitor financials: {str(e)}"
        )]


async def main():
    """
    Main function to run the Market Data MCP server.
    """
    try:
        from mcp.server.stdio import stdio_server
        
        logger.info("Starting Market Data server...")
        
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="market-data",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    except Exception as e:
        logger.error(f"Failed to start Market Data server: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())