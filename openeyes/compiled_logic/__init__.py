"""
Compiled Logic Index: The Instinct Layer for OpenEyes.

This module implements Phase 2 of the architectural shift:
- Stores pre-verified fragment combinations (Synapses) 
- Provides instant retrieval for familiar queries
- Falls back to Monte Carlo simulation for novel queries
- Automatically creates new synapses from high-confidence results

Neuroscience Parallel: Moves decisions from energy-expensive deliberation 
(Prefrontal Cortex/Monte Carlo) to efficient instinct (Basal Ganglia/Compiled Logic).
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib


class Synapse:
    """
    A pre-compiled logic chain that bypasses Monte Carlo simulation.
    
    Represents a verified fragment combination that has proven successful
    across multiple queries with high consistency.
    """
    
    def __init__(self, synapse_id: str, fragment_chain: List[str], 
                 trigger_keywords: List[str], avg_confidence: float,
                 metadata: Dict[str, Any] = None):
        self.synapse_id = synapse_id
        self.fragment_chain = fragment_chain  # List of fragment_ids in order
        self.trigger_keywords = trigger_keywords  # Keywords that activate this synapse
        self.avg_confidence = avg_confidence
        self.usage_count = 0
        self.created_at = datetime.now().isoformat()
        self.last_used = None
        self.metadata = metadata or {}
        
    def matches_query(self, query_keywords: List[str]) -> bool:
        """Check if query keywords match this synapse's trigger pattern."""
        if not self.trigger_keywords:
            return False
            
        # Require at least 50% keyword overlap
        query_set = set(query_keywords)
        trigger_set = set(self.trigger_keywords)
        
        if not trigger_set:
            return False
            
        overlap = len(query_set & trigger_set)
        required = max(1, len(trigger_set) // 2)
        
        return overlap >= required
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize synapse to dictionary."""
        return {
            'synapse_id': self.synapse_id,
            'fragment_chain': self.fragment_chain,
            'trigger_keywords': self.trigger_keywords,
            'avg_confidence': self.avg_confidence,
            'usage_count': self.usage_count,
            'created_at': self.created_at,
            'last_used': self.last_used,
            'metadata': self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Synapse':
        """Deserialize synapse from dictionary."""
        synapse = cls(
            synapse_id=data['synapse_id'],
            fragment_chain=data['fragment_chain'],
            trigger_keywords=data.get('trigger_keywords', []),
            avg_confidence=data['avg_confidence'],
            metadata=data.get('metadata', {})
        )
        synapse.usage_count = data.get('usage_count', 0)
        synapse.created_at = data.get('created_at', datetime.now().isoformat())
        synapse.last_used = data.get('last_used')
        return synapse


class CompiledLogicIndex:
    """
    The Instinct Layer: stores and retrieves pre-compiled Synapses.
    
    Provides O(1) lookup for familiar queries, falling back to 
    Monte Carlo simulation for novel queries.
    """
    
    def __init__(self, storage_path: str = "/workspace/openeyes/data/compiled_logic.json"):
        self.storage_path = storage_path
        self.synapses: Dict[str, Synapse] = {}
        self.keyword_index: Dict[str, List[str]] = {}  # keyword -> [synapse_ids]
        
        # Load existing synapses
        self._load_synapses()
        
    def _load_synapses(self):
        """Load synapses from storage file."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    
                for synapse_data in data.get('synapses', []):
                    synapse = Synapse.from_dict(synapse_data)
                    self.synapses[synapse.synapse_id] = synapse
                    
                # Rebuild keyword index
                self._rebuild_keyword_index()
                
                print(f"[CompiledLogicIndex] Loaded {len(self.synapses)} synapses")
            except Exception as e:
                print(f"[CompiledLogicIndex] Error loading synapses: {e}")
                self.synapses = {}
        else:
            print("[CompiledLogicIndex] No existing synapses found, starting fresh")
            
    def _rebuild_keyword_index(self):
        """Rebuild the keyword-to-synapse index."""
        self.keyword_index = {}
        
        for synapse_id, synapse in self.synapses.items():
            for keyword in synapse.trigger_keywords:
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = []
                self.keyword_index[keyword].append(synapse_id)
                
    def _save_synapses(self):
        """Save synapses to storage file."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        data = {
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'synapses': [s.to_dict() for s in self.synapses.values()]
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def add_synapse(self, synapse: Synapse) -> bool:
        """Add a new synapse to the index."""
        if synapse.synapse_id in self.synapses:
            print(f"[CompiledLogicIndex] Synapse {synapse.synapse_id} already exists, updating")
            
        self.synapses[synapse.synapse_id] = synapse
        self._rebuild_keyword_index()
        self._save_synapses()
        
        print(f"[CompiledLogicIndex] Added synapse: {synapse.synapse_id} with {len(synapse.fragment_chain)} fragments")
        return True
        
    def remove_synapse(self, synapse_id: str) -> bool:
        """Remove a synapse from the index."""
        if synapse_id in self.synapses:
            del self.synapses[synapse_id]
            self._rebuild_keyword_index()
            self._save_synapses()
            print(f"[CompiledLogicIndex] Removed synapse: {synapse_id}")
            return True
        return False
        
    def query(self, query_keywords: List[str]) -> Optional[Synapse]:
        """
        Find the best matching synapse for given query keywords.
        
        Returns the synapse with highest confidence that matches the query,
        or None if no match found.
        """
        if not query_keywords:
            return None
            
        candidates = []
        
        # Find synapses that match query keywords
        for keyword in query_keywords:
            if keyword in self.keyword_index:
                for synapse_id in self.keyword_index[keyword]:
                    synapse = self.synapses.get(synapse_id)
                    if synapse and synapse.matches_query(query_keywords):
                        candidates.append(synapse)
                        
        if not candidates:
            return None
            
        # Return highest confidence candidate
        best_match = max(candidates, key=lambda s: s.avg_confidence)
        best_match.usage_count += 1
        best_match.last_used = datetime.now().isoformat()
        self._save_synapses()  # Save updated usage stats
        
        print(f"[CompiledLogicIndex] INSTINCT MODE: Found synapse {best_match.synapse_id} (confidence: {best_match.avg_confidence:.1f}%)")
        return best_match
        
    def get_fragments_for_synapse(self, synapse: Synapse, fragment_library) -> List[Dict[str, Any]]:
        """
        Retrieve actual fragment objects for a synapse's fragment chain.
        
        Returns list of fragment dictionaries ready for assembly.
        """
        fragments = []
        
        for frag_id in synapse.fragment_chain:
            # Use correct method name: get_fragment (not get_fragment_by_id)
            fragment = fragment_library.get_fragment(frag_id)
            if fragment:
                # Convert Fragment object to dict if needed
                if hasattr(fragment, 'to_dict'):
                    frag_dict = fragment.to_dict()
                elif hasattr(fragment, '__dict__'):
                    frag_dict = vars(fragment)
                else:
                    frag_dict = fragment
                    
                # Add synapse metadata
                frag_dict['from_synapse'] = True
                frag_dict['synapse_id'] = synapse.synapse_id
                frag_dict['instinct_mode'] = True
                
                fragments.append(frag_dict)
            else:
                print(f"[CompiledLogicIndex] Warning: Fragment {frag_id} not found in library")
                
        return fragments
        
    def create_synapse_from_result(self, query: str, fragments: List[Dict[str, Any]], 
                                   confidence: float, min_confidence_threshold: float = 0.85) -> Optional[Synapse]:
        """
        Create a new synapse from a successful Monte Carlo result.
        
        Called after a high-confidence answer is generated to compile
        the successful fragment combination for future instant retrieval.
        """
        if confidence < min_confidence_threshold * 100:
            return None  # Not confident enough to compile
            
        if len(fragments) < 2:
            return None  # Need at least 2 fragments to form a chain
            
        # Extract fragment IDs
        fragment_ids = []
        for frag in fragments:
            frag_id = frag.get('fragment_id') or frag.get('id')
            if frag_id:
                fragment_ids.append(frag_id)
                
        if len(fragment_ids) < 2:
            return None
            
        # Generate synapse ID
        synapse_hash = hashlib.md5('_'.join(sorted(fragment_ids)).encode()).hexdigest()[:8]
        synapse_id = f"synapse_{synapse_hash}"
        
        # Extract trigger keywords from query
        from openeyes.night_mode import ConsolidationEngine
        engine = ConsolidationEngine()
        trigger_keywords = engine._extract_keywords(query)[:5]  # Top 5 keywords
        
        # Create synapse
        synapse = Synapse(
            synapse_id=synapse_id,
            fragment_chain=fragment_ids,
            trigger_keywords=trigger_keywords,
            avg_confidence=confidence,
            metadata={
                'source': 'monte_carlo_compilation',
                'original_query_length': len(query),
                'fragment_count': len(fragment_ids)
            }
        )
        
        self.add_synapse(synapse)
        print(f"[CompiledLogicIndex] Created new synapse from high-confidence result: {synapse_id}")
        return synapse
        
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the compiled logic index."""
        if not self.synapses:
            return {
                'total_synapses': 0,
                'total_usage': 0,
                'avg_confidence': 0,
                'avg_chain_length': 0
            }
            
        total_usage = sum(s.usage_count for s in self.synapses.values())
        avg_confidence = sum(s.avg_confidence for s in self.synapses.values()) / len(self.synapses)
        avg_chain_length = sum(len(s.fragment_chain) for s in self.synapses.values()) / len(self.synapses)
        
        return {
            'total_synapses': len(self.synapses),
            'total_usage': total_usage,
            'avg_confidence': round(avg_confidence, 2),
            'avg_chain_length': round(avg_chain_length, 2),
            'most_used_synapse': max(self.synapses.values(), key=lambda s: s.usage_count).synapse_id if self.synapses else None
        }


def initialize_compiled_logic_index(storage_path: str = "/workspace/openeyes/data/compiled_logic.json") -> CompiledLogicIndex:
    """Initialize and return the Compiled Logic Index singleton."""
    return CompiledLogicIndex(storage_path=storage_path)
