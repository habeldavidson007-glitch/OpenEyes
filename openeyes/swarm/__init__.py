"""
OpenEyes Swarm — Query Decomposition and Fragment Retrieval

Layer 1 of the OpenEyes engine. Decomposes user queries into atomic
sub-questions and dispatches agents to retrieve candidate fragments.

Agent Types:
- LibraryAgent: Retrieves from local fragment library (fastest)
- APIAgent: Retrieves from external domain APIs (requires API keys)
- WebAgent: Retrieves from live internet (slowest, credibility scoring required)
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openeyes.fragment_library import FragmentLibrary, Fragment


@dataclass
class FragmentCandidate:
    """A candidate fragment returned by a swarm agent."""
    fragment_id: str
    content: str
    source: str
    source_url: str
    credibility_estimate: float  # 0.0 to 1.0
    domain_tags: List[str]
    agent_type: str  # "library", "api", "web"
    sub_question: str  # Which sub-question this addresses
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fragment_id": self.fragment_id,
            "content": self.content,
            "source": self.source,
            "source_url": self.source_url,
            "credibility_estimate": self.credibility_estimate,
            "domain_tags": self.domain_tags,
            "agent_type": self.agent_type,
            "sub_question": self.sub_question
        }


class LibraryAgent:
    """
    Retrieves fragments from the local fragment library.
    
    Fastest agent type. Returns pre-verified fragments.
    """
    
    def __init__(self, library: FragmentLibrary):
        self.library = library
    
    def retrieve(self, sub_question: str, domain: Optional[str] = None) -> List[FragmentCandidate]:
        """
        Retrieve fragments matching a sub-question.
        
        Args:
            sub_question: The atomic sub-question to answer
            domain: Optional domain filter
            
        Returns:
            List of FragmentCandidates from the library
        """
        candidates = []
        
        # Extract keywords from sub-question
        keywords = self._extract_keywords(sub_question)
        
        # Search library by keywords
        for keyword in keywords:
            fragments = self.library.search_fragments(
                query=keyword,
                domain=domain
            )
            
            for frag in fragments:
                # Map credibility class to estimate
                credibility_map = {
                    "clinical_guideline": 0.95,
                    "peer_reviewed_study": 0.85,
                    "textbook": 0.80,
                    "expert_consensus": 0.70,
                    "case_report": 0.50,
                    "anecdotal": 0.30
                }
                cred_estimate = credibility_map.get(frag.credibility_class, 0.50)
                
                candidate = FragmentCandidate(
                    fragment_id=frag.id,
                    content=frag.content,
                    source=frag.source,
                    source_url=frag.source_url,
                    credibility_estimate=cred_estimate,
                    domain_tags=[frag.domain] + frag.tags,
                    agent_type="library",
                    sub_question=sub_question
                )
                candidates.append(candidate)
        
        # Remove duplicates by fragment_id
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c.fragment_id not in seen:
                seen.add(c.fragment_id)
                unique_candidates.append(c)
        
        return unique_candidates
    
    @staticmethod
    def _extract_keywords(question: str) -> List[str]:
        """Extract meaningful keywords from a question."""
        # Remove common stop words
        stop_words = {
            "what", "is", "are", "the", "a", "an", "for", "with", 
            "in", "on", "at", "to", "of", "and", "or", "but",
            "how", "which", "when", "where", "why", "can", "could",
            "should", "would", "may", "might", "must", "shall"
        }
        
        # Simple tokenization
        words = re.findall(r'\b[a-zA-Z]+\b', question.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords[:5]  # Limit to top 5 keywords


class APIAgent:
    """
    Retrieves fragments from external domain APIs.
    
    Examples: PubMed for medical, legal databases for law.
    Requires API keys configuration.
    """
    
    def __init__(self, api_configs: Optional[Dict[str, Any]] = None):
        """
        Initialize with API configurations.
        
        Args:
            api_configs: Dict with API endpoint configs per domain
        """
        self.api_configs = api_configs or {}
    
    def retrieve(self, sub_question: str, domain: str) -> List[FragmentCandidate]:
        """
        Retrieve fragments from external APIs.
        
        Note: This is a placeholder implementation. Real implementation
        would call actual APIs (PubMed, legal databases, etc.).
        
        Args:
            sub_question: The atomic sub-question to answer
            domain: Domain to determine which API to use
            
        Returns:
            List of FragmentCandidates from APIs
        """
        # Placeholder - in production, this would call real APIs
        # For now, return empty list with a note
        print(f"[APIAgent] Would query external APIs for domain '{domain}': {sub_question}")
        return []
    
    def configure_api(self, domain: str, config: Dict[str, Any]):
        """Configure API settings for a domain."""
        self.api_configs[domain] = config


class WebAgent:
    """
    Retrieves fragments from live internet sources.
    
    Slowest agent type. Used only when library gaps are detected.
    Requires credibility scoring via cross-referencing.
    """
    
    def __init__(self, min_sources: int = 3):
        """
        Initialize web agent.
        
        Args:
            min_sources: Minimum number of independent sources to verify a claim
        """
        self.min_sources = min_sources
    
    def retrieve(self, sub_question: str, domain: str) -> List[FragmentCandidate]:
        """
        Retrieve fragments from web sources.
        
        Note: This is a placeholder implementation. Real implementation
        would perform web searches and cross-reference claims.
        
        Args:
            sub_question: The atomic sub-question to answer
            domain: Domain for context
            
        Returns:
            List of FragmentCandidates from web (with reduced credibility)
        """
        # Placeholder - in production, this would:
        # 1. Search web for the sub_question
        # 2. Extract claims from search results
        # 3. Cross-reference claims across multiple sources
        # 4. Assign credibility based on source authority and consensus
        
        print(f"[WebAgent] Would search web for: {sub_question}")
        return []


class Swarm:
    """
    Query decomposition and fragment retrieval engine.
    
    Decomposes user queries into atomic sub-questions and dispatches
    agents to retrieve candidate fragments in parallel.
    """
    
    def __init__(
        self,
        fragment_library: FragmentLibrary,
        internet_access: bool = False,
        api_configs: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Swarm.
        
        Args:
            fragment_library: The fragment library to search
            internet_access: Whether to allow web searches (default False)
            api_configs: Optional API configurations for external APIs
        """
        self.library = fragment_library
        self.internet_access = internet_access
        
        # Initialize agents
        self.library_agent = LibraryAgent(fragment_library)
        self.api_agent = APIAgent(api_configs)
        self.web_agent = WebAgent() if internet_access else None
    
    def decompose_query(self, query: str) -> List[str]:
        """
        Decompose a user query into atomic sub-questions.
        
        Uses simple heuristic decomposition. In production, this could
        use an LLM for more sophisticated decomposition.
        
        Args:
            query: The user's original query
            
        Returns:
            List of atomic sub-questions
        """
        sub_questions = []
        
        # Heuristic: Look for compound questions with "and", "or", commas
        # This is a simple implementation; production would use NLP
        
        # Check for "and" conjunctions
        if " and " in query.lower():
            parts = re.split(r'\s+and\s+', query, flags=re.IGNORECASE)
            sub_questions.extend(parts)
        # Check for comma-separated clauses
        elif "," in query:
            parts = query.split(",")
            sub_questions.extend([p.strip() for p in parts if p.strip()])
        else:
            # Single question - try to identify implicit sub-questions
            sub_questions = self._decompose_single_query(query)
        
        # Ensure we have at least one sub-question
        if not sub_questions:
            sub_questions = [query]
        
        return sub_questions
    
    def _decompose_single_query(self, query: str) -> List[str]:
        """
        Attempt to decompose a single query into implicit sub-questions.
        
        Uses pattern matching for common query structures.
        """
        sub_questions = []
        query_lower = query.lower()
        
        # Pattern: "safest X for Y with Z" → "What X treats Y?" + "What contraindications with Z?"
        safest_match = re.search(r'safest\s+(\w+)\s+for\s+(.+?)\s+with\s+(.+)', query_lower)
        if safest_match:
            target = safest_match.group(1)
            condition = safest_match.group(2)
            contraindication = safest_match.group(3)
            
            sub_questions = [
                f"What {target}s treat {condition}?",
                f"What is contraindicated with {contraindication}?",
                f"What safety thresholds apply?"
            ]
            return sub_questions
        
        # Pattern: "best X for Y" → "What are options for X?" + "Which X is best for Y?"
        best_match = re.search(r'best\s+(\w+)\s+for\s+(.+)', query_lower)
        if best_match:
            target = best_match.group(1)
            condition = best_match.group(2)
            
            sub_questions = [
                f"What {target}s exist?",
                f"Which {target} is most effective for {condition}?",
                f"What are the risks of {target}s?"
            ]
            return sub_questions
        
        # Default: return original as single sub-question
        return [query]
    
    def decompose_and_retrieve(
        self,
        query: str,
        domain: Optional[str] = None
    ) -> List[FragmentCandidate]:
        """
        Decompose a query and retrieve candidate fragments.
        
        Args:
            query: The user's original query
            domain: Optional domain filter
            
        Returns:
            List of all candidate fragments from all agents
        """
        # Step 1: Decompose query
        sub_questions = self.decompose_query(query)
        
        # Step 2: Dispatch agents for each sub-question
        all_candidates = []
        
        for sub_q in sub_questions:
            # Library agent (always runs)
            library_candidates = self.library_agent.retrieve(sub_q, domain)
            all_candidates.extend(library_candidates)
            
            # API agent (runs if domain has configured APIs)
            if domain and domain in self.api_agent.api_configs:
                api_candidates = self.api_agent.retrieve(sub_q, domain)
                all_candidates.extend(api_candidates)
            
            # Web agent (only if internet_access enabled AND library found nothing)
            if self.internet_access and not library_candidates:
                print(f"[Swarm] Library gap detected for: {sub_q}")
                web_candidates = self.web_agent.retrieve(sub_q, domain)
                all_candidates.extend(web_candidates)
        
        # Step 3: Cross-verification check
        # If multiple agents retrieved claims about same sub-question,
        # reduce credibility for conflicting claims
        verified_candidates = self._cross_verify(all_candidates)
        
        return verified_candidates
    
    def _cross_verify(self, candidates: List[FragmentCandidate]) -> List[FragmentCandidate]:
        """
        Cross-verify candidates and adjust credibility for conflicts.
        
        When multiple sources make conflicting claims, reduce credibility.
        """
        # Group by sub-question
        by_subquestion: Dict[str, List[FragmentCandidate]] = {}
        for c in candidates:
            if c.sub_question not in by_subquestion:
                by_subquestion[c.sub_question] = []
            by_subquestion[c.sub_question].append(c)
        
        verified = []
        for sub_q, cands in by_subquestion.items():
            if len(cands) <= 1:
                # No conflict possible
                verified.extend(cands)
            else:
                # Check for conflicts (simplified: different content = potential conflict)
                contents = set(c.content.lower().strip() for c in cands)
                
                if len(contents) > 1:
                    # Potential conflict - reduce credibility
                    for c in cands:
                        c.credibility_estimate *= 0.7  # Reduce by 30%
                
                verified.extend(cands)
        
        return verified
    
    def get_decomposition(self, query: str) -> Dict[str, Any]:
        """
        Get the decomposition of a query without retrieving fragments.
        
        Useful for debugging and logging.
        """
        sub_questions = self.decompose_query(query)
        return {
            "original_query": query,
            "sub_questions": sub_questions,
            "num_sub_questions": len(sub_questions)
        }
