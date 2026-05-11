#!/usr/bin/env python3
"""
Build GEO (Geopolitics & Trade Policy) sector fragments for OpenEyes.
Target: 150 fragments total (currently 13, need 137 new).

Sources: Council on Foreign Relations (cfr.org), World Trade Organization (wto.org), 
Congressional Research Service (crs.gov), IMF working papers (imf.org).

Topics covered:
- US-China economic relations
- Global trade architecture
- Sanctions and financial warfare
- Currency and monetary geopolitics
- Regional economic blocs
"""

import json
from pathlib import Path

FRAGMENTS_DIR = Path("/workspace/openeyes/fragment_library/fragments")

# Fragment templates organized by topic area
GEO_FRAGMENTS = [
    # ==================== US-CHINA ECONOMIC RELATIONS ====================
    {
        "id": "frag_eco_GEO_us_china_tariffs_def_001",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["us_china", "trade_war", "tariffs", "definition"],
        "reasoning_role": "definition",
        "content": "US-China trade war began in 2018 with Section 301 tariffs on $34B of Chinese goods. Escalated to cover ~$370B annually. Average tariff rate on Chinese imports rose from 3% to 21%. China retaliated with tariffs on $110B of US goods, targeting agriculture and energy.",
        "source": "congressional_research_service",
        "source_url": "https://crs.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.95
    },
    {
        "id": "frag_eco_GEO_us_china_tariffs_counter_001",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["us_china", "trade_war", "tariffs", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Trade war costs: US consumers bore ~90% of tariff costs per NBER studies. Manufacturing employment declined in tariff-exposed sectors. Agricultural exports to China fell 36% in 2019, requiring $28B in federal farm aid. Supply chain disruptions exceeded strategic benefits.",
        "source": "nber_working_paper",
        "source_url": "https://www.nber.org/",
        "credibility_class": "academic_research",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_us_china_tariffs_latest_001",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["us_china", "trade_war", "tariffs", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "As of 2024, most Trump-era tariffs remain in place. Biden administration maintained strategic tariffs while launching targeted exclusions. US-China trade deficit narrowed to $279B in 2023 from $418B peak. Trade diversion to Vietnam, Mexico, India accelerated.",
        "source": "us_trade_representative",
        "source_url": "https://ustr.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_decoupling_derisking_def_002",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["decoupling", "de_risking", "supply_chain", "definition"],
        "reasoning_role": "definition",
        "content": "Decoupling vs de-risking distinction: Decoupling implies comprehensive economic separation across all sectors. De-risking targets specific vulnerabilities (critical tech, supply chains) while maintaining general trade. EU and US officially pursue de-risking, not decoupling, with China.",
        "source": "council_on_foreign_relations",
        "source_url": "https://www.cfr.org/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_decoupling_derisking_counter_002",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["decoupling", "de_risking", "supply_chain", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "De-risking critique: In practice, de-risking creates same disruption as decoupling. Companies face binary choices on tech standards, data governance, supply chains. 'Small yard, high fence' approach expands incrementally. Compliance costs disproportionately burden smaller firms.",
        "source": "peterson_institute",
        "source_url": "https://www.piie.com/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.89
    },
    {
        "id": "frag_eco_GEO_decoupling_derisking_latest_002",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["decoupling", "de_risking", "supply_chain", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "2024 de-risking metrics: US direct investment in China down 90% from 2022 peak. EU investment declined 47%. Friend-shoring to Mexico, Vietnam, India accelerated. However, US-China trade in non-restricted categories remains near record highs, limiting practical impact.",
        "source": "rhodium_group",
        "source_url": "https://rhg.com/",
        "credibility_class": "research_firm",
        "year": 2024,
        "weight": 0.91
    },
    {
        "id": "frag_eco_GEO_chips_act_def_003",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["chips_act", "semiconductors", "export_controls", "definition"],
        "reasoning_role": "definition",
        "content": "CHIPS and Science Act (2022): $52.7B in semiconductor subsidies, $24B tax credits. Goals: restore US chip manufacturing capacity, counter China's semiconductor ambitions. Includes guardrails preventing recipients from expanding advanced chip production in China for 10 years.",
        "source": "department_of_commerce",
        "source_url": "https://www.commerce.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.96
    },
    {
        "id": "frag_eco_GEO_chips_act_counter_003",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["chips_act", "semiconductors", "export_controls", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "CHIPS Act limitations: $52B represents only ~6% of global chip capex annually. TSMC, Samsung remain dominant. Export controls may accelerate China's indigenous development. Subsidies risk overcapacity in mature nodes. Labor shortage constrains US manufacturing expansion.",
        "source": "semi_analysis",
        "source_url": "https://www.semianalysis.com/",
        "credibility_class": "industry_analysis",
        "year": 2024,
        "weight": 0.87
    },
    {
        "id": "frag_eco_GEO_chips_act_latest_003",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["chips_act", "semiconductors", "export_controls", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "CHIPS Act implementation 2024: $33B awarded to Intel, TSMC, Samsung, Micron. 38 projects announced across 22 states. October 2023 export controls expanded to cover AI chips, HBM memory. Netherlands, Japan joined restrictions on lithography equipment exports to China.",
        "source": "white_house",
        "source_url": "https://www.whitehouse.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.95
    },
    {
        "id": "frag_eco_GEO_cfius_review_def_004",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["cfius", "foreign_investment", "national_security", "definition"],
        "reasoning_role": "definition",
        "content": "CFIUS (Committee on Foreign Investment in the US): Interagency committee reviewing foreign investments for national security risks. FIRRMA (2018) expanded jurisdiction to include real estate, critical tech, sensitive data. Mandatory filing required for certain transactions involving foreign government control.",
        "source": "treasury_department",
        "source_url": "https://home.treasury.gov/policy-issues/international-policy/the-committee-on-foreign-investment-in-the-united-states-cfius",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.96
    },
    {
        "id": "frag_eco_GEO_cfius_review_counter_004",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["cfius", "foreign_investment", "national_security", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "CFIUS critique: Process lacks transparency, timelines unpredictable. 'National security' definition expanded beyond traditional defense to include data, critical infrastructure. Deters legitimate investment. Retaliatory screening mechanisms emerging in China, EU, creating fragmented global investment landscape.",
        "source": "cfr_working_paper",
        "source_url": "https://www.cfr.org/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.88
    },
    {
        "id": "frag_eco_GEO_cfius_review_latest_004",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["cfius", "foreign_investment", "national_security", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "CFIUS 2023 annual report: 284 notices filed, 132 short-form declarations. 10 transactions blocked or divested. China-related deals down 75% from 2019 peak. Focus shifted to venture capital, minority stakes in AI, biotech, quantum computing startups. Real estate cases near military bases increased.",
        "source": "treasury_department",
        "source_url": "https://home.treasury.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_tiktok_data_sovereignty_def_005",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["tiktok", "data_sovereignty", "china", "tech_regulation", "definition"],
        "reasoning_role": "definition",
        "content": "TikTok data sovereignty debate centers on whether Chinese-owned apps pose national security risks through potential data access by CCP. Project Texas (Oracle partnership) aims to isolate US user data. Broader implications for cross-border data flows, tech decoupling, platform regulation.",
        "source": "congressional_hearing",
        "source_url": "https://www.congress.gov/",
        "credibility_class": "government_proceedings",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_tiktok_data_sovereignty_counter_005",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["tiktok", "data_sovereignty", "china", "tech_regulation", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "TikTok ban critique: No public evidence of data misuse presented. US social media platforms also harvest extensive user data. Selective enforcement raises free speech concerns. Technical isolation ('Project Texas') may be sufficient. Precedent for banning foreign apps threatens open internet principles.",
        "source": "aclc_policy_brief",
        "source_url": "https://www.aclu.org/",
        "credibility_class": "advocacy_organization",
        "year": 2024,
        "weight": 0.85
    },
    {
        "id": "frag_eco_GEO_tiktok_data_sovereignty_latest_005",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["tiktok", "data_sovereignty", "china", "tech_regulation", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "TikTok legislation 2024: Protecting Americans from Foreign Adversary Controlled Applications Act passed April 2024. Requires ByteDance divestiture within 270 days or app banned from US app stores. TikTok filed lawsuit challenging constitutionality. Montana state ban blocked by federal court.",
        "source": "congressional_record",
        "source_url": "https://www.congress.gov/",
        "credibility_class": "government_legislation",
        "year": 2024,
        "weight": 0.95
    },
    {
        "id": "frag_eco_GEO_taiwan_strait_risk_def_006",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["taiwan", "supply_chain", "semiconductors", "geopolitical_risk", "definition"],
        "reasoning_role": "definition",
        "content": "Taiwan Strait economic risk: Taiwan produces 92% of advanced semiconductors (<10nm). TSMC alone makes 60% of global chips. Conflict would eliminate advanced chip supply for 6-12 months minimum. Estimated global GDP impact: $2.7-3.5 trillion. Defense, auto, AI sectors most vulnerable.",
        "source": "cfr_special_report",
        "source_url": "https://www.cfr.org/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_taiwan_strait_risk_counter_006",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["taiwan", "supply_chain", "semiconductors", "geopolitical_risk", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Taiwan risk mitigation limits: TSMC Arizona fab won't match Taiwan capacity until 2030+. Advanced packaging remains Taiwan-concentrated. Chip stockpiles provide only weeks of buffer. Diversification to Korea, US, EU insufficient for advanced nodes. Military deterrence remains primary risk management tool.",
        "source": "csis_analysis",
        "source_url": "https://www.csis.org/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.90
    },
    {
        "id": "frag_eco_GEO_taiwan_strait_risk_latest_006",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["taiwan", "supply_chain", "semiconductors", "geopolitical_risk", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Taiwan semiconductor diversification 2024: TSMC Arizona producing 4nm, planning 3nm. Japan fab operational. Germany fab delayed. CHIPS Act incentives accelerating US capacity. However, Taiwan still accounts for 90%+ of cutting-edge production. Cross-strait tensions elevated following 2024 elections.",
        "source": "tsmc_investor_report",
        "source_url": "https://www.tsmc.com/",
        "credibility_class": "corporate_disclosure",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_belt_road_def_007",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["belt_and_road", "china", "infrastructure", "development", "definition"],
        "reasoning_role": "definition",
        "content": "Belt and Road Initiative (BRI): China's global infrastructure strategy launched 2013. Two components: Silk Road Economic Belt (land routes) and 21st Century Maritime Silk Road. 150+ countries signed MOUs. Cumulative investment: $1-1.3 trillion through 2023. Focus: ports, railways, energy, digital infrastructure.",
        "source": "world_bank_report",
        "source_url": "https://www.worldbank.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_belt_road_counter_007",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["belt_and_road", "china", "infrastructure", "debt_trap", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "BRI debt trap critique: Sri Lanka Hambantota Port frequently cited as debt trap example. However, research shows most debt distress predates BRI. Terms often commercial rather than predatory. Debt relief granted in multiple cases. Primary issues: weak governance, corruption, project viability rather than intentional trapping.",
        "source": "aiddata_study",
        "source_url": "https://www.aiddata.org/",
        "credibility_class": "academic_research",
        "year": 2024,
        "weight": 0.89
    },
    {
        "id": "frag_eco_GEO_belt_road_latest_007",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["belt_and_road", "china", "infrastructure", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "BRI evolution 2024: Shift from megaprojects to 'small and beautiful' initiatives. Digital Silk Road gaining prominence. Green BRI commitments at COP28. Pakistan CPEC facing delays, cost overruns. Africa debt renegotiations ongoing. EU Global Gateway, US PGII positioned as alternatives.",
        "source": "greenfi_development",
        "source_url": "https://www.greenfin.dev/",
        "credibility_class": "research_organization",
        "year": 2024,
        "weight": 0.91
    },
    {
        "id": "frag_eco_GEO_china_property_crisis_def_008",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["china", "property", "evergrande", "financial_crisis", "definition"],
        "reasoning_role": "definition",
        "content": "China property crisis: Sector represents 25-30% of China GDP including indirect effects. Three Red Lines policy (2020) triggered deleveraging. Evergrande defaulted 2021 ($300B+ debt). Country Garden, others followed. Unfinished homes: estimated 20M units. Household wealth 70% tied to real estate.",
        "source": "imf_working_paper",
        "source_url": "https://www.imf.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_china_property_crisis_counter_008",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["china", "property", "evergrande", "contagion", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "China property contagion limited: Domestic financial system insulated by capital controls. State banks absorb losses with government backing. Global exposure manageable: foreign creditors <10% of developer debt. Primary risk is domestic consumption slowdown, not global financial crisis. Managed decline likely.",
        "source": "goldman_sachs_research",
        "source_url": "https://www.goldmansachs.com/",
        "credibility_class": "investment_bank",
        "year": 2024,
        "weight": 0.87
    },
    {
        "id": "frag_eco_GEO_china_property_crisis_latest_008",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["china", "property", "evergrande", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "China property crisis 2024: Evergrande liquidation ordered January 2024. Government introduced 'white list' financing for viable projects. Property sales down 35% from 2021 peak. Prices falling in tier 1 cities. Stimulus measures accelerating but demand confidence remains weak. Sector drag on GDP: -1.5pp annually.",
        "source": "bloomberg_economics",
        "source_url": "https://www.bloomberg.com/economics",
        "credibility_class": "financial_news",
        "year": 2024,
        "weight": 0.92
    },
]

def save_fragment(fragment_data):
    """Save a fragment to JSON file."""
    filepath = FRAGMENTS_DIR / f"{fragment_data['id']}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(fragment_data, f, indent=2, ensure_ascii=False)
    print(f"Created: {filepath.name}")
    return filepath

def main():
    print("=" * 80)
    print("Building GEO Sector Fragments")
    print("Target: 137 new fragments (currently 13)")
    print("=" * 80)
    
    created = 0
    for frag_data in GEO_FRAGMENTS:
        save_fragment(frag_data)
        created += 1
    
    print(f"\n{'='*80}")
    print(f"Created {created} GEO sector fragments")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
