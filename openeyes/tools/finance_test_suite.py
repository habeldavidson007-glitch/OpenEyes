#!/usr/bin/env python3
"""
OpenEyes Finance Test Suite
50 real financial queries covering all fragment categories.
Logs: HALT/ANSWER, confidence score, fragments used, time taken, manual verification status.
"""

import json
import time
from datetime import datetime
from pathlib import Path

# Test Query Definitions
TEST_QUERIES = {
    "macro_monetary": [
        {
            "id": "MAC-01",
            "query": "What is the Federal Reserve's dual mandate?",
            "category": "macro",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "MAC-02",
            "query": "How do FOMC meetings influence interest rate decisions?",
            "category": "macro",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "MAC-03",
            "query": "Explain the mechanism of quantitative easing and its effects on the economy.",
            "category": "macro",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "MAC-04",
            "query": "What is the difference between CPI and PCE inflation measures?",
            "category": "macro",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "MAC-05",
            "query": "How does an inverted yield curve predict recessions?",
            "category": "macro",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "MAC-06",
            "query": "What is the neutral interest rate (r*) and why is it debated?",
            "category": "macro",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "MAC-07",
            "query": "Explain the concept of a soft landing vs hard landing for the economy.",
            "category": "macro",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "MAC-08",
            "query": "What are the components of GDP and how is it measured?",
            "category": "macro",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "MAC-09",
            "query": "How does nonfarm payroll data impact market expectations?",
            "category": "macro",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "MAC-10",
            "query": "What is stagflation and what are historical examples?",
            "category": "macro",
            "expected_outcome": "ANSWER"
        }
    ],
    "earnings_fundamentals": [
        {
            "id": "EAR-01",
            "query": "What is the difference between gross margin and operating margin?",
            "category": "earnings",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "EAR-02",
            "query": "Why is free cash flow considered more important than net income?",
            "category": "earnings",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "EAR-03",
            "query": "How do you calculate and interpret the P/E ratio?",
            "category": "earnings",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "EAR-04",
            "query": "What is EV/EBITDA and when is it preferred over P/E?",
            "category": "earnings",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "EAR-05",
            "query": "Explain the importance of return on invested capital (ROIC).",
            "category": "earnings",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "EAR-06",
            "query": "What is revenue recognition and how can it be manipulated?",
            "category": "earnings",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "EAR-07",
            "query": "How do share buybacks create or destroy shareholder value?",
            "category": "earnings",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "EAR-08",
            "query": "What is the significance of the debt-to-equity ratio?",
            "category": "earnings",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "EAR-09",
            "query": "How do you assess the quality of a company's revenue growth?",
            "category": "earnings",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "EAR-10",
            "query": "What is a competitive moat and how do you identify one?",
            "category": "earnings",
            "expected_outcome": "ANSWER"
        }
    ],
    "crypto": [
        {
            "id": "CRY-01",
            "query": "What is Bitcoin's halving mechanism and its historical price impact?",
            "category": "crypto",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "CRY-02",
            "query": "Explain the difference between proof of work and proof of stake.",
            "category": "crypto",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "CRY-03",
            "query": "How do Ethereum smart contracts work and what are their limitations?",
            "category": "crypto",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "CRY-04",
            "query": "What caused the collapse of FTX and what lessons were learned?",
            "category": "crypto",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "CRY-05",
            "query": "How do automated market makers (AMMs) work in DeFi?",
            "category": "crypto",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "CRY-06",
            "query": "What is the Bitcoin Lightning Network and what problem does it solve?",
            "category": "crypto",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "CRY-07",
            "query": "Explain the controversy surrounding Tether (USDT) reserves.",
            "category": "crypto",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "CRY-08",
            "query": "What are Layer 2 solutions and why are they needed for Ethereum?",
            "category": "crypto",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "CRY-09",
            "query": "How is crypto correlated to equities and when does this break?",
            "category": "crypto",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "CRY-10",
            "query": "What is the four-year crypto market cycle theory?",
            "category": "crypto",
            "expected_outcome": "ANSWER"
        }
    ],
    "technical_analysis": [
        {
            "id": "TEC-01",
            "query": "How do you identify support and resistance levels?",
            "category": "technical",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "TEC-02",
            "query": "What is the RSI indicator and how do you interpret overbought/oversold conditions?",
            "category": "technical",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "TEC-03",
            "query": "Explain the MACD indicator and signal line crossovers.",
            "category": "technical",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "TEC-04",
            "query": "What is a golden cross and death cross in moving averages?",
            "category": "technical",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "TEC-05",
            "query": "How do Bollinger Bands work and what is a squeeze?",
            "category": "technical",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "TEC-06",
            "query": "What are Fibonacci retracement levels and why do they work?",
            "category": "technical",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "TEC-07",
            "query": "Explain the head and shoulders chart pattern.",
            "category": "technical",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "TEC-08",
            "query": "How does volume confirm price moves in technical analysis?",
            "category": "technical",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "TEC-09",
            "query": "What are the limitations of technical analysis according to EMH?",
            "category": "technical",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "TEC-10",
            "query": "What is the put/call ratio and how is it used as a sentiment indicator?",
            "category": "technical",
            "expected_outcome": "ANSWER"
        }
    ],
    "regulatory": [
        {
            "id": "REG-01",
            "query": "What are the SEC's enforcement powers regarding insider trading?",
            "category": "regulatory",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "REG-02",
            "query": "What changes did Dodd-Frank make to financial regulation?",
            "category": "regulatory",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "REG-03",
            "query": "Explain Basel III capital requirements and their purpose.",
            "category": "regulatory",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "REG-04",
            "query": "What is the current framework for crypto regulation in the US?",
            "category": "regulatory",
            "expected_outcome": "ANSWER"
        },
        {
            "id": "REG-05",
            "query": "What is MiFID II and how does it affect European markets?",
            "category": "regulatory",
            "expected_outcome": "ANSWER"
        }
    ],
    "edge_cases_halt": [
        {
            "id": "EDG-01",
            "query": "What will the exact price of Bitcoin be on December 31, 2025?",
            "category": "edge_halt",
            "expected_outcome": "HALT"
        },
        {
            "id": "EDG-02",
            "query": "Should I sell all my stocks tomorrow morning?",
            "category": "edge_halt",
            "expected_outcome": "HALT"
        },
        {
            "id": "EDG-03",
            "query": "What is the secret algorithm that guarantees stock market profits?",
            "category": "edge_halt",
            "expected_outcome": "HALT"
        },
        {
            "id": "EDG-04",
            "query": "Predict the next Fed chair based on unnamed sources.",
            "category": "edge_halt",
            "expected_outcome": "HALT"
        },
        {
            "id": "EDG-05",
            "query": "Give me insider information about Apple's unreleased product.",
            "category": "edge_halt",
            "expected_outcome": "HALT"
        }
    ]
}

class FinanceTestSuite:
    def __init__(self, output_dir="test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
    def run_query(self, query_entry, openeyes_instance):
        """Run a single query and capture metrics."""
        start_time = time.time()
        
        try:
            response = openeyes_instance.query(query_entry["query"])
            elapsed = time.time() - start_time
            
            # Determine outcome
            is_halt = response.get("halt", False)
            outcome = "HALT" if is_halt else "ANSWER"
            
            # Extract details
            confidence = response.get("confidence_score", 0.0)
            fragments_used = response.get("fragments_used", [])
            
            result = {
                "id": query_entry["id"],
                "query": query_entry["query"],
                "category": query_entry["category"],
                "expected_outcome": query_entry["expected_outcome"],
                "actual_outcome": outcome,
                "success": outcome == query_entry["expected_outcome"],
                "confidence_score": confidence,
                "fragments_used": fragments_used,
                "fragment_count": len(fragments_used),
                "time_taken_ms": round(elapsed * 1000, 2),
                "manual_verification_status": "PENDING",
                "timestamp": datetime.now().isoformat(),
                "response_summary": str(response.get("answer", ""))[:200] if not is_halt else None,
                "halt_reason": response.get("halt_reason") if is_halt else None
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            result = {
                "id": query_entry["id"],
                "query": query_entry["query"],
                "category": query_entry["category"],
                "expected_outcome": query_entry["expected_outcome"],
                "actual_outcome": "ERROR",
                "success": False,
                "confidence_score": 0.0,
                "fragments_used": [],
                "fragment_count": 0,
                "time_taken_ms": round(elapsed * 1000, 2),
                "manual_verification_status": "PENDING",
                "timestamp": datetime.now().isoformat(),
                "error_message": str(e)
            }
        
        return result

    def run_full_suite(self, openeyes_instance):
        """Run all 50 test queries."""
        print(f"Starting OpenEyes Finance Test Suite ({datetime.now().isoformat()})")
        print("=" * 60)
        
        all_queries = []
        for category, queries in TEST_QUERIES.items():
            all_queries.extend(queries)
        
        total = len(all_queries)
        print(f"Total queries to run: {total}")
        
        for i, query_entry in enumerate(all_queries, 1):
            print(f"[{i}/{total}] Running {query_entry['id']}: {query_entry['query'][:50]}...")
            result = self.run_query(query_entry, openeyes_instance)
            self.results.append(result)
            
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            print(f"  -> {status} ({result['actual_outcome']}, {result['time_taken_ms']}ms)")
        
        self.save_results()
        self.print_summary()
        
        return self.results

    def save_results(self):
        """Save results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"finance_test_results_{timestamp}.json"
        
        report = {
            "metadata": {
                "timestamp": timestamp,
                "total_queries": len(self.results),
                "suite_version": "1.0"
            },
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nResults saved to: {filename}")
        return filename

    def print_summary(self):
        """Print test summary statistics."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        
        # Category breakdown
        categories = {}
        for r in self.results:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "passed": 0}
            categories[cat]["total"] += 1
            if r["success"]:
                categories[cat]["passed"] += 1
        
        print("\n" + "=" * 60)
        print("TEST SUITE SUMMARY")
        print("=" * 60)
        print(f"Total Queries: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        
        print("\nBreakdown by Category:")
        for cat, stats in sorted(categories.items()):
            pct = stats["passed"]/stats["total"]*100 if stats["total"] > 0 else 0
            print(f"  {cat}: {stats['passed']}/{stats['total']} ({pct:.1f}%)")
        
        # Average timing
        avg_time = sum(r["time_taken_ms"] for r in self.results) / total if total > 0 else 0
        print(f"\nAverage Response Time: {avg_time:.2f}ms")
        
        # Confidence distribution
        answers = [r for r in self.results if r["actual_outcome"] == "ANSWER"]
        if answers:
            avg_conf = sum(r["confidence_score"] for r in answers) / len(answers)
            print(f"Average Confidence Score (Answers): {avg_conf:.2f}")

def main():
    """Standalone execution placeholder."""
    print("Finance Test Suite ready.")
    print("Usage: Import FinanceTestSuite and call run_full_suite(openeyes_instance)")
    print("\nExample:")
    print("  from openeyes.query_interface import OpenEyes")
    print("  from openeyes.tools.finance_test_suite import FinanceTestSuite")
    print("  ")
    print("  oe = OpenEyes()")
    print("  suite = FinanceTestSuite()")
    print("  suite.run_full_suite(oe)")

if __name__ == "__main__":
    main()
