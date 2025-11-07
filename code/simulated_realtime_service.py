#!/usr/bin/env python3
"""
Simulated Real-Time WIG80 Data Generator
Generates realistic market data with time-based variations
Mimics real market behavior for demonstration purposes
"""

import json
import time
import random
import math
from datetime import datetime, timedelta
import os
import sys

class SimulatedRealTimeWIG80:
    def __init__(self, output_file: str, base_data_file: str):
        self.output_file = output_file
        self.base_data_file = base_data_file
        self.companies = []
        self.last_prices = {}
        self.price_trends = {}
        
        # Load base data
        self.load_base_data()
        
    def load_base_data(self):
        """Load base company data"""
        try:
            with open(self.base_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.companies = data.get('companies', [])
                
            print(f"Loaded {len(self.companies)} companies from base data")
            
            # Initialize tracking
            for company in self.companies:
                symbol = company['symbol']
                self.last_prices[symbol] = company['current_price']
                self.price_trends[symbol] = random.choice([-1, 0, 1])  # -1: down, 0: sideways, 1: up
                
        except Exception as e:
            print(f"Error loading base data: {e}")
            sys.exit(1)
    
    def get_market_status(self):
        """Determine if market is open (WSE hours: 9:00-17:00 CET/CEST)"""
        now = datetime.now()
        
        # Poland time (CET/CEST) - approximate
        hour = now.hour
        day = now.weekday()  # 0-6, Mon-Sun
        
        # Weekend
        if day >= 5:  # Saturday or Sunday
            return {
                'status': 'closed',
                'label': 'Rynek Zamknięty (Weekend)',
                'is_open': False,
                'volatility': 0.0
            }
        
        # Pre-market (8:30-9:00)
        if 8 <= hour < 9:
            return {
                'status': 'pre_market',
                'label': 'Pre-market',
                'is_open': False,
                'volatility': 0.2
            }
        
        # Market hours (9:00-17:00)
        if 9 <= hour < 17:
            return {
                'status': 'open',
                'label': 'Rynek Otwarty',
                'is_open': True,
                'volatility': 1.0
            }
        
        # After hours (17:00-17:10)
        if 17 <= hour < 18:
            return {
                'status': 'after_hours',
                'label': 'Po Sesji',
                'is_open': False,
                'volatility': 0.3
            }
        
        # Closed
        return {
            'status': 'closed',
            'label': 'Rynek Zamknięty',
            'is_open': False,
            'volatility': 0.0
        }
    
    def generate_realistic_update(self, company: dict, market_status: dict):
        """Generate realistic price update based on market conditions"""
        symbol = company['symbol']
        last_price = self.last_prices.get(symbol, company['current_price'])
        trend = self.price_trends.get(symbol, 0)
        
        volatility = market_status['volatility']
        
        if volatility == 0:
            # Market closed - no changes
            return {
                **company,
                'current_price': last_price,
                'last_update': datetime.now().strftime("%H:%M:%S"),
                'status': 'success'
            }
        
        # Calculate price change
        # Trend influence: -0.3% to +0.3%
        trend_change = trend * random.uniform(0.1, 0.3) * volatility
        
        # Random noise: -0.2% to +0.2%
        noise = random.uniform(-0.2, 0.2) * volatility
        
        # Total change percentage
        change_pct = trend_change + noise
        
        # Apply change to price
        new_price = last_price * (1 + change_pct / 100)
        
        # Keep price reasonable (prevent extreme values)
        new_price = max(0.01, min(new_price, last_price * 1.5))
        
        # Update stored values
        self.last_prices[symbol] = new_price
        
        # Occasionally change trend (10% chance)
        if random.random() < 0.1:
            self.price_trends[symbol] = random.choice([-1, 0, 1])
        
        # Calculate overall change from original
        original_price = company['current_price']
        total_change = ((new_price - original_price) / original_price) * 100
        
        # Generate volume (varies during day)
        base_volume = company.get('trading_volume', '100K')
        volume_multiplier = random.uniform(0.8, 1.2) * volatility
        
        # Update company data
        return {
            'company_name': company['company_name'],
            'symbol': symbol,
            'current_price': round(new_price, 2),
            'change_percent': round(total_change, 2),
            'pe_ratio': company.get('pe_ratio'),
            'pb_ratio': company.get('pb_ratio'),
            'trading_volume': base_volume,  # Keep base for consistency
            'trading_volume_obrot': company.get('trading_volume_obrot', '0 PLN'),
            'last_update': datetime.now().strftime("%H:%M:%S"),
            'status': 'success'
        }
    
    def generate_update(self):
        """Generate complete data update"""
        market_status = self.get_market_status()
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Market Status: {market_status['label']}")
        
        updated_companies = []
        
        for company in self.companies:
            updated = self.generate_realistic_update(company, market_status)
            updated_companies.append(updated)
        
        # Calculate statistics
        avg_change = sum(c['change_percent'] for c in updated_companies) / len(updated_companies)
        gainers = sum(1 for c in updated_companies if c['change_percent'] > 0)
        losers = sum(1 for c in updated_companies if c['change_percent'] < 0)
        
        print(f"  Avg Change: {avg_change:+.2f}%")
        print(f"  Gainers: {gainers}, Losers: {losers}, Unchanged: {len(updated_companies) - gainers - losers}")
        
        return {
            'metadata': {
                'collection_date': datetime.now().isoformat(),
                'data_source': 'stooq.pl (simulated real-time)',
                'index': 'WIG80 (sWIG80)',
                'currency': 'PLN',
                'total_companies': len(updated_companies),
                'successful_fetches': len(updated_companies),
                'market_status': market_status['status'],
                'poland_time': datetime.now().strftime("%H:%M:%S"),
                'is_market_hours': market_status['is_open'],
                'avg_change': round(avg_change, 2)
            },
            'companies': updated_companies
        }
    
    def save_data(self, data: dict):
        """Save data to JSON file atomically - save to multiple locations"""
        locations = [
            self.output_file,
            "/workspace/polish-finance-platform/polish-finance-app/dist/wig80_current_data.json"
        ]
        
        for location in locations:
            try:
                # Create directory if needed
                os.makedirs(os.path.dirname(location), exist_ok=True)
                
                temp_file = f"{location}.tmp"
                
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                os.replace(temp_file, location)
            except Exception as e:
                print(f"  Warning: Could not save to {location}: {e}")
        
        print(f"  Data saved to {len(locations)} locations")
    
    def run_continuous(self, interval_seconds: int = 30):
        """Run continuously, updating data at regular intervals"""
        print(f"\n{'='*70}")
        print(f"Simulated Real-Time WIG80 Data Service Started")
        print(f"Update interval: {interval_seconds} seconds")
        print(f"Output file: {self.output_file}")
        print(f"Companies: {len(self.companies)}")
        print(f"{'='*70}\n")
        
        iteration = 0
        
        while True:
            try:
                iteration += 1
                print(f"\n{'='*70}")
                print(f"Update #{iteration}")
                print(f"{'='*70}")
                
                data = self.generate_update()
                self.save_data(data)
                
                print(f"\nNext update in {interval_seconds} seconds...")
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n\nService stopped by user")
                break
            except Exception as e:
                print(f"\nError in main loop: {e}")
                import traceback
                traceback.print_exc()
                print(f"Retrying in {interval_seconds} seconds...")
                time.sleep(interval_seconds)

def main():
    base_data = "/workspace/data/wig80_current_data.json"
    output_file = "/workspace/polish-finance-platform/polish-finance-app/public/wig80_current_data.json"
    
    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    service = SimulatedRealTimeWIG80(output_file, base_data)
    service.run_continuous(interval_seconds=30)

if __name__ == "__main__":
    main()
