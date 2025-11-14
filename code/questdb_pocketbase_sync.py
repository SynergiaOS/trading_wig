#!/usr/bin/env python3
"""
QuestDB to Pocketbase Data Ingestion Service
============================================

Comprehensive data synchronization service that connects QuestDB test database
with Pocketbase collections for WIG80 Polish stock market data.

Features:
- Batch transfer of 32,120 historical records for 88 WIG80 companies
- Real-time streaming for live updates
- Data validation and error handling
- Retry logic with exponential backoff
- Comprehensive logging and monitoring

Author: Data Engineering Team
Date: 2025-11-06
"""

import asyncio
import aiohttp
import json
import logging
import sqlite3
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from contextlib import asynccontextmanager

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/logs/questdb_pocketbase_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Company:
    """WIG80 company data structure"""
    symbol: str
    name: str
    sector: str
    description: str

@dataclass
class StockData:
    """Stock data structure for QuestDB ingestion"""
    ts: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    macd: float
    rsi: float
    bb_upper: float
    bb_lower: float

@dataclass
class AIInsight:
    """AI insight data structure"""
    ts: datetime
    symbol: str
    insight_type: str
    result: Dict[str, Any]
    confidence: float

@dataclass
class MarketCorrelation:
    """Market correlation data structure"""
    ts: datetime
    symbol_a: str
    symbol_b: str
    correlation: float
    strength: float

@dataclass
class ValuationAnalysis:
    """Valuation analysis data structure"""
    ts: datetime
    symbol: str
    pe_ratio: float
    pb_ratio: float
    historical_pe_avg: float
    historical_pb_avg: float
    overvaluation_score: float

class QuestDBPocketbaseSync:
    """
    Main data ingestion service for QuestDB to Pocketbase synchronization.
    
    This service handles:
    - Initial bulk data transfer from QuestDB to Pocketbase
    - Real-time streaming of new data
    - Data validation and transformation
    - Error handling and retry logic
    - Performance monitoring and logging
    """
    
    def __init__(self, questdb_path: str, pocketbase_url: str, admin_email: str = None, admin_password: str = None):
        """Initialize the sync service with database configurations"""
        self.questdb_path = questdb_path
        self.pocketbase_url = pocketbase_url.rstrip('/')
        self.admin_email = admin_email
        self.admin_password = admin_password
        self.session = None
        self.pocketbase_token = None
        self.is_running = False
        
        # Performance and retry configuration
        self.batch_size = 1000
        self.max_retries = 5
        self.retry_delay = 1.0
        self.max_concurrent_transfers = 3
        
        # Data statistics
        self.stats = {
            'total_records_processed': 0,
            'records_synced': 0,
            'records_failed': 0,
            'sync_start_time': None,
            'last_sync_time': None
        }
        
        # WIG80 Companies data
        self.companies = self._load_wig80_companies()
        
        # Processing queues for real-time sync
        self.processing_queue = queue.Queue()
        self.streaming_active = False
        
        logger.info("QuestDB-Pocketbase sync service initialized")
    
    def _load_wig80_companies(self) -> List[Company]:
        """Load WIG80 companies data"""
        companies = [
            Company("PKN", "PKN Orlen SA", "Energy", "Polish oil company"),
            Company("KGH", "KGHM Polska Miedź SA", "Mining", "Copper mining company"),
            Company("PGE", "Polska Grupa Energetyczna SA", "Energy", "Power utility company"),
            Company("PZU", "PZU SA", "Insurance", "Insurance company"),
            Company("TPS", "Telekomunikacja Polska SA", "Telecommunications", "Telecom services"),
            Company("ALE", "Allegro EU SA", "E-commerce", "Online marketplace"),
            Company("PCC", "PCC Rokita SA", "Chemicals", "Chemical manufacturer"),
            Company("KRU", "Kruk SA", "Financial Services", "Debt management"),
            Company("PGN", "PGNiG SA", "Energy", "Natural gas company"),
            Company("CCC", "CCC SA", "Retail", "Shoe retailer"),
            Company("ING", "ING Bank Śląski SA", "Banking", "Banking services"),
            Company("LPP", "LPP SA", "Retail", "Fashion retail chain"),
            Company("MIL", "Millennium Bank SA", "Banking", "Banking services"),
            Company("CDR", "CD Projekt SA", "Technology", "Game development"),
            Company("CIG", "CIG PAK SA", "Technology", "Technology services"),
            Company("DNP", "Dino Polska SA", "Retail", "Supermarket chain"),
            Company("ORB", "Orbis SA", "Hospitality", "Hotel services"),
            Company("BIOT", "Bioton SA", "Pharmaceuticals", "Pharmaceutical company"),
            Company("JOP", "Juroszek JSW", "Mining", "Mining services"),
            Company("KGN", "KGHM Copper Silver SA", "Mining", "Mining company"),
            Company("11B", "11 bit studios SA", "Technology", "Game development"),
            Company("ACM", "ACM SA", "Technology", "Technology services"),
            Company("ACP", "Asseco Poland SA", "Technology", "Software company"),
            Company("ACT", "Action SA", "Technology", "Technology distributor"),
            Company("ADR", "Adler Poland SA", "Retail", "Retail services"),
            Company("ADV", "Advisory SA", "Services", "Consulting services"),
            Company("AGO", "Agora SA", "Media", "Media company"),
            Company("AMB", "Ambra SA", "Beverages", "Wine company"),
            Company("APN", "Apart SA", "Retail", "Jewelry retailer"),
            Company("ARH", "Arheo SA", "Real Estate", "Real estate services"),
            Company("ASB", "ASBISc Enterprises PLC", "Technology", "IT distribution"),
            Company("ATR", "Atom TMT SA", "Technology", "Technology services"),
            Company("BFT", "Benefit Systems SA", "Services", "Employee benefits"),
            Company("BMC", "BMC Software", "Technology", "Software company"),
            Company("BRA", "Braster SA", "Technology", "Medical technology"),
            Company("BRU", "Brupack SA", "Packaging", "Packaging company"),
            Company("BST", "Biotest SA", "Healthcare", "Medical diagnostics"),
            Company("CDA", "CDRL SA", "Retail", "Online retail"),
            Company("CIE", "CIECH SA", "Chemicals", "Chemical company"),
            Company("COM", "Comarch SA", "Technology", "Software solutions"),
            Company("COR", "Cormay SA", "Healthcare", "Medical equipment"),
            Company("CYF", "Cyfrowy Polsat SA", "Media", "Media services"),
            Company("DEK", "Deka GmbH", "Finance", "Investment management"),
            Company("DOM", "Dom Development SA", "Real Estate", "Property development"),
            Company("DVL", "DVL SA", "Logistics", "Logistics services"),
            Company("DWN", "Dawn SA", "Manufacturing", "Manufacturing company"),
            Company("EAT", "Eaton Corp", "Manufacturing", "Power management"),
            Company("ENI", "ENI SA", "Energy", "Energy services"),
            Company("ERB", "Erba Diagnostics", "Healthcare", "Medical diagnostics"),
            Company("ETH", "Ethereal SA", "Technology", "Blockchain technology"),
            Company("FOR", "Forter SA", "Fraud prevention", "Fraud prevention services"),
            Company("FSK", "Fastnet SA", "Technology", "Network services"),
            Company("GHE", "GHG CO SA", "Environment", "Environmental services"),
            Company("GLC", "GLC SA", "Manufacturing", "Manufacturing company"),
            Company("GPL", "GPL SA", "Energy", "Energy services"),
            Company("GRO", "GRODNO SA", "Retail", "Retail services"),
            Company("GTN", "Gitrend SA", "Technology", "Technology services"),
            Company("HUD", "HUDSON SA", "Finance", "Financial services"),
            Company("HRS", "HRS SA", "Real Estate", "Property management"),
            Company("IFR", "IFR Investments", "Investment", "Investment management"),
            Company("IGN", "IGN Polska SA", "Energy", "Energy services"),
            Company("IKC", "IKC Capital SA", "Investment", "Investment management"),
            Company("IPN", "IPN SA", "Energy", "Energy services"),
            Company("IRC", "IRC SA", "Telecommunications", "Telecom services"),
            Company("IRL", "IRL SA", "Technology", "Technology services"),
            Company("ITM", "ITM SA", "Technology", "Technology services"),
            Company("KER", "Kern SA", "Technology", "Technology services"),
            Company("KTY", "Koty SA", "Retail", "Pet retail"),
            Company("LCC", "LCC SA", "Telecommunications", "Telecom services"),
            Company("LST", "Lastorol SA", "Investment", "Investment management"),
            Company("MAB", "Mabion SA", "Pharmaceuticals", "Pharmaceutical company"),
            Company("MAL", "Malcolmcusack SA", "Services", "Services company"),
            Company("MCL", "MCI Capital SA", "Investment", "Investment management"),
            Company("MLG", "ML Group SA", "Technology", "Technology services"),
            Company("MRC", "Merck SA", "Healthcare", "Pharmaceutical company"),
            Company("MSP", "MSP SA", "Technology", "Technology services"),
            Company("MSW", "MSW SA", "Manufacturing", "Manufacturing company"),
            Company("OPN", "Open SA", "Technology", "Technology services"),
            Company("PCE", "PCE SA", "Energy", "Energy services"),
            Company("PCF", "PCF Group SA", "Technology", "Technology services"),
            Company("PCR", "PCR SA", "Healthcare", "Healthcare services"),
            Company("PCT", "PCT SA", "Technology", "Technology services"),
            Company("PEN", "Pension Plus SA", "Finance", "Financial services"),
            Company("PEP", "PepsiCo SA", "Food & Beverage", "Food and beverage"),
            Company("PGM", "PGM SA", "Mining", "Mining services"),
            Company("PKO", "PKO Bank Polski SA", "Banking", "Banking services"),
            Company("PLY", "PlayWay SA", "Technology", "Gaming technology"),
            Company("PMA", "PMA SA", "Manufacturing", "Manufacturing company"),
            Company("PNT", "Penta SA", "Technology", "Technology services"),
            Company("POM", "Pomerania SA", "Services", "Services company"),
            Company("PRI", "Primetech SA", "Technology", "Technology services"),
            Company("PST", "PST SA", "Technology", "Technology services"),
            Company("REG", "Regul SA", "Services", "Services company"),
            Company("RIV", "Rivia SA", "Technology", "Technology services"),
            Company("SAL", "Salesforce SA", "Technology", "Technology services"),
            Company("SEL", "Selvita SA", "Pharmaceuticals", "Pharmaceutical company"),
            Company("SFG", "SFG Group SA", "Technology", "Technology services"),
            Company("SKR", "Skrivanek SA", "Technology", "Technology services"),
            Company("SLM", "Sloma SA", "Technology", "Technology services"),
            Company("SNK", "Snack SA", "Food & Beverage", "Food company"),
            Company("SON", "Sony SA", "Technology", "Technology services"),
            Company("SPL", "Spółka SA", "Services", "Services company"),
            Company("STS", "Stage SA", "Entertainment", "Entertainment services"),
            Company("STX", "Stx SA", "Technology", "Technology services"),
            Company("SVD", "SVD SA", "Technology", "Technology services"),
            Company("TER", "Teradata SA", "Technology", "Data analytics"),
            Company("TXM", "TXM SA", "Technology", "Technology services"),
            Company("ULG", "Ulg SA", "Services", "Services company"),
            Company("UNI", "Unity SA", "Technology", "Technology services"),
            Company("VOT", "Voting SA", "Services", "Voting services"),
            Company("VTI", "Vті SA", "Technology", "Technology services"),
            Company("WIG", "WIG SA", "Investment", "Investment company"),
            Company("WSE", "WSE SA", "Services", "Stock exchange services"),
            Company("XTB", "XTB SA", "Financial Services", "Online brokerage")
        ]
        logger.info(f"Loaded {len(companies)} WIG80 companies")
        return companies

    @asynccontextmanager
    async def get_session(self):
        """Get aiohttp session with proper cleanup"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=300)
            self.session = aiohttp.ClientSession(timeout=timeout)
        try:
            yield self.session
        except Exception as e:
            logger.error(f"Session error: {e}")
            raise
        finally:
            # Don't close the session to maintain connection reuse
            pass

    async def authenticate_pocketbase(self) -> bool:
        """Authenticate with Pocketbase and get access token"""
        try:
            async with self.get_session() as session:
                auth_data = {
                    "identity": self.admin_email,
                    "password": self.admin_password
                }
                
                async with session.post(
                    f"{self.pocketbase_url}/api/admins/auth-with-password",
                    json=auth_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.pocketbase_token = result.get('token')
                        logger.info("Successfully authenticated with Pocketbase")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Pocketbase authentication failed: {response.status} - {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def connect_questdb(self) -> sqlite3.Connection:
        """Connect to QuestDB test database (SQLite format)"""
        try:
            conn = sqlite3.connect(self.questdb_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            logger.info(f"Connected to QuestDB test database: {self.questdb_path}")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to QuestDB: {e}")
            raise

    async def fetch_questdb_data(self, table_name: str, limit: int = None) -> List[Dict[str, Any]]:
        """Fetch data from QuestDB tables with error handling"""
        conn = None
        try:
            conn = self.connect_questdb()
            
            # Build query
            query = f"SELECT * FROM {table_name}"
            if limit:
                query += f" LIMIT {limit}"
            
            # Execute query and fetch results
            cursor = conn.execute(query)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                row_dict = dict(row)
                # Convert datetime strings to datetime objects
                for key, value in row_dict.items():
                    if isinstance(value, str) and 'T' in value and 'Z' in value:
                        try:
                            row_dict[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except:
                            pass
                data.append(row_dict)
            
            logger.info(f"Fetched {len(data)} records from {table_name}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data from {table_name}: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def validate_stock_data(self, data: Dict[str, Any]) -> bool:
        """Validate stock data completeness and correctness"""
        required_fields = ['symbol', 'ts', 'open', 'high', 'low', 'close', 'volume']
        
        # Check required fields exist
        for field in required_fields:
            if field not in data or data[field] is None:
                return False
        
        # Validate data types and ranges
        try:
            # Check numeric fields
            for field in ['open', 'high', 'low', 'close']:
                if not isinstance(data[field], (int, float)) or data[field] <= 0:
                    return False
            
            # Check volume
            if not isinstance(data['volume'], (int, float)) or data['volume'] < 0:
                return False
            
            # Check high >= low and within reasonable bounds
            if data['high'] < data['low']:
                return False
            
            # Check OHLC logic: high >= open,close,low and low <= open,close,high
            if not (data['high'] >= data['open'] and data['high'] >= data['close'] and 
                   data['high'] >= data['low'] and data['low'] <= data['open'] and 
                   data['low'] <= data['close'] and data['low'] <= data['high']):
                return False
            
            # Check timestamp
            if not isinstance(data['ts'], (datetime, str)):
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False

    async def transform_stock_data_for_pocketbase(self, questdb_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform QuestDB stock data to Pocketbase format"""
        transformed_data = []
        
        for record in questdb_data:
            if not self.validate_stock_data(record):
                logger.warning(f"Invalid stock data record: {record}")
                continue
            
            # Find company info
            company_info = next((c for c in self.companies if c.symbol == record['symbol']), None)
            company_name = company_info.name if company_info else "Unknown Company"
            sector = company_info.sector if company_info else "Unknown"
            
            # Transform to Pocketbase format
            transformed_record = {
                'id': str(uuid.uuid4()),
                'symbol': record['symbol'],
                'company_name': company_name,
                'sector': sector,
                'timestamp': record['ts'].isoformat() if isinstance(record['ts'], datetime) else record['ts'],
                'open_price': float(record['open']),
                'high_price': float(record['high']),
                'low_price': float(record['low']),
                'close_price': float(record['close']),
                'volume': int(record['volume']),
                'macd': float(record.get('macd', 0.0)) if record.get('macd') is not None else None,
                'rsi': float(record.get('rsi', 0.0)) if record.get('rsi') is not None else None,
                'bb_upper': float(record.get('bb_upper', 0.0)) if record.get('bb_upper') is not None else None,
                'bb_lower': float(record.get('bb_lower', 0.0)) if record.get('bb_lower') is not None else None,
                'created': datetime.now(timezone.utc).isoformat(),
                'updated': datetime.now(timezone.utc).isoformat()
            }
            
            transformed_data.append(transformed_record)
        
        logger.info(f"Transformed {len(transformed_data)} valid stock data records")
        return transformed_data

    async def batch_upload_to_pocketbase(self, collection: str, data: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Upload data to Pocketbase in batches with retry logic"""
        if not self.pocketbase_token:
            logger.error("No Pocketbase authentication token available")
            return 0, len(data)
        
        success_count = 0
        failed_records = []
        
        # Process in batches
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            
            success = await self._upload_batch_with_retry(collection, batch)
            
            if success:
                success_count += len(batch)
            else:
                failed_records.extend(batch)
            
            # Small delay between batches to avoid rate limiting
            await asyncio.sleep(0.1)
        
        # Log results
        if failed_records:
            logger.warning(f"Failed to upload {len(failed_records)} records to {collection}")
        
        logger.info(f"Successfully uploaded {success_count} records to {collection}")
        return success_count, len(data)

    async def _upload_batch_with_retry(self, collection: str, batch: List[Dict[str, Any]]) -> bool:
        """Upload a single batch with retry logic"""
        for attempt in range(self.max_retries):
            try:
                async with self.get_session() as session:
                    headers = {
                        'Authorization': f'Bearer {self.pocketbase_token}',
                        'Content-Type': 'application/json'
                    }
                    
                    # Prepare batch data
                    payload = {'items': batch}
                    
                    async with session.post(
                        f"{self.pocketbase_url}/api/collections/{collection}/records/batch",
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status == 200 or response.status == 201:
                            logger.debug(f"Successfully uploaded batch of {len(batch)} records to {collection}")
                            return True
                        else:
                            error_text = await response.text()
                            logger.warning(f"Batch upload attempt {attempt + 1} failed: {response.status} - {error_text}")
            
            except Exception as e:
                logger.error(f"Batch upload attempt {attempt + 1} error: {e}")
            
            # Wait before retry with exponential backoff
            if attempt < self.max_retries - 1:
                wait_time = self.retry_delay * (2 ** attempt)
                logger.info(f"Retrying batch upload in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
        
        logger.error(f"Failed to upload batch of {len(batch)} records after {self.max_retries} attempts")
        return False

    async def sync_all_tables(self) -> Dict[str, Dict[str, int]]:
        """Synchronize all data from QuestDB to Pocketbase"""
        logger.info("Starting comprehensive data synchronization...")
        self.stats['sync_start_time'] = datetime.now()
        
        # Ensure Pocketbase authentication
        if not await self.authenticate_pocketbase():
            raise Exception("Failed to authenticate with Pocketbase")
        
        results = {}
        
        # Sync stock data (wig80_historical)
        logger.info("Syncing stock data (wig80_historical)...")
        stock_data = await self.fetch_questdb_data('wig80_historical', limit=32120)
        if stock_data:
            transformed_stock_data = await self.transform_stock_data_for_pocketbase(stock_data)
            synced, total = await self.batch_upload_to_pocketbase('stock_data', transformed_stock_data)
            results['stock_data'] = {'synced': synced, 'total': total}
            self.stats['records_synced'] += synced
            self.stats['records_failed'] += (total - synced)
        else:
            results['stock_data'] = {'synced': 0, 'total': 0}
        
        # Sync AI insights
        logger.info("Syncing AI insights...")
        ai_data = await self.fetch_questdb_data('ai_insights')
        if ai_data:
            transformed_ai_data = await self._transform_ai_data_for_pocketbase(ai_data)
            synced, total = await self.batch_upload_to_pocketbase('ai_insights', transformed_ai_data)
            results['ai_insights'] = {'synced': synced, 'total': total}
            self.stats['records_synced'] += synced
            self.stats['records_failed'] += (total - synced)
        else:
            results['ai_insights'] = {'synced': 0, 'total': 0}
        
        # Sync market correlations
        logger.info("Syncing market correlations...")
        correlation_data = await self.fetch_questdb_data('market_correlations')
        if correlation_data:
            transformed_corr_data = await self._transform_correlation_data_for_pocketbase(correlation_data)
            synced, total = await self.batch_upload_to_pocketbase('market_correlations', transformed_corr_data)
            results['market_correlations'] = {'synced': synced, 'total': total}
            self.stats['records_synced'] += synced
            self.stats['records_failed'] += (total - synced)
        else:
            results['market_correlations'] = {'synced': 0, 'total': 0}
        
        # Sync valuation analysis
        logger.info("Syncing valuation analysis...")
        valuation_data = await self.fetch_questdb_data('valuation_analysis')
        if valuation_data:
            transformed_val_data = await self._transform_valuation_data_for_pocketbase(valuation_data)
            synced, total = await self.batch_upload_to_pocketbase('valuation_analysis', transformed_val_data)
            results['valuation_analysis'] = {'synced': synced, 'total': total}
            self.stats['records_synced'] += synced
            self.stats['records_failed'] += (total - synced)
        else:
            results['valuation_analysis'] = {'synced': 0, 'total': 0}
        
        self.stats['total_records_processed'] = sum(r['total'] for r in results.values())
        self.stats['last_sync_time'] = datetime.now()
        
        logger.info(f"Synchronization completed. Total processed: {self.stats['total_records_processed']}, "
                   f"Synced: {self.stats['records_synced']}, Failed: {self.stats['records_failed']}")
        
        return results

    async def _transform_ai_data_for_pocketbase(self, questdb_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform AI insights data to Pocketbase format"""
        transformed_data = []
        
        for record in questdb_data:
            try:
                # Find company info
                company_info = next((c for c in self.companies if c.symbol == record['symbol']), None)
                company_name = company_info.name if company_info else "Unknown Company"
                
                transformed_record = {
                    'id': str(uuid.uuid4()),
                    'symbol': record['symbol'],
                    'company_name': company_name,
                    'timestamp': record['ts'].isoformat() if isinstance(record['ts'], datetime) else record['ts'],
                    'insight_type': record.get('insight_type', 'unknown'),
                    'insight_result': record.get('result', {}),
                    'confidence': float(record.get('confidence', 0.0)),
                    'created': datetime.now(timezone.utc).isoformat(),
                    'updated': datetime.now(timezone.utc).isoformat()
                }
                
                transformed_data.append(transformed_record)
            except Exception as e:
                logger.warning(f"Failed to transform AI insight record: {e}")
                continue
        
        logger.info(f"Transformed {len(transformed_data)} AI insight records")
        return transformed_data

    async def _transform_correlation_data_for_pocketbase(self, questdb_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform market correlation data to Pocketbase format"""
        transformed_data = []
        
        for record in questdb_data:
            try:
                transformed_record = {
                    'id': str(uuid.uuid4()),
                    'symbol_a': record['symbol_a'],
                    'symbol_b': record['symbol_b'],
                    'timestamp': record['ts'].isoformat() if isinstance(record['ts'], datetime) else record['ts'],
                    'correlation_value': float(record.get('correlation', 0.0)),
                    'strength': float(record.get('strength', 0.0)),
                    'created': datetime.now(timezone.utc).isoformat(),
                    'updated': datetime.now(timezone.utc).isoformat()
                }
                
                transformed_data.append(transformed_record)
            except Exception as e:
                logger.warning(f"Failed to transform correlation record: {e}")
                continue
        
        logger.info(f"Transformed {len(transformed_data)} correlation records")
        return transformed_data

    async def _transform_valuation_data_for_pocketbase(self, questdb_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform valuation analysis data to Pocketbase format"""
        transformed_data = []
        
        for record in questdb_data:
            try:
                # Find company info
                company_info = next((c for c in self.companies if c.symbol == record['symbol']), None)
                company_name = company_info.name if company_info else "Unknown Company"
                
                transformed_record = {
                    'id': str(uuid.uuid4()),
                    'symbol': record['symbol'],
                    'company_name': company_name,
                    'timestamp': record['ts'].isoformat() if isinstance(record['ts'], datetime) else record['ts'],
                    'pe_ratio': float(record.get('pe_ratio', 0.0)) if record.get('pe_ratio') is not None else None,
                    'pb_ratio': float(record.get('pb_ratio', 0.0)) if record.get('pb_ratio') is not None else None,
                    'historical_pe_avg': float(record.get('historical_pe_avg', 0.0)) if record.get('historical_pe_avg') is not None else None,
                    'historical_pb_avg': float(record.get('historical_pb_avg', 0.0)) if record.get('historical_pb_avg') is not None else None,
                    'overvaluation_score': float(record.get('overvaluation_score', 0.0)) if record.get('overvaluation_score') is not None else None,
                    'created': datetime.now(timezone.utc).isoformat(),
                    'updated': datetime.now(timezone.utc).isoformat()
                }
                
                transformed_data.append(transformed_record)
            except Exception as e:
                logger.warning(f"Failed to transform valuation record: {e}")
                continue
        
        logger.info(f"Transformed {len(transformed_data)} valuation records")
        return transformed_data

    async def start_realtime_streaming(self, poll_interval: int = 60) -> None:
        """Start real-time data streaming from QuestDB to Pocketbase"""
        logger.info(f"Starting real-time streaming with {poll_interval}s poll interval")
        self.is_running = True
        self.streaming_active = True
        
        # Create a separate thread for real-time processing
        streaming_thread = threading.Thread(
            target=self._realtime_streaming_loop,
            args=(poll_interval,),
            daemon=True
        )
        streaming_thread.start()
        
        logger.info("Real-time streaming started")

    def _realtime_streaming_loop(self, poll_interval: int) -> None:
        """Main real-time streaming loop (runs in separate thread)"""
        logger.info("Real-time streaming loop started")
        
        while self.is_running:
            try:
                # Get the most recent data from QuestDB
                latest_data = self._get_latest_questdb_data()
                
                if latest_data:
                    # Process data in batches
                    self._process_realtime_batch(latest_data)
                
                # Wait for next poll
                time.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"Error in real-time streaming loop: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying
        
        logger.info("Real-time streaming loop stopped")

    def _get_latest_questdb_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the latest data from QuestDB for real-time processing"""
        latest_data = {}
        
        try:
            conn = self.connect_questdb()
            
            # Get latest records from each table
            for table in ['wig80_historical', 'ai_insights', 'market_correlations', 'valuation_analysis']:
                query = f"""
                    SELECT * FROM {table} 
                    WHERE ts > datetime('now', '-1 day') 
                    ORDER BY ts DESC 
                    LIMIT 100
                """
                
                cursor = conn.execute(query)
                rows = cursor.fetchall()
                
                if rows:
                    latest_data[table] = [dict(row) for row in rows]
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error getting latest QuestDB data: {e}")
        
        return latest_data

    def _process_realtime_batch(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Process a batch of real-time data"""
        for table_name, records in data.items():
            try:
                if table_name == 'wig80_historical':
                    # Process stock data
                    asyncio.run(self._process_realtime_stock_data(records))
                elif table_name == 'ai_insights':
                    # Process AI insights
                    asyncio.run(self._process_realtime_ai_data(records))
                elif table_name == 'market_correlations':
                    # Process correlations
                    asyncio.run(self._process_realtime_correlation_data(records))
                elif table_name == 'valuation_analysis':
                    # Process valuation data
                    asyncio.run(self._process_realtime_valuation_data(records))
                
            except Exception as e:
                logger.error(f"Error processing real-time batch for {table_name}: {e}")

    async def _process_realtime_stock_data(self, records: List[Dict[str, Any]]) -> None:
        """Process real-time stock data"""
        transformed_data = await self.transform_stock_data_for_pocketbase(records)
        if transformed_data:
            await self.batch_upload_to_pocketbase('stock_data', transformed_data)

    async def _process_realtime_ai_data(self, records: List[Dict[str, Any]]) -> None:
        """Process real-time AI insights data"""
        transformed_data = await self._transform_ai_data_for_pocketbase(records)
        if transformed_data:
            await self.batch_upload_to_pocketbase('ai_insights', transformed_data)

    async def _process_realtime_correlation_data(self, records: List[Dict[str, Any]]) -> None:
        """Process real-time correlation data"""
        transformed_data = await self._transform_correlation_data_for_pocketbase(records)
        if transformed_data:
            await self.batch_upload_to_pocketbase('market_correlations', transformed_data)

    async def _process_realtime_valuation_data(self, records: List[Dict[str, Any]]) -> None:
        """Process real-time valuation data"""
        transformed_data = await self._transform_valuation_data_for_pocketbase(records)
        if transformed_data:
            await self.batch_upload_to_pocketbase('valuation_analysis', transformed_data)

    def stop_realtime_streaming(self) -> None:
        """Stop real-time streaming"""
        logger.info("Stopping real-time streaming...")
        self.is_running = False
        self.streaming_active = False
        logger.info("Real-time streaming stopped")

    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get comprehensive synchronization statistics"""
        stats = self.stats.copy()
        
        if stats['sync_start_time']:
            duration = datetime.now() - stats['sync_start_time']
            stats['sync_duration_seconds'] = duration.total_seconds()
            
            if stats['total_records_processed'] > 0:
                stats['records_per_second'] = stats['total_records_processed'] / duration.total_seconds()
                stats['success_rate'] = (stats['records_synced'] / stats['total_records_processed']) * 100
        
        return stats

    async def health_check(self) -> Dict[str, bool]:
        """Perform health check on all system components"""
        health = {
            'pocketbase_connection': False,
            'questdb_connection': False,
            'authentication': False,
            'data_access': False
        }
        
        try:
            # Test QuestDB connection
            conn = self.connect_questdb()
            cursor = conn.execute("SELECT COUNT(*) as count FROM wig80_historical")
            count = cursor.fetchone()['count']
            conn.close()
            health['questdb_connection'] = True
            health['data_access'] = count > 0
            
        except Exception as e:
            logger.error(f"QuestDB health check failed: {e}")
        
        try:
            # Test Pocketbase connection and authentication
            health['pocketbase_connection'] = await self.authenticate_pocketbase()
            health['authentication'] = bool(self.pocketbase_token)
            
        except Exception as e:
            logger.error(f"Pocketbase health check failed: {e}")
        
        return health

    async def cleanup(self) -> None:
        """Clean up resources and connections"""
        logger.info("Cleaning up resources...")
        
        self.stop_realtime_streaming()
        
        if self.session and not self.session.closed:
            await self.session.close()
        
        logger.info("Cleanup completed")


async def main():
    """Main function to run the data ingestion service"""
    # Configuration (use environment variables for Railway service discovery)
    import os
    QUESTDB_PATH = os.getenv('QUESTDB_PATH', '/workspace/code/questdb_wig80_test.db')
    POCKETBASE_URL = os.getenv('POCKETBASE_URL', 'http://localhost:8090')
    ADMIN_EMAIL = os.getenv('POCKETBASE_ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.getenv('POCKETBASE_ADMIN_PASSWORD', 'admin123')
    
    # Create logs directory
    Path("/workspace/logs").mkdir(exist_ok=True)
    
    # Initialize and run the sync service
    sync_service = QuestDBPocketbaseSync(
        questdb_path=QUESTDB_PATH,
        pocketbase_url=POCKETBASE_URL,
        admin_email=ADMIN_EMAIL,
        admin_password=ADMIN_PASSWORD
    )
    
    try:
        # Perform health check
        logger.info("Performing system health check...")
        health = await sync_service.health_check()
        logger.info(f"Health check results: {health}")
        
        # Run initial synchronization
        logger.info("Starting initial data synchronization...")
        results = await sync_service.sync_all_tables()
        
        # Print results
        print("\n" + "="*60)
        print("SYNCHRONIZATION RESULTS")
        print("="*60)
        
        for table, result in results.items():
            print(f"{table:20}: {result['synced']:>6}/{result['total']:>6} records")
        
        # Show statistics
        stats = sync_service.get_sync_statistics()
        print(f"\nStatistics:")
        print(f"  Total processed: {stats['total_records_processed']}")
        print(f"  Successfully synced: {stats['records_synced']}")
        print(f"  Failed: {stats['records_failed']}")
        print(f"  Success rate: {(stats['records_synced']/max(stats['total_records_processed'],1)*100):.2f}%")
        
        # Start real-time streaming
        logger.info("Starting real-time data streaming...")
        await sync_service.start_realtime_streaming(poll_interval=30)
        
        # Keep the service running
        logger.info("Data ingestion service is running. Press Ctrl+C to stop...")
        while True:
            await asyncio.sleep(60)
            stats = sync_service.get_sync_statistics()
            logger.info(f"Service stats: {stats}")
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Service error: {e}")
    finally:
        await sync_service.cleanup()
        logger.info("Service shutdown completed")


if __name__ == "__main__":
    asyncio.run(main())