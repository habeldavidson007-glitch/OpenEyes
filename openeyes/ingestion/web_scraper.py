"""
OpenEyes Web Scraper: Automated Data Acquisition

Phase 1 of Autonomous Cognitive Engine: "The Eyes"

This module uses Playwright and BeautifulSoup to scrape authoritative sources
when confidence is below threshold (< 0.5). It focuses on surface web sources
that are safe and reliable.

Authoritative Sources by Domain:
- Medical: PubMed, CDC, WHO, NCCN, Mayo Clinic
- Investment: SEC filings, Federal Reserve, BLS, Vanguard Research
- Legal: Cornell LII, Supreme Court, Government archives
- Science: NASA, NSF, National Academies, arXiv
- Technology: IEEE, ACM, NIST, official documentation
"""

from __future__ import annotations

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    BeautifulSoup = None
    requests = None

# Authoritative source URLs by domain
AUTHORITATIVE_SOURCES = {
    "medical": [
        "https://pubmed.ncbi.nlm.nih.gov/",
        "https://www.cdc.gov/",
        "https://www.who.int/",
        "https://www.nccn.org/",
        "https://www.mayoclinic.org/",
    ],
    "investment": [
        "https://www.sec.gov/",
        "https://www.federalreserve.gov/",
        "https://www.bls.gov/",
        "https://investor.vanguard.com/",
    ],
    "legal": [
        "https://www.law.cornell.edu/",
        "https://www.supremecourt.gov/",
        "https://www.congress.gov/",
    ],
    "science": [
        "https://www.nasa.gov/",
        "https://www.nsf.gov/",
        "https://www.nationalacademies.org/",
        "https://arxiv.org/",
    ],
    "technology": [
        "https://www.ieee.org/",
        "https://www.acm.org/",
        "https://www.nist.gov/",
    ],
    "engineering": [
        "https://www.iso.org/",
        "https://www.astm.org/",
        "https://www.asme.org/",
    ],
}

# Safe search prefixes for each domain
SEARCH_ENDPOINTS = {
    "medical": "https://pubmed.ncbi.nlm.nih.gov/?term={query}",
    "investment": "https://www.investopedia.com/search?q={query}",
    "legal": "https://www.law.cornell.edu/search?query={query}",
    "science": "https://arxiv.org/search/?query={query}&searchtype=all",
    "technology": "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={query}",
    "general": "https://en.wikipedia.org/w/index.php?search={query}",
}


def _expand_query(query: str, domain: str) -> List[str]:
    """Expand broad queries into focused retrieval intents."""
    q = query.lower()
    expanded = [query]
    if domain == "general" and any(k in q for k in ["world", "global", "current", "condition"]):
        expanded.extend([
            "global economy outlook 2026",
            "geopolitical conflict summary 2026",
            "climate change status report 2026",
            "ai and labor market impact 2026",
        ])
    return expanded


def _extract_text_from_html(html_content: str) -> str:
    """Extract clean text from HTML using BeautifulSoup."""
    if BeautifulSoup is None:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(['script', 'style', 'nav', 'footer', 'header']):
        script.decompose()
    
    # Get text
    text = soup.get_text(separator=' ', strip=True)
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text[:5000]  # Limit to 5000 chars


def _fetch_url(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch URL content with proper headers."""
    if requests is None:
        return None
    
    headers = {
        "User-Agent": "OpenEyes/1.0 (Autonomous Cognitive Engine; https://github.com/OpenEyes)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[SCRAPER] Failed to fetch {url}: {e}")
        return None


async def _scrape_with_playwright(url: str, timeout: int = 15) -> Optional[str]:
    """Scrape using Playwright for JavaScript-heavy sites."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return _fetch_url(url)  # Fallback to requests
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=timeout * 1000)
            
            # Wait for content to load
            await page.wait_for_load_state('networkidle', timeout=timeout * 1000)
            
            html = await page.content()
            await browser.close()
            
            return _extract_text_from_html(html)
    except Exception as e:
        print(f"[SCRAPER] Playwright failed for {url}: {e}")
        return _fetch_url(url)  # Fallback


def scrape_authoritative_sources(
    query: str,
    domain: str,
    max_results: int = 5,
    use_playwright: bool = False
) -> List[Dict[str, Any]]:
    """
    Scrape authoritative sources for the given query and domain.
    
    This is the "Research Loop" trigger when confidence < 0.5.
    
    Args:
        query: User's query string
        domain: Domain classification (medical, investment, etc.)
        max_results: Maximum number of results to return
        use_playwright: Whether to use Playwright for JS-heavy sites
        
    Returns:
        List of scraped content dictionaries with:
        - title: Page title
        - content: Extracted text content
        - source_url: Original URL
        - source_type: Type of source (peer_reviewed, government, etc.)
        - timestamp: When it was scraped
    """
    results = []
    expanded_queries = _expand_query(query, domain)
    
    # Get relevant sources for domain
    sources = AUTHORITATIVE_SOURCES.get(domain, AUTHORITATIVE_SOURCES.get("general", []))
    search_template = SEARCH_ENDPOINTS.get(domain, "")
    
    print(f"[SCRAPER] Searching {domain} sources for: {query}")
    
    # If we have a search endpoint, use it first
    if search_template and len(results) < max_results:
        for q in expanded_queries[:4]:
            if len(results) >= max_results:
                break
            search_url = search_template.format(query=q.replace(" ", "+"))
            print(f"[SCRAPER] Using search endpoint: {search_url}")
            if use_playwright:
                content = asyncio.run(_scrape_with_playwright(search_url))
            else:
                html = _fetch_url(search_url)
                content = _extract_text_from_html(html) if html else None

            if content:
                results.append({
                    "title": f"Search results for: {q}",
                    "content": content,
                    "source_url": search_url,
                    "source_type": "search_results",
                    "timestamp": datetime.now().isoformat(),
                })
    
    # Try direct source pages
    for source_url in sources[:3]:  # Limit to top 3 sources
        if len(results) >= max_results:
            break
        
        print(f"[SCRAPER] Fetching: {source_url}")
        
        if use_playwright:
            content = asyncio.run(_scrape_with_playwright(source_url))
        else:
            html = _fetch_url(source_url)
            content = _extract_text_from_html(html) if html else None
        
        if content and len(content) > 200:  # Only keep substantial content
            results.append({
                "title": f"Source: {source_url}",
                "content": content,
                "source_url": source_url,
                "source_type": _infer_source_type(source_url, domain),
                "timestamp": datetime.now().isoformat(),
            })
    
    print(f"[SCRAPER] Retrieved {len(results)} results")
    return results


def _infer_source_type(url: str, domain: str) -> str:
    """Infer source type from URL and domain."""
    url_lower = url.lower()
    
    if "pubmed" in url_lower or "ncbi" in url_lower:
        return "peer_reviewed_study"
    elif "cdc.gov" in url_lower or "who.int" in url_lower:
        return "government_report"
    elif "sec.gov" in url_lower:
        return "regulatory_filing"
    elif "law.cornell" in url_lower or "supremecourt" in url_lower:
        return "court_ruling"
    elif "arxiv" in url_lower:
        return "preprint_verified"
    elif "ieee" in url_lower or "iso.org" in url_lower:
        return "standard_specification"
    elif "nasa.gov" in url_lower or "nsf.gov" in url_lower:
        return "government_report"
    else:
        # Default based on domain
        type_map = {
            "medical": "clinical_guideline",
            "investment": "statistical_bureau",
            "legal": "court_ruling",
            "science": "peer_reviewed_study",
            "technology": "technical_manual",
            "engineering": "standard_specification",
        }
        return type_map.get(domain, "textbook")


if __name__ == "__main__":
    # Test scraper
    print("Testing Web Scraper...")
    results = scrape_authoritative_sources("cancer treatment", "medical", max_results=3)
    for r in results:
        print(f"\n{'='*60}")
        print(f"Title: {r['title']}")
        print(f"Source: {r['source_url']}")
        print(f"Type: {r['source_type']}")
        print(f"Content length: {len(r['content'])} chars")
