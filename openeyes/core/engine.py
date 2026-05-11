from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime

from openeyes.config import audit_dir
from openeyes.core.router import route_domain
from openeyes.knowledge.fragments import Fragment
from openeyes.knowledge.live_fetch import fetch_live_fragments, jit_synthesize_fragments, normalize_query
from openeyes.knowledge.retrieval import retrieve_records
from openeyes.monte_carlo.engine import MonteCarloEngine
from openeyes.storage.memory import ingest_case, retrieve_similar
from openeyes.storage.vault import write_audit_log
from openeyes.akinator_engine import refine_query_with_binary_search, AkinatorEngine
from openeyes.identity import IdentityEngine, IdentityType
from openeyes.ingestion.web_scraper import scrape_authoritative_sources
from openeyes.ingestion.auto_fragment import convert_to_fragments, verify_consistency
from openeyes.core.intent_router import route_intent
from openeyes.core.reasoning_engine import get_reasoning_engine

akinator = AkinatorEngine()
identity = IdentityEngine(IdentityType.ANALYTICAL)  # Default identity
VERBOSE_PIPELINE = os.getenv("OPENEYES_VERBOSE_PIPELINE", "0") == "1"


def _pipeline_log(message: str) -> None:
    """Emit internal pipeline logs only when explicitly enabled."""
    if VERBOSE_PIPELINE:
        print(message)


def _is_complex_query(query: str) -> bool:
    q = query.lower()
    markers = ["plan", "strategy", "step by step", "roadmap", "how to", "fast", "rich", "investment"]
    return len(q.split()) >= 8 or any(m in q for m in markers)





def _compose_user_answer(
    query: str,
    domain: str,
    narrative: dict,
    status: str,
    fragments_count: int = 0,
    fragments: list[Fragment] | None = None
) -> str:
    """Compose answer directly from fragments without narrative expansion."""
    if not fragments:
        return "No verified information available for this query."
    
    # Build answer from fragment content only
    answer_parts = []
    for frag in fragments[:5]:  # Limit to top 5 fragments
        content = getattr(frag, "content", "") or getattr(frag, "claim", "")
        if content:
            answer_parts.append(content)
    
    return "\n\n".join(answer_parts) if answer_parts else "No verified information available."


class OpenEyesEngine:
    def __init__(self, vault_path: Path | None = None) -> None:
        self.mc = MonteCarloEngine()
        self.vault_path = vault_path or audit_dir()
        self.memory_path = self.vault_path / "memory.bin"

    def _fragments_for(self, query: str, domain: str) -> list[Fragment]:
        # Use Akinator binary search to refine query before fetching
        search_mask, traversal_path = refine_query_with_binary_search(query, domain)
        
        # Log the decision path for audit
        if traversal_path:
            _pipeline_log(f"[Akinator] Navigated {len(traversal_path)} decision points")
        
        normalized_query = normalize_query(query)
        intent = route_intent(normalized_query, domain)
        # Fetch live fragments through retriever contract
        records = retrieve_records(normalized_query, domain, limit=search_mask.max_results)
        fetched = [r.fragment for r in records]
        
        # If no fragments found, trigger JIT synthesis (Research Loop)
        if not fetched:
            _pipeline_log(f"[JIT Synthesizer] No fragments found, triggering auto-research...")
            synthesized = jit_synthesize_fragments(normalized_query, domain, limit=5)
            if synthesized:
                _pipeline_log(f"[JIT Synthesizer] Generated {len(synthesized)} synthetic fragments")
                fetched = synthesized
        
        # Filter fragments using CES-based mask
        filtered = akinator.filter_fragments_by_mask(fetched, search_mask)
        active_ces_threshold = search_mask.min_ces_score
        
        _pipeline_log(f"[Akinator] Filtered {len(fetched)} -> {len(filtered)} fragments (CES >= {active_ces_threshold})")
        if fetched and not filtered:
            fallback_count = min(len(fetched), max(1, search_mask.max_results))
            filtered = sorted(fetched, key=lambda f: getattr(f, "effective_weight", 0.0))[:fallback_count]
            _pipeline_log(f"[Akinator][WARN] Filtered count = 0; accepting {len(filtered)} lowest-scoring fragments as fallback")
        
        # PHASE 1-2: Autonomous Research Loop (if confidence would be low)
        # Check if we have enough high-quality fragments
        high_evidence_count = sum(1 for f in filtered if getattr(f, 'evidence_level', '') == 'high')
        intent_type = intent.intent_type if hasattr(intent, 'intent_type') else str(intent)
        if high_evidence_count < 2 and intent_type in {"current_events", "factual_entity"}:
            _pipeline_log(f"[AUTONOMOUS] Low evidence detected ({high_evidence_count} high-evidence fragments), triggering web research...")
            
            # Phase 1: Scrape authoritative sources
            scraped = scrape_authoritative_sources(normalized_query, domain, max_results=5)
            
            if scraped:
                # Phase 2: Convert to fragments
                new_fragments = convert_to_fragments(scraped, normalized_query, domain, max_fragments=10)
                
                # Verify consistency with existing knowledge
                if new_fragments:
                    consistent_frags = verify_consistency(new_fragments, filtered)
                    filtered.extend(consistent_frags)
                    _pipeline_log(f"[AUTONOMOUS] Added {len(consistent_frags)} verified fragments from web research")
        
        # Apply identity-based weighting
        if identity:
            weighted_filtered = []
            for frag in filtered:
                weight = identity.apply_weight_to_fragment(frag)
                if weight >= identity.config.evidence_threshold * 0.5:
                    weighted_filtered.append(frag)
            filtered = weighted_filtered
            _pipeline_log(f"[IDENTITY] {identity.config.name} filtered to {len(filtered)} fragments")
        
        # Apply 5-Stage Reasoning Engine
        if filtered:
            _pipeline_log(f"[REASONING] Running 5-stage reasoning pipeline...")
            reasoning_engine = get_reasoning_engine()
            trace = reasoning_engine.process(normalized_query, domain, filtered)
            
            # Update fragment weights based on reasoning results
            # Fragments already have their weights adjusted in-place by the engine
            
            _pipeline_log(f"[REASONING] Confidence: {trace.final_confidence:.1f}%, Actionability: {trace.actionability_score:.2f}")
            _pipeline_log(f"[REASONING] Cross-domain links: {len(trace.cross_domain_links)}, Contradictions: {len(trace.contradictions_detected)}")
            
            # Store trace in fragments metadata for audit
            for frag in filtered:
                if not hasattr(frag, 'reasoning_trace'):
                    frag.reasoning_trace = trace
        
        return filtered

    @staticmethod
    def _safe_fallback_answer(query: str, domain: str, status: str, narrative: dict) -> str:
        scenarios = narrative.get("scenarios", {})
        return (
            f"OpenEyes safety mode: {status} for query '{query}'.\n\n"
            f"Context: {narrative.get('context', '')}\n"
            f"Best-case: {scenarios.get('best', '')}\n"
            f"Likely-case: {scenarios.get('likely', '')}\n"
            f"Worst-case: {scenarios.get('worst', '')}\n"
            f"Recommendation: {narrative.get('recommendation', '')}\n"
            "Disclaimer: For real financial, legal, or medical decisions, consult licensed professionals."
        )

    def answer(self, query: str, domain: str | None = None) -> dict:
        routed_domain = route_domain(query, domain)
        frags = self._fragments_for(query, routed_domain)
        priors = retrieve_similar(self.memory_path, query, routed_domain)
        result = self.mc.run(query=query, domain=routed_domain, fragments=frags)
        if result["status"].startswith("HALT") and frags:
            result["status"] = "ANSWER_LOW_CONFIDENCE"
        if priors and result.get("confidence", 0.0) < 60:
            result["confidence"] = round(min(99.0, result["confidence"] + 5.0 * len(priors)), 2)

        replay = json.loads(result["replay"])
        # Generate narrative from result
        narrative = result.get("narrative", {"context": "", "scenarios": {}, "recommendation": ""})
        
        # Pass fragment count for narrative expansion
        answer = _compose_user_answer(
            query,
            routed_domain,
            narrative,
            result["status"],
            fragments_count=len(frags),
            fragments=frags
        )
        answer_class = "ANSWER_CONFIDENT" if result["status"] == "ANSWER" else "ANSWER_LOW_CONFIDENCE"

        out = {
            "status": result["status"],
            "answer_class": answer_class,
            "answer": answer,
            "confidence": result["confidence"],
            "domain": routed_domain,
            "narrative": narrative,
            "replay": replay,
            "data_recency_years": self._estimate_data_recency_years(frags),
        }
        ingest_case(
            self.memory_path,
            {
                "query": query,
                "domain": routed_domain,
                "status": result["status"],
                "confidence": result["confidence"],
                "data_recency_years": out["data_recency_years"],
                "winning_fragment_set": self._winning_fragment_set(frags),
                "top_claim": getattr(frags[0], "claim", "") if frags else "",
            }
        )
        write_audit_log(self.vault_path, query, out)
        return out

    @staticmethod
    def _estimate_data_recency_years(fragments: list[Fragment]) -> int:
        """Estimate recency window in years from fragment publication dates."""
        years = []
        current_year = datetime.now().year
        for frag in fragments:
            published = getattr(frag, "published_on", "")
            if isinstance(published, str) and len(published) >= 4 and published[:4].isdigit():
                years.append(max(0, current_year - int(published[:4])))
        if not years:
            return 10
        return max(1, min(years))

    @staticmethod
    def _winning_fragment_set(fragments: list[Fragment]) -> list[str]:
        """Store correlated fragment source IDs for retrieval-memory recall."""
        return [getattr(f, "source_id", "") for f in fragments if getattr(f, "source_id", "")]
