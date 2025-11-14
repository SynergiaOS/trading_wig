"""
Data router - handles market data endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Literal
from ..models.market import MarketDataResponse, HealthResponse, StatsResponse
from ..services.data_loader import data_loader
from datetime import datetime
import time

router = APIRouter(tags=["data"])

# Simple stats tracking
_start_time = time.time()
_request_count = 0
_successful_requests = 0
_failed_requests = 0


@router.get("/data", response_model=MarketDataResponse, summary="Get WIG80 data")
@router.get("/wig80", response_model=MarketDataResponse, summary="Get WIG80 data (alias)")
@router.get("/", response_model=MarketDataResponse, summary="Get WIG80 data (root)")
async def get_wig80_data(use_cache: bool = Query(True, description="Use cached data if available")):
    """
    Get WIG80 market data (all 88 companies)
    
    - **use_cache**: Use cached data if available (default: true)
    """
    global _request_count, _successful_requests, _failed_requests
    
    _request_count += 1
    try:
        data = data_loader.get_data(use_cache=use_cache)
        _successful_requests += 1
        return MarketDataResponse(**data)
    except FileNotFoundError as e:
        _failed_requests += 1
        raise HTTPException(status_code=404, detail=f"Data file not found: {str(e)}")
    except Exception as e:
        _failed_requests += 1
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


@router.get("/wig30", response_model=MarketDataResponse, summary="Get WIG30 data")
async def get_wig30_data(use_cache: bool = Query(True, description="Use cached data if available")):
    """
    Get WIG30 market data (top 30 companies by volume)
    
    - **use_cache**: Use cached data if available (default: true)
    """
    global _request_count, _successful_requests, _failed_requests
    
    _request_count += 1
    try:
        data = data_loader.get_wig30_data(use_cache=use_cache)
        _successful_requests += 1
        return MarketDataResponse(**data)
    except FileNotFoundError as e:
        _failed_requests += 1
        raise HTTPException(status_code=404, detail=f"Data file not found: {str(e)}")
    except Exception as e:
        _failed_requests += 1
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


@router.get("/health", response_model=HealthResponse, summary="Health check")
@router.get("/api/health", response_model=HealthResponse, summary="Health check (API path)")
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service="backend-api"
    )


@router.get("/stats", response_model=StatsResponse, summary="Get API statistics")
@router.get("/api/stats", response_model=StatsResponse, summary="Get API statistics (API path)")
async def get_stats():
    """Get API statistics"""
    global _request_count, _successful_requests, _failed_requests, _start_time
    
    uptime = time.time() - _start_time
    
    return StatsResponse(
        total_requests=_request_count,
        successful_requests=_successful_requests,
        failed_requests=_failed_requests,
        uptime_seconds=uptime
    )

