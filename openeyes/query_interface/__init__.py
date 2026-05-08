"""
OpenEyes Query Interface — Day Mode Entry Point

Receives user queries, routes through the full engine:
1. Swarm decomposition and retrieval
2. Monte Carlo evaluation with domain-tier thresholds
3. Philosophy Guard validation
4. Dice Table assembly
5. Output with traceability

Returns verified answer or HALT with reason.
"""

import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from openeyes.fragment_library import FragmentLibrary
from openeyes.swarm import Swarm, FragmentCandidate, create_api_connectors
from openeyes.dice_table import WurfelspielAssembler, DiceTable
from openeyes.domain_rules import get_domain_rules, get_domain_tier, DomainRulesLoader

from shared_core.monte_carlo_engine import (
    monte_carlo_evolve, 
    evaluate_composition, 
    DEFAULT_THRESHOLDS
)
from shared_core.survival_and_weights import survives_mc, load_gene_pool, save_gene_pool
from shared_core.philosophy_guard import PhilosophyGuard
from shared_core.obsidian_connector import ObsidianReporter as ObsidianConnector


class OpenEyes:
    """
    Main OpenEyes query interface.
    
    Usage:
        oe = OpenEyes(domain="medical")
        result = oe.query("What is the safest antibiotic for a penicillin-allergic patient with a UTI?")
    """
    
    def __init__(self, domain: str = "general", 
                 fragment_library_path: str = "openeyes/fragment_library/fragments.json",
                 api_config: Optional[Dict[str, str]] = None,
                 obsidian_vault_path: Optional[str] = None):
        
        self.domain = domain.lower()
        self.domain_tier = get_domain_tier(self.domain)
        
        # Load domain rules
        self.rules_config = get_domain_rules(self.domain)
        
        # Initialize fragment library
        self.library = FragmentLibrary(storage_path=fragment_library_path)
        
        # Initialize API connectors if config provided
        self.api_connectors = create_api_connectors(api_config or {})
        
        # Initialize Swarm
        self.swarm = Swarm(
            fragment_library=self.library,
            internet_access=bool(api_config),
            api_configs=api_config or {}
        )
        
        # Initialize Philosophy Guard with domain rules
        self.guard = PhilosophyGuard()
        self.guard.rules = self.rules_config.get("rules", [])
        
        # Initialize Dice Table and Assembler
        self.dice_table = DiceTable()
        self.assembler = WurfelspielAssembler(self.dice_table)
        
        # Initialize Obsidian connector (optional)
        self.obsidian = None
        if obsidian_vault_path:
            self.obsidian = ObsidianConnector(vault_path=obsidian_vault_path)
        
        # Load gene pool
        self.gene_pool = load_gene_pool()
        
        print(f"[OpenEyes] Initialized for domain '{self.domain}' (Tier {self.domain_tier[-1]})")
        print(f"✓ Loaded {len(self.rules_config.get('rules', []))} domain rules")
        print(f"✓ Fragment library: {len(self.library._fragments)} fragments")
    
    def query(self, query_text: str) -> Dict[str, Any]:
        """
        Process a user query through the full OpenEyes pipeline.
        
        Returns dict with:
        - answer: str or None (if halted)
        - confidence: float (0-100)
        - halt: bool
        - halt_reason: str (if halted)
        - fragments_used: list
        - philosophy_checks_passed: list
        - trace_id: str
        """
        start_time = time.time()
        trace_id = self._generate_trace_id()
        
        print(f"\n{'='*60}")
        print(f"QUERY: {query_text}")
        print(f"Domain: {self.domain} | Tier: {self.domain_tier}")
        print(f"Trace ID: {trace_id}")
        print(f"{'='*60}\n")
        
        result = {
            "trace_id": trace_id,
            "domain": self.domain,
            "tier": self.domain_tier,
            "query": query_text,
            "answer": None,
            "confidence": 0.0,
            "halt": False,
            "halt_reason": None,
            "fragments_used": [],
            "philosophy_checks_passed": [],
            "processing_time_ms": 0
        }
        
        try:
            # Step 1: Swarm decomposition and retrieval
            candidates = self._run_swarm(query_text)
            
            if not candidates:
                result["halt"] = True
                result["halt_reason"] = "No candidate fragments found for this query."
                print(f"\n[HALT] {result['halt_reason']}")
                return self._finalize_result(result, start_time, trace_id)
            
            print(f"\n[Step 1 Complete] Retrieved {len(candidates)} candidate fragments")
            
            # Step 2: Monte Carlo evaluation
            survivors = self._run_monte_carlo(candidates)
            
            if not survivors:
                result["halt"] = True
                result["halt_reason"] = "No fragments survived Monte Carlo evaluation."
                print(f"\n[HALT] {result['halt_reason']}")
                return self._finalize_result(result, start_time, trace_id)
            
            print(f"\n[Step 2 Complete] {len(survivors)} fragments survived Monte Carlo")
            
            # Step 3: Philosophy Guard validation
            cleared_fragments = self._run_philosophy_guard(survivors)
            
            if not cleared_fragments:
                result["halt"] = True
                result["halt_reason"] = "No fragments passed Philosophy Guard validation."
                print(f"\n[HALT] {result['halt_reason']}")
                return self._finalize_result(result, start_time, trace_id)
            
            print(f"\n[Step 3 Complete] {len(cleared_fragments)} fragments cleared Philosophy Guard")
            
            # Step 4: Dice Table assembly
            assembled_output = self._assemble_answer(cleared_fragments, query_text)
            
            if assembled_output.get("halt"):
                result["halt"] = True
                result["halt_reason"] = assembled_output.get("halt_reason", "Assembly failed.")
                print(f"\n[HALT] {result['halt_reason']}")
                return self._finalize_result(result, start_time, trace_id)
            
            result["answer"] = assembled_output.get("answer", "")
            result["confidence"] = assembled_output.get("confidence", 0.0)
            result["fragments_used"] = assembled_output.get("fragments_used", [])
            result["philosophy_checks_passed"] = assembled_output.get("philosophy_checks", [])
            
            print(f"\n[Step 4 Complete] Answer assembled with confidence {result['confidence']:.1f}")
            
            # Step 5: Final composition-level Philosophy Guard check
            final_check = self._final_philosophy_check(assembled_output)
            if not final_check.get("passed", True):
                result["halt"] = True
                result["halt_reason"] = f"Final validation failed: {final_check.get('reason', 'Unknown')}"
                print(f"\n[HALT] {result['halt_reason']}")
                return self._finalize_result(result, start_time, trace_id)
            
            print(f"\n[Final Check Passed]")
            
            # Success!
            print(f"\n{'='*60}")
            print(f"ANSWER: {result['answer'][:200]}..." if len(str(result['answer'])) > 200 else f"ANSWER: {result['answer']}")
            print(f"Confidence: {result['confidence']:.1f}%")
            print(f"Fragments used: {len(result['fragments_used'])}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            result["halt"] = True
            result["halt_reason"] = f"System error: {str(e)}"
            print(f"\n[ERROR] {result['halt_reason']}")
            import traceback
            traceback.print_exc()
        
        return self._finalize_result(result, start_time, trace_id)
    
    def _run_swarm(self, query_text: str) -> List[Dict[str, Any]]:
        """Run Swarm decomposition and retrieval."""
        candidates = self.swarm.decompose_and_retrieve(
            domain=self.domain,
            query=query_text
        )
        
        # Convert FragmentCandidate objects to dicts
        return [c.to_dict() for c in candidates]
    
    def _run_monte_carlo(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run Monte Carlo evaluation on candidates."""
        survivors = []
        
        for candidate in candidates:
            # Create single-fragment composition for evaluation
            composition = [candidate]
            
            # Evaluate composition
            eval_result = evaluate_composition(
                composition=composition,
                scenario=None,
                
            )
            
            # Check survival criteria using survives_mc
            survival_result = survives_mc(
                score=eval_result.mean_score,
                selected=[candidate],  # Pass as list
                variance=eval_result.variance,
                survival_probability=eval_result.survival_probability,
                aggregate_stats={}
            )
            
            if survival_result["passed"]:
                # Add evaluation metrics to candidate
                candidate["mc_score"] = eval_result.mean_score
                candidate["mc_variance"] = eval_result.variance
                candidate["mc_survival_prob"] = eval_result.survival_probability
                candidate["reasoning_role"] = candidate.get("reasoning_role", "unknown")
                candidate["source_type"] = candidate.get("source_type", "tertiary")
                candidate["year"] = candidate.get("year", 0)
                survivors.append(candidate)
                
                print(f"  ✓ Fragment {candidate.get('id', 'unknown')[:20]}... survived (score={eval_result.mean_score:.1f})")
            else:
                print(f"  ✗ Fragment {candidate.get('id', 'unknown')[:20]}... failed MC (score={eval_result.mean_score:.1f}, var={eval_result.variance:.1f})")
        
        return survivors
    
    def _run_philosophy_guard(self, fragments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run Philosophy Guard validation on fragments."""
        cleared = []
        
        for fragment in fragments:
            # Validate fragment against domain rules
            violations = []
            
            for rule in self.guard.rules:
                check_result = self.guard._apply_rule(rule, fragment)
                if not check_result.get("passed", True):
                    violations.append(check_result)
            
            if not violations:
                cleared.append(fragment)
                print(f"  ✓ Fragment {fragment.get('id', 'unknown')[:20]}... passed Philosophy Guard")
            else:
                print(f"  ✗ Fragment {fragment.get('id', 'unknown')[:20]}... failed: {[v.get('rule_id') for v in violations]}")
        
        return cleared
    
    def _assemble_answer(self, fragments: List[Dict[str, Any]], query_text: str) -> Dict[str, Any]:
        """Assemble final answer using Dice Table."""
        assembly = self.assembler.assemble(
            fragments=fragments,
            domain=self.domain,
            query=query_text
        )
        
        return assembly
    
    def _final_philosophy_check(self, assembled_output: Dict[str, Any]) -> Dict[str, Any]:
        """Final composition-level Philosophy Guard check."""
        # Check reasoning chain completeness for tier1/tier2
        if self.domain_tier in ["tier1", "tier2"]:
            fragments = assembled_output.get("fragments_used", [])
            
            roles_present = set(f.get("reasoning_role", "unknown") for f in fragments)
            
            # Must have at least definition
            if "definition" not in roles_present:
                return {
                    "passed": False,
                    "reason": "Missing definition fragment in reasoning chain"
                }
            
            # Tier1 must also have counter_argument
            if self.domain_tier == "tier1" and "counter_argument" not in roles_present:
                return {
                    "passed": False,
                    "reason": "Tier 1 requires counter-argument fragment"
                }
        
        return {"passed": True}
    
    def _finalize_result(self, result: Dict[str, Any], start_time: float, trace_id: str) -> Dict[str, Any]:
        """Finalize result with timing and logging."""
        result["processing_time_ms"] = (time.time() - start_time) * 1000
        
        # Log to Obsidian if configured
        if self.obsidian:
            try:
                self.obsidian.report_run(
                    run_id=trace_id,
                    proposal={"query": result["query"], "answer": result["answer"]},
                    score=result["confidence"],
                    metadata={
                        "domain": self.domain,
                        "tier": self.domain_tier,
                        "halt": result["halt"],
                        "halt_reason": result["halt_reason"],
                        "fragments_used": result["fragments_used"],
                        "processing_time_ms": result["processing_time_ms"]
                    }
                )
            except Exception as e:
                print(f"[Warning] Failed to log to Obsidian: {e}")
        
        # Update gene pool weights based on outcome
        self._update_gene_pool(result)
        
        return result
    
    def _update_gene_pool(self, result: Dict[str, Any]):
        """Update gene pool weights based on query outcome."""
        for fragment in result.get("fragments_used", []):
            fid = fragment.get("id")
            if fid and fid in self.gene_pool:
                # Boost weight for successful fragments
                current_weight = self.gene_pool[fid]
                self.gene_pool[fid] = min(2.0, current_weight + 0.02)
        
        save_gene_pool(self.gene_pool)
    
    def _generate_trace_id(self) -> str:
        """Generate unique trace ID for this query."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:4]
        return f"oe_{timestamp}_{random_suffix}"


# Convenience function
def ask(query: str, domain: str = "general") -> Dict[str, Any]:
    """Quick query function with default settings."""
    oe = OpenEyes(domain=domain)
    return oe.query(query)
