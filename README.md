# Startup Idea Analyzer Agent

An AI-powered startup analysis platform that automatically researches and evaluates startup ideas using real-time market data, competitor analysis, and social media sentiment. Built with a modern Python stack featuring LangGraph orchestration, Model Context Protocol (MCP) for tool integration, and a beautiful Gradio web interface.

## 🚀 Features

- **Multi-Step AI Workflow**: Automated 5-step analysis pipeline using LangGraph
- **Real-Time Market Research**: Web search, competitor analysis, and financial data
- **Social Media Intelligence**: Reddit and Twitter sentiment analysis
- **Structured Output**: Pydantic models ensure data consistency and validation
- **Multiple Interfaces**: Web UI (Gradio) and Command Line Interface
- **Report Generation**: Export analysis in Text, PDF, and Word formats
- **Modular Architecture**: MCP-based tool servers for easy extension

## 🏗️ Architecture

The system uses a client-server architecture with MCP (Model Context Protocol):

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main Agent    │    │   MCP Client    │    │   Tool Servers  │
│  (LangGraph)    │◄──►│  (Orchestrator) │◄──►│  (Data Sources) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   CLI Interface │    │   External APIs │
│    (Gradio)     │    │   (Terminal)    │    │   (SERP, etc.)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 APIs & External Services

### Core APIs (Required)

- **Google Gemini 2.5 Flash**: Primary LLM for analysis and reasoning
- **SERP API**: Web search and news search functionality

### Optional APIs (Enhanced Features)

- **Polygon.io API**: Financial market data and company information
- **Reddit API (PRAW)**: Social media sentiment and trend analysis
- **Twitter API v2**: Social media sentiment and engagement metrics

### Internal APIs

- **Model Context Protocol (MCP)**: Tool server communication
- **LangChain**: LLM orchestration and tool integration
- **LangGraph**: Workflow state management and execution

## 📁 Project Structure

```
startup-idea-analyzer-agent/
├── src/                          # Core application logic
│   ├── workflow.py              # LangGraph workflow definition
│   ├── models.py                # Pydantic data models
│   └── prompts.py               # LLM prompt templates
├── server/                      # MCP tool servers
│   ├── serp_server.py           # Web search server
│   ├── market_data_server.py    # Financial data server
│   └── social_trends_server.py  # Social media analysis server
├── main.py                      # CLI application entry point
├── gradio_app.py                # Web interface application
├── pyproject.toml               # Project configuration and dependencies
├── uv.lock                      # Dependency lock file
├── .python-version              # Python version specification
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🛠️ Implementation Details

### Core Workflow (`src/workflow.py`)

The main analysis pipeline consists of 5 sequential steps:

1. **Market Research**: Web search for market size, trends, and demographics
2. **Competitor Analysis**: Identify and analyze existing competitors
3. **Social Trends**: Analyze Reddit and Twitter sentiment
4. **Viability Assessment**: Score startup potential (1-10)
5. **Final Recommendations**: Generate actionable insights

### Data Models (`src/models.py`)

Structured Pydantic models for:

- `MarketAnalysis`: Market size, growth, target audience
- `CompetitorInfo`: Competitor details and positioning
- `StartupAnalysis`: Viability scoring and assessment
- `StartupIdea`: Complete startup information
- `ResearchState`: Workflow state management

### Tool Servers

#### SERP Server (`server/serp_server.py`)

- **Purpose**: Web search and news search
- **Tools**: `search`, `search_news`
- **API**: SERP API (Google Search)
- **Features**: Location-based search, result filtering

#### Market Data Server (`server/market_data_server.py`)

- **Purpose**: Financial market analysis
- **Tools**: `get_market_size`, `get_growth_trends`, `get_competitor_financials`
- **API**: Polygon.io (optional)
- **Features**: Market cap analysis, growth trends, competitor financials

#### Social Trends Server (`server/social_trends_server.py`)

- **Purpose**: Social media sentiment analysis
- **Tools**: `analyze_trends`, `reddit_analysis`, `twitter_sentiment`
- **APIs**: Reddit API (PRAW), Twitter API v2 (optional)
- **Features**: Sentiment analysis, engagement metrics, trend identification

### User Interfaces

#### Web Interface (`gradio_app.py`)

- **Framework**: Gradio
- **Features**:
  - Real-time progress tracking
  - Beautiful dark theme UI
  - Multiple export formats (TXT, PDF, DOCX)
  - Interactive results display
  - Environment validation

#### CLI Interface (`main.py`)

- **Features**:
  - Interactive terminal interface
  - Pretty-printed results
  - File export capability
  - Environment validation
  - Error handling and recovery

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd startup-idea-analyzer-agent

# Install dependencies using uv
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Required API Keys

Create a `.env` file with:

```env
# Required APIs
GOOGLE_API_KEY=your_gemini_api_key
SERP_API_KEY=your_serp_api_key

# Optional APIs (for enhanced features)
POLYGON_API_KEY=your_polygon_api_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

### 3. Run the Application

#### Web Interface (Recommended)

```bash
uv run python gradio_app.py
```

Open browser to `http://localhost:7860`

#### Command Line Interface

```bash
uv run python main.py
```

#### Hugging Face Spaces Deployment

```bash
# Use app.py for Hugging Face Spaces
uv run python app.py
```

## 📊 Analysis Output

The system generates comprehensive reports including:

### Market Analysis

- Market size and growth projections
- Target audience demographics
- Market trends and barriers to entry
- Regulatory considerations

### Competitor Analysis

- Top 5 competitors with detailed profiles
- Business models and funding stages
- Key features and competitive advantages
- Pricing strategies and market positioning

### Social Media Intelligence

- Reddit discussion analysis and sentiment
- Twitter engagement metrics
- Trending topics and public sentiment
- Community feedback and pain points

### Viability Assessment

- Overall viability score (1-10)
- Market opportunity assessment
- Competitive advantages and challenges
- Monetization strategies
- Risk assessment and time to market

### Final Recommendations

- Go/No-Go decision with reasoning
- Immediate next steps
- Key success factors
- Risk mitigation strategies
- Alternative pivot opportunities

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Required for LLM analysis
- `SERP_API_KEY`: Required for web search
- `POLYGON_API_KEY`: Optional for financial data
- `REDDIT_CLIENT_ID/SECRET`: Optional for Reddit analysis
- `TWITTER_BEARER_TOKEN`: Optional for Twitter analysis

### Customization

- Modify prompts in `src/prompts.py`
- Add new tools in server files
- Extend data models in `src/models.py`
- Customize workflow in `src/workflow.py`
- Update deployment configuration in `app.py`

## 🛡️ Error Handling

The system includes robust error handling:

- Graceful fallbacks when APIs are unavailable
- Partial analysis when some tools fail
- Detailed error logging and user feedback
- Automatic retry mechanisms for transient failures

## 📈 Performance

- **Typical Analysis Time**: 2-5 minutes per startup idea
- **Concurrent Users**: Limited by API rate limits
- **Data Sources**: Real-time web search + cached financial data
- **Scalability**: MCP architecture allows horizontal scaling
- **Python Version**: 3.13+ (specified in .python-version)

## 🚀 Tech Stack

### Core Framework & Orchestration

- **LangGraph** - Workflow orchestration and state management
- **LangChain** - LLM integration and tool management
- **Model Context Protocol (MCP)** - Tool server communication protocol

### AI & Machine Learning

- **Google Gemini 2.5 Flash** - Primary LLM for analysis and reasoning
- **Pydantic** - Data validation and serialization
- **Structured Output** - LLM response formatting

### Web Development & UI

- **Gradio** - Web interface framework
- **HTML/CSS** - Custom styling and layout
- **JavaScript** - Interactive UI components

### External APIs & Services

- **SERP API** - Web search and news search
- **Polygon.io API** - Financial market data (optional)
- **Reddit API (PRAW)** - Social media analysis (optional)
- **Twitter API v2 (Tweepy)** - Social media sentiment (optional)

### Development & Build Tools

- **uv** - Python package manager and project management
- **Python 3.13+** - Programming language
- **asyncio** - Asynchronous programming
- **logging** - Application logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review API documentation
3. Open an issue on GitHub
4. Check environment variable configuration
5. Refer to `DEPLOYMENT_GUIDE.md` for deployment help

---

