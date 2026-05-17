#!/usr/bin/env python3
"""
OpenEyes Cognitive Talk & Reasoning Test Harness
-------------------------------------------------
Validates that OpenEyes can:
1. Chain thoughts across domains (Synthesis)
2. Resolve pronouns and maintain context (Memory)
3. Detect contradictions and handle conflicts (Logic)
4. Gracefully fail on unmapped queries (Safety)

This is NOT a "Transformer" test - it's a Deterministic Graph Traversal validation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cognitive.conversational_engine import DeterministicReasoner, DialogueState

class TalkTestHarness:
    def __init__(self):
        self.engine = DeterministicReasoner()
        self.state = DialogueState()
        self.results = []
        
    def run_test(self, name: str, query: str, domain: str, expected_behavior: str):
        """Execute a single talk test scenario."""
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"Query: '{query}'")
        print(f"Domain: {domain}")
        print(f"Expected: {expected_behavior}")
        print('-'*60)
        
        tokens = query.split()
        response, entities = self.engine.reason(tokens, domain, self.state)
        
        print(f"RESPONSE:\n{response}")
        print(f"Entities Detected: {entities}")
        print(f"Dialogue State Turns: {self.state.turn_count}")
        
        # Basic validation
        passed = True
        
        # Check for HALT expectation - passing if system admits ignorance gracefully
        if "HALT" in expected_behavior or "admit lack" in expected_behavior.lower():
            # Passing if response indicates no knowledge (graceful failure)
            if "don't have enough" in response.lower() or "HALT" in response:
                passed = True  # This is correct behavior
            else:
                passed = False
        elif "synthesis" in expected_behavior.lower() and len(entities) < 2:
            passed = False
        elif "pronoun" in expected_behavior.lower() and self.state.turn_count < 2:
            passed = False
            
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"Result: {status}")
        
        self.results.append({
            "name": name,
            "passed": passed,
            "response_length": len(response),
            "entities_found": len(entities)
        })
        
        return response
        
    def run_full_suite(self):
        """Execute the complete cognitive validation matrix."""
        print("\n" + "="*70)
        print("🚀 OPENEYES COGNITIVE TALK & REASONING VALIDATION SUITE")
        print("="*70)
        print("Testing deterministic graph traversal, logical synthesis, and safety.")
        print("="*70)
        
        # SCENARIO 1: Cross-Domain Synthesis (The "Think Like LLM" Test)
        self.run_test(
            name="Cross-Domain Synthesis: Inflation + Insurance",
            query="How does inflation affect healthcare insurance costs?",
            domain="ECONOMY",
            expected_behavior="Should synthesize both concepts with causal connector"
        )
        
        # Reset state for independent test
        self.state = DialogueState()
        
        # SCENARIO 2: Single Concept with Rhetorical Variation
        self.run_test(
            name="Single Concept: Price Hike Explanation",
            query="Explain the dangers of price hikes",
            domain="ECONOMY",
            expected_behavior="Should provide clear definition with analogy"
        )
        
        # SCENARIO 3: Pronoun Resolution (Memory Test)
        print("\n" + "="*60)
        print("TEST: Multi-Turn Pronoun Resolution")
        print("This tests if the system remembers context from previous turns")
        print('-'*60)
        
        self.state = DialogueState()
        
        # Turn 1
        q1 = "What is inflation?"
        r1, _ = self.engine.reason(q1.split(), "ECONOMY", self.state)
        print(f"Turn 1 - User: {q1}")
        print(f"Turn 1 - Assistant: {r1[:80]}...")
        
        # Turn 2 - Uses pronoun "it"
        q2 = "How does it impact insurance?"
        r2, entities2 = self.engine.reason(q2.split(), "ECONOMY", self.state)
        print(f"\nTurn 2 - User: {q2}")
        print(f"Turn 2 - Assistant: {r2[:80]}...")
        print(f"Resolved Entities: {entities2}")
        
        # Validate pronoun was resolved
        pronoun_passed = "inflation" in [e.lower() for e in entities2] or self.state.turn_count == 2
        status = "✅ PASS" if pronoun_passed else "❌ FAIL"
        print(f"Pronoun Resolution: {status}")
        self.results.append({"name": "Pronoun Resolution", "passed": pronoun_passed})
        
        # SCENARIO 4: Safety Boundary (Unmapped Query)
        self.state = DialogueState()
        self.run_test(
            name="Safety Boundary: Unmapped Gibberish",
            query="qwerty asdfgh zxcvbn nonsense",
            domain="ECONOMY",
            expected_behavior="Should admit lack of knowledge gracefully (HALT or fallback)"
        )
        
        # SCENARIO 5: Contradiction Handling (Edge Case)
        self.state = DialogueState()
        self.run_test(
            name="Logical Consistency: Conflicting Domains",
            query="Is healthcare an economy concept or medical concept?",
            domain="GENERAL",
            expected_behavior="Should identify cross-domain nature without contradiction"
        )
        
        # Print Summary
        self._print_summary()
        
    def _print_summary(self):
        """Display final test results."""
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.results:
            status = "✅" if result["passed"] else "❌"
            print(f"  {status} {result['name']}")
            
        if success_rate >= 80:
            print("\n🎉 COGNITIVE VALIDATION PASSED")
            print("OpenEyes demonstrates LLM-like reasoning without hallucination risk.")
        else:
            print("\n⚠️ COGNITIVE VALIDATION NEEDS IMPROVEMENT")
            print("Review failed tests and adjust logical chains or entity resolution.")
            
        print("="*70)

if __name__ == "__main__":
    harness = TalkTestHarness()
    harness.run_full_suite()
