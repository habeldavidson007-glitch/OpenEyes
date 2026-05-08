"""
Fragment Library — Domain Knowledge Fragment Store

Stores, indexes, and serves knowledge fragments. Manages fragment metadata:
- Source and credibility class
- Last-verified timestamp
- Domain tags
- Weight (from gene pool)
- Compatibility rules

Fragments are pre-existing, source-tagged pieces of knowledge. The system
selects from these fragments rather than generating new text.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class FragmentLibrary:
    """
    Knowledge fragment storage and retrieval.
    
    Each fragment is a verified piece of domain knowledge with:
    - Stable content-addressable ID (hash of source + content)
    - Credibility class and source URL
    - Domain tags for filtering
    - Compatibility/incompatibility rules
    """
    
    def __init__(self, library_path: str = None, domain: str = "general"):
        """
        Initialize Fragment Library.
        
        Args:
            library_path: Path to fragment library JSON file or directory
            domain: Default domain filter
        """
        self.domain = domain
        self.library_path = Path(library_path) if library_path else None
        self.fragments: Dict[str, Dict] = {}
        self.index: Dict[str, List[str]] = {}  # tag -> fragment_ids
        
        if self.library_path:
            self.load_library()
    
    def load_library(self) -> None:
        """Load fragments from library path."""
        if not self.library_path.exists():
            print(f"⚠ Fragment library not found: {self.library_path}")
            return
        
        if self.library_path.is_file():
            self._load_from_file(self.library_path)
        elif self.library_path.is_dir():
            for file in self.library_path.glob("*.json"):
                self._load_from_file(file)
    
    def _load_from_file(self, filepath: Path) -> None:
        """Load fragments from a single JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
                if isinstance(data, list):
                    fragments = data
                elif isinstance(data, dict) and "fragments" in data:
                    fragments = data["fragments"]
                else:
                    fragments = [data]
                
                for frag in fragments:
                    self.add_fragment(frag, rebuild_index=False)
            
            self._rebuild_index()
            print(f"✓ Loaded {len(self.fragments)} fragments from {filepath.name}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠ Failed to load fragment file {filepath}: {e}")
    
    def add_fragment(self, fragment: Dict, rebuild_index: bool = True) -> str:
        """
        Add a fragment to the library.
        
        Args:
            fragment: Fragment dict with required fields
            rebuild_index: Whether to rebuild the search index
            
        Returns:
            Fragment ID
        """
        # Generate stable ID if not provided
        if "id" not in fragment:
            content = fragment.get("content", "")
            source = fragment.get("source", "")
            id_input = f"{source}:{content}"
            fragment["id"] = f"frag_{hashlib.md5(id_input.encode()).hexdigest()[:16]}"
        
        # Set defaults
        fragment.setdefault("domain", self.domain)
        fragment.setdefault("weight", 1.0)
        fragment.setdefault("last_verified", datetime.now().isoformat()[:10])
        fragment.setdefault("compatible_with", [])
        fragment.setdefault("incompatible_with", [])
        
        self.fragments[fragment["id"]] = fragment
        
        if rebuild_index:
            self._rebuild_index()
        
        return fragment["id"]
    
    def _rebuild_index(self) -> None:
        """Rebuild the tag-based search index."""
        self.index = {}
        
        for frag_id, frag in self.fragments.items():
            tags = frag.get("tags", [])
            domain = frag.get("domain", "general")
            
            # Index by domain
            if domain not in self.index:
                self.index[domain] = []
            if frag_id not in self.index[domain]:
                self.index[domain].append(frag_id)
            
            # Index by tags
            for tag in tags:
                if tag not in self.index:
                    self.index[tag] = []
                if frag_id not in self.index[tag]:
                    self.index[tag].append(frag_id)
    
    def search(self, query: str, domain_filter: Optional[str] = None) -> List[Dict]:
        """
        Search for fragments matching a query.
        
        Args:
            query: Search query string
            domain_filter: Optional domain to filter by
            
        Returns:
            List of matching fragment dicts
        """
        # Simple keyword-based search
        # In production: use vector embeddings or BM25
        
        query_terms = set(query.lower().split())
        results = []
        
        # Filter by domain if specified
        candidates = self.fragments.values()
        if domain_filter:
            candidates = [f for f in candidates if f.get("domain") == domain_filter]
        elif self.domain != "general":
            # Use library's default domain if no explicit filter
            candidates = [f for f in candidates if f.get("domain") == self.domain or 
                         f.get("domain") in ["pharmacology", "medical"]]
        
        for frag in candidates:
            score = self._score_fragment(frag, query_terms)
            if score > 0:
                results.append((score, frag))
        
        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [frag for score, frag in results]
    
    def _score_fragment(self, fragment: Dict, query_terms: set) -> float:
        """
        Score a fragment's relevance to query terms.
        
        Args:
            fragment: Fragment dict
            query_terms: Set of lowercase query terms
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        score = 0.0
        
        # Check content match
        content = fragment.get("content", "").lower()
        for term in query_terms:
            if term in content:
                score += 0.3
        
        # Check tags match
        tags = [t.lower() for t in fragment.get("tags", [])]
        for term in query_terms:
            if term in tags:
                score += 0.5
        
        # Check domain match
        if fragment.get("domain", "").lower() in query_terms:
            score += 0.2
        
        return min(1.0, score)
    
    def get_fragment(self, fragment_id: str) -> Optional[Dict]:
        """Get a specific fragment by ID."""
        return self.fragments.get(fragment_id)
    
    def get_fragments_by_tag(self, tag: str) -> List[Dict]:
        """Get all fragments with a specific tag."""
        fragment_ids = self.index.get(tag, [])
        return [self.fragments[fid] for fid in fragment_ids if fid in self.fragments]
    
    def get_compatible_fragments(self, fragment_id: str) -> List[Dict]:
        """Get fragments compatible with a given fragment."""
        fragment = self.get_fragment(fragment_id)
        if not fragment:
            return []
        
        compatible_ids = fragment.get("compatible_with", [])
        return [self.fragments[fid] for fid in compatible_ids if fid in self.fragments]
    
    def check_compatibility(self, fragment_ids: List[str]) -> bool:
        """
        Check if a set of fragments are mutually compatible.
        
        Args:
            fragment_ids: List of fragment IDs to check
            
        Returns:
            True if all fragments are compatible, False otherwise
        """
        for fid in fragment_ids:
            fragment = self.get_fragment(fid)
            if not fragment:
                continue
            
            incompatible = fragment.get("incompatible_with", [])
            for other_fid in fragment_ids:
                if other_fid != fid and other_fid in incompatible:
                    return False
        
        return True
    
    def update_weight(self, fragment_id: str, weight: float) -> None:
        """Update a fragment's weight from the gene pool."""
        if fragment_id in self.fragments:
            # Clamp weight to valid range per spec
            weight = max(0.1, min(2.0, weight))
            self.fragments[fragment_id]["weight"] = round(weight, 2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics."""
        domains = {}
        credibility_classes = {}
        
        for frag in self.fragments.values():
            domain = frag.get("domain", "unknown")
            cred_class = frag.get("credibility_class", "unknown")
            
            domains[domain] = domains.get(domain, 0) + 1
            credibility_classes[cred_class] = credibility_classes.get(cred_class, 0) + 1
        
        return {
            "total_fragments": len(self.fragments),
            "domains": domains,
            "credibility_classes": credibility_classes,
            "index_size": len(self.index)
        }
    
    def save_library(self, filepath: Optional[str] = None) -> None:
        """Save the library to a JSON file."""
        output_path = Path(filepath) if filepath else self.library_path
        
        if not output_path:
            raise ValueError("No output path specified")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "version": "0.1",
            "last_updated": datetime.now().isoformat(),
            "fragments": list(self.fragments.values())
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Saved {len(self.fragments)} fragments to {output_path}")


def create_sample_medical_library() -> FragmentLibrary:
    """Create a sample medical fragment library for testing."""
    library = FragmentLibrary(domain="medical")
    
    # Sample fragments per the spec
    sample_fragments = [
        {
            "id": "frag_pharma_nitrofurantoin_uti_001",
            "domain": "pharmacology",
            "tags": ["antibiotic", "uti", "first_line", "safe_penicillin_allergy"],
            "content": "Nitrofurantoin 100mg modified-release twice daily for 5 days is a first-line treatment for uncomplicated lower UTI in non-pregnant adults.",
            "source": "NICE Clinical Guideline NG109",
            "source_url": "https://www.nice.org.uk/guidance/ng109",
            "credibility_class": "clinical_guideline",
            "last_verified": "2026-01-15",
            "weight": 1.0,
            "compatible_with": ["frag_pharma_allergy_cross_reactivity", "frag_pharma_dosage_adjustment_renal"],
            "incompatible_with": ["frag_pharma_penicillin_class"]
        },
        {
            "id": "frag_pharma_allergy_cross_reactivity",
            "domain": "pharmacology",
            "tags": ["allergy", "penicillin", "cross_reactivity", "contraindication"],
            "content": "Patients with penicillin allergy have <1% cross-reactivity with nitrofurantoin. Nitrofurantoin is considered safe for penicillin-allergic patients.",
            "source": "British National Formulary (BNF)",
            "source_url": "https://bnf.nice.org.uk/",
            "credibility_class": "clinical_guideline",
            "last_verified": "2026-01-10",
            "weight": 1.0,
            "compatible_with": ["frag_pharma_nitrofurantoin_uti_001"],
            "incompatible_with": []
        },
        {
            "id": "frag_pharma_trimethoprim_uti_002",
            "domain": "pharmacology",
            "tags": ["antibiotic", "uti", "second_line", "safe_penicillin_allergy"],
            "content": "Trimethoprim 200mg twice daily for 5 days is an alternative first-line treatment for uncomplicated lower UTI, but resistance rates vary by region.",
            "source": "NICE Clinical Guideline NG109",
            "source_url": "https://www.nice.org.uk/guidance/ng109",
            "credibility_class": "clinical_guideline",
            "last_verified": "2026-01-15",
            "weight": 0.95,
            "compatible_with": ["frag_pharma_allergy_cross_reactivity"],
            "incompatible_with": ["frag_pharma_penicillin_class"]
        }
    ]
    
    for frag in sample_fragments:
        library.add_fragment(frag)
    
    return library


__all__ = ["FragmentLibrary", "create_sample_medical_library"]