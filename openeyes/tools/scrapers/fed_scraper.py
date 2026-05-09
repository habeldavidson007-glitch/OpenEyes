"""
Federal Reserve Scraper
Scrapes press releases, FOMC statements, and meeting minutes.
"""

import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

class FedScraper:
    def __init__(self):
        self.base_url = "https://www.federalreserve.gov"
        self.state_file = os.path.join(os.path.dirname(__file__), "state.json")
        self.review_queue_dir = os.path.join(os.path.dirname(__file__), "../../fragment_library/review_queue")
        self.log_file = os.path.join(os.path.dirname(__file__), "../../obsidian_connector/logs/scraper_logs.md")
        
        os.makedirs(self.review_queue_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
    def get_last_run(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                return state.get('fed_last_run', '2020-01-01')
        return '2020-01-01'
    
    def save_last_run(self):
        state = {}
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        state['fed_last_run'] = datetime.now().strftime('%Y-%m-%d')
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def fetch_new_content(self):
        """Fetch new Fed content since last run."""
        new_items = []
        last_run = self.get_last_run()
        
        # Press releases
        try:
            response = requests.get(f"{self.base_url}/newsevents/pressreleases.htm", timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract recent press releases (simplified parsing)
                for item in soup.find_all('a', href=True)[:10]:  # Top 10 recent
                    if '202' in item.text or '202' in item.get('href', ''):
                        title = item.text.strip()
                        url = self.base_url + item['href'] if item['href'].startswith('/') else item['href']
                        if last_run < '2020-01-01':  # Simplified date check
                            new_items.append({
                                'type': 'press_release',
                                'title': title,
                                'url': url,
                                'date': datetime.now().strftime('%Y-%m-%d')
                            })
        except Exception as e:
            print(f"[FedScraper] Error fetching press releases: {e}")
        
        return new_items
    
    def extract_content(self, url):
        """Extract text content from a Fed URL."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract main content
                content = soup.get_text(separator=' ', strip=True)[:5000]  # Limit length
                return content
        except Exception as e:
            print(f"[FedScraper] Error extracting content from {url}: {e}")
        return ""
    
    def generate_fragment(self, item):
        """Generate a fragment JSON for review."""
        content = self.extract_content(item['url'])
        if not content:
            return None
        
        # Determine subdomain and tags
        tags = ['monetary_policy', 'fed', 'latest_data']
        if 'FOMC' in item['title']:
            tags.append('fomc')
            subdomain = 'fomc_statements'
        elif 'interest' in item['title'].lower():
            tags.append('interest_rate')
            subdomain = 'policy_rates'
        else:
            subdomain = 'press_releases'
        
        fragment = {
            "id": f"frag_fin_fed_{len(content)}_{datetime.now().strftime('%Y%m%d')}",
            "domain": "finance",
            "subdomain": subdomain,
            "tags": tags,
            "reasoning_role": "latest_data",
            "content": content[:3000],  # Truncate for fragment
            "source": "Federal Reserve",
            "source_url": item['url'],
            "credibility_class": "peer_reviewed_study",
            "year": int(item['date'][:4]),
            "compatible_with": [],
            "incompatible_with": [],
            "weight": 1.0
        }
        return fragment
    
    def log_findings(self, items):
        """Log findings to Obsidian vault."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"\n## Fed Scraper Run - {timestamp}\n")
            f.write(f"Found {len(items)} new items\n")
            for item in items:
                f.write(f"- [{item['type']}] {item['title']} ({item['url']})\n")
            f.write("\n")
    
    def run(self):
        """Main run method."""
        print("[FedScraper] Starting...")
        new_items = self.fetch_new_content()
        
        if not new_items:
            print("[FedScraper] No new content found.")
            self.save_last_run()
            return []
        
        fragments = []
        for item in new_items:
            fragment = self.generate_fragment(item)
            if fragment:
                # Save to review queue
                filename = f"{fragment['id']}.json"
                filepath = os.path.join(self.review_queue_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(fragment, f, indent=2)
                fragments.append(fragment)
                print(f"[FedScraper] Generated fragment: {filename}")
        
        self.log_findings(new_items)
        self.save_last_run()
        print(f"[FedScraper] Complete. {len(fragments)} fragments added to review queue.")
        return fragments

if __name__ == "__main__":
    scraper = FedScraper()
    scraper.run()
