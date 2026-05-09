"""
FRED Scraper
Pulls economic time series data from FRED API.
"""

import requests
import json
import os
from datetime import datetime

class FredScraper:
    def __init__(self):
        self.api_base = "https://api.stlouisfed.org/fred"
        self.api_key = "YOUR_FRED_API_KEY"  # User must replace with actual key
        self.state_file = os.path.join(os.path.dirname(__file__), "state.json")
        self.review_queue_dir = os.path.join(os.path.dirname(__file__), "../../fragment_library/review_queue")
        self.log_file = os.path.join(os.path.dirname(__file__), "../../obsidian_connector/logs/scraper_logs.md")
        
        # Key economic series IDs
        self.series_ids = {
            'GDP': 'GDP',
            'CPI': 'CPIAUCSL',
            'Unemployment': 'UNRATE',
            'Fed Funds Rate': 'FEDFUNDS',
            '10Y Treasury': 'GS10',
            '2Y Treasury': 'GS2',
            'M2 Money Stock': 'M2SL',
            'Nonfarm Payrolls': 'PAYEMS',
            'Retail Sales': 'RETAIL',
            'Consumer Sentiment': 'UMCSENT'
        }
        
        os.makedirs(self.review_queue_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def get_last_run(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                return state.get('fred_last_run', '2020-01-01')
        return '2020-01-01'
    
    def save_last_run(self):
        state = {}
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        state['fred_last_run'] = datetime.now().strftime('%Y-%m-%d')
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def fetch_series_data(self, series_id):
        """Fetch latest data for a FRED series."""
        try:
            url = f"{self.api_base}/series/observations"
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'limit': 5,
                'sort_order': 'desc'
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'observations' in data and len(data['observations']) > 0:
                    latest = data['observations'][0]
                    return {
                        'series_id': series_id,
                        'value': latest.get('value', 'N/A'),
                        'date': latest.get('date', ''),
                        'realtime_start': latest.get('realtime_start', '')
                    }
        except Exception as e:
            print(f"[FredScraper] Error fetching {series_id}: {e}")
        return None
    
    def generate_fragment(self, series_data, series_name):
        """Generate fragment JSON for review."""
        if not series_data or series_data['value'] == 'N/A':
            return None
        
        content = f"""FRED Economic Data: {series_name}

Series ID: {series_data['series_id']}
Latest Value: {series_data['value']}
Release Date: {series_data['date']}
Data Source: Federal Reserve Bank of St. Louis (FRED)

This data point represents the most recent observation for this economic indicator. 
Use in conjunction with historical trends for analysis.

API Retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Map series to tags
        tag_map = {
            'GDP': ['gdp', 'economic_growth', 'latest_data'],
            'CPI': ['cpi', 'inflation', 'latest_data'],
            'Unemployment': ['unemployment', 'labor_market', 'latest_data'],
            'Fed Funds Rate': ['fed_funds_rate', 'interest_rate', 'monetary_policy', 'latest_data'],
            '10Y Treasury': ['treasury', 'yield', 'fixed_income', 'latest_data'],
            '2Y Treasury': ['treasury', 'yield', 'fixed_income', 'latest_data'],
            'M2 Money Stock': ['money_supply', 'monetary_policy', 'latest_data'],
            'Nonfarm Payrolls': ['nonfarm_payroll', 'employment', 'latest_data'],
            'Retail Sales': ['retail_sales', 'consumer_spending', 'latest_data'],
            'Consumer Sentiment': ['consumer_sentiment', 'economic_indicator', 'latest_data']
        }
        
        tags = tag_map.get(series_name, ['fred', 'economic_data', 'latest_data'])
        
        fragment = {
            "id": f"frag_fin_fred_{series_data['series_id']}_{datetime.now().strftime('%Y%m%d')}",
            "domain": "finance",
            "subdomain": "economic_indicators",
            "tags": tags,
            "reasoning_role": "latest_data",
            "content": content.strip(),
            "source": "FRED - Federal Reserve Bank of St. Louis",
            "source_url": f"https://fred.stlouisfed.org/series/{series_data['series_id']}",
            "credibility_class": "government_source",
            "year": int(series_data['date'][:4]) if series_data['date'] else datetime.now().year,
            "compatible_with": [],
            "incompatible_with": [],
            "weight": 1.0
        }
        return fragment
    
    def log_findings(self, series_data_list):
        """Log to Obsidian."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"\n## FRED Scraper Run - {timestamp}\n")
            f.write(f"Fetched {len(series_data_list)} series\n")
            for sd in series_data_list:
                f.write(f"- {sd['name']}: {sd['data']['value']} ({sd['data']['date']})\n")
            f.write("\n")
    
    def run(self):
        """Main run method."""
        print("[FredScraper] Starting...")
        
        if self.api_key == "YOUR_FRED_API_KEY":
            print("[FredScraper] ERROR: API key not set. Replace YOUR_FRED_API_KEY in fred_scraper.py")
            return []
        
        all_data = []
        for series_name, series_id in self.series_ids.items():
            data = self.fetch_series_data(series_id)
            if data:
                all_data.append({'name': series_name, 'data': data})
        
        if not all_data:
            print("[FredScraper] No data retrieved.")
            self.save_last_run()
            return []
        
        fragments = []
        for item in all_data:
            fragment = self.generate_fragment(item['data'], item['name'])
            if fragment:
                filename = f"{fragment['id']}.json"
                filepath = os.path.join(self.review_queue_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(fragment, f, indent=2)
                fragments.append(fragment)
                print(f"[FredScraper] Generated: {filename}")
        
        self.log_findings(all_data)
        self.save_last_run()
        print(f"[FredScraper] Complete. {len(fragments)} fragments added to review queue.")
        return fragments

if __name__ == "__main__":
    scraper = FredScraper()
    scraper.run()
