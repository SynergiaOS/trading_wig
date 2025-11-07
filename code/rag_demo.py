#!/usr/bin/env python3
"""
Polish Financial Market RAG System - Demonstration Script

This script demonstrates the key capabilities of the RAG system including:
- Overvaluation detection
- Company analysis
- Market insights
- Risk assessment
- Regulatory information

Run this script to see the RAG system in action!
"""

import sys
import os
sys.path.append('/workspace/code')

from rag_system import PolishFinancialRAG, QueryType

def main():
    print("🚀 Polish Financial Market RAG System - Live Demo")
    print("=" * 60)
    
    # Initialize the RAG system
    print("🔧 Initializing RAG system...")
    rag = PolishFinancialRAG()
    
    # Display market summary
    market_summary = rag.get_market_summary()
    print(f"\n📊 Current Market Overview:")
    print(f"   📈 Total Companies Analyzed: {market_summary['total_companies']}")
    print(f"   💰 Average P/E Ratio: {market_summary['average_pe_ratio']}")
    print(f"   📚 Average P/B Ratio: {market_summary['average_pb_ratio']}")
    print(f"   🏛️  Exchange: {market_summary['exchange']}")
    print(f"   💱 Currency: {market_summary['currency']}")
    
    # Demo 1: Overvaluation Detection
    print(f"\n" + "="*60)
    print("🎯 DEMO 1: OVERVALUATION DETECTION")
    print("="*60)
    
    overvalued_companies = ["AGO", "BUM", "APT", "ECH"]  # Companies with high ratios
    for symbol in overvalued_companies:
        analysis = rag.get_company_analysis(symbol)
        if "error" not in analysis:
            print(f"\n🏢 {symbol} - {analysis['company_name']}")
            print(f"   📊 {analysis['analysis']}")
            print(f"   ⚠️  Risk Level: {analysis['risk_level'].upper()}")
    
    # Demo 2: Query-based Analysis
    print(f"\n" + "="*60)
    print("🔍 DEMO 2: QUERY-BASED ANALYSIS")
    print("="*60)
    
    test_queries = [
        ("Which Polish companies have the highest overvaluation risk?", QueryType.OVERVALUATION_DETECTION),
        ("What makes the banking sector attractive for investment?", QueryType.SECTOR_ANALYSIS),
        ("How does the KNF regulate market manipulation?", QueryType.REGULATORY_INFO),
        ("What's the difference between WIG20 and sWIG80 indices?", QueryType.MARKET_COMPARISON),
    ]
    
    for query, query_type in test_queries:
        print(f"\n❓ Query: {query}")
        result = rag.query(query, query_type)
        print(f"📝 Response: {result['response'][:300]}...")
        print(f"🎯 Confidence: {result['confidence']:.2f}")
        print("-" * 40)
    
    # Demo 3: Specific Company Deep Dive
    print(f"\n" + "="*60)
    print("🏢 DEMO 3: SPECIFIC COMPANY ANALYSIS")
    print("="*60)
    
    # Analyze a specific well-known company
    company_symbol = "KGH"  # KGHM - well-known Polish mining company
    analysis = rag.get_company_analysis(company_symbol)
    
    if "error" not in analysis:
        print(f"\n🏢 {analysis['company_name']} ({company_symbol})")
        print(f"📊 Financial Data:")
        fd = analysis['financial_data']
        print(f"   💰 Current Price: {fd.get('current_price', 'N/A')} PLN")
        print(f"   📈 P/E Ratio: {fd.get('pe_ratio', 'N/A')}")
        print(f"   📚 P/B Ratio: {fd.get('pb_ratio', 'N/A')}")
        print(f"   📊 Daily Change: {fd.get('change_percent', 'N/A')}%")
        print(f"   📦 Volume: {fd.get('trading_volume', 'N/A')}")
        
        print(f"\n🎯 Analysis Results:")
        print(f"   {analysis['analysis']}")
        print(f"   ⚠️  Risk Level: {analysis['risk_level'].upper()}")
    
    # Demo 4: Market Risk Assessment
    print(f"\n" + "="*60)
    print("⚠️  DEMO 4: MARKET RISK ASSESSMENT")
    print("="*60)
    
    # Get companies with high P/E ratios (potential overvaluation)
    import sqlite3
    conn = sqlite3.connect(rag.knowledge_base.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT symbol, company_name, financial_data
        FROM wgi80_companies
        WHERE CAST(json_extract(financial_data, '$.pe_ratio') AS REAL) > 30
        ORDER BY CAST(json_extract(financial_data, '$.pe_ratio') AS REAL) DESC
        LIMIT 5
    """)
    
    high_pe_companies = cursor.fetchall()
    conn.close()
    
    print(f"\n🔴 Companies with High P/E Ratios (>30):")
    for symbol, company_name, financial_data_str in high_pe_companies:
        import json
        fd = json.loads(financial_data_str)
        pe_ratio = fd.get('pe_ratio', 'N/A')
        change = fd.get('change_percent', 0)
        print(f"   📊 {symbol} - {company_name}")
        print(f"      P/E: {pe_ratio}, Change: {change:+.2f}%")
    
    # Demo 5: Regulatory Information
    print(f"\n" + "="*60)
    print("📋 DEMO 5: REGULATORY FRAMEWORK")
    print("="*60)
    
    regulatory_query = "What are the key responsibilities of KNF in protecting Polish investors?"
    result = rag.query(regulatory_query, QueryType.REGULATORY_INFO)
    
    print(f"\n❓ {regulatory_query}")
    print(f"📝 Answer: {result['response']}")
    
    # Demo 6: Interactive Query
    print(f"\n" + "="*60)
    print("💬 DEMO 6: INTERACTIVE ANALYSIS")
    print("="*60)
    
    print("\nTry your own query! Examples:")
    print("- 'Analyze PKO BP valuation'")
    print("- 'What are the risks of investing in Polish tech companies?'")
    print("- 'Compare energy sector vs banking sector'")
    print("- 'Explain NewConnect market'")
    
    # Uncomment the following lines for interactive mode
    # while True:
    #     try:
    #         user_query = input("\nEnter your financial analysis query (or 'quit' to exit): ")
    #         if user_query.lower() in ['quit', 'exit', 'q']:
    #             break
    #         if user_query.strip():
    #             result = rag.query(user_query, QueryType.VALUATION_ANALYSIS)
    #             print(f"\n🤖 RAG Analysis:")
    #             print(result['response'])
    #             print(f"\n📊 Confidence: {result['confidence']:.2f}")
    #     except KeyboardInterrupt:
    #         break
    
    print(f"\n" + "="*60)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\n🎉 The Polish Financial Market RAG System is ready for use!")
    print(f"💾 Knowledge base: /workspace/data/rag_knowledge.db")
    print(f"📖 Documentation: /workspace/docs/rag_system_guide.md")
    print(f"🔧 Main system: /workspace/code/rag_system.py")
    
    print(f"\n💡 Key Features Demonstrated:")
    print(f"   ✅ Overvaluation detection using P/E and P/B ratios")
    print(f"   ✅ Company-specific financial analysis")
    print(f"   ✅ Market structure and regulatory information")
    print(f"   ✅ Query-based semantic search")
    print(f"   ✅ Risk level assessment")
    print(f"   ✅ Polish financial market expertise")

if __name__ == "__main__":
    main()