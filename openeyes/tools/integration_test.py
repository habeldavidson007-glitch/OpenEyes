"""
OpenEyes Integration Test with SEO Trend Queries

This script tests the complete Day Mode flow using real-world complex queries
harvested from SEO trends. It demonstrates:

1. Query decomposition by Swarm
2. Fragment retrieval and credibility scoring
3. Monte Carlo evaluation with survival filtering
4. Philosophy Guard validation
5. Dice Table assembly or HALT decision
6. Obsidian audit trail generation

Run this to see how OpenEyes handles high-stakes questions where 
"mostly right" is worse than silence.
"""

import json
from datetime import datetime
from pathlib import Path

from openeyes.query_interface import OpenEyes
from openeyes.tools.seo_trend_harvester import SEOTrendHarvester
from shared_core.obsidian_connector import ObsidianReporter


def run_integration_test(query_text: str, domain: str = "medical", verbose: bool = True):
    """
    Run a single query through the complete OpenEyes engine.
    
    Args:
        query_text: The user query to test
        domain: Domain for rule selection (medical, legal, financial, etc.)
        verbose: Print detailed trace output
        
    Returns:
        dict: Complete result with answer/halt decision and metadata
    """
    if verbose:
        print("\n" + "=" * 80)
        print(f"QUERY: {query_text}")
        print(f"Domain: {domain} | Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
    
    # Initialize OpenEyes engine
    oe = OpenEyes(domain=domain)
    
    # Execute query
    result_obj = oe.query(query_text)
    
    # Convert QueryResult object to dict
    if hasattr(result_obj, 'to_dict'):
        result = result_obj.to_dict()
    else:
        result = result_obj
    
    if verbose:
        print("\n📊 RESULT:")
        print("-" * 80)
        
        if result.get("halt"):
            print("🛑 HALT DECISION")
            print(f"   Reason: {result.get('halt_reason', 'Unknown')}")
            print(f"   Recommendation: {result.get('recommendation', 'No recommendation provided')}")
        else:
            print("✅ ANSWER GENERATED")
            print(f"   Confidence: {result.get('confidence', 0):.1f}%")
            print(f"\n   Answer:\n   {result.get('answer', 'No answer')}")
        
        print(f"\n📋 Metadata:")
        print(f"   Trace ID: {result.get('trace_id', 'N/A')}")
        print(f"   Fragments used: {len(result.get('fragments_used', []))}")
        print(f"   Philosophy checks passed: {result.get('philosophy_checks_passed', [])}")
        
        if result.get('fragments_used'):
            print(f"\n🧩 Fragment Details:")
            for frag in result.get('fragments_used', []):
                print(f"   • {frag.get('fragment_id', 'Unknown')}")
                print(f"     Score: {frag.get('monte_carlo_score', 'N/A')}")
                print(f"     Source: {frag.get('source', 'N/A')}")
    
    return result


def run_batch_test(queries: list, domain: str = "medical"):
    """
    Run multiple queries and generate summary statistics.
    
    Args:
        queries: List of query strings
        domain: Domain for all queries
        
    Returns:
        dict: Summary statistics and individual results
    """
    print("\n" + "=" * 80)
    print("BATCH INTEGRATION TEST")
    print(f"Running {len(queries)} queries through OpenEyes engine")
    print("=" * 80)
    
    results = []
    halt_count = 0
    answer_count = 0
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Testing: {query[:60]}...")
        
        result = run_integration_test(query, domain, verbose=False)
        results.append({
            "query": query,
            "result": result
        })
        
        if result.get("halt"):
            halt_count += 1
        else:
            answer_count += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("BATCH TEST SUMMARY")
    print("=" * 80)
    print(f"Total queries: {len(queries)}")
    print(f"Answers generated: {answer_count} ({answer_count/len(queries)*100:.1f}%)")
    print(f"Halts: {halt_count} ({halt_count/len(queries)*100:.1f}%)")
    print(f"\nInterpretation:")
    if halt_count > answer_count:
        print("  ⚠️  High halt rate suggests fragment library gaps")
        print("  → Priority: Expand fragment coverage for this domain")
    else:
        print("  ✅ Good coverage - most queries found viable fragments")
    
    return {
        "total": len(queries),
        "answers": answer_count,
        "halts": halt_count,
        "results": results
    }


def main():
    """
    Main integration test workflow:
    1. Harvest trending complex queries from multiple domains
    2. Run top queries through OpenEyes
    3. Generate Obsidian audit trails
    4. Report knowledge gaps
    """
    print("=" * 80)
    print("OpenEyes Integration Test Suite")
    print("Testing engine against SEO-trending complex queries (Multi-Domain)")
    print("=" * 80)
    
    # Step 1: Harvest trending queries from multiple domains
    harvester = SEOTrendHarvester()
    
    # Medical queries
    medical_queries = harvester.get_trending_queries(category="medical", min_complexity=8, limit=3)
    
    # Engineering queries
    engineering_queries = harvester.get_trending_queries(category="engineering", min_complexity=8, limit=3)
    
    # Cooking queries
    cooking_queries = harvester.get_trending_queries(category="cooking", min_complexity=7, limit=3)
    
    all_queries = []
    print(f"\n📈 Selected queries for testing:")
    
    if medical_queries:
        print(f"\n   🏥 MEDICAL ({len(medical_queries)} queries):")
        for i, q in enumerate(medical_queries, 1):
            print(f"      {i}. {q.query} (Complexity: {q.complexity_score}/10)")
        all_queries.extend([(q.query, "medical") for q in medical_queries])
    
    if engineering_queries:
        print(f"\n   ⚙️ ENGINEERING ({len(engineering_queries)} queries):")
        for i, q in enumerate(engineering_queries, 1):
            print(f"      {i}. {q.query} (Complexity: {q.complexity_score}/10)")
        all_queries.extend([(q.query, "engineering") for q in engineering_queries])
    
    if cooking_queries:
        print(f"\n   🍳 COOKING ({len(cooking_queries)} queries):")
        for i, q in enumerate(cooking_queries, 1):
            print(f"      {i}. {q.query} (Complexity: {q.complexity_score}/10)")
        all_queries.extend([(q.query, "cooking") for q in cooking_queries])
    
    if not all_queries:
        # Fallback to hardcoded queries if harvester returns empty
        print("\n   ⚠️ No trending queries found, using fallback queries...")
        all_queries = [
            ("What are the early symptoms of pancreatic cancer?", "medical"),
            ("Is intermittent fasting safe for diabetics?", "medical"),
            ("What happens if you drink methanol?", "medical"),
            ("How do I calculate load-bearing capacity for a steel beam?", "engineering"),
            ("What's the best way to prevent concrete cracking in cold weather?", "engineering"),
            ("How do I fix a sourdough starter that won't rise?", "cooking"),
        ]
    
    # Step 2: Run integration tests
    query_texts = [q[0] for q in all_queries]
    query_domains = [q[1] for q in all_queries]
    
    print("\n" + "=" * 80)
    print("BATCH INTEGRATION TEST")
    print(f"Running {len(all_queries)} queries through OpenEyes engine")
    print("=" * 80)
    
    results = []
    halt_count = 0
    answer_count = 0
    domain_stats = {}
    
    for i, (query, domain) in enumerate(zip(query_texts, query_domains), 1):
        print(f"\n[{i}/{len(all_queries)}] Testing: {query[:60]}... (Domain: {domain})")
        
        result = run_integration_test(query, domain, verbose=False)
        results.append({
            "query": query,
            "domain": domain,
            "result": result
        })
        
        # Track domain stats
        if domain not in domain_stats:
            domain_stats[domain] = {"answers": 0, "halts": 0}
        
        if result.get("halt"):
            halt_count += 1
            domain_stats[domain]["halts"] += 1
        else:
            answer_count += 1
            domain_stats[domain]["answers"] += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("BATCH TEST SUMMARY")
    print("=" * 80)
    print(f"Total queries: {len(all_queries)}")
    print(f"Answers generated: {answer_count} ({answer_count/len(all_queries)*100:.1f}%)")
    print(f"Halts: {halt_count} ({halt_count/len(all_queries)*100:.1f}%)")
    
    print(f"\n📊 Domain Breakdown:")
    for domain, stats in domain_stats.items():
        total = stats["answers"] + stats["halts"]
        print(f"   {domain.capitalize()}: {stats['answers']}/{total} answered ({stats['answers']/total*100:.1f}%)")
    
    print(f"\nInterpretation:")
    if halt_count > answer_count:
        print("  ⚠️  High halt rate suggests fragment library gaps")
        print("  → Priority: Expand fragment coverage for this domain")
    else:
        print("  ✅ Good coverage - most queries found viable fragments")
    
    batch_results = {
        "total": len(all_queries),
        "answers": answer_count,
        "halts": halt_count,
        "domain_stats": domain_stats,
        "results": results
    }
    
    # Step 3: Generate Obsidian audit trail
    print("\n" + "=" * 80)
    print("📝 Generating Obsidian audit trails...")
    print("-" * 80)
    
    obsidian = ObsidianReporter(vault_path="workspace_obsidian_vault")
    
    for result_item in batch_results["results"]:
        query = result_item["query"]
        domain = result_item["domain"]
        result = result_item["result"]
        
        # Create metadata for the report
        metadata = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "domain": domain,
            "result_type": "halt" if result.get("halt") else "answer",
            "confidence": result.get("confidence"),
            "halt_reason": result.get("halt_reason"),
            "fragments_used": result.get("fragments_used"),
            "trace_id": result.get("trace_id")
        }
        
        # Use the reporter's method to write query trace
        note_path = obsidian.report_run(
            mc_result={"answer": result.get("answer"), "confidence": result.get("confidence")},
            run_metadata=metadata
        )
        print(f"   ✓ Written: {note_path}")
    
    # Step 4: Knowledge gap analysis
    print("\n" + "=" * 80)
    print("🔍 KNOWLEDGE GAP ANALYSIS")
    print("=" * 80)
    
    halted_queries = [r["query"] for r in batch_results["results"] if r["result"].get("halt")]
    
    if halted_queries:
        print(f"\n⚠️  {len(halted_queries)} queries resulted in HALT:")
        for q in halted_queries:
            print(f"   • {q}")
        
        print(f"\n💡 Recommended actions:")
        print(f"   1. Add verified fragments for these query patterns")
        print(f"   2. Run Night Mode simulations targeting these gaps")
        print(f"   3. Prioritize high-search-volume halted queries")
    else:
        print("\n✅ No knowledge gaps detected in this batch!")
    
    # Final summary
    print("\n" + "=" * 80)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 80)
    print(f"\nNext steps:")
    print(f"   • Review Obsidian vault for detailed traces")
    print(f"   • Add fragments for halted query patterns")
    print(f"   • Re-run test to measure improvement")
    print(f"   • Expand to legal/financial domains")
    
    return batch_results


if __name__ == "__main__":
    main()
