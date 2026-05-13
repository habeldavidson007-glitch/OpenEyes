"""
FragmentLibrary — Compatibility Layer for Domain-Based Fragment Storage

This module provides the FragmentLibrary class that was previously a standalone storage system.
Now it acts as a compatibility wrapper around the new domain-based fragment organization:
  /workspace/openeyes/domains/{domain}/{sector}/frag_*.json

All existing imports of `from openeyes.fragment_library import FragmentLibrary` will work.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from openeyes.knowledge.fragments import Fragment


@dataclass
class FragmentMetadata:
    """Metadata for a fragment in the library."""
    filepath: str
    domain: str
    sector: str
    topic: str
    role: str
    confidence: float
    last_updated: str


class FragmentLibrary:
    """
    Fragment Library — Unified access layer for all domain fragments.
    
    This class provides backward-compatible access to fragments stored in the
    new domain-based directory structure:
        domains/{domain}/{sector}/frag_{domain}_{sector}_{topic}_{role}_{num}.json
    
    Usage:
        library = FragmentLibrary()
        frags = library.search(query="inflation", domain="economy")
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the fragment library.
        
        Args:
            storage_path: Base path for fragment storage. If None, uses the 
                         domains directory in the openeyes package.
        """
        if storage_path is None:
            # Default to the domains directory
            import openeyes
            package_dir = Path(openeyes.__file__).parent
            self.storage_path = package_dir / 'domains'
        else:
            self.storage_path = Path(storage_path)
        
        # Index structures
        self.fragments_by_id: dict[str, Fragment] = {}
        self.fragments_by_domain: dict[str, list[Fragment]] = defaultdict(list)
        self.fragments_by_sector: dict[str, list[Fragment]] = defaultdict(list)
        self.fragments_by_topic: dict[str, list[Fragment]] = defaultdict(list)
        self.keyword_index: dict[str, list[Fragment]] = defaultdict(list)
        
        self._loaded = False
        self.total_count = 0
        
    def load_all(self) -> int:
        """
        Load all fragments from the domain directories.
        
        Returns:
            Total number of fragments loaded.
        """
        if self._loaded:
            return self.total_count
        
        count = 0
        domains_dir = self.storage_path
        
        if not domains_dir.exists():
            print(f"[FragmentLibrary] Warning: Domains directory not found: {domains_dir}")
            return 0
        
        print(f"[FragmentLibrary] Loading fragments from: {domains_dir}")
        
        # Scan all domain directories
        for domain_dir in domains_dir.iterdir():
            if not domain_dir.is_dir() or domain_dir.name.startswith('.'):
                continue
                
            domain_name = domain_dir.name
            
            # Scan all sector directories within domain
            for sector_dir in domain_dir.iterdir():
                if not sector_dir.is_dir() or sector_dir.name.startswith('.'):
                    continue
                    
                sector_name = sector_dir.name
                
                # Load all JSON files in sector directory
                for json_file in sector_dir.glob('*.json'):
                    fragment = self._load_fragment_from_file(str(json_file))
                    if fragment:
                        self._index_fragment(fragment)
                        count += 1
        
        self.total_count = count
        self._loaded = True
        print(f"[FragmentLibrary] Loaded {count} fragments from {len(self.fragments_by_domain)} domains")
        return count
    
    def _load_fragment_from_file(self, filepath: str) -> Optional[Fragment]:
        """Load a single fragment from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both direct fragment format and wrapped format
            if 'fragment' in data:
                frag_data = data['fragment']
            else:
                frag_data = data
            
            # Create Fragment object
            fragment = Fragment(
                topic=frag_data.get('topic', ''),
                definition=frag_data.get('definition', ''),
                counter_argument=frag_data.get('counter_argument', ''),
                latest_data=frag_data.get('latest_data', ''),
                source_url=frag_data.get('source_url', ''),
                year=frag_data.get('year', 0),
                credibility_score=frag_data.get('credibility_score', 0.5),
                domain=frag_data.get('domain', ''),
                sector=frag_data.get('sector', ''),
                tags=frag_data.get('tags', []),
                metadata=frag_data.get('metadata', {})
            )
            
            # Store filepath in metadata
            fragment.metadata['filepath'] = filepath
            
            return fragment
            
        except Exception as e:
            print(f"[FragmentLibrary] Error loading {filepath}: {e}")
            return None
    
    def _index_fragment(self, fragment: Fragment):
        """Index a fragment for fast retrieval."""
        frag_id = f"{fragment.domain}_{fragment.sector}_{fragment.topic}"
        
        self.fragments_by_id[frag_id] = fragment
        self.fragments_by_domain[fragment.domain].append(fragment)
        self.fragments_by_sector[fragment.sector].append(fragment)
        self.fragments_by_topic[fragment.topic].append(fragment)
        
        # Index by keywords/tags
        for tag in fragment.tags:
            self.keyword_index[tag.lower()].append(fragment)
        
        # Also index key terms from topic
        words = fragment.topic.lower().replace('_', ' ').split()
        for word in words:
            if len(word) > 2:
                self.keyword_index[word].append(fragment)
    
    def search(self, query: str, domain: Optional[str] = None, 
               sector: Optional[str] = None, limit: int = 20) -> list[Fragment]:
        """
        Search for fragments matching a query.
        
        Args:
            query: Search query (matched against topics and tags)
            domain: Filter by domain (optional)
            sector: Filter by sector (optional)
            limit: Maximum number of results to return
            
        Returns:
            List of matching fragments, sorted by relevance.
        """
        if not self._loaded:
            self.load_all()
        
        query_lower = query.lower()
        candidates = []
        
        # Search by keyword matches
        matched_ids = set()
        for word in query_lower.split():
            if len(word) > 2 and word in self.keyword_index:
                for frag in self.keyword_index[word]:
                    if frag.topic not in matched_ids:
                        matched_ids.add(frag.topic)
                        candidates.append((frag, 1.0))
        
        # Search by topic substring match
        for frag_list in self.fragments_by_domain.values():
            for frag in frag_list:
                if query_lower in frag.topic.lower():
                    if frag.topic not in matched_ids:
                        matched_ids.add(frag.topic)
                        candidates.append((frag, 0.8))
        
        # Apply filters
        if domain:
            candidates = [(f, s) for f, s in candidates if f.domain == domain]
        if sector:
            candidates = [(f, s) for f, s in candidates if f.sector == sector]
        
        # Sort by score and return
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [frag for frag, score in candidates[:limit]]
    
    def get_by_domain(self, domain: str) -> list[Fragment]:
        """Get all fragments for a domain."""
        if not self._loaded:
            self.load_all()
        return self.fragments_by_domain.get(domain, [])
    
    def get_by_sector(self, sector: str) -> list[Fragment]:
        """Get all fragments for a sector."""
        if not self._loaded:
            self.load_all()
        return self.fragments_by_sector.get(sector, [])
    
    def get_by_topic(self, domain: str, sector: str, topic: str) -> Optional[Fragment]:
        """Get a specific fragment by domain, sector, and topic."""
        if not self._loaded:
            self.load_all()
        frag_id = f"{domain}_{sector}_{topic}"
        return self.fragments_by_id.get(frag_id)
    
    def count(self) -> int:
        """Get total fragment count."""
        if not self._loaded:
            self.load_all()
        return self.total_count
    
    def get_domains(self) -> list[str]:
        """Get list of all domains."""
        if not self._loaded:
            self.load_all()
        return list(self.fragments_by_domain.keys())
    
    def get_sectors(self, domain: str) -> list[str]:
        """Get list of sectors for a domain."""
        if not self._loaded:
            self.load_all()
        sectors = set()
        for frag in self.fragments_by_domain.get(domain, []):
            sectors.add(frag.sector)
        return list(sectors)
    
    def add_fragment(self, fragment: Fragment) -> bool:
        """Add a new fragment to the library."""
        if not self._loaded:
            self.load_all()
        
        self._index_fragment(fragment)
        self.total_count += 1
        return True
    
    def __len__(self) -> int:
        return self.count()
    
    def __repr__(self) -> str:
        return f"FragmentLibrary({self.total_count} fragments, {len(self.fragments_by_domain)} domains)"


# Export for backward compatibility
__all__ = ['FragmentLibrary', 'FragmentMetadata']
