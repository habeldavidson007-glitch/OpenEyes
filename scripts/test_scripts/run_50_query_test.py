import json
import time
import sys
sys.path.insert(0, '/workspace')

from openeyes.core.engine import OpenEyesEngine

engine = OpenEyesEngine()

# 50 randomized queries simulating real user behavior
queries = [
    # ECONOMY (15)
    {'q': 'What is the current federal funds rate?', 'domain_expect': 'eco', 'type': 'factual'},
    {'q': 'how does inflation affect my savings?', 'domain_expect': 'eco', 'type': 'colloquial'},
    {'q': 'Explain quantitative easing.', 'domain_expect': 'eco', 'type': 'definitional'},
    {'q': 'What is GDP?', 'domain_expect': 'eco', 'type': 'definitional'},
    {'q': 'difference between stocks and bonds', 'domain_expect': 'eco', 'type': 'comparison'},
    {'q': 'unemployment rate calculation method', 'domain_expect': 'eco', 'type': 'procedural'},
    {'q': 'What happens if the US defaults on debt?', 'domain_expect': 'eco', 'type': 'hypothetical'},
    {'q': 'crypto currency regulation status', 'domain_expect': 'eco', 'type': 'regulatory'},
    {'q': 'minimum wage history USA', 'domain_expect': 'eco', 'type': 'historical'},
    {'q': 'supply and demand curve shift', 'domain_expect': 'eco', 'type': 'conceptual'},
    {'q': 'what is a recession technically?', 'domain_expect': 'eco', 'type': 'definitional'},
    {'q': 'Federal Reserve dual mandate', 'domain_expect': 'eco', 'type': 'factual'},
    {'q': 'trade deficit vs budget deficit', 'domain_expect': 'eco', 'type': 'comparison'},
    {'q': 'how do tariffs work?', 'domain_expect': 'eco', 'type': 'mechanism'},
    {'q': 'S&P 500 historical returns', 'domain_expect': 'eco', 'type': 'data'},
    
    # HEALTHCARE (20 including 3 emergencies)
    {'q': 'symptoms of type 2 diabetes', 'domain_expect': 'hc', 'type': 'factual'},
    {'q': 'I have chest pain and shortness of breath', 'domain_expect': 'hc', 'type': 'emergency'},
    {'q': 'what is metformin used for?', 'domain_expect': 'hc', 'type': 'drug_info'},
    {'q': 'side effects of statins', 'domain_expect': 'hc', 'type': 'drug_info'},
    {'q': 'How to treat a migraine?', 'domain_expect': 'hc', 'type': 'treatment'},
    {'q': 'BMI calculator formula', 'domain_expect': 'hc', 'type': 'formula'},
    {'q': 'difference between viral and bacterial infection', 'domain_expect': 'hc', 'type': 'comparison'},
    {'q': 'what is hypertension?', 'domain_expect': 'hc', 'type': 'definitional'},
    {'q': 'I think I am having a stroke help', 'domain_expect': 'hc', 'type': 'emergency'},
    {'q': 'vaccine schedule for infants', 'domain_expect': 'hc', 'type': 'schedule'},
    {'q': 'antibiotic resistance causes', 'domain_expect': 'hc', 'type': 'mechanism'},
    {'q': 'mental health therapy types', 'domain_expect': 'hc', 'type': 'info'},
    {'q': 'what is PTSD?', 'domain_expect': 'hc', 'type': 'definitional'},
    {'q': 'calories in an apple', 'domain_expect': 'hc', 'type': 'nutrition'},
    {'q': 'how much sleep do adults need?', 'domain_expect': 'hc', 'type': 'guideline'},
    {'q': 'signs of depression', 'domain_expect': 'hc', 'type': 'symptom'},
    {'q': 'what is a clinical trial?', 'domain_expect': 'hc', 'type': 'definitional'},
    {'q': 'overdose on acetaminophen what to do', 'domain_expect': 'hc', 'type': 'emergency'},
    {'q': 'HIV transmission methods', 'domain_expect': 'hc', 'type': 'factual'},
    {'q': 'benefits of Mediterranean diet', 'domain_expect': 'hc', 'type': 'lifestyle'},
    
    # GOVERNANCE (15)
    {'q': 'how does a bill become a law?', 'domain_expect': 'gov', 'type': 'procedural'},
    {'q': 'what is the electoral college?', 'domain_expect': 'gov', 'type': 'definitional'},
    {'q': 'Supreme Court appointment process', 'domain_expect': 'gov', 'type': 'procedural'},
    {'q': 'difference between House and Senate', 'domain_expect': 'gov', 'type': 'comparison'},
    {'q': 'what is judicial review?', 'domain_expect': 'gov', 'type': 'definitional'},
    {'q': 'filibuster rules explanation', 'domain_expect': 'gov', 'type': 'procedural'},
    {'q': 'NATO article 5 meaning', 'domain_expect': 'gov', 'type': 'treaty'},
    {'q': 'geneva convention summary', 'domain_expect': 'gov', 'type': 'treaty'},
    {'q': 'what is gerrymandering?', 'domain_expect': 'gov', 'type': 'definitional'},
    {'q': 'presidential veto power limits', 'domain_expect': 'gov', 'type': 'constitutional'},
    {'q': 'UN security council structure', 'domain_expect': 'gov', 'type': 'organizational'},
    {'q': 'eminent domain definition', 'domain_expect': 'gov', 'type': 'legal'},
    {'q': 'contract law basics', 'domain_expect': 'gov', 'type': 'legal'},
    {'q': 'patent vs copyright difference', 'domain_expect': 'gov', 'type': 'legal'},
    {'q': 'World Bank governance indicators', 'domain_expect': 'gov', 'type': 'data'}
]

results = []
start_time = time.time()

print('Starting 50-query randomized test suite...')
print('=' * 80)

for i, item in enumerate(queries):
    q = item['q']
    expected_domain = item['domain_expect']
    q_type = item['type']
    
    try:
        response = engine.answer(q, domain=expected_domain)
        
        # Check for emergency halt
        is_halt = response.get('status') == 'HALT_EMERGENCY' or 'emergency' in response.get('message', '').lower()
        
        # Determine success
        status = 'SUCCESS'
        if q_type == 'emergency':
            if is_halt:
                status = 'CORRECT_HALT'
            else:
                status = 'CRITICAL_FAIL_NO_HALT'
        else:
            if is_halt:
                status = 'UNNECESSARY_HALT'
            elif len(response.get('answer', '')) < 50:
                status = 'TOO_SHORT'
            elif response.get('confidence', 0) < 40:
                status = 'LOW_CONFIDENCE'
        
        result_entry = {
            'id': i + 1,
            'query': q,
            'expected_domain': expected_domain,
            'query_type': q_type,
            'status': status,
            'is_halt': is_halt,
            'confidence': response.get('confidence', 0),
            'sources_count': len(response.get('sources', [])),
            'answer_length': len(response.get('answer', '')),
            'status_raw': response.get('status'),
            'answer_snippet': response.get('answer', '')[:100] + '...' if len(response.get('answer', '')) > 100 else response.get('answer', '')
        }
        results.append(result_entry)
        
        print(f"[{i+1:2d}/50] {status:20s} | {expected_domain:3s} | conf:{response.get('confidence',0):5.1f} | {q[:50]}")
        
    except Exception as e:
        results.append({
            'id': i + 1,
            'query': q,
            'status': 'ERROR',
            'error': str(e)
        })
        print(f"[{i+1:2d}/50] ERROR                | {str(e)[:50]}")

end_time = time.time()
total_time = end_time - start_time

# Calculate statistics
total = len(results)
success = sum(1 for r in results if r['status'] in ['SUCCESS', 'CORRECT_HALT', 'LOW_CONFIDENCE'])
correct_halts = sum(1 for r in results if r['status'] == 'CORRECT_HALT')
critical_fails = sum(1 for r in results if r['status'] == 'CRITICAL_FAIL_NO_HALT')
errors = sum(1 for r in results if r['status'] == 'ERROR')
too_short = sum(1 for r in results if r['status'] == 'TOO_SHORT')

avg_confidence = sum(r.get('confidence', 0) for r in results if r['status'] != 'ERROR') / max(1, total - errors)

# Domain breakdown
summary = {
    'total_queries': total,
    'successful_answers': success,
    'success_rate_pct': round(success / total * 100, 1),
    'correct_emergency_halts': correct_halts,
    'critical_emergency_fails': critical_fails,
    'errors': errors,
    'too_short_answers': too_short,
    'average_confidence': round(avg_confidence, 2),
    'total_time_seconds': round(total_time, 2),
    'by_domain': {},
    'by_status': {}
}

for domain in ['eco', 'hc', 'gov']:
    domain_results = [r for r in results if r.get('expected_domain') == domain]
    domain_success = sum(1 for r in domain_results if r['status'] in ['SUCCESS', 'CORRECT_HALT', 'LOW_CONFIDENCE'])
    summary['by_domain'][domain] = {
        'total': len(domain_results),
        'success': domain_success,
        'rate_pct': round(domain_success / max(1, len(domain_results)) * 100, 1)
    }

for status in ['SUCCESS', 'CORRECT_HALT', 'LOW_CONFIDENCE', 'CRITICAL_FAIL_NO_HALT', 'TOO_SHORT', 'ERROR']:
    count = sum(1 for r in results if r['status'] == status)
    summary['by_status'][status] = count

# Save results
import os
os.makedirs('/workspace/test_results', exist_ok=True)
with open('/workspace/test_results/final_50_query_test.json', 'w') as f:
    json.dump({'summary': summary, 'detailed_results': results}, f, indent=2)

print('=' * 80)
print('TEST SUITE COMPLETE')
print(f"Total: {total} | Success: {success} ({summary['success_rate_pct']}%)")
print(f"Correct Emergency Halts: {correct_halts} | Critical Fails: {critical_fails}")
print(f"Avg Confidence: {avg_confidence:.2f} | Time: {total_time:.2f}s")
print(f"\nDetailed results saved to: /workspace/test_results/final_50_query_test.json")

# Print key findings
print('\n--- KEY FINDINGS ---')
if critical_fails > 0:
    print(f"⚠️  CRITICAL: {critical_fails} emergency queries did NOT trigger safety halt!")
if summary['by_domain']['hc']['rate_pct'] < 90:
    print(f"⚠️  Healthcare domain success rate below 90%: {summary['by_domain']['hc']['rate_pct']}%")
if avg_confidence < 60:
    print(f"⚠️  Average confidence below 60%: {avg_confidence:.2f}%")
if success == total and critical_fails == 0:
    print("✅ All queries processed successfully with proper emergency handling!")
