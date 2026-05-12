"""
Live Ingestion Engine: Scraps data on-the-fly and creates new domain fragments.

This module allows OpenEyes to dynamically acquire knowledge when queries fail,
creating new domain folders and fragment files in the standard format.

Usage:
    python -m openeyes.ingestion.live_scraper "your query here"
    
Or integrate into the main engine flow when confidence is low.
"""
import os
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Import existing scraper
try:
    from .web_scraper import scrape_authoritative_sources, SEARCH_ENDPOINTS
except ImportError:
    # Fallback if running as script
    try:
        from web_scraper import scrape_authoritative_sources, SEARCH_ENDPOINTS
    except ImportError:
        def scrape_authoritative_sources(query, domain, max_results=5):
            print(f"[LIVE_INGEST] Warning: Scraper not available. Mocking for '{query}'")
            return []
        SEARCH_ENDPOINTS = {"general": "https://duckduckgo.com/html/?q={query}"}


class LiveIngestor:
    """
    Live data ingestion system that scrapes web content and converts it
    into OpenEyes fragment format, creating new domain directories as needed.
    """
    
    def __init__(self, base_knowledge_path: str = None):
        if base_knowledge_path is None:
            # Default to the standard knowledge path relative to this file
            base = Path(__file__).parent.parent.parent
            self.base_path = base / "knowledge" / "fragments"
        else:
            self.base_path = Path(base_knowledge_path)
        
        self.base_path.mkdir(parents=True, exist_ok=True)
        print(f"[LIVE_INGEST] Knowledge base path: {self.base_path}")

    def generate_domain_slug(self, topic: str, detected_domain: str = None) -> str:
        """
        Create a safe folder name from the topic.
        If a domain is detected (economy, medical, etc.), use that as prefix.
        """
        # Map common domain classifications to short codes
        domain_map = {
            "economy": "eco", "investment": "eco", "finance": "eco",
            "medical": "hc", "health": "hc", "healthcare": "hc",
            "government": "gov", "legal": "gov", "policy": "gov",
            "science": "sci", "technology": "tech",
        }
        
        prefix = domain_map.get(detected_domain.lower() if detected_domain else "", "live")
        slug = topic.lower().replace(" ", "_").replace("-", "_").replace("?", "")
        # Remove non-alphanumeric except underscore
        slug = "".join(c for c in slug if c.isalnum() or c == "_")[:40]  # Limit length
        return f"{prefix}_{slug}"

    def create_fragment(self, title: str, content: str, source_url: str, domain: str, query_context: str = "") -> Dict[str, Any]:
        """Format raw scraped data into the standard OpenEyes fragment structure."""
        fragment_id = hashlib.md5(f"{source_url}{time.time()}{title}".encode()).hexdigest()[:12]
        
        return {
            "id": fragment_id,
            "domain": domain,
            "topic": query_context or "live_ingested",
            "title": title[:200],  # Limit title length
            "content": content,
            "source": source_url,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.75,  # Moderate confidence for fresh scrapes
            "tags": [
                "live", 
                "auto-generated", 
                datetime.now().strftime("%Y-%m-%d"),
                "web-scraped"
            ],
            "metadata": {
                "ingestion_method": "live_scraper",
                "original_query": query_context
            }
        }

    def ingest_topic(self, topic: str, domain_hint: str = "general", num_sources: int = 8) -> Dict[str, Any]:
        """
        Main entry point: Scrapes topic, creates/uses domain directory, saves fragments.
        
        Args:
            topic: The query/topic to search for
            domain_hint: Suggested domain classification (economy, medical, etc.)
            num_sources: Number of sources to scrape
            
        Returns:
            Dictionary with ingestion statistics
        """
        print(f"\n🌱 [LIVE_INGEST] Starting live ingestion for: '{topic}'")
        print(f"   ├── Domain hint: {domain_hint}")
        
        # 1. Determine Domain Directory
        domain_slug = self.generate_domain_slug(topic, domain_hint)
        domain_path = self.base_path / domain_slug
        
        # 2. Create Domain Directory if missing
        if not domain_path.exists():
            domain_path.mkdir(parents=True, exist_ok=True)
            print(f"   ├── ✓ Created new domain directory: {domain_slug}/")
        else:
            existing_files = list(domain_path.glob("*.json"))
            print(f"   ├── ℹ Using existing domain: {domain_slug}/ ({len(existing_files)} existing fragments)")

        # 3. Scrape Data using existing OpenEyes scraper
        print(f"   ├── 🔍 Scraping web sources...")
        try:
            raw_results = scrape_authoritative_sources(
                query=topic,
                domain=domain_hint,
                max_results=num_sources,
                use_playwright=False  # Keep it fast for live ingestion
            )
        except Exception as e:
            print(f"   ├── [ERROR] Scraper failed: {e}")
            raw_results = []

        if not raw_results:
            print("   └── ⚠ No results found to ingest.")
            return {"ingested": 0, "domain": domain_slug, "path": str(domain_path)}

        # 4. Process and Save Fragments
        saved_count = 0
        for i, item in enumerate(raw_results):
            # Extract data from scraper result
            title = item.get('title', f"Ingested Result {i+1}")
            content = item.get('content', '')
            url = item.get('source_url', 'unknown')
            
            # Skip if no meaningful content
            if not content or len(content) < 50:
                continue

            # Create standardized fragment
            fragment_data = self.create_fragment(
                title=title,
                content=content[:8000],  # Limit content size
                source_url=url,
                domain=domain_slug,
                query_context=topic
            )

            # Save to JSON file
            filename = f"{fragment_data['id']}.json"
            filepath = domain_path / filename
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(fragment_data, f, indent=2, ensure_ascii=False)
                saved_count += 1
                
                # Show progress for first few items
                if saved_count <= 3:
                    preview = title[:60].replace('\n', ' ')
                    print(f"   ├── ✓ Ingested: {preview}...")
            except Exception as e:
                print(f"   ├── [ERROR] Failed to save {filename}: {e}")

        print(f"   └── ✅ [SUCCESS] Ingested {saved_count} new fragments into '{domain_slug}/'")
        
        return {
            "ingested": saved_count,
            "domain": domain_slug,
            "path": str(domain_path),
            "sources_scraped": len(raw_results)
        }

    def quick_ingest(self, query: str, auto_detect_domain: bool = True) -> int:
        """
        Simplified one-call ingestion. Auto-detects domain from query keywords.
        Returns number of fragments ingested.
        """
        # Simple keyword-based domain detection
        query_lower = query.lower()
        domain = "general"
        
        if any(k in query_lower for k in ["stock", "exchange rate", "roi", "market", "invest", "economy", "finance"]):
            domain = "economy"
        elif any(k in query_lower for k in ["disease", "treatment", "patient", "medical", "health", "drug", "fda"]):
            domain = "medical"
        elif any(k in query_lower for k in ["law", "court", "regulation", "policy", "government", "congress"]):
            domain = "government"
        elif any(k in query_lower for k in ["climate", "nasa", "space", "research", "study", "science"]):
            domain = "science"
        
        result = self.ingest_topic(topic=query, domain_hint=domain, num_sources=6)
        return result.get("ingested", 0)


# CLI entry point for manual testing and direct usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m openeyes.ingestion.live_scraper \"your query here\"")
        print("\nExample:")
        print('  python -m openeyes.ingestion.live_scraper "current stock market roi trends"')
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    ingestor = LiveIngestor()
    count = ingestor.quick_ingest(query)
    
    if count > 0:
        print(f"\n🎉 Successfully ingested {count} fragments!")
        print("You can now query OpenEyes again - the new knowledge is available immediately.")
    else:
        print("\n⚠ No data was ingested. Check network or try a different query.")
