"""
Phase 3: Multi-Branch Boolean Logic Gate Matrix
Implements conditional truth ladder with AND/OR/NOT operators
for data validity, safety, and freshness checks.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum, auto


class LogicGateResult(Enum):
    """Result of boolean gate evaluation."""
    IF_MATCH = auto()      # Fresh, verified, safe - serve standard payload
    ELSEIF_MATCH = auto()  # Stale data - serve ambiguity template
    ELSE_FALLBACK = auto() # No match - route to fallback graph edge
    HALT_SECURITY = auto() # Malicious input detected
    HALT_EXHAUSTED = auto() # State depth exceeded


@dataclass
class BooleanGateInput:
    """Input parameters for boolean gate evaluation."""
    node_has_token: bool = False
    synonym_matched: bool = False
    source_is_fresh: bool = True
    source_is_verified: bool = True
    contains_malicious_input: bool = False
    state_depth: int = 0
    
    # Additional metadata
    trust_score: float = 0.95
    domain: str = "general"
    query: str = ""


@dataclass
class BooleanGateResult:
    """Result of boolean gate matrix evaluation."""
    result: LogicGateResult
    confidence: float
    message: str
    action: str
    fallback_node: Optional[str] = None
    security_reason: Optional[str] = None


class BooleanLogicGateMatrix:
    """
    Phase 3: Multi-Branch Boolean Logic Gate Matrix
    
    Runs simultaneous checks on data validity, user safety,
    and environment timelines using AND/OR/NOT boolean operators.
    """
    
    # Security blacklist patterns
    SECURITY_BLACKLIST = [
        'exploit', 'bypass_halt', 'force_override', 'jailbreak',
        'ignore_safety', 'disable_filter', 'admin_mode', 'debug_bypass'
    ]
    
    # Maximum state depth before halt
    MAX_STATE_DEPTH = 3
    
    def __init__(self):
        self._security_patterns = self.SECURITY_BLACKLIST
    
    def _check_security(self, query_tokens: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Check for malicious input using NOT operator.
        Returns (is_malicious, reason).
        """
        for token in query_tokens:
            token_lower = token.lower()
            for pattern in self._security_patterns:
                if pattern in token_lower:
                    return True, f"Security pattern detected: {pattern}"
        return False, None
    
    def _evaluate_if_branch(self, inputs: BooleanGateInput) -> bool:
        """
        IF Branch: Using OR, AND, NOT operators
        
        Logic: IF (node_has_token OR synonym_matched) 
                  AND (source_is_fresh AND source_is_verified) 
                  AND (NOT contains_malicious_input)
        
        Execution: Mark target parameters valid and trigger THEN block
        to serve direct human shorthand payload.
        """
        # (node_has_token OR synonym_matched)
        has_match = inputs.node_has_token or inputs.synonym_matched
        
        # (source_is_fresh AND source_is_verified)
        is_validated = inputs.source_is_fresh and inputs.source_is_verified
        
        # (NOT contains_malicious_input)
        is_safe = not inputs.contains_malicious_input
        
        # Full condition
        return has_match and is_validated and is_safe
    
    def _evaluate_elseif_branch(self, inputs: BooleanGateInput) -> bool:
        """
        ELSEIF Branch: Using AND, NOT operators
        
        Logic: ELSEIF (node_has_token OR synonym_matched) 
                  AND (NOT source_is_fresh)
        
        Execution: Route into specialized fuzzy evaluation loop.
        Do not render stale statistics; pull alternative node histories.
        """
        # (node_has_token OR synonym_matched)
        has_match = inputs.node_has_token or inputs.synonym_matched
        
        # (NOT source_is_fresh)
        is_stale = not inputs.source_is_fresh
        
        return has_match and is_stale
    
    def _evaluate_else_branch(self, inputs: BooleanGateInput) -> bool:
        """
        ELSE Fallback Branch
        
        Logic: Catch-all for input terms outside knowledge cluster.
        
        Execution: Increment state_depth flag. If state_depth <= 3,
        walk backward up knowledge graph to closest broad category.
        """
        # Always true - this is the catch-all
        return inputs.state_depth <= self.MAX_STATE_DEPTH
    
    def evaluate(self, inputs: BooleanGateInput, query_tokens: List[str]) -> BooleanGateResult:
        """
        Execute prioritized sequence of conditional rules.
        
        Args:
            inputs: Boolean gate input parameters
            query_tokens: Tokenized query for security check
            
        Returns:
            BooleanGateResult with action directive
        """
        # Step 1: Security Override Gate (Using NOT)
        is_malicious, security_reason = self._check_security(query_tokens)
        if is_malicious:
            return BooleanGateResult(
                result=LogicGateResult.HALT_SECURITY,
                confidence=0.0,
                message="HALT_SECURITY_BREACH: Unsafe system operation command blocked.",
                action="HALT",
                security_reason=security_reason
            )
        
        # Update input with security check result
        inputs.contains_malicious_input = is_malicious
        
        # Step 2: IF Gate (Primary success path)
        if self._evaluate_if_branch(inputs):
            return BooleanGateResult(
                result=LogicGateResult.IF_MATCH,
                confidence=min(1.0, inputs.trust_score + 0.1),
                message="MATCH: Fresh, verified data available",
                action="SERVE_STANDARD_PAYLOAD"
            )
        
        # Step 3: ELSEIF Gate (Stale data path)
        if self._evaluate_elseif_branch(inputs):
            return BooleanGateResult(
                result=LogicGateResult.ELSEIF_MATCH,
                confidence=max(0.3, inputs.trust_score - 0.3),
                message="STALE_DATA: Serving ambiguity template",
                action="SERVE_AMBIGUITY_PAYLOAD"
            )
        
        # Step 4: ELSE Fallback Gate
        if self._evaluate_else_branch(inputs):
            return BooleanGateResult(
                result=LogicGateResult.ELSE_FALLBACK,
                confidence=0.5,
                message=f"FALLBACK: Routing to broader category (depth: {inputs.state_depth + 1})",
                action="ROUTE_TO_FALLBACK",
                fallback_node="frag_001_general"
            )
        
        # Step 5: State depth exceeded - HALT
        return BooleanGateResult(
            result=LogicGateResult.HALT_EXHAUSTED,
            confidence=0.0,
            message=f"HALT_EXHAUSTED: Structural reasoning depth limit exceeded (>{self.MAX_STATE_DEPTH})",
            action="HALT"
        )


class StateDecayCounter:
    """
    Phase 3.3: State Decay & Loop-Limit Counter
    
    Tracks active user sessions through state machine that monitors
    continuous execution depths using numeric counter.
    """
    
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self._session_depths: Dict[str, int] = {}
    
    def get_depth(self, session_id: str) -> int:
        """Get current depth for session."""
        return self._session_depths.get(session_id, 0)
    
    def increment(self, session_id: str) -> int:
        """Increment depth counter for session. Returns new depth."""
        current = self._session_depths.get(session_id, 0)
        new_depth = current + 1
        self._session_depths[session_id] = new_depth
        return new_depth
    
    def reset(self, session_id: str):
        """Reset depth counter for session."""
        self._session_depths[session_id] = 0
    
    def is_exhausted(self, session_id: str) -> bool:
        """Check if session has exceeded max depth."""
        return self._session_depths.get(session_id, 0) > self.max_depth
    
    def should_halt(self, session_id: str) -> bool:
        """Determine if operations should halt due to depth."""
        return self.is_exhausted(session_id)


# Singleton instances
_gate_matrix: Optional[BooleanLogicGateMatrix] = None
_state_counter: Optional[StateDecayCounter] = None


def get_boolean_gate_matrix() -> BooleanLogicGateMatrix:
    """Get or create singleton BooleanLogicGateMatrix instance."""
    global _gate_matrix
    if _gate_matrix is None:
        _gate_matrix = BooleanLogicGateMatrix()
    return _gate_matrix


def get_state_decay_counter() -> StateDecayCounter:
    """Get or create singleton StateDecayCounter instance."""
    global _state_counter
    if _state_counter is None:
        _state_counter = StateDecayCounter()
    return _state_counter


def evaluate_query_safety(query: str, **kwargs) -> BooleanGateResult:
    """
    Convenience function to evaluate query through boolean gate matrix.
    
    Args:
        query: User query string
        **kwargs: Additional parameters for BooleanGateInput
        
    Returns:
        BooleanGateResult with action directive
    """
    import re
    tokens = re.findall(r'\b\w+\b', query)
    
    inputs = BooleanGateInput(
        query=query,
        **kwargs
    )
    
    return get_boolean_gate_matrix().evaluate(inputs, tokens)


if __name__ == "__main__":
    # Test Phase 3 components
    print("=" * 80)
    print("PHASE 3: BOOLEAN LOGIC GATE MATRIX TEST SUITE")
    print("=" * 80)
    
    gate_matrix = BooleanLogicGateMatrix()
    state_counter = StateDecayCounter()
    
    test_cases = [
        # (description, inputs, expected_result_type)
        (
            "Fresh verified data with match",
            BooleanGateInput(
                node_has_token=True,
                source_is_fresh=True,
                source_is_verified=True,
                trust_score=0.95
            ),
            LogicGateResult.IF_MATCH
        ),
        (
            "Stale data with match",
            BooleanGateInput(
                node_has_token=True,
                source_is_fresh=False,
                source_is_verified=True,
                trust_score=0.8
            ),
            LogicGateResult.ELSEIF_MATCH
        ),
        (
            "No match, within depth limit",
            BooleanGateInput(
                node_has_token=False,
                synonym_matched=False,
                state_depth=1
            ),
            LogicGateResult.ELSE_FALLBACK
        ),
        (
            "Security breach attempt",
            BooleanGateInput(
                node_has_token=True,
                contains_malicious_input=True
            ),
            LogicGateResult.HALT_SECURITY
        ),
        (
            "State depth exhausted",
            BooleanGateInput(
                node_has_token=False,
                state_depth=4
            ),
            LogicGateResult.HALT_EXHAUSTED
        ),
    ]
    
    print("\n--- BOOLEAN GATE TESTS ---\n")
    
    for desc, inputs, expected in test_cases:
        tokens = ['test', 'query']
        if inputs.contains_malicious_input:
            tokens.append('exploit')
        
        result = gate_matrix.evaluate(inputs, tokens)
        
        status = "✓" if result.result == expected else "✗"
        print(f"{status} {desc}")
        print(f"   Expected: {expected.name}")
        print(f"   Got:      {result.result.name}")
        print(f"   Action:   {result.action}")
        print(f"   Message:  {result.message}")
        print(f"   Confidence: {result.confidence:.2f}")
        print()
    
    # Test State Decay Counter
    print("\n--- STATE DECAY COUNTER TESTS ---\n")
    
    session_id = "test_session_001"
    
    print(f"Session: {session_id}")
    for i in range(5):
        depth = state_counter.increment(session_id)
        exhausted = state_counter.is_exhausted(session_id)
        should_halt = state_counter.should_halt(session_id)
        print(f"  Depth {depth}: Exhausted={exhausted}, Should Halt={should_halt}")
    
    state_counter.reset(session_id)
    print(f"  Reset: Depth={state_counter.get_depth(session_id)}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
