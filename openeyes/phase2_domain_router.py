"""
Phase 2: Domain SWITCH Router & Knowledge Graph
Implements O(1) domain routing using native switch/match syntax
and transforms static fragments into an active knowledge graph.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import hashlib


class Domain(Enum):
    """Top-level application domains for O(1) routing."""
    ECONOMY = auto()
    HEALTHCARE = auto()
    INVESTMENT = auto()
    GOVERNANCE = auto()
    GENERAL = auto()
    UNKNOWN = auto()


@dataclass
class KnowledgeNode:
    """
    A structural node in the knowledge graph.
    Represents a single information fragment with relationship edges.
    """
    node_id: str
    domain_tag: str
    content: str
    shorthand: str = ""
    analogy: str = ""
    
    # Metadata for validation
    timestamp_fresh: bool = True
    verified_source: bool = True
    trust_score: float = 0.95
    
    # Lexical anchors for matching
    lexical_anchors: List[str] = field(default_factory=list)
    
    # Graph relationships
    graph_edges: List[str] = field(default_factory=list)  # Points to other node_ids
    
    # Routing conditions
    if_condition: str = ""
    elseif_condition: str = ""
    else_fallback_node: Optional[str] = None
    
    # Payload variants
    standard_payload: Optional[Dict[str, str]] = None
    ambiguous_payload: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            'node_id': self.node_id,
            'domain_tag': self.domain_tag,
            'content': self.content,
            'shorthand': self.shorthand,
            'analogy': self.analogy,
            'validation_metadata': {
                'timestamp_fresh': self.timestamp_fresh,
                'verified_source': self.verified_source,
                'trust_score': self.trust_score,
            },
            'lexical_anchors': self.lexical_anchors,
            'routing_matrix': {
                'if_condition': self.if_condition,
                'elseif_condition': self.elseif_condition,
                'else_fallback_node': self.else_fallback_node,
            },
            'payload_variants': {
                'standard_payload': self.standard_payload,
                'ambiguous_payload': self.ambiguous_payload,
            },
            'graph_edges': self.graph_edges,
        }


class DomainRouter:
    """
    Phase 2: The Core Router
    
    Implements O(1) domain extraction using SWITCH block routing.
    Processes heaviest-weighted tokens to instantly steer execution
    to isolated database sections.
    """
    
    # Domain keyword mappings for instant routing
    DOMAIN_KEYWORDS: Dict[Domain, Set[str]] = {
        Domain.ECONOMY: {
            'inflation', 'recession', 'gdp', 'unemployment', 'fiscal', 'monetary',
            'interest rate', 'central bank', 'fed', 'treasury', 'deficit', 'debt',
            'economic', 'economy', 'macroeconomic', 'stimulus', 'austerity'
        },
        Domain.HEALTHCARE: {
            'disease', 'symptom', 'treatment', 'medication', 'diagnosis', 'therapy',
            'patient', 'doctor', 'hospital', 'clinic', 'prescription', 'dosage',
            'medical', 'health', 'clinical', 'pharmaceutical', 'vaccine', 'surgery'
        },
        Domain.INVESTMENT: {
            'stock', 'bond', 'asset', 'portfolio', 'return', 'risk', 'dividend',
            'equity', 'security', 'market', 'fund', 'etf', 'mutual fund',
            'investment', 'investing', 'trading', 'broker', 'capital', 'yield'
        },
        Domain.GOVERNANCE: {
            'policy', 'regulation', 'law', 'legislation', 'compliance', 'government',
            'agency', 'authority', 'mandate', 'statute', 'legal', 'regulatory',
            'governance', 'administration', 'bureau', 'department', 'ministry'
        },
        Domain.GENERAL: {
            'general', 'overview', 'introduction', 'basic', 'fundamental',
            'system', 'process', 'method', 'approach', 'strategy'
        },
    }
    
    # Fallback domain mapping
    FALLBACK_DOMAIN = Domain.GENERAL
    
    def __init__(self):
        self._domain_index: Dict[Domain, List[str]] = {d: [] for d in Domain}
        self._keyword_to_domain: Dict[str, Domain] = {}
        self._build_keyword_index()
    
    def _build_keyword_index(self):
        """Build reverse index from keywords to domains for O(1) lookup."""
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                self._keyword_to_domain[keyword.lower()] = domain
    
    def extract_domain(self, query: str, weighted_keywords: Optional[List[str]] = None) -> Domain:
        """
        Extract parent application field using SWITCH block logic.
        
        Args:
            query: Raw or normalized query string
            weighted_keywords: Optional list of pre-extracted priority keywords
            
        Returns:
            Domain enum value
        """
        query_lower = query.lower()
        
        # Use weighted keywords if provided, otherwise tokenize query
        if weighted_keywords:
            tokens = [kw.lower() for kw in weighted_keywords]
        else:
            import re
            tokens = re.findall(r'\b[a-z]+\b', query_lower)
        
        # Count domain matches
        domain_scores: Dict[Domain, int] = {d: 0 for d in Domain}
        
        for token in tokens:
            # O(1) hash lookup
            if token in self._keyword_to_domain:
                matched_domain = self._keyword_to_domain[token]
                domain_scores[matched_domain] += 1
        
        # Find highest-scoring domain (SWITCH logic)
        max_score = 0
        best_domain = self.FALLBACK_DOMAIN
        
        for domain, score in domain_scores.items():
            if score > max_score:
                max_score = score
                best_domain = domain
        
        # If no matches, use fallback
        if max_score == 0:
            return self.FALLBACK_DOMAIN
        
        return best_domain
    
    def route_to_domain(self, query: str, **kwargs) -> Tuple[Domain, Dict[str, Any]]:
        """
        Complete domain routing with metadata.
        
        Args:
            query: User query
            **kwargs: Additional context
            
        Returns:
            Tuple of (Domain, routing_metadata)
        """
        domain = self.extract_domain(query)
        
        metadata = {
            'routed_domain': domain.name,
            'confidence': 'high' if domain != self.FALLBACK_DOMAIN else 'low',
            'fallback_used': domain == self.FALLBACK_DOMAIN,
        }
        
        return domain, metadata


class KnowledgeGraph:
    """
    Phase 2: Graph Data Transformation
    
    Reorganizes individual text fragments into a structured,
    memory-efficient data array with relationship edges.
    """
    
    def __init__(self):
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._domain_index: Dict[str, List[str]] = {}
        self._anchor_index: Dict[str, Set[str]] = {}
    
    def add_node(self, node: KnowledgeNode):
        """Register a node in the knowledge graph."""
        self._nodes[node.node_id] = node
        
        # Index by domain
        if node.domain_tag not in self._domain_index:
            self._domain_index[node.domain_tag] = []
        if node.node_id not in self._domain_index[node.domain_tag]:
            self._domain_index[node.domain_tag].append(node.node_id)
        
        # Index by lexical anchors
        for anchor in node.lexical_anchors:
            anchor_lower = anchor.lower()
            if anchor_lower not in self._anchor_index:
                self._anchor_index[anchor_lower] = set()
            self._anchor_index[anchor_lower].add(node.node_id)
    
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Retrieve a node by ID."""
        return self._nodes.get(node_id)
    
    def get_nodes_by_domain(self, domain: str) -> List[KnowledgeNode]:
        """Get all nodes in a domain."""
        node_ids = self._domain_index.get(domain, [])
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]
    
    def search_by_anchor(self, anchor: str) -> List[KnowledgeNode]:
        """Search for nodes by lexical anchor."""
        node_ids = self._anchor_index.get(anchor.lower(), set())
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]
    
    def get_neighbors(self, node_id: str, depth: int = 1) -> List[KnowledgeNode]:
        """
        Get neighboring nodes via graph edges.
        
        Args:
            node_id: Starting node ID
            depth: How many hops to traverse
            
        Returns:
            List of neighboring nodes
        """
        if depth <= 0 or node_id not in self._nodes:
            return []
        
        node = self._nodes[node_id]
        neighbors = []
        visited = {node_id}
        
        # BFS traversal
        current_level = [node_id]
        for _ in range(depth):
            next_level = []
            for nid in current_level:
                if nid not in self._nodes:
                    continue
                current_node = self._nodes[nid]
                for edge_id in current_node.graph_edges:
                    if edge_id not in visited and edge_id in self._nodes:
                        visited.add(edge_id)
                        neighbors.append(self._nodes[edge_id])
                        next_level.append(edge_id)
            current_level = next_level
        
        return neighbors
    
    def build_graph_from_fragments(self, fragments: List[Any], domain: str):
        """
        Convert fragment objects into knowledge graph nodes.
        
        Args:
            fragments: List of Fragment objects
            domain: Target domain tag
        """
        for frag in fragments:
            # Extract content from fragment
            content = getattr(frag, 'content', '') or getattr(frag, 'claim', '') or ''
            if not content:
                continue
            
            # Generate node ID
            node_id = getattr(frag, 'id', f"frag_{hashlib.sha256(content.encode()).hexdigest()[:12]}")
            
            # Extract lexical anchors from tags
            tags = getattr(frag, 'tags', [])
            lexical_anchors = list(tags) if tags else []
            
            # Add content keywords as anchors
            import re
            words = re.findall(r'\b[a-z]{4,}\b', content.lower())
            lexical_anchors.extend(words[:10])  # Limit to top 10
            
            # Create node
            node = KnowledgeNode(
                node_id=node_id,
                domain_tag=domain,
                content=content,
                shorthand=getattr(frag, 'shorthand', ''),
                analogy=getattr(frag, 'analogy', ''),
                timestamp_fresh=getattr(frag, 'timestamp_fresh', True),
                verified_source=getattr(frag, 'verified_source', True),
                trust_score=getattr(frag, 'trust_score', 0.95),
                lexical_anchors=list(set(lexical_anchors)),
                graph_edges=[],  # Will be populated by relationship analysis
            )
            
            self.add_node(node)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export graph as dictionary."""
        return {
            'nodes': {nid: node.to_dict() for nid, node in self._nodes.items()},
            'domain_counts': {d: len(ids) for d, ids in self._domain_index.items()},
            'total_nodes': len(self._nodes),
        }


# Singleton instances
_router: Optional[DomainRouter] = None
_graph: Optional[KnowledgeGraph] = None


def get_domain_router() -> DomainRouter:
    """Get or create singleton DomainRouter instance."""
    global _router
    if _router is None:
        _router = DomainRouter()
    return _router


def get_knowledge_graph() -> KnowledgeGraph:
    """Get or create singleton KnowledgeGraph instance."""
    global _graph
    if _graph is None:
        _graph = KnowledgeGraph()
    return _graph


def route_query_domain(query: str, keywords: Optional[List[str]] = None) -> Domain:
    """Convenience function to route query to domain."""
    return get_domain_router().extract_domain(query, keywords)


if __name__ == "__main__":
    # Test Phase 2 components
    print("=" * 80)
    print("PHASE 2: DOMAIN ROUTER & KNOWLEDGE GRAPH TEST SUITE")
    print("=" * 80)
    
    # Test Domain Router
    router = DomainRouter()
    
    test_queries = [
        "What causes inflation and how does the Fed respond?",
        "Is insulin safe for type 2 diabetes patients?",
        "Should I invest in stocks or bonds during recession?",
        "What are the new compliance regulations for healthcare?",
        "Can you explain the general approach to problem solving?",
        "Random query about nothing specific",
    ]
    
    print("\n--- DOMAIN ROUTING TESTS ---\n")
    for query in test_queries:
        domain, metadata = router.route_to_domain(query)
        print(f"Query: {query}")
        print(f"  → Domain: {domain.name}")
        print(f"  → Confidence: {metadata['confidence']}")
        print(f"  → Fallback: {metadata['fallback_used']}")
        print()
    
    # Test Knowledge Graph
    print("\n--- KNOWLEDGE GRAPH TESTS ---\n")
    
    graph = KnowledgeGraph()
    
    # Create sample nodes
    node1 = KnowledgeNode(
        node_id="frag_inflation_001",
        domain_tag="ECONOMY",
        content="Inflation is the rate at which prices increase over time.",
        shorthand="A hidden tax on savings",
        analogy="Your paycheck stays same size, but grocery cart shrinks",
        lexical_anchors=['inflation', 'prices', 'purchasing power', 'monetary'],
        graph_edges=['frag_interest_rates_001', 'frag_consumer_spending_001'],
        standard_payload={
            'shorthand': 'A hidden tax on savings; money loses purchasing power daily.',
            'analogy': 'Your paycheck stays the same size, but your grocery cart shrinks.'
        }
    )
    
    node2 = KnowledgeNode(
        node_id="frag_interest_rates_001",
        domain_tag="ECONOMY",
        content="Interest rates are the cost of borrowing money.",
        shorthand="Price of money",
        analogy="Like rent for cash",
        lexical_anchors=['interest', 'rates', 'borrowing', 'fed funds'],
        graph_edges=['frag_inflation_001'],
    )
    
    graph.add_node(node1)
    graph.add_node(node2)
    
    print(f"Added {len(graph._nodes)} nodes to graph")
    print(f"Graph stats: {graph.to_dict()}")
    
    # Search by anchor
    results = graph.search_by_anchor('inflation')
    print(f"\nSearch 'inflation': Found {len(results)} nodes")
    for node in results:
        print(f"  - {node.node_id}: {node.shorthand}")
    
    # Get neighbors
    neighbors = graph.get_neighbors('frag_inflation_001', depth=1)
    print(f"\nNeighbors of inflation node: {len(neighbors)} nodes")
    for node in neighbors:
        print(f"  - {node.node_id}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
