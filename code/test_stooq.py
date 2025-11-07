import urllib.request
import re

url = 'https://stooq.pl/q/?s=PKN'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        html = response.read().decode('utf-8')
        print(f'Success! Got {len(html)} bytes')
        
        # Try different price patterns
        patterns = [
            (r'Kurs:\s*([0-9,\.]+)', 'Pattern 1: Kurs'),
            (r'id="aq_[^"]*_c[^>]*>([0-9,\.]+)<', 'Pattern 2: aq_c'),
            (r'class="[^"]*price[^"]*"[^>]*>([0-9,\.]+)<', 'Pattern 3: price class'),
        ]
        
        found = False
        for pattern, name in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                print(f'{name} found: {match.group(1)}')
                found = True
        
        if not found:
            print('No price patterns matched')
            print('\nHTML sample (first 1000 chars):')
            print(html[:1000])
            
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
