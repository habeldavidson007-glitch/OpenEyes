"""
openeyes/knowledge/retrieval.py

Original retrieval implementation (preserved for backward compatibility).
This is NOT a wrapper - it's the original implementation.
New code can optionally use openeyes.pipeline.retriever instead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from openeyes.knowledge.fragments import Fragment
from openeyes.knowledge.live_fetch import fetch_live_fragments, jit_synthesize_fragments
from openeyes.knowledge.local_retrieval import retrieve_local_fragments


@dataclass
class RetrievalRecord:
    claim: str
    source: str
    url: str
    published_on: str
    confidence: float
    fragment: Fragment


def retrieve_records(query: str, domain: str, limit: int) -> List[RetrievalRecord]:
    """
    Enhanced retrieval with local fragment support and swarm integration.
    
    New retrieval chain:
    1. Swarm WAL buffer (pre-computed autonomous harvest data) - ZERO LATENCY
    2. Local fragments (curated knowledge base) - FAST & RELIABLE
    3. Live web fetch (external APIs) - For recent/missing info
    4. JIT synthesis (only for non-verified domains) - Fallback
    
    This integrates the Autonomous Signal-Pulse Swarm into the query pipeline,
    enabling zero-latency answers from pre-harvested, tokenized data.
    """
    frags: List[Fragment] = []
    
    # PRIORITY 0: Swarm WAL buffer (NEW - autonomous harvest data)
    try:
        from openeyes.swarm.swarm_retrieval import integrate_swarm_with_retrieval
        swarm_frags = integrate_swarm_with_retrieval(query, domain, limit=limit)
        if swarm_frags:
            frags.extend(swarm_frags)
            print(f"[RETRIEVAL] Found {len(swarm_frags)} fragments from SWARM (pre-computed)")
    except ImportError as e:
        print(f"[RETRIEVAL] Swarm integration not available: {e}")
    except Exception as e:
        print(f"[RETRIEVAL] Swarm retrieval error: {e}")
    
    # PRIORITY 1: Local fragment retrieval (curated knowledge base)
    # Map domain names to internal codes
    domain_code_map = {
        'healthcare': 'hc',
        'economy': 'eco',
        'engineering': 'eng',
    }
    domain_code = domain_code_map.get(domain.lower(), domain.lower())
    
    try:
        local_frags = retrieve_local_fragments(query, domain=domain_code, limit=limit)
        if local_frags:
            frags.extend(local_frags)
            print(f"[RETRIEVAL] Found {len(local_frags)} local fragments for '{query}'")
    except Exception as e:
        print(f"[RETRIEVAL] Local retrieval error: {e}")
    
    # PRIORITY 2: Live web fetch (if local + swarm insufficient)
    if len(frags) < limit:
        remaining = limit - len(frags)
        live_frags = fetch_live_fragments(query, domain, limit=remaining)
        if live_frags:
            frags.extend(live_frags)
            print(f"[RETRIEVAL] Found {len(live_frags)} live fragments for '{query}'")
    
    # PRIORITY 3: JIT synthesis (only for non-verified domains)
    if len(frags) < limit:
        from openeyes.knowledge.live_fetch import VERIFIED_DOMAINS
        if domain not in VERIFIED_DOMAINS:
            remaining = limit - len(frags)
            jit_frags = jit_synthesize_fragments(query, domain, limit=remaining)
            if jit_frags:
                frags.extend(jit_frags)
                print(f"[RETRIEVAL] Synthesized {len(jit_frags)} fragments for '{query}'")
    
    # Build records
    records: List[RetrievalRecord] = []
    seen_claims = set()  # Deduplicate by claim
    
    for f in frags:
        if f.claim in seen_claims:
            continue
        seen_claims.add(f.claim)
        
        confidence = 0.9 if getattr(f, "evidence_level", "moderate") == "high" else 0.7
        
        # Boost confidence for local curated fragments
        if hasattr(f, 'source_id') and f.source_id.endswith('.json'):
            confidence = min(0.95, confidence + 0.15)  # Local fragments get boost
        
        # Boost confidence for swarm-harvested fragments (pre-verified)
        if hasattr(f, 'swarm_metadata'):
            confidence = min(0.95, confidence + 0.10)  # Swarm fragments get boost
        
        records.append(
            RetrievalRecord(
                claim=f.claim,
                source=f.evidence,
                url=getattr(f, "source_url", ""),
                published_on=getattr(f, "published_on", ""),
                confidence=confidence,
                fragment=f,
            )
        )
    
    return records
