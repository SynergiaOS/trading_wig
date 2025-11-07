#!/usr/bin/env python3
"""
Polish Financial Market RAG System
A comprehensive Retrieval-Augmented Generation system for Polish financial market data.

Features:
- Knowledge base with Polish financial market data, regulations, and analysis
- Vector embeddings for financial concepts and WIG80 companies
- Retrieval system architecture for relevant market information
- Prompt engineering templates for market analysis queries
- Contextual response system for overvaluation detection

Author: AI Agent
Date: November 6, 2025
"""

import json
import logging
import os
import pickle
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of financial queries supported by the RAG system."""
    VALUATION_ANALYSIS = "valuation_analysis"
    OVERVALUATION_DETECTION = "overvaluation_detection"
    MARKET_COMPARISON = "market_comparison"
    FINANCIAL_HEALTH = "financial_health"
    SECTOR_ANALYSIS = "sector_analysis"
    REGULATORY_INFO = "regulatory_info"
    HISTORICAL_TRENDS = "historical_trends"
    RISK_ASSESSMENT = "risk_assessment"

class RiskLevel(Enum):
    """Risk levels for investment assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CompanyData:
    """Represents company financial data."""
    symbol: str
    company_name: str
    current_price: float
    change_percent: float
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    trading_volume: str
    trading_volume_pln: float
    market_cap: Optional[float] = None
    debt_to_equity: Optional[float] = None
    roe: Optional[float] = None

@dataclass
class EmbeddingVector:
    """Represents a vector embedding for text or financial data."""
    id: str
    vector: List[float]
    text: str
    metadata: Dict[str, Any]
    created_at: datetime

@dataclass
class QueryResult:
    """Represents a query result from the RAG system."""
    text: str
    score: float
    metadata: Dict[str, Any]
    source: str

class PolishFinancialKnowledgeBase:
    """Knowledge base containing Polish financial market information."""
    
    def __init__(self, db_path: str = "/workspace/data/rag_knowledge.db"):
        self.db_path = db_path
        self._init_database()
        self._load_financial_regulations()
        self._load_market_concepts()
        self._load_wig80_data()
    
    def _init_database(self):
        """Initialize the SQLite database for storing knowledge."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for knowledge storage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                category TEXT NOT NULL,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id TEXT PRIMARY KEY,
                vector BLOB NOT NULL,
                text TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wgi80_companies (
                symbol TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                financial_data TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def _load_financial_regulations(self):
        """Load Polish financial market regulations and legal framework."""
        regulations = [
            {
                "text": "Polish Financial Market Authority (KNF) regulations govern all securities trading on the Warsaw Stock Exchange (GPW). Key regulations include transparency requirements, insider trading prevention, and market manipulation detection.",
                "category": "regulatory",
                "source": "KNF Official Guidelines"
            },
            {
                "text": "WIG20 is the main index of the Warsaw Stock Exchange, containing the 20 largest companies by market capitalization. It serves as a benchmark for the Polish stock market performance.",
                "category": "market_structure",
                "source": "GPW Official"
            },
            {
                "text": "sWIG80 (formerly WIG80) index contains 80 smaller Polish companies following the WIG20. It's considered a measure of the broader Polish equity market beyond the largest companies.",
                "category": "market_structure",
                "source": "GPW Official"
            },
            {
                "text": "NewConnect is the alternative trading system for emerging Polish companies operated by the Warsaw Stock Exchange. Companies on NewConnect typically have higher risk and lower liquidity than main market companies.",
                "category": "market_structure",
                "source": "GPW Official"
            },
            {
                "text": "Polish companies must comply with IFRS or Polish GAAP reporting standards. Quarterly and annual financial reports are required, with specific disclosure requirements for financial metrics.",
                "category": "accounting",
                "source": "Polish Accounting Standards"
            },
            {
                "text": "Market capitalisation weighting is used in Polish stock indices. Large-cap companies (WIG20) have more influence on index movements than mid-cap (sWIG80) and small-cap companies.",
                "category": "index_methodology",
                "source": "GPW Methodology"
            },
            {
                "text": "Polish financial markets are regulated by the Polish Financial Supervision Authority (KNF), which oversees securities trading, market integrity, and investor protection.",
                "category": "regulatory",
                "source": "KNF Website"
            },
            {
                "text": "Dividend policy in Poland follows European standards. Companies typically pay dividends annually or semi-annually, with yield calculations based on current market price.",
                "category": "corporate_governance",
                "source": "Market Practices"
            }
        ]
        
        self._insert_knowledge_entries(regulations)
        logger.info("Loaded financial regulations and market structure data")
    
    def _load_market_concepts(self):
        """Load financial concepts and analysis frameworks."""
        concepts = [
            {
                "text": "P/E ratio (Price-to-Earnings) measures how much investors are willing to pay for each dollar of earnings. A high P/E ratio may indicate overvaluation, while a low P/E may suggest undervaluation or poor growth prospects.",
                "category": "valuation_metrics",
                "source": "Financial Analysis Theory"
            },
            {
                "text": "P/B ratio (Price-to-Book) compares market price to book value. A P/B ratio above 1.0 suggests the market values the company more than its book value, which may indicate growth expectations or overvaluation.",
                "category": "valuation_metrics",
                "source": "Financial Analysis Theory"
            },
            {
                "text": "Market capitalization weighting means larger companies have more impact on index performance. In WIG20, the largest 20 companies by market cap determine most of the index movement.",
                "category": "index_methodology",
                "source": "Portfolio Theory"
            },
            {
                "text": "Overvaluation occurs when a stock trades above its intrinsic value. Warning signs include P/E ratios significantly above market average, low dividend yields, and high price momentum without fundamental justification.",
                "category": "risk_assessment",
                "source": "Value Investing Principles"
            },
            {
                "text": "Volume analysis in Polish markets considers both trading volume and turnover value. High volume with price increases may indicate strong buying interest, while low volume with price changes may suggest market manipulation.",
                "category": "market_analysis",
                "source": "Technical Analysis"
            },
            {
                "text": "Sector analysis in Polish markets typically groups companies by industry: banking, energy, mining, technology, consumer goods, and real estate. Each sector has different valuation multiples and growth patterns.",
                "category": "sector_analysis",
                "source": "Market Research"
            },
            {
                "text": "Risk assessment in Polish equities considers market risk, sector risk, and company-specific risk. Emerging market factors, currency fluctuations, and political stability also affect Polish stock valuations.",
                "category": "risk_assessment",
                "source": "Risk Management Theory"
            },
            {
                "text": "Liquidity analysis examines trading volume and bid-ask spreads. Polish mid-cap stocks (sWIG80) generally have lower liquidity than large-cap stocks, affecting price discovery and transaction costs.",
                "category": "market_analysis",
                "source": "Market Microstructure"
            }
        ]
        
        self._insert_knowledge_entries(concepts)
        logger.info("Loaded financial concepts and analysis frameworks")
    
    def _load_wig80_data(self):
        """Load WIG80 company data from the existing dataset."""
        try:
            with open("/workspace/data/wig80_current_data.json", "r") as f:
                wig80_data = json.load(f)
            
            # Extract companies data from the correct structure
            companies = []
            if "companies" in wig80_data:
                companies = wig80_data["companies"]
            else:
                logger.warning("No companies data found in wig80_current_data.json")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for company in companies:
                if isinstance(company, dict) and "symbol" in company:
                    cursor.execute("""
                        INSERT OR REPLACE INTO wgi80_companies 
                        (symbol, company_name, financial_data, last_updated)
                        VALUES (?, ?, ?, ?)
                    """, (
                        company["symbol"],
                        company["company_name"],
                        json.dumps(company),
                        datetime.now().isoformat()
                    ))
            
            conn.commit()
            conn.close()
            logger.info(f"Loaded {len(companies)} WIG80 companies data")
            
        except Exception as e:
            logger.error(f"Error loading WIG80 data: {e}")
    
    def _insert_knowledge_entries(self, entries: List[Dict]):
        """Insert knowledge entries into the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for entry in entries:
            cursor.execute("""
                INSERT INTO knowledge_entries (text, category, source, metadata)
                VALUES (?, ?, ?, ?)
            """, (entry["text"], entry["category"], entry["source"], json.dumps({})))
        
        conn.commit()
        conn.close()

class VectorEmbedder:
    """Simple vector embedding system for financial text and data."""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vocabulary = {}
        self._build_vocabulary()
    
    def _build_vocabulary(self):
        """Build vocabulary from financial terms and concepts."""
        financial_terms = [
            "valuation", "earnings", "profit", "revenue", "debt", "equity", "assets", 
            "liabilities", "cash_flow", "dividend", "yield", "growth", "risk", "return",
            "market", "capital", "price", "ratio", "analysis", "financial", "accounting",
            "polish", "pln", "gpw", "wig20", "sWIG80", "knf", "regulatory", "compliance",
            "overvalued", "undervalued", "bubble", "correction", "trading", "volume",
            "liquidity", "bid", "ask", "spread", "momentum", "technical", "fundamental",
            "sector", "industry", "banking", "energy", "mining", "technology", "retail",
            "real_estate", "insurance", "pharmaceutical", "telecom", "utilities",
            "pe_ratio", "pb_ratio", "roe", "roa", "eps", "book_value", "market_cap",
            "volatility", "beta", "alpha", "sharpe", "diversification", "portfolio",
            "investment", "stock", "bond", "derivative", "option", "future", "index",
            "performance", "benchmark", "tracking", "error", "correlation", "covariance",
            "variance", "standard_deviation", "confidence", "interval", "hypothesis",
            "testing", "significance", "p_value", "regression", "modeling", "forecasting",
            "scenario", "sensitivity", "stress_test", "black_swan", "contagion",
            "crisis", "recession", "expansion", "cycle", "phase", "trend", "pattern",
            "signal", "noise", "efficiency", "information", "news", "event", "announcement",
            "earnings_call", "guidance", "forecast", "estimate", "consensus", "surprise",
            "upgrade", "downgrade", "rating", "credit", "rating_agency", "fitch",
            "moodys", "sp", "standard_poors", "investment_grade", "high_yield", "junk",
            "currency", "exchange_rate", "hedge", "hedging", "basis", "contango", "backwardation"
        ]
        
        for i, term in enumerate(financial_terms):
            self.vocabulary[term] = i
    
    def embed_text(self, text: str) -> List[float]:
        """Create a simple vector embedding based on term frequency."""
        vector = [0.0] * self.dimension
        
        # Simple bag-of-words approach
        words = text.lower().split()
        term_counts = {}
        
        for word in words:
            if word in self.vocabulary:
                term_counts[word] = term_counts.get(word, 0) + 1
        
        # Normalize by vocabulary size
        for word, count in term_counts.items():
            idx = self.vocabulary[word] % self.dimension
            vector[idx] = count / len(words)
        
        # Add some financial-specific features
        if "overvalued" in text.lower() or "overvaluation" in text.lower():
            vector[0] = 1.0
        if "undervalued" in text.lower() or "undervaluation" in text.lower():
            vector[1] = 1.0
        if "high risk" in text.lower() or "volatile" in text.lower():
            vector[2] = 1.0
        if "pe ratio" in text.lower() or "p/e" in text.lower():
            vector[3] = 1.0
        if "pb ratio" in text.lower() or "p/b" in text.lower():
            vector[4] = 1.0
        
        # Add Polish market specifics
        if "polish" in text.lower() or "poland" in text.lower():
            vector[5] = 1.0
        if "wig" in text.lower() or "wig20" in text.lower() or "sWIG80" in text.lower():
            vector[6] = 1.0
        if "pln" in text.lower():
            vector[7] = 1.0
        
        # Normalize vector to unit length
        norm = sum(x*x for x in vector) ** 0.5
        if norm > 0:
            vector = [x/norm for x in vector]
        
        return vector
    
    def embed_company_data(self, company: CompanyData) -> List[float]:
        """Create embedding for company financial data."""
        vector = [0.0] * self.dimension
        
        # Add financial ratios to embedding
        if company.pe_ratio is not None:
            # Normalize P/E ratio (typical range 0-50)
            pe_norm = min(company.pe_ratio / 50.0, 1.0)
            vector[10] = pe_norm
        
        if company.pb_ratio is not None:
            # Normalize P/B ratio (typical range 0-10)
            pb_norm = min(company.pb_ratio / 10.0, 1.0)
            vector[11] = pb_norm
        
        # Add price movement
        vector[12] = company.change_percent / 100.0  # Normalized change
        
        # Add volume indicator (log scale)
        if company.trading_volume_pln > 0:
            vol_log = min(np.log10(company.trading_volume_pln) / 9.0, 1.0)  # 1M to 1B range
            vector[13] = vol_log
        
        # Market cap if available
        if company.market_cap is not None:
            cap_log = min(np.log10(company.market_cap) / 12.0, 1.0)  # 1M to 1T range
            vector[14] = cap_log
        
        # Risk indicators
        if company.pe_ratio is not None and company.pe_ratio > 30:
            vector[15] = 1.0  # High P/E risk
        if company.pb_ratio is not None and company.pb_ratio > 5:
            vector[16] = 1.0  # High P/B risk
        if company.change_percent < -5:
            vector[17] = 1.0  # Significant decline
        
        return vector

class VectorStore:
    """Simple vector store for similarity search."""
    
    def __init__(self, db_path: str = "/workspace/data/rag_knowledge.db"):
        self.db_path = db_path
    
    def store_embedding(self, embedding: EmbeddingVector):
        """Store an embedding in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO embeddings 
            (id, vector, text, metadata, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            embedding.id,
            pickle.dumps(embedding.vector),
            embedding.text,
            json.dumps(embedding.metadata),
            embedding.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def search(self, query_vector: List[float], limit: int = 10) -> List[QueryResult]:
        """Search for similar embeddings using cosine similarity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, vector, text, metadata FROM embeddings")
        results = []
        
        for row in cursor.fetchall():
            stored_vector = pickle.loads(row[1])
            similarity = self._cosine_similarity(query_vector, stored_vector)
            
            results.append(QueryResult(
                text=row[2],
                score=similarity,
                metadata=json.loads(row[3]) if row[3] else {},
                source=row[0]
            ))
        
        conn.close()
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

class PolishFinancialRAG:
    """Main RAG system for Polish financial market analysis."""
    
    def __init__(self, db_path: str = "/workspace/data/rag_knowledge.db"):
        self.knowledge_base = PolishFinancialKnowledgeBase(db_path)
        self.embedder = VectorEmbedder()
        self.vector_store = VectorStore(db_path)
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize embeddings for all knowledge entries."""
        logger.info("Initializing embeddings...")
        
        # Create embeddings for knowledge entries
        conn = sqlite3.connect(self.knowledge_base.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, text, category, source FROM knowledge_entries")
        entries = cursor.fetchall()
        
        for entry_id, text, category, source in entries:
            vector = self.embedder.embed_text(text)
            embedding = EmbeddingVector(
                id=f"knowledge_{entry_id}",
                vector=vector,
                text=text,
                metadata={"category": category, "source": source},
                created_at=datetime.now()
            )
            self.vector_store.store_embedding(embedding)
        
        # Create embeddings for WIG80 companies
        cursor.execute("SELECT symbol, company_name, financial_data FROM wgi80_companies")
        companies = cursor.fetchall()
        
        for symbol, company_name, financial_data_str in companies:
            try:
                financial_data = json.loads(financial_data_str)
                company = CompanyData(
                    symbol=symbol,
                    company_name=company_name,
                    current_price=financial_data.get("current_price", 0.0),
                    change_percent=financial_data.get("change_percent", 0.0),
                    pe_ratio=financial_data.get("pe_ratio"),
                    pb_ratio=financial_data.get("pb_ratio"),
                    trading_volume=financial_data.get("trading_volume", "0"),
                    trading_volume_pln=self._parse_volume_pln(financial_data.get("trading_volume_obrot", "0M PLN"))
                )
                
                vector = self.embedder.embed_company_data(company)
                embedding = EmbeddingVector(
                    id=f"company_{symbol}",
                    vector=vector,
                    text=f"{company_name} ({symbol}) - P/E: {company.pe_ratio}, P/B: {company.pb_ratio}",
                    metadata={
                        "type": "company",
                        "symbol": symbol,
                        "company_name": company_name,
                        "financial_data": financial_data
                    },
                    created_at=datetime.now()
                )
                self.vector_store.store_embedding(embedding)
            except Exception as e:
                logger.error(f"Error creating embedding for {symbol}: {e}")
        
        conn.close()
        logger.info(f"Created embeddings for {len(entries)} knowledge entries and {len(companies)} companies")
    
    def _parse_volume_pln(self, volume_str: str) -> float:
        """Parse trading volume string to numeric PLN value."""
        if not volume_str:
            return 0.0
        
        try:
            # Handle formats like "1.5M PLN", "250K PLN", etc.
            if "M" in volume_str:
                number = float(volume_str.replace("M PLN", "").replace("M", ""))
                return number * 1_000_000
            elif "K" in volume_str:
                number = float(volume_str.replace("K PLN", "").replace("K", ""))
                return number * 1_000
            else:
                return float(volume_str.replace(" PLN", ""))
        except:
            return 0.0
    
    def query(self, user_query: str, query_type: QueryType = QueryType.VALUATION_ANALYSIS) -> Dict[str, Any]:
        """Process a user query and return relevant information."""
        logger.info(f"Processing query: {user_query} (type: {query_type.value})")
        
        # Create query embedding
        query_vector = self.embedder.embed_text(user_query)
        
        # Search for relevant information
        relevant_info = self.vector_store.search(query_vector, limit=15)
        
        # Generate response based on query type
        response = self._generate_response(user_query, query_type, relevant_info)
        
        return {
            "query": user_query,
            "query_type": query_type.value,
            "response": response,
            "sources": [result.source for result in relevant_info[:5]],
            "confidence": self._calculate_confidence(relevant_info[:5]),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_response(self, query: str, query_type: QueryType, relevant_info: List[QueryResult]) -> str:
        """Generate a contextual response based on the query and retrieved information."""
        
        if query_type == QueryType.OVERVALUATION_DETECTION:
            return self._generate_overvaluation_response(query, relevant_info)
        elif query_type == QueryType.VALUATION_ANALYSIS:
            return self._generate_valuation_response(query, relevant_info)
        elif query_type == QueryType.MARKET_COMPARISON:
            return self._generate_comparison_response(query, relevant_info)
        elif query_type == QueryType.FINANCIAL_HEALTH:
            return self._generate_health_response(query, relevant_info)
        elif query_type == QueryType.SECTOR_ANALYSIS:
            return self._generate_sector_response(query, relevant_info)
        elif query_type == QueryType.REGULATORY_INFO:
            return self._generate_regulatory_response(query, relevant_info)
        else:
            return self._generate_general_response(query, relevant_info)
    
    def _generate_overvaluation_response(self, query: str, relevant_info: List[QueryResult]) -> str:
        """Generate response for overvaluation detection queries."""
        response = "## Overvaluation Analysis\n\n"
        
        # Check for company-specific queries
        company_symbol = self._extract_company_symbol(query)
        if company_symbol:
            response += f"**Analysis for {company_symbol}:**\n\n"
            response += self._analyze_company_overvaluation(company_symbol)
        else:
            response += "Based on the financial data and market analysis:\n\n"
            
            # Get valuation metrics from relevant info
            valuation_info = [info for info in relevant_info if "valuation" in info.metadata.get("category", "")]
            risk_info = [info for info in relevant_info if "risk" in info.metadata.get("category", "")]
            
            if valuation_info:
                response += "### Key Valuation Metrics:\n"
                response += f"- {valuation_info[0].text}\n\n"
            
            if risk_info:
                response += "### Risk Indicators:\n"
                response += f"- {risk_info[0].text}\n\n"
        
        # Add general overvaluation warnings
        response += "### Overvaluation Warning Signs:\n"
        response += "1. **P/E Ratio**: Values above 30-35 may indicate overvaluation\n"
        response += "2. **P/B Ratio**: Values above 5-7 suggest high price-to-book premium\n"
        response += "3. **Price Momentum**: Sustained gains without fundamental justification\n"
        response += "4. **Low Dividend Yields**: Companies not returning value to shareholders\n"
        response += "5. **Market Cap Growth**: Rapid expansion without proportional earnings growth\n\n"
        
        response += "**Recommendation**: Always combine quantitative metrics with qualitative analysis and market context."
        
        return response
    
    def _generate_valuation_response(self, query: str, relevant_info: List[QueryResult]) -> str:
        """Generate response for general valuation analysis."""
        response = "## Valuation Analysis\n\n"
        
        response += "### Current Market Context:\n"
        response += "The Polish financial market (GPW) consists of three main segments:\n"
        response += "1. **WIG20**: 20 largest companies by market capitalization\n"
        response += "2. **sWIG80**: 80 mid-cap companies (WIG80)\n"
        response += "3. **NewConnect**: Alternative market for emerging companies\n\n"
        
        response += "### Key Valuation Metrics:\n"
        for info in relevant_info[:3]:
            if "valuation" in info.metadata.get("category", ""):
                response += f"- {info.text}\n"
        
        response += "\n### Analysis Framework:\n"
        response += "1. **Relative Valuation**: Compare P/E and P/B ratios to market averages\n"
        response += "2. **Absolute Valuation**: Assess intrinsic value using DCF or asset-based models\n"
        response += "3. **Sector Comparison**: Analyze multiples within industry peers\n"
        response += "4. **Market Cycle**: Consider current market phase and economic conditions\n\n"
        
        return response
    
    def _generate_comparison_response(self, query: str, relevant_info: List[QueryResult]) -> str:
        """Generate response for market comparison queries."""
        response = "## Market Comparison Analysis\n\n"
        
        response += "### Polish Market Structure:\n"
        response += "- **WIG20**: Large-cap benchmark index representing ~70% of market cap\n"
        response += "- **sWIG80**: Mid-cap segment with higher growth potential and risk\n"
        response += "- **Market Cap Weighting**: Larger companies have disproportionate index influence\n\n"
        
        response += "### International Context:\n"
        response += "Polish markets (as part of emerging European markets) typically exhibit:\n"
        response += "- Higher volatility compared to developed markets\n"
        response += "- Currency risk (PLN fluctuations)\n"
        response += "- Political and economic transition factors\n"
        response += "- Regulatory convergence with EU standards\n\n"
        
        return response
    
    def _generate_health_response(self, query: str, relevant_info: List[QueryResult]) -> str:
        """Generate response for financial health analysis."""
        response = "## Financial Health Assessment\n\n"
        
        response += "### Key Health Indicators:\n"
        response += "1. **Liquidity Analysis**: Trading volume and bid-ask spreads\n"
        response += "2. **Profitability Metrics**: ROE, ROA, and margin analysis\n"
        response += "3. **Leverage Assessment**: Debt-to-equity ratios\n"
        response += "4. **Cash Flow Quality**: Operating vs. financing cash flows\n\n"
        
        response += "### Risk Assessment Framework:\n"
        for info in relevant_info:
            if "risk" in info.metadata.get("category", ""):
                response += f"- {info.text}\n"
        
        return response
    
    def _generate_sector_response(self, query: str, relevant_info: List[QueryResult]) -> str:
        """Generate response for sector analysis."""
        response = "## Sector Analysis\n\n"
        
        response += "### Major Sectors in Polish Markets:\n"
        response += "1. **Banking**: Largest sector by market cap (PKO BP, Pekao, Santander)\n"
        response += "2. **Energy**: Coal, renewables, and utilities (PGE, Tauron, Energa)\n"
        response += "3. **Mining**: Copper and precious metals (KGHM)\n"
        response += "4. **Technology**: Growing segment with international exposure\n"
        response += "5. **Real Estate**: Property developers and REITs\n"
        response += "6. **Consumer**: Retail and consumer goods\n\n"
        
        return response
    
    def _generate_regulatory_response(self, query: str, relevant_info: List[QueryResult]) -> str:
        """Generate response for regulatory information."""
        response = "## Regulatory Information\n\n"
        
        response += "### Key Regulatory Bodies:\n"
        response += "- **KNF (Polish Financial Supervision Authority)**: Main regulator\n"
        response += "- **GPW (Warsaw Stock Exchange)**: Market operator\n"
        response += "- **MF (Ministry of Finance)**: Fiscal policy coordination\n\n"
        
        response += "### Compliance Requirements:\n"
        for info in relevant_info:
            if "regulatory" in info.metadata.get("category", ""):
                response += f"- {info.text}\n"
        
        return response
    
    def _generate_general_response(self, query: str, relevant_info: List[QueryResult]) -> str:
        """Generate general response for other query types."""
        response = "## General Market Information\n\n"
        
        response += "Based on your query, here are the key points:\n\n"
        
        for i, info in enumerate(relevant_info[:5], 1):
            response += f"{i}. {info.text}\n\n"
        
        response += "**Note**: This analysis is based on historical data and should be combined with current market information for investment decisions."
        
        return response
    
    def _extract_company_symbol(self, query: str) -> Optional[str]:
        """Extract company symbol from query if present."""
        # Simple pattern matching for Polish stock symbols
        import re
        
        # Look for 3-4 character symbols
        symbols = re.findall(r'\b[A-Z]{3,4}\b', query.upper())
        return symbols[0] if symbols else None
    
    def _analyze_company_overvaluation(self, symbol: str) -> str:
        """Analyze overvaluation for a specific company."""
        conn = sqlite3.connect(self.knowledge_base.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT financial_data FROM wgi80_companies WHERE symbol = ?", (symbol,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return f"No financial data found for {symbol}."
        
        try:
            financial_data = json.loads(result[0])
            
            analysis = []
            pe_ratio = financial_data.get("pe_ratio")
            pb_ratio = financial_data.get("pb_ratio")
            current_price = financial_data.get("current_price", 0)
            
            if pe_ratio is not None:
                if pe_ratio > 35:
                    analysis.append(f"⚠️ **High P/E Ratio**: {pe_ratio:.2f} - May indicate overvaluation")
                elif pe_ratio < 10:
                    analysis.append(f"📈 **Low P/E Ratio**: {pe_ratio:.2f} - Potential value opportunity")
                else:
                    analysis.append(f"✅ **P/E Ratio**: {pe_ratio:.2f} - Within normal range")
            
            if pb_ratio is not None:
                if pb_ratio > 7:
                    analysis.append(f"⚠️ **High P/B Ratio**: {pb_ratio:.2f} - Premium valuation")
                elif pb_ratio < 1:
                    analysis.append(f"📈 **Low P/B Ratio**: {pb_ratio:.2f} - Potential undervaluation")
                else:
                    analysis.append(f"✅ **P/B Ratio**: {pb_ratio:.2f} - Reasonable valuation")
            
            change_percent = financial_data.get("change_percent", 0)
            if change_percent > 5:
                analysis.append(f"🚀 **Strong Performance**: +{change_percent:.2f}% - Monitor for sustainability")
            elif change_percent < -5:
                analysis.append(f"📉 **Significant Decline**: {change_percent:.2f}% - Investigate reasons")
            
            return "\n".join(analysis) if analysis else "Insufficient data for detailed analysis."
            
        except Exception as e:
            return f"Error analyzing {symbol}: {str(e)}"
    
    def _calculate_confidence(self, results: List[QueryResult]) -> float:
        """Calculate confidence score for the response based on retrieval results."""
        if not results:
            return 0.0
        
        # Average similarity score
        avg_score = sum(result.score for result in results) / len(results)
        
        # Number of relevant results
        relevant_count = sum(1 for result in results if result.score > 0.3)
        relevance_factor = relevant_count / len(results)
        
        # Combine factors
        confidence = (avg_score * 0.7) + (relevance_factor * 0.3)
        
        return min(confidence, 1.0)
    
    def get_company_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get detailed analysis for a specific company."""
        conn = sqlite3.connect(self.knowledge_base.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT financial_data, company_name FROM wgi80_companies WHERE symbol = ?", (symbol,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {"error": f"No data found for {symbol}"}
        
        try:
            financial_data = json.loads(result[0])
            company_name = result[1]
            
            # Create query for company-specific analysis
            query = f"Analyze {symbol} {company_name} overvaluation risk financial health"
            company_vector = self.embedder.embed_text(query)
            
            # Get relevant knowledge
            relevant_info = self.vector_store.search(company_vector, limit=10)
            
            return {
                "symbol": symbol,
                "company_name": company_name,
                "financial_data": financial_data,
                "analysis": self._analyze_company_overvaluation(symbol),
                "market_context": [info.text for info in relevant_info[:3]],
                "risk_level": self._assess_risk_level(financial_data),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error analyzing {symbol}: {str(e)}"}
    
    def _assess_risk_level(self, financial_data: Dict) -> str:
        """Assess risk level based on financial data."""
        risk_score = 0
        
        pe_ratio = financial_data.get("pe_ratio")
        if pe_ratio is not None:
            if pe_ratio > 40:
                risk_score += 3
            elif pe_ratio > 25:
                risk_score += 2
            elif pe_ratio > 15:
                risk_score += 1
        
        pb_ratio = financial_data.get("pb_ratio")
        if pb_ratio is not None:
            if pb_ratio > 8:
                risk_score += 3
            elif pb_ratio > 5:
                risk_score += 2
            elif pb_ratio > 3:
                risk_score += 1
        
        change_percent = financial_data.get("change_percent", 0)
        if abs(change_percent) > 10:
            risk_score += 2
        elif abs(change_percent) > 5:
            risk_score += 1
        
        if risk_score >= 6:
            return RiskLevel.CRITICAL.value
        elif risk_score >= 4:
            return RiskLevel.HIGH.value
        elif risk_score >= 2:
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get a summary of the current market state."""
        conn = sqlite3.connect(self.knowledge_base.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM wgi80_companies")
        total_companies = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(CAST(json_extract(financial_data, '$.pe_ratio') AS REAL)) FROM wgi80_companies WHERE json_extract(financial_data, '$.pe_ratio') IS NOT NULL")
        avg_pe = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT AVG(CAST(json_extract(financial_data, '$.pb_ratio') AS REAL)) FROM wgi80_companies WHERE json_extract(financial_data, '$.pb_ratio') IS NOT NULL")
        avg_pb = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_companies": total_companies,
            "average_pe_ratio": round(avg_pe, 2),
            "average_pb_ratio": round(avg_pb, 2),
            "market_status": "Data collected from Warsaw Stock Exchange",
            "last_update": datetime.now().isoformat(),
            "currency": "PLN (Polish Złoty)",
            "exchange": "GPW (Giełda Papierów Wartościowych w Warszawie)"
        }

# Prompt Engineering Templates
class PromptTemplates:
    """Templates for generating prompts for different analysis types."""
    
    @staticmethod
    def valuation_analysis_template(company_data: Dict, market_context: str) -> str:
        """Template for valuation analysis prompts."""
        return f"""
        You are a financial analyst specializing in Polish markets. Analyze the following company data:
        
        Company: {company_data.get('company_name', 'N/A')} ({company_data.get('symbol', 'N/A')})
        Current Price: {company_data.get('current_price', 'N/A')} PLN
        P/E Ratio: {company_data.get('pe_ratio', 'N/A')}
        P/B Ratio: {company_data.get('pb_ratio', 'N/A')}
        Daily Change: {company_data.get('change_percent', 'N/A')}%
        Trading Volume: {company_data.get('trading_volume', 'N/A')}
        
        Market Context: {market_context}
        
        Provide a comprehensive valuation analysis including:
        1. Assessment of current valuation metrics
        2. Comparison to market averages
        3. Identification of potential overvaluation/undervaluation signals
        4. Risk factors specific to this company
        5. Investment recommendation with justification
        
        Focus on Polish market specifics and regulatory environment.
        """
    
    @staticmethod
    def overvaluation_detection_template(company_data: Dict, sector_context: str) -> str:
        """Template for overvaluation detection."""
        return f"""
        Act as a value investor analyzing potential overvaluation in Polish markets.
        
        Company Analysis: {company_data.get('company_name', 'N/A')} ({company_data.get('symbol', 'N/A')})
        Valuation Metrics:
        - P/E: {company_data.get('pe_ratio', 'N/A')}
        - P/B: {company_data.get('pb_ratio', 'N/A')}
        - Price Movement: {company_data.get('change_percent', 'N/A')}%
        
        Sector Context: {sector_context}
        
        Evaluate:
        1. Warning signs of overvaluation
        2. Historical valuation ranges for similar companies
        3. Market conditions that might justify high valuations
        4. Potential catalysts for valuation compression
        5. Specific red flags to monitor
        
        Provide actionable insights for Polish market investors.
        """
    
    @staticmethod
    def risk_assessment_template(company_data: Dict, market_conditions: str) -> str:
        """Template for risk assessment."""
        return f"""
        You are a risk management expert focusing on Polish equity markets.
        
        Risk Analysis for: {company_data.get('company_name', 'N/A')} ({company_data.get('symbol', 'N/A')})
        
        Current Market Conditions: {market_conditions}
        
        Assess:
        1. Company-specific risks (financial, operational, governance)
        2. Sector risks and cyclical factors
        3. Market and liquidity risks
        4. Currency and political risks (PLN, Polish regulatory environment)
        5. Black swan event preparedness
        
        Provide a risk rating and mitigation strategies.
        """

def main():
    """Main function to demonstrate the RAG system."""
    print("🚀 Initializing Polish Financial Market RAG System...")
    
    # Initialize the RAG system
    rag = PolishFinancialRAG()
    
    # Get market summary
    market_summary = rag.get_market_summary()
    print(f"\n📊 Market Summary:")
    print(f"Total Companies: {market_summary['total_companies']}")
    print(f"Average P/E: {market_summary['average_pe_ratio']}")
    print(f"Average P/B: {market_summary['average_pb_ratio']}")
    
    # Example queries
    example_queries = [
        {
            "query": "Analyze KGHM for overvaluation risk",
            "type": QueryType.OVERVALUATION_DETECTION
        },
        {
            "query": "What are the key valuation metrics for Polish banking sector?",
            "type": QueryType.SECTOR_ANALYSIS
        },
        {
            "query": "Explain the Polish financial regulatory framework",
            "type": QueryType.REGULATORY_INFO
        },
        {
            "query": "Compare WIG20 vs sWIG80 market performance",
            "type": QueryType.MARKET_COMPARISON
        }
    ]
    
    print(f"\n🔍 Example Analysis Results:")
    for i, example in enumerate(example_queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Query: {example['query']}")
        result = rag.query(example['query'], example['type'])
        print(f"Response Preview: {result['response'][:200]}...")
        print(f"Confidence: {result['confidence']:.2f}")
    
    # Company-specific analysis
    company_analysis = rag.get_company_analysis("KGH")
    if "error" not in company_analysis:
        print(f"\n🏢 Company Analysis Example (KGH):")
        print(f"Company: {company_analysis['company_name']}")
        print(f"Analysis: {company_analysis['analysis']}")
        print(f"Risk Level: {company_analysis['risk_level']}")
    
    print(f"\n✅ RAG System initialized and tested successfully!")
    print(f"💾 Knowledge base stored at: /workspace/data/rag_knowledge.db")

if __name__ == "__main__":
    main()