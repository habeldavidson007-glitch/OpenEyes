"""
OpenEyes Fragment Library

Stores, indexes, and serves knowledge fragments with metadata:
- source, credibility, last-verified timestamp
- domain tags, weight (from gene pool)
- compatibility rules

Fragment Schema:
{
    "id": "frag_pharma_nitrofurantoin_uti_001",
    "domain": "pharmacology",
    "tags": ["antibiotic", "uti", "first_line", "safe_penicillin_allergy"],
    "content": "Nitrofurantoin 100mg modified-release twice daily for 5 days...",
    "source": "NICE Clinical Guideline NG109",
    "source_url": "https://www.nice.org.uk/guidance/ng109",
    "credibility_class": "clinical_guideline",
    "last_verified": "2026-01-15",
    "weight": 1.0,
    "compatible_with": ["frag_pharma_allergy_cross_reactivity"],
    "incompatible_with": ["frag_pharma_penicillin_class"]
}
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class Fragment:
    """A knowledge fragment with metadata."""
    id: str
    domain: str
    tags: List[str]
    content: str
    source: str
    source_url: str
    credibility_class: str
    last_verified: str
    weight: float = 1.0
    compatible_with: List[str] = field(default_factory=list)
    incompatible_with: List[str] = field(default_factory=list)
    subdomain: Optional[str] = None
    reasoning_role: Optional[str] = None  # "definition", "counter_argument", "latest_data"
    source_type: Optional[str] = None     # "primary", "secondary", "tertiary"
    year: Optional[int] = None            # Publication year for temporal scoring
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Fragment':
        return cls(**data)
    
    def is_compatible(self, other_fragment_id: str) -> bool:
        """Check if this fragment is compatible with another."""
        return other_fragment_id not in self.incompatible_with


class FragmentLibrary:
    """
    Store, index, and serve knowledge fragments.
    
    Manages fragment metadata and provides retrieval methods
    for the Swarm layer.
    """
    
    CREDIBILITY_CLASSES = [
        "clinical_guideline",      # Highest - official guidelines
        "peer_reviewed_study",     # High - published research
        "textbook",                # High - established knowledge
        "expert_consensus",        # Medium - expert agreement
        "case_report",             # Lower - single case
        "anecdotal"                # Lowest - not recommended
    ]
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the fragment library.
        
        Args:
            storage_path: Path to store fragment JSON files. 
                         If None, uses in-memory only.
        """
        self.storage_path = Path(storage_path) if storage_path else Path(__file__).parent / "fragments"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # In-memory index: fragment_id -> Fragment
        self._fragments: Dict[str, Fragment] = {}
        
        # Domain index: domain -> [fragment_ids]
        self._domain_index: Dict[str, List[str]] = {}
        
        # Tag index: tag -> [fragment_ids]
        self._tag_index: Dict[str, List[str]] = {}
        
        # Load existing fragments
        self._load_all_fragments()
    
    def _load_all_fragments(self):
        """Load all fragments from storage."""
        if not self.storage_path.exists():
            return
        
        for fragment_file in self.storage_path.glob("*.json"):
            try:
                with open(fragment_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    fragment = Fragment.from_dict(data)
                    self._register_fragment(fragment)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Failed to load {fragment_file}: {e}")
    
    def _register_fragment(self, fragment: Fragment):
        """Register a fragment in all indices."""
        self._fragments[fragment.id] = fragment
        
        # Update domain index
        if fragment.domain not in self._domain_index:
            self._domain_index[fragment.domain] = []
        if fragment.id not in self._domain_index[fragment.domain]:
            self._domain_index[fragment.domain].append(fragment.id)
        
        # Update tag index
        for tag in fragment.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            if fragment.id not in self._tag_index[tag]:
                self._tag_index[tag].append(fragment.id)
    
    def _save_fragment(self, fragment: Fragment):
        """Save a fragment to storage."""
        if self.storage_path:
            fragment_file = self.storage_path / f"{fragment.id}.json"
            with open(fragment_file, 'w', encoding='utf-8') as f:
                json.dump(fragment.to_dict(), f, indent=2)
    
    @staticmethod
    def generate_fragment_id(content: str, source: str) -> str:
        """
        Generate a stable, content-addressable fragment ID.
        
        Uses hash of source + content for stability.
        """
        combined = f"{source}|{content}"
        hash_value = hashlib.sha256(combined.encode('utf-8')).hexdigest()[:12]
        return f"frag_{hash_value}"
    
    def add_fragment(
        self,
        domain: str,
        tags: List[str],
        content: str,
        source: str,
        source_url: str,
        credibility_class: str,
        last_verified: Optional[str] = None,
        weight: float = 1.0,
        compatible_with: Optional[List[str]] = None,
        incompatible_with: Optional[List[str]] = None,
        fragment_id: Optional[str] = None
    ) -> Fragment:
        """
        Add a new fragment to the library.
        
        Args:
            domain: Domain category (e.g., "pharmacology")
            tags: List of descriptive tags
            content: The actual knowledge content
            source: Source name (e.g., "NICE Clinical Guideline NG109")
            source_url: URL to the source
            credibility_class: One of CREDIBILITY_CLASSES
            last_verified: ISO date string, defaults to today
            weight: Initial weight (default 1.0)
            compatible_with: List of compatible fragment IDs
            incompatible_with: List of incompatible fragment IDs
            fragment_id: Optional custom ID, auto-generated if None
            
        Returns:
            The created Fragment
        """
        if credibility_class not in self.CREDIBILITY_CLASSES:
            raise ValueError(
                f"Invalid credibility_class: {credibility_class}. "
                f"Must be one of: {self.CREDIBILITY_CLASSES}"
            )
        
        if fragment_id is None:
            fragment_id = self.generate_fragment_id(content, source)
        
        if last_verified is None:
            last_verified = datetime.now().strftime("%Y-%m-%d")
        
        fragment = Fragment(
            id=fragment_id,
            domain=domain,
            tags=tags,
            content=content,
            source=source,
            source_url=source_url,
            credibility_class=credibility_class,
            last_verified=last_verified,
            weight=weight,
            compatible_with=compatible_with or [],
            incompatible_with=incompatible_with or []
        )
        
        self._register_fragment(fragment)
        self._save_fragment(fragment)
        
        return fragment
    
    def get_fragment(self, fragment_id: str) -> Optional[Fragment]:
        """Get a fragment by ID."""
        return self._fragments.get(fragment_id)
    
    def get_fragments_by_domain(self, domain: str) -> List[Fragment]:
        """Get all fragments in a domain."""
        fragment_ids = self._domain_index.get(domain, [])
        return [self._fragments[fid] for fid in fragment_ids if fid in self._fragments]
    
    def get_fragments_by_tag(self, tag: str) -> List[Fragment]:
        """Get all fragments with a specific tag."""
        fragment_ids = self._tag_index.get(tag, [])
        return [self._fragments[fid] for fid in fragment_ids if fid in self._fragments]
    
    def get_fragments_by_tags(self, tags: List[str], require_all: bool = False) -> List[Fragment]:
        """
        Get fragments matching tags.
        
        Args:
            tags: List of tags to match
            require_all: If True, fragment must have ALL tags. 
                        If False, fragment must have ANY tag.
        """
        if not tags:
            return []
        
        if require_all:
            # Find fragments that have all specified tags
            candidate_ids = set(self._tag_index.get(tags[0], []))
            for tag in tags[1:]:
                candidate_ids &= set(self._tag_index.get(tag, []))
        else:
            # Find fragments that have any of the specified tags
            candidate_ids = set()
            for tag in tags:
                candidate_ids |= set(self._tag_index.get(tag, []))
        
        return [self._fragments[fid] for fid in candidate_ids if fid in self._fragments]
    
    def search_fragments(
        self,
        query: str,
        domain: Optional[str] = None,
        min_credibility_class: Optional[str] = None
    ) -> List[Fragment]:
        """
        Search fragments by content/text match.
        
        Args:
            query: Search string (case-insensitive)
            domain: Optional domain filter
            min_credibility_class: Minimum credibility threshold
            
        Returns:
            List of matching fragments, sorted by weight (descending)
        """
        results = []
        query_lower = query.lower()
        
        # Determine minimum credibility index
        min_cred_idx = 0
        if min_credibility_class:
            if min_credibility_class not in self.CREDIBILITY_CLASSES:
                raise ValueError(f"Invalid credibility_class: {min_credibility_class}")
            min_cred_idx = self.CREDIBILITY_CLASSES.index(min_credibility_class)
        
        for fragment in self._fragments.values():
            # Domain filter
            if domain and fragment.domain != domain:
                continue
            
            # Credibility filter
            if min_credibility_class:
                frag_cred_idx = self.CREDIBILITY_CLASSES.index(fragment.credibility_class)
                if frag_cred_idx < min_cred_idx:
                    continue
            
            # Text search
            if (query_lower in fragment.content.lower() or
                query_lower in fragment.source.lower() or
                any(query_lower in tag.lower() for tag in fragment.tags)):
                results.append(fragment)
        
        # Sort by weight descending
        results.sort(key=lambda f: f.weight, reverse=True)
        return results
    
    def update_fragment_weight(self, fragment_id: str, new_weight: float):
        """Update a fragment's weight (called by survival_and_weights)."""
        if fragment_id not in self._fragments:
            raise KeyError(f"Fragment not found: {fragment_id}")
        
        # Clamp weight
        new_weight = max(0.1, min(2.0, new_weight))
        
        self._fragments[fragment_id].weight = new_weight
        self._save_fragment(self._fragments[fragment_id])
    
    def get_all_fragments(self) -> List[Fragment]:
        """Get all fragments in the library."""
        return list(self._fragments.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics."""
        domain_counts = {d: len(ids) for d, ids in self._domain_index.items()}
        
        credibility_counts = {}
        for frag in self._fragments.values():
            cc = frag.credibility_class
            credibility_counts[cc] = credibility_counts.get(cc, 0) + 1
        
        return {
            "total_fragments": len(self._fragments),
            "domains": domain_counts,
            "credibility_distribution": credibility_counts,
            "total_tags": len(self._tag_index),
            "average_weight": sum(f.weight for f in self._fragments.values()) / len(self._fragments) if self._fragments else 0
        }
    
    def remove_fragment(self, fragment_id: str) -> bool:
        """
        Remove a fragment from the library.
        
        Returns True if removed, False if not found.
        """
        if fragment_id not in self._fragments:
            return False
        
        fragment = self._fragments[fragment_id]
        
        # Remove from indices
        del self._fragments[fragment_id]
        
        if fragment.domain in self._domain_index:
            if fragment_id in self._domain_index[fragment.domain]:
                self._domain_index[fragment.domain].remove(fragment_id)
        
        for tag in fragment.tags:
            if tag in self._tag_index:
                if fragment_id in self._tag_index[tag]:
                    self._tag_index[tag].remove(fragment_id)
        
        # Remove from storage
        if self.storage_path:
            fragment_file = self.storage_path / f"{fragment_id}.json"
            if fragment_file.exists():
                fragment_file.unlink()
        
        return True


# Convenience functions for direct usage
_default_library: Optional[FragmentLibrary] = None


def get_library(storage_path: Optional[Path] = None) -> FragmentLibrary:
    """Get or create the default fragment library."""
    global _default_library
    if _default_library is None:
        _default_library = FragmentLibrary(storage_path)
    return _default_library


def reset_library():
    """Reset the default library (for testing)."""
    global _default_library
    _default_library = None
