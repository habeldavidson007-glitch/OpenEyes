"""
P0 Implementation: Local Fragment Retrieval System

This module implements robust local fragment indexing and retrieval
to fix the critical gap where 280+ curated JSON files exist but 
are never queried.

Key Features:
- Fragment indexing by domain, sector, topic, keywords
- TF-IDF semantic similarity search
- Entity extraction for drugs, conditions, symptoms
- Fallback chain: local → web → synthetic → low-confidence answer
"""

from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import math
except ImportError:
    math = None

from openeyes.knowledge.fragments import Fragment


@dataclass
class IndexedFragment:
    """A fragment with indexing metadata for fast retrieval."""
    fragment: Fragment
    domain: str
    sector: str
    topic: str
    role: str
    keywords: list[str]
    tags: list[str]
    tfidf_vector: dict[str, float] = field(default_factory=dict)
    
    @classmethod
    def from_json_file(cls, filepath: str) -> 'IndexedFragment | None':
        """Load a fragment from a standardized JSON file.
        
        Supports both formats:
        1. New format: frag_{domain}_{sector}_{topic}_{role}_{num}.json
        2. Legacy format: {topic}.json with fragments array
        """
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
            print(f"[LOCAL_INDEX] Error loading {filepath}: {e}")
            return None
    
    @classmethod
    def _create_fragment(cls, data: dict, domain: str, sector: str, topic: str, 
                         role: str, keywords: list[str], source_id: str) -> 'IndexedFragment':
        """Helper to create IndexedFragment from parsed data."""
        claim = data.get('claim', '') or data.get('content', '')
        
        fragment = Fragment(
            claim=claim,
            evidence=data.get('evidence', '') or data.get('source', ''),
            limitations=data.get('limitations', []),
            sub_questions=data.get('sub_questions', []),
            source_type=data.get('source_type', 'peer_reviewed_study'),
            source_id=source_id,
            source_url=data.get('source_url', '') or data.get('source', ''),
            published_on=data.get('published_on', '') or (str(data.get('year', '')) + '-01-01' if data.get('year') else ''),
            jurisdiction=data.get('jurisdiction', 'global'),
            evidence_level=data.get('evidence_level', 'moderate'),
        )
        
        return cls(
            fragment=fragment,
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
    
    Supports:
    - Domain/sector/topic filtering
    - Keyword matching with TF-IDF scoring
    - Entity recognition (drugs, conditions, symptoms)
    - Semantic similarity search
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
                print(f"[LOCAL_INDEX] Directory not found: {domains_dir}")
                continue
            
            print(f"[LOCAL_INDEX] Scanning directory: {domains_dir}")
            
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
        print(f"[LOCAL_INDEX] Loaded {count} total fragments across all directories")
        
        # Print domain breakdown
        for domain, frags in self.index.items():
            print(f"[LOCAL_INDEX]   - {domain}: {len(frags)} fragments")
        
        return count
    
    def search_by_keywords(self, query: str, domain: str = None, limit: int = 10) -> list[Fragment]:
        """Search fragments by keyword matching with TF-IDF-like scoring."""
        if not self._loaded:
            self.load_all()
        
        query_keywords = extract_keywords(query)
        if not query_keywords:
            return []
        
        # Score fragments by keyword overlap
        fragment_scores: dict[int, float] = defaultdict(float)
        
        for kw in query_keywords:
            # Exact keyword match
            for frag in self.keyword_index.get(kw, []):
                if domain and frag.domain != domain:
                    continue
                frag_id = id(frag.fragment)
                # Boost score for exact matches
                fragment_scores[frag_id] += 2.0
            
            # Partial keyword match (substring)
            for stored_kw, frags in self.keyword_index.items():
                if kw in stored_kw or stored_kw in kw:
                    for frag in frags:
                        if domain and frag.domain != domain:
                            continue
                        frag_id = id(frag.fragment)
                        fragment_scores[frag_id] += 0.5
        
        # Sort by score and return top fragments
        sorted_frags = sorted(
            fragment_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # Convert back to Fragment objects
        frag_map = {id(frag.fragment): frag.fragment for frags in self.index.values() for frag in frags}
        return [frag_map[frag_id] for frag_id, _ in sorted_frags if frag_id in frag_map]
    
    def search_by_entity(self, entity: str, entity_type: str = None, domain: str = None, limit: int = 10) -> list[Fragment]:
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
                    results.append(frag.fragment)
        
        # Also search in keywords
        for kw, frags in self.keyword_index.items():
            if entity_lower in kw or kw in entity_lower:
                for frag in frags:
                    if domain and frag.domain != domain:
                        continue
                    if frag.fragment not in results:
                        results.append(frag.fragment)
        
        return results[:limit]
    
    def search_by_hierarchical_path(self, domain: str, sector: str = None, topic: str = None, limit: int = 10) -> list[Fragment]:
        """Search using the domain > sector > topic hierarchy."""
        if not self._loaded:
            self.load_all()
        
        results = []
        
        # Most specific: domain + sector + topic
        if sector and topic:
            key = (domain, sector, topic)
            results = [f.fragment for f in self.domain_sector_topic_index.get(key, [])]
        
        # Medium: domain + topic
        if not results and topic:
            for key, frags in self.domain_sector_topic_index.items():
                if key[0] == domain and key[2] == topic:
                    results.extend([f.fragment for f in frags])
        
        # Broad: domain + sector
        if not results and sector:
            for key, frags in self.domain_sector_topic_index.items():
                if key[0] == domain and key[1] == sector:
                    results.extend([f.fragment for f in frags])
        
        # Broadest: domain only
        if not results:
            results = [f.fragment for f in self.index.get(domain, [])]
        
        return results[:limit]
    
    def get_domain_statistics(self) -> dict[str, Any]:
        """Get statistics about loaded fragments per domain."""
        stats = {}
        for domain, frags in self.index.items():
            sectors = set(f.sector for f in frags)
            topics = set(f.topic for f in frags)
            stats[domain] = {
                'total_fragments': len(frags),
                'sectors': len(sectors),
                'topics': len(topics),
                'sector_list': list(sectors),
                'topic_list': list(topics)[:20],  # Top 20
            }
        return stats


# Entity recognition dictionaries built from fragment content
ENTITY_TYPES = {
    'drug': [],
    'condition': [],
    'symptom': [],
    'procedure': [],
    'anatomy': [],
    'organization': [],
}


def build_entity_dictionaries(index: LocalFragmentIndex) -> dict[str, list[str]]:
    """Build entity dictionaries from loaded fragments."""
    entities = defaultdict(set)
    
    for domain, frags in index.index.items():
        for frag in frags:
            # Extract potential entities from topic and keywords
            topic = frag.topic.lower()
            
            # Simple heuristics for entity type classification
            if domain in ['hc', 'healthcare']:
                if any(x in topic for x in ['drug', 'medication', 'pharm', 'therapy']):
                    entities['drug'].add(topic)
                elif any(x in topic for x in ['disease', 'disorder', 'condition', 'syndrome', 'cancer']):
                    entities['condition'].add(topic)
                elif any(x in topic for x in ['symptom', 'sign', 'pain', 'fever']):
                    entities['symptom'].add(topic)
            
            # Add keywords as potential entities
            for kw in frag.keywords:
                entities['general'].add(kw)
    
    return {k: list(v) for k, v in entities.items()}


def recognize_entities(query: str, index: LocalFragmentIndex = None) -> list[dict[str, Any]]:
    """
    Recognize entities in a query (drugs, conditions, symptoms, etc.).
    
    Returns list of recognized entities with type and confidence.
    """
    entities = []
    query_lower = query.lower()
    
    # If we have an index, use its entity dictionaries
    if index and index._loaded:
        entity_dicts = build_entity_dictionaries(index)
        
        for entity_type, entity_list in entity_dicts.items():
            for entity in entity_list:
                if entity in query_lower:
                    entities.append({
                        'text': entity,
                        'type': entity_type,
                        'start': query_lower.find(entity),
                        'end': query_lower.find(entity) + len(entity),
                        'confidence': 0.8,
                    })
    
    # Pattern-based entity recognition
    # Drug names (capitalized words, common drug suffixes)
    drug_patterns = [
        r'\b[A-Z][a-z]+(?:pril|statin|olol|sartan|mab|tinib|ciclovir)\b',
        r'\b(metformin|warfarin|aspirin|ibuprofen|lisinopril|atorvastatin)\b',
    ]
    for pattern in drug_patterns:
        for match in re.finditer(pattern, query, re.IGNORECASE):
            entities.append({
                'text': match.group(),
                'type': 'drug',
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.9,
            })
    
    # Condition patterns
    condition_patterns = [
        r'\b(diabetes|hypertension|cancer|arthritis|depression|anxiety|asthma)\b',
        r'\b[A-Z][a-z]+(?:itis|osis|emia|opathy| syndrome)\b',
    ]
    for pattern in condition_patterns:
        for match in re.finditer(pattern, query, re.IGNORECASE):
            entities.append({
                'text': match.group(),
                'type': 'condition',
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.85,
            })
    
    # Symptom patterns
    symptom_patterns = [
        r'\b(pain|fever|headache|nausea|fatigue|dizziness|cough|rash)\b',
    ]
    for pattern in symptom_patterns:
        for match in re.finditer(pattern, query, re.IGNORECASE):
            entities.append({
                'text': match.group(),
                'type': 'symptom',
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.8,
            })
    
    # Deduplicate and sort by position
    seen = set()
    unique_entities = []
    for entity in sorted(entities, key=lambda x: x['start']):
        if entity['text'] not in seen:
            seen.add(entity['text'])
            unique_entities.append(entity)
    
    return unique_entities


# Singleton instance for global access
_local_index: LocalFragmentIndex | None = None


def get_local_index() -> LocalFragmentIndex:
    """Get or create the singleton local fragment index."""
    global _local_index
    if _local_index is None:
        _local_index = LocalFragmentIndex()
        _local_index.load_all()
    return _local_index


def retrieve_local_fragments(query: str, domain: str = None, limit: int = 10) -> list[Fragment]:
    """
    Main entry point: Retrieve relevant fragments from local storage.
    
    Strategy:
    1. Recognize entities in query
    2. Search by entity if found
    3. Fall back to keyword search
    4. Apply domain filtering (supports hc/eco/gov and full names)
    5. Return ranked results
    """
    from openeyes.knowledge.hierarchies import normalize_domain
    
    index = get_local_index()
    
    # Normalize domain code using central function, but keep original for fallback
    normalized_domain = normalize_domain(domain) if domain else None
    
    # CRITICAL FIX: The index uses short codes (eco, hc, gov), not full names
    # So we need to use the original domain code if it's already a short code
    domain_code = domain.lower() if domain else None
    
    # Step 1: Entity recognition
    entities = recognize_entities(query, index)
    
    if entities:
        # Search by primary entity - try both normalized and code forms
        primary_entity = entities[0]
        results = index.search_by_entity(
            primary_entity['text'],
            entity_type=primary_entity['type'],
            domain=domain_code,
            limit=limit
        )
        if results:
            return results
        
        # Fallback: try with normalized domain if code didn't work
        if normalized_domain and normalized_domain != domain_code:
            results = index.search_by_entity(
                primary_entity['text'],
                entity_type=primary_entity['type'],
                domain=normalized_domain,
                limit=limit
            )
            if results:
                return results
    
    # Step 2: Keyword search fallback - try domain code first
    results = index.search_by_keywords(query, domain=domain_code, limit=limit)
    
    # If no results and domain was specified, try without domain filter
    if not results and domain_code:
        results = index.search_by_keywords(query, domain=None, limit=limit)
    
    return results


if __name__ == '__main__':
    # Test the local fragment retrieval
    print("Testing Local Fragment Retrieval System...")
    
    index = get_local_index()
    stats = index.get_domain_statistics()
    
    print(f"\nLoaded {index.total_fragments} total fragments")
    print("\nDomain Statistics:")
    for domain, stat in stats.items():
        print(f"  {domain}: {stat['total_fragments']} fragments, {stat['sectors']} sectors, {stat['topics']} topics")
    
    # Test queries
    test_queries = [
        "What is metformin used for?",
        "Side effects of warfarin",
        "Treatment for diabetes",
        "Symptoms of hypertension",
    ]
    
    print("\n\nTest Query Results:")
    for query in test_queries:
        print(f"\nQuery: {query}")
        fragments = retrieve_local_fragments(query, domain='hc', limit=3)
        if fragments:
            for i, frag in enumerate(fragments[:3], 1):
                print(f"  {i}. [{frag.source_type}] {frag.claim[:100]}...")
        else:
            print("  No fragments found")
