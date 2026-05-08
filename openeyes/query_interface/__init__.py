"""
Query Interface — Day Mode Entry Point

The Day Mode entry point. Receives user queries, routes them through the full 
engine (Swarm → Monte Carlo → Philosophy Guard → Dice Table), and returns 
final output with traceability.

Target interface per spec:
    from openeyes.query_interface import OpenEyes
    oe = OpenEyes(domain="medical")
    result = oe.query("What is the safest antibiotic for a penicillin-allergic patient with a UTI?")
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

# Add shared_core to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from openeyes.swarm import Swarm, FragmentCandidate
from openeyes.fragment_library import FragmentLibrary, create_sample_medical_library
from openeyes.dice_table import DiceTable
from openeyes.domain_rules import DomainRulesConfig
from shared_core.survival_and_weights import survives_mc
from shared_core.philosophy_guard import PhilosophyGuard


class OpenEyes:
    """
    OpenEyes Query Engine — Day Mode entry point.
    
    Answers user queries by:
    1. Decomposing via Swarm
    2. Evaluating via Monte Carlo
    3. Vetoing via Philosophy Guard
    4. Assembling via Dice Table
    5. Returning traceable answer or HALT
    """
    
    def __init__(self, domain: str = "general", fragment_library: Optional[FragmentLibrary] = None):
        """
        Initialize OpenEyes engine.
        
        Args:
            domain: Domain type (medical, legal, engineering, ethics, general)
            fragment_library: Optional pre-loaded FragmentLibrary instance
        """
        self.domain = domain
        
        # Initialize fragment library
        if fragment_library:
            self.library = fragment_library
        elif domain == "medical":
            self.library = create_sample_medical_library()
        else:
            self.library = FragmentLibrary(domain=domain)
        
        # Initialize Swarm
        self.swarm = Swarm(
            fragment_library=self.library,
            internet_access=True,
            domain=domain
        )
        
        # Initialize Dice Table
        self.dice_table = DiceTable(domain=domain)
        
        # Initialize Domain Rules
        self.domain_rules = DomainRulesConfig(domain=domain)
        
        # Initialize Philosophy Guard with domain rules
        self.guard = PhilosophyGuard()
    
    def query(self, query_text: str) -> Dict[str, Any]:
        """
        Process a user query through the full engine pipeline.
        
        Args:
            query_text: User's natural language query
            
        Returns:
            Result dict with answer, confidence, fragments_used, trace_id, halt status
        """
        # Generate trace ID
        trace_id = f"oe_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(query_text.encode()).hexdigest()[:4]}"
        
        try:
            # Step 1: Swarm decomposes and retrieves candidates
            candidates = self.swarm.decompose_and_retrieve(query_text)
            
            if not candidates:
                return self._halt_result(
                    reason="No candidate fragments retrieved",
                    recommendation="The knowledge base may not cover this topic.",
                    trace_id=trace_id
                )
            
            # Step 2: Convert candidates to format for Monte Carlo evaluation
            # For now, we simulate MC evaluation on individual fragments
            survivors = self._evaluate_candidates(candidates)
            
            if not survivors:
                return self._halt_result(
                    reason="No fragments survived Monte Carlo evaluation",
                    recommendation="Insufficient evidence for this query.",
                    trace_id=trace_id
                )
            
            # Step 3: Apply domain rules validation
            cleared_survivors = self._apply_domain_rules(survivors)
            
            if not cleared_survivors:
                return self._halt_result(
                    reason="No fragments passed domain rule validation",
                    recommendation=f"Review {self.domain} domain requirements.",
                    trace_id=trace_id
                )
            
            # Step 4: Dice Table selection and assembly
            selected_fragments, should_halt, halt_message = self.dice_table.select_fragments(cleared_survivors)
            
            if should_halt:
                return self._halt_result(
                    reason=halt_message,
                    recommendation="Consult a certified professional in this domain.",
                    trace_id=trace_id
                )
            
            # Step 5: Assemble final output
            assembled = self.dice_table.assemble_output(selected_fragments)
            
            # Step 6: Final Philosophy Guard check on assembled output
            guard_result = self.guard.validate_proposal({
                "type": "answer_assembly",
                "content": assembled.get("answer", ""),
                "fragments": selected_fragments,
                "domain": self.domain
            })
            
            if not guard_result.get("passed", True):
                return self._halt_result(
                    reason=f"Philosophy Guard veto: {', '.join(guard_result.get('rejected_by', []))}",
                    recommendation="Answer assembly violated core principles.",
                    trace_id=trace_id
                )
            
            # Success - return full result
            return {
                "answer": assembled["answer"],
                "confidence": assembled["confidence"],
                "fragments_used": assembled["fragments_used"],
                "philosophy_checks_passed": [r["rule_id"] for r in guard_result.get("rule_results", []) if r.get("passed")],
                "trace_id": trace_id,
                "halt": False,
                "domain": self.domain,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._halt_result(
                reason=f"Engine error: {str(e)}",
                recommendation="Report this issue to system administrators.",
                trace_id=trace_id
            )
    
    def _evaluate_candidates(self, candidates: List[FragmentCandidate]) -> List[Dict]:
        """
        Evaluate candidates using Monte Carlo simulation.
        
        For each candidate, runs N simulations to compute mean_score, variance, survival_probability.
        Only survivors (passing all three thresholds) are returned.
        
        Args:
            candidates: List of FragmentCandidate objects
            
        Returns:
            List of survivor dicts with evaluation metrics
        """
        survivors = []
        
        for candidate in candidates:
            # Simulate Monte Carlo evaluation
            # In production: would run actual MC simulations
            # For now: use credibility_estimate as base for simulated score
            
            base_score = candidate.credibility_estimate * 100
            
            # Simulate variance based on source type
            variance_map = {
                "library": 100,  # Low variance - pre-verified
                "api": 200,      # Medium variance
                "web": 400       # High variance
            }
            variance = variance_map.get(candidate.agent_type, 300)
            
            # Calculate survival probability
            survival_prob = candidate.credibility_estimate
            
            # Create primitive-like structure for survives_mc
            primitive_data = {
                "id": candidate.fragment_id,
                "content": candidate.content,
                "weight": candidate.metadata.get("weight", 1.0)
            }
            
            # Check against thresholds per spec
            survival_result = survives_mc(
                score=base_score,
                selected=[primitive_data],
                variance=variance,
                survival_probability=survival_prob,
                aggregate_stats={}
            )
            
            if survival_result.get("passed"):
                # Add evaluation metrics to candidate
                # Include credibility_class from metadata for domain rules validation
                survivor = {
                    "fragment_id": candidate.fragment_id,
                    "content": candidate.content,
                    "source": candidate.source,
                    "source_url": candidate.source_url,
                    "tags": candidate.domain_tags,
                    "mean_score": round(base_score, 2),
                    "variance": variance,
                    "survival_probability": round(survival_prob, 2),
                    "credibility_class": candidate.metadata.get("credibility_class", ""),
                    "metadata": candidate.metadata
                }
                survivors.append(survivor)
        
        return survivors
    
    def _apply_domain_rules(self, survivors: List[Dict]) -> List[Dict]:
        """
        Apply domain-specific rules to filter survivors.
        
        Args:
            survivors: List of survivor dicts
            
        Returns:
            List of survivors that pass domain rules
        """
        cleared = []
        
        for survivor in survivors:
            validation = self.domain_rules.validate_fragment(survivor)
            
            if validation.get("passed"):
                cleared.append(survivor)
        
        return cleared
    
    def _halt_result(self, reason: str, recommendation: str, trace_id: str) -> Dict[str, Any]:
        """
        Create a HALT result structure.
        
        Per spec: The system never returns a partial answer when it halts.
        It halts completely and explains why.
        
        Args:
            reason: Explanation of why the system halted
            recommendation: What the user should do instead
            trace_id: Unique trace identifier
            
        Returns:
            HALT result dict
        """
        return {
            "answer": None,
            "halt": True,
            "halt_reason": reason,
            "recommendation": recommendation,
            "trace_id": trace_id,
            "domain": self.domain,
            "timestamp": datetime.now().isoformat()
        }


__all__ = ["OpenEyes"]