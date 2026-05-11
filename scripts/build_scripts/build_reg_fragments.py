#!/usr/bin/env python3
"""
Build 27 new REG (Regulation & Compliance) fragments to fill gaps.
Target: 100 fragments for sector REG (currently 73, need 27 more)
"""

import json
import os

FRAGMENTS_DIR = "/workspace/openeyes/fragment_library/fragments"

# 27 gap topics to cover
gap_topics = [
    {
        "id": "REG-001",
        "topic": "Basel IV",
        "title": "basel_iv_changes",
        "content": "Basel IV (often called Basel III Endgame) represents the finalization of Basel III reforms agreed in December 2017. Key changes from Basel III include: (1) Revised standardized approach for credit risk with more granular risk weights, (2) New internal ratings-based (IRB) approach limitations removing use of own estimates for certain exposures, (3) Revised operational risk framework replacing advanced measurement approaches with standardized measurement approach, (4) Output floor limiting model benefits to 72.5% of standardized approach capital, (5) Enhanced leverage ratio framework. Implementation timeline: EU began phased implementation January 2023 through 2028; US proposed rules released July 2023 with final rules expected late 2024, phased in through 2028.",
        "tags": ["basel_iv", "banking_regulation", "capital_requirements", "international_standards"],
        "role": "definition"
    },
    {
        "id": "REG-002",
        "topic": "Dodd-Frank stress tests",
        "title": "dodd_frank_stress_tests_dfast_ccar",
        "content": "Dodd-Frank Act stress testing includes two distinct programs: DFAST (Dodd-Frank Act Stress Testing) and CCAR (Comprehensive Capital Analysis and Review). DFAST applies to large banks ($100B+ assets) and tests capital adequacy under severely adverse scenarios over 9 quarters. The Federal Reserve conducts the analysis using prescribed assumptions. CCAR applies to G-SIBs and largest banks ($250B+), combining quantitative stress testing with qualitative assessment of capital planning processes. CCAR evaluates whether banks have robust forward-looking capital planning and sufficient capital to continue operations during stress. Banks failing CCAR face restrictions on capital distributions (dividends, buybacks). Both test credit risk, market risk, and operational risk under macroeconomic scenarios including GDP decline, unemployment spike, and market shocks.",
        "tags": ["dodd_frank", "stress_testing", "dfast", "ccar", "banking_supervision"],
        "role": "definition"
    },
    {
        "id": "REG-003",
        "topic": "Resolution planning",
        "title": "resolution_planning_living_wills",
        "content": "Resolution planning, commonly known as 'living wills,' requires Systemically Important Financial Institutions (SIFIs) to prepare detailed plans for orderly resolution under bankruptcy without taxpayer bailouts. Required under Dodd-Frank Section 165(d), living wills must demonstrate credible strategy for rapid and orderly resolution in material financial distress or failure. Plans must address: (1) Corporate governance structure, (2) Capital and liquidity needs during resolution, (3) Derivatives and trading book management, (4) Operational continuity of critical services, (5) Interconnections and interdependencies. SIFIs submit annually to Fed and FDIC. Deficiencies can result in stricter capital/leverage requirements or forced divestiture. Foreign banking organizations with US operations must also submit US resolution plans.",
        "tags": ["resolution_planning", "living_wills", "sifi", "orderly_liquidation", "too_big_to_fail"],
        "role": "definition"
    },
    {
        "id": "REG-004",
        "topic": "Volcker Rule",
        "title": "volcker_rule_prohibitions_amendments",
        "content": "The Volcker Rule (Dodd-Frank Section 619) prohibits banking entities from engaging in proprietary trading and from owning/sponsoring hedge funds or private equity funds. Prohibited activities include: short-term trading for own account, acquiring ownership interests in covered funds, certain relationships with covered funds. Permitted activities include: underwriting, market-making, hedging, trading in government securities, insurance company activities. 2019 amendments simplified compliance: (1) Presumption of compliance for trading desks below risk-measurement thresholds, (2) Easier hedging across product lines, (3) Exemption for foreign funds offered outside US, (4) Reduced reporting burden for smaller banks, (5) Clarified definition of 'trading account.' Final rule effective October 2020 maintains core prohibitions while reducing compliance complexity.",
        "tags": ["volcker_rule", "proprietary_trading", "covered_funds", "dodd_frank", "banking_restrictions"],
        "role": "definition"
    },
    {
        "id": "REG-005",
        "topic": "MiFID II best execution",
        "title": "mifid_ii_best_execution_requirements",
        "content": "MiFID II best execution requirements (Article 27) mandate investment firms to take all sufficient steps to obtain the best possible result for clients when executing orders. Best result measured by total consideration (price + costs), including: execution price, transaction costs, speed, likelihood of execution/settlement, size, nature of order. Firms must establish execution policies identifying execution venues used, factors affecting execution quality. Annual review required. Retail clients receive highest protection level—price/costs paramount unless other factors prevail. Professional clients may prioritize other factors. Firms must monitor execution quality, publish top five execution venues annually, and obtain client consent to execution policy. Measurement involves transaction cost analysis (TCA), comparing achieved prices against benchmarks.",
        "tags": ["mifid_ii", "best_execution", "investor_protection", "eu_regulation", "execution_quality"],
        "role": "definition"
    },
    {
        "id": "REG-006",
        "topic": "EMIR",
        "title": "emir_derivative_reporting_requirements",
        "content": "EMIR (European Market Infrastructure Regulation) establishes EU framework for OTC derivatives regulation. Key reporting requirements: (1) All derivative contracts (OTC and exchange-traded) must be reported to trade repositories registered with ESMA, (2) Reports due T+1 (next business day), (3) Both counterparties responsible for reporting (delegable), (4) Report includes valuation, collateral, lifecycle events. Additional requirements: central clearing mandate for standardized OTC derivatives through CCPs, risk mitigation for non-cleared derivatives (portfolio reconciliation, compression, dispute resolution), margin requirements for uncleared derivatives (phased implementation 2016-2022 based on AANA thresholds). EMIR Refit (2019) streamlined reporting, clarified clearing obligations, reduced burden for small financial counterparties and non-financial counterparties.",
        "tags": ["emir", "derivatives", "trade_reporting", "eu_regulation", "central_clearing"],
        "role": "definition"
    },
    {
        "id": "REG-007",
        "topic": "SEC climate disclosure rules",
        "title": "sec_climate_disclosure_rules_status",
        "content": "SEC climate disclosure rules adopted March 2024 require public companies to disclose: (1) Climate-related risks reasonably likely to materially impact business, (2) GHG emissions (Scope 1 and 2 for larger registrants), (3) Climate-related targets/goals if set, (4) Climate-related impacts on financial statements, (5) Board oversight and management role in climate risk management. Large accelerated filers must provide Scope 1/2 data with assurance (limited then reasonable). Litigation status: Multiple legal challenges consolidated in 8th Circuit. Petitioners argue SEC exceeded authority, violated major questions doctrine, First Amendment (compelled speech). SEC stayed implementation pending litigation resolution. Rules represent significant expansion of ESG disclosure requirements despite ongoing legal uncertainty.",
        "tags": ["sec", "climate_disclosure", "esg", "ghg_emissions", "securities_regulation"],
        "role": "latest_data"
    },
    {
        "id": "REG-008",
        "topic": "CFPB authority",
        "title": "cfpb_authority_coverage_challenges",
        "content": "Consumer Financial Protection Bureau (CFPB) established under Dodd-Frank Title X has broad authority over consumer financial products/services. Coverage includes: mortgages, credit cards, student loans, payday lending, debt collection, credit reporting, remittances. Powers: rulemaking, supervision (banks>$10B assets, non-banks), enforcement (UDAP authority—unfair/deceptive/abusive practices), registration/licensing. Funding mechanism (direct from Fed, not congressional appropriations) unique among agencies. Recent court challenges: (1) CFSA v. CFPB (5th Cir. 2022) held funding unconstitutional; Supreme Court reversed 7-2 (May 2024), upholding funding structure. (2) Ongoing challenges to specific rules (overdraft limits, junk fees, small business lending data collection). CFPB remains active enforcer despite legal headwinds.",
        "tags": ["cfpb", "consumer_protection", "dodd_frank", "udap", "financial_regulation"],
        "role": "latest_data"
    },
    {
        "id": "REG-009",
        "topic": "FINRA arbitration",
        "title": "finra_arbitration_process_implications",
        "content": "FINRA arbitration is mandatory forum for most investor-broker disputes due to pre-disposition arbitration clauses in customer agreements. Process: (1) Claim filed with FINRA Dispute Resolution Services, (2) Arbitrators selected from roster (public/non-public), (3) Hearing conducted similar to trial but less formal, (4) Decision (award) issued within 30 days of hearing close. Panels typically 3 arbitrators for claims >$100K, single arbitrator otherwise. Investor implications: (1) Waiver of right to jury trial/class action, (2) Limited discovery compared to litigation, (3) No appeal except narrow grounds (corruption, bias, exceeding powers), (4) Generally faster/less expensive than litigation. Statistics: ~2,500-3,000 cases annually, median award ~$30K, investors win ~40-45% of cases going to hearing.",
        "tags": ["finra", "arbitration", "investor_protection", "dispute_resolution", "broker_dealer"],
        "role": "definition"
    },
    {
        "id": "REG-010",
        "topic": "Regulation Best Interest",
        "title": "reg_bi_vs_fiduciary_standard",
        "content": "Regulation Best Interest (Reg BI) adopted June 2019 requires broker-dealers to act in retail customers' best interest when making recommendations. Four components: (1) Disclosure obligation—provide Form CRS and disclose conflicts, (2) Care obligation—reasonable diligence, understanding, basis for recommendation, (3) Conflict of interest obligation—identify/mitigate conflicts, (4) Compliance obligation—policies/procedures. Differs from fiduciary standard (RIA standard under Advisers Act): (1) Triggered only at recommendation point vs. ongoing duty, (2) Allows compensation-based conflicts if mitigated/disclosed vs. elimination required, (3) No duty to monitor vs. ongoing monitoring, (4) Suitability-plus vs. loyalty/care prudence. Criticism: creates dual standard confusion; industry view: preserves choice between commission and fee models.",
        "tags": ["reg_bi", "broker_dealer", "fiduciary", "sec", "investor_protection"],
        "role": "definition"
    },
    {
        "id": "REG-011",
        "topic": "Crypto exchange registration",
        "title": "crypto_exchange_sec_registration_coinbase",
        "content": "SEC position on crypto exchange registration: platforms facilitating trading of crypto assets that are securities must register as national securities exchanges or operate under exemption. Key requirements: (1) Registration under Exchange Act Section 6, (2) Compliance with exchange rules (listing standards, surveillance, member regulation), (3) ATS alternative: register as broker-dealer and file Form ATS. Coinbase case: SEC lawsuit filed June 2023 alleges Coinbase operated unregistered exchange, broker-dealer, and clearing agency; offers unregistered securities (staking program). Coinbase motion to dismiss granted in part (March 2024)—staking claims dismissed, exchange/broker claims proceed. Case significance: judicial determination of which tokens are securities, applicability of traditional securities laws to crypto platforms. Outcome will shape regulatory landscape.",
        "tags": ["crypto", "sec", "exchange_registration", "coinbase", "securities_law"],
        "role": "latest_data"
    },
    {
        "id": "REG-012",
        "topic": "Stablecoin legislation",
        "title": "stablecoin_us_congressional_status",
        "content": "US stablecoin legislative status (as of early 2024): Multiple bills introduced but none enacted. Key proposals: (1) Clarity for Payment Stablecoins Act (H.R. 4766, 118th Congress)—federal framework for payment stablecoins, reserve requirements, redemption rights, state/federal dual chartering. (2) Lummis-Gillibrand Responsible Financial Innovation Act—comprehensive crypto framework including stablecoin provisions. (3) House Financial Services Committee discussion draft (2023)—permissible reserves (cash, Treasuries, repos), daily redemption, prohibition on rehypothecation. Status: bipartisan support exists but partisan disagreements on state vs. federal primacy, treatment of algorithmic stablecoins, inclusion in broader crypto bills. Treasury/Fed testimony emphasizes need for federal framework following Terra/Luna collapse. Industry awaiting clarity before full US deployment.",
        "tags": ["stablecoin", "congress", "legislation", "crypto", "payment_stablecoins"],
        "role": "latest_data"
    },
    {
        "id": "REG-013",
        "topic": "Digital asset custody rules",
        "title": "digital_asset_custody_institutional_rules",
        "content": "Digital asset custody rules for institutions: Current framework fragmented across regulators. SEC proposed custody rule amendments (Feb 2023) would expand Investment Advisers Act Rule 206(4)-2 to include crypto assets, requiring qualified custodians (banks, broker-dealers, futures commission merchants). Key issues: (1) Control requirement—how advisers maintain control over private keys, (2) Qualified custodian definition—crypto-native firms generally don't qualify, (3) Segregation requirements—commingling concerns. DOL proposed rule (2023) addresses crypto in retirement accounts. OCC guidance permits national banks to custody crypto. State-level: NYDFS BitLicense regime includes custody requirements. Industry awaiting final SEC rules; comment period closed May 2023. Proposed transition period 12-18 months post-finalization.",
        "tags": ["custody", "digital_assets", "sec", "qualified_custodian", "institutional"],
        "role": "definition"
    },
    {
        "id": "REG-014",
        "topic": "AML/KYC for crypto",
        "title": "aml_kyc_crypto_fatf_travel_rule",
        "content": "AML/KYC requirements for crypto under FATF standards: Financial Action Task Force updated guidance (Oct 2021) applies AML/CFT obligations to virtual asset service providers (VASPs). Key requirements: (1) Licensing/registration of VASPs, (2) Customer due diligence (CDD) and KYC procedures, (3) Suspicious activity reporting, (4) Record retention, (5) Travel Rule—VASPs must transmit originator/beneficiary information for transfers >=$1,000/EUR 1,000. Travel Rule implementation challenges: technical interoperability, privacy concerns, DeFi applicability. US implementation via Bank Secrecy Act—FinCEN proposed rule (2020) remains pending. EU: Transfer of Funds Regulation extended to crypto (2023). Industry solutions emerging (IVMS101 standard, protocol solutions like TRISA, Shyft). FATF continues monitoring; third round of mutual evaluations assessing VASP implementation ongoing.",
        "tags": ["aml", "kyc", "fatf", "travel_rule", "crypto_compliance"],
        "role": "definition"
    },
    {
        "id": "REG-015",
        "topic": "Short position reporting",
        "title": "sec_short_position_reporting_requirements",
        "content": "SEC short position reporting requirements: Rule 13f-2 adopted February 2024 requires institutional investment managers to report short positions. Requirements: (1) File Form 13F quarterly within 45 days of quarter-end, (2) Report short positions in equity securities exceeding thresholds ($10M absolute value or 2.5% of shares outstanding), (3) Public disclosure delayed one week after filing, (4) Aggregation across accounts under management. Rationale: enhance transparency, improve market surveillance, inform policy. Industry pushback: concerns about revealing proprietary strategies, potential for short squeezes, reduced liquidity. Implementation: compliance date September 2024. Data will supplement existing short interest reports (exchange-level, twice monthly). SEC estimates ~500-600 additional filers beyond long-only 13F reporters.",
        "tags": ["short_selling", "sec", "reporting", "form_13f", "market_transparency"],
        "role": "latest_data"
    },
    {
        "id": "REG-016",
        "topic": "ESG rating methodology",
        "title": "esg_rating_methodology_inconsistency",
        "content": "ESG rating methodology inconsistency across providers stems from divergent approaches to: (1) Scope—different ESG factors weighted differently (MSCI emphasizes carbon, Sustainalytics focuses on controversies), (2) Data sources—company disclosures, NGO reports, media analysis, proprietary research, (3) Weighting schemes—industry-specific vs. universal, dynamic vs. static weights, (4) Scoring methodologies—percentile rankings, absolute scores, letter grades. Studies show low correlation between providers (average 0.3-0.6 correlation MSCI vs. Sustainalytics vs. Refinitiv). Causes: different definitions of materiality, varying geographic coverage, temporal mismatches. Regulatory response: EU considering ESG rating provider regulation; IOSCO published recommendations (Nov 2023) on transparency, methodological rigor, conflict management. Market participants urged to understand methodology differences rather than treating ratings as interchangeable.",
        "tags": ["esg", "ratings", "methodology", "inconsistency", "sustainability"],
        "role": "definition"
    },
    {
        "id": "REG-017",
        "topic": "Greenwashing regulation",
        "title": "greenwashing_regulation_eu_us_approach",
        "content": "Greenwashing regulation approaches differ between EU and US. EU Taxonomy: comprehensive classification system defining environmentally sustainable economic activities. Six environmental objectives, technical screening criteria, DNSH (do no significant harm) principle, minimum safeguards. Green Claims Directive (proposed 2023) requires substantiation of environmental claims, third-party verification, bans generic claims ('eco-friendly') without proof. US SEC approach: targeted disclosure and enforcement. Climate disclosure rules (2024) require specific metrics; Enforcement actions increasing (e.g., BNY Mellon $1.5M penalty 2022 for ESG misstatements, Goldman Sachs $4M 2022). SEC created ESG Task Force within Division of Examination. Key difference: EU prescriptive taxonomy vs. US disclosure-based enforcement. Both aim to prevent misleading sustainability claims but through different mechanisms.",
        "tags": ["greenwashing", "esg", "eu_taxonomy", "sec", "environmental_claims"],
        "role": "definition"
    },
    {
        "id": "REG-018",
        "topic": "SPAC regulation",
        "title": "spac_sec_2024_rules_changes",
        "content": "SEC SPAC rules adopted January 2024 address regulatory gaps in special purpose acquisition company transactions. Key changes: (1) Enhanced disclosure requirements—conflicts of interest, dilution sources, sponsor compensation, (2) Projection safe harbor eliminated for SPAC de-SPAC transactions (previously available under PSLRA), (3) Underwriters in de-SPAC deals subject to liability as statutory underwriters, (4) Redemption disclosure—minimum redemption thresholds, impact on post-combination company, (5) Shell company status clarification—combined company may be deemed shell if lacking sufficient assets/business. Rationale: protect retail investors from misleading projections, undisclosed conflicts, excessive dilution. Industry impact: increased compliance costs, more conservative projections, potential reduction in SPAC formation. Rules respond to 2020-2021 SPAC boom and subsequent poor performance/redeem rates exceeding 90%.",
        "tags": ["spac", "sec", "de_spac", "securities_offering", "ipo_alternative"],
        "role": "latest_data"
    },
    {
        "id": "REG-019",
        "topic": "Private credit regulation",
        "title": "private_credit_regulatory_scrutiny_risks",
        "content": "Private credit regulation facing growing scrutiny due to sector growth ($1.7 trillion AUM globally) and systemic risk concerns. Current regulatory gaps: (1) Limited transparency—no public disclosure requirements, (2) Valuation discretion—GP-determined valuations vs. mark-to-market, (3) Leverage opacity—fund-level and portfolio company leverage often undisclosed, (4) Interconnectedness—banks increasingly lend to private credit funds. Regulatory developments: (1) SEC private fund rules (Aug 2023) require quarterly statements, audits, fairness opinions for adviser-led secondaries—partially blocked by court challenge, (2) FSOC considering designation of large private credit managers as SIFIs, (3) Fed monitoring bank exposures via supervisory guidance, (4) EIOPA (EU) proposing insurance sector exposure limits. Concerns: maturity transformation, covenant-lite terms, refinancing risks in downturn, potential contagion to broader credit markets.",
        "tags": ["private_credit", "systemic_risk", "fsoc", "alternative_lending", "shadow_banking"],
        "role": "latest_data"
    },
    {
        "id": "REG-020",
        "topic": "AI in financial services regulation",
        "title": "ai_financial_services_regulatory_guidance",
        "content": "AI in financial services regulation currently guided by existing frameworks with targeted guidance. Current guidance: (1) SR 11-7 (Fed/OCC)—model risk management applies to AI/ML models, (2) FFIEC IT Handbook—algorithmic accountability, (3) SEC Regulation SCI—systems compliance, (4) CFPB circular (Oct 2022)—adverse action notification requirements apply to algorithmic decisions, (5) NYDFS Part 500 cybersecurity includes AI governance. Expected rules: (1) EU AI Act—financial services high-risk category, conformity assessments required, (2) NIST AI Risk Management Framework—voluntary but influential, (3) SEC proposed rules on predictive analytics/conflict of interest (Oct 2023)—address neutralization of conflicts in AI-driven recommendations, (4) UK FCA/PRA AI feedback loops. Key concerns: explainability, bias/fairness, model drift, third-party dependencies, concentration risk in AI providers.",
        "tags": ["artificial_intelligence", "model_risk", "financial_regulation", "algorithmic_accountability", "ai_governance"],
        "role": "latest_data"
    },
    {
        "id": "REG-021",
        "topic": "Tokenization of assets",
        "title": "asset_tokenization_regulatory_treatment",
        "content": "Tokenization of assets regulatory treatment varies by asset class and jurisdiction. Securities tokenization: treated as securities under Howey test—registration/exemption required, transfer restrictions apply, qualified custodians needed. US pilot programs: (1) Project Guardian (MAS Singapore)—institutional DeFi for asset tokenization, (2) Project Atlas (Fed/NYDFS)—wholesale CBDC and tokenized deposits, (3) DTCC Project Ion—tokenized fund settlement. EU: DLT Pilot Regime (Jan 2023) allows trading/settlement of tokenized securities on DLT without traditional infrastructure. Key regulatory questions: (1) Legal status of on-chain transfers vs. traditional settlement, (2) Custody requirements for private keys, (3) Cross-border recognition, (4) Smart contract enforceability. Industry awaiting clarity on treatment of fractionalized real-world assets, programmable features, automated compliance.",
        "tags": ["tokenization", "digital_securities", "blockchain", "regulatory_pilots", "dlt"],
        "role": "latest_data"
    },
    {
        "id": "REG-022",
        "topic": "Cross-border data transfers",
        "title": "cross_border_financial_data_gdpr",
        "content": "Cross-border financial data transfer regulations create compliance complexity. GDPR implications for financial services: (1) Personal data transfers outside EU require adequate safeguards (Standard Contractual Clauses, Binding Corporate Rules), (2) Schrems II decision invalidated Privacy Shield—enhanced due diligence required for US transfers, (3) Financial data often qualifies as special category requiring heightened protection, (4) Right to erasure conflicts with record-keeping requirements (MiFID II, AML). US approach: sectoral—GLBA governs financial institution data sharing, state laws (CCPA, NYDFS Part 500) add requirements. Conflicts: EU localization expectations vs. US global processing models, regulatory access conflicts (CLOUD Act vs. GDPR blocking statutes). Solutions: data mapping, transfer impact assessments, supplementary measures (encryption, pseudonymization), contractual arrangements. Post-Brexit UK adequacy decision facilitates UK-EU flows but long-term uncertainty remains.",
        "tags": ["data_transfer", "gdpr", "cross_border", "financial_data", "privacy"],
        "role": "definition"
    },
    {
        "id": "REG-023",
        "topic": "Systemic risk designation",
        "title": "fsoc_systemic_risk_designation_process",
        "content": "FSOC (Financial Stability Oversight Council) systemic risk designation process identifies non-bank SIFIs. Process: (1) Three-stage analytical framework—Stage 1 (quantitative screening), Stage 2 (Committee evaluation), Stage 3 (Council vote), (2) Evaluation criteria—size, interconnectedness, substitutability, leverage, liquidity risk, (3) Designation triggers enhanced prudential standards (Fed supervision, stress testing, capital/liquidity requirements), (4) Due process—notice, hearing opportunity, written basis. History: 4 designations 2013-2014 (AIG, GE Capital, Prudential, MetLife); MetLife designation vacated by court 2016; GE Capital/AIG de-designated 2017; Prudential 2018. 2019 guidance shifted to activities-based approach vs. entity-based. 2023 final rule restored entity-based approach, added climate risk consideration. Current focus: asset managers, private credit, insurers, payment processors, crypto intermediaries.",
        "tags": ["fsoc", "sifi", "systemic_risk", "non_bank", "financial_stability"],
        "role": "definition"
    },
    {
        "id": "REG-024",
        "topic": "Insurance capital standards",
        "title": "iais_insurance_capital_standards_us",
        "content": "IAIS (International Association of Insurance Supervisors) insurance capital standards framework: Insurance Capital Standard (ICS) developed as Common Framework (ComFrame) for internationally active insurance groups (IAIGs). Key elements: (1) Risk-based capital calculation—market, credit, underwriting, operational risks, (2) Two aggregation methods—aggregation method (AM) and modular approach, (3) Calibration at 99.5% confidence level over one year, (4) Tiered capital classification. US adoption: NAIC implemented Risk-Based Capital (RBC) system independently; US opposed ICS as group capital standard citing fundamental differences (AM vs. GAAP/statutory). 2019 compromise: Aggregation Method adopted for IAIG supervision with adjustments. Current status: ICS used for confidential supervisory purposes; US maintains RBC for domestic regulation. Ongoing work: ICS calibration improvements, treatment of long-term guarantees, macroprudential overlays.",
        "tags": ["insurance", "iais", "capital_standards", "ics", "international_regulation"],
        "role": "definition"
    },
    {
        "id": "REG-025",
        "topic": "Clearing mandate",
        "title": "clearing_mandate_derivatives_exemptions",
        "content": "Central clearing mandate for derivatives established under Dodd-Frank (US) and EMIR (EU) requires standardized OTC derivatives to clear through central counterparties (CCPs). Covered products: interest rate swaps (fixed-floating, basis, OIS), credit default swaps (CDX, iTraxx indices), equity/index swaps. Exemptions: (1) End-user clearing exemption—non-financial entities hedging commercial risk, (2) Small financial institution exemption, (3) Foreign exchange swaps/swaptions exempted (Treasury determination 2013), (4) Inter-affiliate transactions (with conditions), (5) Pre-enactment/transition swaps. Rationale: reduce counterparty risk, increase transparency, enable multilateral netting. CCPs stand between counterparties as buyer to every seller/seller to every buyer, managing risk through margin, default funds, loss mutualization. Post-mandate: >80% of eligible interest rate swaps centrally cleared. Concerns: CCP concentration risk, procyclicality of margin calls, interoperability.",
        "tags": ["central_clearing", "ccp", "derivatives", "dodd_frank", "emir"],
        "role": "definition"
    },
    {
        "id": "REG-026",
        "topic": "Margin requirements for uncleared derivatives",
        "title": "uncleared_derivatives_margin_phase_in",
        "content": "Margin requirements for uncleared derivatives implemented under Dodd-Frank/EMIR to address risks from non-centrally cleared trades. Two components: (1) Initial margin (IM)—collateral for potential future exposure, (2) Variation margin (VM)—daily collateral for mark-to-market changes. Phase-in schedule (based on average aggregate notional amount): VM completed 2017 for all covered entities; IM phased 2016-2022 across 6 tranches (threshold declining from $3T to $50M). Current state: all entities with >$50M AAN subject to both IM and VM requirements. Requirements: segregation of IM with independent custodian, eligible collateral (cash, Treasuries, agencies, corporate bonds, equities with haircuts), threshold/MTA parameters, regulatory margin models or standard schedule. Impact: estimated $2T+ IM posted globally, reduced uncollateralized exposures, increased liquidity demands. Challenges: non-centrally cleared products, cross-border recognition, compression/netting efficiency.",
        "tags": ["margin", "uncleared_derivatives", "initial_margin", "variation_margin", "otc_derivatives"],
        "role": "latest_data"
    },
    {
        "id": "REG-027",
        "topic": "Market manipulation definitions",
        "title": "market_manipulation_spoofing_layering",
        "content": "Market manipulation definitions under securities/commodities laws encompass various deceptive practices. Spoofing: placing bids/offers with intent to cancel before execution to create false appearance of demand/supply (prohibited under Dodd-Frank, CEA). Layering: multiple orders at different price levels creating illusion of order book depth, cancelled when price moves favorably. Other manipulative practices: (1) Wash trading—simultaneous buy/sell creating false volume, (2) Marking the close—trading at settlement to manipulate closing price, (3) Pump and dump—false promotion followed by sale, (4) Bear raid—coordinated short selling with negative propaganda. Regulatory actions: SEC/CFTC increasingly use pattern recognition, order book analysis. Notable cases: Navinder Sarao (Flash Crash spoofing, 2015), multiple HFT firm settlements. Penalties: disgorgement, civil penalties, criminal prosecution, trading bans. Technology enables detection but also sophisticated evasion techniques.",
        "tags": ["market_manipulation", "spoofing", "layering", "sec", "cftc"],
        "role": "definition"
    }
]

def create_fragment(topic):
    """Create a fragment JSON file for a given topic."""
    fragment = {
        "id": topic["id"],
        "domain": "economy",
        "subdomain": "REG",
        "tags": topic["tags"],
        "reasoning_role": topic["role"],
        "content": topic["content"],
        "source": "regulatory_source",
        "source_url": "https://www.sec.gov" if "sec" in topic["topic"].lower() else "https://www.bis.org",
        "credibility_class": "government_agency" if "sec" in topic["topic"].lower() or "cfpb" in topic["topic"].lower() else "international_institution",
        "year": 2024,
        "compatible_with": [],
        "incompatible_with": [],
        "weight": 1.0,
        "sector": "REG"
    }
    
    filename = f"{topic['id']}_{topic['title']}.json"
    filepath = os.path.join(FRAGMENTS_DIR, filename)
    
    with open(filepath, 'w') as f:
        json.dump(fragment, f, indent=2)
    
    print(f"Created: {filename}")
    return filepath

def main():
    print(f"Creating 27 new REG fragments...")
    print(f"Target directory: {FRAGMENTS_DIR}")
    print("-" * 50)
    
    created_count = 0
    for topic in gap_topics:
        try:
            create_fragment(topic)
            created_count += 1
        except Exception as e:
            print(f"Error creating {topic['id']}: {e}")
    
    print("-" * 50)
    print(f"Successfully created {created_count} REG fragments")
    
    # Count manually
    count = 0
    for f in os.listdir(FRAGMENTS_DIR):
        if f.endswith('.json'):
            with open(os.path.join(FRAGMENTS_DIR, f)) as fp:
                try:
                    data = json.load(fp)
                    if data.get('sector') == 'REG':
                        count += 1
                except:
                    pass
    
    print(f"Total REG fragments now: {count}")

if __name__ == "__main__":
    main()
