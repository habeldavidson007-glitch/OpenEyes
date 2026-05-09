"""
BLS Scraper
Scrapes Bureau of Labor Statistics for CPI, NFP, PPI releases.
"""

import requests
import json
import os
from datetime import datetime

class BlsScraper:
    def __init__(self):
        self.base_url = "https://www.bls.gov"
        self.state_file = os.path.join(os.path.dirname(__file__), "state.json")
        self.review_queue_dir = os.path.join(os.path.dirname(__file__), "../../fragment_library/review_queue")
        self.log_file = os.path.join(os.path.dirname(__file__), "../../obsidian_connector/logs/scraper_logs.md")
        
        # Key BLS release URLs
        self.release_urls = {
            'cpi': f"{self.base_url}/cpi/",
            'nfp': f"{self.base_url}/ces/",  # Current Employment Statistics
            'ppi': f"{self.base_url}/ppi/"
        }
        
        os.makedirs(self.review_queue_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def get_last_run(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                return state.get('bls_last_run', '2020-01-01')
        return '2020-01-01'
    
    def save_last_run(self):
        state = {}
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        state['bls_last_run'] = datetime.now().strftime('%Y-%m-%d')
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def check_new_release(self, release_type):
        """Check if new data is available for a release type."""
        new_releases = []
        try:
            url = self.release_urls[release_type]
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Look for "news release" or recent dates in the page
                text = response.text.lower()
                if 'news release' in text or 'latest' in text:
                    # Simplified detection - in production, parse actual release dates
                    new_releases.append({
                        'type': release_type,
                        'title': f"BLS {release_type.upper()} Latest Release",
                        'url': url,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
        except Exception as e:
            print(f"[BlsScraper] Error checking {release_type}: {e}")
        
        return new_releases
    
    def extract_content(self, url, release_type):
        """Extract summary content from BLS page."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Extract relevant sections
                content = f"BLS {release_type.upper()} Data Release\n\n"
                content += f"Source: {url}\n"
                content += f"Retrieved: {datetime.now().strftime('%Y-%m-%d')}\n\n"
                
                # In production, parse actual data tables
                content += "Latest data available. Refer to source URL for detailed tables and analysis."
                return content[:3000]
        except Exception as e:
            print(f"[BlsScraper] Error extracting from {url}: {e}")
        return ""
    
    def generate_fragment(self, release):
        """Generate fragment JSON for review."""
        content = self.extract_content(release['url'], release['type'])
        if not content:
            return None
        
        # Map release type to tags
        tag_map = {
            'cpi': ['inflation', 'cpi', 'consumer_price_index', 'latest_data'],
            'nfp': ['nonfarm_payroll', 'employment', 'labor_market', 'latest_data'],
            'ppi': ['ppi', 'producer_price_index', 'inflation', 'latest_data']
        }
        
        tags = tag_map.get(release['type'], ['bls', 'economic_data', 'latest_data'])
        subdomain = f"{release['type']}_data"
        
        fragment = {
            "id": f"frag_fin_bls_{release['type']}_{datetime.now().strftime('%Y%m%d')}",
            "domain": "finance",
            "subdomain": subdomain,
            "tags": tags,
            "reasoning_role": "latest_data",
            "content": content,
            "source": "Bureau of Labor Statistics",
            "source_url": release['url'],
            "credibility_class": "government_source",
            "year": int(release['date'][:4]),
            "compatible_with": [],
            "incompatible_with": [],
            "weight": 1.0
        }
        return fragment
    
    def log_findings(self, releases):
        """Log to Obsidian."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"\n## BLS Scraper Run - {timestamp}\n")
            f.write(f"Found {len(releases)} new releases\n")
            for rel in releases:
                f.write(f"- [{rel['type'].upper()}] {rel['title']} ({rel['url']})\n")
            f.write("\n")
    
    def run(self):
        """Main run method."""
        print("[BlsScraper] Starting...")
        all_releases = []
        
        for release_type in ['cpi', 'nfp', 'ppi']:
            releases = self.check_new_release(release_type)
            all_releases.extend(releases)
        
        if not all_releases:
            print("[BlsScraper] No new releases detected.")
            self.save_last_run()
            return []
        
        fragments = []
        for release in all_releases:
            fragment = self.generate_fragment(release)
            if fragment:
                filename = f"{fragment['id']}.json"
                filepath = os.path.join(self.review_queue_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(fragment, f, indent=2)
                fragments.append(fragment)
                print(f"[BlsScraper] Generated: {filename}")
        
        self.log_findings(all_releases)
        self.save_last_run()
        print(f"[BlsScraper] Complete. {len(fragments)} fragments added to review queue.")
        return fragments

if __name__ == "__main__":
    scraper = BlsScraper()
    scraper.run()
