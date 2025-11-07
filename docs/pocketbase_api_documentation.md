# WIG80 Pocketbase API Documentation v2.0

## Overview

The WIG80 Pocketbase API provides comprehensive REST endpoints for WIG80 stock data analysis, including historical prices, technical analysis, AI insights, and market correlations. This API is designed for financial applications, trading platforms, and market analysis tools.

**Base URL:** `http://localhost:8090`  
**API Version:** 2.0.0  
**Authentication:** Bearer Token  
**Rate Limiting:** 100 requests/hour (authenticated), 10 requests/minute (unauthenticated)  

---

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [Stock Data Endpoints](#stock-data-endpoints)
4. [Technical Analysis Endpoints](#technical-analysis-endpoints)
5. [AI Insights Endpoints](#ai-insights-endpoints)
6. [Market Correlation Endpoints](#market-correlation-endpoints)
7. [Utility Endpoints](#utility-endpoints)
8. [Data Models](#data-models)
9. [Error Handling](#error-handling)
10. [Code Examples](#code-examples)
11. [Integration Guides](#integration-guides)

---

## Authentication

The API uses Bearer token authentication. Clients must obtain a token by calling the login endpoint.

### Login

```http
POST /api/auth/login
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response:**
```json
{
    "success": true,
    "token": "abc123def456",
    "user": "admin",
    "expires_in": 3600
}
```

**Usage:**
```http
Authorization: Bearer abc123def456
```

### Sample Login Code

#### JavaScript (Node.js)
```javascript
const axios = require('axios');

async function login() {
    try {
        const response = await axios.post('http://localhost:8090/api/auth/login', {
            username: 'admin',
            password: 'admin123'
        });
        
        const token = response.data.token;
        console.log('Token:', token);
        
        // Store token for subsequent requests
        return token;
    } catch (error) {
        console.error('Login failed:', error.response.data);
    }
}
```

#### Python
```python
import requests

def login():
    url = 'http://localhost:8090/api/auth/login'
    data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        token = response.json()['token']
        print(f'Token: {token}')
        return token
    else:
        print(f'Login failed: {response.text}')
        return None
```

---

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Unauthenticated requests:** 10 requests per minute
- **Authenticated requests:** 100 requests per hour per token
- **Authentication endpoint:** 10 requests per 5 minutes

**Rate Limit Headers:**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Stock Data Endpoints

### Get All Stocks

Retrieve stock data for all WIG80 companies or filter by symbol.

```http
GET /api/stocks
Authorization: Bearer {token}
```

**Query Parameters:**
- `symbol` (optional): Filter by specific stock symbol
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `limit` (optional): Maximum number of records (default: 100)

**Example Request:**
```http
GET /api/stocks?symbol=PKN_ORLEN&start_date=2025-01-01&limit=50
```

**Response:**
```json
[
    {
        "symbol": "PKN_ORLEN",
        "timestamp": "2025-11-06T20:23:56",
        "open_price": 65.50,
        "high_price": 67.20,
        "low_price": 64.80,
        "close_price": 66.90,
        "volume": 1250000,
        "macd": 0.25,
        "rsi": 58.5,
        "bb_upper": 68.40,
        "bb_lower": 63.50,
        "sma_20": 65.20,
        "ema_20": 65.80
    }
]
```

### Get Stock Details

Get detailed data for a specific company.

```http
GET /api/stocks/{symbol}
Authorization: Bearer {token}
```

**Example Request:**
```http
GET /api/stocks/KGHM
```

### Get Companies List

Retrieve the list of WIG80 companies.

```http
GET /api/companies
Authorization: Bearer {token}
```

**Query Parameters:**
- `active_only` (optional): Return only active companies (default: true)

**Response:**
```json
{
    "companies": [
        {
            "symbol": "PKN_ORLEN",
            "name": "PKN Orlen SA",
            "sector": "Oil & Gas",
            "market_cap": 25000000000,
            "is_active": true
        }
    ],
    "total": 88
}
```

---

## Technical Analysis Endpoints

### Get Technical Analysis

Retrieve technical analysis indicators for a specific stock.

```http
GET /api/technical/{symbol}?period=14&indicators=macd,rsi,bb
Authorization: Bearer {token}
```

**Path Parameters:**
- `symbol`: Stock symbol

**Query Parameters:**
- `period` (optional): Analysis period (default: 14)
- `indicators` (optional): Comma-separated list of indicators (macd, rsi, bb, sma, ema)

**Available Indicators:**
- `macd`: Moving Average Convergence Divergence
- `rsi`: Relative Strength Index
- `bb` or `bollinger`: Bollinger Bands
- `sma`: Simple Moving Average
- `ema`: Exponential Moving Average

**Example Request:**
```http
GET /api/technical/PKN_ORLEN?period=14&indicators=macd,rsi,bb
```

**Response:**
```json
{
    "symbol": "PKN_ORLEN",
    "period": 14,
    "indicators": {
        "macd": {
            "macd": 0.25,
            "signal": 0.18,
            "histogram": 0.07
        },
        "rsi": {
            "value": 58.5,
            "signal": "neutral"
        },
        "bollinger_bands": {
            "upper": 68.40,
            "middle": 65.20,
            "lower": 63.50,
            "position": "middle"
        }
    },
    "timestamp": "2025-11-06T20:23:56"
}
```

### Technical Analysis Code Examples

#### JavaScript
```javascript
async function getTechnicalAnalysis(symbol, indicators = ['macd', 'rsi', 'bb']) {
    try {
        const response = await axios.get(
            `http://localhost:8090/api/technical/${symbol}`,
            {
                params: { indicators: indicators.join(',') },
                headers: { Authorization: `Bearer ${token}` }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Technical analysis error:', error.response.data);
    }
}

// Usage
getTechnicalAnalysis('PKN_ORLEN', ['macd', 'rsi', 'bb']).then(data => {
    console.log('MACD:', data.indicators.macd);
    console.log('RSI:', data.indicators.rsi);
    console.log('Bollinger Bands:', data.indicators.bollinger_bands);
});
```

#### Python
```python
import requests

def get_technical_analysis(symbol, indicators=['macd', 'rsi', 'bb']):
    url = f'http://localhost:8090/api/technical/{symbol}'
    params = {'indicators': ','.join(indicators)}
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return None

# Usage
data = get_technical_analysis('PKN_ORLEN', ['macd', 'rsi', 'bb'])
if data:
    print(f"MACD: {data['indicators']['macd']}")
    print(f"RSI: {data['indicators']['rsi']}")
```

---

## AI Insights Endpoints

### Get AI Insights

Retrieve AI-generated market insights.

```http
GET /api/ai-insights
Authorization: Bearer {token}
```

**Query Parameters:**
- `symbol` (optional): Filter by specific stock symbol
- `min_confidence` (optional): Minimum confidence score (0.0-1.0)
- `limit` (optional): Maximum number of insights (default: 50)

**Response:**
```json
[
    {
        "id": 123,
        "timestamp": "2025-11-06T20:23:56",
        "symbol": "KGHM",
        "insight_type": "overvaluation",
        "result": {
            "status": "overvalued",
            "overvaluation_score": 25.5,
            "pe_analysis": {
                "current_pe": 18.5,
                "historical_pe": 14.2,
                "deviation_percent": 30.3
            },
            "pb_analysis": {
                "current_pb": 1.8,
                "historical_pb": 1.4,
                "deviation_percent": 28.6
            },
            "recommendation": "sell",
            "confidence": 0.85
        },
        "confidence": 0.85
    }
]
```

### Generate AI Insights

Trigger AI analysis for a specific stock and analysis type.

```http
POST /api/ai-insights/generate
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
    "symbol": "KGHM",
    "analysis_type": "overvaluation"
}
```

**Available Analysis Types:**
- `overvaluation`: Fundamental overvaluation analysis
- `trend`: Price trend and momentum analysis
- `volatility`: Volatility and risk analysis

**Response:**
```json
{
    "success": true,
    "insight_id": 124,
    "symbol": "KGHM",
    "analysis_type": "overvaluation",
    "result": {
        "status": "overvalued",
        "overvaluation_score": 25.5,
        "pe_analysis": {
            "current_pe": 18.5,
            "historical_pe": 14.2,
            "deviation_percent": 30.3
        },
        "recommendation": "sell",
        "confidence": 0.85
    },
    "timestamp": "2025-11-06T20:23:56"
}
```

### AI Insights Code Examples

#### JavaScript
```javascript
async function generateAIInsight(symbol, analysisType) {
    try {
        const response = await axios.post(
            'http://localhost:8090/api/ai-insights/generate',
            { symbol, analysis_type: analysisType },
            { headers: { Authorization: `Bearer ${token}` } }
        );
        return response.data;
    } catch (error) {
        console.error('AI insight generation error:', error.response.data);
    }
}

async function getAIInsights(symbol = null, minConfidence = 0.0) {
    try {
        const response = await axios.get('http://localhost:8090/api/ai-insights', {
            params: { symbol, min_confidence: minConfidence },
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    } catch (error) {
        console.error('Get AI insights error:', error.response.data);
    }
}

// Usage examples
generateAIInsight('KGHM', 'overvaluation').then(insight => {
    console.log('Generated insight:', insight.result);
});

getAIInsights('PKN_ORLEN', 0.7).then(insights => {
    console.log('High confidence insights:', insights);
});
```

#### Python
```python
def generate_ai_insight(symbol, analysis_type):
    url = 'http://localhost:8090/api/ai-insights/generate'
    data = {'symbol': symbol, 'analysis_type': analysis_type}
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return None

def get_ai_insights(symbol=None, min_confidence=0.0):
    url = 'http://localhost:8090/api/ai-insights'
    params = {'min_confidence': min_confidence}
    if symbol:
        params['symbol'] = symbol
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return None

# Usage examples
insight = generate_ai_insight('KGHM', 'overvaluation')
if insight:
    print(f"Generated: {insight['result']['status']}")

insights = get_ai_insights('PKN_ORLEN', 0.7)
if insights:
    print(f"Found {len(insights)} high-confidence insights")
```

---

## Market Correlation Endpoints

### Get Market Correlations

Calculate and retrieve market correlation data between stocks.

```http
GET /api/correlations?symbols=PKN_ORLEN,KGHM,PGE,ORANGE_PL
Authorization: Bearer {token}
```

**Query Parameters:**
- `symbols` (optional): Comma-separated list of stock symbols (defaults to top 10 companies)

**Response:**
```json
{
    "correlation_matrix": {
        "PKN_ORLEN": {
            "KGHM": 0.45,
            "PGE": 0.67,
            "ORANGE_PL": 0.23
        },
        "KGHM": {
            "PKN_ORLEN": 0.45,
            "PGE": 0.34,
            "ORANGE_PL": 0.12
        }
    },
    "top_correlations": [
        {
            "symbol_a": "PKN_ORLEN",
            "symbol_b": "PGE",
            "correlation": 0.67,
            "strength": "moderate"
        },
        {
            "symbol_a": "PKN_ORLEN",
            "symbol_b": "KGHM",
            "correlation": 0.45,
            "strength": "weak"
        }
    ],
    "summary": {
        "average_correlation": 0.35,
        "highest_correlation": {
            "symbol_a": "PKN_ORLEN",
            "symbol_b": "PGE",
            "correlation": 0.67
        },
        "sectors_most_correlated": ["Banking", "Energy"]
    }
}
```

### Market Correlation Code Examples

#### JavaScript
```javascript
async function getMarketCorrelations(symbols = null) {
    try {
        const params = symbols ? { symbols: symbols.join(',') } : {};
        const response = await axios.get('http://localhost:8090/api/correlations', {
            params,
            headers: { Authorization: `Bearer ${token}` }
        });
        return response.data;
    } catch (error) {
        console.error('Correlation analysis error:', error.response.data);
    }
}

// Usage
const symbols = ['PKN_ORLEN', 'KGHM', 'PGE', 'ORANGE_PL'];
getMarketCorrelations(symbols).then(data => {
    console.log('Average correlation:', data.summary.average_correlation);
    console.log('Top correlations:', data.top_correlations);
});
```

#### Python
```python
def get_market_correlations(symbols=None):
    url = 'http://localhost:8090/api/correlations'
    params = {}
    if symbols:
        params['symbols'] = ','.join(symbols)
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.text}")
        return None

# Usage
symbols = ['PKN_ORLEN', 'KGHM', 'PGE', 'ORANGE_PL']
correlations = get_market_correlations(symbols)
if correlations:
    print(f"Average correlation: {correlations['summary']['average_correlation']}")
    print(f"Top correlations: {correlations['top_correlations'][:3]}")
```

---

## Utility Endpoints

### Get Market Alerts

Retrieve market alerts and notifications.

```http
GET /api/alerts?symbol=PKN_ORLEN&unread_only=true
Authorization: Bearer {token}
```

**Query Parameters:**
- `symbol` (optional): Filter by specific stock symbol
- `unread_only` (optional): Return only unread alerts (default: false)

**Response:**
```json
{
    "alerts": [
        {
            "id": 456,
            "timestamp": "2025-11-06T20:23:56",
            "symbol": "PKN_ORLEN",
            "alert_type": "price_spike",
            "severity": "high",
            "message": "PKN_ORLEN price increased by 5.2% in the last hour",
            "is_read": false
        }
    ],
    "total": 1
}
```

### Health Check

Check API health and status.

```http
GET /api/health
```

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-11-06T20:23:56",
    "version": "2.0.0",
    "database": "connected"
}
```

### API Statistics

Get API usage statistics and database metrics.

```http
GET /api/stats
Authorization: Bearer {token}
```

**Response:**
```json
{
    "database_stats": {
        "total_stock_records": 1250,
        "total_ai_insights": 89,
        "active_companies": 88,
        "unread_alerts": 12
    },
    "api_stats": {
        "uptime": "running",
        "rate_limiting": "enabled",
        "authentication": "enabled"
    },
    "timestamp": "2025-11-06T20:23:56"
}
```

---

## Data Models

### StockDataResponse

```typescript
interface StockDataResponse {
    symbol: string;
    timestamp: string;
    open_price: number;
    high_price: number;
    low_price: number;
    close_price: number;
    volume: number;
    macd?: number;
    rsi?: number;
    bb_upper?: number;
    bb_lower?: number;
    sma_20?: number;
    ema_20?: number;
}
```

### TechnicalAnalysisResponse

```typescript
interface TechnicalAnalysisResponse {
    symbol: string;
    period: number;
    indicators: {
        macd?: {
            macd: number;
            signal: number;
            histogram: number;
        };
        rsi?: {
            value: number;
            signal: "overbought" | "oversold" | "neutral";
        };
        bollinger_bands?: {
            upper: number;
            middle: number;
            lower: number;
            position: "upper" | "middle" | "lower";
        };
        sma?: {
            value: number;
            trend: "above" | "below";
        };
        ema?: {
            value: number;
            trend: "above" | "below";
        };
    };
    timestamp: string;
}
```

### AIInsightResponse

```typescript
interface AIInsightResponse {
    id: number;
    timestamp: string;
    symbol: string;
    insight_type: string;
    result: {
        status: string;
        confidence: number;
        [key: string]: any;
    };
    confidence: number;
}
```

---

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format.

### Error Response Format

```json
{
    "detail": "Error message description",
    "type": "error_type",
    "code": "ERROR_CODE"
}
```

### Common Error Codes

| Status Code | Description | Example |
|-------------|-------------|---------|
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Invalid or missing token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Code Examples

#### Rate Limit Exceeded
```json
{
    "detail": "Rate limit exceeded. Please try again later.",
    "type": "rate_limit_exceeded",
    "code": 429
}
```

#### Invalid Token
```json
{
    "detail": "Invalid authentication token",
    "type": "authentication_error",
    "code": 401
}
```

#### Resource Not Found
```json
{
    "detail": "No data found for symbol INVALID_SYMBOL",
    "type": "resource_not_found",
    "code": 404
}
```

---

## Code Examples

### Complete JavaScript Example

```javascript
const axios = require('axios');

class WIG80APIClient {
    constructor(baseURL = 'http://localhost:8090') {
        this.baseURL = baseURL;
        this.token = null;
    }

    async login(username, password) {
        const response = await axios.post(`${this.baseURL}/api/auth/login`, {
            username,
            password
        });
        this.token = response.data.token;
        return this.token;
    }

    async getAuthHeaders() {
        if (!this.token) throw new Error('Not authenticated');
        return { Authorization: `Bearer ${this.token}` };
    }

    async getStocks(symbol = null, options = {}) {
        const params = { ...options };
        if (symbol) params.symbol = symbol;
        
        const headers = await this.getAuthHeaders();
        const response = await axios.get(`${this.baseURL}/api/stocks`, {
            params,
            headers
        });
        return response.data;
    }

    async getTechnicalAnalysis(symbol, indicators = ['macd', 'rsi', 'bb']) {
        const headers = await this.getAuthHeaders();
        const params = { indicators: indicators.join(',') };
        
        const response = await axios.get(`${this.baseURL}/api/technical/${symbol}`, {
            params,
            headers
        });
        return response.data;
    }

    async generateAIInsight(symbol, analysisType) {
        const headers = await this.getAuthHeaders();
        const response = await axios.post(`${this.baseURL}/api/ai-insights/generate`, {
            symbol,
            analysis_type: analysisType
        }, { headers });
        return response.data;
    }

    async getCorrelations(symbols = null) {
        const params = symbols ? { symbols: symbols.join(',') } : {};
        const headers = await this.getAuthHeaders();
        
        const response = await axios.get(`${this.baseURL}/api/correlations`, {
            params,
            headers
        });
        return response.data;
    }
}

// Usage example
async function main() {
    const client = new WIG80APIClient();
    
    // Login
    await client.login('admin', 'admin123');
    
    // Get stock data
    const stocks = await client.getStocks('PKN_ORLEN', { limit: 10 });
    console.log('Stock data:', stocks);
    
    // Get technical analysis
    const technical = await client.getTechnicalAnalysis('PKN_ORLEN', ['macd', 'rsi']);
    console.log('Technical analysis:', technical);
    
    // Generate AI insight
    const insight = await client.generateAIInsight('KGHM', 'overvaluation');
    console.log('AI insight:', insight);
    
    // Get correlations
    const correlations = await client.getCorrelations(['PKN_ORLEN', 'KGHM', 'PGE']);
    console.log('Correlations:', correlations);
}

main().catch(console.error);
```

### Complete Python Example

```python
import requests
import time

class WIG80APIClient:
    def __init__(self, base_url='http://localhost:8090'):
        self.base_url = base_url
        self.token = None
        
    def login(self, username, password):
        url = f'{self.base_url}/api/auth/login'
        data = {'username': username, 'password': password}
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            self.token = result['token']
            return self.token
        else:
            raise Exception(f"Login failed: {response.text}")
    
    def get_headers(self):
        if not self.token:
            raise Exception("Not authenticated")
        return {'Authorization': f'Bearer {self.token}'}
    
    def get_stocks(self, symbol=None, **options):
        url = f'{self.base_url}/api/stocks'
        params = {**options}
        if symbol:
            params['symbol'] = symbol
            
        response = requests.get(url, params=params, headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.text}")
    
    def get_technical_analysis(self, symbol, indicators=['macd', 'rsi', 'bb']):
        url = f'{self.base_url}/api/technical/{symbol}'
        params = {'indicators': ','.join(indicators)}
        
        response = requests.get(url, params=params, headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.text}")
    
    def generate_ai_insight(self, symbol, analysis_type):
        url = f'{self.base_url}/api/ai-insights/generate'
        data = {'symbol': symbol, 'analysis_type': analysis_type}
        
        response = requests.post(url, json=data, headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.text}")
    
    def get_correlations(self, symbols=None):
        url = f'{self.base_url}/api/correlations'
        params = {}
        if symbols:
            params['symbols'] = ','.join(symbols)
            
        response = requests.get(url, params=params, headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.text}")

# Usage example
def main():
    client = WIG80APIClient()
    
    try:
        # Login
        client.login('admin', 'admin123')
        
        # Get stock data
        stocks = client.get_stocks('PKN_ORLEN', limit=10)
        print('Stock data:', stocks)
        
        # Get technical analysis
        technical = client.get_technical_analysis('PKN_ORLEN', ['macd', 'rsi'])
        print('Technical analysis:', technical)
        
        # Generate AI insight
        insight = client.generate_ai_insight('KGHM', 'overvaluation')
        print('AI insight:', insight)
        
        # Get correlations
        correlations = client.get_correlations(['PKN_ORLEN', 'KGHM', 'PGE'])
        print('Correlations:', correlations)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

### React Integration Example

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const WIG80Dashboard = () => {
    const [stocks, setStocks] = useState([]);
    const [token, setToken] = useState('');
    const [selectedSymbol, setSelectedSymbol] = useState('PKN_ORLEN');

    useEffect(() => {
        login();
    }, []);

    const login = async () => {
        try {
            const response = await axios.post('http://localhost:8090/api/auth/login', {
                username: 'admin',
                password: 'admin123'
            });
            setToken(response.data.token);
        } catch (error) {
            console.error('Login failed:', error);
        }
    };

    const getAuthHeaders = () => ({
        Authorization: `Bearer ${token}`
    });

    const fetchStocks = async (symbol = null) => {
        try {
            const params = symbol ? { symbol } : {};
            const response = await axios.get('http://localhost:8090/api/stocks', {
                params,
                headers: getAuthHeaders()
            });
            setStocks(response.data);
        } catch (error) {
            console.error('Failed to fetch stocks:', error);
        }
    };

    const fetchTechnicalAnalysis = async (symbol) => {
        try {
            const response = await axios.get(
                `http://localhost:8090/api/technical/${symbol}`,
                {
                    params: { indicators: 'macd,rsi,bb' },
                    headers: getAuthHeaders()
                }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to fetch technical analysis:', error);
        }
    };

    const generateAIInsight = async (symbol, analysisType) => {
        try {
            const response = await axios.post(
                'http://localhost:8090/api/ai-insights/generate',
                { symbol, analysis_type: analysisType },
                { headers: getAuthHeaders() }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to generate AI insight:', error);
        }
    };

    return (
        <div className="wig80-dashboard">
            <h1>WIG80 Stock Analysis Dashboard</h1>
            
            <div className="controls">
                <select 
                    value={selectedSymbol} 
                    onChange={(e) => setSelectedSymbol(e.target.value)}
                >
                    <option value="PKN_ORLEN">PKN Orlen</option>
                    <option value="KGHM">KGHM</option>
                    <option value="PGE">PGE</option>
                    <option value="ORANGE_PL">Orange Polska</option>
                </select>
                
                <button onClick={() => fetchStocks(selectedSymbol)}>
                    Fetch Stock Data
                </button>
                
                <button onClick={() => fetchStocks()}>
                    Fetch All Stocks
                </button>
            </div>

            <div className="data-section">
                <h2>Stock Data</h2>
                {stocks.map((stock, index) => (
                    <div key={index} className="stock-item">
                        <h3>{stock.symbol}</h3>
                        <p>Price: {stock.close_price}</p>
                        <p>Volume: {stock.volume.toLocaleString()}</p>
                        <p>Timestamp: {stock.timestamp}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default WIG80Dashboard;
```

---

## Integration Guides

### React + PocketBase SDK Integration

```javascript
// Install: npm install pocketbase
import PocketBase from 'pocketbase';

const pb = new PocketBase('http://localhost:8090');

// Authenticate
const authData = await pb.admins.authWithPassword('admin', 'admin123');

// Fetch companies
const companies = await pb.collection('companies').getList(1, 50, {
    filter: 'is_active = true',
    sort: 'symbol'
});

// Get latest stock data for a company
const stockData = await pb.collection('stock_data').getList(1, 1, {
    filter: 'symbol = "PKN_ORLEN"',
    sort: '-timestamp'
});

// Real-time subscription
pb.collection('stock_data').subscribe('*', function (e) {
    console.log('Stock update:', e.record);
    // Update your React state here
});
```

### Next.js Integration

```jsx
// pages/api/wig80/[endpoint].js
export default async function handler(req, res) {
    const { endpoint } = req.query;
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    try {
        const response = await fetch(`http://localhost:8090/api/${endpoint}`, {
            method: req.method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined
        });
        
        const data = await response.json();
        res.status(response.status).json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
}
```

### Vue.js Integration

```vue
<template>
    <div class="wig80-app">
        <h1>WIG80 Stock Analysis</h1>
        
        <div class="controls">
            <input v-model="symbol" placeholder="Enter symbol" />
            <button @click="fetchStockData">Get Stock Data</button>
            <button @click="fetchTechnicalAnalysis">Get Technical Analysis</button>
        </div>
        
        <div v-if="stockData" class="data-display">
            <h2>Stock Data for {{ symbol }}</h2>
            <p>Price: {{ stockData.close_price }}</p>
            <p>Volume: {{ stockData.volume }}</p>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            token: null,
            symbol: 'PKN_ORLEN',
            stockData: null
        };
    },
    
    async mounted() {
        await this.login();
    },
    
    methods: {
        async login() {
            try {
                const response = await fetch('http://localhost:8090/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: 'admin',
                        password: 'admin123'
                    })
                });
                const data = await response.json();
                this.token = data.token;
            } catch (error) {
                console.error('Login failed:', error);
            }
        },
        
        async fetchStockData() {
            try {
                const response = await fetch(`http://localhost:8090/api/stocks/${this.symbol}`, {
                    headers: { Authorization: `Bearer ${this.token}` }
                });
                const data = await response.json();
                this.stockData = data[0];
            } catch (error) {
                console.error('Failed to fetch stock data:', error);
            }
        }
    }
};
</script>
```

---

## Testing

### API Testing with curl

```bash
# Login
curl -X POST http://localhost:8090/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get stock data
curl -X GET "http://localhost:8090/api/stocks?symbol=PKN_ORLEN&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get technical analysis
curl -X GET "http://localhost:8090/api/technical/PKN_ORLEN?indicators=macd,rsi,bb" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Generate AI insight
curl -X POST http://localhost:8090/api/ai-insights/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"symbol":"KGHM","analysis_type":"overvaluation"}'
```

---

## Deployment

### Environment Variables

```bash
export POCKETBASE_URL="http://localhost:8090"
export API_HOST="0.0.0.0"
export API_PORT="8090"
export DB_PATH="/path/to/wig80_pocketbase.db"
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY enhanced_pocketbase_setup.py .
EXPOSE 8090

CMD ["python", "enhanced_pocketbase_setup.py"]
```

### Production Considerations

1. **Security**: Use HTTPS in production
2. **Database**: Consider using PostgreSQL for better performance
3. **Caching**: Implement Redis for frequently accessed data
4. **Monitoring**: Add logging and monitoring tools
5. **Scaling**: Use load balancers for high traffic
6. **Backup**: Regular database backups

---

## Support

For support and questions:
- **Documentation**: Refer to this document
- **API Version**: 2.0.0
- **Last Updated**: 2025-11-06
- **Compatible with**: Pocketbase 0.31.0+

---

## Changelog

### Version 2.0.0 (2025-11-06)
- ✅ Complete REST API implementation
- ✅ Technical analysis endpoints (MACD, RSI, Bollinger Bands)
- ✅ AI insights generation and retrieval
- ✅ Market correlation analysis
- ✅ Authentication and rate limiting
- ✅ Comprehensive error handling
- ✅ Real-time data support
- ✅ Multi-language integration examples
- ✅ Production-ready deployment guides

### Version 1.0.0
- Basic Pocketbase setup
- Simple database schema
- Mock API endpoints