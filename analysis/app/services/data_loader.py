"""
Data loader service for analysis API
Uses real-time data fetching from backend service or Stooq.pl
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


class DataLoader:
    """Service for loading market data with real-time support"""
    
    def __init__(self):
        self._base_dir = Path(__file__).parent.parent.parent.parent
        self._data_paths = [
            self._base_dir / "data" / "wig80_current_data.json",
            self._base_dir / "polish-finance-platform" / "polish-finance-app" / "public" / "wig80_current_data.json",
        ]
        # Try to use backend API first, fallback to direct Stooq or file
        self._backend_url = os.environ.get('BACKEND_API_URL', 'http://localhost:8000')
        self._use_backend_api = os.environ.get('USE_BACKEND_API', 'true').lower() == 'true'
    
    def _get_data_file(self) -> Optional[Path]:
        """Find the first available data file"""
        for path in self._data_paths:
            if path.exists():
                return path
        return None
    
    def _fetch_from_backend(self) -> Optional[Dict[str, Any]]:
        """Try to fetch data from backend API"""
        try:
            url = f"{self._backend_url}/data"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Analysis-API/1.0')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            logger.debug(f"Backend API not available: {e}")
            return None
    
    def _load_from_file(self) -> Dict[str, Any]:
        """Load data from JSON file (fallback)"""
        data_file = self._get_data_file()
        if not data_file:
            raise FileNotFoundError("WIG80 data file not found")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_wig80_data(self) -> Dict[str, Any]:
        """
        Load WIG80 data - tries backend API first, then file
        
        Returns:
            Market data dictionary
            
        Raises:
            FileNotFoundError: If all sources fail
        """
        # Try backend API first
        if self._use_backend_api:
            data = self._fetch_from_backend()
            if data:
                logger.debug("Loaded data from backend API")
                return data
        
        # Fallback to file
        try:
            data = self._load_from_file()
            logger.debug("Loaded data from file")
            return data
        except FileNotFoundError:
            raise FileNotFoundError("WIG80 data not available from backend API or file")


# Global instance
data_loader = DataLoader()
