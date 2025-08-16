class StartupAnalysisPrompts:
    """Collection of prompts for analyzing startup ideas and market opportunities"""

    # Market Research Prompts
    MARKET_RESEARCH_SYSTEM = """You are a market research analyst specializing in startup ecosystems and emerging business opportunities.
                            Focus on identifying market size, growth trends, target demographics, and market dynamics."""

    @staticmethod
    def market_research_user(startup_idea: str, search_content: str) -> str:
        return f"""Startup Idea: {startup_idea}
                Market Research Content: {search_content}

                Based on this market research content, analyze the market opportunity for "{startup_idea}".

                Focus on:
                - Market size and growth potential
                - Target audience demographics and behavior
                - Current market trends and future projections
                - Barriers to entry and regulatory landscape
                - Market gaps and opportunities

                Provide specific data points, statistics, and insights where available.
                If information is limited, indicate areas that need further research."""

    # Competitor Analysis Prompts
    COMPETITOR_ANALYSIS_SYSTEM = """You are a competitive intelligence analyst. Analyze competitors, their business models,
                                funding, strengths, weaknesses, and market positioning."""

    @staticmethod
    def competitor_analysis_user(startup_idea: str, competitor_name: str, competitor_content: str) -> str:
        return f"""Startup Idea: {startup_idea}
                Competitor: {competitor_name}
                Competitor Information: {competitor_content[:2000]}

                Analyze this competitor in relation to the startup idea "{startup_idea}":

                Extract:
                - funding_stage: Current funding stage (Pre-seed, Seed, Series A/B/C, etc.)
                - funding_amount: Total funding raised if mentioned
                - business_model: How they make money (B2B, B2C, SaaS, Marketplace, etc.)
                - key_features: Main product features or services offered
                - strengths: What they do well or competitive advantages
                - weaknesses: Limitations or areas for improvement
                - pricing_model: How they price their product/service

                Focus on information relevant to understanding their market position."""

    # Startup Viability Assessment Prompts
    VIABILITY_ASSESSMENT_SYSTEM = """You are a startup advisor and investor with expertise in evaluating business ideas.
                                  Assess viability based on market opportunity, competition, execution difficulty, and business model."""

    @staticmethod
    def viability_assessment_user(startup_idea: str, market_data: str, competitor_data: str, social_data: str) -> str:
        return f"""Startup Idea: {startup_idea}

                Market Research Summary:
                {market_data}

                Competitor Analysis Summary:
                {competitor_data}

                Social Trends & Sentiment:
                {social_data}

                Provide a comprehensive viability assessment:

                - viability_score: Rate from 1-10 (1=very poor, 10=excellent opportunity)
                - market_opportunity: Brief assessment of market size and timing
                - competitive_advantage: Potential ways to differentiate from competitors
                - potential_challenges: Main obstacles and risks to consider
                - monetization_strategies: Suggested revenue models and pricing approaches
                - required_resources: Key resources needed (funding, team, technology, etc.)
                - time_to_market: Estimated time to launch MVP and scale
                - risk_assessment: Overall risk level (Low/Medium/High) with brief explanation

                Be realistic but constructive in your assessment."""

    # Final Recommendation Prompts
    FINAL_RECOMMENDATION_SYSTEM = """You are a startup mentor providing actionable advice to entrepreneurs.
                                  Synthesize research findings into clear, practical recommendations."""

    @staticmethod
    def final_recommendation_user(startup_idea: str, full_analysis: str) -> str:
        return f"""Startup Idea: {startup_idea}

                Complete Analysis:
                {full_analysis}

                Provide final recommendations (keep to 4-5 key points):

                1. GO/NO-GO decision with brief reasoning
                2. If GO: Top 3 immediate next steps
                3. Key success factors to focus on
                4. Major risks to monitor and mitigate
                5. Alternative pivots or variations to consider

                Keep recommendations specific, actionable, and realistic.
                Aim for clarity over comprehensiveness."""

    # Social Trends Analysis Prompts
    SOCIAL_TRENDS_SYSTEM = """You are a social media analyst and trend researcher. Identify public sentiment,
                           discussions, and emerging trends related to business ideas and market needs."""

    @staticmethod
    def social_trends_user(startup_idea: str, social_content: str) -> str:
        return f"""Startup Idea: {startup_idea}
                Social Media & Discussion Content: {social_content}

                Analyze social trends and sentiment related to "{startup_idea}":

                Look for:
                - Public interest and demand signals
                - Common pain points and frustrations
                - Existing solutions people are discussing
                - Sentiment toward similar products/services
                - Trending topics and emerging needs
                - User behavior patterns and preferences

                Provide insights on market timing and customer validation opportunities."""