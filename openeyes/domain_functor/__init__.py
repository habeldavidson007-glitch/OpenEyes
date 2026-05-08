"""
Priority 5: Category Theory Implementation
Cross-Domain Knowledge Transfer via Functors

Implements structure-preserving maps (functors) between knowledge domains,
enabling transfer of relationship architectures without probabilistic training.
"""

from typing import Dict, List, Any, Callable
import json


class DomainOntology:
    """Defines a domain as a category with objects and morphisms."""
    
    def __init__(self, domain_name: str):
        self.domain_name = domain_name
        self.objects = {}  # object_type -> list of fragment types
        self.morphisms = {}  # (from_type, to_type) -> relationship_type
        
    def add_object(self, object_type: str, fragment_types: List[str]):
        """Add an object type (e.g., 'clinical_guideline', 'case_precedent')."""
        self.objects[object_type] = fragment_types
        
    def add_morphism(self, from_type: str, to_type: str, relationship: str):
        """Add a morphism (relationship) between object types."""
        self.morphisms[(from_type, to_type)] = relationship
        
    def get_structure(self) -> Dict[str, Any]:
        """Return the complete domain structure."""
        return {
            'domain': self.domain_name,
            'objects': self.objects,
            'morphisms': {f"{k[0]}->{k[1]}": v for k, v in self.morphisms.items()}
        }


class DomainFunctor:
    """
    A functor that maps one domain category to another.
    Preserves relationship structure while transforming object types.
    """
    
    def __init__(self, source_domain: str, target_domain: str):
        self.source_domain = source_domain
        self.target_domain = target_domain
        self.object_mapping = {}  # source_type -> target_type
        self.morphism_mapping = {}  # source_rel -> target_rel
        
    def map_object(self, source_type: str, target_type: str):
        """Define how a source object type maps to target type."""
        self.object_mapping[source_type] = target_type
        
    def map_morphism(self, source_rel: str, target_rel: str):
        """Define how a source relationship maps to target relationship."""
        self.morphism_mapping[source_rel] = target_rel
        
    def apply_to_fragment(self, fragment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a fragment from source domain to target domain structure.
        
        Args:
            fragment: Source domain fragment data
            
        Returns:
            Target domain fragment template (needs content filling)
        """
        source_type = fragment.get('credibility_class', '')
        target_type = self.object_mapping.get(source_type, source_type)
        
        # Transform tags
        new_tags = []
        for tag in fragment.get('tags', []):
            # Apply tag transformations if defined
            new_tag = self._transform_tag(tag)
            if new_tag:
                new_tags.append(new_tag)
                
        return {
            'target_domain': self.target_domain,
            'suggested_credibility_class': target_type,
            'suggested_tags': new_tags,
            'reasoning_role': fragment.get('reasoning_role', 'definition'),
            'source_fragment_id': fragment.get('id', ''),
            'structural_template': True
        }
        
    def _transform_tag(self, tag: str) -> str:
        """Transform a tag from source to target domain."""
        # Simple heuristic: replace domain-specific terms
        tag_mappings = {
            'medical': {'clinical': 'legal', 'patient': 'client', 'treatment': 'remedy'},
            'engineering': {'load': 'stress', 'material': 'component', 'safety': 'reliability'}
        }
        
        # Check if tag contains domain-specific terms
        for source_term, target_term in tag_mappings.get(self.source_domain, {}).items():
            if source_term in tag.lower():
                return tag.replace(source_term, target_term)
                
        return tag
        
    def get_mapping_summary(self) -> Dict[str, Any]:
        """Return summary of this functor's mappings."""
        return {
            'source': self.source_domain,
            'target': self.target_domain,
            'object_mappings': self.object_mapping,
            'morphism_mappings': self.morphism_mapping
        }


class CrossDomainTransferEngine:
    """
    Manages domain functors and applies them for knowledge transfer.
    """
    
    def __init__(self):
        self.domains = {}
        self.functors = {}
        
    def register_domain(self, domain: DomainOntology):
        """Register a domain ontology."""
        self.domains[domain.domain_name] = domain
        
    def create_functor(self, source: str, target: str) -> DomainFunctor:
        """Create a functor between two registered domains."""
        if source not in self.domains or target not in self.domains:
            raise ValueError(f"Domains {source} or {target} not registered")
            
        functor = DomainFunctor(source, target)
        self.functors[f"{source}->{target}"] = functor
        
        # Auto-populate common mappings based on domain ontologies
        self._auto_populate_mappings(functor)
        
        return functor
        
    def _auto_populate_mappings(self, functor: DomainFunctor):
        """Automatically suggest mappings based on domain structures."""
        source_domain = self.domains[functor.source_domain]
        target_domain = self.domains[functor.target_domain]
        
        # Map similar object types by name heuristics
        credibility_hierarchy = [
            'peer_reviewed_study', 'clinical_guideline', 'standard',
            'textbook', 'government_source', 'news_article', 'forum'
        ]
        
        # Map credibility classes in order
        for source_type in source_domain.objects.keys():
            if source_type in credibility_hierarchy:
                # Find closest match in target
                for target_type in target_domain.objects.keys():
                    if target_type in credibility_hierarchy:
                        if source_type == target_type:
                            functor.map_object(source_type, target_type)
                            break
                            
        # Default morphism mapping (identity for now)
        for (from_t, to_t), rel in source_domain.morphisms.items():
            functor.map_morphism(rel, rel)
            
    def transfer_knowledge(self, source_domain: str, target_domain: str, 
                          fragments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transfer fragment structures from source to target domain.
        
        Args:
            source_domain: Name of source domain
            target_domain: Name of target domain  
            fragments: List of source domain fragments
            
        Returns:
            List of target domain fragment templates
        """
        functor_key = f"{source_domain}->{target_domain}"
        if functor_key not in self.functors:
            # Create functor if doesn't exist
            if source_domain in self.domains and target_domain in self.domains:
                self.create_functor(source_domain, target_domain)
            else:
                raise ValueError(f"Cannot create functor: missing domains")
                
        functor = self.functors[functor_key]
        transferred = []
        
        for fragment in fragments:
            template = functor.apply_to_fragment(fragment)
            transferred.append(template)
            
        return transferred
        
    def identify_target_gaps(self, target_domain: str, 
                            existing_fragments: List[Dict[str, Any]],
                            source_domain: str = None) -> List[Dict[str, Any]]:
        """
        Identify gaps in target domain by comparing with source domain structure.
        
        Args:
            target_domain: Target domain name
            existing_fragments: Current fragments in target domain
            source_domain: Optional source domain to compare against
            
        Returns:
            List of suggested fragment additions
        """
        gaps = []
        
        if target_domain not in self.domains:
            return gaps
            
        target_struct = self.domains[target_domain].get_structure()
        
        # Count existing fragment types
        type_counts = {}
        for frag in existing_fragments:
            cred = frag.get('credibility_class', 'unknown')
            role = frag.get('reasoning_role', 'unknown')
            key = f"{cred}_{role}"
            type_counts[key] = type_counts.get(key, 0) + 1
            
        # Check for missing combinations
        for obj_type in target_struct['objects'].keys():
            for role in ['definition', 'counter_argument', 'latest_data']:
                key = f"{obj_type}_{role}"
                if type_counts.get(key, 0) == 0:
                    gaps.append({
                        'missing_type': obj_type,
                        'missing_role': role,
                        'priority': 'high' if role == 'definition' else 'medium',
                        'suggestion': f"Add {role} fragment with {obj_type} credibility"
                    })
                    
        return gaps


# Pre-defined domain ontologies
def create_medical_ontology() -> DomainOntology:
    """Create medical domain ontology."""
    med = DomainOntology('medical')
    
    # Objects (credibility classes)
    med.add_object('clinical_guideline', ['NICE', 'WHO', 'CDC'])
    med.add_object('peer_reviewed_study', ['RCT', 'meta_analysis', 'cohort_study'])
    med.add_object('textbook', ['Harrison', 'Merck_Manual'])
    med.add_object('government_source', ['FDA', 'NIH'])
    
    # Morphisms (relationships)
    med.add_morphism('clinical_guideline', 'peer_reviewed_study', 'based_on')
    med.add_morphism('peer_reviewed_study', 'clinical_guideline', 'informs')
    med.add_morphism('clinical_guideline', 'textbook', 'summarized_in')
    
    return med


def create_legal_ontology() -> DomainOntology:
    """Create legal domain ontology."""
    legal = DomainOntology('legal')
    
    # Objects
    legal.add_object('statutory_law', ['USC', 'CFR', 'Public_Law'])
    legal.add_object('case_precedent', ['SCOTUS', 'Circuit_Court', 'District_Court'])
    legal.add_object('legal_treatise', ['Restatement', 'ALR'])
    legal.add_object('government_source', ['DOJ', 'FTC'])
    
    # Morphisms
    legal.add_morphism('statutory_law', 'case_precedent', 'interpreted_by')
    legal.add_morphism('case_precedent', 'statutory_law', 'applies')
    legal.add_morphism('case_precedent', 'legal_treatise', 'analyzed_in')
    
    return legal


def create_engineering_ontology() -> DomainOntology:
    """Create engineering domain ontology."""
    eng = DomainOntology('engineering')
    
    # Objects
    eng.add_object('standard', ['ISO', 'ASTM', 'ACI', 'AISC'])
    eng.add_object('peer_reviewed_study', ['journal_article', 'conference_paper'])
    eng.add_object('textbook', ['Perry', 'Marks'])
    eng.add_object('government_source', ['OSHA', 'EPA', 'NIST'])
    
    # Morphisms
    eng.add_morphism('standard', 'peer_reviewed_study', 'validates')
    eng.add_morphism('peer_reviewed_study', 'standard', 'incorporated_into')
    eng.add_morphism('standard', 'textbook', 'explained_in')
    
    return eng


def initialize_domain_functors() -> CrossDomainTransferEngine:
    """Initialize engine with pre-defined domains and functors."""
    engine = CrossDomainTransferEngine()
    
    # Register domains
    engine.register_domain(create_medical_ontology())
    engine.register_domain(create_legal_ontology())
    engine.register_domain(create_engineering_ontology())
    
    # Create functors
    engine.create_functor('medical', 'legal')
    engine.create_functor('medical', 'engineering')
    engine.create_functor('engineering', 'legal')
    
    return engine


# Example usage
if __name__ == "__main__":
    engine = initialize_domain_functors()
    
    print("=== Domain Ontologies ===")
    for name, domain in engine.domains.items():
        print(f"\n{name}:")
        struct = domain.get_structure()
        print(f"  Objects: {list(struct['objects'].keys())}")
        print(f"  Morphisms: {len(struct['morphisms'])} relationships")
        
    print("\n=== Functor Mappings (Medical → Legal) ===")
    functor = engine.functors['medical->legal']
    mapping = functor.get_mapping_summary()
    print(f"Object mappings: {mapping['object_mappings']}")
    
    print("\n=== Transfer Example ===")
    sample_medical_fragment = {
        'id': 'frag_med_001',
        'credibility_class': 'clinical_guideline',
        'tags': ['antibiotic', 'UTI', 'first_line'],
        'reasoning_role': 'definition',
        'content': 'Nitrofurantoin is first-line for uncomplicated UTI'
    }
    
    transferred = engine.transfer_knowledge(
        'medical', 'legal',
        [sample_medical_fragment]
    )
    
    print(f"Source fragment: {sample_medical_fragment['id']}")
    print(f"Transferred template: {transferred[0]}")
    
    print("\n=== Gap Analysis ===")
    existing_legal = [
        {'credibility_class': 'statutory_law', 'reasoning_role': 'definition'},
        {'credibility_class': 'case_precedent', 'reasoning_role': 'definition'}
    ]
    
    gaps = engine.identify_target_gaps('legal', existing_legal)
    print(f"Identified {len(gaps)} gaps in legal domain:")
    for gap in gaps[:3]:
        print(f"  - {gap['suggestion']}")
