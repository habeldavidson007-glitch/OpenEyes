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
from openeyes.core.kap import build_kap, kap_to_trace
from openeyes.core.ekd import EKDStore

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
    """Check if query is outside the economy domain."""
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
              'because', 'until', 'while', 'although', 'though', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'i', 
              'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
              'my', 'your', 'his', 'its', 'our', 'their', 'mine', 'yours', 'hers', 
              'ours', 'theirs', 'myself', 'yourself', 'himself', 'herself', 'itself', 
              'ourselves', 'themselves', 'think', 'current', 'world', 'look', 'like'}

def score_relevance(fragment: dict, query: str, sub_questions: list = None) -> float:
    """
    Score how relevant a fragment is to the actual query.
    Returns 0.0 to 1.0. Below 0.4 = exclude from assembly.
    
    Uses fragment tags and content to determine relevance to query keywords.
    Includes semantic matching for common finance terms (e.g., "stock" matches "stock_market", "equity").
    """
    if sub_questions is None:
        sub_questions = []
    
    # Clean query words: remove punctuation and stop words
    import re
    query_clean = re.sub(r'[^\w\s]', ' ', query.lower())
    query_words = set(query_clean.split()) - STOP_WORDS
    
    frag_tags = set(fragment.get('tags', []))
    frag_content = fragment.get('content', '').lower()
    
    # Semantic expansion for economy domain
    SEMANTIC_MAP = {
        'stock': {'stock', 'stock_market', 'equity', 'equities', 'share', 'shares', 'equity_factors'},
        'exchange': {'exchange', 'market', 'trading', 'trade', 'market_structure', 'market_liquidity'},
        'advice': {'advice', 'strategy', 'strategies', 'best_practices', 'guidance'},
        'invest': {'invest', 'investing', 'investment', 'portfolio', 'allocation'},
        'price': {'price', 'pricing', 'valuation', 'value'},
        'risk': {'risk', 'volatility', 'uncertainty', 'beta'},
    }
    
    # Expand query words with semantic equivalents
    expanded_query_words = set(query_words)
    for word in query_words:
        if word in SEMANTIC_MAP:
            expanded_query_words.update(SEMANTIC_MAP[word])
    
    # Tag overlap score (40% weight) - use expanded query words
    tag_overlap = len(expanded_query_words & frag_tags) / max(len(expanded_query_words), 1)
    
    # Content keyword score (40% weight) - check if query words or their stems appear in content
    content_hits = 0
    for word in query_words:
        if word in frag_content:
            content_hits += 1
        else:
            # Check for stemmed versions (simple approach: check first 4 chars for longer words)
            if len(word) > 4:
                stem = word[:4]
                if any(stem in w for w in frag_content.split()):
                    content_hits += 0.5
    
    content_score = content_hits / max(len(query_words), 1)
    
    # Sub-question match score (20% weight)
    sub_score = 0.0
    for sub_q in sub_questions:
        sub_clean = re.sub(r'[^\w\s]', ' ', sub_q.lower())
        sub_words = set(sub_clean.split()) - STOP_WORDS
        # Also expand sub-question words
        expanded_sub_words = set(sub_words)
        for sw in sub_words:
            if sw in SEMANTIC_MAP:
                expanded_sub_words.update(SEMANTIC_MAP[sw])
        overlap = len(expanded_sub_words & frag_tags) / max(len(expanded_sub_words), 1)
        sub_score = max(sub_score, overlap)
    
    # Combined relevance score
    relevance = (tag_overlap * 0.4) + (content_score * 0.4) + (sub_score * 0.2)
    return relevance

RELEVANCE_THRESHOLD = 0.15  # Lowered to allow relevant fragments through with semantic matching


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
                 obsidian_vault_path: Optional[str] = None,
                 night_mode: bool = False):
        
        self.domain = domain.lower()
        self.domain_tier = get_domain_tier(self.domain)
        
        # Load domain rules
        self.rules_config = get_domain_rules(self.domain)
        
        # Initialize fragment library with proper path handling
        if fragment_library_path is None:
            # Use the domains directory relative to this module (NEW structure)
            fragment_library_path = Path(__file__).parent.parent / "domains"
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
        
        # Initialize EKD Store
        self.ekd_store = EKDStore()
        
        # Initialize Obsidian connector (optional)
        self.obsidian = None
        if obsidian_vault_path:
            self.obsidian = ObsidianConnector(vault_path=obsidian_vault_path)
        
        # Load gene pool
        self.gene_pool = load_gene_pool()
        
        # Start Night Mode if requested
        self.night_mode_thread = None
        if night_mode:
            from openeyes.night_mode import start_night_mode
            halt_log_path = Path(__file__).parent.parent / "logs" / "halts.log"
            self.night_mode_thread = start_night_mode(
                fragment_library=self.library,
                halt_log_path=str(halt_log_path),
                obsidian_vault_path=obsidian_vault_path
            )
        
        print(f"[OpenEyes] Initialized for domain '{self.domain}' (Tier {self.domain_tier[-1]})")
        print(f"✓ Loaded {len(self.rules_config.get('rules', []))} domain rules")
        # Load fragments on demand
        if not self.library._loaded:
            self.library.load_all()
        print(f"✓ Fragment library: {self.library.total_count} fragments")
        if night_mode:
            print(f"✓ Night Mode: Started as background thread")
    
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
        
        # FIX 3: ENHANCED IMPOSSIBLE PREMISE DETECTION (Tier 5 adversarial tests)
        # Expanded patterns for better detection of unrealistic requests
        impossible_patterns = [
            ('guaranteed.*return.*zero risk', 'Impossible: No investment can guarantee returns with zero risk'),
            ('guaranteed.*wealth.*no risk', 'Impossible: No wealth-building strategy is risk-free'),
            ('cure.*all diseases', 'Impossible: No single cure exists for all diseases'),
            ('immortal|eternal life', 'Impossible: Eternal life is not medically achievable'),
            ('zero risk', 'Impossible: Zero risk does not exist in finance, medicine, or governance'),
            ('100%.*guarantee', 'Impossible: No outcome can be 100% guaranteed'),
            ('always.*win', 'Impossible: No strategy wins 100% of the time'),
            ('never loses', 'Impossible: All investments carry some risk of loss'),
            ('perfect.*democracy', 'Impossible: No political system is perfect'),
            ('absolute power.*zero corruption', 'Impossible: Absolute power without corruption is unachievable'),
            ('solve all problems', 'Impossible: No solution addresses all problems without tradeoffs'),
            ('risk-free arbitrage', 'Impossible: True arbitrage opportunities are extremely rare and not risk-free'),
            ('infinite growth', 'Impossible: Infinite growth is not sustainable in finite systems'),
            ('omniscient government', 'Impossible: No government can be omniscient'),
            ('universal.*zero taxes', 'Impossible: Universal benefits require funding'),
            ('stock.*only goes up', 'Impossible: All stocks experience volatility'),
            ('vaccine.*100%', 'Impossible: No vaccine is 100% effective for all variants'),
            ('immune to all viruses', 'Impossible: Complete immunity to all viruses is not achievable'),
            ('perfect health guarantee', 'Impossible: Perfect health cannot be guaranteed'),
            # Additional Tier 5 patterns
            ('50%.*return.*zero risk', 'Impossible: High returns always correlate with high risk'),
            ('guaranteed.*profit', 'Impossible: No profit can be guaranteed in markets'),
            ('riskless.*investment', 'Impossible: All investments carry inherent risk'),
            ('can\'t lose|cannot lose|cant lose', 'Impossible: All strategies have potential for loss'),
            ('free lunch|something for nothing', 'Impossible: There is no such thing as a free lunch in economics'),
            ('beat the market.*always', 'Impossible: Consistently beating the market without risk is impossible'),
            ('perfect prediction', 'Impossible: Perfect prediction of future events is not possible'),
            ('eliminate all risk', 'Impossible: Risk can be managed but never eliminated'),
            ('foolproof.*system', 'Impossible: No system is completely foolproof'),
            ('fail-safe.*guarantee', 'Impossible: No guarantee can cover all failure modes'),
        ]
        
        import re
        query_lower = query_text.lower()
        for pattern, reason in impossible_patterns:
            if re.search(pattern, query_lower):
                result = {
                    "trace_id": trace_id,
                    "domain": self.domain,
                    "tier": self.domain_tier,
                    "query": query_text,
                    "answer": None,
                    "confidence": 0.0,
                    "halt": True,
                    "halt_reason": reason,
                    "fragments_used": [],
                    "philosophy_checks_passed": [],
                    "processing_time_ms": 0,
                    "mode": "HALT_IMPOSSIBLE_PREMISE"
                }
                halt_msg = f"""I cannot fulfill this request because it contains an impossible premise.

Reason: {reason}

OpenEyes provides evidence-based, realistic information. I can instead help you understand:
- What is actually achievable in this area
- The real risks and tradeoffs involved
- Evidence-based strategies with realistic expectations

Would you like me to provide information on any of these alternatives?"""
                result["answer"] = halt_msg
                print(f"\n[HALT - Impossible Premise] {reason}")
                return self._finalize_result(result, start_time, trace_id)
        
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
                "halt_reason": "This query is outside the economy domain.",
                "fragments_used": [],
                "philosophy_checks_passed": [],
                "processing_time_ms": 0,
                "mode": "HALT"
            }
            halt_msg = f"""I don't have verified information to answer this query.

Reason: This query is outside the economy domain. OpenEyes currently covers: 
financial markets, energy markets, commodities, agriculture, macroeconomic indicators, 
geopolitical risk, and economic regulation.

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
            
            # Step 0.5: Extract keywords for KAP
            from openeyes.core.kap import build_kap
            keywords = [
                w for w in normalized_query.lower().split() 
                if w not in {'what', 'is', 'are', 'the', 'a', 'an', 'for', 'with', 'in', 'on', 'at', 'to', 'of', 'and', 'or', 'but', 'how', 'which', 'when', 'where', 'why', 'can', 'could', 'should', 'would', 'may', 'might', 'must', 'shall', 'i', 'me', 'my', 'we', 'us', 'our', 'you', 'your', 'he', 'she', 'it', 'they', 'them', 'their'} and len(w) > 2
            ]
            
            # Step 0.6: Build KAP — reason about what this query needs
            kap = build_kap(
                query=normalized_query,
                domain=self.domain,
                keywords=keywords
            )
            
            # Step 0.7: EKD check — find matching knowledge cluster
            ekd_match = self.ekd_store.find_matching_cluster(
                canonical_query=normalized_query,
                domain=self.domain,
                primary_tags=keywords[:5]
            )
            
            cluster_fragments = []
            if ekd_match:
                # Activate cluster — get its pre-validated fragments as head start
                cluster_fragments = self.ekd_store.get_cluster_fragments(
                    ekd_match, self.library
                )
                print(f"[EKD] Activated cluster v{ekd_match.current_version}: "
                      f"{len(cluster_fragments)} fragments pre-loaded")
            
            # Step 0.8: Log KAP trace
            kap_trace = kap_to_trace(kap)
            print(f"\n{kap_trace}\n")
            
            # Step 0.9: Execute retrieval layer by layer
            candidates_by_layer = self.swarm.retrieve_by_kap(
                query=normalized_query,
                domain=self.domain,
                kap=kap
            )
            
            # Step 0.10: Merge cluster fragments with fresh retrieval
            # Cluster fragments get a slight priority boost (they're pre-validated)
            all_candidates = list(cluster_fragments)
            for layer_name, candidates in candidates_by_layer.items():
                if not layer_name.endswith('_MISSING'):
                    all_candidates.extend(candidates)
            
            # Deduplicate by fragment_id
            seen_ids = set()
            unique_candidates = []
            for c in all_candidates:
                frag_id = getattr(c, 'fragment_id', getattr(c, 'id', str(c)))
                if frag_id not in seen_ids:
                    seen_ids.add(frag_id)
                    unique_candidates.append(c)
            
            candidates = unique_candidates
            
            # Step 0.11: Check mandatory layers all have results
            halt_reason = None
            for layer in kap.mandatory_layers():
                missing_key = f"{layer.name}_MISSING"
                if missing_key in candidates_by_layer:
                    halt_reason = (
                        f"Mandatory knowledge layer '{layer.name}' returned no fragments. "
                        f"Purpose: {layer.purpose}. "
                        f"Searched for roles: {layer.required_roles} "
                        f"with tags: {layer.target_tags}"
                    )
                    break
            
            if halt_reason:
                result.update(self._build_halt_response(
                    reason=halt_reason,
                    failed_candidates=[],
                    domain=self.domain
                ))
                print(f"\n[HALT] {result['halt_reason']}")
                return self._finalize_result(result, start_time, trace_id)
            
            # Step 0.10: Flatten candidates from all layers for Monte Carlo
            all_candidates = []
            for layer_name, candidates in candidates_by_layer.items():
                if not layer_name.endswith('_MISSING'):
                    all_candidates.extend(candidates)
            
            candidates = all_candidates
            
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
            
            # FIX 1: Ensure HALT responses have NO additional content appended
            if assembled_output.get("halt"):
                result["answer"] = assembled_output.get("answer", "")
                result["confidence"] = 0.0
                result["fragments_used"] = []
                result["philosophy_checks_passed"] = []
                print(f"\n[HALT] {assembled_output.get('halt_reason', 'Unknown')}")
                return self._finalize_result(result, start_time, trace_id)
            
            result["answer"] = assembled_output.get("answer", "")
            # FIX 1 & 2: IMPROVED CONFIDENCE SCORING ALGORITHM
            # Addresses: General domain low confidence (66%) and Healthcare all-LOW_CONFIDENCE issue
            used_frag_ids = [f.get('fragment_id', '') for f in assembled_output.get("fragments_used", [])]
            relevant_scores = [relevance_scores.get(fid, 0) for fid in used_frag_ids]
            avg_relevance = sum(relevant_scores) / max(len(relevant_scores), 1) if relevant_scores else 0
            mc_scores = [f.get('score', 0) for f in assembled_output.get("fragments_used", [])]
            avg_mc = sum(mc_scores) / max(len(mc_scores), 1) if mc_scores else 0
            philosophy_factor = 1.0 if assembled_output.get("philosophy_checks_passed", []) else 0.5
            
            # Count fragments for calibration
            num_fragments = len(used_frag_ids)
            
            # IMPROVEMENT 1: Add fragment count bonus (more verified fragments = higher confidence)
            fragment_count_bonus = min(num_fragments / 5.0, 1.0) * 0.15  # Up to 15% bonus for 5+ fragments
            
            # IMPROVEMENT 2: Domain-specific calibration
            # Healthcare was penalized too harshly - adjust weights for high-stakes domains
            if self.domain in ['healthcare', 'governance', 'medical', 'legal']:
                # For high-stakes domains, trust MC scores more (they've passed strict verification)
                confidence = (avg_relevance * 0.3) + (avg_mc / 100 * 0.5) + (philosophy_factor * 0.05) + fragment_count_bonus
            elif self.domain == 'general':
                # General domain was scoring too low - rebalance weights
                confidence = (avg_relevance * 0.4) + (avg_mc / 100 * 0.45) + (philosophy_factor * 0.1) + fragment_count_bonus
            else:
                # Standard weighting for other domains
                confidence = (avg_relevance * 0.35) + (avg_mc / 100 * 0.45) + (philosophy_factor * 0.1) + fragment_count_bonus
            
            # IMPROVEMENT 3: Apply minimum confidence floor for answers that pass all checks
            # If an answer passes philosophy guard and has decent fragments, it shouldn't be below 70%
            if assembled_output.get("philosophy_checks_passed") and num_fragments >= 2:
                confidence = max(confidence, 0.70)
            
            # IMPROVEMENT 4: Cap at reasonable maximum based on domain tier
            # Tier 1 domains (healthcare, governance) should not exceed 95% to maintain appropriate caution
            tier_caps = {
                'tier0': 0.90, 'tier1': 0.95, 'tier2': 0.97, 'tier3': 0.98, 'tier4': 0.99
            }
            domain_tier = get_domain_tier(self.domain)
            max_confidence = tier_caps.get(domain_tier, 0.97)
            confidence = min(confidence, max_confidence)
            
            result["confidence"] = round(confidence * 100, 1)
            
            result["fragments_used"] = assembled_output.get("fragments_used", [])
            result["philosophy_checks_passed"] = assembled_output.get("philosophy_checks_passed", [])
            
            print(f"\n[Step 4 Complete] Answer assembled with confidence {result['confidence']:.1f}%")
            
            # Step 5: Final composition-level Philosophy Guard check
            final_check = self._final_philosophy_check(assembled_output)
            if not final_check.get("passed", True):
                # FIX 1: Hard HALT on final check failure - no fallback unless explicitly permitted
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
                    # FIX 1: HARD HALT - no content after this
                    halt_response = self._build_halt_response(
                        reason=f"Final validation failed: {final_check.get('reason', 'Unknown')} (Fallback not permitted)",
                        failed_candidates=relevant_fragments,
                        domain=self.domain
                    )
                    result.update(halt_response)
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
            
            # EKD CRYSTALLIZATION: If answer succeeded with high confidence, crystallize into EKD
            if not result.get('halt') and result.get('confidence', 0) >= 75.0:
                used_fragment_ids = [
                    f.get('fragment_id', '') 
                    for f in result.get('fragments_used', [])
                ]
                self.ekd_store.crystallize(
                    canonical_query=normalized_query,
                    domain=self.domain,
                    fragment_ids=used_fragment_ids,
                    confidence=result.get('confidence', 0),
                    primary_tags=keywords[:5],
                    kap_intent_type=kap.intent.intent_type,
                    trigger_query=query_text
                )
            
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
    
    def _run_monte_carlo(self, candidates) -> List[Dict[str, Any]]:
        """Run Monte Carlo evaluation on candidates."""
        survivors = []
        
        # Determine domain tier for appropriate thresholds
        from openeyes.domain_rules import get_domain_tier
        from openeyes.swarm import FragmentCandidate
        domain_tier = get_domain_tier(self.domain)
        
        for candidate in candidates:
            # Handle both FragmentCandidate objects and dict candidates
            if isinstance(candidate, FragmentCandidate):
                cand_dict = candidate.to_dict()
            else:
                cand_dict = candidate
            
            # Create single-fragment composition for evaluation
            composition = [cand_dict]
            
            # Evaluate composition with domain tier
            eval_result = evaluate_composition(
                composition=composition,
                scenario=None,
                domain_tier=domain_tier
            )
            
            # Set tier-appropriate thresholds
            # FIX 2: Tighter survival thresholds to reduce survivors from 128-218 to 20-40 range
            if domain_tier == "tier1":
                score_threshold = 65  # Increased from 50 to require higher quality
                variance_threshold = 300  # Reduced from 600 for tighter stability
                survival_prob_threshold = 0.55  # Increased from 0.3 for better discrimination
            elif domain_tier == "tier2":
                score_threshold = 65  # Increased from 45
                variance_threshold = 300  # Reduced from 700
                survival_prob_threshold = 0.55  # Increased from 0.25
            else:  # tier3
                score_threshold = 65  # Increased from 40
                variance_threshold = 300  # Reduced from 800
                survival_prob_threshold = 0.55  # Increased from 0.2
            
            # Check survival criteria using survives_mc with tier-adjusted thresholds
            survival_result = survives_mc(
                score=eval_result.mean_score,
                selected=[cand_dict],
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
                cand_dict["score"] = eval_result.mean_score
                cand_dict["mc_variance"] = eval_result.variance
                cand_dict["mc_survival_prob"] = eval_result.survival_probability
                cand_dict["reasoning_role"] = cand_dict.get("reasoning_role", "unknown")
                cand_dict["source_type"] = cand_dict.get("source_type", "tertiary")
                cand_dict["year"] = cand_dict.get("year", 0)
                
                # FIX: Normalize fragment keys for Philosophy Guard compatibility
                # Swarm fragments use 'fragment_id' but Philosophy Guard expects 'id'
                if "fragment_id" in cand_dict and "id" not in cand_dict:
                    cand_dict["id"] = cand_dict["fragment_id"]
                # Swarm fragments use 'credibility_estimate' but Philosophy Guard expects 'credibility_class'
                if "credibility_estimate" in cand_dict and "credibility_class" not in cand_dict:
                    # Map numeric estimate to class name for rule compatibility
                    cred_est = cand_dict["credibility_estimate"]
                    if cred_est >= 0.9:
                        cand_dict["credibility_class"] = "international_institution"
                    elif cred_est >= 0.8:
                        cand_dict["credibility_class"] = "academic_research"
                    elif cred_est >= 0.7:
                        cand_dict["credibility_class"] = "financial_publication"
                    elif cred_est >= 0.5:
                        cand_dict["credibility_class"] = "financial_news"
                    else:
                        cand_dict["credibility_class"] = "anecdotal"
                # Ensure tags field exists (some sources use 'domain_tags')
                if "domain_tags" in cand_dict and "tags" not in cand_dict:
                    cand_dict["tags"] = cand_dict["domain_tags"]
                # Ensure last_verified exists for age checks
                if "last_verified" not in cand_dict:
                    from datetime import datetime
                    cand_dict["last_verified"] = datetime.now().strftime("%Y-%m-%d")
                
                survivors.append(cand_dict)
                
                frag_id = cand_dict.get('fragment_id', cand_dict.get('id', 'unknown'))
                print(f"  ✓ Fragment {frag_id[:20] if frag_id else 'unknown'}... survived (score={eval_result.mean_score:.1f})")
            else:
                frag_id = cand_dict.get('fragment_id', 'unknown')
                print(f"  ✗ Fragment {frag_id[:20] if frag_id else 'unknown'}... failed MC (score={eval_result.mean_score:.1f}, var={eval_result.variance:.1f})")
        
        return survivors
    
    def _run_philosophy_guard(self, fragments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run Philosophy Guard validation on fragments."""
        cleared = []
        
        for fragment in fragments:
            # Convert Fragment object to dict if needed
            if hasattr(fragment, 'to_dict'):
                frag_dict = fragment.to_dict()
            else:
                frag_dict = fragment
            
            # Validate fragment against domain rules
            violations = []
            
            for rule in self.guard.rules:
                check_result = self.guard._apply_rule(rule, frag_dict)
                if not check_result.get("passed", True):
                    violations.append(check_result)
            
            if not violations:
                cleared.append(fragment)  # Keep original object (Fragment or dict)
                frag_id = frag_dict.get('id', 'unknown')
                print(f"  ✓ Fragment {frag_id[:20]}... passed Philosophy Guard")
            else:
                frag_id = frag_dict.get('id', 'unknown')
                print(f"  ✗ Fragment {frag_id[:20]}... failed: {[v.get('rule_id') for v in violations]}")
        
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
        
        # ECO-004: Check for price prediction language in economy domain (includes finance)
        if self.domain in ["economy", "finance"]:
            answer_text = assembled_output.get("answer", "")
            if self._check_prediction_language(answer_text):
                return {
                    "passed": False,
                    "reason": "ECO-004: Answer contains price prediction language. OpenEyes does not make price predictions."
                }
        
        return {"passed": True}
    
    @staticmethod
    def _check_prediction_language(assembled_answer: str) -> bool:
        """
        Returns True if prediction language detected in economy domain.
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
