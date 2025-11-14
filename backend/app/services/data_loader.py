"""
Data loader service for market data
Handles loading and caching of WIG80 data from real-time sources
"""

import json
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging
from .stooq_fetcher import stooq_fetcher

logger = logging.getLogger(__name__)


class DataLoader:
    """Service for loading market data with caching and real-time fetching"""
    
    def __init__(self):
        self._base_dir = Path(__file__).parent.parent.parent.parent
        self._possible_paths = [
            self._base_dir / "polish-finance-platform" / "polish-finance-app" / "public" / "wig80_current_data.json",
            self._base_dir / "data" / "wig80_current_data.json",
            self._base_dir / "polish-finance-platform" / "polish-finance-app" / "dist" / "wig80_current_data.json",
        ]
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(seconds=30)  # Cache for 30 seconds
        self._use_realtime = os.environ.get('USE_REALTIME_API', 'true').lower() == 'true'
    
    def _get_data_file(self) -> Optional[Path]:
        """Find the first available data file"""
        for path in self._possible_paths:
            if path.exists():
                return path
        return None
    
    def _load_from_file(self) -> Dict[str, Any]:
        """Load data from JSON file (fallback)"""
        data_file = self._get_data_file()
        if not data_file:
            raise FileNotFoundError("WIG80 data file not found")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _fetch_realtime_data(self) -> Dict[str, Any]:
        """Fetch real-time data from Stooq.pl"""
        try:
            logger.info("Fetching real-time data from Stooq.pl...")
            companies_data = stooq_fetcher.fetch_all_companies()
            
            successful = sum(1 for c in companies_data if c.get('status') == 'success')
            
            return {
                "metadata": {
                    "collection_date": datetime.now().isoformat(),
                    "data_source": "stooq.pl (real-time)",
                    "index": "WIG80",
                    "currency": "PLN",
                    "total_companies": len(companies_data),
                    "successful_fetches": successful
                },
                "companies": companies_data
            }
        except Exception as e:
            logger.error(f"Error fetching real-time data: {e}")
            raise
    
    def get_data(self, use_cache: bool = True, force_realtime: bool = False) -> Dict[str, Any]:
        """
        Get market data with optional caching and real-time fetching
        
        Args:
            use_cache: Whether to use cached data if available
            force_realtime: Force real-time fetch even if cache is valid
            
        Returns:
            Market data dictionary
        """
        # Check cache (unless forcing realtime)
        if not force_realtime and use_cache and self._cache and self._cache_timestamp:
            if datetime.now() - self._cache_timestamp < self._cache_ttl:
                logger.debug("Returning cached data")
                return self._cache
        
        # Try to fetch real-time data
        if self._use_realtime:
            try:
                data = self._fetch_realtime_data()
                # Update cache
                self._cache = data
                self._cache_timestamp = datetime.now()
                logger.info("Successfully fetched real-time data from Stooq.pl")
                return data
            except Exception as e:
                logger.warning(f"Real-time fetch failed: {e}, falling back to file")
                # Fallback to file if real-time fails
                try:
                    data = self._load_from_file()
                    # Update cache
                    self._cache = data
                    self._cache_timestamp = datetime.now()
                    logger.info("Using fallback data from file")
                    return data
                except FileNotFoundError:
                    raise Exception("Both real-time fetch and file fallback failed")
        else:
            # Use file-based approach
            data = self._load_from_file()
            # Update cache
            self._cache = data
            self._cache_timestamp = datetime.now()
            return data
    
    def get_wig30_data(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get WIG30 data (top 30 companies by volume)
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            WIG30 data dictionary
        """
        data = self.get_data(use_cache)
        companies = data.get('companies', [])
        
        def get_volume_num(vol_str: str) -> float:
            """Convert volume string to number"""
            try:
                vol = str(vol_str).replace('K', '').replace('M', '').replace(',', '').replace(' ', '')
                num = float(vol)
                if 'M' in str(vol_str):
                    num *= 1000
                return num
            except:
                return 0.0
        
        # Sort by volume and take top 30
        sorted_companies = sorted(
            companies,
            key=lambda x: get_volume_num(x.get('trading_volume', '0')),
            reverse=True
        )
        top_30 = sorted_companies[:30]
        
        return {
            'metadata': {
                **data['metadata'],
                'index': 'WIG30',
                'total_companies': 30
            },
            'companies': top_30
        }
    
    def clear_cache(self):
        """Clear the data cache"""
        self._cache = None
        self._cache_timestamp = None


# Global instance
data_loader = DataLoader()

