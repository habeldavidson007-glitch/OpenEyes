"""
OpenEyes Axioms Library - Universal Laws for First-Principles Reasoning

This module contains universal axioms that allow OpenEyes to reason about
domains it hasn't explicitly ingested, using first-principles deduction.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum


class AxiomCategory(Enum):
    """Categories of universal axioms."""
    CAUSALITY = "causality"
    OPTIMIZATION = "optimization"
    CONSERVATION = "conservation"
    EQUILIBRIUM = "equilibrium"
    INFORMATION = "information"
    GAME_THEORY = "game_theory"
    EVOLUTION = "evolution"
    STRUCTURE = "structure"


@dataclass
class Axiom:
    """A universal law that can be applied across domains."""
    id: str
    name: str
    category: AxiomCategory
    description: str
    formal_statement: str  # Mathematical/logical formulation
    applicable_domains: List[str]
    derivation_rules: List[str]  # How to derive conclusions from this axiom
    confidence_weight: float = 1.0  # Weight in consensus calculations
    
    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply this axiom to a specific context and derive conclusions."""
        result = {
            "axiom_id": self.id,
            "axiom_name": self.name,
            "derived_facts": [],
            "confidence": self.confidence_weight
        }
        
        # Domain-specific application logic
        if self.category == AxiomCategory.CAUSALITY:
            result = self._apply_causality(context, result)
        elif self.category == AxiomCategory.OPTIMIZATION:
            result = self._apply_optimization(context, result)
        elif self.category == AxiomCategory.GAME_THEORY:
            result = self._apply_game_theory(context, result)
        elif self.category == AxiomCategory.INFORMATION:
            result = self._apply_information(context, result)
        elif self.category == AxiomCategory.EQUILIBRIUM:
            result = self._apply_equilibrium(context, result)
        elif self.category == AxiomCategory.CONSERVATION:
            result = self._apply_conservation(context, result)
        elif self.category == AxiomCategory.EVOLUTION:
            result = self._apply_evolution(context, result)
        elif self.category == AxiomCategory.STRUCTURE:
            result = self._apply_structure(context, result)
            
        return result
    
    def _apply_causality(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply causality axioms."""
        # Causal Chain: If A->B and B->C, then A->C
        if "causal_chain" in context:
            chain = context["causal_chain"]
            if len(chain) >= 2:
                result["derived_facts"].append({
                    "type": "causal_transitivity",
                    "statement": f"{chain[0]} causes {chain[-1]} through intermediate steps",
                    "confidence": 0.9
                })
        
        # Resource Conflict: Limited Resources + Competing Agents = Tension
        if "limited_resources" in context and context.get("competing_agents", False):
            result["derived_facts"].append({
                "type": "resource_conflict",
                "statement": "Competition for limited resources creates tension and potential conflict",
                "confidence": 0.85
            })
        
        # Historical Causation: Geopolitical factors + Economic pressure = Social change
        if "geopolitical_factors" in context and "economic_pressure" in context:
            result["derived_facts"].append({
                "type": "historical_causation",
                "statement": "Geopolitical and economic pressures drive historical social changes",
                "confidence": 0.8
            })
            
        return result
    
    def _apply_optimization(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimization axioms."""
        # Utility Maximization: Agents act to maximize their utility function
        if "agents" in context:
            result["derived_facts"].append({
                "type": "utility_maximization",
                "statement": "Rational agents will act to maximize their perceived utility",
                "confidence": 0.75
            })
        
        # Pareto Efficiency: Systems tend toward Pareto optimal states
        if "system_state" in context:
            result["derived_facts"].append({
                "type": "pareto_tendency",
                "statement": "Systems evolve toward states where no agent can improve without harming others",
                "confidence": 0.7
            })
            
        return result
    
    def _apply_game_theory(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply game theory axioms."""
        # Nash Equilibrium: In competitive scenarios, stable states emerge
        if "competitive_scenario" in context:
            result["derived_facts"].append({
                "type": "nash_equilibrium",
                "statement": "Competitive interactions tend toward Nash equilibrium where no player benefits from unilateral deviation",
                "confidence": 0.85
            })
        
        # Prisoner's Dilemma: Individual rationality can lead to collective suboptimal outcomes
        if "cooperation_dilemma" in context:
            result["derived_facts"].append({
                "type": "prisoners_dilemma",
                "statement": "Without enforcement mechanisms, rational individuals may fail to cooperate even when it's mutually beneficial",
                "confidence": 0.9
            })
            
        # Zero-Sum vs Positive-Sum: Determine if competition is zero-sum
        if "resource_type" in context:
            if context["resource_type"] == "fixed":
                result["derived_facts"].append({
                    "type": "zero_sum",
                    "statement": "Fixed resources create zero-sum competitive dynamics",
                    "confidence": 0.8
                })
            else:
                result["derived_facts"].append({
                    "type": "positive_sum",
                    "statement": "Expandable resources enable positive-sum cooperative dynamics",
                    "confidence": 0.75
                })
                
        return result
    
    def _apply_information(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply information theory axioms."""
        # Information Entropy: Uncertainty decreases with more information
        if "uncertainty_level" in context:
            result["derived_facts"].append({
                "type": "information_entropy",
                "statement": "Additional reliable information reduces uncertainty and improves decision quality",
                "confidence": 0.9
            })
        
        # Signal-to-Noise: Quality of information matters more than quantity
        if "information_sources" in context:
            result["derived_facts"].append({
                "type": "signal_noise_ratio",
                "statement": "High-quality, verified sources provide better signal than numerous unverified sources",
                "confidence": 0.85
            })
            
        return result
    
    def _apply_equilibrium(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply equilibrium axioms."""
        # Supply-Demand Equilibrium: Markets tend toward price equilibrium
        if "market_system" in context:
            result["derived_facts"].append({
                "type": "market_equilibrium",
                "statement": "Free markets tend toward equilibrium where supply equals demand",
                "confidence": 0.8
            })
        
        # Homeostasis: Biological and social systems maintain stability through feedback
        if "feedback_loops" in context:
            result["derived_facts"].append({
                "type": "homeostasis",
                "statement": "Systems with negative feedback loops maintain stability around set points",
                "confidence": 0.85
            })
            
        return result
    
    def _apply_conservation(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply conservation axioms."""
        # Energy Conservation: Energy cannot be created or destroyed, only transformed
        if "energy_system" in context:
            result["derived_facts"].append({
                "type": "energy_conservation",
                "statement": "Total energy in a closed system remains constant; it only changes form",
                "confidence": 0.95
            })
        
        # Mass Conservation: Matter is conserved in chemical reactions
        if "chemical_reaction" in context:
            result["derived_facts"].append({
                "type": "mass_conservation",
                "statement": "Mass is conserved in chemical reactions; atoms are rearranged but not created or destroyed",
                "confidence": 0.95
            })
            
        return result
    
    def _apply_evolution(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply evolutionary axioms."""
        # Natural Selection: Traits that enhance survival/reproduction become more common
        if "population" in context and "selection_pressure" in context:
            result["derived_facts"].append({
                "type": "natural_selection",
                "statement": "Traits enhancing survival and reproduction under current pressures will increase in frequency",
                "confidence": 0.9
            })
        
        # Cultural Evolution: Ideas spread based on fitness (memetics)
        if "cultural_traits" in context:
            result["derived_facts"].append({
                "type": "cultural_evolution",
                "statement": "Ideas and behaviors spread through populations based on their transmission fitness",
                "confidence": 0.75
            })
            
        return result
    
    def _apply_structure(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply structural axioms."""
        # Hierarchy Emergence: Complex systems develop hierarchical structures
        if "complex_system" in context:
            result["derived_facts"].append({
                "type": "hierarchy_emergence",
                "statement": "Complex systems naturally develop hierarchical organizational structures",
                "confidence": 0.8
            })
        
        # Modularity: Systems evolve toward modular architectures for robustness
        if "system_architecture" in context:
            result["derived_facts"].append({
                "type": "modularity_principle",
                "statement": "Modular architectures increase system robustness and adaptability",
                "confidence": 0.8
            })
            
        return result


# ============================================================================
# UNIVERSAL AXIOMS LIBRARY
# ============================================================================

UNIVERSAL_AXIOMS: List[Axiom] = [
    # CAUSALITY AXIOMS
    Axiom(
        id="CAUS_001",
        name="Causal Transitivity",
        category=AxiomCategory.CAUSALITY,
        description="If A causes B and B causes C, then A causes C",
        formal_statement="∀A,B,C: (A→B ∧ B→C) → (A→C)",
        applicable_domains=["history", "philosophy", "science", "economics", "sociology"],
        derivation_rules=["transitive_inference", "causal_chain_analysis"]
    ),
    Axiom(
        id="CAUS_002",
        name="Resource Conflict Principle",
        category=AxiomCategory.CAUSALITY,
        description="Limited resources with competing agents leads to tension",
        formal_statement="Limited(R) ∧ Agents(A) ∧ Competing(A,R) → Tension(A)",
        applicable_domains=["history", "economics", "political_science", "sociology"],
        derivation_rules=["conflict_prediction", "resource_analysis"]
    ),
    Axiom(
        id="CAUS_003",
        name="Historical Causation",
        category=AxiomCategory.CAUSALITY,
        description="Geopolitical and economic factors drive historical change",
        formal_statement="Geopolitical(G) ∧ Economic(E) → Social_Change(S)",
        applicable_domains=["history", "political_science", "sociology"],
        derivation_rules=["historical_analysis", "multifactor_causation"]
    ),
    
    # OPTIMIZATION AXIOMS
    Axiom(
        id="OPT_001",
        name="Utility Maximization",
        category=AxiomCategory.OPTIMIZATION,
        description="Rational agents maximize their utility functions",
        formal_statement="∀Agent(a): Rational(a) → Maximize(Utility(a))",
        applicable_domains=["economics", "philosophy", "psychology", "game_theory"],
        derivation_rules=["rational_choice_analysis", "preference_modeling"]
    ),
    Axiom(
        id="OPT_002",
        name="Pareto Efficiency Tendency",
        category=AxiomCategory.OPTIMIZATION,
        description="Systems evolve toward Pareto optimal states",
        formal_statement="System(S) → TendTowards(S, ParetoOptimal)",
        applicable_domains=["economics", "sociology", "biology", "engineering"],
        derivation_rules=["efficiency_analysis", "optimization_modeling"]
    ),
    
    # GAME THEORY AXIOMS
    Axiom(
        id="GAME_001",
        name="Nash Equilibrium",
        category=AxiomCategory.GAME_THEORY,
        description="Competitive interactions converge to stable equilibria",
        formal_statement="∀Game(g): Competitive(g) → ∃Equilibrium(e): Stable(e,g)",
        applicable_domains=["economics", "philosophy", "political_science", "biology"],
        derivation_rules=["equilibrium_analysis", "strategy_modeling"]
    ),
    Axiom(
        id="GAME_002",
        name="Prisoner's Dilemma",
        category=AxiomCategory.GAME_THEORY,
        description="Individual rationality can lead to collective suboptimal outcomes",
        formal_statement="Rational(Individuals) ∧ NoEnforcement → Suboptimal(Collective)",
        applicable_domains=["philosophy", "economics", "political_science", "sociology"],
        derivation_rules=["cooperation_analysis", "incentive_modeling"]
    ),
    Axiom(
        id="GAME_003",
        name="Zero-Sum Dynamics",
        category=AxiomCategory.GAME_THEORY,
        description="Fixed resources create zero-sum competitive dynamics",
        formal_statement="Fixed(Resources) → ZeroSum(Competition)",
        applicable_domains=["economics", "political_science", "sports", "warfare"],
        derivation_rules=["resource_classification", "competition_analysis"]
    ),
    
    # INFORMATION AXIOMS
    Axiom(
        id="INFO_001",
        name="Information Entropy Reduction",
        category=AxiomCategory.INFORMATION,
        description="More information reduces uncertainty",
        formal_statement="Info(I) ∧ Reliable(I) → ¬Uncertainty(U)",
        applicable_domains=["science", "philosophy", "decision_making", "statistics"],
        derivation_rules=["uncertainty_quantification", "information_valuation"]
    ),
    Axiom(
        id="INFO_002",
        name="Signal-to-Noise Principle",
        category=AxiomCategory.INFORMATION,
        description="Quality of information matters more than quantity",
        formal_statement="Quality(Q) > Quantity(N) for DecisionAccuracy",
        applicable_domains=["science", "journalism", "research", "intelligence"],
        derivation_rules=["source_evaluation", "quality_assessment"]
    ),
    
    # EQUILIBRIUM AXIOMS
    Axiom(
        id="EQ_001",
        name="Market Equilibrium",
        category=AxiomCategory.EQUILIBRIUM,
        description="Free markets tend toward supply-demand equilibrium",
        formal_statement="FreeMarket(M) → TendTowards(M, Supply=Demand)",
        applicable_domains=["economics", "economy", "finance", "business"],
        derivation_rules=["market_analysis", "price_modeling"]
    ),
    Axiom(
        id="EQ_002",
        name="Homeostasis",
        category=AxiomCategory.EQUILIBRIUM,
        description="Systems with negative feedback maintain stability",
        formal_statement="NegativeFeedback(F) ∧ System(S) → Stable(S)",
        applicable_domains=["biology", "medicine", "engineering", "sociology"],
        derivation_rules=["feedback_analysis", "stability_modeling"]
    ),
    
    # CONSERVATION AXIOMS
    Axiom(
        id="CONS_001",
        name="Energy Conservation",
        category=AxiomCategory.CONSERVATION,
        description="Energy is conserved in closed systems",
        formal_statement="ClosedSystem(S) → Constant(TotalEnergy(S))",
        applicable_domains=["physics", "chemistry", "engineering", "biology"],
        derivation_rules=["energy_balance", "transformation_tracking"]
    ),
    Axiom(
        id="CONS_002",
        name="Mass Conservation",
        category=AxiomCategory.CONSERVATION,
        description="Mass is conserved in chemical reactions",
        formal_statement="ChemicalReaction(R) → Constant(TotalMass(R))",
        applicable_domains=["chemistry", "physics", "engineering"],
        derivation_rules=["stoichiometry", "mass_balance"]
    ),
    
    # EVOLUTION AXIOMS
    Axiom(
        id="EVOL_001",
        name="Natural Selection",
        category=AxiomCategory.EVOLUTION,
        description="Traits enhancing survival become more common",
        formal_statement="Trait(T) ∧ EnhancesSurvival(T,P) → IncreaseFrequency(T,P)",
        applicable_domains=["biology", "medicine", "anthropology", "sociology"],
        derivation_rules=["fitness_analysis", "selection_modeling"]
    ),
    Axiom(
        id="EVOL_002",
        name="Cultural Evolution",
        category=AxiomCategory.EVOLUTION,
        description="Ideas spread based on transmission fitness",
        formal_statement="Idea(I) ∧ TransmissionFitness(I) → Spread(I,Population)",
        applicable_domains=["sociology", "anthropology", "history", "psychology"],
        derivation_rules=["memetic_analysis", "cultural_transmission"]
    ),
    
    # STRUCTURE AXIOMS
    Axiom(
        id="STR_001",
        name="Hierarchy Emergence",
        category=AxiomCategory.STRUCTURE,
        description="Complex systems develop hierarchical structures",
        formal_statement="Complex(System) → Hierarchical(Structure(System))",
        applicable_domains=["biology", "sociology", "computer_science", "management"],
        derivation_rules=["complexity_analysis", "structure_detection"]
    ),
    Axiom(
        id="STR_002",
        name="Modularity Principle",
        category=AxiomCategory.STRUCTURE,
        description="Modular architectures increase robustness",
        formal_statement="Modular(Architecture) → Robust(System) ∧ Adaptable(System)",
        applicable_domains=["engineering", "computer_science", "biology", "management"],
        derivation_rules=["architecture_analysis", "robustness_modeling"]
    )
]


def get_axioms_for_domain(domain: str) -> List[Axiom]:
    """Get all axioms applicable to a specific domain."""
    return [a for a in UNIVERSAL_AXIOMS if domain.lower() in a.applicable_domains]


def get_axiom_by_id(axiom_id: str) -> Optional[Axiom]:
    """Get a specific axiom by its ID."""
    for axiom in UNIVERSAL_AXIOMS:
        if axiom.id == axiom_id:
            return axiom
    return None


def apply_axioms_to_context(axioms: List[Axiom], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply a list of axioms to a context and return derived facts."""
    results = []
    for axiom in axioms:
        result = axiom.apply(context)
        if result["derived_facts"]:
            results.append(result)
    return results


def generate_first_principles_explanation(
    query: str,
    domain: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a first-principles explanation for a query using universal axioms.
    
    Args:
        query: The user's query
        domain: The identified domain
        context: Additional context about the query
        
    Returns:
        Dictionary containing derived facts and confidence scores
    """
    # Get relevant axioms for the domain
    relevant_axioms = get_axioms_for_domain(domain)
    
    # Build default context if none provided
    if context is None:
        context = {}
    
    # Add query-derived context hints
    query_lower = query.lower()
    if any(word in query_lower for word in ["why", "cause", "reason", "because"]):
        context["causal_chain"] = query_lower.split()
    if any(word in query_lower for word in ["conflict", "war", "competition", "fight"]):
        context["competing_agents"] = True
        context["limited_resources"] = True
    if any(word in query_lower for word in ["optimize", "best", "maximize", "efficient"]):
        context["optimization_problem"] = True
    if any(word in query_lower for word in ["game", "strategy", "choice", "decision"]):
        context["competitive_scenario"] = True
    if any(word in query_lower for word in ["market", "price", "supply", "demand"]):
        context["market_system"] = True
    if any(word in query_lower for word in ["evolve", "adapt", "survive", "select"]):
        context["population"] = True
        context["selection_pressure"] = True
    
    # Apply axioms
    derived_results = apply_axioms_to_context(relevant_axioms, context)
    
    # Compile final explanation
    all_derived_facts = []
    total_confidence = 0.0
    axiom_count = 0
    
    for result in derived_results:
        all_derived_facts.extend(result["derived_facts"])
        total_confidence += result["confidence"]
        axiom_count += 1
    
    avg_confidence = total_confidence / axiom_count if axiom_count > 0 else 0.0
    
    return {
        "query": query,
        "domain": domain,
        "axioms_applied": len(relevant_axioms),
        "derived_facts": all_derived_facts,
        "confidence": min(avg_confidence, 0.95),  # Cap at 0.95
        "methodology": "first_principles_deduction"
    }
