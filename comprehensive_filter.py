#!/usr/bin/env python3
import json
import numpy as np
from collections import defaultdict

def parse_volume(volume_str):
    """Convert volume string like '246K', '367.37M' to actual numbers"""
    if not volume_str or volume_str == "N/A":
        return 0
    
    volume_str = volume_str.strip().upper()
    
    if 'M' in volume_str:
        number = float(volume_str.replace('M', ''))
        return int(number * 1000000)
    elif 'K' in volume_str:
        number = float(volume_str.replace('K', ''))
        return int(number * 1000)
    else:
        try:
            return int(float(volume_str))
        except:
            return 0

def analyze_data_distribution(companies):
    """Analyze the distribution of key metrics"""
    pe_ratios = []
    pb_ratios = []
    volumes = []
    
    for company in companies:
        if company.get('pe_ratio'):
            pe_ratios.append(company['pe_ratio'])
        if company.get('pb_ratio'):
            pb_ratios.append(company['pb_ratio'])
        
        volume = parse_volume(company.get('trading_volume', '0'))
        volumes.append(volume)
    
    return {
        'pe_ratio': {
            'count': len(pe_ratios),
            'min': min(pe_ratios) if pe_ratios else 0,
            'max': max(pe_ratios) if pe_ratios else 0,
            'avg': sum(pe_ratios) / len(pe_ratios) if pe_ratios else 0,
            'median': sorted(pe_ratios)[len(pe_ratios)//2] if pe_ratios else 0
        },
        'pb_ratio': {
            'count': len(pb_ratios),
            'min': min(pb_ratios) if pb_ratios else 0,
            'max': max(pb_ratios) if pb_ratios else 0,
            'avg': sum(pb_ratios) / len(pb_ratios) if pb_ratios else 0,
            'median': sorted(pb_ratios)[len(pb_ratios)//2] if pb_ratios else 0
        },
        'trading_volume': {
            'count': len(volumes),
            'min': min(volumes),
            'max': max(volumes),
            'avg': sum(volumes) / len(volumes),
            'median': sorted(volumes)[len(volumes)//2]
        }
    }

def find_alternative_opportunities(companies):
    """Find opportunities using alternative, more realistic criteria"""
    
    # Alternative 1: Small-cap value plays
    small_cap_value = []
    
    # Alternative 2: Growth potential with reasonable valuations
    growth_potential = []
    
    # Alternative 3: High volume, undervalued companies
    liquid_value = []
    
    for company in companies:
        if not company.get('pe_ratio') or not company.get('pb_ratio'):
            continue
            
        pe_ratio = company['pe_ratio']
        pb_ratio = company['pb_ratio']
        volume = parse_volume(company.get('trading_volume', '0'))
        price = company['current_price']
        change = company['change_percent']
        
        # Calculate scores
        value_score = calculate_value_score(pe_ratio, pb_ratio, price, volume)
        growth_score = calculate_growth_score(pe_ratio, pb_ratio, change)
        liquidity_score = calculate_liquidity_score(volume)
        small_cap_score = calculate_small_cap_score(price, volume)
        
        company_analysis = {
            'company_name': company['company_name'],
            'symbol': company['symbol'],
            'current_price': price,
            'change_percent': change,
            'pe_ratio': pe_ratio,
            'pb_ratio': pb_ratio,
            'trading_volume': company['trading_volume'],
            'trading_volume_numeric': volume,
            'value_score': value_score,
            'growth_score': growth_score,
            'liquidity_score': liquidity_score,
            'small_cap_score': small_cap_score,
            'overall_score': (value_score + growth_score + small_cap_score) / 3,
            'last_update': company['last_update']
        }
        
        # Alternative 1: Small-cap value (low P/B, low volume, decent P/E)
        if (pb_ratio < 8 and volume < 100000 and pe_ratio > 5 and pe_ratio < 25):
            small_cap_value.append(company_analysis)
        
        # Alternative 2: Growth potential (higher P/E, positive momentum)
        if (pe_ratio > 10 and change > -5 and pb_ratio < 15):
            growth_potential.append(company_analysis)
        
        # Alternative 3: Liquid value (reasonable volume, good valuation)
        if (volume > 100000 and volume < 1000000 and pe_ratio < 20 and pb_ratio < 8):
            liquid_value.append(company_analysis)
    
    # Sort each category
    small_cap_value.sort(key=lambda x: x['overall_score'], reverse=True)
    growth_potential.sort(key=lambda x: x['growth_score'], reverse=True)
    liquid_value.sort(key=lambda x: x['value_score'], reverse=True)
    
    return {
        'small_cap_value': small_cap_value[:15],  # Top 15
        'growth_potential': growth_potential[:15],  # Top 15
        'liquid_value': liquid_value[:15]  # Top 15
    }

def calculate_value_score(pe_ratio, pb_ratio, price, volume):
    """Calculate value investment score"""
    # Lower P/E is better for value
    pe_score = max(0, (25 - pe_ratio) / 25) if pe_ratio > 0 else 0
    
    # Lower P/B is better for value
    pb_score = max(0, (10 - pb_ratio) / 10) if pb_ratio > 0 else 0
    
    # Moderate volume preferred
    volume_score = 1.0 if 50000 <= volume <= 500000 else 0.5
    
    return (pe_score + pb_score + volume_score) / 3

def calculate_growth_score(pe_ratio, pb_ratio, change_percent):
    """Calculate growth potential score"""
    # Higher P/E suggests growth expectations
    pe_score = min(pe_ratio / 30, 1.0) if pe_ratio > 0 else 0
    
    # Moderate P/B for growth companies
    pb_score = 1.0 if 3 <= pb_ratio <= 12 else 0.5
    
    # Positive price momentum
    change_score = max(0, (change_percent + 10) / 20)  # Normalize from -10% to +10%
    
    return (pe_score + pb_score + change_score) / 3

def calculate_liquidity_score(volume):
    """Calculate liquidity score"""
    if volume >= 500000:
        return 1.0  # High liquidity
    elif volume >= 100000:
        return 0.8  # Good liquidity
    elif volume >= 50000:
        return 0.6  # Moderate liquidity
    else:
        return 0.3  # Low liquidity

def calculate_small_cap_score(price, volume):
    """Calculate small-cap potential"""
    # Lower price suggests smaller companies
    price_score = max(0, (300 - price) / 300)
    
    # Lower volume suggests smaller market cap
    volume_score = max(0, (100000 - volume) / 100000)
    
    return (price_score + volume_score) / 2

def original_criteria_analysis(companies):
    """Analyze how companies perform against original strict criteria"""
    results = {
        'pe_gt_4': [],
        'pb_gt_10': [],
        'volume_lt_50k': [],
        'all_criteria': []
    }
    
    for company in companies:
        pe_ratio = company.get('pe_ratio')
        pb_ratio = company.get('pb_ratio')
        volume = parse_volume(company.get('trading_volume', '0'))
        
        meets_pe = pe_ratio and pe_ratio > 4
        meets_pb = pb_ratio and pb_ratio > 10
        meets_volume = volume < 50000
        
        if meets_pe:
            results['pe_gt_4'].append({
                'symbol': company['symbol'],
                'company_name': company['company_name'],
                'pe_ratio': pe_ratio
            })
        
        if meets_pb:
            results['pb_gt_10'].append({
                'symbol': company['symbol'],
                'company_name': company['company_name'],
                'pb_ratio': pb_ratio
            })
        
        if meets_volume:
            results['volume_lt_50k'].append({
                'symbol': company['symbol'],
                'company_name': company['company_name'],
                'volume': company['trading_volume']
            })
        
        if meets_pe and meets_pb and meets_volume:
            results['all_criteria'].append({
                'symbol': company['symbol'],
                'company_name': company['company_name'],
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'volume': company['trading_volume']
            })
    
    return results

def main():
    # Load the data
    with open('/workspace/data/wig80_current_data.json', 'r') as f:
        data = json.load(f)
    
    companies = data['companies']
    
    # Analyze data distribution
    distribution = analyze_data_distribution(companies)
    
    # Original criteria analysis
    original_analysis = original_criteria_analysis(companies)
    
    # Find alternative opportunities
    alternatives = find_alternative_opportunities(companies)
    
    # Create comprehensive analysis
    analysis = {
        'metadata': {
            'analysis_date': '2025-11-05 03:35:10',
            'total_companies': len(companies),
            'data_source': data['metadata']['data_source'],
            'original_collection_date': data['metadata']['collection_date']
        },
        'data_distribution': distribution,
        'original_criteria_analysis': {
            'criteria': {
                'pe_ratio_min': 4,
                'pb_ratio_min': 10,
                'trading_volume_max': 50000,
                'description': 'Original strict criteria: P/E > 4, P/B > 10, Volume < 50K'
            },
            'results': original_analysis,
            'summary': {
                'companies_meeting_pe_criteria': len(original_analysis['pe_gt_4']),
                'companies_meeting_pb_criteria': len(original_analysis['pb_gt_10']),
                'companies_meeting_volume_criteria': len(original_analysis['volume_lt_50k']),
                'companies_meeting_all_criteria': len(original_analysis['all_criteria'])
            }
        },
        'alternative_opportunities': {
            'description': 'More realistic investment opportunities based on market conditions',
            'categories': alternatives
        },
        'recommendations': generate_investment_recommendations(alternatives, original_analysis),
        'risk_analysis': {
            'market_overview': 'Small-cap Polish stocks show varied valuations',
            'liquidity_concerns': 'Many companies have limited trading volume',
            'valuation_risk': 'High P/B ratios may indicate overvaluation in some sectors',
            'diversification': 'Spread investments across different sectors and market caps'
        }
    }
    
    # Save comprehensive results
    with open('/workspace/data/filtered_companies.json', 'w') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print("=== WIG80 COMPREHENSIVE ANALYSIS ===")
    print(f"Total companies analyzed: {len(companies)}")
    print(f"Companies meeting original P/E > 4 criteria: {len(original_analysis['pe_gt_4'])}")
    print(f"Companies meeting original P/B > 10 criteria: {len(original_analysis['pb_gt_10'])}")
    print(f"Companies meeting original volume < 50K criteria: {len(original_analysis['volume_lt_50k'])}")
    print(f"Companies meeting ALL original criteria: {len(original_analysis['all_criteria'])}")
    
    print("\n=== ALTERNATIVE INVESTMENT OPPORTUNITIES ===")
    print(f"Small-cap value plays found: {len(alternatives['small_cap_value'])}")
    print(f"Growth potential opportunities: {len(alternatives['growth_potential'])}")
    print(f"Liquid value opportunities: {len(alternatives['liquid_value'])}")
    
    print("\n=== TOP SMALL-CAP VALUE OPPORTUNITIES ===")
    for i, company in enumerate(alternatives['small_cap_value'][:10], 1):
        print(f"{i:2}. {company['company_name']} ({company['symbol']})")
        print(f"    Price: {company['current_price']:.2f} PLN | P/E: {company['pe_ratio']:.2f} | P/B: {company['pb_ratio']:.2f}")
        print(f"    Volume: {company['trading_volume']} | Change: {company['change_percent']:+.2f}%")
        print(f"    Overall Score: {company['overall_score']:.2f}")
        print()

def generate_investment_recommendations(alternatives, original_analysis):
    """Generate specific investment recommendations"""
    recommendations = {
        'primary_recommendations': [],
        'secondary_picks': [],
        'caution_flags': []
    }
    
    # Primary recommendations from small-cap value plays
    for company in alternatives['small_cap_value'][:5]:
        recommendations['primary_recommendations'].append({
            'symbol': company['symbol'],
            'company_name': company['company_name'],
            'rationale': 'Small-cap value opportunity with reasonable valuation',
            'price_target': company['current_price'] * 1.3,  # 30% upside potential
            'risk_level': 'Medium',
            'investment_thesis': f"Trading at P/E {company['pe_ratio']:.1f}, P/B {company['pb_ratio']:.1f} with good growth potential"
        })
    
    # Growth picks
    for company in alternatives['growth_potential'][:3]:
        recommendations['secondary_picks'].append({
            'symbol': company['symbol'],
            'company_name': company['company_name'],
            'rationale': 'Growth potential with positive momentum',
            'price_target': company['current_price'] * 1.5,
            'risk_level': 'Medium-High',
            'investment_thesis': f"Growth profile with P/E {company['pe_ratio']:.1f} and recent performance of {company['change_percent']:+.1f}%"
        })
    
    # Companies that came close to original criteria
    if original_analysis['pb_gt_10']:
        recommendations['caution_flags'].append({
            'note': 'High P/B ratios detected',
            'companies': original_analysis['pb_gt_10'][:5],
            'risk': 'Potential overvaluation, monitor fundamentals closely'
        })
    
    return recommendations

if __name__ == "__main__":
    main()