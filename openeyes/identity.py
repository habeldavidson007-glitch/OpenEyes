"""
OpenEyes Identity Module: Agentic Intent

Phase 4 of Autonomous Cognitive Engine: "The Subject"

This module gives OpenEyes a "personality" or "intent" that influences
how it processes queries and weights Monte Carlo simulations.

Available Identities:
- ANALYTICAL: Focus on data, statistics, logical rigor
- CRITICAL: Seeks counter-arguments, skeptical of claims
- CREATIVE: Explores novel connections, cross-domain synthesis
- PRAGMATIC: Action-oriented, practical solutions focus
- CONSERVATIVE: Risk-averse, prioritizes established knowledge
- EXPLORATORY: Open to new hypotheses, higher risk tolerance

The identity affects:
- Fragment weighting in Monte Carlo
- Question refinement strategy
- Narrative tone and structure
- Evidence threshold requirements
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass


class IdentityType(Enum):
    """Available system identities."""
    ANALYTICAL = "analytical"
    CRITICAL = "critical"
    CREATIVE = "creative"
    PRAGMATIC = "pragmatic"
    CONSERVATIVE = "conservative"
    EXPLORATORY = "exploratory"


@dataclass
class IdentityConfig:
    """Configuration for an identity type."""
    name: str
    description: str
    evidence_threshold: float  # Minimum evidence level required
    risk_tolerance: float  # 0.0 = risk-averse, 1.0 = risk-seeking
    counter_argument_weight: float  # How much to weight opposing views
    novelty_bonus: float  # Bonus for novel/cross-domain connections
    narrative_style: str  # Tone of output
    
    # Monte Carlo parameters
    simulation_count: int  # Number of simulations to run
    variance_penalty: float  # Penalty for high-variance outcomes
    recency_bias: float  # Bias toward recent data (0.0 = no bias, 1.0 = strong bias)


# Predefined identity configurations
IDENTITY_PRESETS: Dict[IdentityType, IdentityConfig] = {
    IdentityType.ANALYTICAL: IdentityConfig(
        name="Analytical",
        description="Data-driven, statistically rigorous analysis",
        evidence_threshold=0.7,
        risk_tolerance=0.3,
        counter_argument_weight=0.5,
        novelty_bonus=0.1,
        narrative_style="objective",
        simulation_count=10000,
        variance_penalty=0.3,
        recency_bias=0.2,
    ),
    IdentityType.CRITICAL: IdentityConfig(
        name="Critical",
        description="Skeptical, seeks counter-arguments and weaknesses",
        evidence_threshold=0.8,
        risk_tolerance=0.2,
        counter_argument_weight=1.0,
        novelty_bonus=0.0,
        narrative_style="skeptical",
        simulation_count=15000,
        variance_penalty=0.5,
        recency_bias=0.1,
    ),
    IdentityType.CREATIVE: IdentityConfig(
        name="Creative",
        description="Explores novel connections across domains",
        evidence_threshold=0.5,
        risk_tolerance=0.6,
        counter_argument_weight=0.3,
        novelty_bonus=0.8,
        narrative_style="imaginative",
        simulation_count=8000,
        variance_penalty=0.1,
        recency_bias=0.4,
    ),
    IdentityType.PRAGMATIC: IdentityConfig(
        name="Pragmatic",
        description="Action-oriented, focuses on practical solutions",
        evidence_threshold=0.6,
        risk_tolerance=0.4,
        counter_argument_weight=0.4,
        novelty_bonus=0.2,
        narrative_style="actionable",
        simulation_count=5000,
        variance_penalty=0.2,
        recency_bias=0.5,
    ),
    IdentityType.CONSERVATIVE: IdentityConfig(
        name="Conservative",
        description="Risk-averse, prioritizes established knowledge",
        evidence_threshold=0.9,
        risk_tolerance=0.1,
        counter_argument_weight=0.6,
        novelty_bonus=0.0,
        narrative_style="cautious",
        simulation_count=20000,
        variance_penalty=0.7,
        recency_bias=0.0,
    ),
    IdentityType.EXPLORATORY: IdentityConfig(
        name="Exploratory",
        description="Open to hypotheses, higher risk tolerance",
        evidence_threshold=0.4,
        risk_tolerance=0.8,
        counter_argument_weight=0.2,
        novelty_bonus=0.6,
        narrative_style="speculative",
        simulation_count=6000,
        variance_penalty=0.1,
        recency_bias=0.6,
    ),
}


class IdentityEngine:
    """
    Manages system identity and applies identity-based weighting.
    
    This is the "Subject Module" that gives OpenEyes agentic intent.
    """
    
    def __init__(self, identity_type: IdentityType = IdentityType.ANALYTICAL):
        """
        Initialize with specified identity.
        
        Args:
            identity_type: The identity to adopt
        """
        self.identity_type = identity_type
        self.config = IDENTITY_PRESETS[identity_type]
        self.history: List[Dict[str, Any]] = []
    
    @classmethod
    def from_name(cls, name: str) -> "IdentityEngine":
        """Create identity engine from name string."""
        try:
            identity_type = IdentityType(name.lower())
            return cls(identity_type)
        except ValueError:
            print(f"[IDENTITY] Unknown identity '{name}', defaulting to ANALYTICAL")
            return cls(IdentityType.ANALYTICAL)
    
    def get_config(self) -> IdentityConfig:
        """Get current identity configuration."""
        return self.config
    
    def set_identity(self, identity_type: IdentityType) -> None:
        """Change system identity."""
        old_identity = self.identity_type
        self.identity_type = identity_type
        self.config = IDENTITY_PRESETS[identity_type]
        print(f"[IDENTITY] Changed from {old_identity.value} to {identity_type.value}")
    
    def apply_weight_to_fragment(self, fragment: Any) -> float:
        """
        Apply identity-based weight to a fragment.
        
        This modifies how fragments are scored in Monte Carlo simulations.
        
        Args:
            fragment: Fragment object to weight
            
        Returns:
            Weight multiplier (0.0 to 2.0)
        """
        base_weight = 1.0
        
        # Evidence threshold check
        evidence_map = {"high": 1.0, "moderate": 0.7, "low": 0.4}
        frag_evidence = getattr(fragment, 'evidence_level', 'low')
        evidence_score = evidence_map.get(frag_evidence, 0.5)
        
        if evidence_score < self.config.evidence_threshold:
            base_weight *= 0.5  # Penalize below-threshold evidence
        
        # Counter-argument bonus (for CRITICAL identity)
        claim_text = getattr(fragment, 'claim', '').lower()
        has_counter = any(word in claim_text for word in ['however', 'but', 'contrary', 'alternative', 'dispute'])
        if has_counter:
            base_weight *= (1.0 + self.config.counter_argument_weight)
        
        # Novelty bonus (for CREATIVE/EXPLORATORY identities)
        source_type = getattr(fragment, 'source_type', '')
        is_novel = source_type in ['preprint_verified', 'conference_paper']
        if is_novel:
            base_weight *= (1.0 + self.config.novelty_bonus)
        
        # Recency bias
        from datetime import datetime
        pub_date = getattr(fragment, 'published_on', '')
        if pub_date:
            try:
                pub_year = int(pub_date[:4])
                years_old = datetime.now().year - pub_year
                recency_factor = max(0.5, 1.0 - (years_old * 0.1))
                base_weight *= (1.0 + (recency_factor - 0.5) * self.config.recency_bias)
            except:
                pass
        
        return min(2.0, max(0.0, base_weight))
    
    def adjust_simulation_params(self, base_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust Monte Carlo parameters based on identity.
        
        Args:
            base_params: Default simulation parameters
            
        Returns:
            Adjusted parameters
        """
        adjusted = base_params.copy()
        adjusted['num_simulations'] = self.config.simulation_count
        adjusted['variance_penalty'] = self.config.variance_penalty
        return adjusted
    
    def format_narrative(self, content: str) -> str:
        """
        Format narrative according to identity style.
        
        Args:
            content: Raw narrative content
            
        Returns:
            Styled narrative
        """
        style_prefixes = {
            "objective": "Analysis:",
            "skeptical": "Critical Review:",
            "imaginative": "Exploration:",
            "actionable": "Action Plan:",
            "cautious": "Conservative Assessment:",
            "speculative": "Hypothesis:",
        }
        
        prefix = style_prefixes.get(self.config.narrative_style, "Analysis:")
        return f"{prefix}\n{content}"
    
    def record_decision(self, query: str, decision: Dict[str, Any]) -> None:
        """Record decision for identity learning."""
        self.history.append({
            "query": query,
            "decision": decision,
            "identity": self.identity_type.value,
            "timestamp": str(datetime.now()),
        })
        
        # Keep history manageable
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get identity summary and statistics."""
        return {
            "identity": self.identity_type.value,
            "description": self.config.description,
            "evidence_threshold": self.config.evidence_threshold,
            "risk_tolerance": self.config.risk_tolerance,
            "decisions_made": len(self.history),
        }


# Import datetime for timestamp
from datetime import datetime


# Convenience function
def create_identity(name: str) -> IdentityEngine:
    """Create an identity engine by name."""
    return IdentityEngine.from_name(name)


if __name__ == "__main__":
    # Test identity system
    print("Testing Identity System...\n")
    
    for identity_type in IdentityType:
        engine = IdentityEngine(identity_type)
        config = engine.get_config()
        print(f"{config.name}:")
        print(f"  {config.description}")
        print(f"  Evidence threshold: {config.evidence_threshold}")
        print(f"  Risk tolerance: {config.risk_tolerance}")
        print(f"  Simulations: {config.simulation_count}")
        print()
