#!/usr/bin/env python3
"""
WIG80 Companies Data Scraper for Stooq.pl
Extracts current stock prices, P/E ratios, P/B ratios, trading volumes, and company info
"""

import json
import time
import re
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup

class WIG80Scraper:
    def __init__(self):
        self.base_url = "https://stooq.pl"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # WIG80 Companies list from Investing.com extraction
        self.wig80_companies = {
            "AGORA SA": {"symbol": "AGO", "price_data": None, "pe_data": None, "pb_data": None},
            "Polimex-Mostostal": {"symbol": "PXM", "price_data": None, "pe_data": None, "pb_data": None},
            "Bioton SA": {"symbol": "BIO", "price_data": None, "pe_data": None, "pb_data": None},
            "Echo Investment SA": {"symbol": "ECH", "price_data": None, "pe_data": None, "pb_data": None},
            "Asseco Business Solutions": {"symbol": "ABS", "price_data": None, "pe_data": None, "pb_data": None},
            "AC SA": {"symbol": "ACS", "price_data": None, "pe_data": None, "pb_data": None},
            "Ambra SA": {"symbol": "AMB", "price_data": None, "pe_data": None, "pb_data": None},
            "AMICA Wronki SA": {"symbol": "AMC", "price_data": None, "pe_data": None, "pb_data": None},
            "Apator SA": {"symbol": "APT", "price_data": None, "pe_data": None, "pb_data": None},
            "Astarta Holding NV": {"symbol": "AST", "price_data": None, "pe_data": None, "pb_data": None},
            "Arctic Paper SA": {"symbol": "APC", "price_data": None, "pe_data": None, "pb_data": None},
            "Bumech SA": {"symbol": "BUM", "price_data": None, "pe_data": None, "pb_data": None},
            "Boryszew SA": {"symbol": "BRS", "price_data": None, "pe_data": None, "pb_data": None},
            "Bank Ochrony Środowiska": {"symbol": "BOS", "price_data": None, "pe_data": None, "pb_data": None},
            "CI Games": {"symbol": "CIG", "price_data": None, "pe_data": None, "pb_data": None},
            "Comp SA": {"symbol": "CMP", "price_data": None, "pe_data": None, "pb_data": None},
            "Cognor SA": {"symbol": "COG", "price_data": None, "pe_data": None, "pb_data": None},
            "Decora SA": {"symbol": "DEC", "price_data": None, "pe_data": None, "pb_data": None},
            "Elektrotim SA": {"symbol": "ELT", "price_data": None, "pe_data": None, "pb_data": None},
            "Erbud SA": {"symbol": "ERB", "price_data": None, "pe_data": None, "pb_data": None},
            "Grenevia": {"symbol": "GRN", "price_data": None, "pe_data": None, "pb_data": None},
            "Ferro SA": {"symbol": "FRO", "price_data": None, "pe_data": None, "pb_data": None},
            "FORTE SA": {"symbol": "FTE", "price_data": None, "pe_data": None, "pb_data": None},
            "Kogeneracja SA": {"symbol": "KOG", "price_data": None, "pe_data": None, "pb_data": None},
            "Lubelski Wegiel Bogdanka": {"symbol": "LWB", "price_data": None, "pe_data": None, "pb_data": None},
            "MCI Management SA": {"symbol": "MCI", "price_data": None, "pe_data": None, "pb_data": None},
            "Mercor SA": {"symbol": "MCR", "price_data": None, "pe_data": None, "pb_data": None},
            "Mennica Polska SA": {"symbol": "MPS", "price_data": None, "pe_data": None, "pb_data": None},
            "Mostostal Zabrze": {"symbol": "MSZ", "price_data": None, "pe_data": None, "pb_data": None},
            "Quercus TFI SA": {"symbol": "QRS", "price_data": None, "pe_data": None, "pb_data": None},
            "Rank Progress SA": {"symbol": "RPG", "price_data": None, "pe_data": None, "pb_data": None},
            "Selena FM SA": {"symbol": "SLN", "price_data": None, "pe_data": None, "pb_data": None},
            "Sygnity SA": {"symbol": "SGN", "price_data": None, "pe_data": None, "pb_data": None},
            "ŚNIEŻKA SA": {"symbol": "SNZ", "price_data": None, "pe_data": None, "pb_data": None},
            "Stomil Sanok SA": {"symbol": "STS", "price_data": None, "pe_data": None, "pb_data": None},
            "Stalprodukt SA": {"symbol": "STP", "price_data": None, "pe_data": None, "pb_data": None},
            "Stalexport Autostrady": {"symbol": "STE", "price_data": None, "pe_data": None, "pb_data": None},
            "Toya SA": {"symbol": "TOY", "price_data": None, "pe_data": None, "pb_data": None},
            "Unibep SA": {"symbol": "UNB", "price_data": None, "pe_data": None, "pb_data": None},
            "Votum SA": {"symbol": "VOT", "price_data": None, "pe_data": None, "pb_data": None},
            "VRG": {"symbol": "VRG", "price_data": None, "pe_data": None, "pb_data": None},
            "Wielton SA": {"symbol": "WLT", "price_data": None, "pe_data": None, "pb_data": None},
            "WAWEL SA": {"symbol": "WWL", "price_data": None, "pe_data": None, "pb_data": None},
            "Zespol Elektrowni Patnow Adamow Konin": {"symbol": "ZEPA", "price_data": None, "pe_data": None, "pb_data": None},
            "Oponeo.pl SA": {"symbol": "OPN", "price_data": None, "pe_data": None, "pb_data": None},
            "Mabion": {"symbol": "MAB", "price_data": None, "pe_data": None, "pb_data": None},
            "Tarczynski": {"symbol": "TRZ", "price_data": None, "pe_data": None, "pb_data": None},
            "Bloober": {"symbol": "BLB", "price_data": None, "pe_data": None, "pb_data": None},
            "Synthaverse": {"symbol": "SNV", "price_data": None, "pe_data": None, "pb_data": None},
            "Medicalg": {"symbol": "MDG", "price_data": None, "pe_data": None, "pb_data": None},
            "Datawalk": {"symbol": "DAT", "price_data": None, "pe_data": None, "pb_data": None},
            "Ryvu": {"symbol": "RYV", "price_data": None, "pe_data": None, "pb_data": None},
            "Ailleron": {"symbol": "ALL", "price_data": None, "pe_data": None, "pb_data": None},
            "Mercator WA": {"symbol": "MRC", "price_data": None, "pe_data": None, "pb_data": None},
            "Torpol": {"symbol": "TOR", "price_data": None, "pe_data": None, "pb_data": None},
            "Columbus": {"symbol": "COL", "price_data": None, "pe_data": None, "pb_data": None},
            "PCC Rokita": {"symbol": "PCC", "price_data": None, "pe_data": None, "pb_data": None},
            "Unimot": {"symbol": "UNM", "price_data": None, "pe_data": None, "pb_data": None},
            "Vigo System": {"symbol": "VGS", "price_data": None, "pe_data": None, "pb_data": None},
            "Atal SA": {"symbol": "1AT", "price_data": None, "pe_data": None, "pb_data": None},
            "Poznanska Korporacja Budowlana Peka": {"symbol": "PKB", "price_data": None, "pe_data": None, "pb_data": None},
            "Wittchen SA": {"symbol": "WTC", "price_data": None, "pe_data": None, "pb_data": None},
            "Enter Air": {"symbol": "ENT", "price_data": None, "pe_data": None, "pb_data": None},
            "Archicom SA": {"symbol": "ARC", "price_data": None, "pe_data": None, "pb_data": None},
            "GreenX Metals": {"symbol": "GRX", "price_data": None, "pe_data": None, "pb_data": None},
            "Playway": {"symbol": "PLW", "price_data": None, "pe_data": None, "pb_data": None},
            "Celon Pharma": {"symbol": "CLP", "price_data": None, "pe_data": None, "pb_data": None},
            "Scope Fluidics": {"symbol": "SCF", "price_data": None, "pe_data": None, "pb_data": None},
            "XTPL": {"symbol": "XTPL", "price_data": None, "pe_data": None, "pb_data": None},
            "Molecure": {"symbol": "MOL", "price_data": None, "pe_data": None, "pb_data": None},
            "ML System": {"symbol": "MLS", "price_data": None, "pe_data": None, "pb_data": None},
            "Creepy Jar": {"symbol": "CRJ", "price_data": None, "pe_data": None, "pb_data": None},
            "Selvita": {"symbol": "SLV", "price_data": None, "pe_data": None, "pb_data": None},
            "Dadelo": {"symbol": "DDL", "price_data": None, "pe_data": None, "pb_data": None},
            "Captor Therapeutics": {"symbol": "CPT", "price_data": None, "pe_data": None, "pb_data": None},
            "Shoper": {"symbol": "SHP", "price_data": None, "pe_data": None, "pb_data": None},
            "Onde": {"symbol": "OND", "price_data": None, "pe_data": None, "pb_data": None},
            "Creotech Instruments": {"symbol": "CRT", "price_data": None, "pe_data": None, "pb_data": None},
            "Bioceltix": {"symbol": "BCX", "price_data": None, "pe_data": None, "pb_data": None},
            "Murapol": {"symbol": "MRP", "price_data": None, "pe_data": None, "pb_data": None}
        }
    
    def parse_volume(self, volume_str: str) -> Optional[int]:
        """Parse volume string like '1.37K', '866.95K', '11.9K', '1.59M' to integer"""
        if not volume_str or volume_str == '-':
            return None
        
        volume_str = volume_str.upper().replace(',', '').replace(' ', '')
        
        # Handle K (thousands) and M (millions)
        if volume_str.endswith('K'):
            return int(float(volume_str[:-1]) * 1000)
        elif volume_str.endswith('M'):
            return int(float(volume_str[:-1]) * 1000000)
        else:
            try:
                return int(float(volume_str))
            except ValueError:
                return None
    
    def extract_stock_data(self, symbol: str) -> Dict:
        """Extract current stock data for a given symbol"""
        data = {
            "symbol": symbol,
            "price": None,
            "change_percent": None,
            "volume": None,
            "volume_obrot": None,  # Trading volume in PLN (OBROT)
            "pe_ratio": None,
            "pb_ratio": None,
            "last_update": None,
            "status": "success"
        }
        
        try:
            # Extract current price and volume
            price_url = f"{self.base_url}/q/?s={symbol.lower()}"
            price_response = self.session.get(price_url)
            price_soup = BeautifulSoup(price_response.content, 'html.parser')
            
            # Extract price information
            price_element = price_soup.find('span', {'id': 'Last'})
            if price_element:
                data["price"] = float(price_element.get_text().replace(',', '.'))
            
            # Extract volume (Wolumen)
            volume_elements = price_soup.find_all(text=re.compile(r'Wolumen', re.I))
            if volume_elements:
                for elem in volume_elements:
                    parent = elem.parent
                    if parent:
                        volume_value = parent.get_text()
                        # Extract numeric value from volume text
                        vol_match = re.search(r'(\d+\.?\d*)\s*([kKmM]?)', volume_value)
                        if vol_match:
                            value = float(vol_match.group(1))
                            unit = vol_match.group(2).upper()
                            if unit == 'K':
                                value *= 1000
                            elif unit == 'M':
                                value *= 1000000
                            data["volume"] = int(value)
                            break
            
            # Extract change percentage
            change_elements = price_soup.find_all('span', {'class': re.compile(r'.*Change.*')})
            for elem in change_elements:
                change_text = elem.get_text()
                if '%' in change_text:
                    change_match = re.search(r'([+-]?\d+\.?\d*)%', change_text)
                    if change_match:
                        data["change_percent"] = float(change_match.group(1))
                        break
            
            # Extract P/E ratio
            try:
                pe_url = f"{self.base_url}/q/?s={symbol.lower()}_pe"
                pe_response = self.session.get(pe_url)
                if pe_response.status_code == 200:
                    pe_soup = BeautifulSoup(pe_response.content, 'html.parser')
                    pe_element = pe_soup.find('span', {'id': 'Last'})
                    if pe_element:
                        pe_text = pe_element.get_text().replace(',', '.')
                        try:
                            data["pe_ratio"] = float(pe_text)
                        except ValueError:
                            pass
            except Exception as e:
                print(f"Error extracting P/E for {symbol}: {e}")
            
            # Extract P/B ratio
            try:
                pb_url = f"{self.base_url}/q/?s={symbol.lower()}_pb"
                pb_response = self.session.get(pb_url)
                if pb_response.status_code == 200:
                    pb_soup = BeautifulSoup(pb_response.content, 'html.parser')
                    pb_element = pb_soup.find('span', {'id': 'Last'})
                    if pb_element:
                        pb_text = pb_element.get_text().replace(',', '.')
                        try:
                            data["pb_ratio"] = float(pb_text)
                        except ValueError:
                            pass
            except Exception as e:
                print(f"Error extracting P/B for {symbol}: {e}")
            
            # Extract last update time
            time_element = price_soup.find(text=re.compile(r'Data.*\d{2}:\d{2}', re.I))
            if time_element:
                data["last_update"] = time_element.strip()
            
        except Exception as e:
            data["status"] = f"error: {str(e)}"
            print(f"Error extracting data for {symbol}: {e}")
        
        return data
    
    def scrape_all_companies(self) -> List[Dict]:
        """Scrape data for all WIG80 companies"""
        results = []
        total_companies = len(self.wig80_companies)
        
        print(f"Starting to scrape data for {total_companies} WIG80 companies...")
        
        for i, (company_name, company_data) in enumerate(self.wig80_companies.items(), 1):
            symbol = company_data["symbol"]
            print(f"Processing {i}/{total_companies}: {company_name} ({symbol})")
            
            stock_data = self.extract_stock_data(symbol)
            stock_data["company_name"] = company_name
            
            results.append(stock_data)
            
            # Small delay to be respectful to the server
            if i < total_companies:
                time.sleep(0.5)
        
        return results
    
    def save_results(self, results: List[Dict], filename: str = "/workspace/data/wig80_current_data.json"):
        """Save results to JSON file"""
        final_data = {
            "metadata": {
                "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_companies": len(results),
                "data_source": "stooq.pl",
                "index": "WIG80 (sWIG80)",
                "currency": "PLN"
            },
            "companies": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {filename}")
        return final_data

def main():
    scraper = WIG80Scraper()
    results = scraper.scrape_all_companies()
    final_data = scraper.save_results(results)
    
    # Print summary
    successful_extractions = [r for r in results if r["status"] == "success"]
    failed_extractions = [r for r in results if r["status"] != "success"]
    
    print(f"\nScraping Summary:")
    print(f"Total companies: {len(results)}")
    print(f"Successful: {len(successful_extractions)}")
    print(f"Failed: {len(failed_extractions)}")
    
    if failed_extractions:
        print(f"\nFailed companies:")
        for company in failed_extractions:
            print(f"  {company['company_name']}: {company['status']}")

if __name__ == "__main__":
    main()