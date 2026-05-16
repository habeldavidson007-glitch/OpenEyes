"""
Unified Knowledge Orchestrator for OpenEyes
Consolidates local_retrieval, live_fetch, fragment_orchestrator, and graceful_degradation.
Implements cascading retrieval (Local -> Cache -> Live) with Adaptive Confidence Calibration.
Uses real database and API clients instead of mocks.
"""

import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Real implementations
from .database_client import get_database, KnowledgeDatabase
from .api_client import get_api_client, LiveAPIClient, APIProvider
from .quality_assessor import get_assessor, KnowledgeQualityAssessor, CredibilityLevel

logger = logging.getLogger(__name__)

class SourceTier(Enum):
    LOCAL_HIGH_CONFIDENCE = 1
    LOCAL_VERIFIED = 2
    CACHE_RECENT = 3
    LIVE_FETCH = 4
    FALLBACK_ESTIMATE = 5

@dataclass
class KnowledgeFragment:
    content: str
    source_url: str
    confidence_score: float
    tier: SourceTier
    domain: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OrchestratorResult:
    answer: str
    confidence: float
    sources: List[str]
    execution_time_ms: float
    strategy_used: str
    cross_domain_fusion: bool = False

class AdaptiveConfidenceCalibrator:
    """
    ML-based (simulated) system to track answer accuracy and adjust confidence scores.
    In production, this would load a trained model or maintain a running history.
    """
    def __init__(self):
        # Simulated historical performance per domain
        self.domain_history = {
            "Healthcare": {"accuracy": 0.98, "count": 150},
            "Economy": {"accuracy": 0.99, "count": 120},
            "Governance": {"accuracy": 0.97, "count": 80},
            "Investment": {"accuracy": 0.96, "count": 90},
            "General": {"accuracy": 0.85, "count": 200} # Lower historical accuracy
        }
    
    def calibrate(self, base_confidence: float, domain: str, source_tier: SourceTier) -> float:
        history = self.domain_history.get(domain, {"accuracy": 0.90, "count": 10})
        
        # Weight factors
        tier_weight = {
            SourceTier.LOCAL_HIGH_CONFIDENCE: 1.0,
            SourceTier.LOCAL_VERIFIED: 0.95,
            SourceTier.CACHE_RECENT: 0.90,
            SourceTier.LIVE_FETCH: 0.85,
            SourceTier.FALLBACK_ESTIMATE: 0.60
        }.get(source_tier, 0.5)
        
        # Adjust based on historical domain accuracy
        domain_factor = history["accuracy"]
        
        # Formula: Base * TierWeight * DomainFactor + Small Noise Buffer
        calibrated = base_confidence * tier_weight * domain_factor
        
        # Ensure bounds [0, 1]
        return max(0.0, min(1.0, calibrated))

    def record_feedback(self, domain: str, was_accurate: bool):
        """Update historical stats based on real-world feedback."""
        if domain not in self.domain_history:
            self.domain_history[domain] = {"accuracy": 0.5, "count": 0}
        
        stats = self.domain_history[domain]
        total = stats["count"]
        current_acc = stats["accuracy"]
        
        new_count = total + 1
        new_acc = ((current_acc * total) + (1.0 if was_accurate else 0.0)) / new_count
        
        self.domain_history[domain] = {"accuracy": new_acc, "count": new_count}

class CrossDomainFusionEngine:
    """
    Enables reasoning across multiple domains (e.g., "economic impact of diabetes").
    Combines fragments from different domains and synthesizes a unified answer.
    """
    def __init__(self):
        self.enabled = True
    
    def detect_domains(self, query: str) -> List[str]:
        """Simple heuristic to detect multi-domain intent."""
        query_lower = query.lower()
        detected = []
        if any(k in query_lower for k in ["cost", "economic", "market", "gdp", "finance"]):
            detected.append("Economy")
        if any(k in query_lower for k in ["health", "disease", "medical", "hospital", "patient"]):
            detected.append("Healthcare")
        if any(k in query_lower for k in ["policy", "law", "government", "regulation", "vote"]):
            detected.append("Governance")
        if any(k in query_lower for k in ["invest", "stock", "return", "portfolio"]):
            detected.append("Investment")
        
        if not detected:
            detected.append("General")
        return detected

    def fuse_fragments(self, fragments: List[KnowledgeFragment], query: str) -> str:
        if len(fragments) <= 1:
            return fragments[0].content if fragments else "No information found."
        
        # Group by domain
        by_domain: Dict[str, List[KnowledgeFragment]] = {}
        for frag in fragments:
            if frag.domain not in by_domain:
                by_domain[frag.domain] = []
            by_domain[frag.domain].append(frag)
        
        synthesis_parts = []
        for domain, frags in by_domain.items():
            content_summary = " ".join([f.content[:100] + "..." for f in frags])
            synthesis_parts.append(f"[{domain} Insight]: {content_summary}")
        
        return f"Cross-Domain Analysis for '{query}':\n" + "\n".join(synthesis_parts)

class UnifiedKnowledgeOrchestrator:
    def __init__(self, db_path: str = None, api_keys: Dict[str, str] = None):
        self.db = get_database(db_path)
        self.api_client = get_api_client(api_keys)
        self.assessor = get_assessor()
        self.calibrator = AdaptiveConfidenceCalibrator()
        self.fusion_engine = CrossDomainFusionEngine()
        
    def retrieve_knowledge(self, query: str, domain_hint: Optional[str] = None) -> OrchestratorResult:
        start_time = time.time()
        
        # 1. Detect Domains (Support Cross-Domain)
        target_domains = self.fusion_engine.detect_domains(query) if not domain_hint else [domain_hint]
        is_cross_domain = len(target_domains) > 1
        
        all_fragments: List[KnowledgeFragment] = []
        strategy_used = "LOCAL_ONLY"
        
        # 2. Cascading Retrieval Strategy
        # Tier 1: Check Cache First
        cached_result = self.db.get_cached_result(query)
        if cached_result and cached_result.get('fragments'):
            logger.info(f"Cache hit for '{query}'")
            for frag_data in cached_result['fragments']:
                all_fragments.append(KnowledgeFragment(
                    content=frag_data['content'],
                    source_url=frag_data['source_url'],
                    confidence_score=frag_data['confidence_score'],
                    tier=SourceTier[frag_data['tier']],
                    domain=frag_data['domain'],
                    timestamp=frag_data.get('timestamp', time.time()),
                    metadata=frag_data.get('metadata', {})
                ))
            strategy_used = "CACHE_HIT"
        
        # Tier 2: Local Database Retrieval
        if not all_fragments:
            for domain in target_domains:
                db_frags = self.db.retrieve_fragments(query, domain, min_confidence=0.7, limit=5)
                if db_frags:
                    for frag_data in db_frags:
                        all_fragments.append(KnowledgeFragment(
                            content=frag_data['content'],
                            source_url=frag_data['source_url'],
                            confidence_score=frag_data['confidence_score'],
                            tier=SourceTier.LOCAL_HIGH_CONFIDENCE if frag_data.get('credibility_level') == 'HIGH' else SourceTier.LOCAL_VERIFIED,
                            domain=frag_data['domain'],
                            timestamp=frag_data.get('timestamp', time.time()),
                            metadata=frag_data.get('metadata', {})
                        ))
            
            if all_fragments:
                strategy_used = "LOCAL_DB"
        
        # Tier 3: Live Fetch Fallback
        if not all_fragments:
            logger.info(f"Local cache miss for '{query}', initiating Live Fetch...")
            strategy_used = "LIVE_FETCH"
            for domain in target_domains:
                api_response = self.api_client.fetch_knowledge(query, domain)
                if api_response.success and api_response.data:
                    # Assess credibility of the source
                    cred_report = self.assessor.assess_source_credibility(api_response.source_url)
                    
                    # Determine tier based on credibility
                    if cred_report.credibility_level == CredibilityLevel.HIGH:
                        tier = SourceTier.LOCAL_HIGH_CONFIDENCE
                    elif cred_report.credibility_level == CredibilityLevel.MEDIUM:
                        tier = SourceTier.LOCAL_VERIFIED
                    else:
                        tier = SourceTier.LIVE_FETCH
                    
                    fragment = KnowledgeFragment(
                        content=str(api_response.data),
                        source_url=api_response.source_url,
                        confidence_score=0.85 if api_response.success else 0.5,
                        tier=tier,
                        domain=domain,
                        metadata={'provider': api_response.provider.value}
                    )
                    all_fragments.append(fragment)
                    
                    # Store in database for future use
                    self.db.store_fragment(
                        content=fragment.content,
                        source_url=fragment.source_url,
                        confidence_score=fragment.confidence_score,
                        tier=tier.name,
                        domain=domain,
                        metadata=fragment.metadata,
                        credibility_level=cred_report.credibility_level.value
                    )
                    
                    # Update source credibility in DB
                    self.db.update_source_credibility(
                        source_url=api_response.source_url,
                        credibility_level=cred_report.credibility_level.value,
                        score=cred_report.score,
                        factors=cred_report.factors
                    )

        # 3. Calculate Adaptive Confidence
        final_confidence = 0.0
        if all_fragments:
            # Weighted average confidence
            total_weight = 0
            weighted_sum = 0
            for frag in all_fragments:
                calibrated_score = self.calibrator.calibrate(frag.confidence_score, frag.domain, frag.tier)
                frag.confidence_score = calibrated_score # Update fragment with calibrated score
                weight = 1.0 if frag.tier == SourceTier.LOCAL_HIGH_CONFIDENCE else 0.8
                weighted_sum += calibrated_score * weight
                total_weight += weight
            
            final_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0

        # 4. Fusion (if cross-domain)
        final_answer = ""
        if is_cross_domain and len(all_fragments) > 1:
            final_answer = self.fusion_engine.fuse_fragments(all_fragments, query)
        else:
            final_answer = " ".join([f.content for f in all_fragments]) if all_fragments else "No data available."

        execution_time = (time.time() - start_time) * 1000

        # Cache the result for future queries
        if all_fragments:
            self.db.cache_result(query, {
                'fragments': [{
                    'content': f.content,
                    'source_url': f.source_url,
                    'confidence_score': f.confidence_score,
                    'tier': f.tier.name,
                    'domain': f.domain,
                    'timestamp': f.timestamp,
                    'metadata': f.metadata
                } for f in all_fragments],
                'answer': final_answer,
                'confidence': final_confidence
            }, target_domains[0] if target_domains else "General")
        
        # Record metrics
        self.db.record_metric('query_latency', target_domains[0] if target_domains else "General", execution_time)
        for domain in target_domains:
            self.assessor.record_domain_usage(domain)

        return OrchestratorResult(
            answer=final_answer,
            confidence=final_confidence,
            sources=[f.source_url for f in all_fragments],
            execution_time_ms=execution_time,
            strategy_used=strategy_used,
            cross_domain_fusion=is_cross_domain
        )

    def submit_feedback(self, query_id: str, domain: str, was_accurate: bool, 
                        user_rating: int = None, comments: str = None):
        """Submit user feedback for adaptive learning."""
        self.db.store_feedback(query_id, domain, was_accurate, user_rating, comments)
        self.calibrator.record_feedback(domain, was_accurate)

    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics from database."""
        return self.db.get_metrics_summary(hours=24)


# Singleton instance
_orchestrator_instance: Optional[UnifiedKnowledgeOrchestrator] = None

def get_orchestrator(db_path: str = None, api_keys: Dict[str, str] = None) -> UnifiedKnowledgeOrchestrator:
    """Get or create the unified orchestrator singleton."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = UnifiedKnowledgeOrchestrator(db_path, api_keys)
    return _orchestrator_instance
