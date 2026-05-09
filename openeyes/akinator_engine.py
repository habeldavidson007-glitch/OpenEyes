"""
OpenEyes Akinator Engine: Binary Search Decision Tree for Query Refinement

This module implements:
1. Decision Tree Navigation: Cuts search space in half with each question
2. Query Refinement Mask: Creates precise search masks before fragment retrieval
3. Cognitive Efficiency Scoring (CES): Ranks fragments by relevance and evidence
4. Dynamic Pruning: Eliminates irrelevant scenarios before Monte Carlo simulation

Inspired by Akinator's binary search logic, this transforms OpenEyes from passive
retrieval to active reasoning - from librarian to detective.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class DecisionNodeType(Enum):
    """Types of decision nodes in the tree."""
    ROOT = "root"
    DOMAIN_FILTER = "domain_filter"
    RISK_LEVEL = "risk_level"
    TIME_HORIZON = "time_horizon"
    EVIDENCE_STRENGTH = "evidence_strength"
    URGENCY = "urgency"
    COMPLEXITY = "complexity"
    LEAF = "leaf"


@dataclass
class DecisionNode:
    """A node in the binary decision tree."""
    node_id: str
    node_type: DecisionNodeType
    question: str
    yes_mask: Dict[str, Any]  # Search mask if answer is yes
    no_mask: Dict[str, Any]   # Search mask if answer is no
    left_child: Optional['DecisionNode'] = None
    right_child: Optional['DecisionNode'] = None
    ces_threshold: float = 0.5  # Cognitive Efficiency Score threshold
    priority: int = 0  # Higher priority = asked earlier
    
    def is_leaf(self) -> bool:
        return self.left_child is None and self.right_child is None


@dataclass
class SearchMask:
    """Binary search mask for fragment filtering."""
    domain_filters: List[str] = field(default_factory=list)
    evidence_levels: List[str] = field(default_factory=list)
    source_types: List[str] = field(default_factory=list)
    recency_years: int = 10
    min_ces_score: float = 0.3
    max_results: int = 5
    exclude_patterns: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'domain_filters': self.domain_filters,
            'evidence_levels': self.evidence_levels,
            'source_types': self.source_types,
            'recency_years': self.recency_years,
            'min_ces_score': self.min_ces_score,
            'max_results': self.max_results,
            'exclude_patterns': self.exclude_patterns,
        }


class AkinatorEngine:
    """
    Binary Search Decision Tree Engine for Query Refinement.
    
    Works like Akinator: asks strategic questions to cut the search space
    in half with each iteration, converging on the most relevant fragments
    before Monte Carlo simulation.
    """
    
    def __init__(self):
        self.root = self._build_default_tree()
        self.current_node: Optional[DecisionNode] = None
        self.path_history: List[Tuple[str, str]] = []  # (question, answer)
        self.active_mask = SearchMask()
        
    def _build_default_tree(self) -> DecisionNode:
        """Build the default binary decision tree."""
        
        # Level 1: Domain Classification (highest priority)
        root = DecisionNode(
            node_id="root_001",
            node_type=DecisionNodeType.ROOT,
            question="Is this query about medical/health topics?",
            yes_mask={'domain_filters': ['medical'], 'evidence_levels': ['high', 'moderate']},
            no_mask={'domain_filters': ['investment', 'legal', 'engineering', 'general']},
            priority=10
        )
        
        # Medical branch
        medical_node = DecisionNode(
            node_id="med_001",
            node_type=DecisionNodeType.URGENCY,
            question="Is this about an urgent/emergency medical situation?",
            yes_mask={
                'domain_filters': ['medical'],
                'evidence_levels': ['high'],
                'source_types': ['clinical_guideline', 'government_report'],
                'exclude_patterns': ['preliminary', 'experimental']
            },
            no_mask={
                'domain_filters': ['medical'],
                'evidence_levels': ['high', 'moderate'],
                'source_types': ['peer_reviewed_study', 'textbook', 'systematic_review']
            },
            priority=9
        )
        
        medical_urgent = DecisionNode(
            node_id="med_urg_001",
            node_type=DecisionNodeType.LEAF,
            question="",
            yes_mask={'ces_threshold': 0.8, 'max_results': 3},
            no_mask={},
            priority=8
        )
        
        medical_non_urgent = DecisionNode(
            node_id="med_non_001",
            node_type=DecisionNodeType.EVIDENCE_STRENGTH,
            question="Do you need peer-reviewed research or general information?",
            yes_mask={
                'source_types': ['peer_reviewed_study', 'systematic_review'],
                'evidence_levels': ['high'],
                'ces_threshold': 0.7
            },
            no_mask={
                'source_types': ['textbook', 'clinical_guideline'],
                'evidence_levels': ['high', 'moderate'],
                'ces_threshold': 0.5
            },
            priority=7
        )
        
        medical_non_urgent.left_child = DecisionNode(
            node_id="med_res_001",
            node_type=DecisionNodeType.LEAF,
            question="",
            yes_mask={'recency_years': 5},
            no_mask={}
        )
        
        medical_non_urgent.right_child = DecisionNode(
            node_id="med_gen_001",
            node_type=DecisionNodeType.LEAF,
            question="",
            yes_mask={'recency_years': 10},
            no_mask={}
        )
        
        medical_node.left_child = medical_urgent
        medical_node.right_child = medical_non_urgent
        
        # Investment branch (from root.no)
        investment_root = DecisionNode(
            node_id="inv_001",
            node_type=DecisionNodeType.RISK_LEVEL,
            question="Are you looking for high-risk/high-reward strategies?",
            yes_mask={
                'domain_filters': ['investment'],
                'source_types': ['peer_reviewed_study', 'dataset_documentation'],
                'exclude_patterns': ['guaranteed', 'risk-free']
            },
            no_mask={
                'domain_filters': ['investment'],
                'source_types': ['government_report', 'textbook', 'statistical_bureau'],
                'evidence_levels': ['high']
            },
            priority=9
        )
        
        investment_high_risk = DecisionNode(
            node_id="inv_high_001",
            node_type=DecisionNodeType.TIME_HORIZON,
            question="Is your investment horizon short-term (<1 year)?",
            yes_mask={
                'ces_threshold': 0.8,
                'recency_years': 2,
                'max_results': 5
            },
            no_mask={
                'ces_threshold': 0.6,
                'recency_years': 5,
                'max_results': 7
            },
            priority=7
        )
        
        investment_low_risk = DecisionNode(
            node_id="inv_low_001",
            node_type=DecisionNodeType.LEAF,
            question="",
            yes_mask={
                'source_types': ['statistical_bureau', 'government_report'],
                'ces_threshold': 0.7
            },
            no_mask={}
        )
        
        investment_high_risk.left_child = DecisionNode(
            node_id="inv_short_001",
            node_type=DecisionNodeType.LEAF,
            question="",
            yes_mask={'exclude_patterns': ['long-term', 'retirement']},
            no_mask={}
        )
        
        investment_high_risk.right_child = DecisionNode(
            node_id="inv_long_001",
            node_type=DecisionNodeType.LEAF,
            question="",
            yes_mask={'exclude_patterns': ['day-trading', 'speculative']},
            no_mask={}
        )
        
        investment_root.left_child = investment_high_risk
        investment_root.right_child = investment_low_risk
        
        # General knowledge branch
        general_root = DecisionNode(
            node_id="gen_001",
            node_type=DecisionNodeType.COMPLEXITY,
            question="Do you need a simple definition or detailed explanation?",
            yes_mask={
                'source_types': ['textbook', 'wikipedia'],
                'max_results': 3,
                'ces_threshold': 0.4
            },
            no_mask={
                'source_types': ['peer_reviewed_study', 'systematic_review', 'technical_manual'],
                'max_results': 7,
                'ces_threshold': 0.6
            },
            priority=8
        )
        
        general_simple = DecisionNode(
            node_id="gen_simple_001",
            node_type=DecisionNodeType.LEAF,
            question="",
            yes_mask={'evidence_levels': ['high', 'moderate']},
            no_mask={}
        )
        
        general_detailed = DecisionNode(
            node_id="gen_det_001",
            node_type=DecisionNodeType.EVIDENCE_STRENGTH,
            question="Is peer-reviewed evidence important?",
            yes_mask={
                'source_types': ['peer_reviewed_study', 'conference_paper'],
                'evidence_levels': ['high'],
                'recency_years': 10
            },
            no_mask={
                'source_types': ['technical_manual', 'standard_specification'],
                'evidence_levels': ['high', 'moderate']
            },
            priority=6
        )
        
        general_detailed.left_child = DecisionNode(
            node_id="gen_peer_001",
            node_type=DecisionNodeType.LEAF,
            question="",
            yes_mask={},
            no_mask={}
        )
        
        general_detailed.right_child = DecisionNode(
            node_id="gen_tech_001",
            node_type=DecisionNodeType.LEAF,
            question="",
            yes_mask={},
            no_mask={}
        )
        
        general_root.left_child = general_simple
        general_root.right_child = general_detailed
        
        # Connect tree
        root.left_child = medical_node
        root.right_child = investment_root  # Simplified: investment as default for non-medical
        
        return root
    
    def reset(self):
        """Reset the decision tree traversal."""
        self.current_node = self.root
        self.path_history = []
        self.active_mask = SearchMask()
    
    def ask_question(self) -> Optional[str]:
        """Get the current question to ask the user."""
        if self.current_node is None or self.current_node.is_leaf():
            return None
        return self.current_node.question
    
    def answer_question(self, answer: bool) -> SearchMask:
        """
        Process user's answer and navigate the tree.
        
        Args:
            answer: True for 'yes', False for 'no'
            
        Returns:
            SearchMask if leaf node reached, None otherwise
        """
        if self.current_node is None or self.current_node.is_leaf():
            return self.active_mask
        
        question = self.current_node.question
        answer_str = "yes" if answer else "no"
        self.path_history.append((question, answer_str))
        
        # Apply mask based on answer
        mask_dict = self.current_node.yes_mask if answer else self.current_node.no_mask
        self._apply_mask(mask_dict)
        
        # Navigate to child
        self.current_node = self.current_node.left_child if answer else self.current_node.right_child
        
        # Check if we reached a leaf
        if self.current_node is None or self.current_node.is_leaf():
            if self.current_node:
                final_mask = self.current_node.yes_mask if answer else self.current_node.no_mask
                self._apply_mask(final_mask)
            return self.active_mask
        
        return None
    
    def _apply_mask(self, mask_dict: Dict[str, Any]):
        """Apply mask updates to the active search mask."""
        if 'domain_filters' in mask_dict:
            self.active_mask.domain_filters = mask_dict['domain_filters']
        if 'evidence_levels' in mask_dict:
            self.active_mask.evidence_levels = mask_dict['evidence_levels']
        if 'source_types' in mask_dict:
            self.active_mask.source_types = mask_dict['source_types']
        if 'recency_years' in mask_dict:
            self.active_mask.recency_years = mask_dict['recency_years']
        if 'min_ces_score' in mask_dict:
            self.active_mask.min_ces_score = mask_dict['min_ces_score']
        if 'max_results' in mask_dict:
            self.active_mask.max_results = mask_dict['max_results']
        if 'exclude_patterns' in mask_dict:
            self.active_mask.exclude_patterns.extend(mask_dict['exclude_patterns'])
        if 'ces_threshold' in mask_dict:
            self.active_mask.min_ces_score = mask_dict['ces_threshold']
    
    def get_final_mask(self) -> SearchMask:
        """Get the accumulated search mask after traversal."""
        return self.active_mask
    
    def get_traversal_path(self) -> List[Tuple[str, str]]:
        """Get the history of questions and answers."""
        return self.path_history.copy()
    
    def compute_ces(self, fragment: Any) -> float:
        """
        Compute Cognitive Efficiency Score for a fragment.
        
        CES = (evidence_weight * recency_weight * relevance_weight) / complexity_penalty
        
        Higher CES = more cognitively efficient to process
        """
        # Evidence weight
        evidence_map = {'high': 1.0, 'moderate': 0.7, 'low': 0.4}
        evidence_weight = evidence_map.get(getattr(fragment, 'evidence_level', 'low'), 0.5)
        
        # Recency weight (exponential decay)
        from datetime import datetime
        try:
            pub_date = getattr(fragment, 'published_on', '')
            if pub_date:
                pub_year = int(pub_date[:4])
                years_old = datetime.now().year - pub_year
                recency_weight = max(0.3, 1.0 - (years_old * 0.05))
            else:
                recency_weight = 0.5
        except:
            recency_weight = 0.5
        
        # Relevance weight (based on feedback)
        feedback = getattr(fragment, 'feedback', {})
        thumbs_up = feedback.get('thumbs_up', 0)
        thumbs_down = feedback.get('thumbs_down', 0)
        total = thumbs_up + thumbs_down
        if total > 0:
            relevance_weight = thumbs_up / total
        else:
            relevance_weight = 0.5
        
        # Complexity penalty (longer claims are harder to process)
        claim = getattr(fragment, 'claim', '')
        claim_length = len(claim.split())
        complexity_penalty = 1.0 + (max(0, claim_length - 50) / 100)
        
        ces = (evidence_weight * recency_weight * relevance_weight) / complexity_penalty
        return round(ces, 3)
    
    def filter_fragments_by_mask(self, fragments: List[Any], mask: SearchMask) -> List[Any]:
        """Filter fragments using the search mask."""
        filtered = []
        
        for frag in fragments:
            # Check domain filters (skip if fragment has no domain attribute)
            if mask.domain_filters:
                frag_domain = getattr(frag, 'domain', None)
                if frag_domain is None:
                    # Try to infer domain from source_type or other attributes
                    source_type = getattr(frag, 'source_type', '')
                    if any(df == 'medical' and 'medical' in source_type.lower() for df in mask.domain_filters):
                        pass  # Keep it, might be medical
                    elif any(df == 'investment' and 'investment' in str(getattr(frag, 'claim', '')).lower() for df in mask.domain_filters):
                        pass  # Keep it, might be investment
                    else:
                        # Be permissive when domain can't be determined
                        pass
                elif not any(df in frag_domain for df in mask.domain_filters):
                    continue
            
            # Check evidence levels
            if mask.evidence_levels:
                frag_evidence = getattr(frag, 'evidence_level', 'low')
                if frag_evidence not in mask.evidence_levels:
                    continue
            
            # Check source types
            if mask.source_types:
                frag_source = getattr(frag, 'source_type', '')
                if not any(st in frag_source for st in mask.source_types):
                    continue
            
            # Check exclusion patterns
            claim = getattr(frag, 'claim', '').lower()
            excluded = False
            for pattern in mask.exclude_patterns:
                if pattern.lower() in claim:
                    excluded = True
                    break
            if excluded:
                continue
            
            # Compute CES and check threshold
            ces = self.compute_ces(frag)
            if ces < mask.min_ces_score:
                continue
            
            filtered.append(frag)
        
        # Sort by CES descending
        filtered.sort(key=lambda f: self.compute_ces(f), reverse=True)
        
        # Limit results
        return filtered[:mask.max_results]


# Global instance
akinator_engine = AkinatorEngine()


def refine_query_with_binary_search(query: str, initial_domain: str) -> Tuple[SearchMask, List[Tuple[str, str]]]:
    """
    Use binary search decision tree to refine query before fragment retrieval.
    
    This is the main entry point for Akinator-style query refinement.
    
    Args:
        query: The user's query
        initial_domain: Initial domain classification
        
    Returns:
        Tuple of (SearchMask, traversal_path)
    """
    akinator_engine.reset()
    
    # Auto-navigate based on query content for common cases
    query_lower = query.lower()
    
    # First question: medical?
    medical_keywords = ['cancer', 'symptom', 'disease', 'treatment', 'antibiotic', 'diagnosis', 'medical', 'health']
    is_medical = any(kw in query_lower for kw in medical_keywords)
    akinator_engine.answer_question(is_medical)
    
    if is_medical:
        # Second question: urgent?
        urgent_keywords = ['emergency', 'urgent', 'immediate', 'critical', 'acute']
        is_urgent = any(kw in query_lower for kw in urgent_keywords)
        result = akinator_engine.answer_question(is_urgent)
        
        if result is None and not akinator_engine.current_node.is_leaf():
            # Ask about evidence type
            research_keywords = ['study', 'research', 'trial', 'experiment']
            wants_research = any(kw in query_lower for kw in research_keywords)
            result = akinator_engine.answer_question(wants_research)
    else:
        # Non-medical: investment?
        investment_keywords = ['invest', 'stock', 'portfolio', 'rich', 'wealth', 'return', 'risk']
        is_investment = any(kw in query_lower for kw in investment_keywords)
        
        if is_investment:
            # Ask about risk level
            high_risk_keywords = ['fast', 'quick', 'high-return', 'aggressive', 'speculative']
            high_risk = any(kw in query_lower for kw in high_risk_keywords)
            result = akinator_engine.answer_question(high_risk)
            
            if result is None and not akinator_engine.current_node.is_leaf():
                # Ask about time horizon
                short_term_keywords = ['short-term', 'quick', 'fast', 'day', 'month']
                short_term = any(kw in query_lower for kw in short_term_keywords)
                result = akinator_engine.answer_question(short_term)
        else:
            # General knowledge
            simple_keywords = ['what is', 'define', 'meaning', 'simple', 'basic']
            wants_simple = any(kw in query_lower for kw in simple_keywords)
            result = akinator_engine.answer_question(wants_simple)
            
            if result is None and not akinator_engine.current_node.is_leaf():
                # Ask about peer-review importance
                academic_keywords = ['research', 'study', 'academic', 'peer-reviewed', 'scientific']
                wants_academic = any(kw in query_lower for kw in academic_keywords)
                result = akinator_engine.answer_question(wants_academic)
    
    final_mask = akinator_engine.get_final_mask()
    path = akinator_engine.get_traversal_path()
    
    return final_mask, path


if __name__ == "__main__":
    # Test the Akinator engine
    print("Testing Akinator Binary Search Engine...")
    
    test_queries = [
        ("What are cancer symptoms?", "medical"),
        ("How to get rich quick with stocks?", "investment"),
        ("Explain antibiotic resistance", "medical"),
        ("Safe long-term investment strategy", "investment"),
    ]
    
    for query, domain in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"Initial Domain: {domain}")
        
        mask, path = refine_query_with_binary_search(query, domain)
        
        print(f"\nTraversal Path ({len(path)} questions):")
        for i, (q, a) in enumerate(path, 1):
            print(f"  {i}. Q: {q}")
            print(f"     A: {a}")
        
        print(f"\nFinal Search Mask:")
        mask_dict = mask.to_dict()
        for key, value in mask_dict.items():
            if value:  # Only show non-empty values
                print(f"  {key}: {value}")
    
    print(f"\n{'='*60}")
    print("Akinator Engine Test Complete!")
