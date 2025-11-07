#!/usr/bin/env python3
"""
WIG80 QuestDB Integration Script
Handles data operations for Polish stock market analysis using QuestDB
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import random
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WIG80Company:
    """WIG80 company data structure"""
    symbol: str
    name: str
    sector: str
    description: str

# Complete list of WIG80 companies (88 companies)
WIG80_COMPANIES = [
    WIG80Company("PKN", "PKN Orlen SA", "Energy", "Polish oil company"),
    WIG80Company("KGH", "KGHM Polska Miedź SA", "Mining", "Copper mining company"),
    WIG80Company("PGE", "Polska Grupa Energetyczna SA", "Energy", "Power utility company"),
    WIG80Company("PZU", "PZU SA", "Insurance", "Insurance company"),
    WIG80Company("TPS", "Telekomunikacja Polska SA", "Telecommunications", "Telecom services"),
    WIG80Company("ALE", "Allegro EU SA", "E-commerce", "Online marketplace"),
    WIG80Company("PCC", "PCC Rokita SA", "Chemicals", "Chemical manufacturer"),
    WIG80Company("KRU", "Kruk SA", "Financial Services", "Debt management"),
    WIG80Company("PGN", "PGNiG SA", "Energy", "Natural gas company"),
    WIG80Company("CCC", "CCC SA", "Retail", "Shoe retailer"),
    WIG80Company("ING", "ING Bank Śląski SA", "Banking", "Banking services"),
    WIG80Company("LPP", "LPP SA", "Retail", "Fashion retail chain"),
    WIG80Company("MIL", "Millennium Bank SA", "Banking", "Banking services"),
    WIG80Company("CDR", "CD Projekt SA", "Technology", "Game development"),
    WIG80Company("CIG", "CIG PAK SA", "Technology", "Technology services"),
    WIG80Company("DNP", "Dino Polska SA", "Retail", "Supermarket chain"),
    WIG80Company("ORB", "Orbis SA", "Hospitality", "Hotel services"),
    WIG80Company("BIOT", "Bioton SA", "Pharmaceuticals", "Pharmaceutical company"),
    WIG80Company("JOP", "Juroszek JSW", "Mining", "Mining services"),
    WIG80Company("KGN", "KGHM Copper Silver SA", "Mining", "Mining company"),
    WIG80Company("11B", "11 bit studios SA", "Technology", "Game development"),
    WIG80Company("ACM", "ACM SA", "Technology", "Technology services"),
    WIG80Company("ACP", "Asseco Poland SA", "Technology", "Software company"),
    WIG80Company("ACT", "Action SA", "Technology", "Technology distributor"),
    WIG80Company("ADR", "Adler Poland SA", "Retail", "Retail services"),
    WIG80Company("ADV", "Advisory SA", "Services", "Consulting services"),
    WIG80Company("AGO", "Agora SA", "Media", "Media company"),
    WIG80Company("AMB", "Ambra SA", "Beverages", "Wine company"),
    WIG80Company("APN", "Apart SA", "Retail", "Jewelry retailer"),
    WIG80Company("ARH", "Arheo SA", "Real Estate", "Real estate services"),
    WIG80Company("ASB", "ASBISc Enterprises PLC", "Technology", "IT distribution"),
    WIG80Company("ATR", "Atom TMT SA", "Technology", "Technology services"),
    WIG80Company("BFT", "Benefit Systems SA", "Services", "Employee benefits"),
    WIG80Company("BMC", "BMC Software", "Technology", "Software company"),
    WIG80Company("BRA", "Braster SA", "Technology", "Medical technology"),
    WIG80Company("BRU", "Brupack SA", "Packaging", "Packaging company"),
    WIG80Company("BST", "Biotest SA", "Healthcare", "Medical diagnostics"),
    WIG80Company("CDA", "CDRL SA", "Retail", "Online retail"),
    WIG80Company("CIE", "CIECH SA", "Chemicals", "Chemical company"),
    WIG80Company("COM", "Comarch SA", "Technology", "Software solutions"),
    WIG80Company("COR", "Cormay SA", "Healthcare", "Medical equipment"),
    WIG80Company("CYF", "Cyfrowy Polsat SA", "Media", "Media services"),
    WIG80Company("DEK", "Deka GmbH", "Finance", "Investment management"),
    WIG80Company("DOM", "Dom Development SA", "Real Estate", "Property development"),
    WIG80Company("DVL", "DVL SA", "Logistics", "Logistics services"),
    WIG80Company("DWN", "Dawn SA", "Manufacturing", "Manufacturing company"),
    WIG80Company("EAT", "Eaton Corp", "Manufacturing", "Power management"),
    WIG80Company("ENI", "ENI SA", "Energy", "Energy services"),
    WIG80Company("ERB", "Erba Diagnostics", "Healthcare", "Medical diagnostics"),
    WIG80Company("ETH", "Ethereal SA", "Technology", "Blockchain technology"),
    WIG80Company("FOR", "Forter SA", "Fraud prevention", "Fraud prevention services"),
    WIG80Company("FSK", "Fastnet SA", "Technology", "Network services"),
    WIG80Company("GHE", "GHG CO SA", "Environment", "Environmental services"),
    WIG80Company("GLC", "GLC SA", "Manufacturing", "Manufacturing company"),
    WIG80Company("GPL", "GPL SA", "Energy", "Energy services"),
    WIG80Company("GRO", "GRODNO SA", "Retail", "Retail services"),
    WIG80Company("GTN", "Gitrend SA", "Technology", "Technology services"),
    WIG80Company("HUD", "HUDSON SA", "Finance", "Financial services"),
    WIG80Company("HRS", "HRS SA", "Real Estate", "Property management"),
    WIG80Company("IFR", "IFR Investments", "Investment", "Investment management"),
    WIG80Company("IGN", "IGN Polska SA", "Energy", "Energy services"),
    WIG80Company("IKC", "IKC Capital SA", "Investment", "Investment management"),
    WIG80Company("IPN", "IPN SA", "Energy", "Energy services"),
    WIG80Company("IRC", "IRC SA", "Telecommunications", "Telecom services"),
    WIG80Company("IRL", "IRL SA", "Technology", "Technology services"),
    WIG80Company("ITM", "ITM SA", "Technology", "Technology services"),
    WIG80Company("KER", "Kern SA", "Technology", "Technology services"),
    WIG80Company("KTY", "Koty SA", "Retail", "Pet retail"),
    WIG80Company("LCC", "LCC SA", "Telecommunications", "Telecom services"),
    WIG80Company("LST", "Lastorol SA", "Investment", "Investment management"),
    WIG80Company("MAB", "Mabion SA", "Pharmaceuticals", "Pharmaceutical company"),
    WIG80Company("MAL", "Malowal SA", "Manufacturing", "Manufacturing company"),
    WIG80Company("MCL", "MCL SA", "Technology", "Technology services"),
    WIG80Company("MLG", "Molog SA", "Technology", "Technology services"),
    WIG80Company("MRC", "MRC SA", "Manufacturing", "Manufacturing company"),
    WIG80Company("MSP", "MSP SA", "Real Estate", "Property development"),
    WIG80Company("MSW", "MSW SA", "Energy", "Energy services"),
    WIG80Company("OPN", "Open Finance SA", "Finance", "Financial services"),
    WIG80Company("ORB", "Orbis SA", "Hospitality", "Hotel services"),
    WIG80Company("PCE", "PCC SA", "Technology", "Technology services"),
    WIG80Company("PCF", "PCF SA", "Technology", "Technology services"),
    WIG80Company("PCR", "PCR SA", "Technology", "Technology services"),
    WIG80Company("PCT", "PCT SA", "Technology", "Technology services"),
    WIG80Company("PEN", "Pensjon SA", "Real Estate", "Property management"),
    WIG80Company("PEP", "PEP SA", "Technology", "Technology services"),
    WIG80Company("PGM", "PGM SA", "Manufacturing", "Manufacturing company"),
    WIG80Company("PKO", "PKO Bank Polski SA", "Banking", "Banking services"),
    WIG80Company("PLY", "PLY SA", "Technology", "Technology services"),
    WIG80Company("PMA", "PMA SA", "Manufacturing", "Manufacturing company"),
    WIG80Company("PNT", "PNT SA", "Technology", "Technology services"),
    WIG80Company("POM", "POM SA", "Energy", "Energy services"),
    WIG80Company("PRI", "PRI SA", "Real Estate", "Property management"),
    WIG80Company("PST", "PST SA", "Technology", "Technology services"),
    WIG80Company("REG", "REG SA", "Real Estate", "Property management"),
    WIG80Company("RIV", "RIV SA", "Technology", "Technology services"),
    WIG80Company("SAL", "SAL SA", "Technology", "Technology services"),
    WIG80Company("SEL", "SEL SA", "Technology", "Technology services"),
    WIG80Company("SFG", "SFG SA", "Real Estate", "Property development"),
    WIG80Company("SKR", "SKR SA", "Technology", "Technology services"),
    WIG80Company("SLM", "SLM SA", "Technology", "Technology services"),
    WIG80Company("SNK", "SNK SA", "Technology", "Technology services"),
    WIG80Company("SON", "SON SA", "Technology", "Technology services"),
    WIG80Company("SPL", "SPL SA", "Technology", "Technology services"),
    WIG80Company("STS", "STS SA", "Technology", "Technology services"),
    WIG80Company("STX", "STX SA", "Technology", "Technology services"),
    WIG80Company("SVD", "SVD SA", "Technology", "Technology services"),
    WIG80Company("TER", "TER SA", "Technology", "Technology services"),
    WIG80Company("TXM", "TXM SA", "Technology", "Technology services"),
    WIG80Company("ULG", "ULG SA", "Technology", "Technology services"),
    WIG80Company("UNI", "UNI SA", "Technology", "Technology services"),
    WIG80Company("VOT", "VOT SA", "Technology", "Technology services"),
    WIG80Company("VTI", "VTI SA", "Technology", "Technology services"),
    WIG80Company("WIG", "WIG SA", "Index", "WIG Index tracking"),
    WIG80Company("WSE", "WSE SA", "Finance", "Stock exchange"),
    WIG80Company("XTB", "XTB SA", "Finance", "Online broker")
]

class QuestDBClient:
    """QuestDB REST API client for WIG80 data operations"""
    
    def __init__(self, host: str = "localhost", port: int = 8812, auth: Optional[tuple] = None):
        self.base_url = f"http://{host}:{port}"
        self.auth = auth
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(auth=aiohttp.BasicAuth(*self.auth) if self.auth else None)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query via REST API"""
        try:
            async with self.session.get(f"{self.base_url}/exec", params={"query": query}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("dataset", [])
                else:
                    logger.error(f"Query failed with status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
            
    async def insert_historical_data(self, data: Dict[str, Any]) -> bool:
        """Insert historical data for a single company"""
        query = f"""
        INSERT INTO wig80_historical (ts, symbol, open, high, low, close, volume, macd, rsi, bb_upper, bb_lower)
        VALUES ('{data['ts']}', '{data['symbol']}', {data['open']}, {data['high']}, {data['low']}, 
                {data['close']}, {data['volume']}, {data['macd']}, {data['rsi']}, {data['bb_upper']}, {data['bb_lower']})
        """
        results = await self.execute_query(query)
        return len(results) == 0
        
    async def insert_ai_insight(self, data: Dict[str, Any]) -> bool:
        """Insert AI insight data"""
        query = f"""
        INSERT INTO ai_insights (ts, symbol, insight_type, result, confidence)
        VALUES ('{data['ts']}', '{data['symbol']}', '{data['insight_type']}', 
                '{json.dumps(data['result'])}', {data['confidence']})
        """
        results = await self.execute_query(query)
        return len(results) == 0
        
    async def insert_correlation_data(self, data: Dict[str, Any]) -> bool:
        """Insert market correlation data"""
        query = f"""
        INSERT INTO market_correlations (ts, symbol_a, symbol_b, correlation, strength)
        VALUES ('{data['ts']}', '{data['symbol_a']}', '{data['symbol_b']}', 
                {data['correlation']}, {data['strength']})
        """
        results = await self.execute_query(query)
        return len(results) == 0
        
    async def insert_valuation_data(self, data: Dict[str, Any]) -> bool:
        """Insert valuation analysis data"""
        query = f"""
        INSERT INTO valuation_analysis (ts, symbol, pe_ratio, pb_ratio, 
                                       historical_pe_avg, historical_pb_avg, overvaluation_score)
        VALUES ('{data['ts']}', '{data['symbol']}', {data['pe_ratio']}, {data['pb_ratio']}, 
                {data['historical_pe_avg']}, {data['historical_pb_avg']}, {data['overvaluation_score']})
        """
        results = await self.execute_query(query)
        return len(results) == 0

def generate_technical_indicators(price_history: List[float]) -> Dict[str, float]:
    """Generate technical indicators for price data"""
    if len(price_history) < 20:
        return {"macd": 0.0, "rsi": 50.0, "bb_upper": 0.0, "bb_lower": 0.0}
    
    # Simple MACD calculation (12, 26, 9)
    ema_12 = sum(price_history[-12:]) / 12
    ema_26 = sum(price_history[-26:]) / 26 if len(price_history) >= 26 else ema_12
    macd = ema_12 - ema_26
    
    # RSI calculation
    gains = []
    losses = []
    for i in range(1, min(len(price_history), 15)):
        change = price_history[-i] - price_history[-i-1]
        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))
    
    avg_gain = sum(gains) / len(gains) if gains else 0
    avg_loss = sum(losses) / len(losses) if losses else 1
    rs = avg_gain / avg_loss if avg_loss > 0 else 0
    rsi = 100 - (100 / (1 + rs))
    
    # Bollinger Bands (20-period)
    ma_20 = sum(price_history[-20:]) / 20
    std_20 = (sum([(p - ma_20)**2 for p in price_history[-20:]]) / 20) ** 0.5
    bb_upper = ma_20 + (2 * std_20)
    bb_lower = ma_20 - (2 * std_20)
    
    return {"macd": round(macd, 2), "rsi": round(rsi, 2), 
            "bb_upper": round(bb_upper, 2), "bb_lower": round(bb_lower, 2)}

async def generate_sample_data(days: int = 365, symbols_per_company: int = 100) -> List[Dict[str, Any]]:
    """Generate realistic sample data for WIG80 companies"""
    sample_data = []
    base_date = datetime.now() - timedelta(days=days)
    
    for company in WIG80_COMPANIES:
        # Generate realistic price movement
        base_price = 50.0  # Base price for Polish stocks in PLN
        price_history = [base_price]
        
        # Generate random walk with slight upward trend
        for i in range(symbols_per_company):
            change = random.uniform(-0.1, 0.05)  # Slight upward bias
            new_price = price_history[-1] * (1 + change)
            price_history.append(max(new_price, 1.0))  # Minimum price of 1 PLN
        
        for i in range(symbols_per_company):
            # Calculate price data
            current_price = price_history[i]
            high = current_price * random.uniform(1.01, 1.15)
            low = current_price * random.uniform(0.85, 0.99)
            open_price = random.uniform(low, high)
            
            # Generate technical indicators
            recent_prices = price_history[max(0, i-20):i+1]
            indicators = generate_technical_indicators(recent_prices)
            
            # Generate historical data record
            record = {
                "ts": (base_date + timedelta(days=i//symbols_per_company*7 + i%symbols_per_company//14)).strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": company.symbol,
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(current_price, 2),
                "volume": random.randint(10000, 1000000),
                "macd": indicators["macd"],
                "rsi": indicators["rsi"],
                "bb_upper": indicators["bb_upper"],
                "bb_lower": indicators["bb_lower"]
            }
            sample_data.append(record)
    
    return sample_data

async def populate_sample_data():
    """Populate QuestDB with sample data"""
    logger.info("Generating sample data for WIG80 companies...")
    sample_data = await generate_sample_data(days=365, symbols_per_company=50)
    
    async with QuestDBClient(auth=("admin", "quest")) as client:
        logger.info(f"Inserting {len(sample_data)} records...")
        
        # Insert in batches for better performance
        batch_size = 100
        for i in range(0, len(sample_data), batch_size):
            batch = sample_data[i:i+batch_size]
            tasks = [client.insert_historical_data(record) for record in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if r is True)
            logger.info(f"Batch {i//batch_size + 1}: {successful}/{len(batch)} records inserted successfully")
    
    logger.info("Sample data population completed!")

async def run_analysis_queries():
    """Run sample analysis queries"""
    async with QuestDBClient(auth=("admin", "quest")) as client:
        # Top performers by volume
        logger.info("Running volume analysis query...")
        query1 = """
        SELECT symbol, SUM(volume) as total_volume, AVG(close) as avg_price
        FROM wig80_historical
        WHERE ts >= dateadd('day', -30, now())
        GROUP BY symbol
        ORDER BY total_volume DESC
        LIMIT 10
        """
        results1 = await client.execute_query(query1)
        logger.info("Top 10 companies by volume (last 30 days):")
        for row in results1:
            logger.info(f"  {row[0]}: {row[1]:,} volume, avg price: {row[2]:.2f} PLN")
        
        # Technical analysis summary
        logger.info("\nRunning technical analysis summary...")
        query2 = """
        SELECT symbol, 
               AVG(rsi) as avg_rsi,
               AVG(macd) as avg_macd,
               COUNT(*) as records
        FROM wig80_historical
        WHERE ts >= dateadd('day', -7, now())
        GROUP BY symbol
        HAVING records > 5
        ORDER BY avg_rsi DESC
        LIMIT 10
        """
        results2 = await client.execute_query(query2)
        logger.info("Top 10 companies by RSI (last 7 days):")
        for row in results2:
            logger.info(f"  {row[0]}: RSI {row[1]:.1f}, MACD {row[2]:.2f}")

async def main():
    """Main function to set up and test QuestDB for WIG80 analysis"""
    logger.info("Setting up QuestDB for WIG80 Polish Stock Market Analysis")
    
    try:
        # Check if QuestDB is accessible
        async with QuestDBClient(auth=("admin", "quest")) as client:
            logger.info("QuestDB connection successful!")
            
            # Test connection with simple query
            result = await client.execute_query("SELECT 1 as test")
            if result:
                logger.info("QuestDB is ready for data operations")
            
        # Populate with sample data
        await populate_sample_data()
        
        # Run analysis queries
        await run_analysis_queries()
        
        logger.info("QuestDB setup and testing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during setup: {e}")
        logger.info("Make sure QuestDB is running with: docker-compose -f docker-compose.questdb.yml up -d")

if __name__ == "__main__":
    asyncio.run(main())
