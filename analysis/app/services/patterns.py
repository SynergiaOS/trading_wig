"""
Pattern detection service
Handles technical pattern detection using PatternDetector
"""

from typing import Dict, Any, List, Optional
import sys
import os
from pathlib import Path

# Add code directory to path for PatternDetector import
_code_dir = Path(__file__).parent.parent.parent.parent / "code"
if str(_code_dir) not in sys.path:
    sys.path.insert(0, str(_code_dir))


class PatternService:
    """Service for detecting technical patterns"""
    
    def __init__(self):
        self._pattern_detector = None
        self._load_pattern_detector()
    
    def _load_pattern_detector(self):
        """Lazy load PatternDetector"""
        try:
            from telegram_alerts import PatternDetector
            self._pattern_detector = PatternDetector()
        except ImportError as e:
            print(f"Warning: PatternDetector not available: {e}")
            self._pattern_detector = None
        except Exception as e:
            print(f"Warning: Error loading PatternDetector: {e}")
            self._pattern_detector = None
    
    def detect_patterns(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect technical patterns for a company
        
        Args:
            company: Company data dictionary
            
        Returns:
            List of detected patterns
        """
        if not self._pattern_detector:
            return []
        
        try:
            patterns = self._pattern_detector.detect_patterns(company)
            return patterns if patterns else []
        except Exception as e:
            print(f"Error detecting patterns for {company.get('symbol', 'unknown')}: {e}")
            return []


# Global instance
pattern_service = PatternService()

