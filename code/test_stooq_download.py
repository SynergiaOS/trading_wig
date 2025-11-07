import urllib.request
import json

# Load WIG80 companies
with open('/workspace/data/wig80_current_data.json', 'r') as f:
    data = json.load(f)

# Try to fetch historical data for first 3 companies
for i in range(min(3, len(data['companies']))):
    company = data['companies'][i]
    symbol = company['symbol'].lower()
    url = f"https://stooq.com/q/d/l/?s={symbol}.pl&i=d"
    
    print(f"\n{'='*60}")
    print(f"Company: {company['company_name']} ({symbol.upper()})")
    print(f"URL: {url}")
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')
            lines = content.split('\n')
            
            # Show first 5 lines (header + 4 data rows)
            print(f"\nFirst 5 lines of CSV:")
            for line in lines[:5]:
                print(f"  {line}")
            
            print(f"\n✅ SUCCESS: Downloaded {len(lines)-1} days of historical data")
            
            # Save to file
            output_file = f"/tmp/{symbol}_historical.csv"
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"📁 Saved to: {output_file}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

print(f"\n{'='*60}")
print("✨ Stooq.pl data download test complete!")
