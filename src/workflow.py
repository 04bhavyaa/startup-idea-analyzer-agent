import asyncio
import json
import sys
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
import os

from .models import (
    ResearchState,
    StartupIdea,
    MarketAnalysis,
    CompetitorInfo,
    StartupAnalysis
)
from .prompts import StartupAnalysisPrompts


class StartupWorkflow:
    def __init__(self):
        """
        Initializes the startup analysis workflow with Gemini LLM.
        Async setup for tools and workflow is handled in the setup() method.
        """
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.prompts = StartupAnalysisPrompts()

        # Define server connections using the current Python executable for robustness
        connections = {
            "serp": {
                "command": sys.executable,
                "args": ["server/serp_server.py"],
                "transport": "stdio",
            },
            "market_data": {
                "command": sys.executable,
                "args": ["server/market_data_server.py"],
                "transport": "stdio",
            },
            "social_trends": {
                "command": sys.executable,
                "args": ["server/social_trends_server.py"],
                "transport": "stdio",
            },
        }
        self.mcp_client = MultiServerMCPClient(connections)
        self.tools = {}  # Will store tools by server name
        self.workflow = None  # Will be compiled in setup()
        self._is_setup = False

    async def setup(self):
        """
        Asynchronously sets up MCP tools and compiles the workflow graph.
        This must be called before running the workflow.
        """
        if self._is_setup:
            return

        try:
            # Load tools from each server
            for server_name in ["serp", "market_data", "social_trends"]:
                try:
                    tools_list = await self.mcp_client.get_tools(server_name=server_name)
                    self.tools[server_name] = {tool.name: tool for tool in tools_list}
                    print(f"✅ Loaded {len(tools_list)} tools from {server_name}: {[tool.name for tool in tools_list]}")
                except Exception as e:
                    print(f"⚠️ Warning: Could not load tools from {server_name}: {e}")
                    self.tools[server_name] = {}
            
            total_tools = sum(len(tools) for tools in self.tools.values())
            print(f"✅ Successfully connected to MCP servers. Total tools available: {total_tools}")
        except Exception as e:
            print(f"❌ Error connecting to MCP tools: {e}")
            raise ConnectionError("Could not connect to MCP tool servers.") from e

        self.workflow = self._build_workflow()
        self._is_setup = True

    def _build_workflow(self):
        """
        Builds the computational graph for the startup analysis agent using LangGraph.
        """
        graph = StateGraph(ResearchState)

        # Add nodes for each analysis step, wrapping async methods
        graph.add_node("market_research", self._market_research_step)
        graph.add_node("competitor_analysis", self._competitor_analysis_step)
        graph.add_node("social_trends_analysis", self._social_trends_step)
        graph.add_node("viability_assessment", self._viability_assessment_step)
        graph.add_node("final_recommendations", self._final_recommendations_step)

        # Define the workflow sequence
        graph.set_entry_point("market_research")
        graph.add_edge("market_research", "competitor_analysis")
        graph.add_edge("competitor_analysis", "social_trends_analysis")
        graph.add_edge("social_trends_analysis", "viability_assessment")
        graph.add_edge("viability_assessment", "final_recommendations")
        graph.add_edge("final_recommendations", END)

        return graph.compile()

    async def _market_research_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step 1: Conduct market research for the startup idea
        """
        print(f"--- Step 1: Market Research for '{state.query}' ---")

        market_queries = [
            f"{state.query} market size trends",
            f"{state.query} industry analysis report",
            f"{state.query} target audience demographics"
        ]

        all_market_content = ""
        search_results = []

        try:
            for query in market_queries:
                if "search" in self.tools.get("serp", {}):
                    tool = self.tools["serp"]["search"]
                    response = await tool.ainvoke({"query": query, "num_results": 3})
                    if response:
                        # The tool returns a string, so we parse it as JSON
                        try:
                            results = json.loads(response)
                            search_results.extend(results.get('results', []))

                            for result in results.get('results', []):
                                all_market_content += f"{result.get('title', '')} {result.get('snippet', '')}\n"
                        except json.JSONDecodeError:
                            # If not JSON, treat as plain text
                            all_market_content += f"{response}\n"

        except Exception as e:
            print(f"Error during market research: {e}")

        if all_market_content:
            structured_llm = self.llm.with_structured_output(MarketAnalysis)
            messages = [
                SystemMessage(content=self.prompts.MARKET_RESEARCH_SYSTEM),
                HumanMessage(content=self.prompts.market_research_user(state.query, all_market_content))
            ]
            try:
                market_analysis = await structured_llm.ainvoke(messages)
                print("Market analysis completed")
            except Exception as e:
                print(f"Error in market analysis: {e}")
                market_analysis = MarketAnalysis(market_size="N/A", growth_rate="N/A", target_audience=[], market_trends=[], barriers_to_entry=[])
        else:
            market_analysis = MarketAnalysis(market_size="N/A", growth_rate="N/A", target_audience=[], market_trends=[], barriers_to_entry=[])

        startup_idea = StartupIdea(
            name=state.query,
            description="",
            market_analysis=market_analysis
        )

        return {
            "startup_idea": startup_idea,
            "search_results": search_results,
            "market_data": {"analysis": market_analysis, "content": all_market_content}
        }

    async def _competitor_analysis_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step 2: Identify and analyze competitors
        """
        print("--- Step 2: Competitor Analysis ---")

        competitor_queries = [
            f"{state.query} competitors alternatives",
            f"{state.query} similar companies startups",
            f"{state.query} existing solutions market leaders"
        ]

        competitors = []
        competitor_data = []

        try:
            for query in competitor_queries:
                if "search" in self.tools.get("serp", {}):
                    tool = self.tools["serp"]["search"]
                    response = await tool.ainvoke({"query": query, "num_results": 5})
                    
                    if response:
                        try:
                            results = json.loads(response)
                            for result in results.get('results', []):
                                title = result.get('title', '')
                                url = result.get('link', '')
                                snippet = result.get('snippet', '')

                                if any(keyword in title.lower() for keyword in ['company', 'startup', 'platform', 'service']):
                                    competitor_name = title.split('-')[0].split('|')[0].strip()
                                    structured_llm = self.llm.with_structured_output(CompetitorInfo)
                                    messages = [
                                        SystemMessage(content=self.prompts.COMPETITOR_ANALYSIS_SYSTEM),
                                        HumanMessage(content=self.prompts.competitor_analysis_user(
                                            state.query, competitor_name, f"{title} {snippet}"
                                        ))
                                    ]
                                    try:
                                        competitor_info = await structured_llm.ainvoke(messages)
                                        competitor_info.name = competitor_name
                                        competitor_info.website = url
                                        competitors.append(competitor_info)
                                        competitor_data.append(result)
                                        if len(competitors) >= 5:
                                            break
                                    except Exception as e:
                                        print(f"Error analyzing competitor {competitor_name}: {e}")
                        except json.JSONDecodeError:
                            print(f"Error parsing search results for query: {query}")
                if len(competitors) >= 5:
                    break
        except Exception as e:
            print(f"Error during competitor research: {e}")

        print(f"Found {len(competitors)} competitors")

        updated_startup = state.startup_idea
        if updated_startup:
            updated_startup.competitors = competitors

        return {
            "startup_idea": updated_startup,
            "competitor_data": competitor_data
        }

    async def _social_trends_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step 3: Analyze social trends and sentiment
        """
        print("--- Step 3: Social Trends Analysis ---")

        social_data = {}
        try:
            if "analyze_trends" in self.tools.get("social_trends", {}):
                tool = self.tools["social_trends"]["analyze_trends"]
                response = await tool.ainvoke({
                    "topic": state.query, 
                    "platforms": ["reddit", "twitter"]
                })
                if response:
                    social_data = {"content": response, "source": "social_trends_api"}
                print("Social trends analysis completed")
        except Exception as e:
            print(f"Error in social trends analysis, using fallback: {e}")
            social_queries = [
                f"{state.query} reddit discussion opinions",
                f"{state.query} social media trends sentiment"
            ]
            social_content = ""
            try:
                for query in social_queries:
                    if "search" in self.tools.get("serp", {}):
                        tool = self.tools["serp"]["search"]
                        response = await tool.ainvoke({"query": query, "num_results": 3})
                        if response:
                            try:
                                results = json.loads(response)
                                for result in results.get('results', []):
                                    social_content += f"{result.get('title', '')} {result.get('snippet', '')}\n"
                            except json.JSONDecodeError:
                                social_content += f"{response}\n"
                social_data = {"content": social_content, "source": "web_search"}
            except Exception as fallback_e:
                print(f"Error in social search fallback: {fallback_e}")
                social_data = {"error": str(fallback_e)}

        return {"social_trends": social_data}

    async def _viability_assessment_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step 4: Assess startup viability based on all collected data
        """
        print("--- Step 4: Viability Assessment ---")

        market_summary = ""
        market_data = state.market_data
        if market_data:
            analysis = market_data.get('analysis')
            if analysis:
                market_summary = f"""
                Market Size: {analysis.market_size or 'Unknown'}
                Growth Rate: {analysis.growth_rate or 'Unknown'}
                Target Audience: {', '.join(analysis.target_audience)}
                Market Trends: {', '.join(analysis.market_trends)}
                Barriers: {', '.join(analysis.barriers_to_entry)}
                """

        competitor_summary = ""
        startup_idea = state.startup_idea
        if startup_idea and startup_idea.competitors:
            competitor_names = [comp.name for comp in startup_idea.competitors]
            competitor_summary = f"Main competitors: {', '.join(competitor_names[:5])}"

        social_summary = str(state.social_trends)[:500]

        structured_llm = self.llm.with_structured_output(StartupAnalysis)
        messages = [
            SystemMessage(content=self.prompts.VIABILITY_ASSESSMENT_SYSTEM),
            HumanMessage(content=self.prompts.viability_assessment_user(
                state.query, market_summary, competitor_summary, social_summary
            ))
        ]

        try:
            viability_analysis = await structured_llm.ainvoke(messages)
            print(f"Viability assessment completed - Score: {viability_analysis.viability_score}/10")
        except Exception as e:
            print(f"Error in viability assessment: {e}")
            viability_analysis = StartupAnalysis()

        if startup_idea:
            startup_idea.startup_analysis = viability_analysis

        return {"startup_idea": startup_idea}

    async def _final_recommendations_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Step 5: Generate final recommendations and analysis summary
        """
        print("--- Step 5: Final Recommendations ---")
        
        startup_idea = state.startup_idea
        market_data = state.market_data
        social_trends = state.social_trends

        full_analysis = f"""
        Startup Idea: {state.query}
        Market Analysis: {market_data}
        Competitors Found: {len(startup_idea.competitors) if startup_idea else 0}
        Viability Score: {startup_idea.startup_analysis.viability_score if startup_idea and startup_idea.startup_analysis else 'N/A'}/10
        Social Trends: {str(social_trends)[:300]}...
        """

        messages = [
            SystemMessage(content=self.prompts.FINAL_RECOMMENDATION_SYSTEM),
            HumanMessage(content=self.prompts.final_recommendation_user(state.query, full_analysis))
        ]

        try:
            response = await self.llm.ainvoke(messages)
            final_analysis = response.content
            print("Final recommendations generated")
        except Exception as e:
            print(f"Error generating final recommendations: {e}")
            final_analysis = "Unable to generate final recommendations due to processing error."

        recommendations = []
        if "1." in final_analysis:
            lines = final_analysis.split('\n')
            for line in lines:
                if any(line.strip().startswith(f"{i}.") for i in range(1, 10)):
                    recommendations.append(line.strip())

        return {
            "final_analysis": final_analysis,
            "recommendations": recommendations
        }

    async def run(self, query: str) -> ResearchState:
        """
        Executes the complete startup analysis workflow for a given idea.
        """
        if not self._is_setup:
            await self.setup()

        print(f"Starting startup analysis for: {query}")
        initial_state = {"query": query}

        try:
            final_state = await self.workflow.ainvoke(initial_state)
            print("Startup analysis workflow completed successfully")
        except Exception as e:
            print(f"Error during workflow execution: {e}")
            final_state = initial_state

        return ResearchState(**final_state)
