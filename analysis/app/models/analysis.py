"""
Pydantic models for analysis data
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import datetime


class TechnicalPatternModel(BaseModel):
    """Technical pattern model"""
    pattern_name: str
    direction: Literal["bullish", "bearish", "neutral"]
    strength: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    duration: str
    key_levels: Dict[str, float]
    probability: float = Field(ge=0, le=1)


class CompanyAnalysisModel(BaseModel):
    """Company analysis model"""
    value_score: float
    growth_score: float
    momentum_score: float
    overall_score: float
    recommendation: str
    sentiment: str
    risk_level: str
    confidence: float


class CompanyWithAnalysisModel(BaseModel):
    """Company with analysis model"""
    symbol: str
    company_name: str
    current_price: float
    change_percent: float
    analysis: CompanyAnalysisModel
    patterns: Optional[List[TechnicalPatternModel]] = None
    metrics: Optional[Dict[str, float]] = None
    insights: Optional[List[str]] = None


class AnalysisResponse(BaseModel):
    """Analysis response model"""
    timestamp: str
    total_analyses: Optional[int] = None
    analyses: List[CompanyWithAnalysisModel]


class TopOpportunitiesResponse(BaseModel):
    """Top opportunities response model"""
    timestamp: str
    limit: int
    analyses: List[CompanyWithAnalysisModel]


class PatternsResponse(BaseModel):
    """Patterns response model"""
    timestamp: str
    total_with_patterns: int
    companies: List[CompanyWithAnalysisModel]


class SingleAnalysisResponse(BaseModel):
    """Single company analysis response model"""
    timestamp: str
    analysis: CompanyWithAnalysisModel


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = "healthy"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    service: str = "analysis-api"

