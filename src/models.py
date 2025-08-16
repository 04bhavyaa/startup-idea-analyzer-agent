from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MarketAnalysis(BaseModel):
    """Structured output for LLM Market Analysis"""
    market_size: Optional[str] = None
    growth_rate: Optional[str] = None
    target_audience: List[str] = Field(default_factory=list)
    market_trends: List[str] = Field(default_factory=list)
    barriers_to_entry: List[str] = Field(default_factory=list)
    regulatory_considerations: List[str] = Field(default_factory=list)

class CompetitorInfo(BaseModel):
    """Information about a competitor"""
    name: str
    website: str
    description: str = ""
    funding_stage: Optional[str] = None # Seed, Series A,B,C etc.
    funding_amount: Optional[str] = None
    business_model: Optional[str] = None # B2B, B2C, Marketplace, Saas, etc.
    key_features: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    pricing_model: Optional[str] = None

class StartupAnalysis(BaseModel):
    """Structured output for LLM startup idea analysis"""
    viability_score: Optional[int] = Field(None, ge=1, le=10, description="Viability score from 1-10")
    market_opportunity: Optional[str] = None
    competitive_advantage: List[str] = Field(default_factory=list)
    potential_challenges: List[str] = Field(default_factory=list)
    monetization_strategies: List[str] = Field(default_factory=list)
    required_resources: List[str] = Field(default_factory=list)
    time_to_market: Optional[str] = None
    risk_assessment: Optional[str] = None  # Low, Medium, High

class StartupIdea(BaseModel):
    """Main startup idea information"""
    name: str
    description: str
    category: Optional[str] = None  # FinTech, EdTech, HealthTech, etc.
    business_model: Optional[str] = None
    target_market: List[str] = Field(default_factory=list)
    value_proposition: Optional[str] = None

    # Analysis results
    market_analysis: Optional[MarketAnalysis] = None
    competitors: List[CompetitorInfo] = Field(default_factory=list)
    startup_analysis: Optional[StartupAnalysis] = None

class ResearchState(BaseModel):
    """State management for the startup research workflow"""
    query: str
    startup_idea: Optional[StartupIdea] = None
    search_results: List[Dict[str, Any]] = Field(default_factory=list)
    market_data: Dict[str, Any] = Field(default_factory=dict)
    competitor_data: List[Dict[str, Any]] = Field(default_factory=list)
    social_trends: Dict[str, Any] = Field(default_factory=dict)
    final_analysis: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)