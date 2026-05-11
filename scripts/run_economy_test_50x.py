#!/usr/bin/env python3
"""
Run OpenEyes query test 50 times with randomized Economy domain queries.
"""

import sys
import random
sys.path.insert(0, '/workspace')

from openeyes.query_interface import OpenEyes

# Economy domain test queries - randomized mix of sectors
TEST_QUERIES = [
    # Finance (FIN)
    "What is the best advice for doing a stock exchange?",
    "How do interest rates affect bond prices?",
    "What causes stock market crashes?",
    "Explain the difference between ETFs and mutual funds.",
    "What is short selling and how does it work?",
    "How do dark pools affect market transparency?",
    "What are the risks of high-frequency trading?",
    "Explain the role of market makers in liquidity.",
    "What is the impact of quantitative easing on markets?",
    "How do earnings reports influence stock prices?",
    
    # Energy (ENR)
    "How do oil prices affect inflation?",
    "What factors drive natural gas prices?",
    "Explain the relationship between OPEC and oil supply.",
    "What is the impact of renewable energy on traditional utilities?",
    "How do geopolitical events affect energy markets?",
    "What are futures contracts in energy trading?",
    "Explain the concept of peak oil.",
    "How do refinery outages affect gasoline prices?",
    "What is the role of strategic petroleum reserves?",
    "How does weather affect energy demand?",
    
    # Commodities (COM)
    "What drives gold prices during economic uncertainty?",
    "How do agricultural commodities hedge against inflation?",
    "Explain the copper-to-gold ratio as an economic indicator.",
    "What affects wheat prices globally?",
    "How do supply chains impact commodity pricing?",
    "What is contango in commodity futures?",
    "Explain the role of speculators in commodity markets.",
    "How do currency fluctuations affect commodity prices?",
    "What are the main uses of industrial metals?",
    "How do harvest reports affect grain prices?",
    
    # Macroeconomics (MAC)
    "What is GDP and how is it calculated?",
    "How does unemployment affect economic growth?",
    "Explain the relationship between inflation and interest rates.",
    "What is the Phillips Curve?",
    "How do central banks control money supply?",
    "What causes recessions?",
    "Explain the concept of stagflation.",
    "How does consumer confidence impact the economy?",
    "What is the yield curve and why does it matter?",
    "How do trade deficits affect national economies?",
    
    # Geopolitics & Trade (GEO)
    "How do trade wars affect global markets?",
    "What is the impact of sanctions on economies?",
    "Explain the role of the IMF in global finance.",
    "How do elections affect market stability?",
    "What is the economic impact of conflicts?",
    "How do tariffs affect international trade?",
    "Explain the concept of economic sovereignty.",
    "What role does China play in global supply chains?",
    "How do Brexit-type events affect currencies?",
    "What is the impact of migration on economies?",
]

def run_single_test(run_number: int, query: str):
    """Run a single query test and return the result."""
    print(f"\n{'='*80}")
    print(f"RUN {run_number}/50")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    # Initialize OpenEyes engine (fresh instance each time)
    oe = OpenEyes(domain="economy")
    
    # Execute query
    result = oe.query(query)
    result['test_query'] = query
    
    return result

def main():
    print("="*80)
    print("OpenEyes Economy Domain Test - 50 Randomized Queries")
    print("="*80)
    
    # Shuffle queries for randomization
    random.shuffle(TEST_QUERIES)
    
    all_results = []
    
    for i in range(50):
        query = TEST_QUERIES[i % len(TEST_QUERIES)]
        result = run_single_test(i + 1, query)
        all_results.append(result)
        
        # Print summary for this run
        print(f"\n--- RUN {i+1} SUMMARY ---")
        if result.get("halt"):
            print(f"Result: HALT")
            print(f"Halt Reason: {result.get('halt_reason', 'Unknown')}")
            print(f"Answer: None")
        else:
            print(f"Result: ANSWER GENERATED")
            print(f"Confidence: {result.get('confidence', 0):.1f}%")
            answer_preview = str(result.get('answer', ''))[:80]
            print(f"Answer Preview: {answer_preview}...")
        print(f"Mode: {result.get('mode', 'Unknown')}")
        print(f"Fragments Used: {len(result.get('fragments_used', []))}")
        print(f"Trace ID: {result.get('trace_id', 'N/A')}")
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY - ALL 50 RUNS")
    print("="*80)
    
    halt_count = sum(1 for r in all_results if r.get("halt"))
    answer_count = 50 - halt_count
    
    # Calculate average confidence for answers
    confidences = [r.get('confidence', 0) for r in all_results if not r.get("halt")]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    print(f"\nTotal Runs: 50")
    print(f"Answers Generated: {answer_count}")
    print(f"Halts: {halt_count}")
    print(f"Success Rate: {(answer_count/50)*100:.1f}%")
    print(f"Average Confidence (answers only): {avg_confidence:.1f}%")
    
    print("\nDetailed Results:")
    for i, result in enumerate(all_results, 1):
        status = "HALT" if result.get("halt") else "ANSWER"
        confidence = result.get('confidence', 0)
        mode = result.get('mode', 'Unknown')
        fragments = len(result.get('fragments_used', []))
        query_preview = result.get('test_query', '')[:40]
        
        print(f"\n  Run {i}: {status} | Conf: {confidence:.1f}% | Frags: {fragments} | Q: {query_preview}...")
        if result.get("halt"):
            print(f"         Halt Reason: {result.get('halt_reason', 'Unknown')}")
    
    # Sector breakdown
    print("\n" + "="*80)
    print("SECTOR BREAKDOWN")
    print("="*80)
    
    sector_stats = {}
    for result in all_results:
        query = result.get('test_query', '')
        # Simple sector detection based on keywords
        if any(kw in query.lower() for kw in ['stock', 'bond', 'market', 'trading', 'earnings', 'etf', 'short']):
            sector = 'FIN'
        elif any(kw in query.lower() for kw in ['oil', 'energy', 'gas', 'renewable', 'opec', 'refinery']):
            sector = 'ENR'
        elif any(kw in query.lower() for kw in ['gold', 'commodity', 'agricultural', 'wheat', 'copper', 'metal', 'grain']):
            sector = 'COM'
        elif any(kw in query.lower() for kw in ['gdp', 'unemployment', 'inflation', 'recession', 'central bank', 'interest rate']):
            sector = 'MAC'
        elif any(kw in query.lower() for kw in ['trade', 'sanction', 'imf', 'election', 'conflict', 'tariff', 'brexit']):
            sector = 'GEO'
        else:
            sector = 'OTHER'
        
        if sector not in sector_stats:
            sector_stats[sector] = {'total': 0, 'answers': 0, 'halts': 0}
        
        sector_stats[sector]['total'] += 1
        if result.get("halt"):
            sector_stats[sector]['halts'] += 1
        else:
            sector_stats[sector]['answers'] += 1
    
    for sector, stats in sorted(sector_stats.items()):
        success_rate = (stats['answers'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {sector}: {stats['answers']}/{stats['total']} answers ({success_rate:.1f}% success)")
    
    return all_results

if __name__ == "__main__":
    main()
