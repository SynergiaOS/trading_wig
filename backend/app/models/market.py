"""
Pydantic models for market data
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CompanyModel(BaseModel):
    """Company data model"""
    company_name: str
    symbol: str
    current_price: float
    change_percent: float
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    trading_volume: str
    trading_volume_obrot: Optional[str] = None
    last_update: Optional[str] = None
    status: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "PKN Orlen SA",
                "symbol": "PKN",
                "current_price": 388.50,
                "change_percent": 13.76,
                "pe_ratio": 29.75,
                "pb_ratio": 2.15,
                "trading_volume": "1.5M"
            }
        }


class MarketMetadataModel(BaseModel):
    """Market metadata model"""
    collection_date: str
    data_source: str
    index: str
    currency: str
    total_companies: int
    successful_fetches: Optional[int] = None
    market_status: Optional[str] = None
    poland_time: Optional[str] = None
    is_market_hours: Optional[bool] = None
    avg_change: Optional[float] = None


class MarketDataResponse(BaseModel):
    """Market data response model"""
    metadata: MarketMetadataModel
    companies: List[CompanyModel]


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = "healthy"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    service: str = "backend-api"


class StatsResponse(BaseModel):
    """Statistics response model"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    uptime_seconds: float = 0.0

