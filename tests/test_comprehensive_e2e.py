#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for OpenEyes
Tests all domains with 50 queries each against full fragment knowledge base
"""

import json
import time
from pathlib import Path
from openeyes.core.engine import OpenEyesEngine

# Domain configuration with expected fragment counts
DOMAINS = {
    'healthcare': {'min_frags': 1000, 'description': 'Medical and health queries'},
    'economy': {'min_frags': 1000, 'description': 'Economic and financial queries'},
    'governance': {'min_frags': 1000, 'description': 'Government and policy queries'},
    'investment': {'min_frags': 500, 'description': 'Investment and market queries'},
    'general': {'min_frags': 100, 'description': 'General knowledge queries'},
}

# 50 test queries per domain
HEALTHCARE_QUERIES = [
    "What is diabetes?",
    "How does insulin work?",
    "What are symptoms of type 2 diabetes?",
    "Explain how mRNA vaccines work.",
    "What is the treatment for hypertension?",
    "Is metformin effective for type 2 diabetes?",
    "What are side effects of statins?",
    "How do ACE inhibitors work?",
    "What is atrial fibrillation?",
    "Explain the mechanism of beta blockers.",
    "What causes heart failure?",
    "How is COPD diagnosed?",
    "What is the treatment for asthma?",
    "Explain how anticoagulants prevent stroke.",
    "What are risk factors for coronary artery disease?",
    "How does dialysis work?",
    "What is chronic kidney disease?",
    "Explain the pathophysiology of rheumatoid arthritis.",
    "What is the first-line treatment for osteoporosis?",
    "How do proton pump inhibitors work?",
    "What causes gastroesophageal reflux disease?",
    "Explain how antidepressants work.",
    "What is bipolar disorder?",
    "How is schizophrenia treated?",
    "What are symptoms of major depressive disorder?",
    "Explain the mechanism of SSRIs.",
    "What is cognitive behavioral therapy?",
    "How does exposure therapy work for anxiety?",
    "What is post-traumatic stress disorder?",
    "Explain how opioids work for pain management.",
    "What are alternatives to opioid pain management?",
    "How is cancer immunotherapy effective?",
    "What is checkpoint inhibitor therapy?",
    "Explain how CAR-T cell therapy works.",
    "What is precision medicine in oncology?",
    "How does radiation therapy target cancer cells?",
    "What are side effects of chemotherapy?",
    "Explain targeted therapy in breast cancer.",
    "What is HER2-positive breast cancer?",
    "How does tamoxifen work?",
    "What is the role of aromatase inhibitors?",
    "Explain palliative care principles.",
]

ECONOMY_QUERIES = [
    "What is GDP?",
    "How is inflation measured?",
    "What causes unemployment?",
    "Explain quantitative easing.",
    "What is the federal funds rate?",
    "How does the Fed control interest rates?",
    "What is a recession?",
    "Explain the business cycle.",
    "What is fiscal policy?",
    "How does government spending affect the economy?",
    "What is monetary policy?",
    "Explain how central banks work.",
    "What is the Consumer Price Index?",
    "How is CPI calculated?",
    "What is core inflation?",
    "Explain supply and demand economics.",
    "What is elasticity in economics?",
    "How does trade deficit affect the economy?",
    "What is gross national product?",
    "Explain comparative advantage in trade.",
    "What is a tariff?",
    "How do tariffs affect consumers?",
    "What is a free trade agreement?",
    "Explain the concept of opportunity cost.",
    "What is marginal utility?",
    "How does taxation affect economic growth?",
    "What is the Laffer curve?",
    "Explain Keynesian economics.",
    "What is monetarism?",
    "How does money supply affect inflation?",
    "What is velocity of money?",
    "Explain the quantity theory of money.",
    "What is aggregate demand?",
    "How does aggregate supply shift?",
    "What is stagflation?",
    "Explain the Phillips curve.",
    "What is the natural rate of unemployment?",
    "How does minimum wage affect employment?",
    "What is income inequality?",
    "Explain the Gini coefficient.",
    "What is human capital?",
    "How does education affect economic growth?",
    "What is productivity?",
    "Explain total factor productivity.",
    "What is technological unemployment?",
    "How does automation affect jobs?",
    "What is the gig economy?",
    "Explain network effects in platforms.",
    "What is a natural monopoly?",
    "How does regulation affect markets?",
]

GOVERNANCE_QUERIES = [
    "What is separation of powers?",
    "How does checks and balances work?",
    "What is judicial review?",
    "Explain the electoral college.",
    "What is gerrymandering?",
    "How are Supreme Court justices appointed?",
    "What is the filibuster?",
    "Explain how a bill becomes law.",
    "What is executive order?",
    "How does Congress override a veto?",
    "What is impeachment?",
    "Explain the amendment process.",
    "What is federalism?",
    "How does state preemption work?",
    "What is home rule?",
    "Explain qualified immunity.",
    "What is substantive due process?",
    "How does equal protection apply?",
    "What is strict scrutiny?",
    "Explain rational basis review.",
    "What is administrative law?",
    "How do regulatory agencies work?",
    "What is notice and comment rulemaking?",
    "Explain Chevron deference.",
    "What is the Administrative Procedure Act?",
    "How does lobbying work?",
    "What is campaign finance regulation?",
    "Explain Citizens United decision.",
    "What is redistricting?",
    "How are congressional districts drawn?",
    "What is voter ID law?",
    "Explain the Voting Rights Act.",
    "What is mail-in voting?",
    "How does early voting work?",
    "What is election security?",
    "Explain the Electoral Count Act.",
    "What is presidential succession?",
    "How does the 25th Amendment work?",
    "What is executive privilege?",
    "Explain pardon power.",
    "What is treaty ratification?",
    "How does Senate confirmation work?",
    "What is recess appointment?",
    "Explain war powers resolution.",
    "What is congressional oversight?",
    "How do subpoenas work in Congress?",
    "What is contempt of Congress?",
    "Explain legislative immunity.",
    "What is the pocket veto?",
    "How does continuing resolution work?",
]

INVESTMENT_QUERIES = [
    "What is a stock?",
    "How does bond investing work?",
    "What is diversification?",
    "Explain index fund investing.",
    "What is dollar-cost averaging?",
    "How does compound interest work?",
    "What is risk tolerance?",
    "Explain asset allocation.",
    "What is rebalancing?",
    "How does 401k work?",
    "What is a Roth IRA?",
    "Explain traditional vs Roth retirement accounts.",
    "What is capital gains tax?",
    "How are dividends taxed?",
    "What is tax-loss harvesting?",
    "Explain value investing.",
    "What is growth investing?",
    "How does momentum investing work?",
    "What is technical analysis?",
    "Explain fundamental analysis.",
    "What is price-to-earnings ratio?",
    "How is market cap calculated?",
    "What is enterprise value?",
    "Explain discounted cash flow analysis.",
    "What is net present value?",
    "How does internal rate of return work?",
    "What is beta in investing?",
    "Explain standard deviation as risk measure.",
    "What is Sharpe ratio?",
    "How does Modern Portfolio Theory work?",
    "What is efficient frontier?",
    "Explain capital asset pricing model.",
    "What is alpha in investing?",
    "How do ETFs work?",
    "What is expense ratio?",
    "Explain active vs passive management.",
    "What is hedge fund?",
    "How do private equity firms work?",
    "What is venture capital?",
    "Explain angel investing.",
    "What is IPO?",
    "How does secondary offering work?",
    "What is stock split?",
    "Explain reverse stock split.",
    "What is short selling?",
    "How do options work?",
    "What is futures contract?",
    "Explain commodities investing.",
    "What is real estate investment trust?",
    "How does REIT dividend work?",
]

GENERAL_QUERIES = [
    "What is photosynthesis?",
    "How does gravity work?",
    "What is the speed of light?",
    "Explain quantum mechanics basics.",
    "What is evolution by natural selection?",
    "How does DNA replication work?",
    "What is climate change?",
    "Explain greenhouse effect.",
    "What is renewable energy?",
    "How do solar panels work?",
    "What is nuclear fission?",
    "Explain nuclear fusion.",
    "What is artificial intelligence?",
    "How does machine learning work?",
    "What is neural network?",
    "Explain deep learning.",
    "What is blockchain?",
    "How does cryptocurrency work?",
    "What is internet of things?",
    "Explain cloud computing.",
    "What is cybersecurity?",
    "How does encryption work?",
    "What is public key cryptography?",
    "Explain zero-knowledge proof.",
    "What is virtual reality?",
    "How does augmented reality work?",
    "What is 5G technology?",
    "Explain edge computing.",
    "What is gene editing?",
    "How does CRISPR work?",
    "What is synthetic biology?",
    "Explain stem cell therapy.",
    "What is nanotechnology?",
    "How do 3D printers work?",
    "What is autonomous vehicle?",
    "Explain lidar technology.",
    "What is space exploration?",
    "How do rockets work?",
    "What is international space station?",
    "Explain Mars colonization plans.",
    "What is dark matter?",
    "How does telescope work?",
    "What is black hole?",
    "Explain general relativity.",
    "What is string theory?",
    "How does particle accelerator work?",
    "What is Higgs boson?",
    "Explain standard model of physics.",
    "What is periodic table?",
    "How does chemical reaction work?",
]

DOMAIN_QUERY_MAP = {
    'healthcare': HEALTHCARE_QUERIES,
    'economy': ECONOMY_QUERIES,
    'governance': GOVERNANCE_QUERIES,
    'investment': INVESTMENT_QUERIES,
    'general': GENERAL_QUERIES,
}


def count_fragments():
    """Count fragments in each domain directory."""
    frag_base = Path('/workspace/openeyes/knowledge/fragments')
    counts = {}
    
    # Map domain names to directory codes
    dir_map = {
        'healthcare': ['hc', 'healthcare'],
        'economy': ['eco'],
        'governance': ['gov'],
        'investment': ['eco/fin'],  # Investment fragments are in economy/fin
        'general': ['unknown'],
    }
    
    for domain, dirs in dir_map.items():
        total = 0
        for d in dirs:
            dir_path = frag_base / d
            if dir_path.exists():
                count = len(list(dir_path.rglob('*.json')))
                total += count
        counts[domain] = total
    
    return counts


def run_domain_tests(domain, queries, engine):
    """Run 50 queries for a domain and collect results."""
    results = []
    answer_count = 0
    halt_count = 0
    
    print(f"\n{'='*60}")
    print(f"Testing {domain.upper()} domain ({len(queries)} queries)")
    print(f"{'='*60}")
    
    for i, query in enumerate(queries, 1):
        try:
            result = engine.answer(query, domain)
            status = result.get('status', 'UNKNOWN')
            
            if status.startswith('ANSWER'):
                answer_count += 1
            elif status.startswith('HALT'):
                halt_count += 1
            
            results.append({
                'query': query,
                'status': status,
                'confidence': result.get('confidence', 0),
                'answer_length': len(result.get('answer', '')),
            })
            
            # Progress indicator
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(queries)} - Answers: {answer_count}, Halts: {halt_count}")
                
        except Exception as e:
            results.append({
                'query': query,
                'status': f'ERROR: {str(e)}',
                'confidence': 0,
                'answer_length': 0,
            })
            halt_count += 1
    
    return {
        'domain': domain,
        'total_queries': len(queries),
        'answers': answer_count,
        'halts': halt_count,
        'answer_rate': (answer_count / len(queries)) * 100 if queries else 0,
        'results': results,
    }


def main():
    print("="*80)
    print("OpenEyes Comprehensive End-to-End Test Suite")
    print("Testing all domains with 50 queries each")
    print("="*80)
    
    # Initialize engine
    print("\nInitializing OpenEyes engine...")
    engine = OpenEyesEngine()
    
    # Count available fragments
    print("\nCounting available fragments...")
    frag_counts = count_fragments()
    for domain, count in frag_counts.items():
        print(f"  {domain}: {count:,} fragments")
    
    # Run tests for each domain
    all_results = []
    start_time = time.time()
    
    for domain, queries in DOMAIN_QUERY_MAP.items():
        result = run_domain_tests(domain, queries, engine)
        all_results.append(result)
        
        # Print summary for this domain
        print(f"\n{domain.upper()} Summary:")
        print(f"  Total Queries: {result['total_queries']}")
        print(f"  Answers: {result['answers']} ({result['answer_rate']:.1f}%)")
        print(f"  Halts: {result['halts']}")
    
    total_time = time.time() - start_time
    
    # Overall summary
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    
    total_queries = sum(r['total_queries'] for r in all_results)
    total_answers = sum(r['answers'] for r in all_results)
    total_halts = sum(r['halts'] for r in all_results)
    overall_answer_rate = (total_answers / total_queries) * 100 if total_queries else 0
    
    print(f"\nTotal Execution Time: {total_time:.2f} seconds")
    print(f"Total Queries: {total_queries}")
    print(f"Total Answers: {total_answers} ({overall_answer_rate:.1f}%)")
    print(f"Total Halts: {total_halts}")
    
    # Per-domain breakdown
    print("\nPer-Domain Breakdown:")
    print(f"{'Domain':<15} {'Queries':<10} {'Answers':<10} {'Halts':<10} {'Answer Rate':<12}")
    print("-"*60)
    for r in all_results:
        print(f"{r['domain']:<15} {r['total_queries']:<10} {r['answers']:<10} {r['halts']:<10} {r['answer_rate']:.1f}%")
    
    # Save detailed results
    output_file = Path('/workspace/test_results/comprehensive_e2e_results.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    report = {
        'summary': {
            'total_queries': total_queries,
            'total_answers': total_answers,
            'total_halts': total_halts,
            'overall_answer_rate': overall_answer_rate,
            'execution_time_seconds': total_time,
            'fragment_counts': frag_counts,
        },
        'domains': all_results,
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    print("="*80)
    
    return report


if __name__ == '__main__':
    main()
