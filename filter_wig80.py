#!/usr/bin/env python3
import json
import re

def parse_volume(volume_str):
    """Convert volume string like '246K', '367.37M' to actual numbers"""
    if not volume_str or volume_str == "N/A":
        return 0
    
    # Clean the string and convert to uppercase
    volume_str = volume_str.strip().upper()
    
    # Handle millions (M)
    if 'M' in volume_str:
        number = float(volume_str.replace('M', ''))
        return int(number * 1000000)
    
    # Handle thousands (K)
    elif 'K' in volume_str:
        number = float(volume_str.replace('K', ''))
        return int(number * 1000)
    
    # Handle regular numbers
    else:
        try:
            return int(float(volume_str))
        except:
            return 0

def filter_companies(companies):
    """Filter companies based on criteria:
    - P/E ratio > 4
    - P/B ratio > 10
    - Trading volume < 50000
    """
    filtered = []
    
    for company in companies:
        # Skip if essential data is missing
        if not company.get('pe_ratio') or not company.get('pb_ratio'):
            continue
            
        pe_ratio = company['pe_ratio']
        pb_ratio = company['pb_ratio']
        trading_volume = parse_volume(company.get('trading_volume', '0'))
        
        # Apply filters
        if (pe_ratio > 4 and 
            pb_ratio > 10 and 
            trading_volume < 50000):
            
            # Calculate market cap indicator (price * volume as rough proxy)
            market_cap_proxy = company['current_price'] * trading_volume
            
            # Add additional analysis fields
            filtered.append({
                'company_name': company['company_name'],
                'symbol': company['symbol'],
                'current_price': company['current_price'],
                'change_percent': company['change_percent'],
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'trading_volume': company['trading_volume'],
                'trading_volume_numeric': trading_volume,
                'market_cap_proxy': market_cap_proxy,
                'growth_score': calculate_growth_score(pe_ratio, pb_ratio, company['change_percent']),
                'small_cap_score': calculate_small_cap_score(company['current_price'], trading_volume),
                'last_update': company['last_update']
            })
    
    # Sort by combination of growth potential and small-cap characteristics
    filtered.sort(key=lambda x: (
        -x['growth_score'],  # Higher growth score first
        -x['small_cap_score'],  # Higher small-cap score first
        x['market_cap_proxy']  # Smaller market cap proxy first
    ))
    
    return filtered

def calculate_growth_score(pe_ratio, pb_ratio, change_percent):
    """Calculate growth potential score based on financial ratios and recent performance"""
    # Higher P/E suggests growth expectations
    # Higher P/B suggests asset-rich companies
    # Positive change_percent shows momentum
    
    pe_score = min(pe_ratio / 20, 2)  # Cap at 2, normalize around 20
    pb_score = min(pb_ratio / 15, 2)  # Cap at 2, normalize around 15
    change_score = max(change_percent / 10, -1)  # Normalize change, cap negative
    
    return pe_score + pb_score + change_score

def calculate_small_cap_score(price, volume):
    """Calculate small-cap potential score"""
    # Lower price and lower volume suggest smaller companies
    price_score = max(0, (500 - price) / 500)  # Prefer prices under 500 PLN
    volume_score = max(0, (50000 - volume) / 50000)  # Already filtered by volume < 50K
    
    return (price_score + volume_score) / 2

def main():
    # Load the data
    with open('/workspace/data/wig80_current_data.json', 'r') as f:
        data = json.load(f)
    
    # Filter companies
    filtered_companies = filter_companies(data['companies'])
    
    # Create detailed analysis
    analysis = {
        'metadata': {
            'filtering_date': '2025-11-05 03:35:10',
            'filtering_criteria': {
                'pe_ratio_min': 4,
                'pb_ratio_min': 10,
                'trading_volume_max': 50000,
                'description': 'P/E ratio > 4, P/B ratio > 10, Trading volume < 50K shares'
            },
            'total_companies_analyzed': len(data['companies']),
            'companies_meeting_criteria': len(filtered_companies),
            'data_source': data['metadata']['data_source'],
            'original_collection_date': data['metadata']['collection_date']
        },
        'filtered_companies': filtered_companies,
        'analysis_summary': generate_summary(filtered_companies),
        'investment_themes': identify_investment_themes(filtered_companies),
        'risk_assessment': generate_risk_assessment(filtered_companies)
    }
    
    # Save results
    with open('/workspace/data/filtered_companies.json', 'w') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis complete. Found {len(filtered_companies)} companies meeting criteria.")
    print(f"Results saved to data/filtered_companies.json")
    
    # Print top 10 recommendations
    print("\n=== TOP 10 INVESTMENT OPPORTUNITIES ===")
    for i, company in enumerate(filtered_companies[:10], 1):
        print(f"{i:2}. {company['company_name']} ({company['symbol']})")
        print(f"    Price: {company['current_price']:.2f} PLN | P/E: {company['pe_ratio']:.2f} | P/B: {company['pb_ratio']:.2f}")
        print(f"    Volume: {company['trading_volume']} | Change: {company['change_percent']:+.2f}%")
        print(f"    Growth Score: {company['growth_score']:.2f} | Small-Cap Score: {company['small_cap_score']:.2f}")
        print()

def generate_summary(companies):
    """Generate summary statistics"""
    if not companies:
        return {"message": "No companies meet the filtering criteria"}
    
    pe_ratios = [c['pe_ratio'] for c in companies]
    pb_ratios = [c['pb_ratio'] for c in companies]
    prices = [c['current_price'] for c in companies]
    changes = [c['change_percent'] for c in companies]
    
    return {
        'avg_pe_ratio': sum(pe_ratios) / len(pe_ratios),
        'avg_pb_ratio': sum(pb_ratios) / len(pb_ratios),
        'avg_price': sum(prices) / len(prices),
        'avg_change_percent': sum(changes) / len(changes),
        'price_range': {'min': min(prices), 'max': max(prices)},
        'sector_distribution': analyze_sectors(companies)
    }

def identify_investment_themes(companies):
    """Identify investment themes among filtered companies"""
    themes = {
        'high_growth_potential': [],
        'value_opportunities': [],
        'small_cap_gems': []
    }
    
    for company in companies:
        if company['growth_score'] > 1.5:
            themes['high_growth_potential'].append({
                'symbol': company['symbol'],
                'company_name': company['company_name'],
                'score': company['growth_score']
            })
        
        if company['pb_ratio'] > 12 and company['pe_ratio'] < 15:
            themes['value_opportunities'].append({
                'symbol': company['symbol'],
                'company_name': company['company_name'],
                'pb_ratio': company['pb_ratio'],
                'pe_ratio': company['pe_ratio']
            })
        
        if company['small_cap_score'] > 0.5 and company['current_price'] < 200:
            themes['small_cap_gems'].append({
                'symbol': company['symbol'],
                'company_name': company['company_name'],
                'price': company['current_price'],
                'score': company['small_cap_score']
            })
    
    return themes

def generate_risk_assessment(companies):
    """Generate risk assessment for filtered companies"""
    return {
        'volume_risk': 'Low trading volume may indicate limited liquidity',
        'high_valuation_risk': 'High P/B ratios suggest potential overvaluation',
        'market_sentiment': 'Monitor recent price movements and news',
        'recommendations': [
            'Diversify across multiple companies',
            'Monitor quarterly earnings closely',
            'Set stop-loss levels due to volatility',
            'Consider position sizing based on liquidity'
        ]
    }

def analyze_sectors(companies):
    """Simple sector analysis based on company names and symbols"""
    sectors = {
        'Technology': [],
        'Biotechnology': [],
        'Manufacturing': [],
        'Real Estate': [],
        'Energy': [],
        'Other': []
    }
    
    tech_keywords = ['DATA', 'SOFT', 'TECH', 'IT', 'COMPUTER']
    bio_keywords = ['BIO', 'PHARMA', 'MEDICAL', 'VITA', 'THERA']
    manufacturing_keywords = ['STAL', 'METAL', 'CHEM', 'MACHINE']
    real_estate_keywords = ['BUD', 'NIER', 'DEVEL']
    energy_keywords = ['ENERG', 'GAZ', 'ELEKTR']
    
    for company in companies:
        name = company['company_name'].upper()
        symbol = company['symbol'].upper()
        
        assigned = False
        
        # Check for sector keywords
        for keyword in tech_keywords:
            if keyword in name or keyword in symbol:
                sectors['Technology'].append(company['symbol'])
                assigned = True
                break
        
        if not assigned:
            for keyword in bio_keywords:
                if keyword in name or keyword in symbol:
                    sectors['Biotechnology'].append(company['symbol'])
                    assigned = True
                    break
        
        if not assigned:
            for keyword in manufacturing_keywords:
                if keyword in name or keyword in symbol:
                    sectors['Manufacturing'].append(company['symbol'])
                    assigned = True
                    break
        
        if not assigned:
            for keyword in real_estate_keywords:
                if keyword in name or keyword in symbol:
                    sectors['Real Estate'].append(company['symbol'])
                    assigned = True
                    break
        
        if not assigned:
            for keyword in energy_keywords:
                if keyword in name or keyword in symbol:
                    sectors['Energy'].append(company['symbol'])
                    assigned = True
                    break
        
        if not assigned:
            sectors['Other'].append(company['symbol'])
    
    return sectors

if __name__ == "__main__":
    main()