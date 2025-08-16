# Startup Idea Analyzer Agent

This project is a sophisticated, multi-step AI agent designed to automate the process of researching and analyzing startup ideas. Given a simple query (e.g., "a platform for local artists to sell their work"), the agent performs web searches, scrapes relevant articles, extracts key information, and generates a final, structured analysis with recommendations.

The agent is built with a modern Python stack, features a modular, scalable architecture using the Model Context Protocol (MCP), and has a user-friendly web interface created with Gradio.

## Features

- **Multi-Step Workflow**: Utilizes LangGraph to create a robust, multi-step workflow (e.g., market research → competitor analysis → viability assessment).

- **Modular & Scalable Architecture**: Uses the Model Context Protocol (MCP) to connect the agent to a suite of external, independently-run tool servers. This makes the system easy to extend and maintain.

- **Dynamic Web Search**: Employs the SERP API via a dedicated MCP server to perform real-time, in-depth web searches for market trends, existing competitors, and potential customer bases.

- **AI-Powered Analysis**: Leverages Google's Gemini 2.5 Flash model for intelligent data extraction and final analysis of the startup idea's potential.

- **Structured Output**: Uses Pydantic models to ensure the data passed between steps is structured and validated.

- **Resilient Error Handling**: Includes a fallback mechanism to recover from failed steps and continue the research process.

- **Interactive UI**: Provides both a beautiful web interface built with Gradio and a command-line interface for different use cases.

## Tech Stack

- **Orchestration**: LangChain & LangGraph
- **Tool Integration**: Model Context Protocol (MCP)
- **LLM**: Google Gemini 2.5 Flash
- **Web Search**: SERP API
- **Web UI**: Gradio
- **Package Management**: uv
- **Language**: Python 3.10+

## Architecture

This agent uses a client-server architecture powered by MCP. The core LangGraph agent acts as the "client" that orchestrates the analysis. It connects to one or more specialized MCP "servers," which are small, independent applications that provide specific tools.

This decoupled design means you can easily add, remove, or update tools without changing the core agent logic.

### Tool Servers

- **SERP API Server**: Exposes a tool for performing deep web searches. This is the primary data gathering source for the agent.

- **Market Data Server**: Connects to financial data APIs to fetch information on market size, industry growth rates, and public competitor financials.

- **Social Media Trends Server**: Provides tools to analyze trends, discussions, and sentiment on platforms like Reddit or X to gauge public interest and identify pain points.

## Setup and Installation

Follow these steps to set up the project environment.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-repository-name>
```

### 2. Initialize Project

Initialize the project with uv:

```bash
uv init .
```

### 3. Install Dependencies

Use uv to install all the required packages from requirements.txt or do this:

```bash
uv add google-search-results python-dotenv langchain-google-genai langchain langgraph pydantic mcp "mcp[cli]" langchain-mcp-adapters gradio
```

### 4. Set Up Environment Variables

Create a file named `.env` in the root of your project directory and add your API keys:

```env
GOOGLE_API_KEY=your_google_api_key_here
SERP_API_KEY=your_serp_api_key_here
```

## How to Run

### Option 1: Web Interface (Recommended)

Launch the Gradio web application for a user-friendly interface:

```bash
uv run python gradio_app.py
```

The web interface will:

- Automatically start MCP tool servers
- Provide a beautiful, interactive UI
- Display results with proper formatting
- Allow downloading reports in text and JSON formats
- Show real-time progress updates

### Option 2: Command Line Interface

Run the traditional CLI version:

```bash
uv run python main.py
```

The CLI will:

1. Validate your environment variables
2. Initialize the workflow and connect to MCP servers
3. Start an interactive terminal where you can enter startup ideas for analysis

### Alternative: Manual Server Setup

If you prefer to run the MCP servers manually (for debugging or development), you can start them in separate terminals:

```bash
# Terminal 1: Start the SERP API server
uv run python server/serp_server.py

# Terminal 2: Start the Market Data server
uv run python server/market_data_server.py

# Terminal 3: Start the Social Media Trends server
uv run python server/social_trends_server.py
```

Then run either interface in a fourth terminal:

```bash
# For web interface
uv run python gradio_app.py

# For CLI interface
uv run python main.py
```

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── workflow.py         # Defines the core LangGraph agent and MCP client logic
│   ├── models.py           # Pydantic models for state and data structures
│   └── prompts.py          # Contains all prompts for the LLM
├── server/
│   ├── serp_server.py      # MCP server for the SERP API
│   ├── market_data_server.py # MCP server for financial data
│   └── social_trends_server.py # MCP server for social media analysis
├── .env                    # Stores API keys and environment variables
├── .python-version         # Python version specification
├── main.py                 # The CLI application entry point
├── gradio_app.py           # The Gradio web application
├── pyproject.toml          # Project configuration and dependencies
└── README.md               # You are here!
```

## Usage

### Web Interface (Recommended)

1. Launch the Gradio app: `uv run python gradio_app.py`

2. Open your browser to the provided URL (usually http://127.0.0.1:7860 or http://localhost:7860)

3. Enter your startup idea in the text area (e.g., "a platform for local artists to sell their work")

4. Click "🚀 Analyze Idea" and wait for the analysis to complete

5. Review the comprehensive analysis including:

   - Market research and size assessment
   - Competitor analysis and positioning
   - Social media trends and sentiment
   - Viability assessment with scoring
   - Final recommendations and next steps

6. Download the full report in text or JSON format using the download buttons

### Command Line Interface

1. Run the CLI: `uv run python main.py`

2. Enter your startup idea when prompted

3. Wait for the analysis to complete (this may take a few minutes)

4. Review the results and optionally save to a text file

5. Enter another idea or type 'quit' to exit
