#!/usr/bin/env python3
"""
Dual Domain Test Suite - 100 Randomized Queries (50 Economy + 50 Healthcare)
Tests OpenEyes production readiness on Tier 1 domains with user-like random queries.
"""

import json
import random
import time
import sys
import os

# Add workspace to path
sys.path.insert(0, '/workspace')

from openeyes.query_interface import OpenEyes

# Define randomized query templates for Economy and Healthcare
# These mimic how real users would ask questions - varied phrasing, colloquialisms, specificity levels

ECONOMY_QUERIES = [
    'What is the current inflation rate?',
    'How does GDP growth affect unemployment?',
    'Explain supply and demand in simple terms',
    'What caused the 2008 financial crisis?',
    'How do interest rates impact mortgages?',
    'What is quantitative easing?',
    'Difference between fiscal and monetary policy',
    'How does trade deficit affect currency value?',
    'What is a recession and how is it measured?',
    'Explain blockchain economics',
    'Impact of minimum wage on small businesses',
    'How do stock markets work?',
    'What is cryptocurrency mining cost?',
    'Effect of tariffs on consumer prices',
    'How does housing market bubble form?',
    'What is venture capital funding?',
    'Explain marginal utility with examples',
    'How do credit scores affect loan rates?',
    'What is GDP per capita and why matters?',
    'Impact of automation on job market',
    'How does Federal Reserve set rates?',
    'What is sovereign debt crisis?',
    'Explain opportunity cost in daily life',
    'How do commodity prices fluctuate?',
    'What is economic moat in investing?',
    'Effect of population aging on economy',
    'How does gig economy change labor laws?',
    'What is stagflation and can it happen now?',
    'Explain network effects in tech platforms',
    'How do exchange rates affect exports?',
    'What is yield curve inversion signal?',
    'Impact of climate change on insurance costs',
    'How do private equity firms make money?',
    'What is behavioral economics bias?',
    'Explain trickle-down economics theory',
    'How does student debt affect economy?',
    'What is universal basic income pros/cons?',
    'Effect of remote work on commercial real estate',
    'How do central banks fight inflation?',
    'What is shadow banking system?',
    'Explain comparative advantage in trade',
    'How does oil price shock ripple through economy?',
    'What is wealth inequality Gini coefficient?',
    'Impact of AI on productivity growth',
    'How do pension funds invest assets?',
    'What is circular economy model?',
    'Explain Keynesian vs Austrian economics',
    'How does consumer confidence index work?',
    'What is debt-to-GDP ratio threshold?',
    'Effect of immigration on wage levels',
    # More colloquial/user-like variations
    'Why is everything so expensive now?',
    'Should I invest in stocks or bonds?',
    'Is now a good time to buy a house?',
    'What happens if the stock market crashes?',
    'How can I protect my savings from inflation?',
    'Why do gas prices go up and down?',
    'What does the Fed do exactly?',
    'Is cryptocurrency a good investment?',
    'Why are interest rates rising?',
    'What causes a recession?',
]

HEALTHCARE_QUERIES = [
    'What are symptoms of type 2 diabetes?',
    'How does metformin work for diabetes?',
    'Difference between viral and bacterial infection',
    'What is normal blood pressure range?',
    'Explain how vaccines train immune system',
    'Side effects of statin medications',
    'What causes migraine headaches?',
    'How to recognize stroke symptoms FAST?',
    'What is BMI and is it accurate?',
    'Explain difference between allergy and intolerance',
    'How does insulin regulate blood sugar?',
    'What are risk factors for heart disease?',
    'Treatment options for anxiety disorder',
    'How does chemotherapy target cancer cells?',
    'What is herd immunity threshold?',
    'Explain difference between CT scan and MRI',
    'How to lower cholesterol naturally?',
    'What causes acid reflux and how treat?',
    'Signs of vitamin D deficiency',
    'How does sleep affect mental health?',
    'What is autoimmune disease mechanism?',
    'Effect of smoking on lung capacity',
    'How do antibiotics kill bacteria?',
    'What is precancerous polyp removal process?',
    'Explain difference between type 1 and type 2 diabetes',
    'How does physical therapy help recovery?',
    'What are omega-3 fatty acids benefits?',
    'Symptoms of thyroid dysfunction',
    'How does blood clotting cascade work?',
    'What is preventive screening schedule by age?',
    'Effect of stress on digestive system',
    'How do pain relievers like ibuprofen work?',
    'What causes osteoporosis and prevention?',
    'Explain difference between benign and malignant tumors',
    'How does dialysis filter blood?',
    'What are signs of dehydration in elderly?',
    'Impact of gut microbiome on health',
    'How does asthma inhaler deliver medication?',
    'What is post-concussion syndrome?',
    'Effect of alcohol on liver function',
    'How do antidepressants affect brain chemistry?',
    'What is carpal tunnel syndrome treatment?',
    'Explain difference between sprain and strain',
    'How does menopause affect bone density?',
    'What are warning signs of skin cancer?',
    'Effect of high sodium on blood pressure',
    'How does physical exercise improve cognition?',
    'What is chronic kidney disease stages?',
    'Explain difference between acute and chronic pain',
    'How do probiotics support digestive health?',
    # More colloquial/user-like variations
    'My head hurts all the time, what could it be?',
    'Is it normal to feel tired after eating?',
    'How much water should I drink daily?',
    'What vitamins should I take?',
    'Why do I have trouble sleeping?',
    'Is coffee bad for my heart?',
    'How do I know if Im depressed?',
    'What should I do for lower back pain?',
    'Can stress cause stomach problems?',
    'Is it safe to take ibuprofen every day?',
]

def run_test_suite():
    """Run 100 randomized queries across economy and healthcare domains."""
    
    print("=" * 70)
    print("OPENEYES DUAL DOMAIN TEST SUITE")
    print("100 Randomized Queries - 50 Economy + 50 Healthcare")
    print("=" * 70)
    print()
    
    # Initialize OpenEyes instances for each domain
    oe_economy = OpenEyes(domain="economy")
    oe_healthcare = OpenEyes(domain="healthcare")
    
    # Select 50 random queries from each domain
    random.seed(time.time())
    economy_sample = random.sample(ECONOMY_QUERIES, min(50, len(ECONOMY_QUERIES)))
    healthcare_sample = random.sample(HEALTHCARE_QUERIES, min(50, len(HEALTHCARE_QUERIES)))
    
    # Create test queue with domain labels
    test_queue = []
    for q in economy_sample:
        test_queue.append({'query': q, 'domain': 'economy', 'oe': oe_economy})
    for q in healthcare_sample:
        test_queue.append({'query': q, 'domain': 'healthcare', 'oe': oe_healthcare})
    
    # Shuffle to interleave domains
    random.shuffle(test_queue)
    
    results = []
    start_time = time.time()
    
    print(f"Starting test execution at {time.strftime('%H:%M:%S')}...")
    print(f"Total queries: {len(test_queue)}")
    print("-" * 70)
    
    for i, item in enumerate(test_queue):
        query = item['query']
        domain = item['domain']
        oe = item['oe']
        
        try:
            # Execute query
            result = oe.query(query)
            
            response_data = {
                'id': i + 1,
                'query': query,
                'domain': domain,
                'success': result.get('status') != 'HALT',
                'halted': result.get('status') == 'HALT',
                'response_time_ms': result.get('response_time_ms', 0),
                'confidence': result.get('confidence', 0),
                'sources_count': len(result.get('sources', [])),
                'answer_length': len(result.get('answer', '')),
                'status': result.get('status'),
                'error': result.get('error'),
                'tier': result.get('tier_info', {}).get('tier', 'unknown') if result.get('tier_info') else 'unknown',
                'timestamp': time.time()
            }
            
            if result.get('status') == 'HALT':
                response_data['halt_reason'] = result.get('halt_reason', 'Unknown')
            
            results.append(response_data)
            
        except Exception as e:
            results.append({
                'id': i + 1,
                'query': query,
                'domain': domain,
                'success': False,
                'halted': True,
                'response_time_ms': 0,
                'confidence': 0,
                'sources_count': 0,
                'answer_length': 0,
                'status': 'ERROR',
                'error': str(e),
                'tier': 'unknown',
                'timestamp': time.time(),
                'halt_reason': f'Exception: {str(e)}'
            })
        
        # Progress indicator every 10 queries
        if (i + 1) % 10 == 0:
            success_count = sum(1 for r in results if r['success'])
            elapsed = time.time() - start_time
            print(f"[{i+1:3d}/100] Success: {success_count:3d} ({success_count/(i+1)*100:5.1f}%) | Elapsed: {elapsed:6.1f}s")
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    total_queries = len(results)
    successful = sum(1 for r in results if r['success'])
    halted = sum(1 for r in results if r['halted'])
    avg_response_time = sum(r['response_time_ms'] for r in results) / total_queries if total_queries > 0 else 0
    
    # Domain-specific stats
    economy_results = [r for r in results if r['domain'] == 'economy']
    healthcare_results = [r for r in results if r['domain'] == 'healthcare']
    
    economy_success = sum(1 for r in economy_results if r['success'])
    healthcare_success = sum(1 for r in healthcare_results if r['success'])
    
    # Halt reason analysis
    halt_reasons = {}
    for r in results:
        if r['halted'] and 'halt_reason' in r:
            reason = r['halt_reason']
            # Normalize similar reasons
            if 'knowledge' in reason.lower():
                reason = 'Knowledge Retrieval Failure'
            elif 'threshold' in reason.lower() or 'monte carlo' in reason.lower():
                reason = 'Monte Carlo Threshold Failure'
            elif 'philosophy' in reason.lower() or 'guard' in reason.lower():
                reason = 'Philosophy Guard Rejection'
            elif 'relevance' in reason.lower():
                reason = 'Low Relevance Score'
            elif 'domain' in reason.lower():
                reason = 'Out of Domain'
            halt_reasons[reason] = halt_reasons.get(reason, 0) + 1
    
    # Category breakdown by query type
    categories = {
        'factual': ['what is', 'define', 'explain'],
        'comparative': ['difference between', 'vs ', 'compare'],
        'causal': ['how does', 'why does', 'what causes', 'effect of', 'impact of'],
        'procedural': ['how to', 'treatment', 'prevention'],
        'evaluative': ['should i', 'is it', 'good time', 'safe to'],
        'symptom': ['symptoms', 'signs', 'feel', 'pain', 'hurt']
    }
    
    category_results = {cat: {'total': 0, 'success': 0} for cat in categories}
    category_results['other'] = {'total': 0, 'success': 0}
    
    for r in results:
        query_lower = r['query'].lower()
        matched = False
        for cat, keywords in categories.items():
            if any(kw in query_lower for kw in keywords):
                category_results[cat]['total'] += 1
                if r['success']:
                    category_results[cat]['success'] += 1
                matched = True
                break
        if not matched:
            category_results['other']['total'] += 1
            if r['success']:
                category_results['other']['success'] += 1
    
    # Compile output
    output_data = {
        'test_summary': {
            'total_queries': total_queries,
            'successful': successful,
            'halted': halted,
            'success_rate_pct': round(successful / total_queries * 100, 2) if total_queries > 0 else 0,
            'avg_response_time_ms': round(avg_response_time, 2),
            'total_test_time_seconds': round(total_time, 2),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'domain_breakdown': {
            'economy': {
                'total': len(economy_results),
                'successful': economy_success,
                'success_rate_pct': round(economy_success / len(economy_results) * 100, 2) if economy_results else 0
            },
            'healthcare': {
                'total': len(healthcare_results),
                'successful': healthcare_success,
                'success_rate_pct': round(healthcare_success / len(healthcare_results) * 100, 2) if healthcare_results else 0
            }
        },
        'category_breakdown': {
            cat: {
                'total': data['total'],
                'successful': data['success'],
                'success_rate_pct': round(data['success'] / data['total'] * 100, 2) if data['total'] > 0 else 0
            }
            for cat, data in category_results.items()
        },
        'halt_reasons': halt_reasons,
        'detailed_results': results
    }
    
    # Ensure test_results directory exists
    os.makedirs('/workspace/test_results', exist_ok=True)
    
    # Save detailed results
    output_file = '/workspace/test_results/dual_domain_100queries_full.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    print()
    print(f"OVERALL RESULTS:")
    print(f"  Total Queries:     {total_queries}")
    print(f"  Successful:        {successful} ({successful/total_queries*100:.1f}%)")
    print(f"  Halted:            {halted} ({halted/total_queries*100:.1f}%)")
    print(f"  Avg Response Time: {avg_response_time:.2f}ms")
    print(f"  Total Duration:    {total_time:.2f}s")
    print()
    print("DOMAIN BREAKDOWN:")
    print(f"  Economy:    {economy_success}/{len(economy_results)} ({economy_success/len(economy_results)*100:.1f}% success)")
    print(f"  Healthcare: {healthcare_success}/{len(healthcare_results)} ({healthcare_success/len(healthcare_results)*100:.1f}% success)")
    print()
    print("CATEGORY PERFORMANCE:")
    for cat, data in sorted(category_results.items(), key=lambda x: -x[1]['total']):
        if data['total'] > 0:
            rate = data['success'] / data['total'] * 100
            print(f"  {cat:15s}: {data['success']:2d}/{data['total']:2d} ({rate:5.1f}%)")
    print()
    if halt_reasons:
        print("HALT REASONS:")
        for reason, count in sorted(halt_reasons.items(), key=lambda x: -x[1]):
            pct = count / halted * 100
            print(f"  {reason:35s}: {count:3d} ({pct:5.1f}%)")
    print()
    print(f"Full results saved to: {output_file}")
    print()
    
    return output_data


if __name__ == '__main__':
    run_test_suite()
