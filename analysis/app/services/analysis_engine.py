"""
Analysis engine service
Generates company analysis scores and recommendations
"""

from typing import Dict, Any, List
from ..models.analysis import CompanyAnalysisModel


class AnalysisEngine:
    """Service for generating company analysis"""
    
    @staticmethod
    def generate_analysis(company: Dict[str, Any]) -> CompanyAnalysisModel:
        """
        Generate analysis for a single company
        
        Args:
            company: Company data dictionary
            
        Returns:
            CompanyAnalysisModel with analysis scores
        """
        change = company.get('change_percent', 0)
        pe = company.get('pe_ratio')
        pb = company.get('pb_ratio')
        
        # Calculate scores
        value_score = 0.0
        growth_score = 0.0
        momentum_score = 0.0
        
        # Value analysis
        if pe and pe > 0:
            if pe < 15:
                value_score += 30
            elif pe < 25:
                value_score += 20
            else:
                value_score += 10
        
        if pb and pb > 0:
            if pb < 1.5:
                value_score += 30
            elif pb < 2.5:
                value_score += 20
            else:
                value_score += 10
        
        # Growth analysis
        if change > 5:
            growth_score = 40
        elif change > 2:
            growth_score = 30
        elif change > 0:
            growth_score = 20
        elif change > -2:
            growth_score = 10
        else:
            growth_score = 0
        
        # Momentum analysis
        if change > 3:
            momentum_score = 30
        elif change > 1:
            momentum_score = 20
        elif change > -1:
            momentum_score = 10
        else:
            momentum_score = 0
        
        overall_score = (value_score + growth_score + momentum_score) / 3
        
        # Generate recommendation
        if overall_score >= 70:
            recommendation = "STRONG_BUY"
            sentiment = "very_bullish"
        elif overall_score >= 55:
            recommendation = "BUY"
            sentiment = "bullish"
        elif overall_score >= 40:
            recommendation = "HOLD"
            sentiment = "neutral"
        elif overall_score >= 25:
            recommendation = "SELL"
            sentiment = "bearish"
        else:
            recommendation = "STRONG_SELL"
            sentiment = "very_bearish"
        
        # Risk assessment
        volatility = abs(change)
        if volatility < 2:
            risk_level = "low"
        elif volatility < 5:
            risk_level = "medium"
        elif volatility < 10:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        return CompanyAnalysisModel(
            value_score=round(value_score, 1),
            growth_score=round(growth_score, 1),
            momentum_score=round(momentum_score, 1),
            overall_score=round(overall_score, 1),
            recommendation=recommendation,
            sentiment=sentiment,
            risk_level=risk_level,
            confidence=min(95, max(60, overall_score + 20))
        )
    
    @staticmethod
    def generate_insights(company: Dict[str, Any], score: float, recommendation: str) -> List[str]:
        """
        Generate human-readable insights
        
        Args:
            company: Company data dictionary
            score: Overall analysis score
            recommendation: Recommendation string
            
        Returns:
            List of insight strings
        """
        insights = []
        change = company.get('change_percent', 0)
        pe = company.get('pe_ratio')
        pb = company.get('pb_ratio')
        
        if change > 5:
            insights.append(f"Silny wzrost o {change:.2f}% - pozytywny momentum")
        elif change > 2:
            insights.append(f"Umiarkowany wzrost o {change:.2f}%")
        elif change < -5:
            insights.append(f"Znaczny spadek o {abs(change):.2f}% - wymaga uwagi")
        
        if pe and pe < 15:
            insights.append("Niska wycena P/E - potencjalna okazja wartościowa")
        elif pe and pe > 30:
            insights.append("Wysoka wycena P/E - możliwe przeszacowanie")
        
        if pb and pb < 1.5:
            insights.append("Niski wskaźnik P/B - atrakcyjna wycena")
        
        if score >= 70:
            insights.append("Wysoki ogólny wynik - silna rekomendacja kupna")
        elif score < 30:
            insights.append("Niski ogólny wynik - rozważ sprzedaż")
        
        return insights


# Global instance
analysis_engine = AnalysisEngine()

