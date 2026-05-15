"""
openeyes/pipeline/retriever.py

UnifiedRetriever: Consolidates all retrieval mechanisms into a single interface.
Replaces: retrieval.py, local_retrieval.py, live_fetch.py, fragment_orchestrator.py, graceful_degradation.py
"""

import os
import hashlib
import re
import json
from collections import defaultdict
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
import logging
from datetime import date, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import requests for live fetching
try:
    import requests
except Exception:
    requests = None

try:
    import math
except ImportError:
    math = None

@dataclass
class RetrievalResult:
    fragments: List[Dict]
    source: str  # 'local', 'live', 'hybrid'
    confidence: float
    metadata: Dict

@dataclass
class IndexedFragment:
    """A fragment with indexing metadata for fast retrieval."""
    fragment_data: Dict
    domain: str
    sector: str
    topic: str
    role: str
    keywords: list[str]
    tags: list[str]
    tfidf_vector: dict[str, float] = field(default_factory=dict)
    
    @classmethod
    def from_json_file(cls, filepath: str) -> 'IndexedFragment | None':
        """Load a fragment from a standardized JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            filename = os.path.basename(filepath)
            
            # Try new format first: frag_{domain}_{sector}_{topic}_{role}_{num}.json
            if filename.startswith('frag_'):
                parts = filename.replace('.json', '').split('_')
                
                if len(parts) >= 5:
                    domain = parts[1]
                    sector = parts[2]
                    topic = parts[3]
                    role = parts[4]
                    
                    # Extract keywords from content - handle dict vs string
                    claim = data.get('claim', '') or data.get('content', '')
                    evidence = data.get('evidence', '')
                    
                    # Ensure we're working with strings
                    if isinstance(claim, dict):
                        claim = str(claim.get('text', '') or claim.get('content', ''))
                    if isinstance(evidence, dict):
                        evidence = str(evidence.get('text', ''))
                    
                    keywords = extract_keywords(str(claim) + ' ' + str(evidence))
                    
                    return cls._create_fragment(
                        data=data,
                        domain=domain,
                        sector=sector,
                        topic=topic,
                        role=role,
                        keywords=keywords,
                        source_id=filename,
                    )
            
            # Try legacy format: {topic}.json with fragments array
            if 'fragments' in data and isinstance(data['fragments'], list):
                # Process first fragment from the array
                if data['fragments']:
                    frag_data = data['fragments'][0]
                    
                    domain = frag_data.get('domain', 'unknown')
                    sector = frag_data.get('sector', frag_data.get('subdomain', 'unknown'))
                    topic = frag_data.get('topic', filename.replace('.json', ''))
                    role = frag_data.get('role', 'general')
                    
                    # Extract tags as keywords
                    keywords = frag_data.get('tags', [])
                    if not keywords:
                        content = frag_data.get('content', '')
                        keywords = extract_keywords(content)
                    
                    return cls._create_fragment(
                        data=frag_data,
                        domain=domain.lower() if domain else 'unknown',
                        sector=sector.lower() if sector else 'unknown',
                        topic=topic.lower().replace('_', ' ') if topic else 'unknown',
                        role=role,
                        keywords=keywords,
                        source_id=filename,
                    )
            
            # Single fragment format (no array)
            if 'content' in data or 'claim' in data:
                # Infer from path - three core domains only
                path_parts = filepath.split(os.sep)
                domain = 'unknown'
                sector = 'unknown'
                topic = filename.replace('.json', '')
                
                for i, part in enumerate(path_parts):
                    # Map directory names to three core domains
                    if part == 'hc':
                        domain = 'healthcare'
                    elif part == 'eco':
                        domain = 'economy'
                    elif part == 'gov':
                        domain = 'governance'
                    # Sectors within each domain
                    elif part in ['phr', 'med', 'mh', 'ph']:
                        sector = part
                        if domain == 'unknown':
                            domain = 'healthcare'
                    elif part in ['fin', 'enr', 'com', 'mac', 'geo', 'reg']:
                        sector = part
                        if domain == 'unknown':
                            domain = 'economy'
                    elif part in ['leg', 'jud', 'sec', 'sub', 'ele', 'gel', 'gov', 'int', 'ipl']:
                        sector = part
                        if domain == 'unknown':
                            domain = 'governance'
                
                content = data.get('content', '') or data.get('claim', '')
                keywords = extract_keywords(content)
                
                return cls._create_fragment(
                    data=data,
                    domain=domain,
                    sector=sector,
                    topic=topic.replace('_', ' '),
                    role='general',
                    keywords=keywords,
                    source_id=filename,
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"[LOCAL_INDEX] Error loading {filepath}: {e}")
            return None
    
    @classmethod
    def _create_fragment(cls, data: dict, domain: str, sector: str, topic: str, 
                         role: str, keywords: list[str], source_id: str) -> 'IndexedFragment':
        """Helper to create IndexedFragment from parsed data."""
        claim = data.get('claim', '') or data.get('content', '')
        
        fragment_dict = {
            'claim': claim,
            'evidence': data.get('evidence', '') or data.get('source', ''),
            'limitations': data.get('limitations', []),
            'sub_questions': data.get('sub_questions', []),
            'source_type': data.get('source_type', 'peer_reviewed_study'),
            'source_id': source_id,
            'source_url': data.get('source_url', '') or data.get('source', ''),
            'published_on': data.get('published_on', '') or (str(data.get('year', '')) + '-01-01' if data.get('year') else ''),
            'jurisdiction': data.get('jurisdiction', 'global'),
            'evidence_level': data.get('evidence_level', 'moderate'),
        }
        
        return cls(
            fragment_data=fragment_dict,
            domain=domain,
            sector=sector,
            topic=topic,
            role=role,
            keywords=keywords,
            tags=data.get('tags', []),
        )


def extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from text."""
    # Common stop words to filter out
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
        'we', 'they', 'what', 'which', 'who', 'whom', 'whose', 'where', 'when',
        'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
        'so', 'than', 'too', 'very', 'just', 'also', 'now', 'here', 'there',
        'then', 'once', 'if', 'because', 'as', 'until', 'while', 'about',
        'against', 'between', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again',
        'further', 'am', 'any', 'our', 'your'
    }
    
    # Extract words (alphanumeric, min 3 chars)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter stop words and deduplicate
    keywords = list(dict.fromkeys([w for w in words if w not in stop_words]))
    
    return keywords[:50]  # Limit to top 50 keywords


class LocalFragmentIndex:
    """
    In-memory index for local fragments with keyword-based retrieval.
    Integrated into UnifiedRetriever for consolidated retrieval.
    """
    
    def __init__(self, base_paths: list[str] = None):
        # Three core domain directories only: eco, gov, hc
        if base_paths is None:
            # Use dynamic path relative to package location
            import openeyes
            package_dir = Path(openeyes.__file__).parent
            self.base_paths = [
                str(package_dir / 'domains'),  # NEW: Domain-based directory structure
            ]
        else:
            self.base_paths = base_paths if isinstance(base_paths, list) else [base_paths]
        
        self.index: dict[str, list[IndexedFragment]] = defaultdict(list)  # domain -> fragments
        self.keyword_index: dict[str, list[IndexedFragment]] = defaultdict(list)  # keyword -> fragments
        self.entity_index: dict[str, list[IndexedFragment]] = defaultdict(list)  # entity -> fragments
        self.domain_sector_topic_index: dict[tuple, list[IndexedFragment]] = defaultdict(list)
        self.total_fragments = 0
        self._loaded = False
    
    def load_all(self) -> int:
        """Load all fragments from ALL domain directories."""
        if self._loaded:
            return self.total_fragments
        
        count = 0
        
        for base_path in self.base_paths:
            domains_dir = Path(base_path)
            
            if not domains_dir.exists():
                logger.debug(f"[LOCAL_INDEX] Directory not found: {domains_dir}")
                continue
            
            logger.info(f"[LOCAL_INDEX] Scanning directory: {domains_dir}")
            
            # Find ALL JSON files recursively
            for json_file in domains_dir.rglob('*.json'):
                indexed_frag = IndexedFragment.from_json_file(str(json_file))
                if indexed_frag:
                    # Add to domain index
                    self.index[indexed_frag.domain].append(indexed_frag)
                    
                    # Add to keyword index
                    for kw in indexed_frag.keywords:
                        self.keyword_index[kw].append(indexed_frag)
                    
                    # Add to entity index (topic-level entities)
                    entity_key = f"{indexed_frag.domain}:{indexed_frag.topic}"
                    self.entity_index[entity_key].append(indexed_frag)
                    
                    # Add to hierarchical index
                    hier_key = (indexed_frag.domain, indexed_frag.sector, indexed_frag.topic)
                    self.domain_sector_topic_index[hier_key].append(indexed_frag)
                    
                    count += 1
        
        self.total_fragments = count
        self._loaded = True
        logger.info(f"[LOCAL_INDEX] Loaded {count} total fragments across all directories")
        
        # Print domain breakdown
        for domain, frags in self.index.items():
            logger.info(f"[LOCAL_INDEX]   - {domain}: {len(frags)} fragments")
        
        return count
    
    def search_by_keywords(self, query: str, domain: str = None, limit: int = 10) -> list[Dict]:
        """Search fragments by keyword matching with TF-IDF-like scoring."""
        if not self._loaded:
            self.load_all()
        
        query_keywords = extract_keywords(query)
        if not query_keywords:
            return []
        
        # Score fragments by keyword overlap
        fragment_scores: dict[int, float] = defaultdict(float)
        frag_map = {}
        
        for kw in query_keywords:
            # Exact keyword match
            for frag in self.keyword_index.get(kw, []):
                if domain and frag.domain != domain:
                    continue
                frag_id = id(frag.fragment_data)
                frag_map[frag_id] = frag
                # Boost score for exact matches
                fragment_scores[frag_id] += 2.0
            
            # Partial keyword match (substring)
            for stored_kw, frags in self.keyword_index.items():
                if kw in stored_kw or stored_kw in kw:
                    for frag in frags:
                        if domain and frag.domain != domain:
                            continue
                        frag_id = id(frag.fragment_data)
                        frag_map[frag_id] = frag
                        fragment_scores[frag_id] += 0.5
        
        # Sort by score and return top fragments
        sorted_frags = sorted(
            fragment_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # Convert back to fragment dicts
        return [frag_map[frag_id].fragment_data for frag_id, _ in sorted_frags if frag_id in frag_map]
    
    def search_by_entity(self, entity: str, entity_type: str = None, domain: str = None, limit: int = 10) -> list[Dict]:
        """Search fragments by recognized entity (drug, condition, symptom, etc.)."""
        if not self._loaded:
            self.load_all()
        
        results = []
        entity_lower = entity.lower()
        
        # Search in entity index
        for key, frags in self.entity_index.items():
            if entity_lower in key.lower():
                for frag in frags:
                    if domain and frag.domain != domain:
                        continue
                    results.append(frag.fragment_data)
        
        # Also search in keywords
        for kw, frags in self.keyword_index.items():
            if entity_lower in kw or kw in entity_lower:
                for frag in frags:
                    if domain and frag.domain != domain:
                        continue
                    if frag.fragment_data not in results:
                        results.append(frag.fragment_data)
        
        return results[:limit]
    
    def search_by_hierarchical_path(self, domain: str, sector: str = None, topic: str = None, limit: int = 10) -> list[Dict]:
        """Search using the domain > sector > topic hierarchy."""
        if not self._loaded:
            self.load_all()
        
        results = []
        
        # Most specific: domain + sector + topic
        if sector and topic:
            key = (domain, sector, topic)
            results = [f.fragment_data for f in self.domain_sector_topic_index.get(key, [])]
        
        # Medium: domain + topic
        if not results and topic:
            for key, frags in self.domain_sector_topic_index.items():
                if key[0] == domain and key[2] == topic:
                    results.extend([f.fragment_data for f in frags])
        
        # Broad: domain + sector
        if not results and sector:
            for key, frags in self.domain_sector_topic_index.items():
                if key[0] == domain and key[1] == sector:
                    results.extend([f.fragment_data for f in frags])
        
        # Broadest: domain only
        if not results:
            results = [f.fragment_data for f in self.index.get(domain, [])]
        
        return results[:limit]

class UnifiedRetriever:
    """
    Unified retrieval interface that intelligently combines:
    - Local fragment retrieval (using integrated LocalFragmentIndex)
    - Live web fetching
    - Graceful degradation strategies
    
    Automatically selects the best retrieval strategy based on query type and available data.
    """
    
    def __init__(self):
        self.local_cache = {}
        self.live_enabled = os.getenv('OPENEYES_LIVE_FETCH', '1') == '1'
        self._local_index = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Lazy-load retrieval components only when needed."""
        self._live_fetcher = None
        self._orchestrator = None
    
    @property
    def local_index(self):
        """Get or create the local fragment index."""
        if self._local_index is None:
            self._local_index = LocalFragmentIndex()
        return self._local_index
    
    def build_local_index(self) -> int:
        """Build the local fragment index."""
        return self.local_index.load_all()
    
    @property
    def live_fetcher(self):
        """Return the live_fetch module for backward compatibility.
        
        Note: This is a placeholder property. The actual live fetching
        is handled by the original retrieval.py implementation.
        New code should use openeyes.knowledge.live_fetch directly.
        """
        if self._live_fetcher is None and self.live_enabled:
            from openeyes.knowledge import live_fetch
            self._live_fetcher = live_fetch
        return self._live_fetcher
    
    def retrieve(self, query: str, domain: Optional[str] = None, 
                 max_results: int = 10, use_live: bool = True) -> RetrievalResult:
        """
        Main retrieval method with intelligent fallback.
        
        Strategy:
        1. Try local retrieval first (fastest)
        2. If insufficient results and live enabled, fetch from web
        3. Apply graceful degradation if needed
        4. Return unified result set
        """
        # Step 1: Local retrieval
        local_fragments = self._retrieve_local(query, domain, max_results)
        
        # Step 2: Check if we need live fetch
        if len(local_fragments) < 3 and use_live and self.live_fetcher:
            live_fragments = self._retrieve_live(query, domain, max_results - len(local_fragments))
            local_fragments.extend(live_fragments)
        
        # Step 3: Apply quality filtering and scoring
        filtered_fragments = self._filter_and_score(local_fragments, query)
        
        # Step 4: Determine source and confidence
        has_live = any(f.get('_source') == 'live' for f in filtered_fragments)
        has_local = any(f.get('_source') == 'local' for f in filtered_fragments)
        
        if has_live and has_local:
            source = 'hybrid'
        elif has_live:
            source = 'live'
        else:
            source = 'local'
        
        # Calculate overall confidence
        if filtered_fragments:
            avg_confidence = sum(f.get('confidence_score', 0.5) for f in filtered_fragments) / len(filtered_fragments)
        else:
            avg_confidence = 0.0
        
        return RetrievalResult(
            fragments=filtered_fragments[:max_results],
            source=source,
            confidence=avg_confidence,
            metadata={
                'total_found': len(filtered_fragments),
                'local_count': sum(1 for f in filtered_fragments if f.get('_source') == 'local'),
                'live_count': sum(1 for f in filtered_fragments if f.get('_source') == 'live'),
                'domain': domain
            }
        )
    
    def _retrieve_local(self, query: str, domain: Optional[str], max_results: int) -> List[Dict]:
        """Retrieve from local fragment storage using integrated LocalFragmentIndex."""
        try:
            # First try the new integrated local index
            self.build_local_index()
            
            # Search by keywords
            results = self.local_index.search_by_keywords(query, domain=domain, limit=max_results * 2)
            
            if results:
                for frag in results:
                    frag['_source'] = 'local'
                return results
            
            # Fallback to old retrieval system if new index returns nothing
            from openeyes.knowledge.retrieval import retrieve_records
            records = retrieve_records(query, domain=domain, limit=max_results * 2)
            
            fragments = []
            for record in records:
                if isinstance(record, dict):
                    record['_source'] = 'local'
                    fragments.append(record)
                else:
                    # Convert Fragment object to dict
                    frag_dict = {
                        'claim': getattr(record, 'content', '') or getattr(record, 'claim', ''),
                        'confidence_score': getattr(record, 'confidence_score', 0.5),
                        'source_url': getattr(record, 'source_url', ''),
                        'domain': getattr(record, 'domain', domain or ''),
                        '_source': 'local'
                    }
                    fragments.append(frag_dict)
            
            return fragments
        except Exception as e:
            logger.warning(f"Local retrieval failed: {e}")
            return []
    
    def _retrieve_live(self, query: str, domain: Optional[str], max_results: int) -> List[Dict]:
        """Fetch fresh fragments from web sources."""
        try:
            from openeyes.knowledge.live_fetch import fetch_live_fragments
            fragments = fetch_live_fragments(query, domain=domain, limit=max_results)
            
            for frag in fragments:
                frag['_source'] = 'live'
            
            return fragments
        except Exception as e:
            logger.warning(f"Live fetch failed: {e}")
            return []
    
    def _filter_and_score(self, fragments: List[Dict], query: str) -> List[Dict]:
        """Filter low-quality fragments and re-score based on query relevance."""
        if not fragments:
            return []
        
        query_lower = query.lower()
        query_words = set(w for w in query_lower.split() if len(w) > 2)
        
        scored_fragments = []
        for frag in fragments:
            content = frag.get('claim', '').lower()
            
            # Skip obvious junk
            if len(content) < 20:
                continue
            
            # Skip fragments with scraper artifacts
            if any(artifact in content for artifact in ['duckduckgo', 'search endpoint', 'retrieved 0']):
                continue
            
            # Boost score for query term matches
            content_words = set(content.split())
            overlap = query_words & content_words
            
            base_score = frag.get('confidence_score', 0.5)
            relevance_boost = min(0.3, len(overlap) * 0.1)
            new_score = min(1.0, base_score + relevance_boost)
            
            frag['confidence_score'] = new_score
            scored_fragments.append(frag)
        
        # Sort by confidence
        scored_fragments.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
        
        return scored_fragments
    
    def get_fragments_by_domain(self, domain: str) -> List[Dict]:
        """Get all fragments for a specific domain."""
        try:
            from openeyes.fragment_library import FragmentLibrary
            lib = FragmentLibrary()
            fragments = lib.get_fragments_by_domain(domain)
            
            # Convert to dict format
            result = []
            for frag in fragments:
                if isinstance(frag, dict):
                    result.append(frag)
                else:
                    result.append({
                        'claim': getattr(frag, 'content', '') or getattr(frag, 'claim', ''),
                        'confidence_score': getattr(frag, 'confidence_score', 0.5),
                        'domain': getattr(frag, 'domain', domain)
                    })
            
            return result
        except Exception as e:
            logger.error(f"Error getting fragments for domain {domain}: {e}")
            return []
