#!/usr/bin/env python3
"""
Run OpenEyes query test 5 times end-to-end and report results.
"""

import sys
sys.path.insert(0, '/workspace')

from openeyes.query_interface import OpenEyes

# Test query
TEST_QUERY = "What are the early symptoms of pancreatic cancer?"
DOMAIN = "medical"

def run_single_test(run_number: int):
    """Run a single query test and return the result."""
    print(f"\n{'='*80}")
    print(f"RUN {run_number}/5")
    print(f"{'='*80}")
    
    # Initialize OpenEyes engine (fresh instance each time)
    oe = OpenEyes(domain=DOMAIN)
    
    # Execute query
    result = oe.query(TEST_QUERY)
    
    return result

def main():
    print("="*80)
    print("OpenEyes End-to-End Query Test - 5 Runs")
    print(f"Query: {TEST_QUERY}")
    print(f"Domain: {DOMAIN}")
    print("="*80)
    
    all_results = []
    
    for i in range(1, 6):
        result = run_single_test(i)
        all_results.append(result)
        
        # Print summary for this run
        print(f"\n--- RUN {i} SUMMARY ---")
        if result.get("halt"):
            print(f"Result: HALT")
            print(f"Halt Reason: {result.get('halt_reason', 'Unknown')}")
            print(f"Answer: None")
        else:
            print(f"Result: ANSWER GENERATED")
            print(f"Confidence: {result.get('confidence', 0):.1f}%")
            print(f"Answer: {result.get('answer', 'No answer')}")
        print(f"Mode: {result.get('mode', 'Unknown')}")
        print(f"Fragments Used: {len(result.get('fragments_used', []))}")
        print(f"Trace ID: {result.get('trace_id', 'N/A')}")
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY - ALL 5 RUNS")
    print("="*80)
    
    halt_count = sum(1 for r in all_results if r.get("halt"))
    answer_count = 5 - halt_count
    
    print(f"\nTotal Runs: 5")
    print(f"Answers Generated: {answer_count}")
    print(f"Halts: {halt_count}")
    
    print("\nDetailed Results:")
    for i, result in enumerate(all_results, 1):
        status = "HALT" if result.get("halt") else "ANSWER"
        confidence = result.get('confidence', 0)
        mode = result.get('mode', 'Unknown')
        fragments = len(result.get('fragments_used', []))
        
        print(f"\n  Run {i}: {status} | Confidence: {confidence:.1f}% | Mode: {mode} | Fragments: {fragments}")
        if result.get("halt"):
            print(f"         Halt Reason: {result.get('halt_reason', 'Unknown')}")
        else:
            answer_preview = str(result.get('answer', ''))[:100]
            print(f"         Answer Preview: {answer_preview}...")
    
    return all_results

if __name__ == "__main__":
    main()
