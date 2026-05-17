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
from openeyes.knowledge.graceful_degradation import (
    classify_intent,
    process_query_with_degradation,
    check_safety_halt,
    GradedResponse,
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
from openeyes.cognitive.procedural_manifestor import ProceduralManifestor

akinator = AkinatorEngine()
identity = IdentityEngine(IdentityType.ANALYTICAL)  # Default identity
VERBOSE_PIPELINE = os.getenv("OPENEYES_VERBOSE_PIPELINE", "0") == "1"
logical_engine = LogicalSynthesizer()  # P3: Logical Synthesis Engine
synthesis_engine = SynthesisEngine()  # P4: Narrative Synthesis Engine
manifestor = ProceduralManifestor()  # P5: Procedural Linguistic Engine


def _pipeline_log(message: str) -> None:
    """Emit internal pipeline logs only when explicitly enabled."""
    if VERBOSE_PIPELINE:
        print(message)


def _is_complex_query(query: str) -> bool:
    q = query.lower()
    markers = ["plan", "strategy", "step by step", "roadmap", "how to", "fast", "rich", "investment"]
    return len(q.split()) >= 8 or any(m in q for m in markers)


def _is_strategic_query(query: str) -> bool:
    """Detect if query requires strategic/step-by-step answer format."""
    q = query.lower()
    strategic_markers = [
        "how to", "plan", "strategy", "step by step", "roadmap",
        "practical plan", "get rich", "investment advice", "best way",
        "practical", "action plan", "guide", "tutorial"
    ]
    return any(m in q for m in strategic_markers)





def _compose_user_answer(
    query: str,
    domain: str,
    narrative: dict,
    status: str,
    fragments_count: int = 0,
    fragments: list[Fragment] | None = None
) -> str:
    """
    P5 CRITICAL UPGRADE: Compose answers using Procedural Linguistic Manifestor.
    
    Instead of static templates or simple synthesis, this engine generates
    infinite human-like variations of verified facts using Linguistic DNA.
    
    Flow:
    1. Extract core facts from fragments
    2. Detect user intent (greeting, casual, technical, etc.)
    3. Build response structure dynamically
    4. Apply probabilistic stylistic overlay (zero hallucination)
    5. Return unique, natural language response every time
    """
    if not fragments or len(fragments) == 0:
        return "No verified information available for this query in our knowledge base."
    
    # Extract core components from top fragments
    fact = None
    analogy = None
    mechanism = None
    impact = None
    
    for frag in fragments[:5]:
        content = getattr(frag, "content", "") or getattr(frag, "claim", "") or getattr(frag, "summary", "")
        if content and not fact:
            fact = content
        
        # Look for analogy/mechanism/impact in fragment metadata or content
        if hasattr(frag, 'analogy') and frag.analogy:
            analogy = frag.analogy
        if hasattr(frag, 'mechanism') and frag.mechanism:
            mechanism = frag.mechanism
        if hasattr(frag, 'impact') and frag.impact:
            impact = frag.impact
        
        # Early exit if we have all components
        if fact and analogy and mechanism and impact:
            break
    
    # Fallback: Use synthesis engine to extract components if not in metadata
    if fact and not (analogy or mechanism or impact):
        try:
            frag_dicts = [{
                "claim": getattr(frag, "content", "") or getattr(frag, "claim", ""),
                "confidence_score": getattr(frag, "confidence_score", 0.5),
                "source_url": getattr(frag, "source_url", ""),
                "domain": getattr(frag, "domain", domain)
            } for frag in fragments[:5] if getattr(frag, "content", "") or getattr(frag, "claim", "")]
            
            if frag_dicts:
                synthesized = synthesis_engine.synthesize(query, frag_dicts)
                # Try to extract analogy/mechanism from synthesized text
                if synthesized:
                    sentences = synthesized.split('. ')
                    if len(sentences) > 1:
                        if not analogy and any(word in synthesized.lower() for word in ['imagine', 'like', 'similar', 'picture']):
                            analogy = [s for s in sentences if any(word in s.lower() for word in ['imagine', 'like', 'similar', 'picture'])][0] if any(word in synthesized.lower() for word in ['imagine', 'like', 'similar', 'picture']) else None
        except Exception as e:
            _pipeline_log(f"[MANIFESTOR] Synthesis extraction error: {e}")
    
    # If we have a fact, use the Procedural Manifestor
    if fact:
        try:
            # Get confidence from Monte Carlo result (passed via narrative or default)
            confidence = narrative.get("confidence", 0.8)
            
            # Generate human-like response with infinite variance
            response = manifestor.manifest(
                query=query,
                fact=fact,
                analogy=analogy,
                mechanism=mechanism,
                impact=impact,
                confidence=confidence,
                domain=domain
            )
            
            if response and len(response.strip()) > 10:
                return response
        except Exception as e:
            _pipeline_log(f"[MANIFESTOR] Error: {e}, falling back to synthesis")
    
    # Fallback: Use Synthesis Engine (P4)
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
    
    if frag_dicts:
        try:
            synthesized_narrative = synthesis_engine.synthesize(query, frag_dicts)
            if synthesized_narrative and len(synthesized_narrative.strip()) > 20:
                return synthesized_narrative
        except Exception as e:
            _pipeline_log(f"[SYNTHESIS] Error: {e}, falling back to fragment listing")
    
    # Ultimate fallback: Build answer from fragment content only
    answer_parts = []
    for frag in fragments[:5]:
        content = getattr(frag, "content", "") or getattr(frag, "claim", "") or getattr(frag, "summary", "")
        if content:
            answer_parts.append(content)
    
    if not answer_parts:
        return "No verified information available for this query in our knowledge base."
    

    # Check if this is a strategic query requiring step-by-step format
    if _is_strategic_query(query) and len(answer_parts) > 1:
        # Format as numbered steps for strategic queries
        formatted_parts = []
        for idx, part in enumerate(answer_parts[:5], 1):
            formatted_parts.append(f"{idx}) {part}")
        return "\n\n".join(formatted_parts)

    return "\n\n".join(answer_parts)
