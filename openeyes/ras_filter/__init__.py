"""
Phase 3: The "RAS" Filter (Retrieving What Matters)

Mimics the Reticular Activating System in the human brain.
Dynamically reweights the Semantic Index based on successful verification history.
The system learns to "pay attention" to high-value fragments and topics.
"""

import json
import os
from typing import Dict, List, Tuple
from collections import defaultdict


class RASFilter:
    """
    Reticular Activating System Filter for OpenEyes.
    
    Dynamically adjusts fragment relevance scores based on:
    1. Success frequency (how often a fragment leads to high-confidence answers)
    2. Domain importance (user-defined or auto-detected priority domains)
    3. Recency of successful use
    4. Co-occurrence patterns (fragments that succeed together)
    """
    
    def __init__(self, ras_state_path: str = None):
        # Dynamic path resolution if not provided
        if ras_state_path is None:
            import openeyes
            package_dir = Path(openeyes.__file__).parent
            ras_state_path = str(package_dir.parent / "data" / "ras_state.json")
        
        self.ras_state_path = ras_state_path
        self.state = self._load_state()
        
    def _load_state(self) -> Dict:
        """Load RAS state from disk or initialize defaults."""
        if os.path.exists(self.ras_state_path):
            with open(self.ras_state_path, 'r') as f:
                return json.load(f)
        
        # Initialize default state
        return {
            "fragment_weights": {},  # fragment_id -> weight (0.0 to 2.0)
            "domain_priorities": {},  # domain -> priority multiplier
            "co_occurrence_matrix": {},  # (frag_a, frag_b) -> strength
            "success_history": [],  # Recent success events
            "last_updated": None
        }
    
    def _save_state(self):
        """Persist RAS state to disk."""
        os.makedirs(os.path.dirname(self.ras_state_path), exist_ok=True)
        with open(self.ras_state_path, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def record_success(self, fragment_ids: List[str], domain: str, confidence: float):
        """
        Record a successful query outcome.
        
        Args:
            fragment_ids: List of fragment IDs that contributed to the answer
            domain: The domain of the query (medical, engineering, etc.)
            confidence: The confidence score of the successful answer
        """
        # Boost weights for all contributing fragments
        boost_factor = confidence / 100.0  # Normalize to 0-1
        
        for frag_id in fragment_ids:
            current_weight = self.state["fragment_weights"].get(frag_id, 1.0)
            # Exponential moving average: new = old * 0.9 + boost * 0.1
            new_weight = current_weight * 0.9 + (1.0 + boost_factor) * 0.1
            # Clamp between 0.5 and 2.0
            new_weight = max(0.5, min(2.0, new_weight))
            self.state["fragment_weights"][frag_id] = new_weight
        
        # Update co-occurrence matrix
        for i, frag_a in enumerate(fragment_ids):
            for frag_b in fragment_ids[i+1:]:
                key = tuple(sorted([frag_a, frag_b]))
                key_str = f"{key[0]}|{key[1]}"
                current_strength = self.state["co_occurrence_matrix"].get(key_str, 0.0)
                new_strength = current_strength * 0.9 + boost_factor * 0.1
                self.state["co_occurrence_matrix"][key_str] = new_strength
        
        # Update domain priority
        current_domain_priority = self.state["domain_priorities"].get(domain, 1.0)
        self.state["domain_priorities"][domain] = current_domain_priority * 0.95 + 1.05 * 0.05
        
        # Add to success history (keep last 1000)
        self.state["success_history"].append({
            "fragment_ids": fragment_ids,
            "domain": domain,
            "confidence": confidence
        })
        if len(self.state["success_history"]) > 1000:
            self.state["success_history"] = self.state["success_history"][-1000:]
        
        self.state["last_updated"] = "now"
        self._save_state()
    
    def get_adjusted_relevance(self, fragment_id: str, base_score: float) -> float:
        """
        Get the RAS-adjusted relevance score for a fragment.
        
        Args:
            fragment_id: The fragment ID to adjust
            base_score: The original relevance score from semantic index
            
        Returns:
            Adjusted score incorporating RAS learning
        """
        weight = self.state["fragment_weights"].get(fragment_id, 1.0)
        return base_score * weight
    
    def get_co_occurrence_bonus(self, fragment_id: str, existing_fragments: List[str]) -> float:
        """
        Get bonus score if this fragment frequently succeeds with existing fragments.
        
        Args:
            fragment_id: Candidate fragment
            existing_fragments: Fragments already selected for this query
            
        Returns:
            Bonus multiplier (1.0 = no bonus, >1.0 = strong co-occurrence)
        """
        total_bonus = 0.0
        count = 0
        
        for existing in existing_fragments:
            key = tuple(sorted([fragment_id, existing]))
            key_str = f"{key[0]}|{key[1]}"
            strength = self.state["co_occurrence_matrix"].get(key_str, 0.0)
            if strength > 0.1:  # Only consider meaningful co-occurrences
                total_bonus += strength
                count += 1
        
        if count == 0:
            return 1.0
        
        return 1.0 + (total_bonus / count) * 0.5  # Max 50% bonus
    
    def get_domain_priority(self, domain: str) -> float:
        """Get the priority multiplier for a domain."""
        return self.state["domain_priorities"].get(domain, 1.0)
    
    def analyze_attention_patterns(self) -> Dict:
        """
        Analyze what the system has learned to pay attention to.
        
        Returns:
            Dictionary with attention insights
        """
        # Find highest-weighted fragments
        top_fragments = sorted(
            self.state["fragment_weights"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Find strongest co-occurrences
        top_co_occurrences = sorted(
            self.state["co_occurrence_matrix"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Calculate domain priorities
        domain_priorities = sorted(
            self.state["domain_priorities"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "top_fragments": top_fragments,
            "top_co_occurrences": top_co_occurrences,
            "domain_priorities": domain_priorities,
            "total_successes_recorded": len(self.state["success_history"])
        }
    
    def reset_learning(self):
        """Reset all RAS learning (useful for testing)."""
        self.state = {
            "fragment_weights": {},
            "domain_priorities": {},
            "co_occurrence_matrix": {},
            "success_history": [],
            "last_updated": None
        }
        self._save_state()


# Integration helper for Dice Table assembler
def apply_ras_filter(candidates: List[Dict], ras_filter: RASFilter, domain: str) -> List[Dict]:
    """
    Apply RAS filtering to candidate fragments.
    
    Args:
        candidates: List of FragmentCandidate dicts
        ras_filter: RASFilter instance
        domain: Query domain
        
    Returns:
        Filtered and re-sorted candidate list
    """
    adjusted_candidates = []
    
    for candidate in candidates:
        frag_id = candidate.get('fragment_id')
        base_score = candidate.get('score', 50.0)
        
        # Apply RAS adjustment
        adjusted_score = ras_filter.get_adjusted_relevance(frag_id, base_score)
        
        # Apply domain priority
        domain_mult = ras_filter.get_domain_priority(domain)
        adjusted_score *= domain_mult
        
        candidate['ras_adjusted_score'] = adjusted_score
        adjusted_candidates.append(candidate)
    
    # Sort by RAS-adjusted score
    adjusted_candidates.sort(key=lambda x: x['ras_adjusted_score'], reverse=True)
    
    return adjusted_candidates
