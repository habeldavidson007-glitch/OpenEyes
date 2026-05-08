"""
OpenEyes Combinatorial Game Theory Engine
Implements Sprague-Grundy theorem for fragment robustness verification.
Treats fragment validation as a two-player game: Anchor vs. Challenger.
"""

from typing import Dict, List, Set, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GameTheoryEngine:
    """
    Computes Grundy values (nim-values) for fragments.
    Grundy = 0: Undefeatable (No valid challenger exists) -> PROVEN_ROBUST
    Grundy > 0: Defeatable (Valid challengers exist) -> CHALLENGED
    """
    
    def __init__(self, library_fragments):
        # Handle both dict and Fragment object types
        self.fragments = {}
        for f in library_fragments:
            if hasattr(f, 'fragment_id'):
                # It's a Fragment object
                frag_dict = {
                    'fragment_id': f.fragment_id,
                    'reasoning_role': getattr(f, 'reasoning_role', None),
                    'tags': getattr(f, 'tags', []),
                    'credibility_class': getattr(f, 'credibility_class', 'forum_post'),
                    'year': getattr(f, 'year', 0),
                    'incompatible_with': getattr(f, 'incompatible_with', [])
                }
                self.fragments[f.fragment_id] = frag_dict
            elif hasattr(f, 'id'):
                # It's a Fragment object with 'id' field (not fragment_id)
                frag_dict = {
                    'fragment_id': f.id,
                    'reasoning_role': getattr(f, 'reasoning_role', None),
                    'tags': getattr(f, 'tags', []),
                    'credibility_class': getattr(f, 'credibility_class', 'forum_post'),
                    'year': getattr(f, 'year', 0),
                    'incompatible_with': getattr(f, 'incompatible_with', [])
                }
                self.fragments[f.id] = frag_dict
            else:
                # It's already a dict
                self.fragments[f['fragment_id']] = f
        
        self.grundy_cache: Dict[str, int] = {}
        self.challenger_pool = self._build_challenger_pool()
        
    def _build_challenger_pool(self) -> List[Dict]:
        """Extract all counter_argument fragments."""
        pool = []
        for frag in self.fragments.values():
            if frag.get('reasoning_role') == 'counter_argument':
                pool.append(frag)
        return pool
    
    def compute_all_grundy_values(self) -> Dict[str, int]:
        """Pre-compute Grundy values for all fragments in the library."""
        results = {}
        for frag_id, frag in self.fragments.items():
            # Only compute for definition/latest_data (Anchors)
            if frag.get('reasoning_role') in ['definition', 'latest_data']:
                results[frag_id] = self._compute_grundy_recursive(frag, set())
            else:
                # Challengers don't need Grundy values themselves in this model
                results[frag_id] = -1 
        self.grundy_cache.update(results)
        return results
    
    def _compute_grundy_recursive(self, anchor: Dict, visited: Set[str]) -> int:
        """
        Recursive Mex (Minimum Excludant) calculation.
        A challenger defeats an anchor if:
        1. It targets the same topic (tag overlap)
        2. It has equal or higher credibility
        3. It is more recent (or equal)
        """
        anchor_id = anchor.get('fragment_id')
        if anchor_id in visited:
            return 0  # Prevent cycles
        visited.add(anchor_id)
        
        defeating_grundy_values = []
        
        for challenger in self.challenger_pool:
            if self._challenger_defeats_anchor(challenger, anchor):
                # Recursively compute the challenger's own robustness
                g_val = self._compute_grundy_recursive(challenger, visited.copy())
                defeating_grundy_values.append(g_val)
        
        # Calculate Mex (smallest non-negative integer not in the set)
        mex = 0
        while mex in defeating_grundy_values:
            mex += 1
            
        return mex
    
    def _challenger_defeats_anchor(self, challenger: Dict, anchor: Dict) -> bool:
        """
        Determines if a challenger successfully defeats an anchor.
        Rules:
        1. Topic Overlap: Must share at least one significant tag
        2. Credibility: Challenger >= Anchor
        3. Recency: Challenger year >= Anchor year
        4. Explicit Incompatibility: If listed in incompatible_with
        """
        # 1. Check Topic Overlap
        anchor_tags = set(anchor.get('tags', []))
        challenger_tags = set(challenger.get('tags', []))
        if not anchor_tags.intersection(challenger_tags):
            return False
            
        # 2. Check Credibility Hierarchy
        cred_order = {
            'forum_post': 1, 'news_article': 2, 'textbook': 3,
            'government_source': 4, 'clinical_guideline': 5, 'peer_reviewed_study': 6
        }
        anchor_cred = cred_order.get(anchor.get('credibility_class', 'forum_post'), 0)
        chall_cred = cred_order.get(challenger.get('credibility_class', 'forum_post'), 0)
        
        if chall_cred < anchor_cred:
            return False
            
        # 3. Check Recency
        anchor_year = anchor.get('year') or 0
        chall_year = challenger.get('year') or 0
        if chall_year < anchor_year:
            return False
            
        # 4. Check Explicit Incompatibility (Optional but strong)
        # If anchor explicitly lists this challenger as incompatible, it's a direct hit
        # (Logic inverted: usually anchor lists what IT is incompatible with)
        if challenger.get('fragment_id') in anchor.get('incompatible_with', []):
            return True
            
        return True
    
    def get_grundy_value(self, fragment_id: str) -> int:
        """Retrieve pre-computed Grundy value."""
        return self.grundy_cache.get(fragment_id, -1)
    
    def get_robustness_status(self, fragment_id: str) -> str:
        """Human readable status."""
        val = self.get_grundy_value(fragment_id)
        if val == 0:
            return "PROVEN_ROBUST"
        elif val > 0:
            return f"CHALLENGED (Grundy={val})"
        else:
            return "NOT_ANCHOR"

def run_grundy_computation(library_fragments: List[Dict]) -> Dict[str, int]:
    """Convenience function to run computation."""
    engine = GameTheoryEngine(library_fragments)
    return engine.compute_all_grundy_values()
