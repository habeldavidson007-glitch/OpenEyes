"""
Comprehensive End-to-End Test Suite: 50 Queries per Domain
Tests OpenEyes across all available domains with 1000+ fragments
"""
import pytest
import time
from openeyes.core.engine import OpenEyesEngine


class TestComprehensiveDomains:
    """Test OpenEyes with 50 queries per domain"""
    
    @pytest.fixture(autouse=True)
    def setup_engine(self):
        """Initialize fresh engine for each test class"""
        self.engine = OpenEyesEngine()
        self.results = []
        
    def get_domain_fragments_count(self, domain):
        """Get fragment count for a domain"""
        try:
            from openeyes.knowledge.fragments import FragmentLibrary
            lib = FragmentLibrary()
            frags = lib.get_fragments_by_domain(domain)
            return len(frags) if frags else 0
        except:
            return 0
    
    # ==================== MEDICAL DOMAIN (50 queries) ====================
    
    def test_medical_domain_50_queries(self):
        """Test 50 medical queries - high stakes domain"""
        medical_queries = [
            "What are the symptoms of pancreatic cancer?",
            "How is diabetes diagnosed?",
            "What is the treatment for hypertension?",
            "Explain the stages of chronic kidney disease",
            "What causes myocardial infarction?",
            "How to recognize stroke symptoms?",
            "What is the prognosis for leukemia?",
            "Explain autoimmune disorders mechanism",
            "What are risk factors for Alzheimer's?",
            "How does chemotherapy work?",
            "What is atrial fibrillation treatment?",
            "Explain COPD pathophysiology",
            "What are symptoms of multiple sclerosis?",
            "How is rheumatoid arthritis managed?",
            "What causes inflammatory bowel disease?",
            "Explain the renin-angiotensin system",
            "What is the difference between Type 1 and Type 2 diabetes?",
            "How does insulin resistance develop?",
            "What are complications of untreated hypertension?",
            "Explain the coagulation cascade",
            "What is the treatment for deep vein thrombosis?",
            "How to manage acute asthma attack?",
            "What causes gastroesophageal reflux disease?",
            "Explain the pathophysiology of cirrhosis",
            "What are signs of liver failure?",
            "How does kidney dialysis work?",
            "What is the mechanism of action of statins?",
            "Explain beta-blocker pharmacology",
            "What are side effects of corticosteroids?",
            "How to treat bacterial pneumonia?",
            "What is the difference between viral and bacterial meningitis?",
            "Explain the immune response to vaccination",
            "What causes osteoporosis?",
            "How is thyroid dysfunction diagnosed?",
            "What are symptoms of hyperthyroidism?",
            "Explain the hypothalamic-pituitary axis",
            "What is the treatment for epilepsy?",
            "How does Parkinson's disease progress?",
            "What causes depression neurochemically?",
            "Explain the mechanism of SSRIs",
            "What are risk factors for breast cancer?",
            "How is prostate cancer screened?",
            "What is the TNM staging system?",
            "Explain tumor marker testing",
            "What causes anemia?",
            "How to interpret complete blood count?",
            "What is disseminated intravascular coagulation?",
            "Explain septic shock pathophysiology",
            "What is the treatment for anaphylaxis?",
            "How does mechanical ventilation work?",
            "What are indications for ICU admission?"
        ]
        
        answers = 0
        halts = 0
        total_chars = 0
        
        for query in medical_queries:
            result = self.engine.answer(query, domain="medical")
            if result.get("decision_class", "").startswith("ANSWER"):
                answers += 1
                total_chars += len(result.get("answer", ""))
            elif result.get("decision_class", "").startswith("HALT"):
                halts += 1
                
        print(f"\n=== MEDICAL DOMAIN RESULTS ===")
        print(f"Queries: {len(medical_queries)}")
        print(f"Fragments available: {self.get_domain_fragments_count('medical')}")
        print(f"Answers: {answers} ({answers/len(medical_queries)*100:.1f}%)")
        print(f"Halts: {halts} ({halts/len(medical_queries)*100:.1f}%)")
        print(f"Average answer length: {total_chars/max(answers,1):.0f} chars")
        
        assert answers > 0, "Should get at least some answers in medical domain"
        self.results.append({
            "domain": "medical",
            "queries": len(medical_queries),
            "answers": answers,
            "halts": halts,
            "answer_rate": answers/len(medical_queries)
        })

    # ==================== INVESTMENT DOMAIN (50 queries) ====================
    
    def test_investment_domain_50_queries(self):
        """Test 50 investment/finance queries"""
        investment_queries = [
            "What is the current Federal Reserve interest rate?",
            "Explain quantitative easing policy",
            "How does inflation affect bond prices?",
            "What is the yield curve telling us?",
            "Analyze the S&P 500 valuation metrics",
            "What are REITs and how do they work?",
            "Explain the capital asset pricing model",
            "What is the difference between growth and value stocks?",
            "How to calculate discounted cash flow?",
            "What drives cryptocurrency prices?",
            "Explain options trading strategies",
            "What is portfolio diversification?",
            "How does dollar-cost averaging work?",
            "What are ESG investment criteria?",
            "Explain the efficient market hypothesis",
            "What causes market volatility?",
            "How to hedge against inflation?",
            "What is the role of the SEC?",
            "Explain margin trading risks",
            "What are derivatives used for?",
            "How does forex trading work?",
            "What is the impact of GDP on markets?",
            "Explain the business cycle phases",
            "What are leading economic indicators?",
            "How does unemployment affect stocks?",
            "What is the consumer price index?",
            "Explain the producer price index",
            "What drives oil prices?",
            "How does gold perform as a hedge?",
            "What are commodity futures?",
            "Explain the carry trade strategy",
            "What is the debt-to-equity ratio?",
            "How to analyze a balance sheet?",
            "What is free cash flow?",
            "Explain enterprise value calculation",
            "What are the risks of emerging markets?",
            "How does currency exchange affect multinationals?",
            "What is the VIX index?",
            "Explain mean reversion strategy",
            "What are momentum investing principles?",
            "How to use technical analysis?",
            "What is the random walk theory?",
            "Explain behavioral finance biases",
            "What causes bubbles and crashes?",
            "How does algorithmic trading work?",
            "What are dark pools?",
            "Explain high-frequency trading",
            "What is the impact of tariffs on trade?",
            "How does fiscal policy affect markets?",
            "What is modern portfolio theory?"
        ]
        
        answers = 0
        halts = 0
        total_chars = 0
        
        for query in investment_queries:
            result = self.engine.answer(query, domain="investment")
            if result.get("decision_class", "").startswith("ANSWER"):
                answers += 1
                total_chars += len(result.get("answer", ""))
            elif result.get("decision_class", "").startswith("HALT"):
                halts += 1
                
        print(f"\n=== INVESTMENT DOMAIN RESULTS ===")
        print(f"Queries: {len(investment_queries)}")
        print(f"Fragments available: {self.get_domain_fragments_count('investment')}")
        print(f"Answers: {answers} ({answers/len(investment_queries)*100:.1f}%)")
        print(f"Halts: {halts} ({halts/len(investment_queries)*100:.1f}%)")
        print(f"Average answer length: {total_chars/max(answers,1):.0f} chars")
        
        assert answers > 0, "Should get at least some answers in investment domain"
        self.results.append({
            "domain": "investment",
            "queries": len(investment_queries),
            "answers": answers,
            "halts": halts,
            "answer_rate": answers/len(investment_queries)
        })

    # ==================== HEALTHCARE DOMAIN (50 queries) ====================
    
    def test_healthcare_domain_50_queries(self):
        """Test 50 healthcare system/policy queries"""
        healthcare_queries = [
            "What is the Affordable Care Act?",
            "Explain Medicare Part D coverage",
            "How does Medicaid eligibility work?",
            "What is universal healthcare?",
            "Compare single-payer vs multi-payer systems",
            "What are health savings accounts?",
            "Explain the insurance marketplace",
            "What is prior authorization?",
            "How does value-based care work?",
            "What are accountable care organizations?",
            "Explain bundled payment models",
            "What is the role of CMS?",
            "How does HIPAA protect patient data?",
            "What are quality metrics in healthcare?",
            "Explain readmission penalties",
            "What is telemedicine reimbursement?",
            "How do pharmacy benefit managers work?",
            "What is formulary management?",
            "Explain step therapy requirements",
            "What are specialty drugs?",
            "How does clinical trial approval work?",
            "What is FDA fast track designation?",
            "Explain orphan drug incentives",
            "What are real-world evidence studies?",
            "How does comparative effectiveness research work?",
            "What is population health management?",
            "Explain social determinants of health",
            "What are health information exchanges?",
            "How does EHR interoperability work?",
            "What is meaningful use?",
            "Explain MACRA legislation",
            "What are MIPS reporting requirements?",
            "How does risk adjustment work?",
            "What is capitation payment?",
            "Explain fee-for-service drawbacks",
            "What are hospital readmission rates?",
            "How is patient satisfaction measured?",
            "What is the HCAHPS survey?",
            "Explain never events in healthcare",
            "What is surgical site infection prevention?",
            "How does sepsis protocol work?",
            "What is rapid response team?",
            "Explain code blue procedures",
            "What is palliative care?",
            "How does hospice eligibility work?",
            "What is advance directive?",
            "Explain informed consent requirements",
            "What is medical malpractice?",
            "How does peer review work?",
            "What is credentialing for physicians?"
        ]
        
        answers = 0
        halts = 0
        total_chars = 0
        
        for query in healthcare_queries:
            result = self.engine.answer(query, domain="healthcare")
            if result.get("decision_class", "").startswith("ANSWER"):
                answers += 1
                total_chars += len(result.get("answer", ""))
            elif result.get("decision_class", "").startswith("HALT"):
                halts += 1
                
        print(f"\n=== HEALTHCARE DOMAIN RESULTS ===")
        print(f"Queries: {len(healthcare_queries)}")
        print(f"Fragments available: {self.get_domain_fragments_count('healthcare')}")
        print(f"Answers: {answers} ({answers/len(healthcare_queries)*100:.1f}%)")
        print(f"Halts: {halts} ({halts/len(healthcare_queries)*100:.1f}%)")
        print(f"Average answer length: {total_chars/max(answers,1):.0f} chars")
        
        assert answers > 0, "Should get at least some answers in healthcare domain"
        self.results.append({
            "domain": "healthcare",
            "queries": len(healthcare_queries),
            "answers": answers,
            "halts": halts,
            "answer_rate": answers/len(healthcare_queries)
        })

    # ==================== ECONOMY DOMAIN (50 queries) ====================
    
    def test_economy_domain_50_queries(self):
        """Test 50 economy/macroeconomics queries"""
        economy_queries = [
            "What is Gross Domestic Product?",
            "Explain the business cycle",
            "How does monetary policy work?",
            "What is the federal funds rate?",
            "Explain open market operations",
            "What is quantitative tightening?",
            "How does fiscal stimulus work?",
            "What is the multiplier effect?",
            "Explain supply-side economics",
            "What is Keynesian economics?",
            "How does trickle-down theory work?",
            "What is modern monetary theory?",
            "Explain austerity measures",
            "What causes hyperinflation?",
            "How does deflation affect economy?",
            "What is stagflation?",
            "Explain the Phillips curve",
            "What is the Laffer curve?",
            "How does trade deficit impact economy?",
            "What is balance of payments?",
            "Explain current account vs capital account",
            "What are foreign exchange reserves?",
            "How does currency devaluation work?",
            "What is purchasing power parity?",
            "Explain the impossible trinity",
            "What causes sovereign debt crisis?",
            "How does credit rating affect borrowing?",
            "What is debt-to-GDP ratio?",
            "Explain structural vs cyclical deficit",
            "What is automatic stabilizer?",
            "How does progressive taxation work?",
            "What is regressive tax?",
            "Explain corporate tax incidence",
            "What is capital gains tax?",
            "How does estate tax work?",
            "What is wealth inequality?",
            "Explain the Gini coefficient",
            "What is social mobility?",
            "How does minimum wage affect employment?",
            "What is labor force participation?",
            "Explain natural rate of unemployment",
            "What is frictional unemployment?",
            "How does automation affect jobs?",
            "What is gig economy?",
            "Explain universal basic income",
            "What is productivity growth?",
            "How does innovation drive economy?",
            "What is creative destruction?",
            "Explain network effects",
            "What is platform economy?"
        ]
        
        answers = 0
        halts = 0
        total_chars = 0
        
        for query in economy_queries:
            result = self.engine.answer(query, domain="economy")
            if result.get("decision_class", "").startswith("ANSWER"):
                answers += 1
                total_chars += len(result.get("answer", ""))
            elif result.get("decision_class", "").startswith("HALT"):
                halts += 1
                
        print(f"\n=== ECONOMY DOMAIN RESULTS ===")
        print(f"Queries: {len(economy_queries)}")
        print(f"Fragments available: {self.get_domain_fragments_count('economy')}")
        print(f"Answers: {answers} ({answers/len(economy_queries)*100:.1f}%)")
        print(f"Halts: {halts} ({halts/len(economy_queries)*100:.1f}%)")
        print(f"Average answer length: {total_chars/max(answers,1):.0f} chars")
        
        assert answers > 0, "Should get at least some answers in economy domain"
        self.results.append({
            "domain": "economy",
            "queries": len(economy_queries),
            "answers": answers,
            "halts": halts,
            "answer_rate": answers/len(economy_queries)
        })

    # ==================== GENERAL KNOWLEDGE (50 queries) ====================
    
    def test_general_knowledge_50_queries(self):
        """Test 50 general knowledge queries"""
        general_queries = [
            "Who was the first president of the United States?",
            "What is the capital of France?",
            "Explain the theory of relativity",
            "How does photosynthesis work?",
            "What caused World War II?",
            "Who wrote Romeo and Juliet?",
            "What is the largest planet in our solar system?",
            "Explain the water cycle",
            "What is DNA?",
            "How do vaccines work?",
            "What is climate change?",
            "Explain plate tectonics",
            "What is the Big Bang theory?",
            "Who discovered penicillin?",
            "What is the speed of light?",
            "Explain gravity",
            "What is black hole?",
            "How does electricity work?",
            "What is quantum mechanics?",
            "Explain evolution by natural selection",
            "What is the periodic table?",
            "How does the internet work?",
            "What is artificial intelligence?",
            "Explain blockchain technology",
            "What is machine learning?",
            "How do computers process data?",
            "What is cloud computing?",
            "Explain cybersecurity basics",
            "What is renewable energy?",
            "How do solar panels work?",
            "What is nuclear fusion?",
            "Explain genetic engineering",
            "What is CRISPR?",
            "How does the human brain work?",
            "What is consciousness?",
            "Explain memory formation",
            "What is the scientific method?",
            "How do peer reviews work?",
            "What is academic publishing?",
            "Explain open access movement",
            "What is intellectual property?",
            "How do patents work?",
            "What is copyright law?",
            "Explain fair use doctrine",
            "What is the United Nations?",
            "How does NATO work?",
            "What is the European Union?",
            "Explain the Geneva Conventions",
            "What is international law?",
            "How does the IMF work?"
        ]
        
        answers = 0
        halts = 0
        total_chars = 0
        
        for query in general_queries:
            result = self.engine.answer(query, domain="general")
            if result.get("decision_class", "").startswith("ANSWER"):
                answers += 1
                total_chars += len(result.get("answer", ""))
            elif result.get("decision_class", "").startswith("HALT"):
                halts += 1
                
        print(f"\n=== GENERAL KNOWLEDGE RESULTS ===")
        print(f"Queries: {len(general_queries)}")
        print(f"Fragments available: {self.get_domain_fragments_count('general')}")
        print(f"Answers: {answers} ({answers/len(general_queries)*100:.1f}%)")
        print(f"Halts: {halts} ({halts/len(general_queries)*100:.1f}%)")
        print(f"Average answer length: {total_chars/max(answers,1):.0f} chars")
        
        assert answers > 0, "Should get at least some answers in general domain"
        self.results.append({
            "domain": "general",
            "queries": len(general_queries),
            "answers": answers,
            "halts": halts,
            "answer_rate": answers/len(general_queries)
        })

    # ==================== COMPREHENSIVE SUMMARY ====================
    
    def test_comprehensive_summary_report(self):
        """Generate comprehensive summary report"""
        # Run all tests first to populate results
        if not hasattr(self, 'results') or len(self.results) == 0:
            pytest.skip("Run domain tests first")
            
        total_queries = sum(r['queries'] for r in self.results)
        total_answers = sum(r['answers'] for r in self.results)
        total_halts = sum(r['halts'] for r in self.results)
        overall_answer_rate = total_answers / total_queries * 100
        
        print("\n" + "="*70)
        print("COMPREHENSIVE END-TO-END TEST SUMMARY")
        print("="*70)
        print(f"Total Domains Tested: {len(self.results)}")
        print(f"Total Queries: {total_queries}")
        print(f"Total Answers: {total_answers}")
        print(f"Total Halts: {total_halts}")
        print(f"Overall Answer Rate: {overall_answer_rate:.1f}%")
        print("-"*70)
        print(f"{'Domain':<15} {'Queries':<10} {'Answers':<10} {'Halts':<10} {'Rate':<10}")
        print("-"*70)
        for r in self.results:
            print(f"{r['domain'].capitalize():<15} {r['queries']:<10} {r['answers']:<10} {r['halts']:<10} {r['answer_rate']*100:.1f}%")
        print("="*70)
        
        assert overall_answer_rate > 0, "Should have non-zero answer rate across all domains"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
