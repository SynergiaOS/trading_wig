"""
Analysis router - handles analysis endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from ..models.analysis import (
    AnalysisResponse,
    TopOpportunitiesResponse,
    PatternsResponse,
    SingleAnalysisResponse,
    HealthResponse
)
from ..services.data_loader import data_loader
from ..services.analysis_engine import analysis_engine
from ..services.patterns import pattern_service

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("", response_model=AnalysisResponse, summary="Get all analyses")
async def get_all_analyses():
    """
    Get analysis for all companies
    """
    try:
        data = data_loader.load_wig80_data()
        companies = data.get('companies', [])
        
        analyses = []
        for company in companies:
            analysis = analysis_engine.generate_analysis(company)
            insights = analysis_engine.generate_insights(
                company,
                analysis.overall_score,
                analysis.recommendation
            )
            
            analyses.append({
                "symbol": company.get('symbol', ''),
                "company_name": company.get('company_name', ''),
                "current_price": company.get('current_price', 0),
                "change_percent": company.get('change_percent', 0),
                "analysis": analysis.dict(),
                "metrics": {
                    "pe_ratio": company.get('pe_ratio'),
                    "pb_ratio": company.get('pb_ratio'),
                    "volatility": round(abs(company.get('change_percent', 0)), 2),
                    "price_momentum": "up" if company.get('change_percent', 0) > 0 else "down"
                },
                "insights": insights
            })
        
        # Sort by overall score
        analyses.sort(key=lambda x: x['analysis']['overall_score'], reverse=True)
        
        return AnalysisResponse(
            timestamp=datetime.now().isoformat(),
            total_analyses=len(analyses),
            analyses=analyses
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Data file not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analyses: {str(e)}")


@router.get("/top", response_model=TopOpportunitiesResponse, summary="Get top opportunities")
async def get_top_opportunities(limit: int = Query(10, ge=1, le=100, description="Number of top opportunities")):
    """
    Get top investment opportunities
    
    - **limit**: Number of top opportunities to return (1-100)
    """
    try:
        data = data_loader.load_wig80_data()
        companies = data.get('companies', [])
        
        analyses = []
        for company in companies:
            analysis = analysis_engine.generate_analysis(company)
            insights = analysis_engine.generate_insights(
                company,
                analysis.overall_score,
                analysis.recommendation
            )
            
            analyses.append({
                "symbol": company.get('symbol', ''),
                "company_name": company.get('company_name', ''),
                "current_price": company.get('current_price', 0),
                "change_percent": company.get('change_percent', 0),
                "analysis": analysis.dict(),
                "metrics": {
                    "pe_ratio": company.get('pe_ratio'),
                    "pb_ratio": company.get('pb_ratio'),
                    "volatility": round(abs(company.get('change_percent', 0)), 2),
                    "price_momentum": "up" if company.get('change_percent', 0) > 0 else "down"
                },
                "insights": insights
            })
        
        # Sort by overall score and get top
        analyses.sort(key=lambda x: x['analysis']['overall_score'], reverse=True)
        top_analyses = analyses[:limit]
        
        return TopOpportunitiesResponse(
            timestamp=datetime.now().isoformat(),
            limit=limit,
            analyses=top_analyses
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Data file not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating top opportunities: {str(e)}")


@router.get("/patterns", response_model=PatternsResponse, summary="Get companies with patterns")
async def get_patterns():
    """
    Get all companies with detected technical patterns
    """
    try:
        data = data_loader.load_wig80_data()
        companies = data.get('companies', [])
        
        companies_with_patterns = []
        for company in companies:
            try:
                patterns = pattern_service.detect_patterns(company)
                if patterns:
                    analysis = analysis_engine.generate_analysis(company)
                    insights = analysis_engine.generate_insights(
                        company,
                        analysis.overall_score,
                        analysis.recommendation
                    )
                    
                    companies_with_patterns.append({
                        "symbol": company.get('symbol', ''),
                        "company_name": company.get('company_name', ''),
                        "current_price": company.get('current_price', 0),
                        "change_percent": company.get('change_percent', 0),
                        "analysis": analysis.dict(),
                        "patterns": patterns,
                        "metrics": {
                            "pe_ratio": company.get('pe_ratio'),
                            "pb_ratio": company.get('pb_ratio'),
                            "volatility": round(abs(company.get('change_percent', 0)), 2),
                            "price_momentum": "up" if company.get('change_percent', 0) > 0 else "down"
                        },
                        "insights": insights
                    })
            except Exception as e:
                print(f"Error processing {company.get('symbol', 'unknown')}: {e}")
                continue
        
        # Sort by pattern strength
        companies_with_patterns.sort(
            key=lambda x: max([p.get('strength', 0) for p in x.get('patterns', [])] or [0]),
            reverse=True
        )
        
        return PatternsResponse(
            timestamp=datetime.now().isoformat(),
            total_with_patterns=len(companies_with_patterns),
            companies=companies_with_patterns
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Data file not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting patterns: {str(e)}")


@router.get("/technical/{symbol}", summary="Get technical analysis for symbol")
async def get_technical_analysis(symbol: str):
    """
    Get technical analysis for a specific company symbol
    
    - **symbol**: Company symbol (e.g., PKN, CDR)
    """
    try:
        data = data_loader.load_wig80_data()
        companies = data.get('companies', [])
        
        company = next(
            (c for c in companies if c.get('symbol', '').upper() == symbol.upper()),
            None
        )
        
        if not company:
            raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
        
        analysis = analysis_engine.generate_analysis(company)
        patterns = pattern_service.detect_patterns(company)
        insights = analysis_engine.generate_insights(
            company,
            analysis.overall_score,
            analysis.recommendation
        )
        
        return SingleAnalysisResponse(
            timestamp=datetime.now().isoformat(),
            analysis={
                "symbol": company.get('symbol', ''),
                "company_name": company.get('company_name', ''),
                "current_price": company.get('current_price', 0),
                "change_percent": company.get('change_percent', 0),
                "analysis": analysis.dict(),
                "patterns": patterns,
                "metrics": {
                    "pe_ratio": company.get('pe_ratio'),
                    "pb_ratio": company.get('pb_ratio'),
                    "volatility": round(abs(company.get('change_percent', 0)), 2),
                    "price_momentum": "up" if company.get('change_percent', 0) > 0 else "down"
                },
                "insights": insights
            }
        )
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Data file not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service="analysis-api"
    )


@router.get("/{symbol}", response_model=SingleAnalysisResponse, summary="Get full analysis for symbol")
async def get_analysis(symbol: str):
    """
    Get full analysis (including patterns) for a specific company symbol
    
    - **symbol**: Company symbol (e.g., PKN, CDR)
    """
    # Don't treat "health" as a symbol
    if symbol.lower() == "health":
        raise HTTPException(status_code=404, detail="Use /api/analysis/health endpoint")
    return await get_technical_analysis(symbol)

