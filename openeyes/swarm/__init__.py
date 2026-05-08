"""
Swarm — Layer 1: Query Decomposition and Fragment Retrieval

The Swarm breaks user queries into atomic sub-questions and dispatches 
lightweight agents to retrieve candidate knowledge fragments from:
- Local fragment library (fastest, pre-verified)
- External domain APIs (PubMed, legal databases, etc.)
- Live internet sources (slowest, requires credibility scoring)

Each agent is independent, runs in parallel, and does not share state.
The Swarm collects candidates but does not evaluate correctness.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import hashlib


@dataclass
class FragmentCandidate:
    """A candidate knowledge fragment retrieved by a Swarm agent."""
    fragment_id: str
    content: str
    source: str
    source_url: Optional[str] = None
    credibility_estimate: float = 0.5
    domain_tags: List[str] = field(default_factory=list)
    agent_type: str = "unknown"  # library, api, web
    metadata: Dict[str, Any] = field(default_factory=dict)


class LibraryAgent:
    """Retrieves fragments from the local fragment library."""
    
    def __init__(self, fragment_library):
        """
        Args:
            fragment_library: FragmentLibrary instance
        """
        self.library = fragment_library
    
    def retrieve(self, sub_question: str) -> List[FragmentCandidate]:
        """
        Retrieve fragments matching a sub-question.
        
        Args:
            sub_question: Atomic sub-question string
            
        Returns:
            List of FragmentCandidate objects
        """
        fragments = self.library.search(sub_question)
        candidates = []
        
        for frag in fragments:
            candidate = FragmentCandidate(
                fragment_id=frag["id"],
                content=frag["content"],
                source=frag.get("source", "Unknown"),
                source_url=frag.get("source_url"),
                credibility_estimate=self._estimate_credibility(frag),
                domain_tags=frag.get("tags", []),
                agent_type="library",
                metadata={"last_verified": frag.get("last_verified"), "weight": frag.get("weight", 1.0)}
            )
            candidates.append(candidate)
        
        return candidates
    
    def _estimate_credibility(self, fragment: Dict) -> float:
        """Estimate credibility based on fragment metadata."""
        credibility_class = fragment.get("credibility_class", "")
        
        # Credibility mapping per spec
        credibility_map = {
            "clinical_guideline": 0.95,
            "peer_reviewed_study": 0.90,
            "official_documentation": 0.85,
            "textbook": 0.80,
            "expert_consensus": 0.75,
            "web_source": 0.50,
        }
        
        base_score = credibility_map.get(credibility_class, 0.5)
        
        # Adjust for recency
        last_verified = fragment.get("last_verified")
        if last_verified:
            # Simple decay model - reduce credibility if not verified in >1 year
            from datetime import datetime
            try:
                verified_date = datetime.fromisoformat(last_verified)
                days_old = (datetime.now() - verified_date).days
                if days_old > 365:
                    base_score *= 0.9  # 10% reduction
                if days_old > 730:
                    base_score *= 0.9  # Another 10% reduction
            except (ValueError, TypeError):
                pass
        
        return min(1.0, max(0.0, base_score))


class APIAgent:
    """Retrieves fragments from external domain APIs."""
    
    def __init__(self, domain: str = "general", api_configs: Optional[Dict] = None):
        """
        Args:
            domain: Domain type (medical, legal, engineering, etc.)
            api_configs: Optional dict with API keys and endpoints
        """
        self.domain = domain
        self.api_configs = api_configs or {}
        self._available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if required API keys are configured."""
        # Placeholder - would check for actual API keys
        return bool(self.api_configs.get("api_key"))
    
    def retrieve(self, sub_question: str) -> List[FragmentCandidate]:
        """
        Retrieve fragments from external APIs.
        
        Args:
            sub_question: Atomic sub-question string
            
        Returns:
            List of FragmentCandidate objects
        """
        if not self._available:
            return []
        
        # Placeholder implementation
        # In production: call PubMed API for medical, legal databases for legal, etc.
        candidates = []
        
        # Simulated API response
        if self.domain == "medical":
            candidates.append(FragmentCandidate(
                fragment_id=f"api_med_{hashlib.md5(sub_question.encode()).hexdigest()[:8]}",
                content="[API Retrieved Content]",
                source="PubMed API",
                source_url="https://pubmed.ncbi.nlm.nih.gov/",
                credibility_estimate=0.85,
                domain_tags=["medical", "peer_reviewed"],
                agent_type="api"
            ))
        
        return candidates


class WebAgent:
    """Retrieves fragments from live internet sources."""
    
    def __init__(self, credibility_threshold: float = 0.6):
        """
        Args:
            credibility_threshold: Minimum credibility for web sources
        """
        self.credibility_threshold = credibility_threshold
        self._available = True  # Always available but low credibility
    
    def retrieve(self, sub_question: str) -> List[FragmentCandidate]:
        """
        Retrieve fragments from web sources.
        
        Args:
            sub_question: Atomic sub-question string
            
        Returns:
            List of FragmentCandidate objects
        """
        # Placeholder implementation
        # In production: use search APIs, scrape authoritative sources
        # Apply cross-verification: require ≥3 independent sources
        
        candidates = []
        
        # Simulated web retrieval with reduced credibility
        candidates.append(FragmentCandidate(
            fragment_id=f"web_{hashlib.md5(sub_question.encode()).hexdigest()[:8]}",
            content="[Web Retrieved Content]",
            source="Web Search",
            source_url=None,
            credibility_estimate=0.50,  # Base web credibility
            domain_tags=["web"],
            agent_type="web",
            metadata={"requires_verification": True}
        ))
        
        return candidates


class Swarm:
    """
    Query decomposition and fragment retrieval engine.
    
    Decomposes user queries into atomic sub-questions and dispatches
    agents to retrieve candidate fragments in parallel.
    """
    
    def __init__(self, fragment_library=None, internet_access: bool = True, 
                 domain: str = "general", api_configs: Optional[Dict] = None):
        """
        Initialize Swarm.
        
        Args:
            fragment_library: FragmentLibrary instance
            internet_access: Whether to allow web-based retrieval
            domain: Domain type for API agent configuration
            api_configs: Optional API configurations
        """
        self.fragment_library = fragment_library
        self.internet_access = internet_access
        self.domain = domain
        self.api_configs = api_configs or {}
        
        # Initialize agents
        self.library_agent = LibraryAgent(fragment_library) if fragment_library else None
        self.api_agent = APIAgent(domain=domain, api_configs=api_configs)
        self.web_agent = WebAgent() if internet_access else None
    
    def decompose_and_retrieve(self, query: str) -> List[FragmentCandidate]:
        """
        Decompose query and retrieve candidate fragments.
        
        Args:
            query: User's natural language query
            
        Returns:
            List of FragmentCandidate objects from all agents
        """
        # Step 1: Decompose query into sub-questions
        sub_questions = self._decompose_query(query)
        
        # Step 2: Dispatch agents in parallel (simulated sequential for now)
        all_candidates = []
        
        for sub_q in sub_questions:
            # Library agent
            if self.library_agent:
                candidates = self.library_agent.retrieve(sub_q)
                all_candidates.extend(candidates)
            
            # API agent
            api_candidates = self.api_agent.retrieve(sub_q)
            all_candidates.extend(api_candidates)
            
            # Web agent (only if library gaps detected)
            if self.web_agent and len(all_candidates) < 2:
                web_candidates = self.web_agent.retrieve(sub_q)
                all_candidates.extend(web_candidates)
        
        # Step 3: Cross-verification - check for conflicting claims
        verified_candidates = self._cross_verify(all_candidates)
        
        return verified_candidates
    
    def _decompose_query(self, query: str) -> List[str]:
        """
        Decompose a query into atomic sub-questions.
        
        Args:
            query: User's natural language query
            
        Returns:
            List of atomic sub-question strings
        """
        # Placeholder implementation
        # In production: use NLP parsing or LLM for decomposition
        
        # Simple heuristic: split on conjunctions and question words
        sub_questions = []
        
        # For demo: treat the whole query as one sub-question
        # Real implementation would parse and decompose
        if query.strip():
            sub_questions.append(query.strip())
        
        # Example decomposition logic (commented out for now):
        # if " and " in query.lower():
        #     parts = query.lower().split(" and ")
        #     sub_questions.extend([p.strip() + "?" for p in parts])
        # else:
        #     sub_questions.append(query)
        
        return sub_questions
    
    def _cross_verify(self, candidates: List[FragmentCandidate]) -> List[FragmentCandidate]:
        """
        Run consistency checks on candidates about the same sub-question.
        
        Conflicting claims both get forwarded with reduced credibility.
        
        Args:
            candidates: List of FragmentCandidate objects
            
        Returns:
            List of verified (or credibility-adjusted) candidates
        """
        # Group candidates by content similarity
        # Placeholder: simple deduplication
        
        seen_content = set()
        verified = []
        
        for candidate in candidates:
            content_hash = hashlib.md5(candidate.content.encode()).hexdigest()
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                verified.append(candidate)
            else:
                # Duplicate found - could increase credibility of existing
                # For now, just skip
                pass
        
        return verified


__all__ = ["Swarm", "FragmentCandidate", "LibraryAgent", "APIAgent", "WebAgent"]