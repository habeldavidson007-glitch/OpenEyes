"""
P3: Logical Synthesis & Safety Priority Engine
----------------------------------------------
Solves: "Context Dumping" vs. "Reasoned Advice"
Mechanism:
1. Intent Classification (Factual vs. Strategic vs. Emergency)
2. Noise Filtering (Remove irrelevant high-confidence data)
3. Logical Construction (Because X -> Therefore Y)
4. Safety Override (Suppress data if emergency detected)
"""

import re
from typing import Dict, List, Tuple, Optional

class LogicalSynthesizer:
    def __init__(self):
        # Emergency patterns that require IMMEDIATE action, NO data dump
        self.emergency_patterns = [
            r"\bchest\s*pain\b", r"\bheart\s*attack\b", r"\bcan't\s*breathe\b",
            r"\bsuicide\b", r"\bhurt\s*myself\b", r"\bleeding\s*badly\b",
            r"\bstroke\s*symptoms\b", r"\bunconscious\b"
        ]
        
        # Advice-seeking patterns requiring strategic synthesis
        self.advice_patterns = [
            r"\bbest\s*advice\b", r"\bhow\s*to\s*deal\b", r"\bwhat\s*should\s*i\b",
            r"\bstrategy\b", r"\brecommend\b", r"\btips\b"
        ]

    def classify_intent(self, query: str) -> str:
        """Determine if query needs Facts, Strategy, or Emergency Protocol."""
        query_lower = query.lower()
        
        # 1. Check Emergency First (Highest Priority) - Use flexible matching
        # Handle variations like "chest felt pain", "chest has pain", etc.
        emergency_patterns_flexible = [
            r"chest.*pain", r"pain.*chest",  # Chest pain variations
            r"heart.*attack", r"attack.*heart",
            r"can't\s*breathe", r"cannot\s*breathe", r"trouble\s*breathe",
            r"suicide", r"hurt\s*myself", r"hurt\s*my\s*self", r"killing\s*myself",
            r"bleeding\s*badly", r"severe\s*bleeding",
            r"stroke", r"unconscious", r"passing\s*out", r"faint"
        ]
        import re
        for pattern in emergency_patterns_flexible:
            if re.search(pattern, query_lower):
                return "EMERGENCY"
        
        # 2. Check Advice/Strategy
        for pattern in self.advice_patterns:
            if re.search(pattern, query_lower):
                return "STRATEGIC"
        
        # 3. Default to Factual
        return "FACTUAL"

    def generate_emergency_response(self, query: str, domain: str) -> Dict:
        """Bypass all data retrieval. Output strict safety protocol."""
        query_lower = query.lower()
        
        # Medical Emergency Detection (overrides domain) - Use flexible patterns
        import re
        medical_patterns = [
            r"chest.*pain", r"pain.*chest",
            r"heart.*attack", r"attack.*heart",
            r"can't\s*breathe", r"cannot\s*breathe", r"trouble\s*breathe",
            r"stroke", r"unconscious", r"passing\s*out", r"faint",
            r"bleeding\s*badly", r"severe\s*bleeding"
        ]
        is_medical_emergency = any(re.search(p, query_lower) for p in medical_patterns)
        
        if is_medical_emergency:
            return {
                "action": "HALT_AND_REDIRECT",
                "response": "⚠️ MEDICAL EMERGENCY DETECTED.\n\nI am an AI, not a doctor. Chest pain can indicate a heart attack or other life-threatening conditions.\n\n👉 ACTION REQUIRED:\n1. Call Emergency Services (911) immediately.\n2. Do not drive yourself.\n3. Chew aspirin only if prescribed and not allergic.\n\nDo not rely on AI for acute medical symptoms.",
                "confidence": 1.0,
                "sources": [] # No sources needed for emergency protocol
            }
        
        # Self-Harm Detection
        if "suicide" in query_lower or "hurt myself" in query_lower or "hurt my self" in query_lower or "killing myself" in query_lower:
            return {
                "action": "HALT_AND_REDIRECT",
                "response": "⚠️ CRISIS DETECTED.\n\nYou are not alone. Help is available right now.\n\n👉 ACTION REQUIRED:\n- US: Call/text 988 (Suicide & Crisis Lifeline)\n- International: Find local resources at findahelpline.com\n\nPlease reach out to a human professional immediately.",
                "confidence": 1.0,
                "sources": []
            }
            
        return {"action": "PASS", "response": "", "confidence": 0}

    def synthesize_strategic_answer(self, query: str, retrieved_data: List[str]) -> Dict:
        """
        Transform raw data into logical advice.
        Structure: Context -> Implication -> Actionable Advice.
        """
        if not retrieved_data:
            return {"action": "NO_DATA", "response": "I cannot provide specific advice without market data."}

        # Heuristic Synthesis (In production, this would be an LLM call)
        # We look for keywords in data to build a "Because -> Therefore" chain
        
        advice_intro = "Based on current market structure and regulatory environment, here is the strategic analysis:\n\n"
        logic_chain = []
        
        has_dark_pool = any("dark pool" in d.lower() for d in retrieved_data)
        has_slippage = any("slippage" in d.lower() for d in retrieved_data)
        has_sec = any("sec" in d.lower() or "regulation" in d.lower() for d in retrieved_data)
        
        if has_dark_pool:
            logic_chain.append(
                "**Liquidity Fragmentation:** Significant volume occurs in 'dark pools' (private exchanges). "
                "➡️ **Advice:** Avoid market orders for large positions; use limit orders to prevent adverse selection against hidden liquidity."
            )
        
        if has_slippage:
            logic_chain.append(
                "**Execution Risk:** Slippage (difference between expected and actual price) can erode profits, especially in volatile assets. "
                "➡️ **Advice:** Implement algorithmic execution (TWAP/VWAP) for sizes >1% of average daily volume to minimize market impact."
            )
            
        if has_sec:
            logic_chain.append(
                "**Regulatory Compliance:** Recent SEC proposals target payment for order flow and best execution. "
                "➡️ **Advice:** Ensure your broker provides explicit 'Best Execution' reports and disclose any conflicts of interest."
            )
            
        if not logic_chain:
            # Fallback if specific keywords missing but data exists
            logic_chain.append(f"Analysis of available data suggests careful consideration of market microstructure. {retrieved_data[0][:200]}...")
            logic_chain.append("➡️ **Advice:** Consult a fiduciary financial advisor before executing complex strategies.")

        final_response = advice_intro + "\n\n".join(logic_chain)
        
        return {
            "action": "ANSWER_STRATEGIC",
            "response": final_response,
            "confidence": 0.85, # Synthetic confidence
            "sources": retrieved_data[:3] # Limit sources
        }

    def process(self, query: str, domain: str, retrieved_data: List[str]) -> Dict:
        """Main Entry Point"""
        intent = self.classify_intent(query)
        
        # Emergency check happens FIRST, before any data processing
        if intent == "EMERGENCY":
            emergency_response = self.generate_emergency_response(query, domain)
            if emergency_response["action"] == "HALT_AND_REDIRECT":
                return emergency_response
        
        if intent == "STRATEGIC":
            return self.synthesize_strategic_answer(query, retrieved_data)
        
        # Default: Return raw data but formatted cleanly
        return {
            "action": "ANSWER_FACTUAL",
            "response": "\n\n".join(retrieved_data),
            "confidence": 0.7,
            "sources": retrieved_data
        }

# Self-Test
if __name__ == "__main__":
    engine = LogicalSynthesizer()
    
    # Test 1: Emergency (Chest Pain) - Should trigger HALT
    print("=== TEST 1: EMERGENCY (Chest Pain) ===")
    res = engine.process("my chest felt pain, how do i deal with it?", "healthcare", ["Radiation data...", "Pneumonia stats..."])
    print(f"Action: {res['action']}")
    print(f"Response:\n{res['response']}\n")
    
    # Test 2: Strategic (Stock Advice) - Should synthesize logic
    print("=== TEST 2: STRATEGIC (Stock Advice) ===")
    data = [
        "Dark pools allow institutional investors to trade anonymously without market impact.",
        "Slippage is the difference between expected and actual fill price, often 1-3 bps for liquid equities.",
        "SEC Rule 201 restricts short selling during significant declines."
    ]
    res = engine.process("what is the best advice for doing a stock exchange?", "economy", data)
    print(f"Action: {res['action']}")
    print(f"Response:\n{res['response']}\n")
    
    # Test 3: Out of Scope (No data) - Should handle gracefully
    print("=== TEST 3: OUT OF SCOPE (Poorest Country) ===")
    res = engine.process("what is the poorest country?", "economy", [])
    print(f"Action: {res['action']}")
    if res['action'] == "NO_DATA":
        print("Correctly identified lack of data for strategic advice.")
    else:
        print(f"Response: {res.get('response', 'N/A')[:100]}...\n")

    # Test 4: Factual Query (Should return data as-is)
    print("=== TEST 4: FACTUAL (What is inflation?) ===")
    factual_data = ["Inflation is the rate at which prices rise.", "Central banks target 2% inflation."]
    res = engine.process("what is inflation?", "economy", factual_data)
    print(f"Action: {res['action']}")
    print(f"Response:\n{res['response']}\n")
