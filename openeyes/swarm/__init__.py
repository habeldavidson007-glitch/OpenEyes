"""
OpenEyes Swarm — Query Decomposition and Fragment Retrieval

Layer 1 of the OpenEyes engine. Decomposes user queries into atomic
sub-questions and dispatches agents to retrieve candidate fragments.

Agent Types:
- LibraryAgent: Retrieves from local fragment library (fastest)
- APIAgent: Retrieves from external domain APIs (requires API keys)
- WebAgent: Retrieves from live internet (slowest, credibility scoring required)

Signal-Pulse Swarm Architecture (Autonomous Cyclic Operation):
- PulseScheduler: Manages autonomous WAKE→HARVEST→PROCESS→ARCHIVE→HIBERNATE cycles
- SignalBus: Lightweight async event signaling between agents
- Harvester Agents: Dormant until triggered, collect evidence from sources
- Processor Agents: Validate and convert evidence to fragments
- Archiver Agent: Persist fragments to storage with WAL-friendly buffering
"""

import re
import urllib.request
import urllib.error
from html import unescape
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openeyes.fragment_library import FragmentLibrary, Fragment
from openeyes.core.kap import build_kap, KnowledgeAcquisitionPlan, kap_to_trace

# Import Signal-Pulse Swarm components for easy access
from openeyes.swarm.pulse_scheduler import (
    PulseScheduler,
    PulseState,
    SignalBus,
    PulseSignal,
    SignalType,
    start_autonomous_loop,
    run_pulse_loop,
)

from openeyes.swarm.harvesters import (
    HarvesterAgent,
    FileSystemHarvester,
    LibraryHarvester,
    KnowledgeHarvester,
    HarvestedEvidence,
    create_harvesters,
)

from openeyes.swarm.processors import (
    FragmentProcessor,
    ConsolidationProcessor,
    FragmentArchiver,
    ProcessingResult,
    create_processors,
    create_archiver,
    create_consolidator,
)


# Trusted Finance Sources Whitelist
TRUSTED_FINANCE_SOURCES = [
    "https://www.federalreserve.gov",
    "https://www.sec.gov/cgi-bin/browse-edgar",
    "https://www.bls.gov",
    "https://www.bea.gov",
    "https://fred.stlouisfed.org"
]

# Credibility scores by source domain
SOURCE_CREDIBILITY = {
    "federalreserve.gov": 0.95,
    "sec.gov": 0.92,
    "bls.gov": 0.90,
    "bea.gov": 0.90,
    "fred.stlouisfed.org": 0.88
}

# Stop words for topic extraction
STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "for", "with", 
    "in", "on", "at", "to", "of", "and", "or", "but",
    "how", "which", "when", "where", "why", "can", "could",
    "should", "would", "may", "might", "must", "shall",
    "i", "me", "my", "we", "us", "our", "you", "your",
    "he", "she", "it", "they", "them", "their"
}


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
    reasoning_role: str = "definition"  # "definition", "counter_argument", "latest_data"
    source_type: str = "primary"  # "primary", "secondary", "tertiary"
    year: int = 2026  # Publication/recency year
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fragment_id": self.fragment_id,
            "content": self.content,
            "source": self.source,
            "source_url": self.source_url,
            "credibility_estimate": self.credibility_estimate,
            "domain_tags": self.domain_tags,
            "agent_type": self.agent_type,
            "sub_question": self.sub_question,
            "reasoning_role": self.reasoning_role,
            "source_type": self.source_type,
            "year": self.year
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
        
        Uses semantic inverted index for precise retrieval.
        Falls back to broad keyword scan if initial search yields too few results.
        
        Args:
            sub_question: The atomic sub-question to answer
            domain: Optional domain filter
            
        Returns:
            List of FragmentCandidates from the library
        """
        candidates = []
        
        # Use semantic index to find relevant fragments
        fragment_ids = self.library.search_by_semantic_index(sub_question)
        
        # If no results from semantic search, fall back to keyword extraction
        if not fragment_ids:
            keywords = self._extract_keywords(sub_question)
            for keyword in keywords:
                fragments = self.library.search_fragments(
                    query=keyword,
                    domain=domain
                )
                for frag in fragments:
                    if frag.id not in fragment_ids:
                        fragment_ids.append(frag.id)
        
        # SEMANTIC INDEX FALLBACK: If still fewer than 3 candidates, do a broad scan
        if len(fragment_ids) < 3:
            print(f"[LibraryAgent] Low candidate count ({len(fragment_ids)}), triggering semantic fallback...")
            # Scan all fragments for partial matches on tags and content
            for frag_id, frag in self.library._fragments.items():
                if frag_id in fragment_ids:
                    continue
                
                # Check domain filter first
                if domain and frag.domain != domain:
                    continue
                
                # Check for keyword matches in tags, content, or sub_question
                question_lower = sub_question.lower()
                matched = False
                
                # Check tags
                for tag in frag.tags:
                    if tag.replace('_', ' ') in question_lower or tag in question_lower:
                        matched = True
                        break
                
                # Check content snippet
                if not matched and question_lower in frag.content.lower():
                    matched = True
                
                # Check sub_question field
                if not matched and frag.sub_question:
                    if any(word in frag.sub_question.lower() for word in question_lower.split()):
                        matched = True
                
                if matched:
                    fragment_ids.append(frag.id)
                    print(f"[LibraryAgent] Fallback match: {frag.id}")
        
        # Build candidates from fragment IDs
        for frag_id in fragment_ids:
            frag = self.library.get_fragment(frag_id)
            if not frag:
                continue
            
            # Apply domain filter if specified
            if domain and domain != "general" and frag.domain != domain:
                continue
            
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
                sub_question=sub_question,
                reasoning_role=frag.reasoning_role or "definition",
                source_type=frag.source_type or "primary",
                year=frag.year or 2026
            )
            candidates.append(candidate)
        
        print(f"[LibraryAgent] Retrieved {len(candidates)} candidates for: {sub_question[:50]}...")
        return candidates
    
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
        
        # Enhanced extraction: preserve underscores for compound terms
        # and extract multi-word phrases
        question_lower = question.lower()
        
        # First, extract compound terms with underscores (e.g., pancreatic_cancer)
        compound_terms = re.findall(r'\b[a-z]+_[a-z]+\b', question_lower)
        
        # Extract multi-word phrases (2-3 words) that might be important
        # e.g., "cold weather", "steel beam", "intermittent fasting"
        phrases = re.findall(r'\b([a-z]{3,}(?:\s+[a-z]{3,}){1,2})\b', question_lower)
        
        # Simple tokenization for single words
        words = re.findall(r'\b[a-zA-Z]+(?:_[a-zA-Z]+)*\b', question_lower)
        
        # Combine all keyword types
        all_keywords = []
        all_keywords.extend(compound_terms)  # Keep underscores for compounds
        all_keywords.extend([p.replace(' ', '_') for p in phrases if len(p.split()) > 1])  # Convert phrases to underscore format
        all_keywords.extend([w for w in words if w not in stop_words and len(w) > 2])
        
        # Add reasoning roles to ensure we find definition/counter/latest fragments
        all_keywords.extend(["definition", "counter_argument", "latest_data"])
        
        # Add synonyms for critical terms
        synonym_map = {
            "uti": ["urinary_tract_infection", "bladder_infection"],
            "cancer": ["carcinoma", "tumor", "oncology"],
            "diabetes": ["diabetic", "hyperglycemia", "insulin"],
            "fasting": ["diet", "nutrition", "meal_timing"],
            "methanol": ["poisoning", "toxicology", "antidote"],
            "steel": ["metal", "beam", "structural"],
            "cold": ["freezing", "low_temperature", "winter"],
            "concrete": ["cement", "construction", "curing"],
            "sourdough": ["levain", "starter", "fermentation", "bread"],
            "rising": ["proofing", "leavening", "expansion"]
        }
        
        for keyword in list(all_keywords):
            if keyword in synonym_map:
                all_keywords.extend(synonym_map[keyword])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for k in all_keywords:
            if k not in seen:
                seen.add(k)
                unique_keywords.append(k)
        
        return unique_keywords[:15]  # Limit to top 15 keywords for broader search


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
        Retrieve fragments from trusted web sources.
        
        Fetches content from hardcoded trusted finance sources and extracts
        relevant text based on the sub-question keywords.
        
        Args:
            sub_question: The atomic sub-question to answer
            domain: Domain for context
            
        Returns:
            List of FragmentCandidates from trusted sources with credibility scores
        """
        candidates = []
        
        # Extract keywords from sub-question
        keywords = self._extract_keywords(sub_question)
        search_query = " ".join(keywords[:5])  # Use top 5 keywords
        
        print(f"[WebAgent] Searching trusted sources for: {search_query}")
        
        # Try each trusted source
        for source_url in TRUSTED_FINANCE_SOURCES:
            try:
                # Build search URL (simple approach - in production would use proper search API)
                content = self._fetch_source_content(source_url, search_query)
                
                if content:
                    # Extract relevant text
                    relevant_text = self._extract_relevant_text(content, keywords)
                    
                    if relevant_text:
                        # Determine credibility based on source
                        source_domain = source_url.replace("https://www.", "").replace("https://", "").split("/")[0]
                        credibility = SOURCE_CREDIBILITY.get(source_domain, 0.85)
                        
                        # Create fragment candidate
                        candidate = FragmentCandidate(
                            fragment_id=f"web_{source_domain}_{len(candidates)}",
                            content=relevant_text[:500],  # Limit content length
                            source=source_domain,
                            source_url=source_url,
                            credibility_estimate=credibility,
                            domain_tags=[domain] + keywords[:5],
                            agent_type="web",
                            sub_question=sub_question,
                            reasoning_role="latest_data",
                            source_type="primary",
                            year=2026  # Current year for recency
                        )
                        candidates.append(candidate)
                        print(f"[WebAgent] Found content from {source_domain} (credibility: {credibility})")
                        
            except Exception as e:
                print(f"[WebAgent] Error fetching {source_url}: {e}")
                continue
        
        if not candidates:
            print(f"[WebAgent] No content found in trusted sources for: {sub_question}")
        
        return candidates
    
    def _fetch_source_content(self, base_url: str, query: str) -> Optional[str]:
        """Fetch content from a trusted source."""
        try:
            # Simple fetch - in production would use proper search/query endpoints
            req = urllib.request.Request(
                base_url,
                headers={'User-Agent': 'Mozilla/5.0 (OpenEyes VCIS)'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')
                return html
        except Exception as e:
            print(f"[WebAgent] Fetch error: {e}")
            return None
    
    def _extract_relevant_text(self, html: str, keywords: List[str]) -> Optional[str]:
        """Extract relevant text from HTML content based on keywords."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        text = unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Find sentences containing keywords
        sentences = re.split(r'[.!?]+', text)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if sentence contains any keywords
            for keyword in keywords:
                if keyword.lower() in sentence_lower:
                    relevant_sentences.append(sentence.strip())
                    break
        
        if relevant_sentences:
            # Return up to 3 most relevant sentences
            return " ".join(relevant_sentences[:3])
        
        return None
    
    @staticmethod
    def _extract_keywords(question: str) -> List[str]:
        """Extract meaningful keywords from a question."""
        stop_words = {
            "what", "is", "are", "the", "a", "an", "for", "with", 
            "in", "on", "at", "to", "of", "and", "or", "but",
            "how", "which", "when", "where", "why", "can", "could",
            "should", "would", "may", "might", "must", "shall"
        }
        
        words = re.findall(r'\b[a-zA-Z]+\b', question.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords[:10]


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

    def dfs_retrieve(self, query: str, domain: str, depth_limit: int = 5, 
                     width_limit: int = 3) -> List[FragmentCandidate]:
        """
        Depth-First Search retrieval.
        
        Instead of retrieving all candidates at once, picks the most
        promising sub-question, retrieves fragments for it, uses those
        fragments to inform the next sub-question, and so on.
        
        Each step narrows and deepens the search based on what was
        found in the previous step.
        """
        all_candidates = []
        visited_topics = set()
        
        # Start with decomposed sub-questions
        sub_questions = self.decompose_query(query)
        
        # DFS stack — start with the most specific sub-question
        stack = sub_questions[:depth_limit]
        
        depth = 0
        while stack and depth < depth_limit:
            current_question = stack.pop(0)
            
            # Skip if already covered this topic
            topic_key = self._extract_topic_key(current_question)
            if topic_key in visited_topics:
                continue
            visited_topics.add(topic_key)
            
            # Retrieve candidates for this specific sub-question only
            step_candidates = self.library_agent.retrieve(
                current_question, 
                domain=domain, 
                max_results=width_limit
            )
            
            if step_candidates:
                all_candidates.extend(step_candidates)
                
                # Inform next step based on what we found
                # Look at tags of surviving fragments and expand into related topics
                next_topics = self._extract_related_topics(step_candidates, visited_topics)
                stack = next_topics + stack  # Depth-first: new topics go to front
            
            depth += 1
        
        return all_candidates

    def _extract_topic_key(self, sub_question: str) -> str:
        """Extract a normalized topic key for deduplication."""
        words = set(sub_question.lower().split()) - STOP_WORDS
        return ' '.join(sorted(words)[:3])

    def _extract_related_topics(self, candidates: List[FragmentCandidate], 
                                visited: set) -> List[str]:
        """
        Given fragments found in this step, generate the next
        most relevant sub-questions to pursue.
        """
        related = []
        for candidate in candidates:
            # Get compatible fragment tags as next search directions
            compatible_tags = candidate.domain_tags
            for tag in compatible_tags:
                if tag not in visited and tag not in STOP_WORDS:
                    related.append(tag)
        
        # Return top 3 most common related topics not yet visited
        from collections import Counter
        tag_counts = Counter(related)
        return [topic for topic, _ in tag_counts.most_common(3)]
    
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
    
    def _get_fragment_role(self, fragment_id: str) -> str:
        """Look up fragment's reasoning_role from library."""
        try:
            frag = self.library._fragments.get(fragment_id)
            if frag:
                return getattr(frag, 'reasoning_role', 'definition')
        except:
            pass
        return 'definition'
    
    def _extract_tags_from_candidates(self, candidates: List[FragmentCandidate]) -> List[str]:
        """Extract the most common tags from a set of candidates for DFS propagation."""
        from collections import Counter
        all_tags = []
        for c in candidates:
            try:
                frag = self.library._fragments.get(c.fragment_id)
                if frag:
                    all_tags.extend(getattr(frag, 'tags', []))
            except:
                pass
        tag_counts = Counter(all_tags)
        return [tag for tag, _ in tag_counts.most_common(5)]
    
    def retrieve_by_kap(
        self, 
        query: str, 
        domain: str,
        kap: KnowledgeAcquisitionPlan
    ) -> Dict[str, List[FragmentCandidate]]:
        """
        Execute retrieval layer by layer according to the KAP.
        Returns a dict of {layer_name: [candidates]} for traceability.
        
        For DFS intent: each layer's results inform the next layer's tag targets
        For BFS intent: all layers retrieved in parallel (sorted by priority)
        """
        results_by_layer = {}
        
        for layer in kap.sorted_layers():
            layer_candidates = []
            
            # Build the search query for this layer
            # Combine layer's target_tags with required roles
            for role in layer.required_roles:
                for tag in layer.target_tags[:3]:  # Top 3 tags per role
                    candidates = self.library_agent.retrieve(
                        sub_question=f"{tag}",
                        domain=domain,
                    )
                    # Filter to only fragments with the required role
                    role_matched = [
                        c for c in candidates 
                        if self._get_fragment_role(c.fragment_id) == role
                    ]
                    layer_candidates.extend(role_matched)
            
            # If DFS mode — use this layer's surviving fragments to 
            # inform the next layer's tag targets
            if kap.intent.search_mode == 'DFS' and layer_candidates:
                next_layer_idx = kap.layers.index(layer) + 1
                if next_layer_idx < len(kap.layers):
                    next_layer = kap.sorted_layers()[next_layer_idx]
                    if not next_layer.target_tags:
                        # Propagate discovered tags from survivors
                        discovered_tags = self._extract_tags_from_candidates(layer_candidates)
                        next_layer.target_tags = discovered_tags[:5]
            
            results_by_layer[layer.name] = layer_candidates
            
            # If mandatory layer returned nothing — flag it
            if layer.mandatory and not layer_candidates:
                results_by_layer[f"{layer.name}_MISSING"] = []
        
        return results_by_layer


# Placeholder API connectors (to be implemented with real API keys)
class ArXivConnector:
    """Connector for arXiv preprint database."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def search_definitions(self, query: str, domain: str) -> List[Dict]:
        """Search arXiv for definition papers."""
        # TODO: Implement real arXiv API call
        print("[ArXivConnector] Would query arXiv API")
        return []


class PubMedConnector:
    """Connector for PubMed biomedical literature."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def search_risks(self, query: str) -> List[Dict]:
        """Search PubMed for risk/side-effect studies."""
        # TODO: Implement real PubMed E-utilities API call
        print("[PubMedConnector] Would query PubMed API")
        return []


class IEEEConnector:
    """Connector for IEEE Xplore digital library."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def search_recent(self, query: str, min_year: int = 2024) -> List[Dict]:
        """Search IEEE for recent technical papers."""
        # TODO: Implement real IEEE API call
        print("[IEEEConnector] Would query IEEE Xplore API")
        return []


class GovConnector:
    """Connector for US government databases (CDC, FDA, NIH, etc.)."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def search_statistics(self, query: str) -> List[Dict]:
        """Search government databases for official statistics."""
        # TODO: Implement real government API calls
        print("[GovConnector] Would query government APIs")
        return []


def create_api_connectors(config: Dict[str, str]) -> Dict[str, Any]:
    """
    Create API connectors from configuration.
    
    config: {"arxiv": "api_key", "pubmed": "api_key", ...}
    """
    connectors = {}
    
    if "arxiv" in config:
        connectors["arxiv"] = ArXivConnector(config["arxiv"])
    if "pubmed" in config:
        connectors["pubmed"] = PubMedConnector(config["pubmed"])
    if "ieee" in config:
        connectors["ieee"] = IEEEConnector(config["ieee"])
    if "gov" in config:
        connectors["gov"] = GovConnector(config["gov"])
    
    return connectors
