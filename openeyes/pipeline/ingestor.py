"""
openeyes/pipeline/ingestor.py

KnowledgeIngestor: Consolidates all knowledge ingestion and fragment management.
Replaces: web_scraper.py, live_scraper.py, auto_fragment.py, consistency_checker.py, 
          fragments.py, fragment_validator.py, contradiction_scorer.py
"""

import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class IngestionResult:
    fragments_created: int
    sources_processed: int
    errors: List[str]
    metadata: Dict

class KnowledgeIngestor:
    """
    Unified knowledge ingestion engine that handles:
    - Web scraping from authoritative sources
    - Live data fetching
    - Automatic fragmentation
    - Consistency checking
    - Fragment validation
    - Contradiction detection
    
    Converts raw content into structured, validated fragments.
    """
    
    def __init__(self):
        self._scraper = None
        self._live_fetcher = None
        self._validator = None
        
    @property
    def scraper(self):
        if self._scraper is None:
            from openeyes.ingestion.web_scraper import scrape_authoritative_sources
            self._scraper = scrape_authoritative_sources
        return self._scraper
    
    @property
    def live_fetcher(self):
        if self._live_fetcher is None:
            from openeyes.ingestion.live_scraper import fetch_live_data
            self._live_fetcher = fetch_live_data
        return self._live_fetcher
    
    def ingest_query(self, query: str, domain: str, 
                     use_live: bool = True, max_fragments: int = 10) -> IngestionResult:
        """
        Main ingestion pipeline for a query:
        1. Scrape authoritative sources
        2. Fetch live data if enabled
        3. Convert to fragments
        4. Validate and check consistency
        5. Return validated fragments
        """
        errors = []
        all_content = []
        
        # Step 1: Scrape authoritative sources
        try:
            scraped_data = self._scrape_sources(query, domain)
            all_content.extend(scraped_data)
        except Exception as e:
            errors.append(f"Scraping failed: {str(e)}")
            logger.warning(f"Scraping error: {e}")
        
        # Step 2: Fetch live data if enabled
        if use_live:
            try:
                live_data = self._fetch_live(query, domain)
                all_content.extend(live_data)
            except Exception as e:
                errors.append(f"Live fetch failed: {str(e)}")
                logger.warning(f"Live fetch error: {e}")
        
        # Step 3: Convert to fragments
        if not all_content:
            return IngestionResult(
                fragments_created=0,
                sources_processed=0,
                errors=errors,
                metadata={'reason': 'no_content'}
            )
        
        fragments = self._convert_to_fragments(all_content, query, domain, max_fragments)
        
        # Step 4: Validate fragments
        validated_fragments = self._validate_fragments(fragments)
        
        # Step 5: Store fragments
        stored_count = self._store_fragments(validated_fragments, domain)
        
        return IngestionResult(
            fragments_created=stored_count,
            sources_processed=len(all_content),
            errors=errors,
            metadata={
                'domain': domain,
                'query_hash': hashlib.md5(query.encode()).hexdigest()[:8],
                'validation_passed': len(validated_fragments)
            }
        )
    
    def _scrape_sources(self, query: str, domain: str) -> List[Dict]:
        """Scrape authoritative sources for the query."""
        try:
            # Use existing scraper module
            from openeyes.ingestion.web_scraper import scrape_authoritative_sources
            results = scrape_authoritative_sources(query, domain=domain)
            
            if isinstance(results, list):
                return results
            elif isinstance(results, dict):
                return [results]
            else:
                return []
        except Exception as e:
            logger.warning(f"Scraping failed: {e}")
            return []
    
    def _fetch_live(self, query: str, domain: str) -> List[Dict]:
        """Fetch live data for time-sensitive queries."""
        try:
            from openeyes.ingestion.live_scraper import fetch_live_data
            results = fetch_live_data(query, domain=domain)
            
            if isinstance(results, list):
                return results
            elif isinstance(results, dict):
                return [results]
            else:
                return []
        except Exception as e:
            logger.warning(f"Live fetch failed: {e}")
            return []
    
    def _convert_to_fragments(self, content_list: List[Dict], 
                              query: str, domain: str, 
                              max_fragments: int) -> List[Dict]:
        """Convert raw content to structured fragments."""
        fragments = []
        today = datetime.now().strftime("%Y-%m-%d")
        
        for item in content_list:
            if len(fragments) >= max_fragments:
                break
            
            content = item.get('content', '') or item.get('text', '')
            if not content or len(content) < 50:
                continue
            
            # Extract claims from content
            claims = self._extract_claims(content, query)
            
            for claim in claims:
                if len(claim) < 30:
                    continue
                
                # Apply anti-hoax filtering
                if not self._is_factual_content(claim):
                    logger.info(f"Rejected potentially unreliable content")
                    continue
                
                fragment = {
                    'claim': claim[:800],
                    'evidence': f"Extracted from {item.get('source_type', 'web source')}",
                    'limitations': ['Auto-generated; verify with primary sources'],
                    'source_type': item.get('source_type', 'web'),
                    'source_id': self._compute_fragment_id(item.get('source_type', 'web'), claim),
                    'source_url': item.get('source_url', ''),
                    'published_on': item.get('published_date', today),
                    'jurisdiction': 'global',
                    'domain': domain,
                    'confidence_score': self._calculate_confidence(claim, item),
                    '_raw_content': content
                }
                
                fragments.append(fragment)
        
        return fragments
    
    def _extract_claims(self, content: str, query: str) -> List[str]:
        """Extract individual claims from content."""
        claims = []
        
        # Simple sentence splitting (can be enhanced with NLP)
        sentences = content.replace('\n', ' ').split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 30 or len(sentence) > 500:
                continue
            
            # Check if sentence is relevant to query
            query_words = set(w.lower() for w in query.split() if len(w) > 2)
            sentence_lower = sentence.lower()
            
            if any(word in sentence_lower for word in query_words):
                claims.append(sentence + '.')
        
        # If no relevant claims found, use first substantial sentence
        if not claims and sentences:
            for sentence in sentences:
                sentence = sentence.strip()
                if 50 <= len(sentence) <= 500:
                    claims.append(sentence + '.')
                    break
        
        return claims[:5]  # Limit claims per source
    
    def _is_factual_content(self, content: str) -> bool:
        """Check if content appears factual (anti-hoax filter)."""
        content_lower = content.lower()
        
        # Red flags for unreliable content
        red_flags = [
            'click here', 'you won\'t believe', 'shocking', 'miracle cure',
            'doctors hate', 'one weird trick', '100% guaranteed', 'conspiracy'
        ]
        
        if any(flag in content_lower for flag in red_flags):
            return False
        
        # Positive indicators of factual content
        positive_indicators = [
            'according to', 'study shows', 'research indicates', 'data suggests',
            'published in', 'experts say', 'clinical trial', 'peer-reviewed'
        ]
        
        # Count indicators
        positive_count = sum(1 for indicator in positive_indicators if indicator in content_lower)
        
        # Accept if has positive indicators or no red flags and reasonable length
        return positive_count >= 1 or (len(content) > 100 and not any(f in content_lower for f in red_flags))
    
    def _calculate_confidence(self, claim: str, source: Dict) -> float:
        """Calculate confidence score for a fragment."""
        base_score = 0.5
        
        # Boost for authoritative sources
        source_type = source.get('source_type', '').lower()
        if source_type in ['textbook', 'journal', 'government', 'edu']:
            base_score += 0.2
        elif source_type in ['news', 'reputable_media']:
            base_score += 0.1
        
        # Boost for specific claims (not vague)
        if len(claim.split()) >= 10:
            base_score += 0.1
        
        # Reduce for uncertainty language
        uncertainty_words = ['might', 'could', 'possibly', 'may', 'uncertain']
        if any(word in claim.lower() for word in uncertainty_words):
            base_score -= 0.1
        
        return min(1.0, max(0.1, base_score))
    
    def _compute_fragment_id(self, source_type: str, claim: str) -> str:
        """Generate unique fragment ID."""
        content = f"{source_type}:{claim}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _validate_fragments(self, fragments: List[Dict]) -> List[Dict]:
        """Validate fragments for quality and consistency."""
        validated = []
        
        for frag in fragments:
            # Basic validation
            if not frag.get('claim'):
                continue
            
            if len(frag['claim']) < 30:
                continue
            
            # Check for contradictions with existing fragments (simplified)
            if self._has_contradictions(frag):
                logger.info(f"Fragment rejected due to contradiction")
                continue
            
            validated.append(frag)
        
        return validated
    
    def _has_contradictions(self, new_fragment: Dict) -> bool:
        """Check if fragment contradicts existing knowledge."""
        # Simplified: just check for obvious negation patterns
        claim = new_fragment.get('claim', '').lower()
        
        # This is a placeholder - full implementation would check against fragment library
        contradiction_patterns = [
            'does not cause', 'is not associated', 'no evidence', 'debunked'
        ]
        
        # If new fragment contains contradiction language, might conflict
        return any(pattern in claim for pattern in contradiction_patterns)
    
    def _store_fragments(self, fragments: List[Dict], domain: str) -> int:
        """Store validated fragments in the fragment library."""
        try:
            from openeyes.fragment_library import FragmentLibrary
            lib = FragmentLibrary()
            
            stored = 0
            for frag in fragments:
                try:
                    # Create Fragment object
                    from openeyes.knowledge.fragments import Fragment
                    fragment_obj = Fragment(
                        claim=frag['claim'],
                        evidence=frag.get('evidence', ''),
                        limitations=frag.get('limitations', []),
                        source_type=frag.get('source_type', 'web'),
                        source_id=frag.get('source_id', ''),
                        source_url=frag.get('source_url', ''),
                        published_on=frag.get('published_on', ''),
                        jurisdiction=frag.get('jurisdiction', 'global'),
                        domain=domain,
                        confidence_score=frag.get('confidence_score', 0.5)
                    )
                    
                    lib.add_fragment(fragment_obj)
                    stored += 1
                except Exception as e:
                    logger.warning(f"Failed to store fragment: {e}")
            
            return stored
        except Exception as e:
            logger.error(f"Fragment storage failed: {e}")
            return 0
    
    def ingest_from_file(self, filepath: str, domain: str) -> IngestionResult:
        """Ingest knowledge from a file (JSON, TXT, etc.)."""
        errors = []
        
        try:
            import json
            
            with open(filepath, 'r') as f:
                if filepath.endswith('.json'):
                    content = json.load(f)
                else:
                    content = [{'content': f.read(), 'source_type': 'file'}]
            
            # Process content
            fragments = self._convert_to_fragments(content, '', domain, max_fragments=100)
            validated = self._validate_fragments(fragments)
            stored = self._store_fragments(validated, domain)
            
            return IngestionResult(
                fragments_created=stored,
                sources_processed=len(content),
                errors=errors,
                metadata={'filepath': filepath}
            )
        except Exception as e:
            errors.append(f"File ingestion failed: {str(e)}")
            return IngestionResult(
                fragments_created=0,
                sources_processed=0,
                errors=errors,
                metadata={'filepath': filepath}
            )
