"""
OpenEyes Query Interface — Day Mode Entry Point

The user-facing API for OpenEyes. Receives queries, routes them through
the full engine (Swarm → Monte Carlo → Philosophy Guard → Dice Table),
and returns final output or HALT.

Target interface:
    from openeyes.query_interface import OpenEyes
    
    oe = OpenEyes(domain="medical")
    result = oe.query("What is the safest antibiotic for a penicillin-allergic patient with a UTI?")
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import uuid
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openeyes.fragment_library import FragmentLibrary, get_library
from openeyes.swarm import Swarm, FragmentCandidate
from openeyes.dice_table import DiceTable, WurfelspielAssembler, AssembledOutput
from openeyes.domain_rules import get_domain_rules, DomainRulesLoader

# Import shared_core modules
from shared_core.monte_carlo_engine import monte_carlo_evolve, evaluate_composition
from shared_core.philosophy_guard import PhilosophyGuard
from shared_core.survival_and_weights import survives_mc, load_gene_pool, save_gene_pool
from shared_core.obsidian_connector import ObsidianReporter


# Alias for compatibility
ObsidianConnector = ObsidianReporter


@dataclass
class QueryResult:
    """Result of a query execution."""
    answer: Optional[str]
    confidence: float
    fragments_used: List[Dict[str, Any]]
    philosophy_checks_passed: List[str]
    trace_id: str
    halt: bool
    halt_reason: Optional[str] = None
    recommendation: Optional[str] = None
    confidence_note: Optional[str] = None
    decomposition: Optional[Dict[str, Any]] = None
    processing_time_ms: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "answer": self.answer,
            "confidence": self.confidence,
            "fragments_used": self.fragments_used,
            "philosophy_checks_passed": self.philosophy_checks_passed,
            "trace_id": self.trace_id,
            "halt": self.halt,
            "processing_time_ms": self.processing_time_ms
        }
        if self.halt_reason:
            result["halt_reason"] = self.halt_reason
        if self.recommendation:
            result["recommendation"] = self.recommendation
        if self.confidence_note:
            result["confidence_note"] = self.confidence_note
        if self.decomposition:
            result["decomposition"] = self.decomposition
        return result


class OpenEyes:
    """
    OpenEyes query engine — Day Mode entry point.
    
    Routes user queries through the complete engine:
    1. Swarm: Decompose and retrieve candidates
    2. Monte Carlo: Evaluate and filter survivors
    3. Philosophy Guard: Hard veto on domain rules
    4. Dice Table: Select and assemble output
    
    Returns traceable answers or HALT with reason.
    """
    
    VALID_DOMAINS = ["medical", "legal", "engineering", "ethics", "general"]
    
    # Monte Carlo thresholds (from spec Section 5.1)
    MC_SCORE_THRESHOLD = 60
    MC_VARIANCE_THRESHOLD = 500
    MC_SURVIVAL_PROB_THRESHOLD = 0.4
    
    def __init__(
        self,
        domain: str = "general",
        fragment_library: Optional[FragmentLibrary] = None,
        internet_access: bool = False,
        obsidian_vault_path: Optional[Path] = None
    ):
        """
        Initialize OpenEyes engine.
        
        Args:
            domain: Domain for this session (e.g., "medical", "legal")
            fragment_library: Optional custom fragment library
            internet_access: Allow web searches (default False)
            obsidian_vault_path: Path to Obsidian vault for audit trail
        """
        if domain not in self.VALID_DOMAINS:
            raise ValueError(
                f"Invalid domain: {domain}. Must be one of: {self.VALID_DOMAINS}"
            )
        
        self.domain = domain
        self.internet_access = internet_access
        
        # Initialize fragment library
        self.library = fragment_library or get_library()
        
        # Initialize Swarm
        self.swarm = Swarm(
            fragment_library=self.library,
            internet_access=internet_access
        )
        
        # Initialize Dice Table and Assembler
        self.dice_table = DiceTable()
        self.assembler = WurfelspielAssembler(dice_table=self.dice_table)
        
        # Initialize Philosophy Guard with domain rules
        guard_config_path = Path(f"openeyes/domain_rules/{domain}.json")
        if guard_config_path.exists():
            self.guard = PhilosophyGuard(rules_config=str(guard_config_path))
        else:
            # Fall back to default E-AR rules if domain file doesn't exist
            print(f"[OpenEyes] Warning: Domain rules not found for '{domain}', using defaults")
            self.guard = PhilosophyGuard()
        
        # Initialize Obsidian connector
        self.obsidian = ObsidianConnector(vault_path=obsidian_vault_path)
        
        # Load gene pool
        self.gene_pool = load_gene_pool()
    
    def query(self, query_text: str) -> QueryResult:
        """
        Execute a user query through the full engine.
        
        Args:
            query_text: The user's question
            
        Returns:
            QueryResult with answer or HALT
        """
        import time
        start_time = time.time()
        
        # Generate trace ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_id = f"oe_{timestamp}_{uuid.uuid4().hex[:4]}"
        
        try:
            # Step 1: Decompose query via Swarm
            decomposition = self.swarm.get_decomposition(query_text)
            
            # Step 2: Retrieve candidate fragments
            candidates = self.swarm.decompose_and_retrieve(query_text, self.domain)
            
            if not candidates:
                return QueryResult(
                    answer=None,
                    confidence=0.0,
                    fragments_used=[],
                    philosophy_checks_passed=[],
                    trace_id=trace_id,
                    halt=True,
                    halt_reason="No candidate fragments found for this query.",
                    recommendation="Try reformulating your query or check if the domain has sufficient coverage.",
                    decomposition=decomposition,
                    processing_time_ms=(time.time() - start_time) * 1000
                )
            
            # Step 3: Run Monte Carlo evaluation on candidates
            survivors = self._run_monte_carlo(candidates)
            
            if not survivors:
                return QueryResult(
                    answer=None,
                    confidence=0.0,
                    fragments_used=[],
                    philosophy_checks_passed=[],
                    trace_id=trace_id,
                    halt=True,
                    halt_reason="No fragments survived Monte Carlo evaluation.",
                    recommendation="Insufficient confidence in available information. Consult a specialist.",
                    decomposition=decomposition,
                    processing_time_ms=(time.time() - start_time) * 1000
                )
            
            # Step 4: Apply Philosophy Guard to survivors
            cleared_fragments = self._apply_philosophy_guard(survivors)
            
            if not cleared_fragments:
                rejected_rules = self.guard.last_rejected_rules if hasattr(self.guard, 'last_rejected_rules') else []
                return QueryResult(
                    answer=None,
                    confidence=0.0,
                    fragments_used=[],
                    philosophy_checks_passed=[],
                    trace_id=trace_id,
                    halt=True,
                    halt_reason=f"Philosophy Guard veto: {rejected_rules}",
                    recommendation="No fragments passed domain-specific safety checks.",
                    decomposition=decomposition,
                    processing_time_ms=(time.time() - start_time) * 1000
                )
            
            # Step 5: Assemble output via Dice Table
            assembled = self.assembler.assemble(
                survivors=cleared_fragments,
                domain=self.domain,
                philosophy=self._get_domain_philosophy(),
                trace_id=trace_id
            )
            
            # Replace placeholder in answer
            if assembled.answer:
                assembled.answer = assembled.answer.replace(
                    "{trace_id_placeholder}", trace_id
                )
            
            # Step 6: Final Philosophy Guard check on assembled output
            if not assembled.halt:
                assembly_check = self.guard.validate_proposal({
                    "content": assembled.answer,
                    "fragments": assembled.fragments_used
                })
                
                if not assembly_check.get("passed", True):
                    return QueryResult(
                        answer=None,
                        confidence=assembled.confidence,
                        fragments_used=assembled.fragments_used,
                        philosophy_checks_passed=[],
                        trace_id=trace_id,
                        halt=True,
                        halt_reason=f"Assembly failed philosophy check: {assembly_check.get('rejected_by', [])}",
                        recommendation="Assembled answer violates domain rules.",
                        decomposition=decomposition,
                        processing_time_ms=(time.time() - start_time) * 1000
                    )
            
            # Step 7: Log to Obsidian
            self._log_to_obsidian(trace_id, query_text, assembled, decomposition)
            
            # Step 8: Update gene pool weights
            self._update_gene_pool(cleared_fragments, assembled.halt)
            
            return QueryResult(
                answer=assembled.answer,
                confidence=assembled.confidence,
                fragments_used=assembled.fragments_used,
                philosophy_checks_passed=assembled.philosophy_checks_passed,
                trace_id=trace_id,
                halt=assembled.halt,
                halt_reason=assembled.halt_reason,
                recommendation=assembled.recommendation,
                confidence_note=assembled.confidence_note,
                decomposition=decomposition,
                processing_time_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            # Unexpected error
            return QueryResult(
                answer=None,
                confidence=0.0,
                fragments_used=[],
                philosophy_checks_passed=[],
                trace_id=trace_id,
                halt=True,
                halt_reason=f"System error: {str(e)}",
                recommendation="Please report this error to system administrators.",
                processing_time_ms=(time.time() - start_time) * 1000
            )
    
    def _run_monte_carlo(self, candidates: List[FragmentCandidate]) -> List[Dict[str, Any]]:
        """
        Run Monte Carlo evaluation on candidates.
        
        Returns list of survivor fragments with scores.
        """
        survivors = []
        
        for candidate in candidates:
            # Create a "composition" from the candidate (single fragment)
            composition = {
                "fragments": [candidate.to_dict()],
                "content": candidate.content
            }
            
            # Evaluate composition
            eval_result = evaluate_composition(composition)
            
            # Check survival criteria (use attribute access, not dict syntax)
            survival_result = survives_mc(
                score=eval_result.mean_score,
                selected=[candidate.to_dict()],  # Pass list of dicts, not bool
                variance=eval_result.variance,
                survival_probability=eval_result.survival_probability,
                aggregate_stats={},
                score_threshold=self.MC_SCORE_THRESHOLD,
                variance_threshold=self.MC_VARIANCE_THRESHOLD,
                survival_prob_threshold=self.MC_SURVIVAL_PROB_THRESHOLD
            )
            
            if survival_result["passed"]:
                # This fragment survived
                survivor_data = candidate.to_dict()
                survivor_data["score"] = eval_result.mean_score
                survivor_data["variance"] = eval_result.variance
                survivor_data["survival_probability"] = eval_result.survival_probability
                survivor_data["tags"] = candidate.domain_tags
                
                survivors.append(survivor_data)
        
        return survivors
    
    def _apply_philosophy_guard(self, survivors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply Philosophy Guard to survivor fragments.
        
        Returns list of fragments that pass domain rules.
        """
        cleared = []
        
        for frag in survivors:
            # Validate fragment against domain rules
            result = self.guard.validate_proposal(frag)
            
            if result.get("passed", False):
                cleared.append(frag)
        
        return cleared
    
    def _get_domain_philosophy(self) -> str:
        """Get the philosophy alignment for the current domain."""
        philosophy_map = {
            "medical": "do_no_harm",
            "legal": "jurisdiction_consistency",
            "engineering": "safety_first",
            "ethics": "principle_alignment",
            "general": "evidence_based"
        }
        return philosophy_map.get(self.domain, "evidence_based")
    
    def _log_to_obsidian(
        self,
        trace_id: str,
        query: str,
        assembled: AssembledOutput,
        decomposition: Dict[str, Any]
    ):
        """Log query result to Obsidian vault."""
        if not self.obsidian.vault_path:
            return
        
        log_entry = {
            "trace_id": trace_id,
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "query": query,
            "decomposition": decomposition,
            "result": {
                "answer": assembled.answer,
                "confidence": assembled.confidence,
                "halt": assembled.halt,
                "halt_reason": assembled.halt_reason,
                "fragments_used": assembled.fragments_used
            }
        }
        
        self.obsidian.log_query(log_entry)
    
    def _update_gene_pool(self, fragments: List[Dict[str, Any]], halted: bool):
        """Update gene pool weights based on query outcome."""
        # Simplified weight update
        # In production, this would use full survival_and_weights logic
        
        for frag in fragments:
            fragment_id = frag.get("fragment_id")
            if not fragment_id:
                continue
            
            # Get current weight - handle both dict and float values
            current_entry = self.gene_pool.get(fragment_id, 1.0)
            if isinstance(current_entry, dict):
                current_weight = current_entry.get("weight", 1.0)
            else:
                current_weight = current_entry
            
            # Adjust based on outcome
            if halted:
                # Fragments were cleared but assembly halted - small penalty
                new_weight = max(0.1, current_weight - 0.01)
            else:
                # Successful answer - small bonus
                new_weight = min(2.0, current_weight + 0.02)
            
            self.gene_pool[fragment_id] = new_weight
        
        # Save updated gene pool
        save_gene_pool(self.gene_pool)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            "domain": self.domain,
            "fragment_library_stats": self.library.get_statistics(),
            "gene_pool_size": len(self.gene_pool),
            "available_domains": self.VALID_DOMAINS
        }


# Convenience function for quick usage
def quick_query(query_text: str, domain: str = "general") -> QueryResult:
    """
    Quick one-off query without manual engine setup.
    
    Args:
        query_text: The user's question
        domain: Domain category
        
    Returns:
        QueryResult
    """
    engine = OpenEyes(domain=domain)
    return engine.query(query_text)
