#!/usr/bin/env python3
"""
Real-Time WIG80 Data Fetcher Service
Continuously fetches live data from Stooq.pl and updates JSON file
Runs as background service to provide real-time data to frontend
"""

import json
import time
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional
import sys
import os

class RealTimeWIG80Fetcher:
    def __init__(self, output_file: str):
        self.output_file = output_file
        
        # All 88 WIG80 companies
        self.companies = [
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
        
        print(f"Initialized Real-Time WIG80 Fetcher")
        print(f"Output file: {self.output_file}")
        print(f"Companies to track: {len(self.companies)}")
    
    def fetch_stooq_data(self, symbol: str) -> Optional[Dict]:
        """Fetch real-time data from Stooq.pl for a single company"""
        try:
            import urllib.request
            import urllib.error
            
            url = f"https://stooq.pl/q/?s={symbol}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # Extract price, change, volume using regex
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
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def _extract_price(self, html: str) -> float:
        """Extract current price from HTML"""
        patterns = [
            r'id="aq_[^"]*_c[^>]*>([0-9,\.]+)<',
            r'Kurs:\s*([0-9,\.]+)',
            r'class="[^"]*price[^"]*"[^>]*>([0-9,\.]+)<'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', '.'))
        
        return 0.0
    
    def _extract_change(self, html: str) -> float:
        """Extract change percentage from HTML"""
        patterns = [
            r'id="aq_[^"]*_p[^>]*>([+-]?[0-9,\.]+)%?<',
            r'Zmiana:\s*([+-]?[0-9,\.]+)%'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', '.'))
        
        return 0.0
    
    def _extract_volume(self, html: str) -> int:
        """Extract volume from HTML"""
        patterns = [
            r'Wolumen:\s*([0-9\s]+)',
            r'<td[^>]*>Wolumen</td>\s*<td[^>]*>([0-9\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                vol_str = match.group(1).replace(' ', '').replace('\xa0', '')
                try:
                    return int(vol_str)
                except:
                    pass
        
        return 0
    
    def _extract_pe(self, html: str) -> Optional[float]:
        """Extract P/E ratio from HTML"""
        patterns = [
            r'C/Z:\s*([0-9,\.]+)',
            r'<td[^>]*>C/Z</td>\s*<td[^>]*>([0-9,\.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', '.'))
                except:
                    pass
        
        return None
    
    def _extract_pb(self, html: str) -> Optional[float]:
        """Extract P/B ratio from HTML"""
        patterns = [
            r'C/WK:\s*([0-9,\.]+)',
            r'<td[^>]*>C/WK</td>\s*<td[^>]*>([0-9,\.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', '.'))
                except:
                    pass
        
        return None
    
    def _format_volume(self, volume: int) -> str:
        """Format volume for display"""
        if volume >= 1000000:
            return f"{volume / 1000000:.2f}M"
        elif volume >= 1000:
            return f"{volume / 1000:.2f}K"
        return str(volume)
    
    def fetch_all_companies(self) -> List[Dict]:
        """Fetch data for all companies"""
        results = []
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching data for {len(self.companies)} companies...")
        
        for i, company in enumerate(self.companies):
            print(f"  [{i+1}/{len(self.companies)}] Fetching {company['symbol']}...", end='', flush=True)
            
            data = self.fetch_stooq_data(company['symbol'])
            
            if data:
                company_data = {
                    'company_name': company['name'],
                    'symbol': company['symbol'],
                    **data
                }
                results.append(company_data)
                print(f" OK (Price: {data['current_price']:.2f} PLN, Change: {data['change_percent']:+.2f}%)")
            else:
                # Use placeholder if fetch fails
                company_data = {
                    'company_name': company['name'],
                    'symbol': company['symbol'],
                    'current_price': 0,
                    'change_percent': 0,
                    'pe_ratio': None,
                    'pb_ratio': None,
                    'trading_volume': "0",
                    'trading_volume_obrot': "0 PLN",
                    'last_update': datetime.now().strftime("%H:%M:%S"),
                    'status': 'error'
                }
                results.append(company_data)
                print(" FAILED")
            
            # Small delay to avoid overwhelming Stooq
            if i < len(self.companies) - 1:
                time.sleep(0.5)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"\nFetch complete: {success_count}/{len(self.companies)} successful")
        
        return results
    
    def save_data(self, companies_data: List[Dict]):
        """Save data to JSON file"""
        output = {
            "metadata": {
                "collection_date": datetime.now().isoformat(),
                "data_source": "stooq.pl (live)",
                "index": "WIG80 (sWIG80)",
                "currency": "PLN",
                "total_companies": len(companies_data),
                "successful_fetches": sum(1 for c in companies_data if c['status'] == 'success')
            },
            "companies": companies_data
        }
        
        # Write to file atomically
        temp_file = f"{self.output_file}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        # Atomic rename
        os.replace(temp_file, self.output_file)
        
        print(f"Data saved to {self.output_file}")
    
    def run_once(self):
        """Fetch and save data once"""
        companies_data = self.fetch_all_companies()
        self.save_data(companies_data)
    
    def run_continuous(self, interval_seconds: int = 30):
        """Run continuously, updating data at regular intervals"""
        print(f"\n{'='*60}")
        print(f"Real-Time WIG80 Data Service Started")
        print(f"Update interval: {interval_seconds} seconds")
        print(f"Output file: {self.output_file}")
        print(f"{'='*60}\n")
        
        iteration = 0
        while True:
            try:
                iteration += 1
                print(f"\n{'='*60}")
                print(f"Update #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*60}")
                
                companies_data = self.fetch_all_companies()
                self.save_data(companies_data)
                
                print(f"\nNext update in {interval_seconds} seconds...")
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n\nService stopped by user")
                break
            except Exception as e:
                print(f"\nError in main loop: {e}")
                print(f"Retrying in {interval_seconds} seconds...")
                time.sleep(interval_seconds)

def main():
    output_file = "/workspace/polish-finance-platform/polish-finance-app/public/wig80_current_data.json"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    fetcher = RealTimeWIG80Fetcher(output_file)
    
    # Check if running once or continuously
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        print("Running single fetch...")
        fetcher.run_once()
    else:
        # Run continuously with 30-second updates
        fetcher.run_continuous(interval_seconds=30)

if __name__ == "__main__":
    main()
