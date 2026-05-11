#!/usr/bin/env python3
"""End-to-End Test Suite for KAP + EKD Pipeline"""

import json
import random
from pathlib import Path
from openeyes.query_interface import OpenEyes
from openeyes.core.ekd import EKDStore

def main():
    # Load Economy fragments to generate realistic queries
    fragments_path = Path('openeyes/fragment_library/fragments')
    economy_frags = []
    for f in fragments_path.glob('*.json'):
        try:
            data = json.loads(f.read_text())
            if data.get('domain') == 'economy':
                economy_frags.append(data)
        except:
            pass

    print(f'Loaded {len(economy_frags)} Economy fragments for test generation.')

    # Generate 50 randomized queries based on fragment tags and content
    test_queries = []
    random.seed(42) # Reproducibility

    query_templates = [
        'What is {topic}?',
        'How does {topic} work?',
        'Explain the mechanism of {topic}.',
        'What are the risks associated with {topic}?',
        'What is the current state of {topic}?',
        'Define {topic} and its importance.',
        'How does {topic} affect the market?',
        'What is the relationship between {topic} and inflation?',
        'Explain the role of {topic} in the economy.',
        'What are the latest developments in {topic}?'
    ]

    topics = list(set([tag for f in economy_frags for tag in f.get('tags', [])]))
    if len(topics) > 50:
        topics = random.sample(topics, 50)
    
    if not topics:
        topics = ['inflation', 'interest rates', 'GDP', 'unemployment']

    for i in range(50):
        template = random.choice(query_templates)
        topic = random.choice(topics)
        query = template.format(topic=topic)
        test_queries.append(query)

    # Run the test suite
    results = []
    ekd_store = EKDStore() # Initialize fresh to track new crystallizations during this run
    initial_cluster_count = len(ekd_store.clusters)

    success_count = 0
    halt_count = 0
    total_confidence = 0
    clusters_created = 0

    print(f'\nStarting 50-query randomized test suite on Economy domain...')
    print(f'Initial EKD clusters: {initial_cluster_count}\n')

    for i, query in enumerate(test_queries):
        try:
            oe = OpenEyes(domain='economy')
            result = oe.query(query)
            
            is_halt = result.get('halt', False)
            confidence = result.get('confidence', 0)
            frags_used = len(result.get('fragments_used', []))
            
            if not is_halt:
                success_count += 1
                total_confidence += confidence
            else:
                halt_count += 1
                
            results.append({
                'id': i,
                'query': query[:50],
                'status': 'HALT' if is_halt else 'ANSWER',
                'confidence': confidence,
                'fragments': frags_used
            })
            
            if (i + 1) % 10 == 0:
                print(f'Processed {i+1}/50 queries...')
                
        except Exception as e:
            print(f'Error on query {i}: {e}')
            halt_count += 1

    # Final Stats
    final_cluster_count = len(ekd_store.clusters)
    avg_confidence = (total_confidence / success_count) if success_count > 0 else 0

    print('\n' + '='*60)
    print('END-TO-END TEST SUITE RESULTS (50 Randomized Queries)')
    print('='*60)
    print(f'Total Queries: 50')
    print(f'Successful Answers: {success_count} ({success_count*2}%)')
    print(f'Halts: {halt_count} ({halt_count*2}%)')
    print(f'Average Confidence (successful): {avg_confidence:.1f}%')
    print(f'EKD Clusters Created During Run: {final_cluster_count - initial_cluster_count}')
    print(f'Total EKD Clusters Now: {final_cluster_count}')
    print('='*60)

    # Show sample of first 5 results
    print('\nSample Results (First 5):')
    for r in results[:5]:
        status = r['status']
        conf = r['confidence']
        frags = r['fragments']
        q = r['query']
        print(f"  [{status}] Conf: {conf:.1f}% | Frags: {frags} | Query: {q}...")

    # Show EKD Report if clusters exist
    if final_cluster_count > 0:
        print('\n--- EKD Store Status ---')
        from openeyes.tools.ekd_report import generate_ekd_report
        generate_ekd_report()
    else:
        print('\nNo EKD clusters created (likely due to confidence < 75% threshold in randomized tests).')
        
    # Show detailed pipeline trace for one successful query
    if success_count > 0:
        print('\n--- Detailed Pipeline Trace for One Query ---')
        oe = OpenEyes(domain='economy')
        test_q = "What is quantitative easing?"
        result = oe.query(test_q)
        print(f"Query: {test_q}")
        print(f"Status: {'HALT' if result.get('halt') else 'ANSWER'}")
        print(f"Confidence: {result.get('confidence', 0):.1f}%")
        print(f"Fragments Used: {len(result.get('fragments_used', []))}")
        if result.get('answer'):
            print(f"Answer Preview: {result['answer'][:200]}...")

if __name__ == '__main__':
    main()
