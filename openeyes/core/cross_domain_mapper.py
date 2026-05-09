"""
Cross-Domain Mapper - Translating concepts between domains using explicit rules

This module enables OpenEyes to answer questions in one domain by borrowing
logic and frameworks from analogous domains it understands better.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set
from enum import Enum


class TranslationType(Enum):
    """Types of cross-domain translations."""
    ANALOGY = "analogy"  # Direct analogy (A is like B)
    ISOMORPHISM = "isomorphism"  # Structural equivalence
    REDUCTION = "reduction"  # Domain A reduces to Domain B
    METAPHOR = "metaphor"  # Conceptual metaphor
    FORMALIZATION = "formalization"  # Informal concept -> formal math


@dataclass
class TranslationRule:
    """A rule for translating concepts between domains."""
    id: str
    source_domain: str
    target_domain: str
    translation_type: TranslationType
    concept_mapping: Dict[str, str]  # source_concept -> target_concept
    transformation_logic: str  # How to transform reasoning
    confidence_boost: float = 0.1  # Confidence added when translation succeeds
    examples: List[str] = field(default_factory=list)
    
    def translate_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Translate a query from source domain to target domain."""
        translated_context = context.copy()
        translated_concepts = []
        
        # Apply concept mappings
        for source_concept, target_concept in self.concept_mapping.items():
            if source_concept.lower() in query.lower():
                translated_concepts.append({
                    "original": source_concept,
                    "translated": target_concept,
                    "domain": self.target_domain
                })
                # Update context with translated concept
                if source_concept in context:
                    translated_context[target_concept] = context[source_concept]
        
        return {
            "rule_id": self.id,
            "translation_type": self.translation_type.value,
            "source_domain": self.source_domain,
            "target_domain": self.target_domain,
            "translated_concepts": translated_concepts,
            "new_context": translated_context,
            "transformation_hint": self.transformation_logic
        }


# ============================================================================
# CROSS-DOMAIN TRANSLATION RULES
# ============================================================================

CROSS_DOMAIN_RULES: List[TranslationRule] = [
    # ETHICS -> GAME THEORY
    TranslationRule(
        id="XDOM_001",
        source_domain="philosophy",
        target_domain="game_theory",
        translation_type=TranslationType.FORMALIZATION,
        concept_mapping={
            "utilitarianism": "utility_maximization",
            "moral_choice": "strategy_selection",
            "ethical_dilemma": "prisoners_dilemma",
            "virtue_ethics": "equilibrium_strategy",
            "deontology": "constrained_optimization",
            "consequentialism": "outcome_optimization",
            "moral_agent": "rational_player",
            "good": "high_utility",
            "bad": "low_utility"
        },
        transformation_logic="Convert ethical questions to game-theoretic models: identify players, strategies, payoffs, and find Nash equilibria. Utilitarian ethics maps directly to utility maximization problems.",
        confidence_boost=0.2,
        examples=[
            "Is lying wrong? -> Analyze as repeated prisoner's dilemma where trust is the resource",
            "What is justice? -> Find fair division solutions in cooperative game theory",
            "Should we maximize happiness? -> Utility maximization with constraints"
        ]
    ),
    
    # HISTORY -> CAUSAL GRAPHS + GAME THEORY
    TranslationRule(
        id="XDOM_002",
        source_domain="history",
        target_domain="causal_analysis",
        translation_type=TranslationType.REDUCTION,
        concept_mapping={
            "war": "resource_conflict_game",
            "revolution": "system_phase_transition",
            "empire": "hierarchical_control_system",
            "trade_route": "information_flow_network",
            "alliance": "cooperative_game_coalition",
            "treaty": "nash_equilibrium_agreement",
            "economic_crisis": "system_instability",
            "social_movement": "cascading_adoption_model"
        },
        transformation_logic="Model historical events as causal graphs with game-theoretic agent interactions. Wars are resource conflicts, revolutions are phase transitions, empires are control systems.",
        confidence_boost=0.15,
        examples=[
            "Why did WWI start? -> Analyze as multi-player game with alliance networks and escalation dynamics",
            "Fall of Rome? -> System instability from resource depletion + external pressure",
            "Industrial Revolution? -> Phase transition triggered by technology + capital accumulation"
        ]
    ),
    
    # HISTORY -> GAME THEORY (specific)
    TranslationRule(
        id="XDOM_003",
        source_domain="history",
        target_domain="game_theory",
        translation_type=TranslationType.ISOMORPHISM,
        concept_mapping={
            "cold_war": "iterated_prisoners_dilemma",
            "arms_race": "escalation_game",
            "diplomacy": "signaling_game",
            "colonization": "territorial_competition_game",
            "reform": "coordination_game"
        },
        transformation_logic="Historical geopolitical dynamics map to specific game theory models. Cold War = iterated PD with nuclear deterrence as punishment mechanism.",
        confidence_boost=0.2,
        examples=[
            "Cold War dynamics? -> Iterated prisoner's dilemma with mutually assured destruction",
            "Arms races? -> Escalation games with increasing costs",
            "Diplomatic negotiations? -> Signaling games with incomplete information"
        ]
    ),
    
    # LINGUISTICS -> INFORMATION THEORY
    TranslationRule(
        id="XDOM_004",
        source_domain="linguistics",
        target_domain="information_theory",
        translation_type=TranslationType.FORMALIZATION,
        concept_mapping={
            "grammar": "encoding_protocol",
            "meaning": "semantic_information",
            "ambiguity": "information_entropy",
            "language_evolution": "protocol_optimization",
            "syntax": "formal_grammar",
            "pragmatics": "contextual_decoding",
            "metaphor": "compression_algorithm",
            "translation": "cross_protocol_mapping"
        },
        transformation_logic="Model language as information transmission system. Grammar = encoding protocol, ambiguity = entropy, meaning = decoded information.",
        confidence_boost=0.15,
        examples=[
            "Why do languages simplify? -> Compression optimization for efficient transmission",
            "What is metaphor? -> Lossy compression that preserves essential meaning",
            "How does language evolve? -> Protocol optimization through selection pressure"
        ]
    ),
    
    # SOCIOLOGY -> NETWORK THEORY + GAME THEORY
    TranslationRule(
        id="XDOM_005",
        source_domain="sociology",
        target_domain="network_theory",
        translation_type=TranslationType.ISOMORPHISM,
        concept_mapping={
            "social_norm": "emergent_equilibrium",
            "social_class": "network_hierarchy",
            "social_capital": "network_centrality",
            "group_identity": "cluster_formation",
            "social_mobility": "network_rewiring",
            "institution": "stable_subgraph",
            "social_change": "phase_transition",
            "deviance": "outlier_detection"
        },
        transformation_logic="Model social structures as networks. Norms emerge from repeated interactions (equilibria), classes are hierarchical network positions, social capital is centrality measures.",
        confidence_boost=0.15,
        examples=[
            "Social stratification? -> Network hierarchy with limited bridging ties",
            "Spread of ideas? -> Cascade dynamics on social networks",
            "Social movements? -> Cluster formation and growth dynamics"
        ]
    ),
    
    # PSYCHOLOGY -> OPTIMIZATION + GAME THEORY
    TranslationRule(
        id="XDOM_006",
        source_domain="psychology",
        target_domain="optimization",
        translation_type=TranslationType.FORMALIZATION,
        concept_mapping={
            "motivation": "objective_function",
            "cognitive_bias": "heuristic_approximation",
            "decision_making": "constrained_optimization",
            "learning": "gradient_descent",
            "memory": "cache_system",
            "attention": "resource_allocation",
            "emotion": "value_signal",
            "personality": "parameter_configuration"
        },
        transformation_logic="Model psychological processes as computational/optimization systems. Motivation = objective function, biases = heuristics for fast approximation, learning = gradient descent on error surface.",
        confidence_boost=0.15,
        examples=[
            "Why do we have biases? -> Heuristics for fast approximate optimization under constraints",
            "How do we learn? -> Gradient descent minimizing prediction error",
            "What is motivation? -> Optimization of internal reward signals"
        ]
    ),
    
    # ECONOMICS -> PHYSICS (Thermodynamics analogy)
    TranslationRule(
        id="XDOM_007",
        source_domain="economics",
        target_domain="physics",
        translation_type=TranslationType.ANALOGY,
        concept_mapping={
            "money": "energy",
            "market": "thermodynamic_system",
            "price": "temperature",
            "supply_demand": "pressure_volume",
            "economic_equilibrium": "thermal_equilibrium",
            "inflation": "entropy_increase",
            "wealth_distribution": "energy_distribution",
            "market_crash": "phase_transition"
        },
        transformation_logic="Use thermodynamic analogies: money flows like energy, prices equilibrate like temperature, markets seek equilibrium like thermal systems, crashes are phase transitions.",
        confidence_boost=0.1,
        examples=[
            "Market equilibrium? -> Thermal equilibrium where supply/demand pressures balance",
            "Inflation? -> Entropy increase in monetary system",
            "Wealth inequality? -> Energy distribution following Boltzmann-like statistics"
        ]
    ),
    
    # BIOLOGY -> COMPUTER SCIENCE (Information processing)
    TranslationRule(
        id="XDOM_008",
        source_domain="biology",
        target_domain="computer_science",
        translation_type=TranslationType.ISOMORPHISM,
        concept_mapping={
            "dna": "source_code",
            "protein": "executable_program",
            "cell": "computing_unit",
            "metabolism": "runtime_process",
            "mutation": "code_modification",
            "natural_selection": "evolutionary_algorithm",
            "immune_system": "intrusion_detection",
            "neural_network": "machine_learning_model"
        },
        transformation_logic="Model biological systems as information processing systems. DNA = source code, cells = computing units, evolution = genetic algorithm optimizing fitness function.",
        confidence_boost=0.2,
        examples=[
            "How does evolution work? -> Genetic algorithm with mutation, crossover, and fitness selection",
            "What is DNA? -> Encoded instructions (source code) for building proteins (programs)",
            "Immune response? -> Pattern recognition and adaptive learning system"
        ]
    ),
    
    # POLITICAL SCIENCE -> GAME THEORY
    TranslationRule(
        id="XDOM_009",
        source_domain="political_science",
        target_domain="game_theory",
        translation_type=TranslationType.FORMALIZATION,
        concept_mapping={
            "voting": "preference_aggregation_game",
            "legislation": "coalition_formation",
            "international_relations": "multi_player_game",
            "power": "influence_in_network",
            "democracy": "repeated_voting_game",
            "authoritarianism": "centralized_control_game",
            "lobbying": "influence_peddling_game",
            "war": "conflict_game"
        },
        transformation_logic="Model political systems as games. Voting = preference aggregation, legislation = coalition building, international relations = multi-player strategic interactions.",
        confidence_boost=0.2,
        examples=[
            "Voting paradoxes? -> Arrow's impossibility theorem in social choice theory",
            "Coalition governments? -> Cooperative game theory with coalition stability analysis",
            "International conflicts? -> Multi-player games with alliance dynamics"
        ]
    ),
    
    # PHILOSOPHY (Metaphysics) -> LOGIC + SET THEORY
    TranslationRule(
        id="XDOM_010",
        source_domain="philosophy",
        target_domain="mathematics",
        translation_type=TranslationType.FORMALIZATION,
        concept_mapping={
            "existence": "set_membership",
            "identity": "equality_relation",
            "causality": "functional_mapping",
            "possibility": "modal_logic_operator",
            "necessity": "logical_necessity",
            "truth": "model_satisfaction",
            "property": "predicate",
            "substance": "fundamental_object"
        },
        transformation_logic="Formalize metaphysical concepts using mathematical logic. Existence = set membership, causality = function, modality = modal operators, truth = model satisfaction.",
        confidence_boost=0.15,
        examples=[
            "What exists? -> Define domain of discourse and membership criteria",
            "Nature of causality? -> Functional relationships between events",
            "Possible worlds? -> Modal logic semantics with accessibility relations"
        ]
    )
]


# ============================================================================
# DOMAIN SIMILARITY MATRIX
# ============================================================================

DOMAIN_SIMILARITY = {
    # Each entry: (domain1, domain2) -> similarity score (0-1)
    ("philosophy", "game_theory"): 0.85,
    ("philosophy", "mathematics"): 0.75,
    ("philosophy", "psychology"): 0.70,
    ("history", "game_theory"): 0.80,
    ("history", "causal_analysis"): 0.90,
    ("history", "sociology"): 0.75,
    ("sociology", "network_theory"): 0.90,
    ("sociology", "game_theory"): 0.80,
    ("psychology", "optimization"): 0.85,
    ("psychology", "game_theory"): 0.75,
    ("economics", "game_theory"): 0.95,
    ("economics", "physics"): 0.70,
    ("economics", "mathematics"): 0.85,
    ("biology", "computer_science"): 0.85,
    ("biology", "optimization"): 0.80,
    ("linguistics", "information_theory"): 0.90,
    ("linguistics", "computer_science"): 0.75,
    ("political_science", "game_theory"): 0.90,
    ("political_science", "sociology"): 0.80,
}


def get_translation_rules(source_domain: str, target_domain: str = None) -> List[TranslationRule]:
    """Get translation rules for a source domain, optionally filtered by target."""
    rules = [r for r in CROSS_DOMAIN_RULES if r.source_domain == source_domain]
    if target_domain:
        rules = [r for r in rules if r.target_domain == target_domain]
    return rules


def find_best_translation(query: str, source_domain: str, available_domains: List[str]) -> Optional[Dict[str, Any]]:
    """
    Find the best translation rule for a query from source domain to any available domain.
    
    Args:
        query: The user's query
        source_domain: The identified domain of the query
        available_domains: Domains where OpenEyes has strong knowledge
        
    Returns:
        Best translation rule and mapping, or None if no suitable translation found
    """
    best_rule = None
    best_score = 0.0
    
    # Get all rules from source domain
    rules = get_translation_rules(source_domain)
    
    for rule in rules:
        if rule.target_domain not in available_domains:
            continue
            
        # Calculate translation quality score
        similarity = DOMAIN_SIMILARITY.get((source_domain, rule.target_domain), 0.5)
        
        # Check if query contains mappable concepts
        concept_matches = 0
        for source_concept in rule.concept_mapping.keys():
            if source_concept.lower() in query.lower():
                concept_matches += 1
        
        if concept_matches == 0:
            continue  # No mappable concepts in query
        
        # Score = similarity * concept_coverage * confidence_boost
        concept_coverage = concept_matches / len(rule.concept_mapping)
        score = similarity * (0.5 + 0.5 * concept_coverage) * (1 + rule.confidence_boost)
        
        if score > best_score:
            best_score = score
            best_rule = rule
    
    if best_rule:
        return {
            "rule": best_rule,
            "score": best_score,
            "translation": best_rule.translate_query(query, {})
        }
    
    return None


def apply_cross_domain_reasoning(
    query: str,
    source_domain: str,
    available_domains: List[str],
    reasoning_engine: Any = None
) -> Dict[str, Any]:
    """
    Apply cross-domain reasoning to answer a query.
    
    Args:
        query: The user's query
        source_domain: The domain of the query
        available_domains: Domains with strong knowledge base
        reasoning_engine: Optional engine to perform reasoning in target domain
        
    Returns:
        Dictionary with translated query, reasoning results, and mapped answer
    """
    # Find best translation
    translation_result = find_best_translation(query, source_domain, available_domains)
    
    if not translation_result:
        return {
            "success": False,
            "reason": "No suitable cross-domain translation found",
            "fallback": "use_first_principles"
        }
    
    rule = translation_result["rule"]
    translation = translation_result["translation"]
    
    # Translate the query
    translated_context = translation["new_context"]
    translated_concepts = translation["translated_concepts"]
    
    # Build translated query hint
    translated_hint = translation["transformation_hint"]
    
    result = {
        "success": True,
        "source_domain": source_domain,
        "target_domain": rule.target_domain,
        "translation_type": rule.translation_type.value,
        "translated_concepts": translated_concepts,
        "reasoning_hint": translated_hint,
        "confidence_boost": rule.confidence_boost,
        "examples": rule.examples,
        "context": translated_context
    }
    
    return result


def get_analogous_domains(domain: str, threshold: float = 0.7) -> List[Tuple[str, float]]:
    """Get domains analogous to the given domain with similarity above threshold."""
    analogous = []
    
    for (d1, d2), score in DOMAIN_SIMILARITY.items():
        if d1 == domain and score >= threshold:
            analogous.append((d2, score))
        elif d2 == domain and score >= threshold:
            analogous.append((d1, score))
    
    # Sort by similarity score descending
    analogous.sort(key=lambda x: x[1], reverse=True)
    return analogous
