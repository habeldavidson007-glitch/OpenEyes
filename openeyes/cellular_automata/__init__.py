"""
OpenEyes Cellular Automata Engine
Priority 3 Implementation: Dynamic Fragment Interaction

Applies Conway-style cellular automata rules to fragment assembly.
Fragments interact based on local neighborhood tags, producing emergent
answer structures rather than static sorting.
"""

import copy
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass, field

@dataclass
class CellState:
    """Represents a fragment's state in the CA grid."""
    fragment_id: str
    fragment: Dict[str, Any]
    active: bool = True
    weight_multiplier: float = 1.0
    neighbors: List[str] = field(default_factory=list)

class CellularAutomata:
    """
    Implements cellular automata for fragment assembly.
    
    Rules:
    - Activation: Contraindication adjacent to treatment → doubles weight
    - Suppression: Duplicate first_line treatments → suppress lower score
    - Amplification: Latest_data adjacent to definition → +10 bonus
    - Incompatibility: Incompatible fragments → eject one
    """
    
    def __init__(self, fragments: List[Dict[str, Any]]):
        """Initialize CA with candidate fragments."""
        self.cells: Dict[str, CellState] = {}
        self.generations = 0
        
        for frag in fragments:
            cell = CellState(
                fragment_id=frag.get('fragment_id', frag.get('id')),
                fragment=frag,
                active=True,
                weight_multiplier=1.0
            )
            self.cells[cell.fragment_id] = cell
        
        # Build initial neighborhood based on tag overlap
        self._build_neighborhood()
    
    def _build_neighborhood(self):
        """Connect cells based on tag overlap (neighbors share ≥2 tags)."""
        cell_ids = list(self.cells.keys())
        
        for i, id1 in enumerate(cell_ids):
            for id2 in cell_ids[i+1:]:
                if not self.cells[id1].active or not self.cells[id2].active:
                    continue
                    
                tags1 = set(self.cells[id1].fragment.get('tags', []))
                tags2 = set(self.cells[id2].fragment.get('tags', []))
                
                # Neighbor if share ≥2 tags OR explicit compatibility link
                shared = tags1 & tags2
                compatible = (
                    id2 in self.cells[id1].fragment.get('compatible_with', []) or
                    id1 in self.cells[id2].fragment.get('compatible_with', [])
                )
                
                if len(shared) >= 2 or compatible:
                    self.cells[id1].neighbors.append(id2)
                    self.cells[id2].neighbors.append(id1)
    
    def _get_neighbor_cells(self, cell: CellState) -> List[CellState]:
        """Get active neighbor cells."""
        return [
            self.cells[nid] 
            for nid in cell.neighbors 
            if self.cells[nid].active
        ]
    
    def apply_rules(self) -> List[str]:
        """
        Apply one generation of CA rules to all cells.
        Returns list of changes made.
        """
        changes = []
        new_weights = {}
        to_deactivate = set()
        
        for cell_id, cell in self.cells.items():
            if not cell.active:
                continue
                
            neighbors = self._get_neighbor_cells(cell)
            neighbor_tags = set()
            for n in neighbors:
                neighbor_tags.update(n.fragment.get('tags', []))
            
            frag_tags = set(cell.fragment.get('tags', []))
            frag_role = cell.fragment.get('reasoning_role', '')
            
            # Rule A: Activation (Contraindication next to Treatment)
            if 'contraindication' in frag_tags or 'warning' in frag_tags:
                if any(t in neighbor_tags for t in ['treatment', 'dosage', 'therapy']):
                    if cell.weight_multiplier < 2.0:
                        new_weights[cell_id] = 2.0
                        changes.append(f"ACTIVATED {cell_id} (contraindication near treatment)")
            
            # Rule B: Suppression (Duplicate first_line treatments)
            if 'first_line' in frag_tags and frag_role == 'definition':
                duplicate_neighbors = [
                    n for n in neighbors 
                    if 'first_line' in n.fragment.get('tags', [])
                    and n.fragment.get('reasoning_role') == 'definition'
                    and n.fragment_id != cell_id
                ]
                
                if duplicate_neighbors:
                    # Suppress lower credibility score
                    my_score = cell.fragment.get('score', 50)
                    max_neighbor_score = max(
                        n.fragment.get('score', 0) for n in duplicate_neighbors
                    )
                    
                    if my_score < max_neighbor_score:
                        to_deactivate.add(cell_id)
                        changes.append(f"SUPPRESSED {cell_id} (duplicate first_line, lower score)")
            
            # Rule C: Amplification (Latest_data next to Definition)
            if frag_role == 'latest_data':
                if any(n.fragment.get('reasoning_role') == 'definition' for n in neighbors):
                    if cell.weight_multiplier < 1.5:
                        new_weights[cell_id] = max(new_weights.get(cell_id, 1.0), 1.5)
                        changes.append(f"AMPLIFIED {cell_id} (latest_data near definition)")
            
            # Rule D: Incompatibility Check
            incompatible_list = cell.fragment.get('incompatible_with', [])
            for nid in cell.neighbors:
                if nid in incompatible_list:
                    # Eject lower credibility fragment
                    my_cred = self._get_credibility_rank(cell.fragment)
                    other_cred = self._get_credibility_rank(self.cells[nid].fragment)
                    
                    if my_cred < other_cred:
                        to_deactivate.add(cell_id)
                        changes.append(f"EJECTED {cell_id} (incompatible with higher-cred {nid})")
                        break
        
        # Apply changes
        for cell_id, weight in new_weights.items():
            self.cells[cell_id].weight_multiplier = weight
            
        for cell_id in to_deactivate:
            self.cells[cell_id].active = False
        
        self.generations += 1
        return changes
    
    def _get_credibility_rank(self, fragment: Dict[str, Any]) -> int:
        """Get numeric credibility rank for comparison."""
        cred_map = {
            'peer_reviewed_study': 95,
            'clinical_guideline': 90,
            'government_source': 85,
            'textbook': 80,
            'news_article': 50,
            'forum': 20
        }
        cred_class = fragment.get('credibility_class', 'forum')
        return cred_map.get(cred_class, 50)
    
    def evolve(self, generations: int = 3) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Run CA for N generations and return surviving fragments.
        """
        all_changes = []
        
        for gen in range(generations):
            changes = self.apply_rules()
            all_changes.extend(changes)
            
            # Stop early if no changes
            if not changes:
                break
        
        # Return active fragments with updated weights
        result = []
        for cell in self.cells.values():
            if cell.active:
                frag = copy.deepcopy(cell.fragment)
                original_score = frag.get('score', 50)
                frag['ca_score'] = original_score * cell.weight_multiplier
                frag['ca_generations'] = self.generations
                frag['ca_weight_multiplier'] = cell.weight_multiplier
                result.append(frag)
        
        return result, all_changes

def run_cellular_automata(fragments: List[Dict[str, Any]], generations: int = 3) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Main entry point: Apply CA rules to fragment list.
    
    Args:
        fragments: List of candidate fragments from Monte Carlo
        generations: Number of CA evolution steps (default 3)
    
    Returns:
        Tuple of (surviving_fragments, change_log)
    """
    if not fragments:
        return [], []
    
    ca = CellularAutomata(fragments)
    return ca.evolve(generations)
