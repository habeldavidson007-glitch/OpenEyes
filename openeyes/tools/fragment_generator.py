#!/usr/bin/env python3
"""
OpenEyes Fragment Generator Script

Takes a source URL and scaffolds a fragment JSON with the correct schema.
Automatically extracts content, detects domain tags, and pre-fills fields.

Usage:
    python openeyes/tools/fragment_generator.py <URL>
"""

import sys
import json
import re
import urllib.request
from html import unescape
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


# Credibility class mapping by domain
CREDIBILITY_MAP = {
    "federalreserve.gov": "peer_reviewed_study",
    "sec.gov": "government_source",
    "bls.gov": "government_source",
    "bea.gov": "government_source",
    "fred.stlouisfed.org": "government_source",
    "reuters.com": "news_article",
    "ft.com": "news_article",
    "bloomberg.com": "news_article"
}

# Finance tag taxonomy for auto-detection
FINANCE_TAGS = [
    "macro", "monetary_policy", "fiscal_policy", "inflation", "deflation",
    "interest_rate", "fed_funds_rate", "yield_curve", "inverted_yield_curve",
    "gdp", "recession", "economic_growth", "employment", "unemployment",
    "nonfarm_payroll", "labor_market", "consumer_spending", "retail_sales",
    "equities", "stock_market", "bull_market", "bear_market", "market_correction",
    "sp500", "nasdaq", "dow_jones", "index_fund", "etf",
    "fixed_income", "bonds", "treasury", "corporate_bonds", "yield",
    "duration", "credit_risk", "default_risk", "investment_grade", "junk_bonds",
    "crypto", "bitcoin", "ethereum", "defi", "stablecoin", "on_chain_metrics",
    "proof_of_work", "proof_of_stake", "blockchain", "smart_contracts",
    "earnings", "revenue", "gross_margin", "operating_margin", "net_margin",
    "free_cash_flow", "eps", "guidance", "analyst_estimates", "beat_miss",
    "valuation", "pe_ratio", "price_to_fcf", "price_to_sales", "ev_ebitda",
    "fundamental_analysis", "technical_analysis", "momentum", "support_resistance",
    "moving_average", "rsi", "macd", "volume", "market_cap",
    "risk_management", "volatility", "var", "hedging", "diversification",
    "correlation", "beta", "alpha", "sharpe_ratio", "drawdown",
    "regulation", "sec", "dodd_frank", "basel_iii", "insider_trading",
    "short_selling", "margin", "margin_call", "leverage", "derivatives",
    "options", "futures", "forex", "currency", "exchange_rate",
    "sector", "technology", "healthcare", "energy", "financials",
    "consumer_discretionary", "industrials", "utilities", "real_estate",
    "central_bank", "fed", "ecb", "boj", "pboc", "bank_of_england",
    "quantitative_easing", "quantitative_tightening", "balance_sheet",
    "first_line", "warning", "contraindication", "definition",
    "counter_argument", "latest_data"
]

# Topic keywords for ID generation
TOPIC_KEYWORDS = {
    "inflation": ["inflation", "cpi", "consumer price"],
    "interest_rate": ["interest rate", "fed funds", "policy rate"],
    "gdp": ["gdp", "gross domestic product", "economic output"],
    "employment": ["employment", "jobs", "nonfarm payroll", "unemployment"],
    "fed": ["federal reserve", "fed", "fomc", "central bank"],
    "treasury": ["treasury", "bonds", "fixed income"],
    "equities": ["stocks", "equities", "stock market", "sp500", "nasdaq"],
    "crypto": ["crypto", "bitcoin", "ethereum", "blockchain"],
    "earnings": ["earnings", "revenue", "eps", "guidance"],
    "regulation": ["sec", "regulation", "compliance", "dodd-frank"]
}


def fetch_url_content(url: str) -> Optional[str]:
    """Fetch HTML content from a URL."""
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (OpenEyes Fragment Generator)'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='ignore')
            return html
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None


def extract_main_text(html: str) -> str:
    """Extract main text content from HTML."""
    # Remove script and style tags
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.IGNORECASE | re.DOTALL)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities
    text = unescape(text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove excessive newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text


def detect_domain_tags(text: str) -> List[str]:
    """Auto-detect domain tags from content keywords."""
    text_lower = text.lower()
    detected_tags = []
    
    for tag in FINANCE_TAGS:
        tag_pattern = tag.replace('_', ' ')
        if tag_pattern in text_lower or tag in text_lower:
            detected_tags.append(tag)
    
    # Limit to top 10 most relevant tags
    return detected_tags[:10]


def detect_topic(text: str) -> str:
    """Detect main topic for fragment ID generation."""
    text_lower = text.lower()
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return topic
    
    return "general"


def determine_reasoning_role(text: str) -> str:
    """Determine the reasoning role based on content."""
    text_lower = text.lower()
    
    # Check for definition patterns
    if any(p in text_lower for p in ["is defined as", "refers to", "means", "definition"]):
        return "definition"
    
    # Check for latest data patterns
    if any(p in text_lower for p in ["released", "reported", "announced", "latest", "recent", "2024", "2025", "2026"]):
        return "latest_data"
    
    # Check for counter-argument patterns
    if any(p in text_lower for p in ["however", "but", "although", "despite", "contrary"]):
        return "counter_argument"
    
    # Default to definition
    return "definition"


def get_credibility_class(url: str) -> str:
    """Get credibility class from URL domain."""
    for domain, cred_class in CREDIBILITY_MAP.items():
        if domain in url.lower():
            return cred_class
    
    # Default for unknown sources
    return "news_article"


def generate_fragment_id(topic: str, role: str, counter: int = 1) -> str:
    """Generate a unique fragment ID."""
    return f"frag_fin_{topic}_{role}_{counter:03d}"


def scaffold_fragment(url: str) -> Optional[Dict[str, Any]]:
    """Create a fragment JSON scaffold from a URL."""
    print(f"\nFetching content from: {url}")
    
    # Fetch content
    html = fetch_url_content(url)
    if not html:
        print("Failed to fetch content from URL")
        return None
    
    # Extract main text
    full_text = extract_main_text(html)
    
    if len(full_text) < 100:
        print("Warning: Extracted text is very short, may not be valid content")
    
    # Truncate content to reasonable length (max 2000 chars for fragment)
    content = full_text[:2000] if len(full_text) > 2000 else full_text
    
    # Detect metadata
    topic = detect_topic(content)
    tags = detect_domain_tags(content)
    role = determine_reasoning_role(content)
    cred_class = get_credibility_class(url)
    
    # Extract source info
    domain = url.replace("https://www.", "").replace("https://", "").split("/")[0]
    source_name = domain
    
    # Generate ID
    fragment_id = generate_fragment_id(topic, role)
    
    # Get current year
    current_year = datetime.now().year
    
    # Build fragment JSON
    fragment = {
        "id": fragment_id,
        "domain": "finance",
        "subdomain": "",
        "tags": tags if tags else ["definition"],
        "reasoning_role": role,
        "content": content,
        "source": source_name,
        "source_url": url,
        "credibility_class": cred_class,
        "year": current_year,
        "compatible_with": [],
        "incompatible_with": [],
        "weight": 1.0
    }
    
    return fragment


def save_fragment(fragment: Dict[str, Any], output_dir: str) -> str:
    """Save fragment to file and return the path."""
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename from fragment ID
    filename = f"{fragment['id']}.json"
    filepath = output_path / filename
    
    # Write fragment JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(fragment, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


def main():
    if len(sys.argv) < 2:
        print("Usage: python fragment_generator.py <URL>")
        print("\nExample:")
        print("  python fragment_generator.py https://www.federalreserve.gov/newsevents/pressreleases/...")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Scaffold the fragment
    fragment = scaffold_fragment(url)
    
    if not fragment:
        print("Failed to create fragment scaffold")
        sys.exit(1)
    
    # Save to fragment library
    output_dir = "openeyes/fragment_library/fragments"
    filepath = save_fragment(fragment, output_dir)
    
    print(f"\n{'='*60}")
    print("FRAGMENT SCAFFOLD CREATED")
    print(f"{'='*60}")
    print(f"File saved to: {filepath}")
    print(f"\nFragment ID: {fragment['id']}")
    print(f"Domain: {fragment['domain']}")
    print(f"Tags: {', '.join(fragment['tags'])}")
    print(f"Reasoning Role: {fragment['reasoning_role']}")
    print(f"Credibility Class: {fragment['credibility_class']}")
    print(f"Source: {fragment['source']}")
    print(f"Year: {fragment['year']}")
    print(f"\nContent preview ({len(fragment['content'])} chars):")
    print("-"*60)
    print(fragment['content'][:300] + "..." if len(fragment['content']) > 300 else fragment['content'])
    print("-"*60)
    print("\nPlease review and edit the fragment before adding to the library.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
