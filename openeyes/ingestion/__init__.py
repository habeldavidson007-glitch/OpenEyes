"""
OpenEyes Automated Data Acquisition Module

This module provides autonomous web scraping capabilities when confidence is low.
It transforms OpenEyes from "Static Librarian" to "Autonomous Cognitive Engine".

Components:
- web_scraper: Playwright/BeautifulSoup based scraping for surface web
- auto_fragment: Converts scraped text into binary fragments
- consistency_checker: Binary search verification against existing knowledge
"""

from .web_scraper import scrape_authoritative_sources
from .auto_fragment import convert_to_fragments
from .consistency_checker import verify_consistency

__all__ = [
    'scrape_authoritative_sources',
    'convert_to_fragments', 
    'verify_consistency'
]
