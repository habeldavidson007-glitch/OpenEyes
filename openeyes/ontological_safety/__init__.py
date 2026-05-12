"""
Phase 4: Ontological Safety (Safety as Instinct, not Check)

Makes safety a structural constraint in the answer assembly process.
Instead of post-hoc filtering, safety is built into the Würfelspiel combinatorial logic.
If required safety fragments don't exist, the answer literally cannot be constructed.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SafetyConstraint:
    """Defines a structural safety requirement for a domain/topic."""
    constraint_id: str
    domain: str
    topic_keywords: List[str]
    required_fragment_tags: List[str]  # e.g., ["peer_reviewed_study", "safety_warning"]
    required_reasoning_roles: List[str]  # e.g., ["counter_argument"]
    minimum_credibility_class: str
    maximum_age_years: int
    fatal_if_missing: bool  # If True, halt immediately if constraint not met


class OntologicalSafety:
    """
    Ontological Safety System for OpenEyes.
    
    Enforces safety as a structural constraint rather than a post-hoc filter.
    The assembler physically cannot construct answers that violate safety rules.
    """
    
    def __init__(self, constraints_path: str = None):
        # Dynamic path resolution if not provided
        if constraints_path is None:
            import openeyes
            package_dir = Path(openeyes.__file__).parent
            constraints_path = str(package_dir / "domain_rules" / "safety_constraints.json")
        
        self.constraints_path = constraints_path
        self.constraints = self._load_constraints()
        
    def _load_constraints(self) -> List[SafetyConstraint]:
        """Load safety constraints from JSON or create defaults."""
        if os.path.exists(self.constraints_path):
            with open(self.constraints_path, 'r') as f:
                data = json.load(f)
                return [SafetyConstraint(**c) for c in data]
        
        # Default safety constraints for high-stakes domains
        default_constraints = [
            {
                "constraint_id": "MED-001",
                "domain": "medical",
                "topic_keywords": ["cancer", "tumor", "oncology", "chemotherapy"],
                "required_fragment_tags": ["peer_reviewed_study", "clinical_guideline"],
                "required_reasoning_roles": ["definition", "counter_argument"],
                "minimum_credibility_class": "clinical_guideline",
                "maximum_age_years": 3,
                "fatal_if_missing": True
            },
            {
                "constraint_id": "MED-002",
                "domain": "medical",
                "topic_keywords": ["drug", "medication", "dosage", "prescription"],
                "required_fragment_tags": ["safety_warning", "contraindication"],
                "required_reasoning_roles": ["definition", "counter_argument"],
                "minimum_credibility_class": "clinical_guideline",
                "maximum_age_years": 2,
                "fatal_if_missing": True
            },
            {
                "constraint_id": "MED-003",
                "domain": "medical",
                "topic_keywords": ["interaction", "side effect", "adverse"],
                "required_fragment_tags": ["fatal_interaction", "warning"],
                "required_reasoning_roles": ["counter_argument"],
                "minimum_credibility_class": "clinical_guideline",
                "maximum_age_years": 2,
                "fatal_if_missing": True
            },
            {
                "constraint_id": "ENG-001",
                "domain": "engineering",
                "topic_keywords": ["load", "stress", "structural", "beam", "concrete"],
                "required_fragment_tags": ["safety_factor", "code_compliance"],
                "required_reasoning_roles": ["definition", "counter_argument"],
                "minimum_credibility_class": "building_code",
                "maximum_age_years": 5,
                "fatal_if_missing": True
            },
            {
                "constraint_id": "ENG-002",
                "domain": "engineering",
                "topic_keywords": ["failure", "collapse", "fracture"],
                "required_fragment_tags": ["failure_mode", "safety_warning"],
                "required_reasoning_roles": ["counter_argument"],
                "minimum_credibility_class": "peer_reviewed_study",
                "maximum_age_years": 10,
                "fatal_if_missing": True
            }
        ]
        
        # Save default constraints
        os.makedirs(os.path.dirname(self.constraints_path), exist_ok=True)
        with open(self.constraints_path, 'w') as f:
            json.dump(default_constraints, f, indent=2)
        
        return [SafetyConstraint(**c) for c in default_constraints]
    
    def get_applicable_constraints(self, query_text: str, domain: str) -> List[SafetyConstraint]:
        """
        Find all safety constraints that apply to this query.
        
        Args:
            query_text: The original user query
            domain: The detected domain
            
        Returns:
            List of applicable SafetyConstraint objects
        """
        applicable = []
        query_lower = query_text.lower()
        
        for constraint in self.constraints:
            # Check domain match
            if constraint.domain != domain:
                continue
            
            # Check if any topic keywords appear in query
            for keyword in constraint.topic_keywords:
                if keyword.lower() in query_lower:
                    applicable.append(constraint)
                    break  # Only add once per constraint
        
        return applicable
    
    def validate_fragment_set(
        self, 
        fragments: List[Dict], 
        constraints: List[SafetyConstraint]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that a set of fragments satisfies all safety constraints.
        
        Args:
            fragments: List of fragment dictionaries
            constraints: List of applicable SafetyConstraint objects
            
        Returns:
            Tuple of (is_valid, list_of_violation_messages)
        """
        violations = []
        
        for constraint in constraints:
            # Check if we have required reasoning roles
            available_roles = set(f.get('reasoning_role', '') for f in fragments)
            missing_roles = set(constraint.required_reasoning_roles) - available_roles
            
            if missing_roles:
                msg = (f"Constraint {constraint.constraint_id}: Missing required "
                      f"reasoning roles: {missing_roles}")
                if constraint.fatal_if_missing:
                    violations.append(msg)
                else:
                    violations.append(f"WARNING: {msg}")
            
            # Check if we have required tags
            available_tags = set()
            for f in fragments:
                available_tags.update(f.get('tags', []))
            
            missing_tags = set(constraint.required_fragment_tags) - available_tags
            if missing_tags:
                msg = (f"Constraint {constraint.constraint_id}: Missing required "
                      f"tags: {missing_tags}")
                if constraint.fatal_if_missing:
                    violations.append(msg)
                else:
                    violations.append(f"WARNING: {msg}")
            
            # Check credibility class
            min_cred = constraint.minimum_credibility_class
            cred_hierarchy = {
                "forum": 1,
                "news_article": 2,
                "textbook": 3,
                "government_source": 4,
                "clinical_guideline": 5,
                "building_code": 5,
                "peer_reviewed_study": 6
            }
            
            min_level = cred_hierarchy.get(min_cred, 5)
            for f in fragments:
                frag_cred = f.get('credibility_class', 'textbook')
                frag_level = cred_hierarchy.get(frag_cred, 3)
                if frag_level < min_level:
                    msg = (f"Constraint {constraint.constraint_id}: Fragment "
                          f"{f.get('fragment_id')} has insufficient credibility "
                          f"({frag_cred} < {min_cred})")
                    if constraint.fatal_if_missing:
                        violations.append(msg)
                    else:
                        violations.append(f"WARNING: {msg}")
            
            # Check recency
            from datetime import datetime
            current_year = datetime.now().year
            for f in fragments:
                frag_year = f.get('year', current_year)
                age = current_year - frag_year
                if age > constraint.maximum_age_years:
                    msg = (f"Constraint {constraint.constraint_id}: Fragment "
                          f"{f.get('fragment_id')} is too old ({age} years > "
                          f"{constraint.maximum_age_years} years)")
                    if constraint.fatal_if_missing:
                        violations.append(msg)
                    else:
                        violations.append(f"WARNING: {msg}")
        
        return len(violations) == 0, violations
    
    def can_construct_answer(self, 
                            available_fragments: List[Dict], 
                            query_text: str, 
                            domain: str) -> Tuple[bool, str]:
        """
        Determine if an answer can be structurally constructed given safety constraints.
        
        This is the core "ontological" check - if safety requirements aren't met,
        the answer literally cannot exist in the system.
        
        Args:
            available_fragments: Fragments that passed Monte Carlo evaluation
            query_text: Original user query
            domain: Detected domain
            
        Returns:
            Tuple of (can_construct, reason_if_not)
        """
        constraints = self.get_applicable_constraints(query_text, domain)
        
        if not constraints:
            # No safety constraints apply, answer can be constructed
            return True, ""
        
        is_valid, violations = self.validate_fragment_set(available_fragments, constraints)
        
        if not is_valid:
            reason = "ONTOLOGICAL_SAFETY_VIOLATION: Cannot construct answer due to:\n"
            reason += "\n".join(f"  - {v}" for v in violations)
            reason += "\n\nRequired fragments missing from library."
            return False, reason
        
        return True, ""
    
    def get_safety_requirements_summary(self, query_text: str, domain: str) -> str:
        """
        Get a human-readable summary of safety requirements for this query.
        
        Useful for HALT messages to explain what's needed.
        """
        constraints = self.get_applicable_constraints(query_text, domain)
        
        if not constraints:
            return "No special safety constraints for this query."
        
        summary = "Safety requirements for this query:\n"
        for c in constraints:
            summary += f"\n[{c.constraint_id}] {c.domain.upper()} safety rule:\n"
            summary += f"  - Required reasoning roles: {c.required_reasoning_roles}\n"
            summary += f"  - Required tags: {c.required_fragment_tags}\n"
            summary += f"  - Minimum credibility: {c.minimum_credibility_class}\n"
            summary += f"  - Maximum age: {c.maximum_age_years} years\n"
            summary += f"  - Fatal if missing: {c.fatal_if_missing}\n"
        
        return summary
    
    def add_constraint(self, constraint: SafetyConstraint):
        """Add a new safety constraint."""
        self.constraints.append(constraint)
        self._save_constraints()
    
    def _save_constraints(self):
        """Persist constraints to disk."""
        data = [
            {
                "constraint_id": c.constraint_id,
                "domain": c.domain,
                "topic_keywords": c.topic_keywords,
                "required_fragment_tags": c.required_fragment_tags,
                "required_reasoning_roles": c.required_reasoning_roles,
                "minimum_credibility_class": c.minimum_credibility_class,
                "maximum_age_years": c.maximum_age_years,
                "fatal_if_missing": c.fatal_if_missing
            }
            for c in self.constraints
        ]
        with open(self.constraints_path, 'w') as f:
            json.dump(data, f, indent=2)


# Integration helper for Dice Table assembler
def enforce_ontological_safety(
    available_fragments: List[Dict],
    query_text: str,
    domain: str,
    ontological_safety: OntologicalSafety
) -> Tuple[bool, str, List[Dict]]:
    """
    Enforce ontological safety before answer assembly.
    
    Args:
        available_fragments: Fragments that passed Monte Carlo
        query_text: Original query
        domain: Detected domain
        ontological_safety: OntologicalSafety instance
        
    Returns:
        Tuple of (can_proceed, error_message, filtered_fragments)
    """
    can_construct, reason = ontological_safety.can_construct_answer(
        available_fragments, query_text, domain
    )
    
    if not can_construct:
        return False, reason, []
    
    # Filter fragments to only those that satisfy constraints
    constraints = ontological_safety.get_applicable_constraints(query_text, domain)
    
    if not constraints:
        return True, "", available_fragments
    
    # For now, return all fragments if constraints are satisfied
    # Future: could filter out non-compliant fragments here
    return True, "", available_fragments
