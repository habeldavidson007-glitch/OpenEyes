#!/usr/bin/env python3
"""
Synapse Analysis Report Generator

Generates a comprehensive report from the Synapse index after a period of operation.
Reports on:
- Total synapses compiled
- Most triggered synapses (top 20)
- Average confidence of compiled synapses
- Domains with most/least synapse coverage
"""

import json
import os
from collections import Counter, defaultdict
from pathlib import Path

def load_synapse_index(index_path: str = "openeyes/compiled_logic/synapse_index.json"):
    """Load the synapse index from disk."""
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Synapse index not found at {index_path}")
    
    with open(index_path, 'r') as f:
        return json.load(f)

def generate_synapse_report(index_path: str = "openeyes/compiled_logic/synapse_index.json", output_path: str = "openeyes/tools/reports/synapse_report.json"):
    """
    Generate a comprehensive analysis report from the Synapse index.
    
    Args:
        index_path: Path to the synapse index JSON file
        output_path: Path to save the generated report
    
    Returns:
        dict: The generated report data
    """
    try:
        data = load_synapse_index(index_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Ensure Night Mode has been running long enough to compile synapses.")
        return None

    # Handle different possible structures of the index
    synapses = []
    if isinstance(data, list):
        synapses = data
    elif isinstance(data, dict):
        if 'synapses' in data:
            synapses = data['synapses']
        elif 'entries' in data:
            synapses = data['entries']
        else:
            # Assume it's a dict of synapse_id -> data
            synapses = [v for k, v in data.items() if isinstance(v, dict)]

    if not synapses:
        print("Warning: Synapse index is empty.")
        return {
            "status": "empty",
            "message": "No synapses found in the index."
        }

    # 1. Total synapses compiled
    total_synapses = len(synapses)

    # 2. Most triggered synapses (top 20)
    # Assuming each synapse has a 'hit_count' or 'trigger_count' field
    sorted_by_hits = sorted(
        synapses, 
        key=lambda x: x.get('hit_count', x.get('trigger_count', 0)), 
        reverse=True
    )
    top_20 = [
        {
            "id": s.get('id', s.get('query_hash', 'unknown')),
            "query_preview": s.get('query', s.get('canonical_form', ''))[:60],
            "hit_count": s.get('hit_count', s.get('trigger_count', 0)),
            "confidence": s.get('confidence', 0.0)
        }
        for s in sorted_by_hits[:20]
    ]

    # 3. Average confidence of compiled synapses
    confidences = [s.get('confidence', 0.0) for s in synapses if 'confidence' in s]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    # 4 & 5. Domain coverage analysis
    domain_counts = Counter()
    for s in synapses:
        domains = s.get('domains', [])
        tags = s.get('tags', [])
        
        # If explicit domains exist
        if domains:
            for d in domains:
                domain_counts[d] += 1
        # Infer from tags if domains missing
        elif tags:
            # Simple heuristic: first tag often indicates domain in our taxonomy
            # In a real system, this would use a tag-to-domain mapping
            if any(t in ['macro', 'monetary_policy', 'fed', 'inflation'] for t in tags):
                domain_counts['finance_macro'] += 1
            elif any(t in ['earnings', 'revenue', 'valuation'] for t in tags):
                domain_counts['finance_fundamentals'] += 1
            elif any(t in ['crypto', 'bitcoin', 'ethereum'] for t in tags):
                domain_counts['crypto'] += 1
            elif any(t in ['technical_analysis', 'rsi', 'macd'] for t in tags):
                domain_counts['technical_analysis'] += 1
            elif any(t in ['regulation', 'sec', 'compliance'] for t in tags):
                domain_counts['regulation'] += 1
            else:
                domain_counts['general'] += 1
        else:
            domain_counts['unclassified'] += 1

    # Sort domains by count
    sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
    domains_most = sorted_domains[:5]
    domains_least = sorted_domains[-5:] if len(sorted_domains) >= 5 else sorted_domains

    # Construct Report
    report = {
        "report_type": "synapse_analysis",
        "generated_at": "2026-01-01T00:00:00Z", # Placeholder, could use datetime.now()
        "summary": {
            "total_synapses_compiled": total_synapses,
            "average_confidence": round(avg_confidence, 4),
            "unique_domains_detected": len(domain_counts)
        },
        "top_triggered_synapses": top_20,
        "domain_coverage": {
            "most_covered": [
                {"domain": d, "count": c} for d, c in domains_most
            ],
            "least_covered": [
                {"domain": d, "count": c} for d, c in domains_least
            ]
        },
        "recommendations": []
    }

    # Add simple recommendations
    if avg_confidence < 0.7:
        report["recommendations"].append("Average confidence is low. Consider tightening fragment selection criteria or improving source credibility.")
    
    if total_synapses < 100:
        report["recommendations"].append("Low synapse count. Ensure Night Mode is running consistently and query volume is sufficient.")
    
    if domains_least and domains_least[0][1] < 5:
        report["recommendations"].append(f"Domain '{domains_least[0][0]}' has very low coverage. Consider adding more fragments or queries in this area.")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save report
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    # Print summary to console
    print("="*50)
    print("SYNAPSE ANALYSIS REPORT")
    print("="*50)
    print(f"Total Synapses Compiled: {total_synapses}")
    print(f"Average Confidence:      {avg_confidence:.4f}")
    print("\nTop 5 Domains by Coverage:")
    for d, c in domains_most[:5]:
        print(f"  - {d}: {c}")
    print("\nBottom 5 Domains by Coverage:")
    for d, c in domains_least:
        print(f"  - {d}: {c}")
    print(f"\nFull report saved to: {output_path}")
    print("="*50)

    return report

if __name__ == "__main__":
    generate_synapse_report()
