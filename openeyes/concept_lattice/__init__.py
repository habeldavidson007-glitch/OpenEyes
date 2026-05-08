"""
OpenEyes Formal Concept Analysis (FCA) Module
Priority 4: Automatic Library Structure & Compatibility Derivation

Implements Formal Concept Analysis to automatically discover hierarchical 
structure in the fragment library and derive compatibility relationships.
"""

import json
from typing import Dict, List, Set, Tuple, Any
from concepts import Context


class ConceptLattice:
    """Manages the formal concept lattice for the fragment library."""
    
    def __init__(self):
        self.lattice = None
        self.context = None
        self.concept_map: Dict[str, Any] = {}
        
    def build_lattice(self, fragments: Dict[str, Any]) -> None:
        """
        Build a formal concept lattice from the fragment library.
        
        Args:
            fragments: Dictionary of fragment_id -> fragment_data
        """
        if not fragments:
            return
            
        # Objects = fragment IDs
        objects = list(fragments.keys())
        
        # Attributes = all unique tags across all fragments
        all_tags = set()
        for frag in fragments.values():
            all_tags.update(frag.get('tags', []))
            role = frag.get('reasoning_role', '')
            if role:
                all_tags.add(role)
            cred = frag.get('credibility_class', '')
            if cred:
                all_tags.add(cred)
            year = frag.get('year', 0)
            if year:
                all_tags.add(f"year_{year}")
            
        attributes = sorted(list(all_tags))
        
        if not attributes:
            return
            
        # Build incidence matrix: fragment × attribute
        table = []
        for frag_id in objects:
            frag = fragments[frag_id]
            frag_attrs = set(frag.get('tags', []))
            role = frag.get('reasoning_role', '')
            if role:
                frag_attrs.add(role)
            cred = frag.get('credibility_class', '')
            if cred:
                frag_attrs.add(cred)
            year = frag.get('year', 0)
            if year:
                frag_attrs.add(f"year_{year}")
            
            row = [attr in frag_attrs for attr in attributes]
            table.append(row)
        
        # Create formal context and compute lattice
        try:
            self.context = Context(objects, attributes, table)
            self.lattice = self.context.lattice
            
            # Build concept map for quick lookup
            self._build_concept_map(fragments)
        except Exception as e:
            print(f"FCA lattice construction failed: {e}")
            self.lattice = None
    
    def _build_concept_map(self, fragments: Dict[str, Any]) -> None:
        """Map each fragment to its concepts in the lattice."""
        if not self.lattice:
            return
            
        self.concept_map = {}
        for concept in self.lattice:
            concept_extents = set(concept.extent)  # Fragments in this concept
            concept_intents = set(concept.intent)  # Shared attributes
            
            for frag_id in concept_extents:
                if frag_id not in self.concept_map:
                    self.concept_map[frag_id] = []
                self.concept_map[frag_id].append({
                    'concept_id': id(concept),
                    'shared_attributes': list(concept_intents),
                    'co_fragments': list(concept_extents - {frag_id})
                })
    
    def derive_compatibility(self, fragment_id: str) -> Tuple[List[str], List[str]]:
        """
        Derive compatible and incompatible fragments based on lattice position.
        
        Returns:
            Tuple of (compatible_ids, incompatible_ids)
        """
        if not self.concept_map or fragment_id not in self.concept_map:
            return [], []
            
        compatible = set()
        incompatible = set()
        
        frag_concepts = self.concept_map[fragment_id]
        
        for concept_info in frag_concepts:
            # Fragments in same concept are highly compatible
            compatible.update(concept_info['co_fragments'])
            
        # Remove self
        compatible.discard(fragment_id)
        
        # Find disjoint concepts (incompatible)
        my_attrs = set()
        for concept_info in frag_concepts:
            my_attrs.update(concept_info['shared_attributes'])
            
        for other_id, other_concepts in self.concept_map.items():
            if other_id == fragment_id:
                continue
                
            other_attrs = set()
            for concept_info in other_concepts:
                other_attrs.update(concept_info['shared_attributes'])
                
            # If no attribute overlap and different reasoning roles, likely incompatible
            if not my_attrs.intersection(other_attrs):
                my_roles = {a for a in my_attrs if a in ['definition', 'counter_argument', 'latest_data']}
                other_roles = {a for a in other_attrs if a in ['definition', 'counter_argument', 'latest_data']}
                
                if my_roles and other_roles and my_roles != other_roles:
                    incompatible.add(other_id)
        
        return list(compatible), list(incompatible)
    
    def find_gaps(self, fragments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify gaps in the library by analyzing empty or sparse nodes.
        
        Returns:
            List of suggested fragment additions
        """
        gaps = []
        
        if not self.lattice:
            return gaps
            
        # Analyze concepts with few fragments
        for concept in self.lattice:
            extents = concept.extent
            intents = concept.intent
            
            if len(extents) < 2:  # Sparse concept
                # Check if we have all reasoning roles
                roles_present = set()
                for frag_id in extents:
                    frag = fragments.get(frag_id, {})
                    role = frag.get('reasoning_role', '')
                    if role:
                        roles_present.add(role)
                
                all_roles = {'definition', 'counter_argument', 'latest_data'}
                missing_roles = all_roles - roles_present
                
                if missing_roles and intents:
                    gaps.append({
                        'suggested_role': list(missing_roles)[0],
                        'based_on_attributes': list(intents),
                        'existing_fragments': list(extents),
                        'priority': 'high' if len(extents) == 0 else 'medium'
                    })
        
        return gaps


def rebuild_concept_lattice(fragment_library: Any) -> Dict[str, Any]:
    """
    Rebuild the concept lattice for a fragment library and update compatibilities.
    
    Args:
        fragment_library: FragmentLibrary instance
        
    Returns:
        Dictionary with statistics about the update
    """
    lattice_engine = ConceptLattice()
    
    # Get all fragments as a dictionary
    fragments_list = fragment_library.get_all_fragments()
    
    if not fragments_list:
        return {'status': 'empty', 'updated': 0}
    
    # Convert list to dict
    fragments = {frag.id: frag.to_dict() for frag in fragments_list}
    
    # Build lattice
    lattice_engine.build_lattice(fragments)
    
    if not lattice_engine.lattice:
        return {'status': 'failed', 'error': 'Could not build lattice'}
    
    # Update compatibility for each fragment
    updated_count = 0
    for frag_id in fragments.keys():
        compatible, incompatible = lattice_engine.derive_compatibility(frag_id)
        
        # Update fragment with derived compatibilities
        frag_data = fragments[frag_id]
        
        # Merge with existing compatibilities (FCA-derived as fallback)
        existing_compat = set(frag_data.get('compatible_with', []))
        existing_incompat = set(frag_data.get('incompatible_with', []))
        
        # Add FCA-derived if not explicitly set
        for c in compatible:
            if c not in existing_compat and c not in existing_incompat:
                existing_compat.add(c)
                
        for c in incompatible:
            if c not in existing_incompat and c not in existing_compat:
                existing_incompat.add(c)
        
        frag_data['compatible_with'] = list(existing_compat)
        frag_data['incompatible_with'] = list(existing_incompat)
        updated_count += 1
    
    # Find gaps
    gaps = lattice_engine.find_gaps(fragments)
    
    return {
        'status': 'success',
        'updated': updated_count,
        'concepts_found': len(list(lattice_engine.lattice)) if lattice_engine.lattice else 0,
        'gaps_identified': len(gaps),
        'gap_suggestions': gaps[:5]  # Top 5 suggestions
    }


# Integration hook for FragmentLibrary
def integrate_with_fragment_library():
    """Patch FragmentLibrary to auto-rebuild lattice on changes."""
    from openeyes.fragment_library import FragmentLibrary
    
    original_add = FragmentLibrary.add_fragment
    
    def add_fragment_with_lattice(self, fragment_data):
        result = original_add(self, fragment_data)
        
        # Rebuild lattice after adding
        stats = rebuild_concept_lattice(self)
        if stats['status'] == 'success':
            print(f"FCA: Lattice rebuilt, {stats['updated']} compatibilities updated, {stats['gaps_identified']} gaps found")
        
        return result
    
    FragmentLibrary.add_fragment = add_fragment_with_lattice
    print("FCA integration complete: automatic lattice rebuilding enabled")
