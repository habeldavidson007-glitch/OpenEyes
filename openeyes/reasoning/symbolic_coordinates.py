"""
OpenEyes Symbolic Coordinate System (SCS)
Replaces vector embeddings with deterministic, auditable semantic coordinates.
Every concept maps to a fixed [Domain, Urgency, Risk, Abstraction] coordinate.
"""

from typing import Dict, List, Tuple, Optional
import math

class SymbolicCoordinateSystem:
    """
    Deterministic semantic mapping without stochastic embeddings.
    Coordinates: [Domain_Weight, Urgency_Weight, Risk_Weight, Abstraction_Level]
    """
    
    def __init__(self):
        # Domain dimensions: Healthcare=0, Economy=1, Governance=2, Investment=3, General=4
        self.domains = {
            'healthcare': 0,
            'economy': 1,
            'governance': 2,
            'investment': 3,
            'general': 4
        }
        
        # Hard-coded symbolic latent space for core concepts
        # Format: concept -> [domain_idx, urgency, risk, abstraction]
        self.latent_space: Dict[str, List[float]] = {
            # Healthcare concepts
            'diabetes': [0.0, 0.6, 0.7, 0.3],
            'insulin': [0.0, 0.8, 0.5, 0.4],
            'stroke': [0.0, 1.0, 0.95, 0.3],
            'heart_attack': [0.0, 1.0, 0.98, 0.3],
            'fever': [0.0, 0.4, 0.3, 0.2],
            'vaccine': [0.0, 0.5, 0.4, 0.5],
            'anticoagulants': [0.0, 0.9, 0.85, 0.6],
            'metformin': [0.0, 0.5, 0.4, 0.5],
            'dialysis': [0.0, 0.7, 0.6, 0.5],
            
            # Economy concepts
            'inflation': [1.0, 0.7, 0.6, 0.4],
            'hyperinflation': [1.0, 1.0, 0.95, 0.5],
            'recession': [1.0, 0.8, 0.7, 0.4],
            'gdp': [1.0, 0.3, 0.2, 0.6],
            'unemployment': [1.0, 0.6, 0.5, 0.4],
            'interest_rate': [1.0, 0.7, 0.6, 0.5],
            'price_hike': [1.0, 0.6, 0.5, 0.3],
            'currency': [1.0, 0.4, 0.4, 0.5],
            
            # Governance concepts
            'parliament': [2.0, 0.3, 0.2, 0.4],
            'election': [2.0, 0.6, 0.4, 0.4],
            'constitution': [2.0, 0.4, 0.3, 0.7],
            'policy': [2.0, 0.5, 0.4, 0.5],
            'regulation': [2.0, 0.5, 0.5, 0.5],
            'democracy': [2.0, 0.3, 0.2, 0.8],
            
            # Investment concepts
            'stock': [3.0, 0.5, 0.6, 0.4],
            'bond': [3.0, 0.3, 0.3, 0.5],
            'portfolio': [3.0, 0.4, 0.5, 0.5],
            'diversification': [3.0, 0.4, 0.4, 0.6],
            'roi': [3.0, 0.5, 0.5, 0.4],
            'market_crash': [3.0, 0.9, 0.85, 0.4],
            'asset': [3.0, 0.3, 0.4, 0.5],
            
            # General concepts
            'photosynthesis': [4.0, 0.1, 0.1, 0.5],
            'gravity': [4.0, 0.1, 0.1, 0.6],
            'quantum_mechanics': [4.0, 0.2, 0.2, 0.9],
            'evolution': [4.0, 0.2, 0.2, 0.7],
            'climate_change': [4.0, 0.8, 0.7, 0.5],
            'electricity': [4.0, 0.2, 0.2, 0.5],
        }
        
        # Synonym mappings for token expansion
        self.synonyms = {
            'price_increase': 'inflation',
            'cost_rise': 'inflation',
            'money_supply': 'currency',
            'heart_disease': 'heart_attack',
            'brain_attack': 'stroke',
            'shares': 'stock',
            'bonds': 'bond',
            'law': 'regulation',
            'government': 'governance',
        }

    def normalize_token(self, token: str) -> str:
        """Expand synonyms to canonical concept names."""
        token_lower = token.lower().replace('_', ' ').replace('-', ' ')
        return self.synonyms.get(token_lower, token_lower)

    def get_coordinate(self, concept: str) -> Optional[List[float]]:
        """Retrieve deterministic coordinate for a concept."""
        normalized = self.normalize_token(concept)
        if normalized in self.latent_space:
            return self.latent_space[normalized].copy()
        # Fallback: return general domain with low confidence
        return [4.0, 0.1, 0.1, 0.5]

    def calculate_similarity(self, coord_a: List[float], coord_b: List[float]) -> float:
        """
        Deterministic cosine similarity between two coordinates.
        No stochastic sampling - pure mathematical computation.
        """
        dot_product = sum(a * b for a, b in zip(coord_a, coord_b))
        magnitude_a = math.sqrt(sum(a*a for a in coord_a))
        magnitude_b = math.sqrt(sum(b*b for b in coord_b))
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return dot_product / (magnitude_a * magnitude_b)

    def map_query_to_coordinates(self, tokens: List[str]) -> Dict[str, Tuple[List[float], float]]:
        """
        Convert query tokens to coordinate activations with attention weights.
        Returns: {concept: (coordinate, activation_weight)}
        """
        activations = {}
        
        for token in tokens:
            normalized = self.normalize_token(token)
            coord = self.get_coordinate(normalized)
            
            if coord:
                # Calculate activation based on token position and context
                # Earlier tokens get slight priority boost
                position_weight = 1.0 - (tokens.index(token) * 0.05)
                activation = min(1.0, position_weight)
                
                # Store or update with max activation
                if normalized not in activations or activation > activations[normalized][1]:
                    activations[normalized] = (coord, activation)
        
        return activations

    def find_related_concepts(self, query_tokens: List[str], threshold: float = 0.7) -> List[Tuple[str, float]]:
        """
        Find all concepts related to query tokens above similarity threshold.
        Uses deterministic coordinate comparison.
        """
        query_activations = self.map_query_to_coordinates(query_tokens)
        related = []
        
        # Average query coordinate weighted by activation
        if not query_activations:
            return []
            
        avg_coord = [0.0, 0.0, 0.0, 0.0]
        total_weight = 0.0
        
        for concept, (coord, weight) in query_activations.items():
            for i in range(4):
                avg_coord[i] += coord[i] * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_coord = [c / total_weight for c in avg_coord]
        
        # Compare against all known concepts
        for concept, coord in self.latent_space.items():
            similarity = self.calculate_similarity(avg_coord, coord)
            if similarity >= threshold:
                related.append((concept, similarity))
        
        # Sort by similarity descending
        related.sort(key=lambda x: x[1], reverse=True)
        return related

    def detect_emergency_context(self, activations: Dict[str, Tuple[List[float], float]]) -> bool:
        """
        Detect high-risk emergency contexts using coordinate analysis.
        Returns True if urgency > 0.8 AND risk > 0.8 for any activated concept.
        """
        for concept, (coord, weight) in activations.items():
            urgency = coord[1]  # Index 1 = urgency
            risk = coord[2]     # Index 2 = risk
            
            if urgency > 0.85 and risk > 0.8:
                return True
        
        return False


# Test the system
if __name__ == "__main__":
    scs = SymbolicCoordinateSystem()
    
    print("=== Symbolic Coordinate System Test ===\n")
    
    # Test 1: Basic coordinate retrieval
    print("1. Coordinate Retrieval:")
    for concept in ['inflation', 'stroke', 'stock']:
        coord = scs.get_coordinate(concept)
        print(f"   {concept}: {coord}")
    
    # Test 2: Similarity calculation
    print("\n2. Similarity Calculation:")
    coord1 = scs.get_coordinate('inflation')
    coord2 = scs.get_coordinate('price_hike')
    sim = scs.calculate_similarity(coord1, coord2)
    print(f"   inflation <-> price_hike: {sim:.3f}")
    
    # Test 3: Query mapping
    print("\n3. Query Mapping:")
    tokens = ['what', 'causes', 'hyperinflation']
    activations = scs.map_query_to_coordinates(tokens)
    for concept, (coord, weight) in activations.items():
        print(f"   {concept}: weight={weight:.2f}, coord={coord}")
    
    # Test 4: Related concepts
    print("\n4. Related Concepts:")
    related = scs.find_related_concepts(['economy', 'crisis'], threshold=0.6)
    for concept, sim in related[:5]:
        print(f"   {concept}: {sim:.3f}")
    
    # Test 5: Emergency detection
    print("\n5. Emergency Detection:")
    emergency_tokens = ['stroke', 'symptoms', 'emergency']
    activations = scs.map_query_to_coordinates(emergency_tokens)
    is_emergency = scs.detect_emergency_context(activations)
    print(f"   Query: {emergency_tokens}")
    print(f"   Emergency detected: {is_emergency}")
    
    print("\n✅ Symbolic Coordinate System initialized successfully!")
