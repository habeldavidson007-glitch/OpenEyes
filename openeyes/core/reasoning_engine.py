"""
OpenEyes 5-Stage Reasoning Engine

This module implements the 5-stage reasoning pipeline that processes
fragments through a "chemical reactor" to produce high-grade intelligence.

Stages:
1. Source Provenance & Weighting - Evaluate origin credibility
2. Cross-Domain Resonance Check - Identify inter-domain connections
3. Contradiction & Arbitrage Detection - Resolve conflicts, find inefficiencies
4. Temporal Decay & Regime Analysis - Apply time-based weighting
5. Synthesis & Actionability Scoring - Generate final response with scores
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openeyes.fragment_library import Fragment


@dataclass
class StageResult:
    """Result from a single reasoning stage."""
    stage_name: str
    inputs_processed: int
    outputs_generated: int
    confidence_delta: float  # Change in confidence from this stage
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ReasoningTrace:
    """Complete trace of the 5-stage reasoning process."""
    query: str
    domain: str
    initial_fragments: int
    final_fragments: int
    stages: List[StageResult] = field(default_factory=list)
    cross_domain_links: List[Dict[str, str]] = field(default_factory=list)
    contradictions_detected: List[Dict[str, Any]] = field(default_factory=list)
    temporal_adjustments: List[Dict[str, Any]] = field(default_factory=list)
    final_confidence: float = 0.0
    actionability_score: float = 0.0
    synthesis_summary: str = ""


class FiveStageReasoningEngine:
    """
    Implements the 5-stage reasoning pipeline for fragment processing.
    
    This engine transforms raw fragments into synthesized intelligence
    through sequential filtering, enrichment, and scoring stages.
    """
    
    # Economy sector codes for cross-domain mapping
    SECTOR_CODES = {
        "finance": "FIN",
        "energy": "ENR", 
        "commodities": "COM",
        "agriculture": "AGR",
        "macroeconomics": "MAC",
        "geopolitics": "GEO",
        "regulation": "REG"
    }
    
    # Sector proximity matrix (how closely related sectors are)
    SECTOR_PROXIMITY = {
        ("FIN", "MAC"): 0.9,
        ("FIN", "REG"): 0.8,
        ("ENR", "COM"): 0.9,
        ("ENR", "GEO"): 0.7,
        ("COM", "AGR"): 0.8,
        ("MAC", "GEO"): 0.7,
        ("FIN", "ENR"): 0.6,
        ("FIN", "COM"): 0.6,
    }
    
    def __init__(self):
        self.current_year = datetime.now().year
        
    def process(self, query: str, domain: str, fragments: List[Fragment]) -> ReasoningTrace:
        """
        Run all 5 stages of reasoning on input fragments.
        
        Args:
            query: Original user query
            domain: Domain context (economy sector)
            fragments: Input fragments from retrieval
            
        Returns:
            ReasoningTrace with complete processing history
        """
        trace = ReasoningTrace(
            query=query,
            domain=domain,
            initial_fragments=len(fragments),
            final_fragments=len(fragments)  # Initialize with same value, updated later
        )
        
        current_fragments = fragments.copy()
        
        # Stage 1: Source Provenance & Weighting
        stage1_result, current_fragments = self._stage1_provenance_weighting(
            current_fragments, trace
        )
        trace.stages.append(stage1_result)
        
        # Stage 2: Cross-Domain Resonance Check
        stage2_result, current_fragments = self._stage2_cross_domain_resonance(
            query, domain, current_fragments, trace
        )
        trace.stages.append(stage2_result)
        
        # Stage 3: Contradiction & Arbitrage Detection
        stage3_result, current_fragments = self._stage3_contradiction_arbitrage(
            query, current_fragments, trace
        )
        trace.stages.append(stage3_result)
        
        # Stage 4: Temporal Decay & Regime Analysis
        stage4_result, current_fragments = self._stage4_temporal_decay(
            current_fragments, trace
        )
        trace.stages.append(stage4_result)
        
        # Stage 5: Synthesis & Actionability Scoring
        stage5_result, final_confidence, actionability = self._stage5_synthesis_scoring(
            query, domain, current_fragments, trace
        )
        trace.stages.append(stage5_result)
        
        # Finalize trace
        trace.final_fragments = len(current_fragments)
        trace.final_confidence = final_confidence
        trace.actionability_score = actionability
        
        return trace
    
    def _stage1_provenance_weighting(
        self, 
        fragments: List[Fragment], 
        trace: ReasoningTrace
    ) -> Tuple[StageResult, List[Fragment]]:
        """
        Stage 1: Evaluate source credibility and assign trust weights.
        
        Filters out low-credibility sources and adjusts fragment weights
        based on source authority.
        """
        warnings = []
        filtered_fragments = []
        total_weight_adjustment = 0.0
        
        # Credibility baseline by source type
        credibility_baselines = {
            "government_source": 0.95,
            "central_bank": 0.95,
            "regulatory_agency": 0.92,
            "peer_reviewed_study": 0.88,
            "major_exchange": 0.90,
            "international_org": 0.88,
            "industry_report": 0.75,
            "news_media": 0.65,
            "blog": 0.40,
            "anecdotal": 0.30
        }
        
        for frag in fragments:
            source_type = getattr(frag, 'source_type', 'unknown')
            credibility_class = getattr(frag, 'credibility_class', 'anecdotal')
            
            # Get baseline credibility
            baseline = credibility_baselines.get(
                credibility_class, 
                credibility_baselines.get(source_type, 0.50)
            )
            
            # Adjust existing weight by credibility
            original_weight = getattr(frag, 'weight', 0.5)
            adjusted_weight = original_weight * baseline
            
            # Filter out very low credibility fragments
            if baseline < 0.35:
                frag_id = getattr(frag, 'id', getattr(frag, 'fragment_id', 'unknown'))
                warnings.append(
                    f"Fragment {frag_id} filtered: low credibility source ({baseline:.2f})"
                )
                continue
            
            # Store adjusted weight - use 'weight' attribute for Fragment objects
            original_weight = getattr(frag, 'weight', 0.5)
            adjusted_weight = original_weight * baseline
            
            if hasattr(frag, 'weight'):
                frag.weight = adjusted_weight
            else:
                frag.weight = adjusted_weight
                
            total_weight_adjustment += abs(adjusted_weight - original_weight)
            filtered_fragments.append(frag)
        
        avg_adjustment = (
            total_weight_adjustment / len(fragments) 
            if fragments else 0.0
        )
        
        result = StageResult(
            stage_name="Source Provenance & Weighting",
            inputs_processed=len(fragments),
            outputs_generated=len(filtered_fragments),
            confidence_delta=avg_adjustment * 0.1,  # Small confidence boost from filtering
            metadata={
                "avg_credibility_baseline": sum(
                    credibility_baselines.get(getattr(f, 'credibility_class', 'anecdotal'), 0.5) 
                    for f in filtered_fragments
                ) / max(1, len(filtered_fragments)),
                "filtered_count": len(fragments) - len(filtered_fragments)
            },
            warnings=warnings
        )
        
        return result, filtered_fragments
    
    def _stage2_cross_domain_resonance(
        self,
        query: str,
        domain: str,
        fragments: List[Fragment],
        trace: ReasoningTrace
    ) -> Tuple[StageResult, List[Fragment]]:
        """
        Stage 2: Identify connections between domains.
        
        Finds fragments that bridge multiple economic sectors,
        boosting their relevance for cross-domain synthesis.
        """
        warnings = []
        resonance_boosted = []
        cross_domain_links = []
        
        # Extract query sectors
        query_sectors = self._extract_sectors_from_query(query)
        
        for frag in fragments:
            frag_sectors = self._extract_sectors_from_fragment(frag)
            
            # Check for cross-domain connections
            resonance_score = 0.0
            connected_sectors = []
            
            for q_sector in query_sectors:
                for f_sector in frag_sectors:
                    # Check direct match
                    if q_sector == f_sector:
                        resonance_score += 1.0
                        connected_sectors.append((q_sector, f_sector, "direct"))
                    else:
                        # Check proximity
                        proximity = self.SECTOR_PROXIMITY.get(
                            (q_sector, f_sector),
                            self.SECTOR_PROXIMITY.get((f_sector, q_sector), 0.0)
                        )
                        if proximity > 0.5:
                            resonance_score += proximity
                            connected_sectors.append((q_sector, f_sector, f"proximity:{proximity:.2f}"))
            
            # Boost fragments with cross-domain resonance
            if resonance_score > 1.0:
                original_weight = getattr(frag, 'weight', 0.5)
                boost_factor = min(2.0, 1.0 + (resonance_score - 1.0) * 0.3)
                frag.weight = getattr(frag, 'weight', 0.5) * boost_factor
                
                cross_domain_links.extend([{
                    "fragment_id": getattr(frag, "source_id", "unknown"),
                    "sector_pair": f"{q}->{f}",
                    "connection_type": t,
                    "query": query[:50]
                } for q, f, t in connected_sectors if q != f])
                
                resonance_boosted.append(frag)
            else:
                resonance_boosted.append(frag)
        
        # Store cross-domain links in trace
        trace.cross_domain_links.extend(cross_domain_links[:10])  # Limit to top 10
        
        result = StageResult(
            stage_name="Cross-Domain Resonance Check",
            inputs_processed=len(fragments),
            outputs_generated=len(resonance_boosted),
            confidence_delta=0.05 * min(1.0, len(cross_domain_links) / 5.0),
            metadata={
                "cross_domain_fragments": len(resonance_boosted),
                "total_links_found": len(cross_domain_links),
                "query_sectors": list(query_sectors)
            },
            warnings=warnings
        )
        
        return result, resonance_boosted
    
    def _stage3_contradiction_arbitrage(
        self,
        query: str,
        fragments: List[Fragment],
        trace: ReasoningTrace
    ) -> Tuple[StageResult, List[Fragment]]:
        """
        Stage 3: Detect contradictions and identify arbitrage opportunities.
        
        Finds conflicting claims between fragments and either resolves them
        or flags them as market inefficiencies/uncertainties.
        """
        warnings = []
        resolved_fragments = []
        contradictions = []
        
        # Group fragments by claim topic
        claim_groups: Dict[str, List[Fragment]] = {}
        for frag in fragments:
            content = getattr(frag, 'content', '') or getattr(frag, 'claim', '')
            topic = self._extract_claim_topic(content, query)
            if topic not in claim_groups:
                claim_groups[topic] = []
            claim_groups[topic].append(frag)
        
        # Check each group for contradictions
        for topic, group in claim_groups.items():
            if len(group) < 2:
                resolved_fragments.extend(group)
                continue
            
            # Look for contradictory language
            positive_claims = []
            negative_claims = []
            
            for frag in group:
                content = getattr(frag, 'content', '') or getattr(frag, 'claim', '')
                if self._is_positive_claim(content):
                    positive_claims.append(frag)
                elif self._is_negative_claim(content):
                    negative_claims.append(frag)
                else:
                    resolved_fragments.append(frag)
            
            # If we have both positive and negative claims, mark contradiction
            if positive_claims and negative_claims:
                contradictions.append({
                    "topic": topic,
                    "positive_count": len(positive_claims),
                    "negative_count": len(negative_claims),
                    "resolution": "weighted_consensus",
                    "fragments_involved": [getattr(f, 'source_id', 'unknown') for f in group]
                })
                
                # Apply weighted consensus - higher credibility wins more weight
                all_claims = positive_claims + negative_claims
                for frag in all_claims:
                    cred = getattr(frag, 'weight', 0.5)
                    # Slightly reduce weight for contradictory claims
                    frag.weight = cred * 0.9
                    
                resolved_fragments.extend(all_claims)
                warnings.append(
                    f"Contradiction detected on '{topic}': "
                    f"{len(positive_claims)} vs {len(negative_claims)} claims"
                )
            else:
                resolved_fragments.extend(group)
        
        trace.contradictions_detected = contradictions[:5]  # Limit to top 5
        
        result = StageResult(
            stage_name="Contradiction & Arbitrage Detection",
            inputs_processed=len(fragments),
            outputs_generated=len(resolved_fragments),
            confidence_delta=-0.03 * len(contradictions),  # Reduce confidence for contradictions
            metadata={
                "contradictions_found": len(contradictions),
                "topics_with_conflicts": [c["topic"] for c in contradictions]
            },
            warnings=warnings
        )
        
        return result, resolved_fragments
    
    def _stage4_temporal_decay(
        self,
        fragments: List[Fragment],
        trace: ReasoningTrace
    ) -> Tuple[StageResult, List[Fragment]]:
        """
        Stage 4: Apply temporal decay based on fragment age and market regime.
        
        Older fragments lose weight unless they represent timeless principles.
        Current market regime affects decay rates.
        """
        warnings = []
        temporally_adjusted = []
        adjustments = []
        
        # Decay rates by content type
        decay_rates = {
            "market_data": 0.15,  # Fast decay - markets change quickly
            "economic_indicator": 0.10,  # Medium decay
            "regulation": 0.05,  # Slow decay - regulations stable
            "principle": 0.01,  # Very slow - timeless
            "definition": 0.01,  # Very slow - definitions stable
            "historical_event": 0.02  # Slow - history doesn't change
        }
        
        current_year = self.current_year
        
        for frag in fragments:
            # Get publication year
            published = getattr(frag, 'published_on', '')
            year = None
            if isinstance(published, str) and len(published) >= 4:
                try:
                    year = int(published[:4])
                except ValueError:
                    pass
            
            if year is None:
                year = getattr(frag, 'year', current_year)
            
            # Calculate age
            age = current_year - year
            
            # Determine content type for decay rate
            tags = getattr(frag, 'tags', [])
            content_type = "principle"  # Default
            
            if any(t in tags for t in ["price", "market_data", "trading"]):
                content_type = "market_data"
            elif any(t in tags for t in ["gdp", "inflation", "employment"]):
                content_type = "economic_indicator"
            elif any(t in tags for t in ["regulation", "policy", "law"]):
                content_type = "regulation"
            elif any(t in tags for t in ["definition", "concept"]):
                content_type = "definition"
            
            decay_rate = decay_rates.get(content_type, 0.05)
            
            # Apply exponential decay
            decay_factor = max(0.3, (1 - decay_rate) ** age)
            
            original_weight = getattr(frag, 'weight', 0.5)
            adjusted_weight = original_weight * decay_factor
            
            if age > 0 and decay_factor < 1.0:
                adjustments.append({
                    "fragment_id": getattr(frag, 'source_id', 'unknown'),
                    "age_years": age,
                    "content_type": content_type,
                    "decay_factor": decay_factor,
                    "original_weight": original_weight,
                    "adjusted_weight": adjusted_weight
                })
            
            frag.weight = adjusted_weight
            temporally_adjusted.append(frag)
        
        trace.temporal_adjustments = adjustments[:10]  # Limit to top 10
        
        avg_decay = (
            sum(a["decay_factor"] for a in adjustments) / len(adjustments)
            if adjustments else 1.0
        )
        
        result = StageResult(
            stage_name="Temporal Decay & Regime Analysis",
            inputs_processed=len(fragments),
            outputs_generated=len(temporally_adjusted),
            confidence_delta=0.02 * (1.0 - avg_decay),  # Small boost from recency
            metadata={
                "avg_age_years": sum(a["age_years"] for a in adjustments) / max(1, len(adjustments)),
                "avg_decay_factor": avg_decay,
                "oldest_fragment_age": max((a["age_years"] for a in adjustments), default=0)
            },
            warnings=warnings
        )
        
        return result, temporally_adjusted
    
    def _stage5_synthesis_scoring(
        self,
        query: str,
        domain: str,
        fragments: List[Fragment],
        trace: ReasoningTrace
    ) -> Tuple[StageResult, float, float]:
        """
        Stage 5: Generate final synthesis with actionability score.
        
        Combines all previous stages to produce final confidence
        and actionability metrics.
        """
        warnings = []
        
        if not fragments:
            return StageResult(
                stage_name="Synthesis & Actionability Scoring",
                inputs_processed=0,
                outputs_generated=0,
                confidence_delta=0.0,
                metadata={"reason": "no_fragments"},
                warnings=["No fragments available for synthesis"]
            ), 0.0, 0.0
        
        # Calculate final confidence from fragment weights
        total_weight = sum(getattr(f, 'effective_weight', 0.5) for f in fragments)
        avg_weight = total_weight / len(fragments)
        
        # Diversity bonus: more unique sources = higher confidence
        unique_sources = len(set(getattr(f, 'source_id', '') for f in fragments))
        diversity_bonus = min(0.15, unique_sources * 0.03)
        
        # Cross-domain bonus
        cross_domain_bonus = min(0.10, len(trace.cross_domain_links) * 0.02)
        
        # Contradiction penalty
        contradiction_penalty = len(trace.contradictions_detected) * 0.05
        
        # Final confidence calculation
        base_confidence = avg_weight * 100  # Convert to percentage
        final_confidence = min(99.0, base_confidence + (diversity_bonus + cross_domain_bonus - contradiction_penalty) * 100)
        
        # Calculate actionability score
        # Actionability depends on: specificity, recency, and source authority
        actionability_factors = []
        
        for frag in fragments:
            content = getattr(frag, 'content', '') or getattr(frag, 'claim', '')
            
            # Specificity: does it contain numbers, percentages, specific entities?
            has_numbers = bool(re.search(r'\d+(?:\.\d+)?%?', content))
            has_entities = bool(re.search(r'\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+\b', content))
            specificity_score = (0.4 if has_numbers else 0.0) + (0.3 if has_entities else 0.0)
            
            # Recency factor from temporal adjustments
            recency_factor = 1.0
            frag_id = getattr(frag, 'source_id', 'unknown')
            for adj in trace.temporal_adjustments:
                if adj["fragment_id"] == frag_id:
                    recency_factor = adj["decay_factor"]
                    break
            
            # Authority from provenance
            authority = getattr(frag, 'effective_weight', 0.5)
            
            actionability = specificity_score * recency_factor * authority
            actionability_factors.append(actionability)
        
        avg_actionability = sum(actionability_factors) / len(actionability_factors) if actionability_factors else 0.0
        actionability_score = min(1.0, avg_actionability * 1.5)  # Scale to 0-1
        
        # Generate synthesis summary
        synthesis_parts = []
        if fragments:
            top_frag = max(fragments, key=lambda f: getattr(f, 'effective_weight', 0.5))
            content = getattr(top_frag, 'content', '') or getattr(top_frag, 'claim', '')
            synthesis_parts.append(content[:200])
        
        synthesis_summary = " | ".join(synthesis_parts) if synthesis_parts else "No synthesis possible"
        
        result = StageResult(
            stage_name="Synthesis & Actionability Scoring",
            inputs_processed=len(fragments),
            outputs_generated=1,  # One synthesized answer
            confidence_delta=(final_confidence - 50.0) / 100.0,  # Delta from baseline
            metadata={
                "fragment_count": len(fragments),
                "unique_sources": unique_sources,
                "diversity_bonus": diversity_bonus,
                "cross_domain_bonus": cross_domain_bonus,
                "contradiction_penalty": contradiction_penalty,
                "actionability_score": actionability_score
            },
            warnings=warnings
        )
        
        return result, final_confidence, actionability_score
    
    # Helper methods
    
    def _extract_sectors_from_query(self, query: str) -> set:
        """Extract economy sector codes from query text."""
        query_lower = query.lower()
        sectors = set()
        
        sector_keywords = {
            "FIN": ["finance", "financial", "bank", "stock", "market", "investment", "trading"],
            "ENR": ["energy", "oil", "gas", "power", "electricity", "renewable", "fuel"],
            "COM": ["commodity", "commodities", "metal", "gold", "silver", "copper", "mineral"],
            "AGR": ["agriculture", "farm", "crop", "food", "wheat", "corn", "livestock"],
            "MAC": ["macro", "economy", "gdp", "inflation", "employment", "interest rate"],
            "GEO": ["geopolitical", "trade war", "sanction", "conflict", "policy"],
            "REG": ["regulation", "sec", "fed", "central bank", "policy", "law"]
        }
        
        for sector, keywords in sector_keywords.items():
            if any(kw in query_lower for kw in keywords):
                sectors.add(sector)
        
        return sectors if sectors else {"FIN"}  # Default to finance
    
    def _extract_sectors_from_fragment(self, frag: Fragment) -> set:
        """Extract economy sector codes from fragment tags/domain."""
        sectors = set()
        
        # Check domain
        domain = getattr(frag, 'domain', '').lower()
        for sector_code, sector_name in self.SECTOR_CODES.items():
            if sector_name.lower() in domain or sector_code.lower() in domain:
                sectors.add(sector_code)
        
        # Check tags
        tags = getattr(frag, 'tags', [])
        for tag in tags:
            tag_lower = tag.lower()
            for sector_code, sector_name in self.SECTOR_CODES.items():
                if sector_name.lower() in tag_lower or sector_code.lower() in tag_lower:
                    sectors.add(sector_code)
        
        return sectors if sectors else {"FIN"}  # Default to finance
    
    def _extract_claim_topic(self, content: str, query: str) -> str:
        """Extract main topic from a claim/content."""
        # Simple extraction: first noun phrase or key entity
        content_lower = content.lower() if content else ""
        query_lower = query.lower()
        
        # Try to find query keywords in content
        for word in query_lower.split():
            if len(word) > 3 and word in content_lower:
                return word
        
        # Fallback: first few words
        return content[:30].strip() if content else "unknown"
    
    def _is_positive_claim(self, content: str) -> bool:
        """Check if content expresses a positive claim."""
        positive_indicators = [
            "increases", "rises", "grows", "improves", "benefits",
            "positive", "gain", "profit", "upward", "bullish"
        ]
        content_lower = content.lower()
        return any(ind in content_lower for ind in positive_indicators)
    
    def _is_negative_claim(self, content: str) -> bool:
        """Check if content expresses a negative claim."""
        negative_indicators = [
            "decreases", "falls", "declines", "worsens", "harms",
            "negative", "loss", "downward", "bearish", "risk"
        ]
        content_lower = content.lower()
        return any(ind in content_lower for ind in negative_indicators)


# Singleton instance
_reasoning_engine: Optional[FiveStageReasoningEngine] = None


def get_reasoning_engine() -> FiveStageReasoningEngine:
    """Get or create the singleton reasoning engine instance."""
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = FiveStageReasoningEngine()
    return _reasoning_engine
