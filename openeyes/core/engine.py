from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime

from openeyes.config import audit_dir
from openeyes.core.router import route_domain
from openeyes.knowledge.fragments import Fragment
from openeyes.pipeline.retriever import UnifiedRetriever
from openeyes.knowledge.live_fetch import normalize_query
from openeyes.pipeline.processor import (
    classify_intent,
    process_query_with_degradation,
    check_safety_halt,
)
from openeyes.monte_carlo.engine import MonteCarloEngine
from openeyes.storage.memory import ingest_case, retrieve_similar
from openeyes.storage.vault import write_audit_log
from openeyes.akinator_engine import refine_query_with_binary_search, AkinatorEngine
from openeyes.identity import IdentityEngine, IdentityType
from openeyes.ingestion.web_scraper import scrape_authoritative_sources
from openeyes.ingestion.auto_fragment import convert_to_fragments, verify_consistency
from openeyes.core.intent_router import route_intent
from openeyes.core.reasoning_engine import get_reasoning_engine
from openeyes.core.emergency_detection import detect_emergency, get_emergency_message

from openeyes.core.logical_synthesizer import LogicalSynthesizer
from openeyes.core.synthesis_engine import SynthesisEngine
from openeyes.ui.control_deck import ControlDeck

akinator = AkinatorEngine()
identity = IdentityEngine(IdentityType.ANALYTICAL)  # Default identity
VERBOSE_PIPELINE = os.getenv("OPENEYES_VERBOSE_PIPELINE", "0") == "1"
logical_engine = LogicalSynthesizer()  # P3: Logical Synthesis Engine
synthesis_engine = SynthesisEngine()  # P4: Narrative Synthesis Engine


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
    """
    P4 CRITICAL UPGRADE: Compose answers using Logical Narrative Synthesis.
    
    Instead of just listing facts, this engine builds a coherent argument:
    Premise -> Evidence -> Conclusion
    
    This ensures the answer actually ADDRESSES the query structure, not just
    dumps related facts.
    """
    if not fragments or len(fragments) == 0:
        return "No verified information available for this query in our knowledge base."
    
    # Convert Fragment objects to dictionaries for synthesis engine
    frag_dicts = []
    for frag in fragments:
        content = getattr(frag, "content", "") or getattr(frag, "claim", "") or getattr(frag, "summary", "")
        if content:
            frag_dicts.append({
                "claim": content,
                "confidence_score": getattr(frag, "confidence_score", 0.5),
                "source_url": getattr(frag, "source_url", ""),
                "domain": getattr(frag, "domain", domain)
            })
    
    # Use Synthesis Engine to build structured narrative
    if frag_dicts:
        try:
            synthesized_narrative = synthesis_engine.synthesize(query, frag_dicts)
            if synthesized_narrative and len(synthesized_narrative.strip()) > 20:
                return synthesized_narrative
        except Exception as e:
            _pipeline_log(f"[SYNTHESIS] Error: {e}, falling back to fragment listing")
    
    # Fallback: Build answer from fragment content only - NO synthesis or generation
    answer_parts = []
    for frag in fragments[:5]:  # Limit to top 5 most relevant fragments
        # Extract content from fragment (handle different attribute names)
        content = getattr(frag, "content", "") or getattr(frag, "claim", "") or getattr(frag, "summary", "")
        
        if content:
            answer_parts.append(content)
    
    if not answer_parts:
        return "No verified information available for this query in our knowledge base."
    
    # Join with clear separation
    return "\n\n".join(answer_parts)


class OpenEyesEngine:
    def __init__(self, vault_path: Path | None = None) -> None:
        self.mc = MonteCarloEngine()
        self.vault_path = vault_path or audit_dir()
        self.memory_path = self.vault_path / "memory.bin"
        self.retriever = UnifiedRetriever()

    def _fragments_for(self, query: str, domain: str) -> list[Fragment]:
        # Use Akinator binary search to refine query before fetching
        search_mask, traversal_path = refine_query_with_binary_search(query, domain)
        
        # Log the decision path for audit
        if traversal_path:
            _pipeline_log(f"[Akinator] Navigated {len(traversal_path)} decision points")
        
        normalized_query = normalize_query(query)
        intent = route_intent(normalized_query, domain)
        # Fetch live fragments through unified retriever
        result = self.retriever.retrieve(normalized_query, domain, max_results=search_mask.max_results)
        fetched = []
        for frag_dict in result.fragments:
            # Convert dict back to Fragment object for compatibility
            frag = Fragment(
                claim=frag_dict.get('claim', ''),
                evidence=frag_dict.get('evidence', ''),
                limitations=[],
                sub_questions=[],
                source_url=frag_dict.get('source_url', ''),
                domain=frag_dict.get('domain', domain),
                content=frag_dict.get('claim', ''),
                success_rate_ema=frag_dict.get('confidence_score', 0.7)
            )
            fetched.append(frag)
        
        # If no fragments found, trigger JIT synthesis (Research Loop)
        if not fetched:
            _pipeline_log(f"[JIT Synthesizer] No fragments found, triggering auto-research...")
            from openeyes.knowledge.live_fetch import jit_synthesize_fragments
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
        # Initialize Control Deck UI
        ui = ControlDeck()
        ui.start_session(query, domain or "auto")
        
        # P0 CRITICAL FIX: Emergency detection BEFORE any processing
        is_emergency, emergency_type, emergency_resources = detect_emergency(query)
        if is_emergency:
            ui.update_step("EMERGENCY DETECTED", "CRITICAL", color="red")
            ui.render_halt("HALT_EMERGENCY", f"Medical emergency detected: {emergency_type}", emergency_resources)
            # IMMEDIATE HALT - Do not proceed with answer generation
            return {
                "status": "HALT_EMERGENCY",
                "answer_class": "EMERGENCY_HALT",
                "answer": get_emergency_message(emergency_type, emergency_resources),
                "confidence": 0.0,
                "domain": domain or "healthcare",
                "emergency": True,
                "emergency_type": emergency_type,
                "emergency_resources": emergency_resources,
                "narrative": {"context": "Medical emergency detected", "scenarios": {}, "recommendation": "Seek immediate medical attention"},
                "replay": {},
                "data_recency_years": 0,
            }
        
        ui.update_step("Domain Routing", "PROCESSING", color="yellow")
        routed_domain = route_domain(query, domain)
        ui.update_step("Domain Routing", f"{routed_domain.upper()} ✓", color="green")
        
        # P1: Classify query intent before processing
        ui.update_step("Intent Classification", "ANALYZING", color="yellow")
        intent = classify_intent(query)
        ui.update_step("Intent Classification", f"{intent.intent.value} ✓", color="green")
        
        # P1: Check for immediate safety halt (secondary check)
        should_halt, halt_reason = check_safety_halt(query, intent, 0.5)  # Initial confidence estimate
        if should_halt:
            ui.update_step("Safety Check", "HALT TRIGGERED", color="red")
            ui.render_halt("HALT_SAFETY", halt_reason, self._get_emergency_resources(intent))
            # Return crisis resources immediately
            return {
                "status": "HALT_SAFETY",
                "answer_class": "SAFETY_HALT",
                "answer": f"Safety concern detected: {halt_reason}. Please seek immediate professional help.",
                "confidence": 0.0,
                "domain": routed_domain,
                "emergency_resources": self._get_emergency_resources(intent),
                "narrative": {"context": "", "scenarios": {}, "recommendation": "Seek professional help immediately"},
                "replay": {},
                "data_recency_years": 0,
            }
        
        # Fragment Retrieval Phase
        ui.update_step("Fragment Retrieval", "SEARCHING...", color="yellow")
        frags = self._fragments_for(query, routed_domain)
        ui.update_step("Fragment Retrieval", f"{len(frags)} FRAGMENTS ✓", color="green")
        ui.log_audit(f"Retrieved {len(frags)} fragments from knowledge base")
        
        ui.update_step("Memory Lookup", "SEARCHING...", color="yellow")
        priors = retrieve_similar(self.memory_path, query, routed_domain)
        ui.update_step("Memory Lookup", f"{len(priors)} PRIORS ✓", color="green")
        
        # P3: Logical Synthesis - Check for Emergency/Strategic intent BEFORE data processing
        # This prevents context dumping and ensures safety-first responses
        fragment_texts = [getattr(f, "claim", "") for f in frags if hasattr(f, "claim")]
        p3_result = logical_engine.process(query, routed_domain, fragment_texts)
        
        # If P3 detects emergency, bypass all other processing
        if p3_result["action"] == "HALT_AND_REDIRECT":
            ui.update_step("Logical Synthesis", "EMERGENCY HALT", color="red")
            ui.render_halt("HALT_SAFETY", p3_result["response"], self._get_emergency_resources(intent))
            return {
                "status": "HALT_SAFETY",
                "answer_class": "SAFETY_HALT",
                "answer": p3_result["response"],
                "confidence": 100.0,
                "domain": routed_domain,
                "emergency_resources": self._get_emergency_resources(intent),
                "narrative": {"context": "", "scenarios": {}, "recommendation": "Seek professional help immediately"},
                "replay": {},
                "data_recency_years": 0,
            }
        
        # Monte Carlo Swarm Evaluation
        ui.update_step("Swarm Evaluation", "RUNNING MONTE CARLO...", color="yellow")
        result = self.mc.run(query=query, domain=routed_domain, fragments=frags)
        ui.update_step("Swarm Evaluation", f"CONFIDENCE: {result.get('confidence', 0):.1f}% ✓", color="green")
        ui.log_audit(f"Monte Carlo evaluation complete: {result.get('confidence', 0):.1f}% confidence")
        
        # P3: If strategic query, use synthesized logical answer instead of raw data dump
        if p3_result["action"] == "ANSWER_STRATEGIC":
            ui.update_step("Logical Synthesis", "STRATEGIC MODE", color="cyan")
            # Override narrative with logically synthesized response
            narrative = {
                "context": "Strategic analysis based on market data",
                "scenarios": {},
                "recommendation": p3_result["response"]
            }
            result["status"] = "ANSWER_HIGH_CONFIDENCE"
            result["confidence"] = 85.0  # Synthetic confidence for strategic advice
            ui.log_audit("Strategic synthesis activated")
        
        # P1: Apply graceful degradation instead of binary HALT
        base_confidence = result.get("confidence", 0.0) / 100.0  # Convert to 0-1 scale
        
        # Use graceful degradation for healthcare domain (normalized from hc/medical)
        if routed_domain == "healthcare" or intent.requires_medical_disclaimer:
            ui.update_step("Graceful Degradation", "APPLYING SAFETY FILTERS", color="yellow")
            graded_result = process_query_with_degradation(query, frags, base_confidence)
            
            # Override with graded response
            result["status"] = graded_result["status"]
            # Handle both old dict format and new float format
            if isinstance(graded_result.get("confidence"), dict):
                result["confidence"] = graded_result["confidence"]["percent"] * 100
            else:
                result["confidence"] = graded_result.get("confidence", base_confidence) * 100
            
            # Add disclaimers and resources to narrative
            if "important_notice" in graded_result:
                result["disclaimers"] = graded_result["important_notice"]
            if "urgent_resources" in graded_result:
                result["emergency_resources"] = graded_result["urgent_resources"]
            ui.update_step("Graceful Degradation", f"{graded_result['status']} ✓", color="green")
        
        # Legacy fallback for non-medical domains
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
        answer_class = "ANSWER_CONFIDENT" if result["status"] == "ANSWER_HIGH_CONFIDENCE" else "ANSWER_LOW_CONFIDENCE"

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
        
        # Add P1 enhancements
        if "disclaimers" in result:
            out["disclaimers"] = result["disclaimers"]
        if "emergency_resources" in result:
            out["emergency_resources"] = result["emergency_resources"]
        
        # Log final audit entries
        ui.log_audit(f"Composing final answer from {len(frags)} fragments")
        ui.log_audit(f"Final confidence: {result['confidence']:.1f}%")
        
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
        
        # Render final UI output
        if result["status"].startswith("HALT"):
            ui.render_halt(result["status"], answer, out.get("emergency_resources", {}))
        else:
            ui.render_success(answer_class, answer, out["confidence"], out.get("data_recency_years", 0))
        
        return out
    
    @staticmethod
    def _get_emergency_resources(intent) -> dict:
        """Get emergency resources based on intent."""
        resources = {}
        
        # Always provide immediate emergency contact for urgency
        if intent.urgency_detected:
            resources['immediate'] = 'Call 911 or your local emergency number immediately'
        
        # Provide crisis lifeline for suicide/self-harm related queries
        if intent.intent.value == 'urgency' or intent.suggested_routing == 'emergency':
            resources['crisis'] = '988 Suicide & Crisis Lifeline (US)'
            resources['text_line'] = 'Text HOME to 741741 for Crisis Text Line'
        
        # Poison control for overdose/poisoning queries
        query_keywords = str(intent.entities) if hasattr(intent, 'entities') else ''
        if any(kw in query_keywords.lower() for kw in ['overdose', 'poison']):
            resources['poison'] = 'Poison Control: 1-800-222-1222 (US)'
        
        return resources

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
