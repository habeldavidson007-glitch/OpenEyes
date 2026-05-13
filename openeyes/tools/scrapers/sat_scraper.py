"""
Science & Technology Domain Scrapers
Automated scrapers for trusted scientific data sources.
"""

import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import hashlib
import time

class ArXivScraper:
    """Scrapes ArXiv for latest physics, CS, math preprints."""
    
    def __init__(self):
        self.base_url = "https://export.arxiv.org/api/query"
        self.state_file = os.path.join(os.path.dirname(__file__), "state_sat.json")
        self.review_queue_dir = os.path.join(os.path.dirname(__file__), "../../fragment_library/review_queue")
        os.makedirs(self.review_queue_dir, exist_ok=True)
        
    def get_last_run(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                return state.get('arxiv_last_run', '2024-01-01')
        return '2024-01-01'
    
    def save_last_run(self):
        state = {}
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        state['arxiv_last_run'] = datetime.now().strftime('%Y-%m-%d')
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def fetch_papers(self, category: str, max_results: int = 20) -> List[Dict]:
        """Fetch papers from a specific ArXiv category."""
        categories = {
            'PHY': ['physics.class-ph', 'physics.quant-ph', 'cond-mat'],
            'CSC': ['cs.AI', 'cs.LG', 'cs.CR', 'cs.SE'],
            'MAT': ['math.ST', 'math.PR', 'math.NA'],
            'BIO': ['q-bio'],
            'ENV': ['physics.ao-ph', 'q-bio.QM'],
            'SPC': ['astro-ph'],
            'ENG': ['physics.app-ph']
        }
        
        papers = []
        search_cats = categories.get(category, ['cs.AI'])
        
        for cat in search_cats:
            try:
                params = {
                    'search_query': f'cat:{cat}',
                    'start': 0,
                    'max_results': max_results // len(search_cats),
                    'sortBy': 'submittedDate',
                    'sortOrder': 'descending'
                }
                response = requests.get(self.base_url, params=params, timeout=15)
                if response.status_code == 200:
                    # Parse Atom XML (simplified)
                    soup = BeautifulSoup(response.text, 'xml')
                    for entry in soup.find_all('entry')[:5]:
                        title = entry.find('title').text.strip() if entry.find('title') else "No title"
                        summary = entry.find('summary').text.strip() if entry.find('summary') else ""
                        published = entry.find('published').text if entry.find('published') else datetime.now().isoformat()
                        paper_id = entry.find('id').text if entry.find('id') else f"arxiv_{int(time.time())}"
                        
                        papers.append({
                            'title': title,
                            'summary': summary[:2000],
                            'published': published[:10],
                            'paper_id': paper_id,
                            'category': cat
                        })
            except Exception as e:
                print(f"[ArXivScraper] Error fetching {cat}: {e}")
        
        return papers
    
    def generate_fragment(self, paper: Dict, sector: str, role: str) -> Optional[Dict]:
        """Generate a fragment JSON from an ArXiv paper."""
        content = f"{paper['title']}. {paper['summary']}"
        if not content.strip():
            return None
        
        fragment_id = f"frag_sat_{sector}_{role}_{hashlib.md5(paper['paper_id'].encode()).hexdigest()[:8]}"
        
        fragment = {
            "id": fragment_id,
            "domain": "sat",
            "subdomain": sector.lower(),
            "tags": [sector.lower(), paper['category'].replace('.', '_'), role],
            "reasoning_role": role,
            "content": content[:3000],
            "source": "ArXiv",
            "source_url": paper['paper_id'],
            "credibility_class": "peer_reviewed_study",
            "year": int(paper['published'][:4]) if paper['published'] else datetime.now().year,
            "compatible_with": [],
            "incompatible_with": [],
            "weight": 1.0
        }
        return fragment
    
    def run(self, sector: str) -> List[Dict]:
        """Run scraper for a specific SAT sector."""
        print(f"[ArXivScraper] Starting for sector {sector}...")
        papers = self.fetch_papers(sector)
        
        fragments = []
        roles = ['definition', 'counter_argument', 'latest_data']
        
        for i, paper in enumerate(papers):
            role = roles[i % 3]
            fragment = self.generate_fragment(paper, sector, role)
            if fragment:
                filename = f"{fragment['id']}.json"
                filepath = os.path.join(self.review_queue_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(fragment, f, indent=2)
                fragments.append(fragment)
                print(f"[ArXivScraper] Generated fragment: {filename}")
        
        self.save_last_run()
        print(f"[ArXivScraper] Complete. {len(fragments)} fragments added.")
        return fragments


class NasaScraper:
    """Scrapes NASA APIs for space and astronomy data."""
    
    def __init__(self):
        self.base_url = "https://api.nasa.gov"
        self.api_key = "DEMO_KEY"  # Replace with real key in production
        self.state_file = os.path.join(os.path.dirname(__file__), "state_sat.json")
        self.review_queue_dir = os.path.join(os.path.dirname(__file__), "../../fragment_library/review_queue")
        os.makedirs(self.review_queue_dir, exist_ok=True)
    
    def fetch_apeod(self) -> List[Dict]:
        """Fetch Astronomy Picture of the Day."""
        try:
            response = requests.get(
                f"{self.base_url}/apod",
                params={'api_key': self.api_key},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return [data]
        except Exception as e:
            print(f"[NasaScraper] Error fetching APOD: {e}")
        return []
    
    def fetch_neows(self) -> List[Dict]:
        """Fetch Near Earth Object data."""
        try:
            response = requests.get(
                f"{self.base_url}/neo/rest/v1/feed/today",
                params={'api_key': self.api_key},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('near_earth_objects', {}).get(datetime.now().strftime('%Y-%m-%d'), [])
        except Exception as e:
            print(f"[NasaScraper] Error fetching NEOWS: {e}")
        return []
    
    def generate_fragment(self, item: Dict, role: str) -> Optional[Dict]:
        """Generate a fragment from NASA data."""
        content = item.get('explanation', item.get('name', 'Space data'))
        if not content:
            return None
        
        fragment_id = f"frag_sat_spc_{role}_{hashlib.md5(str(item).encode()).hexdigest()[:8]}"
        
        fragment = {
            "id": fragment_id,
            "domain": "sat",
            "subdomain": "spc",
            "tags": ["space", "astronomy", "nasa", role],
            "reasoning_role": role,
            "content": content[:3000],
            "source": "NASA",
            "source_url": item.get('url', f"{self.base_url}/apod"),
            "credibility_class": "peer_reviewed_study",
            "year": datetime.now().year,
            "compatible_with": [],
            "incompatible_with": [],
            "weight": 1.0
        }
        return fragment
    
    def run(self) -> List[Dict]:
        """Run NASA scraper."""
        print("[NasaScraper] Starting...")
        fragments = []
        roles = ['definition', 'counter_argument', 'latest_data']
        
        # Fetch APOD
        apeod_items = self.fetch_apeod()
        for i, item in enumerate(apeod_items):
            fragment = self.generate_fragment(item, roles[i % 3])
            if fragment:
                filepath = os.path.join(self.review_queue_dir, f"{fragment['id']}.json")
                with open(filepath, 'w') as f:
                    json.dump(fragment, f, indent=2)
                fragments.append(fragment)
        
        # Fetch NEO data
        neo_items = self.fetch_neows()
        for i, item in enumerate(neo_items[:3]):
            fragment = self.generate_fragment(item, roles[i % 3])
            if fragment:
                filepath = os.path.join(self.review_queue_dir, f"{fragment['id']}.json")
                with open(filepath, 'w') as f:
                    json.dump(fragment, f, indent=2)
                fragments.append(fragment)
        
        print(f"[NasaScraper] Complete. {len(fragments)} fragments added.")
        return fragments


def run_all_sat_scrapers():
    """Run all SAT domain scrapers."""
    print("=" * 50)
    print("OpenEyes SAT Domain Scrapers - Starting Run")
    print("=" * 50)
    
    results = {
        'arxiv_phy': [],
        'arxiv_bio': [],
        'arxiv_env': [],
        'arxiv_csc': [],
        'arxiv_spc': [],
        'arxiv_eng': [],
        'arxiv_mat': [],
        'nasa': []
    }
    
    sectors = ['PHY', 'BIO', 'ENV', 'CSC', 'SPC', 'ENG', 'MAT']
    
    # Run ArXiv scrapers for each sector
    arxiv = ArXivScraper()
    for sector in sectors:
        try:
            results[f'arxiv_{sector.lower()}'] = arxiv.run(sector)
        except Exception as e:
            print(f"[ERROR] ArXiv {sector} scraper failed: {e}")
    
    # Run NASA scraper
    try:
        nasa = NasaScraper()
        results['nasa'] = nasa.run()
    except Exception as e:
        print(f"[ERROR] NASA scraper failed: {e}")
    
    # Summary
    total = sum(len(v) for v in results.values())
    print("=" * 50)
    print(f"Run Complete: {total} fragments added to review queue")
    for key, value in results.items():
        print(f"  - {key}: {len(value)}")
    print("=" * 50)
    
    return results


if __name__ == "__main__":
    run_all_sat_scrapers()
