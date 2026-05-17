"""
OpenEyes Cognitive Conversational Engine
----------------------------------------
Replaces "Transformer" marketing fluff with actual Deterministic Graph Traversal.
Features:
1. True Logical Synthesis (A + B -> C, not just "A. Also B.")
2. Stateful Dialogue Memory (Pronoun resolution, context tracking)
3. Dynamic Rhetorical Selection (Varied sentence structures)
4. Anti-Hallucination Guards (Strict boundary enforcement)
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class IntentType(Enum):
    SYNTHESIS = "synthesis"
    SINGLE_FACT = "single_fact"
    CLARIFICATION = "clarification"
    FALLBACK = "fallback"

@dataclass
class DialogueState:
    """Lightweight memory for multi-turn coherence."""
    last_entities: List[str] = field(default_factory=list)
    last_domain: Optional[str] = None
    turn_count: int = 0
    context_window: List[Dict[str, Any]] = field(default_factory=list)
    
    def update(self, entities: List[str], domain: str, response_summary: str):
        self.last_entities = entities[-3:]  # Keep last 3 entities
        self.last_domain = domain
        self.turn_count += 1
        self.context_window.append({"role": "assistant", "content": response_summary})
        if len(self.context_window) > 3:
            self.context_window.pop(0)

class RhetoricalSelector:
    """Generates varied human-like phrasing without randomness hallucination."""
    
    CONNECTORS = {
        "causal": ["because", "since", "as a result", "consequently"],
        "contrast": ["however", "conversely", "on the other hand", "while"],
        "additive": ["furthermore", "additionally", "moreover", "also"],
        "temporal": ["initially", "subsequently", "meanwhile", "finally"]
    }
    
    OPENERS = {
        "high_conf": ["Clearly,", "Specifically,", "The data shows", "Directly,"],
        "med_conf": ["Generally,", "Typically,", "Evidence suggests", "In most cases,"],
        "synthesis": ["Connecting these points,", "When we look at both,", "The relationship indicates"]
    }

    @staticmethod
    def select_phrase(category: str, seed: int) -> str:
        """Deterministic selection based on seed (e.g., turn count or hash) to avoid repetition."""
        options = RhetoricalSelector.CONNECTORS.get(category, RhetoricalSelector.OPENERS["high_conf"])
        return options[seed % len(options)]

class DeterministicReasoner:
    """
    The Core Brain.
    Replaces 'Attention' with Coordinate Matching.
    Replaces 'Generation' with Logical Graph Assembly.
    """
    
    def __init__(self):
        # 1. Symbolic Latent Space (Hard-coded coordinates)
        self.latent_space = {
            "inflation": [1.0, 0.0, 0.6],      # [Economy, Health, Risk]
            "insurance": [0.0, 1.0, 0.5],      # High Health, Med Risk
            "price_hike": [0.9, 0.1, 0.4],
            "healthcare": [0.1, 1.0, 0.8],
            "cost": [0.8, 0.2, 0.5],
            "risk": [0.5, 0.5, 1.0],
            "general_economics": [0.4, 0.0, 0.1]
        }
        
        # 2. Knowledge Graph with Explicit Edges & Logic Types
        self.knowledge_graph = {
            "inflation": {
                "domain": "ECONOMY",
                "verified": True,
                "freshness": 0.95,
                "content": "A hidden tax on cash assets where purchasing power drops daily.",
                "analogy": "Your paycheck stays the same size, but your grocery cart shrinks.",
                "edges": {"insurance": "causal", "cost": "synonym"}
            },
            "insurance": {
                "domain": "HEALTHCARE", # Cross-domain link
                "verified": True,
                "freshness": 0.90,
                "content": "Risk-pooling infrastructure designed to offset catastrophic losses.",
                "analogy": "Everyone pays a small coin into a bucket so whoever breaks a leg can fix it.",
                "edges": {"inflation": "vulnerability"}
            },
            "price_hike": {
                "domain": "ECONOMY",
                "verified": True,
                "freshness": 0.85,
                "content": "A rapid increase in the price of goods or services.",
                "analogy": "The sticker price jumps overnight while your wallet stays thin.",
                "edges": {"inflation": "symptom"}
            },
            "healthcare": {
                "domain": "HEALTHCARE",
                "verified": True,
                "freshness": 0.98,
                "content": "The organized provision of medical care to individuals or a community.",
                "analogy": "A safety net woven from doctors, hospitals, and insurance policies.",
                "edges": {"insurance": "dependency", "cost": "constraint"}
            }
        }
        
        self.rhetoric = RhetoricalSelector()

    def _calculate_attention(self, tokens: List[str]) -> Dict[str, float]:
        """Deterministic coordinate matching with lemmatization support."""
        scores = {}
        
        # Simple lemmatization map for common variations
        lemmatizer = {
            "hikes": "hike",
            "costs": "cost",
            "risks": "risk",
            "prices": "price",
            "insurances": "insurance",
            "economies": "economy",
            "systems": "system"
        }
        
        for token in tokens:
            t_lower = token.lower()
            # Try original token
            candidates = [t_lower]
            
            # Try lemmatized version
            if t_lower in lemmatizer:
                candidates.append(lemmatizer[t_lower])
                
            # Try removing 's' suffix for plurals
            if t_lower.endswith('s') and len(t_lower) > 2:
                candidates.append(t_lower[:-1])
            
            for candidate in candidates:
                # Check direct match
                if candidate in self.latent_space:
                    vec_a = self.latent_space[candidate]
                    for concept, vec_b in self.latent_space.items():
                        dot_prod = sum(a * b for a, b in zip(vec_a, vec_b))
                        mag = math.sqrt(sum(a*a for a in vec_a)) * math.sqrt(sum(b*b for b in vec_b))
                        activation = dot_prod / mag if mag > 0 else 0.0
                        scores[concept] = max(scores.get(concept, 0.0), activation)
                        
                # Check partial match (e.g., "price_hike" contains "hike")
                for concept_key in self.latent_space:
                    if candidate in concept_key or concept_key in candidate:
                        vec_a = self.latent_space[concept_key]
                        for concept, vec_b in self.latent_space.items():
                            dot_prod = sum(a * b for a, b in zip(vec_a, vec_b))
                            mag = math.sqrt(sum(a*a for a in vec_a)) * math.sqrt(sum(b*b for b in vec_b))
                            activation = (dot_prod / mag if mag > 0 else 0.0) * 0.9  # Penalty for partial match
                            scores[concept] = max(scores.get(concept, 0.0), activation)
                            
        return scores

    def _resolve_pronouns(self, query_tokens: List[str], state: DialogueState) -> List[str]:
        """Simple pronoun resolution using dialogue state."""
        resolved = []
        for token in query_tokens:
            if token.lower() in ["it", "that", "this", "they"] and state.last_entities:
                # Map pronoun to last known entity (simplified logic)
                resolved.append(state.last_entities[-1])
            else:
                resolved.append(token)
        return resolved

    def _build_logical_chain(self, active_nodes: Dict[str, float], graph: Dict) -> Optional[Dict]:
        """
        Attempts to find a logical relationship between active nodes.
        Returns a structured plan for synthesis.
        """
        nodes = list(active_nodes.keys())
        if len(nodes) < 2:
            return None
            
        # Check for direct edges
        n1, n2 = nodes[0], nodes[1]
        if n1 in graph and n2 in graph[n1].get("edges", {}):
            relation = graph[n1]["edges"][n2]
            return {"type": "direct", "source": n1, "target": n2, "relation": relation}
        elif n2 in graph and n1 in graph[n2].get("edges", {}):
            relation = graph[n2]["edges"][n1]
            return {"type": "direct", "source": n2, "target": n1, "relation": relation}
            
        # Default to additive if no specific edge found but both high confidence
        return {"type": "additive", "source": n1, "target": n2, "relation": "correlation"}

    def reason(self, query_tokens: List[str], domain: str, state: DialogueState) -> Tuple[str, List[str]]:
        """Main entry point for reasoning and response generation."""
        
        # 1. Pre-processing: Pronoun Resolution
        resolved_tokens = self._resolve_pronouns(query_tokens, state)
        
        # 2. Attention Calculation
        attention_weights = self._calculate_attention(resolved_tokens)
        
        # Filter low confidence matches
        active_nodes = {k: v for k, v in attention_weights.items() if v > 0.5}
        
        if not active_nodes:
            return "I don't have enough verified information to answer that specifically.", []

        # 3. Logical Planning
        chain = self._build_logical_chain(active_nodes, self.knowledge_graph)
        top_node = max(active_nodes, key=active_nodes.get)
        detected_domain = self.knowledge_graph.get(top_node, {}).get("domain", domain)
        
        response_text = ""
        used_entities = list(active_nodes.keys())

        # 4. Response Generation based on Logic Type
        seed = state.turn_count
        
        if chain and chain["type"] == "direct":
            # TRUE SYNTHESIS: A affects B because of Relation R
            n1_data = self.knowledge_graph[chain["source"]]
            n2_data = self.knowledge_graph[chain["target"]]
            
            connector = self.rhetoric.select_phrase(chain["relation"], seed)
            opener = self.rhetoric.select_phrase("synthesis", seed + 1)
            
            # Construct causal narrative with proper grammar
            if chain["relation"] == "causal":
                response_text = (
                    f"{opener} {n1_data['content']} This directly impacts {chain['target']} "
                    f"{connector} {n2_data['content'].lower()}. "
                    f"Think of it this way: {n1_data['analogy']}. Consequently, {n2_data['analogy'].lower()}."
                )
            elif chain["relation"] == "vulnerability":
                response_text = (
                    f"{opener} While {n1_data['content']}, {n2_data['content'].lower()} "
                    f"creates a vulnerability here. Specifically, {connector}, {n1_data['analogy']} "
                    f"which stresses the system described by: {n2_data['analogy']}."
                )
            else:
                # Fallback for other relations - fixed grammar
                response_text = f"{opener} {n1_data['content']} Furthermore, {connector} {n2_data['content']}."

        elif len(active_nodes) == 1:
            # SINGLE FACT with Variation
            node_data = self.knowledge_graph[top_node]
            opener = self.rhetoric.select_phrase("high_conf" if active_nodes[top_node] > 0.8 else "med_conf", seed)
            response_text = f"{opener} {node_data['content']} To visualize: {node_data['analogy']}."
            
        else:
            # ADDITIVE (No direct edge, but both relevant)
            keys = list(active_nodes.keys())
            n1_data = self.knowledge_graph[keys[0]]
            n2_data = self.knowledge_graph[keys[1]]
            connector = self.rhetoric.select_phrase("additive", seed)
            response_text = f"Regarding {keys[0]}: {n1_data['content']} {connector.capitalize()}, concerning {keys[1]}: {n2_data['content']}."

        # 5. Update State
        state.update(used_entities, detected_domain, response_text[:50])
        
        return response_text, used_entities

# Export for use in other modules
__all__ = ['DeterministicReasoner', 'DialogueState', 'IntentType']
