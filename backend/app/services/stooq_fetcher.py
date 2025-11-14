"""
Stooq.pl Data Fetcher Service
Fetches real-time market data from Stooq.pl API
"""

import urllib.request
import urllib.error
import re
from typing import Dict, List, Optional
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)


class StooqFetcher:
    """Service for fetching real-time data from Stooq.pl"""
    
    # All 88 WIG80 companies (exact list from realtime_wig80_fetcher.py)
    WIG80_COMPANIES = [
        {"name": "AGORA SA", "symbol": "AGO"},
        {"name": "Polimex-Mostostal", "symbol": "PXM"},
        {"name": "Bioton SA", "symbol": "BIO"},
        {"name": "Echo Investment SA", "symbol": "ECH"},
        {"name": "Asseco Business Solutions", "symbol": "ABS"},
        {"name": "AC SA", "symbol": "ACS"},
        {"name": "Ambra SA", "symbol": "AMB"},
        {"name": "AMICA Wronki SA", "symbol": "AMC"},
        {"name": "Apator SA", "symbol": "APT"},
        {"name": "Astarta Holding NV", "symbol": "AST"},
        {"name": "Arctic Paper SA", "symbol": "APC"},
        {"name": "Bumech SA", "symbol": "BUM"},
        {"name": "Boryszew SA", "symbol": "BRS"},
        {"name": "Bank Ochrony Środowiska", "symbol": "BOS"},
        {"name": "CI Games", "symbol": "CIG"},
        {"name": "Comp SA", "symbol": "CMP"},
        {"name": "Cognor SA", "symbol": "COG"},
        {"name": "Decora SA", "symbol": "DEC"},
        {"name": "Elektrotim SA", "symbol": "ELT"},
        {"name": "Erbud SA", "symbol": "ERB"},
        {"name": "Grenevia", "symbol": "GRN"},
        {"name": "Ferro SA", "symbol": "FRO"},
        {"name": "FORTE SA", "symbol": "FTE"},
        {"name": "Kogeneracja SA", "symbol": "KOG"},
        {"name": "Lubelski Wegiel Bogdanka", "symbol": "LWB"},
        {"name": "MCI Management SA", "symbol": "MCI"},
        {"name": "Mercor SA", "symbol": "MCR"},
        {"name": "Mennica Polska SA", "symbol": "MPS"},
        {"name": "Mostostal Zabrze", "symbol": "MSZ"},
        {"name": "Quercus TFI SA", "symbol": "QRS"},
        {"name": "Rank Progress SA", "symbol": "RPG"},
        {"name": "Selena FM SA", "symbol": "SLN"},
        {"name": "Sygnity SA", "symbol": "SGN"},
        {"name": "ŚNIEŻKA SA", "symbol": "SNZ"},
        {"name": "Stomil Sanok SA", "symbol": "STS"},
        {"name": "Stalprodukt SA", "symbol": "STP"},
        {"name": "Stalexport Autostrady", "symbol": "STE"},
        {"name": "Toya SA", "symbol": "TOY"},
        {"name": "Unibep SA", "symbol": "UNB"},
        {"name": "Votum SA", "symbol": "VOT"},
        {"name": "VRG", "symbol": "VRG"},
        {"name": "Wielton SA", "symbol": "WLT"},
        {"name": "WAWEL SA", "symbol": "WWL"},
        {"name": "Zespol Elektrowni Patnow Adamow Konin", "symbol": "ZEPA"},
        {"name": "Oponeo.pl SA", "symbol": "OPN"},
        {"name": "Mabion", "symbol": "MAB"},
        {"name": "Tarczynski", "symbol": "TRZ"},
        {"name": "Bloober", "symbol": "BLB"},
        {"name": "Synthaverse", "symbol": "SNV"},
        {"name": "Medicalg", "symbol": "MDG"},
        {"name": "Datawalk", "symbol": "DAT"},
        {"name": "Ryvu", "symbol": "RYV"},
        {"name": "Ailleron", "symbol": "ALL"},
        {"name": "Mercator WA", "symbol": "MRC"},
        {"name": "Torpol", "symbol": "TOR"},
        {"name": "Columbus", "symbol": "COL"},
        {"name": "PCC Rokita", "symbol": "PCC"},
        {"name": "Unimot", "symbol": "UNM"},
        {"name": "Vigo System", "symbol": "VGS"},
        {"name": "Atal SA", "symbol": "1AT"},
        {"name": "Poznanska Korporacja Budowlana Peka", "symbol": "PKB"},
        {"name": "Wittchen SA", "symbol": "WTC"},
        {"name": "Enter Air", "symbol": "ENT"},
        {"name": "Archicom SA", "symbol": "ARC"},
        {"name": "GreenX Metals", "symbol": "GRX"},
        {"name": "Playway", "symbol": "PLW"},
        {"name": "Celon Pharma", "symbol": "CLP"},
        {"name": "Scope Fluidics", "symbol": "SCF"},
        {"name": "XTPL", "symbol": "XTPL"},
        {"name": "Molecure", "symbol": "MOL"},
        {"name": "ML System", "symbol": "MLS"},
        {"name": "Creepy Jar", "symbol": "CRJ"},
        {"name": "Selvita", "symbol": "SLV"},
        {"name": "Dadelo", "symbol": "DDL"},
        {"name": "Captor Therapeutics", "symbol": "CPT"},
        {"name": "Shoper", "symbol": "SHP"},
        {"name": "Onde", "symbol": "OND"},
        {"name": "Creotech Instruments", "symbol": "CRT"},
        {"name": "Bioceltix", "symbol": "BCX"},
        {"name": "Murapol", "symbol": "MRP"},
        {"name": "Benefit Systems", "symbol": "BFT"},
        {"name": "Alumetal", "symbol": "AML"},
        {"name": "Newag", "symbol": "NWG"},
        {"name": "Braster", "symbol": "BRA"},
        {"name": "PKN Orlen", "symbol": "PKN"},
        {"name": "XTB", "symbol": "XTB"},
        {"name": "Mirbud", "symbol": "MIR"},
        {"name": "LiveChat", "symbol": "LVC"}
    ]
    
    def __init__(self):
        self.base_url = "https://stooq.pl"
        self.timeout = 10
        self.request_delay = 0.3  # Delay between requests to avoid rate limiting
    
    def fetch_company_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch real-time data from Stooq.pl for a single company
        
        Args:
            symbol: Company stock symbol (e.g., "PKN", "CDR")
            
        Returns:
            Dictionary with company data or None if failed
        """
        try:
            url = f"{self.base_url}/q/?s={symbol}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # Extract data using regex patterns
            price = self._extract_price(html)
            change = self._extract_change(html)
            volume = self._extract_volume(html)
            pe_ratio = self._extract_pe(html)
            pb_ratio = self._extract_pb(html)
            
            if price > 0:
                return {
                    'current_price': price,
                    'change_percent': change,
                    'pe_ratio': pe_ratio,
                    'pb_ratio': pb_ratio,
                    'trading_volume': self._format_volume(volume),
                    'trading_volume_obrot': f"{(volume * price / 1000000):.2f}M PLN" if volume > 0 else "0 PLN",
                    'last_update': datetime.now().strftime("%H:%M:%S"),
                    'status': 'success'
                }
            
            return None
            
        except urllib.error.URLError as e:
            logger.warning(f"Network error fetching {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None
    
    def _extract_price(self, html: str) -> float:
        """Extract current price from HTML"""
        patterns = [
            r'id="aq_[^"]*_c[^>]*>([0-9,\.]+)<',
            r'Kurs:\s*([0-9,\.]+)',
            r'class="[^"]*price[^"]*"[^>]*>([0-9,\.]+)<',
            r'<span[^>]*class="[^"]*price[^"]*"[^>]*>([0-9,\.]+)</span>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', '.').replace(' ', ''))
                except ValueError:
                    continue
        
        return 0.0
    
    def _extract_change(self, html: str) -> float:
        """Extract change percentage from HTML"""
        patterns = [
            r'id="aq_[^"]*_p[^>]*>([+-]?[0-9,\.]+)%?<',
            r'Zmiana:\s*([+-]?[0-9,\.]+)%',
            r'<span[^>]*class="[^"]*change[^"]*"[^>]*>([+-]?[0-9,\.]+)%?</span>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', '.').replace(' ', ''))
                except ValueError:
                    continue
        
        return 0.0
    
    def _extract_volume(self, html: str) -> int:
        """Extract volume from HTML"""
        patterns = [
            r'Wolumen:\s*([0-9\s]+)',
            r'<td[^>]*>Wolumen</td>\s*<td[^>]*>([0-9\s]+)',
            r'id="aq_[^"]*_v[^>]*>([0-9\s]+)<'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                vol_str = match.group(1).replace(' ', '').replace('\xa0', '').replace(',', '')
                try:
                    return int(vol_str)
                except ValueError:
                    continue
        
        return 0
    
    def _extract_pe(self, html: str) -> Optional[float]:
        """Extract P/E ratio from HTML"""
        patterns = [
            r'P/E[:\s]*([0-9,\.]+)',
            r'<td[^>]*>P/E</td>\s*<td[^>]*>([0-9,\.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', '.'))
                except ValueError:
                    continue
        
        return None
    
    def _extract_pb(self, html: str) -> Optional[float]:
        """Extract P/B ratio from HTML"""
        patterns = [
            r'P/B[:\s]*([0-9,\.]+)',
            r'<td[^>]*>P/B</td>\s*<td[^>]*>([0-9,\.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', '.'))
                except ValueError:
                    continue
        
        return None
    
    def _format_volume(self, volume: int) -> str:
        """Format volume as string (K, M)"""
        if volume >= 1000000:
            return f"{volume / 1000000:.2f}M"
        elif volume >= 1000:
            return f"{volume / 1000:.2f}K"
        return str(volume)
    
    def fetch_all_companies(self, max_workers: int = 5) -> List[Dict]:
        """
        Fetch data for all WIG80 companies
        
        Args:
            max_workers: Maximum concurrent requests (not used in sync version)
            
        Returns:
            List of company data dictionaries
        """
        results = []
        total = len(self.WIG80_COMPANIES)
        
        logger.info(f"Fetching data for {total} companies from Stooq.pl...")
        
        for i, company in enumerate(self.WIG80_COMPANIES):
            symbol = company['symbol']
            name = company['name']
            
            try:
                data = self.fetch_company_data(symbol)
                
                if data:
                    company_data = {
                        'company_name': name,
                        'symbol': symbol,
                        **data
                    }
                    results.append(company_data)
                    logger.debug(f"[{i+1}/{total}] {symbol}: OK (Price: {data['current_price']:.2f} PLN)")
                else:
                    # Use placeholder if fetch fails
                    company_data = {
                        'company_name': name,
                        'symbol': symbol,
                        'current_price': 0,
                        'change_percent': 0,
                        'pe_ratio': None,
                        'pb_ratio': None,
                        'trading_volume': '0',
                        'trading_volume_obrot': '0 PLN',
                        'last_update': datetime.now().strftime("%H:%M:%S"),
                        'status': 'error'
                    }
                    results.append(company_data)
                    logger.warning(f"[{i+1}/{total}] {symbol}: FAILED")
                
                # Small delay to avoid overwhelming Stooq
                if i < total - 1:
                    time.sleep(self.request_delay)
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                # Add error entry
                results.append({
                    'company_name': name,
                    'symbol': symbol,
                    'current_price': 0,
                    'change_percent': 0,
                    'pe_ratio': None,
                    'pb_ratio': None,
                    'trading_volume': '0',
                    'trading_volume_obrot': '0 PLN',
                    'last_update': datetime.now().strftime("%H:%M:%S"),
                    'status': 'error'
                })
        
        success_count = sum(1 for r in results if r.get('status') == 'success')
        logger.info(f"Fetch complete: {success_count}/{total} successful")
        
        return results


# Global instance
stooq_fetcher = StooqFetcher()

