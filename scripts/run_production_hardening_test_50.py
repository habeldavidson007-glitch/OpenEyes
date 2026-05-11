#!/usr/bin/env python3
"""
OpenEyes Production Domain Hardening Test - 50 Randomized Queries

This script runs 50 end-to-end queries on the healthcare domain (production-ready),
randomized to imitate how real users would query the system.

User behavior patterns simulated:
1. Direct symptom queries
2. Treatment questions
3. Diagnostic inquiries
4. Prevention/wellness questions
5. Emergency vs non-emergency distinction
6. Vague/ambiguous queries
7. Multi-symptom combinations
8. Drug interaction checks
9. Second opinion seeking
10. Procedural questions
"""

import sys
import random
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/workspace')

from openeyes.query_interface import OpenEyes

# ============================================================================
# HEALTHCARE DOMAIN QUERY TEMPLATES (Production-Ready Domain)
# ============================================================================

QUERY_TEMPLATES = {
    # Category 1: Direct Symptom Queries (most common user behavior)
    "symptom_direct": [
        "What are the symptoms of {condition}?",
        "Early signs of {condition}",
        "How do I know if I have {condition}?",
        "{condition} symptoms checklist",
        "Common symptoms for {condition}",
    ],
    
    # Category 2: Treatment Questions
    "treatment": [
        "What is the best treatment for {condition}?",
        "How is {condition} treated?",
        "Treatment options for {condition}",
        "Can {condition} be cured?",
        "What medications are used for {condition}?",
    ],
    
    # Category 3: Diagnostic Inquiries
    "diagnostic": [
        "How is {condition} diagnosed?",
        "What tests are needed for {condition}?",
        "Diagnosis process for {condition}",
        "What does a {condition} test involve?",
    ],
    
    # Category 4: Prevention & Wellness
    "prevention": [
        "How can I prevent {condition}?",
        "Risk factors for {condition}",
        "Lifestyle changes to avoid {condition}",
        "Is {condition} preventable?",
    ],
    
    # Category 5: Drug & Interaction Questions
    "drug_interaction": [
        "Can I take {medication} with {medication2}?",
        "Side effects of {medication}",
        "Is {medication} safe for long-term use?",
        "What should I avoid while taking {medication}?",
    ],
    
    # Category 6: Emergency vs Non-Emergency
    "emergency_assessment": [
        "Is {symptom} an emergency?",
        "When should I go to ER for {symptom}?",
        "Should I see a doctor for {symptom}?",
        "Urgent care vs ER for {symptom}",
    ],
    
    # Category 7: Multi-Symptom Combinations (real users often describe multiple issues)
    "multi_symptom": [
        "I have {symptom1} and {symptom2}, what could it be?",
        "{symptom1} together with {symptom2} - should I worry?",
        "Experiencing {symptom1}, {symptom2}, and {symptom3}",
    ],
    
    # Category 8: Vague/Ambiguous Queries (very common in real usage)
    "vague": [
        "I don't feel well",
        "Something's wrong with my {body_part}",
        "Been feeling tired lately",
        "Is this normal?",
        "Should I be concerned about {symptom}?",
    ],
    
    # Category 9: Second Opinion Seeking
    "second_opinion": [
        "My doctor said I have {condition}, is this correct?",
        "Alternative diagnoses for {symptoms}",
        "Could {condition} be something else?",
    ],
    
    # Category 10: Procedural Questions
    "procedural": [
        "What happens during a {procedure}?",
        "How to prepare for {procedure}?",
        "Recovery time after {procedure}?",
        "Is {procedure} painful?",
    ],
}

# Medical conditions for templating
CONDITIONS = [
    "diabetes", "hypertension", "asthma", "migraine", "arthritis",
    "depression", "anxiety", "heart disease", "pneumonia", "bronchitis",
    "gastritis", "acid reflux", "insomnia", "thyroid disorder", "anemia",
    "osteoporosis", "eczema", "psoriasis", "UTI", "kidney stones"
]

# Medications
MEDICATIONS = [
    "ibuprofen", "aspirin", "metformin", "lisinopril", "omeprazole",
    "amlodipine", "metoprolol", "gabapentin", "hydrochlorothiazide", "sertraline"
]

# Symptoms
SYMPTOMS = [
    "chest pain", "shortness of breath", "headache", "dizziness",
    "nausea", "fatigue", "fever", "cough", "abdominal pain", "back pain",
    "joint pain", "rash", "swelling", "numbness", "blurred vision"
]

# Body parts
BODY_PARTS = [
    "chest", "stomach", "head", "back", "knee", "shoulder", "arm", "leg"
]

# Procedures
PROCEDURES = [
    "blood test", "MRI scan", "endoscopy", "colonoscopy", "biopsy",
    "X-ray", "ultrasound", "CT scan", "stress test", "pap smear"
]


def generate_random_query() -> tuple[str, str]:
    """Generate a randomized query imitating user behavior."""
    
    category = random.choice(list(QUERY_TEMPLATES.keys()))
    template = random.choice(QUERY_TEMPLATES[category])
    
    # Fill in template variables based on category
    if category == "symptom_direct":
        query = template.format(condition=random.choice(CONDITIONS))
    elif category == "treatment":
        query = template.format(condition=random.choice(CONDITIONS))
    elif category == "diagnostic":
        query = template.format(condition=random.choice(CONDITIONS))
    elif category == "prevention":
        query = template.format(condition=random.choice(CONDITIONS))
    elif category == "drug_interaction":
        meds = random.sample(MEDICATIONS, 2)
        query = template.format(medication=meds[0], medication2=meds[1])
    elif category == "emergency_assessment":
        query = template.format(symptom=random.choice(SYMPTOMS))
    elif category == "multi_symptom":
        syms = random.sample(SYMPTOMS, 3)
        query = template.format(symptom1=syms[0], symptom2=syms[1], symptom3=syms[2])
    elif category == "vague":
        if "{body_part}" in template:
            query = template.format(body_part=random.choice(BODY_PARTS))
        elif "{symptom}" in template:
            query = template.format(symptom=random.choice(SYMPTOMS))
        else:
            query = template
    elif category == "second_opinion":
        if "{condition}" in template:
            query = template.format(condition=random.choice(CONDITIONS))
        else:
            query = template.format(symptoms=random.choice(SYMPTOMS))
    elif category == "procedural":
        query = template.format(procedure=random.choice(PROCEDURES))
    else:
        query = template
    
    return query, category


def run_single_query(query: str, category: str, run_number: int) -> dict:
    """Execute a single query and capture all metrics."""
    
    start_time = time.time()
    
    try:
        # Initialize fresh OpenEyes instance
        oe = OpenEyes(domain="healthcare")
        
        # Execute query
        result = oe.query(query)
        
        elapsed = time.time() - start_time
        
        return {
            "run_number": run_number,
            "query": query,
            "category": category,
            "success": True,
            "halt": result.get("halt", False),
            "halt_reason": result.get("halt_reason", None),
            "mode": result.get("mode", "Unknown"),
            "confidence": result.get("confidence", 0.0),
            "answer": result.get("answer", None),
            "fragments_used": len(result.get("fragments_used", [])),
            "trace_id": result.get("trace_id", "N/A"),
            "execution_time_sec": round(elapsed, 3),
            "error": None
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "run_number": run_number,
            "query": query,
            "category": category,
            "success": False,
            "halt": True,
            "halt_reason": "EXCEPTION",
            "mode": "ERROR",
            "confidence": 0.0,
            "answer": None,
            "fragments_used": 0,
            "trace_id": "N/A",
            "execution_time_sec": round(elapsed, 3),
            "error": str(e)
        }


def main():
    print("="*100)
    print("OpenEyes Production Domain Hardening Test")
    print("50 Randomized Healthcare Queries - End-to-End")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*100)
    
    all_results = []
    category_stats = {}
    
    # Run 50 randomized queries
    for i in range(1, 51):
        query, category = generate_random_query()
        
        print(f"\n[{i}/50] Category: {category}")
        print(f"      Query: \"{query}\"")
        
        result = run_single_query(query, category, i)
        all_results.append(result)
        
        # Track category statistics
        if category not in category_stats:
            category_stats[category] = {"total": 0, "halts": 0, "answers": 0, "errors": 0}
        category_stats[category]["total"] += 1
        
        if result["halt"]:
            category_stats[category]["halts"] += 1
            status = "HALT"
            if result["error"]:
                category_stats[category]["errors"] += 1
                print(f"      Status: {status} ({result['halt_reason']}) - ERROR: {result['error']}")
            else:
                print(f"      Status: {status} ({result['halt_reason']})")
        else:
            category_stats[category]["answers"] += 1
            print(f"      Status: ANSWER | Confidence: {result['confidence']:.1f}% | Fragments: {result['fragments_used']} | Time: {result['execution_time_sec']}s")
        
        # Small delay to avoid overwhelming the system
        time.sleep(0.1)
    
    # ========================================================================
    # COMPREHENSIVE SUMMARY REPORT
    # ========================================================================
    
    print("\n\n" + "="*100)
    print("COMPREHENSIVE TEST RESULTS SUMMARY")
    print("="*100)
    
    total_runs = len(all_results)
    successful_queries = sum(1 for r in all_results if r["success"])
    halted_queries = sum(1 for r in all_results if r["halt"])
    answered_queries = total_runs - halted_queries
    error_queries = sum(1 for r in all_results if r["error"])
    
    avg_confidence = sum(r["confidence"] for r in all_results if not r["halt"]) / max(answered_queries, 1)
    avg_execution_time = sum(r["execution_time_sec"] for r in all_results) / total_runs
    avg_fragments = sum(r["fragments_used"] for r in all_results) / total_runs
    
    print(f"""
OVERALL METRICS:
----------------
Total Queries Executed:     {total_runs}
Successful Executions:      {successful_queries} ({successful_queries/total_runs*100:.1f}%)
Errors:                     {error_queries} ({error_queries/total_runs*100:.1f}%)

Answer/Halt Breakdown:
  - Answers Generated:      {answered_queries} ({answered_queries/total_runs*100:.1f}%)
  - Halts (Abstentions):    {halted_queries} ({halted_queries/total_runs*100:.1f}%)

Performance Metrics:
  - Avg Confidence:         {avg_confidence:.1f}%
  - Avg Execution Time:     {avg_execution_time:.2f}s
  - Avg Fragments Used:     {avg_fragments:.1f}
""")
    
    # Category breakdown
    print("\nCATEGORY BREAKDOWN:")
    print("-"*80)
    print(f"{'Category':<25} {'Total':<8} {'Answers':<10} {'Halts':<8} {'Errors':<8} {'Answer Rate':<12}")
    print("-"*80)
    
    for cat, stats in sorted(category_stats.items()):
        answer_rate = stats["answers"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"{cat:<25} {stats['total']:<8} {stats['answers']:<10} {stats['halts']:<8} {stats['errors']:<8} {answer_rate:>5.1f}%")
    
    # Halt reasons analysis
    halt_reasons = {}
    for r in all_results:
        if r["halt"] and not r["error"]:
            reason = r["halt_reason"] or "Unknown"
            halt_reasons[reason] = halt_reasons.get(reason, 0) + 1
    
    if halt_reasons:
        print("\n\nHALT REASONS DISTRIBUTION:")
        print("-"*60)
        for reason, count in sorted(halt_reasons.items(), key=lambda x: -x[1]):
            pct = count / halted_queries * 100
            print(f"  {reason:<35} {count:>3} ({pct:>5.1f}%)")
    
    # Sample queries by outcome
    print("\n\nSAMPLE QUERIES BY OUTCOME:")
    print("-"*100)
    
    sample_answers = [r for r in all_results if not r["halt"]][:5]
    sample_halts = [r for r in all_results if r["halt"] and not r["error"]][:5]
    sample_errors = [r for r in all_results if r["error"]][:5]
    
    if sample_answers:
        print("\nSample ANSWERS:")
        for r in sample_answers:
            print(f"  [{r['category']}] \"{r['query'][:60]}...\" -> Confidence: {r['confidence']:.1f}%")
    
    if sample_halts:
        print("\nSample HALTS:")
        for r in sample_halts:
            print(f"  [{r['category']}] \"{r['query'][:60]}...\" -> {r['halt_reason']}")
    
    if sample_errors:
        print("\nSample ERRORS:")
        for r in sample_errors:
            print(f"  [{r['category']}] \"{r['query'][:60]}...\" -> ERROR: {r['error'][:50]}")
    
    # Save detailed results
    output_file = Path("/workspace/test_results/production_hardening_test_50.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    report_data = {
        "test_metadata": {
            "timestamp": datetime.now().isoformat(),
            "domain": "healthcare",
            "total_queries": total_runs,
            "test_type": "randomized_user_simulation"
        },
        "overall_metrics": {
            "total_runs": total_runs,
            "successful_executions": successful_queries,
            "errors": error_queries,
            "answers_generated": answered_queries,
            "halts": halted_queries,
            "avg_confidence": avg_confidence,
            "avg_execution_time_sec": avg_execution_time,
            "avg_fragments_used": avg_fragments
        },
        "category_statistics": category_stats,
        "halt_reasons_distribution": halt_reasons,
        "all_results": all_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n\nDetailed results saved to: {output_file}")
    print("="*100)
    
    return report_data


if __name__ == "__main__":
    main()
