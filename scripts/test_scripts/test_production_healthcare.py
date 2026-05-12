#!/usr/bin/env python3
"""
Production-Ready Domain Test Suite: Healthcare
50 randomized queries imitating real user behavior
"""

import json
import random
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import tempfile
import shutil

from openeyes.core.engine import OpenEyesEngine

random.seed(int(time.time()))

class HealthcareQueryGenerator:
    QUERY_PATTERNS = {
        'symptom_check': [
            "What does {symptom} mean?",
            "I have {symptom}, should I worry?",
            "{symptom} - serious or normal?",
            "Why am I experiencing {symptom}?",
            "Is {symptom} a sign of something bad?",
            "Getting {symptom} randomly, help",
            "{symptom} for {duration}",
            "Sudden {symptom}, what to do?",
        ],
        'drug_info': [
            "What is {drug} used for?",
            "Side effects of {drug}",
            "Can I take {drug} with {other_drug}?",
            "How to take {drug} properly?",
            "Is {drug} safe during pregnancy?",
            "Generic version of {drug}?",
            "What happens if I miss a dose of {drug}?",
            "Long term effects of {drug}",
            "Does {drug} cause weight gain?",
            "Alternative to {drug}",
        ],
        'condition_info': [
            "Tell me about {condition}",
            "What causes {condition}?",
            "How is {condition} diagnosed?",
            "Treatment options for {condition}",
            "Can {condition} be cured?",
            "Living with {condition} tips",
            "Early signs of {condition}",
            "Is {condition} hereditary?",
            "Complications from {condition}",
            "Prevention of {condition}",
        ],
        'urgency_triage': [
            "Emergency: {symptom}",
            "Need help now, {symptom}",
            "Should I go to ER for {symptom}?",
            "Urgent: {symptom} getting worse",
            "Quick answer needed: {symptom}",
        ],
        'comparison': [
            "Difference between {condition1} and {condition2}",
            "{drug1} vs {drug2} which is better?",
            "Which is safer: {drug1} or {drug2}?",
        ],
        'lifestyle': [
            "Diet for {condition}",
            "Exercise with {condition}",
            "Natural remedies for {symptom}",
            "How to prevent {condition}",
            "Vitamins for {condition}",
        ],
        'colloquial': [
            "feeling off, {symptom}",
            "weird sensation in my body, {symptom}",
            "doc said i have {condition}, wtf does that mean",
            "google says {symptom} could be cancer??",
            "my friend has {condition}, contagious?",
        ],
    }
    
    SYMPTOMS = [
        "chest pain", "headache", "dizziness", "nausea", "fatigue",
        "shortness of breath", "abdominal pain", "joint pain", "muscle weakness",
        "blurred vision", "numbness in hands", "rapid heartbeat", "swelling in legs",
        "persistent cough", "fever", "rash", "insomnia", "anxiety",
        "memory loss", "tremors", "difficulty swallowing", "back pain",
        "stiff neck", "confusion", "mood swings", "weight loss", "night sweats"
    ]
    
    CONDITIONS = [
        "diabetes", "hypertension", "asthma", "arthritis", "depression",
        "anxiety disorder", "migraine", "heart disease", "cancer", "stroke",
        "parkinsons disease", "alzheimers", "multiple sclerosis", "epilepsy",
        "thyroid disorder", "kidney disease", "liver disease", "anemia",
        "osteoporosis", "gout", "fibromyalgia", "chronic fatigue syndrome",
        "irritable bowel syndrome", "celiac disease", "lupus"
    ]
    
    DRUGS = [
        "metformin", "lisinopril", "atorvastatin", "omeprazole", "amlodipine",
        "metoprolol", "gabapentin", "hydrochlorothiazide", "losartan", "simvastatin",
        "levothyroxine", "azithromycin", "amoxicillin", "prednisone", "ibuprofen",
        "acetaminophen", "warfarin", "clopidogrel", "insulin", "albuterol"
    ]
    
    DURATIONS = ["2 days", "a week", "several weeks", "a month", "on and off"]
    
    @classmethod
    def generate_query(cls) -> Tuple[str, str]:
        pattern_type = random.choice(list(cls.QUERY_PATTERNS.keys()))
        pattern = random.choice(cls.QUERY_PATTERNS[pattern_type])
        
        query = pattern
        if "{symptom}" in query:
            query = query.replace("{symptom}", random.choice(cls.SYMPTOMS))
        if "{duration}" in query:
            query = query.replace("{duration}", random.choice(cls.DURATIONS))
        if "{condition}" in query:
            query = query.replace("{condition}", random.choice(cls.CONDITIONS))
        if "{drug}" in query:
            query = query.replace("{drug}", random.choice(cls.DRUGS))
        if "{other_drug}" in query:
            other = random.choice([d for d in cls.DRUGS if d != query.split()[-1]])
            query = query.replace("{other_drug}", other)
        if "{condition1}" in query and "{condition2}" in query:
            conds = random.sample(cls.CONDITIONS, 2)
            query = query.replace("{condition1}", conds[0]).replace("{condition2}", conds[1])
        if "{drug1}" in query and "{drug2}" in query:
            drugs = random.sample(cls.DRUGS, 2)
            query = query.replace("{drug1}", drugs[0]).replace("{drug2}", drugs[1])
        
        if random.random() < 0.2:
            query = cls._add_noise(query)
        
        return query, pattern_type
    
    @staticmethod
    def _add_noise(text: str) -> str:
        noise_types = [
            lambda t: t.lower(),
            lambda t: t.replace("ing", "in"),
            lambda t: t + " pls",
            lambda t: t.replace("what", "wat"),
            lambda t: t.replace("the", ""),
        ]
        return random.choice(noise_types)(text)


def run_test_suite(num_queries=50):
    vault_path = Path(tempfile.mkdtemp(prefix="openeyes_test_"))
    engine = OpenEyesEngine(vault_path=vault_path)
    
    results = []
    start_time = datetime.now()
    
    print(f"\n{'='*70}")
    print(f"HEALTHCARE DOMAIN PRODUCTION TEST SUITE")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {num_queries} randomized queries")
    print(f"{'='*70}\n")
    
    generator = HealthcareQueryGenerator()
    
    for i in range(num_queries):
        query, category = generator.generate_query()
        start = time.time()
        
        try:
            result = engine.answer(query, domain="healthcare")
            elapsed = time.time() - start
            
            result_entry = {
                'query_num': i + 1,
                'query': query,
                'category': category,
                'status': result.get('status', 'UNKNOWN'),
                'answer_class': result.get('answer_class', 'UNKNOWN'),
                'confidence': result.get('confidence', 0.0),
                'domain': result.get('domain', ''),
                'data_recency_years': result.get('data_recency_years', -1),
                'elapsed_seconds': round(elapsed, 3),
                'answer_length': len(result.get('answer', '')),
                'has_narrative': 'narrative' in result and bool(result.get('narrative')),
                'error': None
            }
        except Exception as e:
            elapsed = time.time() - start
            result_entry = {
                'query_num': i + 1,
                'query': query,
                'category': category,
                'status': 'ERROR',
                'answer_class': 'ERROR',
                'confidence': 0.0,
                'domain': '',
                'data_recency_years': -1,
                'elapsed_seconds': round(elapsed, 3),
                'answer_length': 0,
                'has_narrative': False,
                'error': str(e)
            }
        
        results.append(result_entry)
        
        status_icon = "OK" if result_entry['status'].startswith('ANSWER') else "HALT"
        conf_display = f"{result_entry['confidence']:.1f}%" if result_entry['confidence'] > 0 else "N/A"
        print(f"[{i+1:2d}/{num_queries}] {status_icon} [{category:15s}] conf={conf_display:6s} time={result_entry['elapsed_seconds']:.2f}s")
        if result_entry['error']:
            print(f"         ERROR: {result_entry['error'][:60]}...")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    shutil.rmtree(vault_path, ignore_errors=True)
    
    return results, duration


def analyze_results(results, duration):
    total = len(results)
    answered = [r for r in results if r['status'].startswith('ANSWER')]
    halted = [r for r in results if r['status'].startswith('HALT')]
    errors = [r for r in results if r['status'] == 'ERROR']
    
    confident_answers = [r for r in answered if r['confidence'] >= 70]
    low_confidence = [r for r in answered if 0 < r['confidence'] < 70]
    
    avg_confidence = sum(r['confidence'] for r in answered) / len(answered) if answered else 0
    avg_time = sum(r['elapsed_seconds'] for r in results) / total if total else 0
    
    by_category = {}
    for cat in set(r['category'] for r in results):
        cat_results = [r for r in results if r['category'] == cat]
        cat_answered = [r for r in cat_results if r['status'].startswith('ANSWER')]
        by_category[cat] = {
            'total': len(cat_results),
            'answered': len(cat_answered),
            'rate': len(cat_answered) / len(cat_results) * 100 if cat_results else 0,
            'avg_confidence': sum(r['confidence'] for r in cat_answered) / len(cat_answered) if cat_answered else 0
        }
    
    summary = {
        'total_queries': total,
        'answered': len(answered),
        'halted': len(halted),
        'errors': len(errors),
        'success_rate': len(answered) / total * 100 if total else 0,
        'confident_rate': len(confident_answers) / total * 100 if total else 0,
        'low_confidence_count': len(low_confidence),
        'average_confidence': avg_confidence,
        'average_response_time': avg_time,
        'total_duration_seconds': duration,
        'by_category': by_category,
        'queries_per_second': total / duration if duration > 0 else 0
    }
    
    weaknesses = []
    for cat, stats in summary['by_category'].items():
        if stats['rate'] < 60:
            weaknesses.append({
                'area': f"Category: {cat}",
                'issue': f"Low answer rate ({stats['rate']:.1f}%)",
                'severity': 'HIGH' if stats['rate'] < 40 else 'MEDIUM'
            })
        if stats['avg_confidence'] < 50 and stats['answered'] > 0:
            weaknesses.append({
                'area': f"Category: {cat}",
                'issue': f"Low average confidence ({stats['avg_confidence']:.1f}%)",
                'severity': 'MEDIUM'
            })
    
    slow_queries = [r for r in results if r['elapsed_seconds'] > 2.0]
    if len(slow_queries) > total * 0.1:
        weaknesses.append({
            'area': 'Performance',
            'issue': f"{len(slow_queries)} queries took >2 seconds",
            'severity': 'MEDIUM'
        })
    
    if len(halted) > total * 0.3:
        weaknesses.append({
            'area': 'Knowledge Coverage',
            'issue': f"High halt rate ({len(halted)/total*100:.1f}%) indicates knowledge gaps",
            'severity': 'HIGH'
        })
    
    return summary, weaknesses


def main():
    results, duration = run_test_suite(num_queries=50)
    summary, weaknesses = analyze_results(results, duration)
    
    print(f"\n{'='*70}")
    print("TEST SUITE RESULTS SUMMARY")
    print(f"{'='*70}")
    
    print(f"\nOVERALL METRICS:")
    print(f"   Total Queries:        {summary['total_queries']}")
    print(f"   Successful Answers:   {summary['answered']} ({summary['success_rate']:.1f}%)")
    print(f"   Confident Answers:    {summary['confident_rate']:.1f}% (>=70% confidence)")
    print(f"   Halted/No Answer:     {summary['halted']}")
    print(f"   Errors:               {summary['errors']}")
    print(f"   Average Confidence:   {summary['average_confidence']:.1f}%")
    print(f"   Avg Response Time:    {summary['average_response_time']:.3f}s")
    print(f"   Throughput:           {summary['queries_per_second']:.2f} queries/sec")
    print(f"   Total Duration:       {summary['total_duration_seconds']:.2f}s")
    
    print(f"\nBY QUERY CATEGORY:")
    for cat, stats in sorted(summary['by_category'].items()):
        bar_len = int(stats['rate'] / 5)
        bar = "#" * bar_len
        print(f"   {cat:20s}: {stats['answered']:2d}/{stats['total']:2d} ({stats['rate']:5.1f}%) {bar} [avg conf: {stats['avg_confidence']:.1f}%]")
    
    if weaknesses:
        print(f"\nIDENTIFIED WEAKNESSES:")
        for w in weaknesses:
            sev = "[HIGH]" if w['severity'] == 'HIGH' else "[MED]"
            print(f"   {sev} {w['area']}: {w['issue']}")
    else:
        print(f"\nNo critical weaknesses identified")
    
    results_file = Path("/workspace/test_results/healthcare_production_test.json")
    results_file.parent.mkdir(exist_ok=True)
    
    detailed_report = {
        'timestamp': datetime.now().isoformat(),
        'duration_seconds': duration,
        'summary': summary,
        'weaknesses': weaknesses,
        'individual_results': results
    }
    
    with open(results_file, 'w') as f:
        json.dump(detailed_report, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return summary, weaknesses


if __name__ == "__main__":
    main()
