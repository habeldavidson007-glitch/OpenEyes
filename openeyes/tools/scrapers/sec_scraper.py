"""
SEC EDGAR Scraper
Scrapes earnings filings (10-K, 10-Q) for S&P 500 companies.
"""

import requests
import json
import os
from datetime import datetime
import time

class SecScraper:
    def __init__(self):
        self.base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        self.state_file = os.path.join(os.path.dirname(__file__), "state.json")
        self.review_queue_dir = os.path.join(os.path.dirname(__file__), "../../fragment_library/review_queue")
        self.log_file = os.path.join(os.path.dirname(__file__), "../../obsidian_connector/logs/scraper_logs.md")
        
        # Sample S&P 500 tickers (in production, load full list)
        self.tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'JPM', 'V']
        
        os.makedirs(self.review_queue_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # SEC requires user agent
        self.headers = {
            'User-Agent': 'OpenEyes VCIS sec_scraper/1.0',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
    
    def get_last_run(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                return state.get('sec_last_run', '2020-01-01')
        return '2020-01-01'
    
    def save_last_run(self):
        state = {}
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        state['sec_last_run'] = datetime.now().strftime('%Y-%m-%d')
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def fetch_filings(self, ticker, form_type='10-K'):
        """Fetch recent filings for a ticker."""
        filings = []
        try:
            # Search for company filings
            params = {
                'action': 'getcompany',
                'CIK': ticker,
                'type': form_type,
                'count': '5',
                'output': 'atom'
            }
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                # Parse Atom feed (simplified)
                # In production, use proper XML parsing
                if '<entry>' in response.text:
                    entries = response.text.split('<entry>')
                    for entry in entries[1:6]:  # Skip header, take 5
                        if '<title>' in entry and '<link' in entry:
                            title_start = entry.find('<title>') + 7
                            title_end = entry.find('</title>')
                            title = entry[title_start:title_end].strip()
                            
                            link_start = entry.find('<link href="') + 12
                            link_end = entry.find('"', link_start)
                            url = entry[link_start:link_end]
                            
                            filings.append({
                                'ticker': ticker,
                                'form_type': form_type,
                                'title': title,
                                'url': url,
                                'date': datetime.now().strftime('%Y-%m-%d')
                            })
        except Exception as e:
            print(f"[SecScraper] Error fetching {ticker} {form_type}: {e}")
        
        return filings
    
    def extract_content(self, url):
        """Extract text from filing HTML."""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                # Extract plain text version if available
                if '/Archives/' in url:
                    content = response.text[:8000]  # First 8k chars
                    return content
        except Exception as e:
            print(f"[SecScraper] Error extracting from {url}: {e}")
        return ""
    
    def generate_fragment(self, filing):
        """Generate fragment JSON for review."""
        content = self.extract_content(filing['url'])
        if not content:
            return None
        
        tags = ['earnings', 'revenue', 'fundamental_analysis', 'latest_data']
        if filing['form_type'] == '10-K':
            tags.append('annual_report')
            subdomain = 'annual_filings'
            role = 'latest_data'
        else:
            tags.append('quarterly_report')
            subdomain = 'quarterly_filings'
            role = 'latest_data'
        
        fragment = {
            "id": f"frag_fin_sec_{filing['ticker']}_{filing['form_type']}_{datetime.now().strftime('%Y%m%d')}",
            "domain": "finance",
            "subdomain": subdomain,
            "tags": tags,
            "reasoning_role": role,
            "content": content[:4000],
            "source": f"SEC EDGAR - {filing['ticker']}",
            "source_url": filing['url'],
            "credibility_class": "government_source",
            "year": int(filing['date'][:4]),
            "compatible_with": [],
            "incompatible_with": [],
            "weight": 1.0
        }
        return fragment
    
    def log_findings(self, filings):
        """Log to Obsidian."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"\n## SEC Scraper Run - {timestamp}\n")
            f.write(f"Found {len(filings)} new filings\n")
            for f_item in filings:
                f.write(f"- [{f_item['form_type']}] {f_item['ticker']}: {f_item['title']} ({f_item['url']})\n")
            f.write("\n")
    
    def run(self):
        """Main run method."""
        print("[SecScraper] Starting...")
        all_filings = []
        
        for ticker in self.tickers:
            for form_type in ['10-K', '10-Q']:
                filings = self.fetch_filings(ticker, form_type)
                all_filings.extend(filings)
                time.sleep(0.5)  # Rate limiting
        
        if not all_filings:
            print("[SecScraper] No new filings found.")
            self.save_last_run()
            return []
        
        fragments = []
        for filing in all_filings:
            fragment = self.generate_fragment(filing)
            if fragment:
                filename = f"{fragment['id']}.json"
                filepath = os.path.join(self.review_queue_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(fragment, f, indent=2)
                fragments.append(fragment)
                print(f"[SecScraper] Generated: {filename}")
        
        self.log_findings(all_filings)
        self.save_last_run()
        print(f"[SecScraper] Complete. {len(fragments)} fragments added to review queue.")
        return fragments

if __name__ == "__main__":
    scraper = SecScraper()
    scraper.run()
