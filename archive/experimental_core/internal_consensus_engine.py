"""
Internal Consensus Engine - Multi-path derivation with confidence boosting

This module runs multiple independent derivation paths for the same query.
If paths converge on similar conclusions, it automatically boosts the
Evidence Level to High, implementing "Self-Trust" through mathematical consistency.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set
from enum import Enum
import hashlib
import json


class DerivationMethod(Enum):
    """Methods for deriving conclusions."""
    AXIOMATIC = "axiomatic"  # From first principles axioms
    CROSS_DOMAIN = "cross_domain"  # Via analogy to other domains
    LIVE_FETCH = "live_fetch"  # From live web sources
    JIT_SYNTHESIS = "jit_synthesis"  # From JIT knowledge synthesis
    FRAGMENT_LIBRARY = "fragment_library"  # From stored fragments


@dataclass
class DerivationPath:
    """A single path of reasoning/derivation."""
    method: DerivationMethod
    source: str  # Source of the derivation (axiom ID, domain, URL, etc.)
    conclusion: str
    confidence: float
    supporting_evidence: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_signature(self) -> str:
        """Get a hash signature of the conclusion for comparison."""
        # Normalize conclusion for comparison
        normalized = self.conclusion.lower().strip()
        # Remove common filler words
        filler_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being"}
        words = [w for w in normalized.split() if w not in filler_words]
        normalized = " ".join(words)
        return hashlib.md5(normalized.encode()).hexdigest()[:16]


@dataclass
class ConsensusResult:
    """Result of consensus analysis across derivation paths."""
    query: str
    all_paths: List[DerivationPath]
    converged_paths: List[DerivationPath]
    divergent_paths: List[DerivationPath]
    consensus_score: float  # 0-1, how much paths agree
    boosted_confidence: float  # Final confidence after consensus
    evidence_level: str  # "low", "moderate", "high"
    final_conclusions: List[str]
    reasoning_trace: List[str]


class InternalConsensusEngine:
    """
    Engine for running multiple derivation paths and checking convergence.
    
    Implements "Self-Trust": if multiple independent methods arrive at
    similar conclusions, boost confidence automatically.
    """
    
    CONVERGENCE_THRESHOLD = 0.6  # Paths are considered convergent if similarity >= this
    CONFIDENCE_BOOST_FACTOR = 1.5  # Multiply confidence by this when consensus is strong
    MAX_CONFIDENCE = 0.98  # Cap confidence at this level
    
    def __init__(self):
        self.derivation_history: List[ConsensusResult] = []
    
    def run_multi_path_derivation(
        self,
        query: str,
        domain: str,
        available_methods: List[DerivationMethod],
        context: Optional[Dict[str, Any]] = None
    ) -> List[DerivationPath]:
        """
        Run multiple independent derivation paths for the same query.
        
        Args:
            query: The user's query
            domain: The domain of the query
            available_methods: Which derivation methods to try
            context: Additional context
            
        Returns:
            List of derivation paths from different methods
        """
        paths = []
        
        if context is None:
            context = {}
        
        # Run each available derivation method
        for method in available_methods:
            try:
                if method == DerivationMethod.AXIOMATIC:
                    path = self._derive_axiomatic(query, domain, context)
                elif method == DerivationMethod.CROSS_DOMAIN:
                    path = self._derive_cross_domain(query, domain, context)
                elif method == DerivationMethod.LIVE_FETCH:
                    path = self._derive_live_fetch(query, domain, context)
                elif method == DerivationMethod.JIT_SYNTHESIS:
                    path = self._derive_jit_synthesis(query, domain, context)
                elif method == DerivationMethod.FRAGMENT_LIBRARY:
                    path = self._derive_fragment_library(query, domain, context)
                else:
                    continue
                
                if path:
                    paths.append(path)
            except Exception as e:
                # Log error but continue with other methods
                pass
        
        return paths
    
    def _derive_axiomatic(self, query: str, domain: str, context: Dict[str, Any]) -> Optional[DerivationPath]:
        """Derive conclusion using axiomatic first principles."""
        try:
            from .axioms import generate_first_principles_explanation
            
            result = generate_first_principles_explanation(query, domain, context)
            
            if not result.get("derived_facts"):
                return None
            
            # Combine derived facts into conclusion
            facts = result["derived_facts"]
            conclusion_parts = [f["statement"] for f in facts]
            conclusion = "; ".join(conclusion_parts)
            
            # Calculate average confidence
            avg_confidence = sum(f.get("confidence", 0.5) for f in facts) / len(facts)
            
            return DerivationPath(
                method=DerivationMethod.AXIOMATIC,
                source=f"axioms:{domain}",
                conclusion=conclusion,
                confidence=avg_confidence * result.get("confidence", 1.0),
                supporting_evidence=facts,
                metadata={
                    "axioms_applied": result.get("axioms_applied", 0),
                    "methodology": result.get("methodology", "first_principles")
                }
            )
        except ImportError:
            return None
        except Exception:
            return None
    
    def _derive_cross_domain(self, query: str, domain: str, context: Dict[str, Any]) -> Optional[DerivationPath]:
        """Derive conclusion using cross-domain analogy."""
        try:
            from .cross_domain_mapper import apply_cross_domain_reasoning, get_analogous_domains
            
            # Strong domains that OpenEyes knows well
            strong_domains = ["game_theory", "optimization", "network_theory", 
                            "information_theory", "causal_analysis", "mathematics"]
            forced_domains = context.get("force_cross_domain_domains", [])
            for forced_domain in forced_domains:
                if forced_domain not in strong_domains:
                    strong_domains.insert(0, forced_domain)
            
            result = apply_cross_domain_reasoning(query, domain, strong_domains)
            
            if not result.get("success"):
                return None
            
            # Build conclusion from translation
            translated_concepts = result.get("translated_concepts", [])
            reasoning_hint = result.get("reasoning_hint", "")
            
            if not translated_concepts:
                return None
            
            # Create conclusion statement
            concept_pairs = [f"{c['original']}→{c['translated']}" for c in translated_concepts]
            conclusion = f"Via {result['translation_type']}: {', '.join(concept_pairs)}. {reasoning_hint[:200]}"
            
            # Confidence based on translation score and domain similarity
            base_confidence = 0.6 + result.get("confidence_boost", 0) * 0.3
            
            return DerivationPath(
                method=DerivationMethod.CROSS_DOMAIN,
                source=f"cross_domain:{result['target_domain']}",
                conclusion=conclusion,
                confidence=min(base_confidence, 0.9),
                supporting_evidence=[{
                    "source_domain": result["source_domain"],
                    "target_domain": result["target_domain"],
                    "examples": result.get("examples", [])
                }],
                metadata=result
            )
        except ImportError:
            return None
        except Exception:
            return None
    
    def _derive_live_fetch(self, query: str, domain: str, context: Dict[str, Any]) -> Optional[DerivationPath]:
        """Derive conclusion from live web fetching."""
        try:
            from ..knowledge.live_fetch import fetch_live_fragments
            
            fragments = fetch_live_fragments(query, domain)
            
            if not fragments or len(fragments) == 0:
                return None
            
            # Extract key information from fragments
            conclusions = []
            total_confidence = 0.0
            
            for frag in fragments[:5]:  # Limit to top 5 fragments
                if hasattr(frag, 'content'):
                    content = frag.content if isinstance(frag.content, str) else str(frag.content)
                    conclusions.append(content[:200])  # Truncate
                elif isinstance(frag, dict) and 'content' in frag:
                    conclusions.append(str(frag['content'])[:200])
                
                # Estimate confidence from fragment evidence level
                evidence = getattr(frag, 'evidence_level', 'moderate')
                conf_map = {'high': 0.9, 'moderate': 0.7, 'low': 0.5}
                total_confidence += conf_map.get(evidence, 0.6)
            
            if not conclusions:
                return None
            
            avg_confidence = total_confidence / len(conclusions)
            conclusion = "; ".join(conclusions[:3])  # Top 3 conclusions
            
            return DerivationPath(
                method=DerivationMethod.LIVE_FETCH,
                source="live_web",
                conclusion=conclusion,
                confidence=avg_confidence,
                supporting_evidence=[{"fragment_count": len(fragments)}],
                metadata={"domains_searched": [domain]}
            )
        except ImportError:
            return None
        except Exception:
            return None
    
    def _derive_jit_synthesis(self, query: str, domain: str, context: Dict[str, Any]) -> Optional[DerivationPath]:
        """Derive conclusion from JIT synthesis."""
        try:
            from ..knowledge.live_fetch import jit_synthesize_fragments
            
            fragments = jit_synthesize_fragments(query, domain)
            
            if not fragments or len(fragments) == 0:
                return None
            
            # Extract synthesized knowledge
            conclusions = []
            total_confidence = 0.0
            
            for frag in fragments[:5]:
                if hasattr(frag, 'content'):
                    content = frag.content if isinstance(frag.content, str) else str(frag.content)
                    conclusions.append(content[:200])
                elif isinstance(frag, dict) and 'content' in frag:
                    conclusions.append(str(frag['content'])[:200])
                
                # JIT synthesis has moderate-high confidence if consistent
                total_confidence += 0.75
            
            if not conclusions:
                return None
            
            avg_confidence = total_confidence / len(conclusions)
            conclusion = "; ".join(conclusions[:3])
            
            return DerivationPath(
                method=DerivationMethod.JIT_SYNTHESIS,
                source=f"jit:{domain}",
                conclusion=conclusion,
                confidence=avg_confidence,
                supporting_evidence=[{"synthesized_fragments": len(fragments)}],
                metadata={"domain": domain}
            )
        except ImportError:
            return None
        except Exception:
            return None
    
    def _derive_fragment_library(self, query: str, domain: str, context: Dict[str, Any]) -> Optional[DerivationPath]:
        """Derive conclusion from existing fragment library."""
        try:
            from ..binary_lib import BinaryLib
            
            lib = BinaryLib()
            
            # Search for relevant fragments
            fragments = lib.search(query, domain=domain, limit=5)
            
            if not fragments or len(fragments) == 0:
                return None
            
            conclusions = []
            total_confidence = 0.0
            
            for frag in fragments:
                content = str(getattr(frag, 'content', frag))[:200]
                conclusions.append(content)
                
                # Get confidence from fragment CES or evidence level
                ces = getattr(frag, 'ces', 0.5)
                evidence = getattr(frag, 'evidence_level', 'moderate')
                conf_map = {'high': 0.9, 'moderate': 0.7, 'low': 0.5}
                conf = max(ces, conf_map.get(evidence, 0.6))
                total_confidence += conf
            
            avg_confidence = total_confidence / len(conclusions)
            conclusion = "; ".join(conclusions[:3])
            
            return DerivationPath(
                method=DerivationMethod.FRAGMENT_LIBRARY,
                source="binary_library",
                conclusion=conclusion,
                confidence=avg_confidence,
                supporting_evidence=[{"fragment_count": len(fragments)}],
                metadata={"domain": domain}
            )
        except ImportError:
            return None
        except Exception:
            return None
    
    def calculate_consensus(self, paths: List[DerivationPath]) -> Tuple[List[DerivationPath], List[DerivationPath], float]:
        """
        Calculate consensus among derivation paths.
        
        Returns:
            Tuple of (converged_paths, divergent_paths, consensus_score)
        """
        if len(paths) < 2:
            # Can't calculate consensus with less than 2 paths
            return paths, [], 0.0 if not paths else 1.0
        
        # Group paths by conclusion signature
        signature_groups: Dict[str, List[DerivationPath]] = {}
        
        for path in paths:
            sig = path.get_signature()
            if sig not in signature_groups:
                signature_groups[sig] = []
            signature_groups[sig].append(path)
        
        # Find the largest group (main consensus)
        if not signature_groups:
            return [], paths, 0.0
        
        main_group = max(signature_groups.values(), key=len)
        converged = main_group
        divergent = [p for p in paths if p not in converged]
        
        # Calculate consensus score
        consensus_score = len(converged) / len(paths)
        
        # Also check semantic similarity between conclusions
        if len(converged) > 1:
            # Boost score if conclusions are semantically similar
            semantic_bonus = self._calculate_semantic_similarity(converged) * 0.2
            consensus_score = min(consensus_score + semantic_bonus, 1.0)
        
        return converged, divergent, consensus_score
    
    def _calculate_semantic_similarity(self, paths: List[DerivationPath]) -> float:
        """Calculate semantic similarity between path conclusions."""
        if len(paths) < 2:
            return 1.0
        
        # Simple word overlap similarity
        conclusions = []
        for path in paths:
            words = set(path.conclusion.lower().split())
            # Remove stopwords
            stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been", 
                        "being", "and", "or", "but", "in", "on", "at", "to", "for"}
            words = words - stopwords
            conclusions.append(words)
        
        # Calculate average pairwise Jaccard similarity
        total_similarity = 0.0
        pair_count = 0
        
        for i in range(len(conclusions)):
            for j in range(i + 1, len(conclusions)):
                intersection = len(conclusions[i] & conclusions[j])
                union = len(conclusions[i] | conclusions[j])
                if union > 0:
                    total_similarity += intersection / union
                    pair_count += 1
        
        return total_similarity / pair_count if pair_count > 0 else 0.0
    
    def determine_evidence_level(self, consensus_score: float, avg_confidence: float, path_count: int) -> str:
        """Determine evidence level based on consensus and confidence."""
        # High evidence: strong consensus (>0.7) with multiple paths (>=2) and good confidence (>0.7)
        if consensus_score >= 0.7 and path_count >= 2 and avg_confidence >= 0.7:
            return "high"
        
        # Moderate evidence: some consensus (>0.5) or high confidence from single path
        if consensus_score >= 0.5 or (path_count == 1 and avg_confidence >= 0.75):
            return "moderate"
        
        # Low evidence otherwise
        return "low"
    
    def analyze_consensus(
        self,
        query: str,
        paths: List[DerivationPath]
    ) -> ConsensusResult:
        """
        Perform full consensus analysis on derivation paths.
        
        Args:
            query: The original query
            paths: List of derivation paths from different methods
            
        Returns:
            ConsensusResult with full analysis
        """
        # Calculate consensus
        converged, divergent, consensus_score = self.calculate_consensus(paths)
        
        # Calculate average confidence
        if paths:
            avg_confidence = sum(p.confidence for p in paths) / len(paths)
        else:
            avg_confidence = 0.0
        
        # Apply confidence boost if consensus is strong
        if consensus_score >= self.CONVERGENCE_THRESHOLD:
            boosted_confidence = min(avg_confidence * self.CONFIDENCE_BOOST_FACTOR, self.MAX_CONFIDENCE)
        else:
            boosted_confidence = avg_confidence
        
        # Determine evidence level
        evidence_level = self.determine_evidence_level(consensus_score, boosted_confidence, len(paths))
        
        # Extract final conclusions from converged paths
        final_conclusions = list(set(p.conclusion for p in converged))
        
        # Build reasoning trace
        reasoning_trace = []
        reasoning_trace.append(f"Analyzed {len(paths)} derivation paths")
        reasoning_trace.append(f"Convergence score: {consensus_score:.2f}")
        if converged:
            methods = list(set(p.method.value for p in converged))
            reasoning_trace.append(f"Converged methods: {', '.join(methods)}")
        if divergent:
            reasoning_trace.append(f"{len(divergent)} divergent path(s) found")
        reasoning_trace.append(f"Evidence level: {evidence_level}")
        reasoning_trace.append(f"Boosted confidence: {boosted_confidence:.2f}")
        
        result = ConsensusResult(
            query=query,
            all_paths=paths,
            converged_paths=converged,
            divergent_paths=divergent,
            consensus_score=consensus_score,
            boosted_confidence=boosted_confidence,
            evidence_level=evidence_level,
            final_conclusions=final_conclusions,
            reasoning_trace=reasoning_trace
        )
        
        # Store in history
        self.derivation_history.append(result)
        
        return result


def run_consensus_analysis(
    query: str,
    domain: str,
    context: Optional[Dict[str, Any]] = None
) -> ConsensusResult:
    """
    Convenience function to run full consensus analysis.
    
    Args:
        query: The user's query
        domain: The domain of the query
        context: Additional context
        
    Returns:
        ConsensusResult with analysis
    """
    engine = InternalConsensusEngine()
    
    # Try all available derivation methods
    available_methods = [
        DerivationMethod.AXIOMATIC,
        DerivationMethod.CROSS_DOMAIN,
        DerivationMethod.JIT_SYNTHESIS,
        DerivationMethod.LIVE_FETCH,
        DerivationMethod.FRAGMENT_LIBRARY
    ]
    
    # Run multi-path derivation
    paths = engine.run_multi_path_derivation(query, domain, available_methods, context)
    
    # Analyze consensus
    result = engine.analyze_consensus(query, paths)
    
    return result
