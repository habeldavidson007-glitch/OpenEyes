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

# Import Compiled Logic Index (Instinct Layer)
from openeyes.compiled_logic import CompiledLogicIndex

# Import Query Normalizer
from openeyes.query_normalizer import canonical_form

# FIX 1 & IMPROVEMENT 1: Out-of-domain detection
OUT_OF_DOMAIN_SIGNALS = [
    'poorest country', 'richest country', 'population', 'geography',
    'history', 'politics', 'war', 'weather', 'sports', 'music',
    'movies', 'food', 'recipe', 'health', 'medicine', 'law'
]

def is_out_of_domain(query: str, domain: str) -> bool:
    """Check if query is outside finance domain."""
    q = query.lower()
    for signal in OUT_OF_DOMAIN_SIGNALS:
        if signal in q:
            return True
    return False

# FIX 2: Relevance scoring function
STOP_WORDS = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
              'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 
              'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 
              'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 
              'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 
              'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 
              'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 
              'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 
              'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or', 
              'because', 'until', 'while', 'although', 'though', 'after', 'before', 
              'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'i', 
              'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
              'my', 'your', 'his', 'its', 'our', 'their', 'mine', 'yours', 'hers', 
              'ours', 'theirs', 'myself', 'yourself', 'himself', 'herself', 'itself', 
              'ourselves', 'themselves', 'think', 'current', 'world', 'look', 'like',
              'best', 'advice', 'doing', 'stock', 'exchange', 'explain'}

def score_relevance(fragment: dict, query: str, sub_questions: list = None) -> float:
    """
    Score how relevant a fragment is to the actual query.
    Returns 0.0 to 1.0. Below 0.4 = exclude from assembly.
    
    Uses fragment tags and content to determine relevance to query keywords.
    """
    if sub_questions is None:
        sub_questions = []
    
    query_words = set(query.lower().split()) - STOP_WORDS
    frag_tags = set(fragment.get('tags', []))
    frag_content = fragment.get('content', '').lower()
    
    # Tag overlap score (40% weight)
    tag_overlap = len(query_words & frag_tags) / max(len(query_words), 1)
    
    # Content keyword score (40% weight) - check if query words appear in content
    content_hits = sum(1 for word in query_words if word in frag_content)
    content_score = content_hits / max(len(query_words), 1)
    
    # Sub-question match score (20% weight)
    sub_score = 0.0
    for sub_q in sub_questions:
        sub_words = set(sub_q.lower().split()) - STOP_WORDS
        overlap = len(sub_words & frag_tags) / max(len(sub_words), 1)
        sub_score = max(sub_score, overlap)
    
    # Combined relevance score
    relevance = (tag_overlap * 0.4) + (content_score * 0.4) + (sub_score * 0.2)
    return relevance

RELEVANCE_THRESHOLD = 0.35  # Lowered threshold to allow more relevant fragments through


class OpenEyes:
    """
    Main OpenEyes query interface.
    
    Usage:
        oe = OpenEyes(domain="medical")
        result = oe.query("What is the safest antibiotic for a penicillin-allergic patient with a UTI?")
    """
    
    def __init__(self, domain: str = "general", 
                 fragment_library_path: Optional[str] = None,
                 api_config: Optional[Dict[str, str]] = None,
                 obsidian_vault_path: Optional[str] = None):
        
        self.domain = domain.lower()
        self.domain_tier = get_domain_tier(self.domain)
        
        # Load domain rules
        self.rules_config = get_domain_rules(self.domain)
        
        # Initialize fragment library with proper path handling
        if fragment_library_path is None:
            # Use the fragments directory relative to this module
            fragment_library_path = Path(__file__).parent.parent / "fragment_library" / "fragments"
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
        
        # Initialize Compiled Logic Index (Instinct Layer)
        self.compiled_logic = CompiledLogicIndex()
        
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
        
        # FIX 1 & IMPROVEMENT 1: Check domain boundary FIRST before any processing
        if is_out_of_domain(query_text, self.domain):
            result = {
                "trace_id": trace_id,
                "domain": self.domain,
                "tier": self.domain_tier,
                "query": query_text,
                "answer": None,
                "confidence": 0.0,
                "halt": True,
                "halt_reason": "This query is outside the finance domain.",
                "fragments_used": [],
                "philosophy_checks_passed": [],
                "processing_time_ms": 0,
                "mode": "HALT"
            }
            halt_msg = f"""I don't have verified information to answer this query.

Reason: This query is outside the finance domain. OpenEyes currently covers: 
financial markets, economic indicators, monetary policy, crypto, 
technical analysis, earnings analysis, and financial regulation.

To answer this, the library would need: general knowledge or encyclopedia fragments."""
            
            result["answer"] = halt_msg
            print(f"\n[HALT] {result['halt_reason']}")
            return self._finalize_result(result, start_time, trace_id)
        
        # Step 0: Normalize query to canonical form
        normalized_query = canonical_form(query_text)
        print(f"\n[Query Normalizer] Original: {query_text}")
        print(f"[Query Normalizer] Canonical: {normalized_query}")
        
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
            "processing_time_ms": 0,
            "mode": "DELIBERATION"  # Default mode
        }
        
        try:
            # STEP 1: Check Compiled Logic Index (Instinct Mode) using canonical form
            synapse = self.compiled_logic.query(normalized_query.split())
            
            if synapse:
                # INSTINCT MODE: Use pre-compiled logic chain
                print(f"\n[INSTINCT MODE] Using compiled synapse: {synapse.synapse_id}")
                
                fragments = self.compiled_logic.get_fragments_for_synapse(synapse, self.library)
                
                if fragments:
                    # Skip Monte Carlo, go straight to assembly
                    cleared_fragments = self._run_philosophy_guard(fragments)
                    
                    if cleared_fragments:
                        assembled_output = self._assemble_answer(cleared_fragments, query_text)
                        
                        if not assembled_output.get("halt"):
                            result["answer"] = assembled_output.get("answer", "")
                            result["confidence"] = synapse.avg_confidence  # Use synapse confidence
                            result["fragments_used"] = assembled_output.get("fragments_used", [])
                            result["philosophy_checks_passed"] = assembled_output.get("philosophy_checks", [])
                            result["mode"] = "INSTINCT"
                            
                            print(f"\n[INSTINCT MODE] Answer retrieved in {time.time() - start_time:.3f}s (vs ~2s for deliberation)")
                            print(f"{'='*60}\n")
                            
                            return self._finalize_result(result, start_time, trace_id)
                
                print("[INSTINCT MODE] Synapse fragments not available, falling back to deliberation")
            
            # DELIBERATION MODE: Full Monte Carlo pipeline
            print("[DELIBERATION MODE] No compiled logic found, running full verification\n")
            
            # Step 1: Swarm decomposition and retrieval (using normalized query)
            candidates = self._run_swarm(normalized_query)
            
            if not candidates:
                # FIX 1: Hard HALT - no content after this
                halt_response = self._build_halt_response(
                    reason="No candidate fragments found for this query.",
                    failed_candidates=[],
                    domain=self.domain
                )
                result.update(halt_response)
                print(f"\n[HALT] {result['halt_reason']}")
                return self._finalize_result(result, start_time, trace_id)
            
            print(f"\n[Step 1 Complete] Retrieved {len(candidates)} candidate fragments")
            
            # Step 2: Monte Carlo evaluation
            survivors = self._run_monte_carlo(candidates)
            
            if not survivors:
                # FIX 1: Hard HALT - no content after this
                halt_response = self._build_halt_response(
                    reason="No fragments survived Monte Carlo evaluation.",
                    failed_candidates=candidates,
                    domain=self.domain
                )
                result.update(halt_response)
                print(f"\n[HALT] {result['halt_reason']}")
                return self._finalize_result(result, start_time, trace_id)
            
            print(f"\n[Step 2 Complete] {len(survivors)} fragments survived Monte Carlo")
            
            # Step 3: Philosophy Guard validation
            cleared_fragments = self._run_philosophy_guard(survivors)
            
            if not cleared_fragments:
                # FIX 1: Hard HALT - no content after this
                halt_response = self._build_halt_response(
                    reason="No fragments passed Philosophy Guard validation.",
                    failed_candidates=survivors,
                    domain=self.domain
                )
                result.update(halt_response)
                print(f"\n[HALT] {result['halt_reason']}")
                return self._finalize_result(result, start_time, trace_id)
            
            print(f"\n[Step 3 Complete] {len(cleared_fragments)} fragments cleared Philosophy Guard")
            
            # FIX 2: Apply relevance scoring gate before assembly
            relevant_fragments = []
            relevance_scores = {}
            for frag in cleared_fragments:
                rel_score = score_relevance(frag, normalized_query, [])
                relevance_scores[frag.get('fragment_id', 'unknown')] = rel_score
                if rel_score >= RELEVANCE_THRESHOLD:
                    relevant_fragments.append(frag)
            
            if not relevant_fragments:
                # FIX 1: Hard HALT - no sufficiently relevant fragments
                halt_response = self._build_halt_response(
                    reason=f"No sufficiently relevant fragments found (all below {RELEVANCE_THRESHOLD} relevance threshold).",
                    failed_candidates=cleared_fragments,
                    domain=self.domain
                )
                result.update(halt_response)
                print(f"\n[HALT] {result['halt_reason']}")
                return self._finalize_result(result, start_time, trace_id)
            
            print(f"\n[Relevance Filter] {len(relevant_fragments)}/{len(cleared_fragments)} fragments passed relevance threshold ({RELEVANCE_THRESHOLD})")
            
            # Step 4: Dice Table assembly (using only relevant fragments)
            assembled_output = self._assemble_answer(relevant_fragments, query_text)
            
            if assembled_output.get("halt"):
                # FIX 1: Hard HALT - no content after this
                halt_response = self._build_halt_response(
                    reason=assembled_output.get("halt_reason", "Assembly failed."),
                    failed_candidates=relevant_fragments,
                    domain=self.domain
                )
                result.update(halt_response)
                print(f"\n[HALT] {result['halt_reason']}")
                return self._finalize_result(result, start_time, trace_id)
            
            result["answer"] = assembled_output.get("answer", "")
            # FIX 4: Compute confidence based on relevance, not just fragment quality
            avg_relevance = sum(relevance_scores.get(f.get('fragment_id', ''), 0) for f in result["fragments_used"]) / max(len(result["fragments_used"]), 1)
            mc_scores = [f.get('monte_carlo_score', 0) for f in result["fragments_used"]]
            avg_mc = sum(mc_scores) / max(len(mc_scores), 1) if mc_scores else 0
            philosophy_factor = 1.0 if assembled_output.get("philosophy_checks", []) else 0.5
            
            confidence = (avg_relevance * 0.5) + (avg_mc / 100 * 0.4) + (philosophy_factor * 0.1)
            result["confidence"] = round(confidence * 100, 1)
            
            result["fragments_used"] = assembled_output.get("fragments_used", [])
            result["philosophy_checks_passed"] = assembled_output.get("philosophy_checks", [])
            
            print(f"\n[Step 4 Complete] Answer assembled with confidence {result['confidence']:.1f}")
            
            # Step 5: Final composition-level Philosophy Guard check
            final_check = self._final_philosophy_check(assembled_output)
            if not final_check.get("passed", True):
                # PATTERN LEARNING: Check if fallback is permitted based on historical successes
                from openeyes.success_pattern_learner import check_fallback
                
                missing_requirements = []
                reason = final_check.get('reason', '')
                if 'counter_argument' in reason.lower():
                    missing_requirements.append('counter_argument')
                if 'definition' in reason.lower():
                    missing_requirements.append('definition')
                if 'latest_data' in reason.lower():
                    missing_requirements.append('latest_data')
                
                fallback_result = check_fallback(
                    query=query_text,
                    domain=self.domain,
                    tier='tier1' if self.domain == 'medical' else ('tier2' if self.domain == 'engineering' else 'tier3'),
                    missing=missing_requirements
                )
                
                if fallback_result.get('allow_fallback'):
                    print(f"\n[Pattern Learning] Fallback permitted: {fallback_result['reason']}")
                    result["confidence"] = result.get("confidence", 0) * fallback_result.get('confidence', 0.9) / 100.0
                    result["warnings"] = [f"Fallback applied: {fallback_result['reason']}"]
                else:
                    result["halt"] = True
                    result["halt_reason"] = f"Final validation failed: {final_check.get('reason', 'Unknown')} (Fallback not permitted: {fallback_result.get('reason', 'no pattern')})"
                    print(f"\n[HALT] {result['halt_reason']}")
                    return self._finalize_result(result, start_time, trace_id)
            
            print(f"\n[Final Check Passed]")
            
            # PATTERN LEARNING: Record this success for future fallback decisions
            if not result["halt"]:
                from openeyes.success_pattern_learner import record_success
                try:
                    record_success(
                        query=query_text,
                        domain=self.domain,
                        tier='tier1' if self.domain == 'medical' else ('tier2' if self.domain == 'engineering' else 'tier3'),
                        fragments=result["fragments_used"],
                        confidence=result["confidence"]
                    )
                except Exception as e:
                    print(f"[Pattern Learning] Could not record success: {e}")
            
            # LOGIC HARDENING: Create synapse from high-confidence result
            if result["confidence"] >= 70.0 and len(result["fragments_used"]) >= 2 and not result["halt"]:
                try:
                    self.compiled_logic.create_synapse_from_result(
                        query=query_text,
                        fragments=result["fragments_used"],
                        confidence=result["confidence"],
                        min_confidence_threshold=0.70  # Lowered threshold
                    )
                    print(f"[Logic Hardening] Created new synapse from this successful query")
                except Exception as e:
                    print(f"[Logic Hardening] Could not create synapse: {e}")
            
            # Success!
            print(f"\n{'='*60}")
            print(f"ANSWER: {result['answer'][:200]}..." if len(str(result['answer'])) > 200 else f"ANSWER: {result['answer']}")
            print(f"Confidence: {result['confidence']:.1f}%")
            print(f"Fragments used: {len(result['fragments_used'])}")
            print(f"Mode: {result['mode']}")
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
        
        # Determine domain tier for appropriate thresholds
        from openeyes.domain_rules import get_domain_tier
        domain_tier = get_domain_tier(self.domain)
        
        for candidate in candidates:
            # Create single-fragment composition for evaluation
            composition = [candidate]
            
            # Evaluate composition with domain tier
            eval_result = evaluate_composition(
                composition=composition,
                scenario=None,
                domain_tier=domain_tier
            )
            
            # Set tier-appropriate thresholds
            if domain_tier == "tier1":
                score_threshold = 50  # Lower threshold for individual fragments
                variance_threshold = 600
                survival_prob_threshold = 0.3
            elif domain_tier == "tier2":
                score_threshold = 45
                variance_threshold = 700
                survival_prob_threshold = 0.25
            else:  # tier3
                score_threshold = 40
                variance_threshold = 800
                survival_prob_threshold = 0.2
            
            # Check survival criteria using survives_mc with tier-adjusted thresholds
            survival_result = survives_mc(
                score=eval_result.mean_score,
                selected=[candidate],
                variance=eval_result.variance,
                survival_probability=eval_result.survival_probability,
                aggregate_stats={},
                score_threshold=score_threshold,
                variance_threshold=variance_threshold,
                survival_prob_threshold=survival_prob_threshold
            )
            
            if survival_result["passed"]:
                # Add evaluation metrics to candidate
                # CRITICAL: Use 'score' key (not 'mc_score') for assembler compatibility
                candidate["score"] = eval_result.mean_score
                candidate["mc_variance"] = eval_result.variance
                candidate["mc_survival_prob"] = eval_result.survival_probability
                candidate["reasoning_role"] = candidate.get("reasoning_role", "unknown")
                candidate["source_type"] = candidate.get("source_type", "tertiary")
                candidate["year"] = candidate.get("year", 0)
                survivors.append(candidate)
                
                print(f"  ✓ Fragment {candidate.get('fragment_id', 'unknown')[:20]}... survived (score={eval_result.mean_score:.1f})")
            else:
                print(f"  ✗ Fragment {candidate.get('fragment_id', 'unknown')[:20]}... failed MC (score={eval_result.mean_score:.1f}, var={eval_result.variance:.1f})")
        
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
            survivors=fragments,
            domain=self.domain,
            philosophy="do_no_harm" if self.domain == "medical" else "evidence_based",
            trace_id=None,  # Will be auto-generated
            original_query=query_text  # CRITICAL FIX: Pass original query for relevance filtering
        )
        
        return assembly.to_dict()
    
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
        
        # FIN-004: Check for price prediction language in finance domain
        if self.domain == "finance":
            answer_text = assembled_output.get("answer", "")
            if self._check_prediction_language(answer_text):
                return {
                    "passed": False,
                    "reason": "FIN-004: Answer contains price prediction language. OpenEyes does not make price predictions."
                }
        
        return {"passed": True}
    
    @staticmethod
    def _check_prediction_language(assembled_answer: str) -> bool:
        """
        Returns True if prediction language detected in finance domain.
        If True, assembly should HALT with FIN-004 violation.
        """
        PREDICTION_TRIGGER_PHRASES = [
            "will reach", "will hit", "price target", "expected to reach",
            "projected to", "forecast to", "will rise to", "will fall to",
            "will go to", "could reach", "should reach", "might hit",
            "by end of year", "by Q", "12-month target", "price objective"
        ]
        
        answer_lower = assembled_answer.lower()
        for phrase in PREDICTION_TRIGGER_PHRASES:
            if phrase.lower() in answer_lower:
                return True
        return False
    
    def _build_halt_response(self, reason: str, failed_candidates: List[Dict[str, Any]] = None, domain: str = None) -> Dict[str, Any]:
        """
        FIX 1: Build HALT response - HARD STOP, no content after this.
        Returns ONLY the halt message with reason and what's needed.
        NO fragments, NO references, NO additional content.
        """
        # Determine what fragment types are missing based on reason
        missing_types = "verified fragments directly addressing the query"
        if "Monte Carlo" in reason:
            missing_types = "fragments with sufficient credibility scores"
        elif "Philosophy Guard" in reason:
            missing_types = "fragments that pass domain rules validation"
        elif "relevant" in reason.lower():
            missing_types = "fragments with relevance score above threshold"
        elif "domain" in reason.lower():
            missing_types = "general knowledge or encyclopedia fragments"
        
        # FIX 1: Return ONLY this message - nothing else appended
        halt_msg = f"""I don't have verified information to answer this query.

Reason: {reason}

To answer this, the library would need: {missing_types}."""
        
        return {
            'halt': True,
            'answer': halt_msg,
            'halt_reason': reason,
            'confidence': 0.0,
            'fragments_used': [],
            'philosophy_checks_passed': []
        }
    
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


# Module-level query function for direct access
def query(query_text: str, domain: str = "general", verbose: bool = False) -> Dict[str, Any]:
    """
    Direct query function for module-level access.
    
    Usage:
        from openeyes import query_interface
        result = query_interface.query("your question here")
        # Or for clean output:
        response = query_interface.query("your question here", verbose=False)
        print(response['answer'])
    
    Args:
        query_text: The user's query string
        domain: Domain context (default: "general")
        verbose: If False, suppresses all debug output (default: False)
    
    Returns:
        Dict with answer, confidence, halt status, and traceability info
    """
    import sys
    from io import StringIO
    
    if not verbose:
        # Suppress stdout temporarily
        old_stdout = sys.stdout
        sys.stdout = StringIO()
    
    try:
        oe = OpenEyes(domain=domain)
        result = oe.query(query_text)
    finally:
        if not verbose:
            # Restore stdout
            sys.stdout = old_stdout
    
    return result
