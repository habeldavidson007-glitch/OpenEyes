"""
Finance Scrapers Package
Automated scrapers for trusted financial data sources.
"""

from .fed_scraper import FedScraper
from .sec_scraper import SecScraper
from .bls_scraper import BlsScraper
from .fred_scraper import FredScraper
from .sat_scraper import run_all_sat_scrapers, ArXivScraper, NasaScraper

def run_all_scrapers():
    """Run all finance scrapers sequentially."""
    print("=" * 50)
    print("OpenEyes Finance Scrapers - Starting Run")
    print("=" * 50)
    
    results = {
        'fed': [],
        'sec': [],
        'bls': [],
        'fred': []
    }
    
    # Run Fed scraper
    try:
        fed = FedScraper()
        results['fed'] = fed.run()
    except Exception as e:
        print(f"[ERROR] Fed scraper failed: {e}")
    
    # Run SEC scraper
    try:
        sec = SecScraper()
        results['sec'] = sec.run()
    except Exception as e:
        print(f"[ERROR] SEC scraper failed: {e}")
    
    # Run BLS scraper
    try:
        bls = BlsScraper()
        results['bls'] = bls.run()
    except Exception as e:
        print(f"[ERROR] BLS scraper failed: {e}")
    
    # Run FRED scraper
    try:
        fred = FredScraper()
        results['fred'] = fred.run()
    except Exception as e:
        print(f"[ERROR] FRED scraper failed: {e}")
    
    # Summary
    total = sum(len(v) for v in results.values())
    print("=" * 50)
    print(f"Run Complete: {total} fragments added to review queue")
    print(f"  - Fed: {len(results['fed'])}")
    print(f"  - SEC: {len(results['sec'])}")
    print(f"  - BLS: {len(results['bls'])}")
    print(f"  - FRED: {len(results['fred'])}")
    print("=" * 50)
    
    return results


def run_sat_scrapers():
    """Run all SAT domain scrapers."""
    return run_all_sat_scrapers()


if __name__ == "__main__":
    run_all_scrapers()
