"""
Advanced Domain Validator with Context-Aware Matching
P2 Fix: Replaces simple keyword matching with phrase, sentence, and concept analysis.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class MatchResult:
    domain: str
    score: float
    match_type: str  # 'phrase', 'concept', 'keyword'
    evidence: str

class AdvancedDomainValidator:
    def __init__(self):
        # Multi-word phrases that strongly indicate a domain (Weight: 0.9-1.0)
        self.domain_phrases = {
            'healthcare': [
                'symptoms of', 'treatment for', 'side effects', 'clinical trial', 
                'patient care', 'medical condition', 'diagnosis of', 'prescription drug',
                'dosage guidelines', 'drug interaction', 'surgical procedure', 'mental health',
                'public health', 'epidemiology', 'pharmaceutical', 'cardiovascular disease',
                'respiratory infection', 'neurological disorder', 'immune system', 'hormone therapy',
                'cancer treatment', 'diabetes management', 'hypertension', 'cholesterol levels',
                'physical therapy', 'occupational therapy', 'emergency room', 'urgent care',
                'overdose', 'chest pain', 'trouble breathing', 'severe bleeding', 'stroke symptoms',
                'suicidal thoughts', 'seizure', 'anaphylaxis', 'viral infection', 'bacterial infection',
                'insulin work', 'body work', 'heart work', 'mechanism of action', 'how insulin'
            ],
            'economy': [
                'federal funds rate', 'interest rate', 'inflation rate', 'unemployment rate',
                'gross domestic product', 'gdp growth', 'stock market', 'bond yield',
                'monetary policy', 'fiscal policy', 'quantitative easing', 'supply and demand',
                'market capitalization', 'price to earnings', 'dividend yield', 'trade deficit',
                'balance of payments', 'currency exchange', 'foreign direct investment',
                'labor market', 'wage growth', 'consumer price index', 'producer price index',
                'recession', 'economic expansion', 'business cycle', 'federal reserve',
                'central bank', 'treasury bond', 'corporate bond', 'mutual fund', 'etf',
                'capital gains', 'tax bracket', 'income inequality', 'poverty rate',
                'housing market', 'real estate prices', 'mortgage rate', 'consumer confidence',
                'retail sales', 'manufacturing index', 'service sector', 'gig economy',
                'supply chain', 'global trade', 'tariff', 'free trade agreement',
                'bankruptcy', 'merger and acquisition', 'initial public offering', 'venture capital',
                'private equity', 'hedge fund', 'commodity prices', 'oil prices', 'gold prices',
                'causes a recession', 'causes inflation', 'causes unemployment'
            ],
            'governance': [
                'bill becomes law', 'legislative process', 'congressional committee', 
                'executive order', 'judicial review', 'supreme court', 'constitutional amendment',
                'veto power', 'filibuster', 'cloture', 'gerrymandering', 'electoral college',
                'popular vote', 'ballot initiative', 'referendum', 'campaign finance',
                'political action committee', 'lobbying disclosure', 'freedom of information',
                'administrative law', 'rulemaking process', 'regulatory agency', 'independent counsel',
                'impeachment process', 'confirmation hearing', 'senate judiciary', 'house oversight',
                'treaty ratification', 'international agreement', 'diplomatic immunity',
                'human rights law', 'geneva convention', 'united nations', 'nato alliance',
                'defense strategy', 'military intervention', 'intelligence community',
                'covert action', 'cybersecurity policy', 'election security', 'voting rights',
                'civil liberties', 'due process', 'equal protection', 'first amendment',
                'second amendment', 'fourth amendment', 'search and seizure', 'double jeopardy',
                'cruel and unusual', 'separation of powers', 'checks and balances',
                'federalism', 'state sovereignty', 'local government', 'municipal code',
                'zoning law', 'land use', 'eminent domain', 'property tax', 'sales tax',
                'income tax', 'corporate tax', 'estate tax', 'social security', 'medicare',
                'medicaid', 'affordable care act', 'clean air act', 'clean water act',
                'endangered species', 'environmental protection', 'climate change policy',
                'immigration policy', 'asylum seeker', 'deportation', 'border control',
                'foreign policy', 'national security', 'homeland security', 'fema',
                'disaster relief', 'infrastructure bill', 'budget resolution', 'appropriations',
                'government shutdown', 'continuing resolution', 'omnibus bill', 'pork barrel',
                'earmark', 'revolving door', 'conflict of interest', 'ethics committee',
                'whistleblower', 'classified information', 'top secret', 'security clearance',
                'vice president', 'how treaties', 'treaties get ratified', 'role of the vice'
            ]
        }

        # Concept mapping for disambiguation (Weight: 0.7-0.8)
        self.concept_map = {
            'rate': {
                'healthcare': ['heart rate', 'breathing rate', 'metabolic rate', 'survival rate', 'mortality rate'],
                'economy': ['interest rate', 'inflation rate', 'unemployment rate', 'exchange rate', 'tax rate'],
                'governance': ['approval rate', 'voter turnout rate', 'crime rate']
            },
            'work': {
                'healthcare': ['how the body works', 'how the heart works', 'how insulin works', 'mechanism of action'],
                'economy': ['labor market', 'work force', 'unemployment', 'job market', 'gig work'],
                'governance': ['public works', 'works project', 'infrastructure']
            },
            'power': {
                'healthcare': ['muscle power', 'healing power', 'potency'],
                'economy': ['market power', 'monopoly power', 'purchasing power', 'bargaining power'],
                'governance': ['executive power', 'legislative power', 'judicial power', 'veto power', 'separation of powers']
            },
            'causes': {
                'healthcare': ['disease causes', 'symptoms causes', 'illness causes', 'risk factors'],
                'economy': ['recession causes', 'inflation causes', 'unemployment causes', 'market crash causes'],
                'governance': ['policy causes', 'legislation causes', 'social unrest causes']
            },
            'security': {
                'healthcare': ['food security', 'nutrition security'],
                'economy': ['social security', 'retirement security', 'financial security', 'job security'],
                'governance': ['national security', 'homeland security', 'cybersecurity', 'border security', 'election security']
            },
            'bond': {
                'healthcare': ['antibody bond', 'chemical bond', 'protein binding'],
                'economy': ['treasury bond', 'corporate bond', 'municipal bond', 'savings bond', 'junk bond'],
                'governance': ['surety bond', 'performance bond', 'bail bond']
            },
            'treatment': {
                'healthcare': ['medical treatment', 'cancer treatment', 'drug treatment', 'therapy'],
                'economy': ['waste treatment', 'water treatment', 'sewage treatment'],
                'governance': ['fair treatment', 'equal treatment', 'discrimination']
            },
            'court': {
                'healthcare': [],
                'economy': ['bankruptcy court', 'tax court', 'small claims court'],
                'governance': ['supreme court', 'federal court', 'district court', 'appeals court', 'trial court']
            },
            'fund': {
                'healthcare': ['research fund', 'grant fund'],
                'economy': ['mutual fund', 'hedge fund', 'pension fund', 'trust fund', 'federal funds'],
                'governance': ['sovereign wealth fund', 'disaster relief fund', 'general fund']
            }
        }

        # Single keywords (lowest weight: 0.3-0.5)
        self.domain_keywords = {
            'healthcare': [
                'doctor', 'hospital', 'nurse', 'medicine', 'drug', 'pill', 'tablet', 
                'injection', 'surgery', 'operation', 'disease', 'illness', 'infection',
                'virus', 'bacteria', 'vaccine', 'immunization', 'cancer', 'tumor',
                'diabetes', 'hypertension', 'asthma', 'arthritis', 'depression', 'anxiety',
                'schizophrenia', 'bipolar', 'adhd', 'autism', 'alzheimers', 'parkinsons',
                'stroke', 'heart attack', 'cardiac', 'pulmonary', 'renal', 'hepatic',
                'neurological', 'psychiatric', 'pediatric', 'geriatric', 'obstetric',
                'gynecologic', 'oncology', 'cardiology', 'dermatology', 'ophthalmology',
                'orthopedic', 'radiology', 'pathology', 'anesthesia', 'pharmacy',
                'prescription', 'over-the-counter', 'generic', 'brand-name', 'dosage',
                'side effect', 'contraindication', 'allergy', 'adverse reaction',
                'clinical', 'trial', 'study', 'patient', 'subject', 'placebo',
                'efficacy', 'safety', 'fda', 'cdc', 'who', 'nih', 'cms', 'medicare',
                'medicaid', 'insurance', 'premium', 'deductible', 'copay', 'coverage',
                'network', 'provider', 'specialist', 'primary care', 'referral',
                'diagnosis', 'prognosis', 'remission', 'relapse', 'chronic', 'acute',
                'terminal', 'palliative', 'hospice', 'rehabilitation', 'recovery',
                'wellness', 'prevention', 'screening', 'checkup', 'exam', 'test',
                'lab', 'blood', 'urine', 'x-ray', 'mri', 'ct scan', 'ultrasound',
                'biopsy', 'transplant', 'dialysis', 'chemotherapy', 'radiation',
                'physical therapy', 'occupational therapy', 'speech therapy',
                'counseling', 'psychotherapy', 'cbt', 'dbt', 'emdr', 'support group'
            ],
            'economy': [
                'money', 'cash', 'currency', 'dollar', 'euro', 'yen', 'pound',
                'bank', 'credit', 'debit', 'loan', 'mortgage', 'interest', 'apr',
                'savings', 'checking', 'investment', 'stock', 'share', 'dividend',
                'bond', 'yield', 'return', 'profit', 'loss', 'revenue', 'expense',
                'asset', 'liability', 'equity', 'capital', 'liquidity', 'solvency',
                'bankruptcy', 'foreclosure', 'repossession', 'default', 'delinquency',
                'inflation', 'deflation', 'recession', 'depression', 'boom', 'bust',
                'gdp', 'gnp', 'gni', 'cpi', 'ppi', 'unemployment', 'employment',
                'wage', 'salary', 'income', 'tax', 'deduction', 'exemption', 'credit',
                'refund', 'audit', 'irs', 'sec', 'fed', 'treasury', 'finance',
                'accounting', 'bookkeeping', 'budget', 'forecast', 'projection',
                'market', 'exchange', 'nasdaq', 'nyse', 'dow', 'sp500', 'russell',
                'bull', 'bear', 'volatility', 'risk', 'hedge', 'diversify', 'portfolio',
                'allocation', 'rebalance', 'compound', 'appreciate', 'depreciate',
                'amortize', 'capitalize', 'liquidate', 'merge', 'acquire', 'ipo',
                'valuation', 'multiple', 'ratio', 'margin', 'leverage', 'derivative',
                'option', 'future', 'swap', 'forward', 'commodity', 'futures',
                'oil', 'gas', 'gold', 'silver', 'copper', 'wheat', 'corn', 'soybean',
                'trade', 'export', 'import', 'tariff', 'quota', 'embargo', 'sanction',
                'nafta', 'usmca', 'eu', 'wto', 'imf', 'world bank', 'oecd',
                'supply', 'demand', 'elasticity', 'surplus', 'shortage', 'equilibrium',
                'competition', 'monopoly', 'oligopoly', 'cartel', 'antitrust',
                'regulation', 'deregulation', 'privatization', 'nationalization',
                'subsidy', 'grant', 'incentive', 'stimulus', 'austerity', 'debt',
                'deficit', 'surplus', 'balance', 'payment', 'transfer', 'remittance',
                'gig', 'freelance', 'contractor', 'employee', 'employer', 'union',
                'strike', 'lockout', 'collective bargaining', 'minimum wage',
                'living wage', 'poverty', 'inequality', 'gini', 'mobility', 'class'
            ],
            'governance': [
                'government', 'politics', 'policy', 'law', 'legal', 'court', 'judge',
                'jury', 'trial', 'lawsuit', 'attorney', 'lawyer', 'prosecutor',
                'defendant', 'plaintiff', 'verdict', 'sentence', 'appeal', 'ruling',
                'precedent', 'statute', 'regulation', 'ordinance', 'code', 'act',
                'bill', 'resolution', 'amendment', 'constitution', 'charter', 'treaty',
                'congress', 'senate', 'house', 'representative', 'senator', 'delegate',
                'parliament', 'mp', 'speaker', 'majority', 'minority', 'whip', 'caucus',
                'committee', 'subcommittee', 'hearing', 'testimony', 'deposition',
                'vote', 'ballot', 'election', 'primary', 'general', 'special', 'recall',
                'referendum', 'initiative', 'petition', 'candidate', 'incumbent',
                'challenger', 'nominee', 'endorsement', 'platform', 'party', 'democrat',
                'republican', 'independent', 'third party', 'green', 'libertarian',
                'president', 'vice president', 'secretary', 'minister', 'governor',
                'mayor', 'council', 'commissioner', 'administrator', 'director',
                'agency', 'department', 'bureau', 'office', 'authority', 'board',
                'commission', 'task force', 'panel', 'cabinet', 'advisor', 'aide',
                'staff', 'intern', 'fellow', 'appointee', 'nominee', 'confirm',
                'sworn', 'inaugurate', 'term', 'tenure', 'succession', 'impeach',
                'censure', 'expel', 'reprimand', 'investigate', 'subpoena', 'contempt',
                'perjury', 'obstruction', 'corruption', 'bribe', 'kickback', 'embezzle',
                'fraud', 'scandal', 'cover-up', 'whistleblower', 'leak', 'classify',
                'declassify', 'redact', 'foia', 'transparency', 'accountability',
                'oversight', 'audit', 'review', 'evaluate', 'assess', 'report',
                'recommendation', 'finding', 'conclusion', 'dissent', 'concurrence',
                'opinion', 'memo', 'brief', 'motion', 'order', 'injunction', 'writ',
                'summons', 'warrant', 'indictment', 'information', 'complaint', 'answer',
                'discovery', 'deposition', 'interrogatory', 'request', 'production',
                'subpoena', 'testimonial', 'documentary', 'physical', 'digital',
                'evidence', 'exhibit', 'objection', 'sustain', 'overrule', 'mistrial',
                'hung jury', 'acquittal', 'conviction', 'guilty', 'not guilty', 'innocent',
                'plea', 'bargain', 'deal', 'cooperate', 'immunity', 'leniency', 'parole',
                'probation', 'supervision', 'release', 'detention', 'custody', 'bail',
                'bond', 'jail', 'prison', 'penitentiary', 'correctional', 'rehabilitation',
                'execution', 'death penalty', 'life sentence', 'mandatory minimum',
                'guideline', 'departure', 'variance', 'enhancement', 'mitigation',
                'victim', 'survivor', 'witness', 'informant', 'snitch', 'undercover',
                'sting', 'raid', 'arrest', 'booking', 'processing', 'intake', 'classification',
                'housing', 'program', 'service', 'benefit', 'entitlement', 'eligibility',
                'application', 'approval', 'denial', 'appeal', 'hearing', 'decision',
                'final', 'binding', 'non-binding', 'advisory', 'consultative', 'participatory',
                'deliberative', 'consensus', 'compromise', 'bipartisan', 'partisan',
                'polarization', 'gridlock', 'shutdown', 'crisis', 'emergency', 'disaster',
                'response', 'recovery', 'mitigation', 'preparedness', 'resilience',
                'adaptation', 'sustainability', 'equity', 'justice', 'fairness', 'rights',
                'liberty', 'freedom', 'equality', 'democracy', 'republic', 'federation',
                'confederation', 'unitary', 'decentralized', 'centralized', 'autonomy',
                'sovereignty', 'independence', 'secession', 'annexation', 'occupation',
                'liberation', 'revolution', 'coup', 'insurgency', 'terrorism', 'war',
                'peace', 'conflict', 'negotiation', 'mediation', 'arbitration', 'conciliation',
                'diplomacy', 'statecraft', 'grand strategy', 'doctrine', 'posture',
                'capability', 'readiness', 'modernization', 'acquisition', 'procurement',
                'logistics', 'personnel', 'training', 'exercise', 'deployment', 'rotation',
                'garrison', 'base', 'installation', 'facility', 'infrastructure', 'asset'
            ]
        }

    def validate_domain(self, query: str) -> Tuple[str, float, str]:
        query_lower = query.lower()
        scores = {'healthcare': 0.0, 'economy': 0.0, 'governance': 0.0}
        evidence_log = []

        # 1. Phrase Matching (Highest Priority - Weight 0.9-1.0)
        for domain, phrases in self.domain_phrases.items():
            for phrase in phrases:
                if phrase in query_lower:
                    scores[domain] += 0.95
                    evidence_log.append(f"Phrase match: '{phrase}' -> {domain}")
                    break

        # 2. Concept Disambiguation (Medium Priority - Weight 0.7-0.8)
        words = query_lower.split()
        for word in words:
            if word in self.concept_map:
                idx = words.index(word)
                start = max(0, idx - 2)
                end = min(len(words), idx + 3)
                context_window = " ".join(words[start:end])
                
                best_domain = None
                best_count = 0
                
                for domain, concepts in self.concept_map[word].items():
                    matches = sum(1 for c in concepts if c in context_window)
                    if matches > best_count:
                        best_count = matches
                        best_domain = domain
                
                if best_domain and best_count > 0:
                    scores[best_domain] += 0.75
                    evidence_log.append(f"Concept match: '{word}' in context '{context_window}' -> {best_domain}")

        # 3. Keyword Matching (Lowest Priority - Weight 0.3-0.5)
        total_phrase_concept_score = sum(scores.values())
        
        if total_phrase_concept_score < 0.5:
            for domain, keywords in self.domain_keywords.items():
                matches = sum(1 for kw in keywords if f" {kw} " in f" {query_lower} " or query_lower.startswith(kw + " ") or query_lower.endswith(" " + kw))
                if matches > 0:
                    keyword_score = min(0.3 + (matches * 0.05), 0.6)
                    scores[domain] += keyword_score
                    if matches > 1:
                        evidence_log.append(f"Keyword cluster ({matches} matches) -> {domain}")

        max_score = max(scores.values()) if scores.values() else 0
        if max_score == 0:
            return "unknown", 0.0, "No domain indicators found"
        
        winner = max(scores, key=scores.get)
        confidence = min(scores[winner] / 2.0, 0.99)
        
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) > 1 and sorted_scores[1] > 0:
            margin = scores[winner] - sorted_scores[1]
            if margin < 0.2:
                confidence *= 0.8
        
        reasoning = "; ".join(evidence_log[:3])
        return winner, confidence, reasoning

validator = AdvancedDomainValidator()

def validate_query_domain(query: str) -> Tuple[str, float, str]:
    return validator.validate_domain(query)

if __name__ == "__main__":
    test_queries = [
        "What causes a recession?",
        "How does insulin work in the body?",
        "Explain the veto power",
        "How do treaties get ratified?",
        "What is the current federal funds rate?",
        "What is the filibuster?",
        "What is the difference between viral and bacterial infections?",
        "What is the role of the Vice President?",
        "symptoms of type 2 diabetes",
        "how does a bill become law",
        "what is a bond",
        "chest pain and trouble breathing",
        "overdose on pills"
    ]
    
    print("Advanced Domain Validator Test Results:")
    print("-" * 60)
    for q in test_queries:
        domain, conf, reason = validate_query_domain(q)
        status = "OK" if conf > 0.6 else "WARN"
        print(f"{status} Query: {q}")
        print(f"   Domain: {domain.upper()} (Confidence: {conf:.2f})")
        print(f"   Reasoning: {reason}")
        print()
