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
    "source_url": "https://www.nice.org.uk/guidance/ng109 ",
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
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict


@dataclass
class Fragment:
    """A knowledge fragment with metadata."""
    id: str
    domain: str
    tags: List[str] = field(default_factory=list)
    content: str = ""
    source: str = ""
    source_url: str = ""
    credibility_class: str = "peer_reviewed_study"
    last_verified: str = None
    weight: float = 1.0
    compatible_with: List[str] = field(default_factory=list)
    incompatible_with: List[str] = field(default_factory=list)
    subdomain: Optional[str] = None
    sector: Optional[str] = None
    reasoning_role: Optional[str] = None
    source_type: Optional[str] = None
    year: Optional[int] = None
    sub_question: Optional[str] = None
    verified: Optional[bool] = None
    _original_credibility_class: Optional[str] = None
    _reasoning_role_auto_classified: Optional[bool] = None
    grundy_value: int = -1
    robustness_status: str = 'PENDING'
    topic: Optional[str] = None  # Legacy field, ignore if present
    
    def __post_init__(self):
        if self.last_verified is None:
            self.last_verified = datetime.now().strftime("%Y-%m-%d")
    
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Remove None and legacy fields
        return {k: v for k, v in d.items() if not k.startswith('_') and v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Fragment':
        # Filter out unknown/legacy fields and provide defaults for missing required fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        # Handle new role-based fragment structure (DEM_*.json format)
        if 'roles' in data and isinstance(data['roles'], dict):
            # Extract from roles structure
            roles = data['roles']
            definition = roles.get('definition', {})
            latest_data = roles.get('latest_data', {})
            
            # Use definition as primary content
            if 'content' not in filtered_data or not filtered_data.get('content'):
                filtered_data['content'] = definition.get('content', '')
            if 'source' not in filtered_data or not filtered_data.get('source'):
                filtered_data['source'] = definition.get('source', 'Unknown')
            if 'source_url' not in filtered_data or not filtered_data.get('source_url'):
                filtered_data['source_url'] = definition.get('url', '')
            if 'year' not in filtered_data or not filtered_data.get('year'):
                filtered_data['year'] = definition.get('year')
            
            # Store additional role content in tags for retrieval
            if 'tags' not in filtered_data:
                filtered_data['tags'] = []
            role_tags = list(roles.keys())  # ['definition', 'counter_argument', 'latest_data']
            filtered_data['tags'].extend(role_tags)
        
        # Ensure required fields have values
        if 'tags' not in filtered_data:
            filtered_data['tags'] = []
        if 'content' not in filtered_data or not filtered_data['content']:
            filtered_data['content'] = data.get('text', '')  # Fallback to 'text' if exists
        if 'source' not in filtered_data or not filtered_data['source']:
            filtered_data['source'] = 'Unknown'
        if 'source_url' not in filtered_data or not filtered_data['source_url']:
            filtered_data['source_url'] = ''
        if 'credibility_class' not in filtered_data or not filtered_data['credibility_class']:
            filtered_data['credibility_class'] = 'peer_reviewed_study'
        
        # Ensure id is present - this is critical
        if 'id' not in filtered_data or not filtered_data['id']:
            # Generate ID from domain/sector if available
            domain = filtered_data.get('domain', 'UNKNOWN')
            sector = filtered_data.get('sector', 'UNK')
            topic = filtered_data.get('topic', 'unknown')
            filtered_data['id'] = f"{sector}_{topic[:8]}_{len(str(hash(str(data))))}"
            
        return cls(**filtered_data)
    
    def is_compatible(self, other_fragment_id: str) -> bool:
        return other_fragment_id not in self.incompatible_with


class FragmentLibrary:
    CREDIBILITY_CLASSES = [
        "clinical_guideline",
        "peer_reviewed_study",
        "textbook",
        "expert_consensus",
        "case_report",
        "anecdotal"
    ]
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = Path(storage_path) if storage_path else Path(__file__).parent / "domains"
        
        if self.storage_path.is_symlink():
            self.storage_path = self.storage_path.resolve()
        
        if not self.storage_path.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._fragments: Dict[str, Fragment] = {}
        self._domain_index: Dict[str, List[str]] = {}
        self._tag_index: Dict[str, List[str]] = {}
        self._semantic_index: Dict[str, Set[str]] = defaultdict(set)
        
        self._load_all_fragments()
        self._build_semantic_index()
    
    def _load_all_fragments(self):
        if not self.storage_path.exists():
            return
        
        for domain_dir in self.storage_path.iterdir():
            if not domain_dir.is_dir() or domain_dir.name.startswith('.'):
                continue
            
            for sector_dir in domain_dir.iterdir():
                if not sector_dir.is_dir():
                    continue
                
                for fragment_file in sector_dir.glob("*.json"):
                    try:
                        with open(fragment_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if 'domain' not in data:
                                data['domain'] = domain_dir.name
                            if 'sector' not in data:
                                data['sector'] = sector_dir.name
                            
                            fragment = Fragment.from_dict(data)
                            self._register_fragment(fragment)
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        print(f"Warning: Failed to load {fragment_file}: {e}")
    
    def _register_fragment(self, fragment: Fragment):
        self._fragments[fragment.id] = fragment
        
        if fragment.domain not in self._domain_index:
            self._domain_index[fragment.domain] = []
        if fragment.id not in self._domain_index[fragment.domain]:
            self._domain_index[fragment.domain].append(fragment.id)
        
        for tag in fragment.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            if fragment.id not in self._tag_index[tag]:
                self._tag_index[tag].append(fragment.id)
    
    def _build_semantic_index(self):
        self._semantic_index.clear()
        
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
            'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
            'because', 'until', 'while', 'although', 'though', 'what', 'which',
            'who', 'whom', 'this', 'that', 'these', 'those', 'it', 'its'
        }
        
        for fragment in self._fragments.values():
            words = self._extract_words(fragment.content)
            
            if fragment.sub_question:
                words.update(self._extract_words(fragment.sub_question))
            
            for tag in fragment.tags:
                words.update(self._extract_words(tag))
            
            for word in words:
                if word not in stop_words and len(word) > 2:
                    self._semantic_index[word].add(fragment.id)
    
    def _extract_words(self, text: str) -> Set[str]:
        import re
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return set(words)
    
    def search_by_semantic_index(self, query: str) -> List[str]:
        query_words = self._extract_words(query)
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
            'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
            'because', 'until', 'while', 'although', 'though', 'what', 'which',
            'who', 'whom', 'this', 'that', 'these', 'those', 'it', 'its'
        }
        
        fragment_scores: Dict[str, int] = defaultdict(int)
        
        for word in query_words:
            if word not in stop_words and len(word) > 2:
                matching_fragments = self._semantic_index.get(word, set())
                for frag_id in matching_fragments:
                    fragment_scores[frag_id] += 1
        
        sorted_fragments = sorted(
            fragment_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [frag_id for frag_id, score in sorted_fragments if score > 0]
    
    def _save_fragment(self, fragment: Fragment):
        if self.storage_path:
            sector_dir = self.storage_path / fragment.domain / (fragment.sector or 'general')
            if not sector_dir.exists():
                sector_dir.mkdir(parents=True, exist_ok=True)
            
            fragment_file = sector_dir / f"{fragment.id}.json"
            with open(fragment_file, 'w', encoding='utf-8') as f:
                json.dump(fragment.to_dict(), f, indent=2)
    
    @staticmethod
    def generate_fragment_id(content: str, source: str) -> str:
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
        fragment_id: Optional[str] = None,
        sector: Optional[str] = None,
        reasoning_role: Optional[str] = None
    ) -> Fragment:
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
            incompatible_with=incompatible_with or [],
            sector=sector,
            reasoning_role=reasoning_role
        )
        
        self._register_fragment(fragment)
        self._save_fragment(fragment)
        
        return fragment
    
    def get_fragment(self, fragment_id: str) -> Optional[Fragment]:
        return self._fragments.get(fragment_id)
    
    def get_fragments_by_domain(self, domain: str) -> List[Fragment]:
        fragment_ids = self._domain_index.get(domain, [])
        return [self._fragments[fid] for fid in fragment_ids if fid in self._fragments]
    
    def get_fragments_by_tag(self, tag: str) -> List[Fragment]:
        fragment_ids = self._tag_index.get(tag, [])
        return [self._fragments[fid] for fid in fragment_ids if fid in self._fragments]
    
    def get_fragments_by_tags(self, tags: List[str], require_all: bool = False) -> List[Fragment]:
        if not tags:
            return []
        
        if require_all:
            candidate_ids = set(self._tag_index.get(tags[0], []))
            for tag in tags[1:]:
                candidate_ids &= set(self._tag_index.get(tag, []))
        else:
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
        results = []
        query_lower = query.lower()
        
        min_cred_idx = 0
        if min_credibility_class:
            if min_credibility_class not in self.CREDIBILITY_CLASSES:
                raise ValueError(f"Invalid credibility_class: {min_credibility_class}")
            min_cred_idx = self.CREDIBILITY_CLASSES.index(min_credibility_class)
        
        for fragment in self._fragments.values():
            if domain and fragment.domain != domain:
                continue
            
            if min_credibility_class:
                frag_cred_idx = self.CREDIBILITY_CLASSES.index(fragment.credibility_class)
                if frag_cred_idx < min_cred_idx:
                    continue
            
            if (query_lower in fragment.content.lower() or
                query_lower in fragment.source.lower() or
                any(query_lower in tag.lower() for tag in fragment.tags)):
                results.append(fragment)
        
        results.sort(key=lambda f: f.weight, reverse=True)
        return results
    
    def update_fragment_weight(self, fragment_id: str, new_weight: float):
        if fragment_id not in self._fragments:
            raise KeyError(f"Fragment not found: {fragment_id}")
        
        new_weight = max(0.1, min(2.0, new_weight))
        self._fragments[fragment_id].weight = new_weight
        self._save_fragment(self._fragments[fragment_id])
    
    def get_all_fragments(self) -> List[Fragment]:
        return list(self._fragments.values())
    
    def get_statistics(self) -> Dict[str, Any]:
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
        if fragment_id not in self._fragments:
            return False
        
        fragment = self._fragments[fragment_id]
        del self._fragments[fragment_id]
        
        if fragment.domain in self._domain_index:
            if fragment_id in self._domain_index[fragment.domain]:
                self._domain_index[fragment.domain].remove(fragment_id)
        
        for tag in fragment.tags:
            if tag in self._tag_index:
                if fragment_id in self._tag_index[tag]:
                    self._tag_index[tag].remove(fragment_id)
        
        if self.storage_path:
            sector_dir = self.storage_path / fragment.domain / (fragment.sector or 'general')
            fragment_file = sector_dir / f"{fragment_id}.json"
            if fragment_file.exists():
                fragment_file.unlink()
        
        return True


_default_library: Optional[FragmentLibrary] = None


def get_library(storage_path: Optional[Path] = None) -> FragmentLibrary:
    global _default_library
    if _default_library is None:
        _default_library = FragmentLibrary(storage_path)
    return _default_library


def reset_library():
    global _default_library
    _default_library = None
