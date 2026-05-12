"""
Context Manager for OpenEyes
Handles short-term conversation history and context preservation.
"""
import time
from collections import deque
from typing import List, Dict, Any, Optional

class ConversationTurn:
    def __init__(self, role: str, content: str, domain_hint: Optional[str] = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.domain_hint = domain_hint
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "domain_hint": self.domain_hint,
            "timestamp": self.timestamp
        }

class ContextManager:
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.history: deque = deque(maxlen=max_turns)
        self.session_id = f"sess_{int(time.time())}"
        self.current_domain_focus: Optional[str] = None

    def add_turn(self, role: str, content: str, domain_hint: Optional[str] = None):
        """Add a new turn to the conversation history."""
        turn = ConversationTurn(role, content, domain_hint)
        self.history.append(turn)
        
        # Update domain focus if the assistant just spoke with a specific domain
        if role == 'assistant' and domain_hint:
            self.current_domain_focus = domain_hint

    def get_history(self, format: str = "list") -> Any:
        """Retrieve history in requested format."""
        if format == "list":
            return [turn.to_dict() for turn in self.history]
        elif format == "text":
            return "\n".join([f"{t.role}: {t.content}" for t in self.history])
        return list(self.history)

    def get_context_boost(self, query: str, target_domain: str) -> float:
        """
        Calculate a confidence boost based on recent conversation context.
        If the last few turns were about 'economy', an economy query gets a boost.
        """
        if not self.history:
            return 0.0

        boost = 0.0
        recent_domains = [t.domain_hint for t in self.history if t.domain_hint and t.role == 'assistant']
        
        if not recent_domains:
            return 0.0

        # Check last 3 turns for domain consistency
        match_count = sum(1 for d in recent_domains[-3:] if d == target_domain)
        
        if match_count > 0:
            # Linear scaling: 1 match = 0.05, 2 matches = 0.10, 3 matches = 0.15
            boost = min(0.15, match_count * 0.05)
            
        return boost

    def requires_clarification_context(self, query: str, confidence: float) -> bool:
        """
        Determine if we should ask for clarification based on low confidence 
        AND lack of supporting context.
        """
        if confidence > 0.40:
            return False
        
        # If confidence is low, check if context saves us
        if self.current_domain_focus:
            # If we have a strong recent focus, we might be more lenient
            # But if the query is totally unrelated, we still need clarification
            return False 
            
        # Low confidence + No context = Ask for clarification
        return True

    def clear(self):
        """Reset the conversation context."""
        self.history.clear()
        self.current_domain_focus = None

# Singleton instance for global access if needed
_global_context = ContextManager()

def get_global_context() -> ContextManager:
    return _global_context

if __name__ == "__main__":
    # Test the context manager
    ctx = ContextManager()
    
    # Simulate a conversation
    ctx.add_turn("user", "How does inflation work?")
    ctx.add_turn("assistant", "Inflation is the rate of increase in prices...", domain_hint="economy")
    
    ctx.add_turn("user", "What about the federal funds rate?")
    ctx.add_turn("assistant", "The federal funds rate is...", domain_hint="economy")
    
    # Check context boost for a related query
    boost = ctx.get_context_boost("Is the rate going up?", "economy")
    print(f"Context Boost for economy query: {boost}")
    
    # Check context boost for an unrelated query
    boost_unrelated = ctx.get_context_boost("Do I have a fever?", "healthcare")
    print(f"Context Boost for healthcare query: {boost_unrelated}")
    
    # Test clarification logic
    needs_clarification = ctx.requires_clarification_context("What is the rate?", 0.35)
    print(f"Needs clarification (low conf, strong context): {needs_clarification}")
    
    # Clear and test again
    ctx.clear()
    needs_clarification_no_ctx = ctx.requires_clarification_context("What is the rate?", 0.35)
    print(f"Needs clarification (low conf, no context): {needs_clarification_no_ctx}")
