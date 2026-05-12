#!/usr/bin/env python3
"""
Build GEO (Geopolitics & Trade Policy) sector fragments - Part 3.
Sanctions and Financial Warfare topics.
"""

import json
from pathlib import Path

FRAGMENTS_DIR = Path("/workspace/openeyes/fragment_library/fragments")

GEO_FRAGMENTS_PART3 = [
    # ==================== SANCTIONS AND FINANCIAL WARFARE ====================
    {
        "id": "frag_eco_GEO_economic_sanctions_def_018",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["sanctions", "economic_warfare", "foreign_policy", "definition"],
        "reasoning_role": "definition",
        "content": "Economic sanctions: Coercive measures restricting trade, finance with target countries/entities. Types: comprehensive (country-wide), targeted/Smart (individuals, sectors), secondary (third-country penalties). Primary sanctions apply to domestic entities; secondary extend to foreign firms. Goal: change behavior without military action.",
        "source": "treasury_ofac",
        "source_url": "https://ofac.treasury.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.96
    },
    {
        "id": "frag_eco_GEO_economic_sanctions_counter_018",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["sanctions", "economic_warfare", "effectiveness", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Sanctions effectiveness debate: Hufbauer study found ~34% success rate historically. Limitations: regime consolidation ('rally around flag'), adaptation (sanctions evasion), humanitarian costs hurting civilians not elites. Overuse risks reducing impact. Sanctions work better when multilateral, limited objectives, strong enforcement.",
        "source": "piie_sanctions_study",
        "source_url": "https://www.piie.com/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.90
    },
    {
        "id": "frag_eco_GEO_economic_sanctions_latest_018",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["sanctions", "economic_warfare", "foreign_policy", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Sanctions landscape 2024: US OFAC administers 40+ sanctions programs. Russia most sanctioned country (16,000+ entries). Iran, Syria, North Korea under comprehensive embargoes. Venezuela, Cuba targeted. Trend toward export controls on dual-use tech. Coordination with allies (G7, EU) increasing effectiveness.",
        "source": "castellum_ai_database",
        "source_url": "https://www.castellum.ai/",
        "credibility_class": "research_organization",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_russia_sanctions_def_019",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["russia", "sanctions", "ukraine", "financial_warfare", "definition"],
        "reasoning_role": "definition",
        "content": "Russia sanctions post-2022 invasion: Unprecedented scope. Central Bank assets frozen ($300B+). Major banks removed from SWIFT. Export controls on semiconductors, energy tech. Oil price cap ($60/barrel). Individual sanctions on oligarchs, officials. Energy imports phased out by EU. Most extensive sanctions ever imposed on major economy.",
        "source": "eu_council_sanctions",
        "source_url": "https://www.consilium.europa.eu/en/policies/sanctions/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.96
    },
    {
        "id": "frag_eco_GEO_russia_sanctions_counter_019",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["russia", "sanctions", "effectiveness", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Russia sanctions limitations: Economy contracted only 2.1% in 2022, grew 2023. Oil revenues resilient despite price cap (shadow fleet, G7 enforcement gaps). Import substitution, parallel imports via third countries. Capital controls prevented financial collapse. War economy mobilization offsetting some impacts. Long-term structural damage significant but immediate coercion limited.",
        "source": "yale_school_management",
        "source_url": "https://som.yale.edu/",
        "credibility_class": "academic_research",
        "year": 2024,
        "weight": 0.91
    },
    {
        "id": "frag_eco_GEO_russia_sanctions_latest_019",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["russia", "sanctions", "ukraine", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Russia sanctions 2024 status: 15th package adopted January 2024. Focus on closing loopholes, third-country evasion. LNG restrictions proposed. Shadow banking network exposed. Russian budget deficit widening, inflation elevated. Defense spending 40% of budget. Long-term capacity constraints emerging in energy sector due to tech denial.",
        "source": "kie_institute",
        "source_url": "https://www.kielinstitut.de/",
        "credibility_class": "research_institute",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_swift_exclusion_def_020",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["swift", "payment_systems", "sanctions", "financial_infrastructure", "definition"],
        "reasoning_role": "definition",
        "content": "SWIFT exclusion: Removing banks from Society for Worldwide Interbank Financial Telecommunication messaging system. Belgium-based cooperative, neutral by charter but subject to EU sanctions decisions. 2022 Russia sanctions disconnected 10+ Russian banks. Iran previously excluded 2012-2016. Severely disrupts cross-border payments but not impossible to circumvent.",
        "source": "swift_official",
        "source_url": "https://www.swift.com/",
        "credibility_class": "financial_infrastructure",
        "year": 2024,
        "weight": 0.95
    },
    {
        "id": "frag_eco_GEO_swift_exclusion_counter_020",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["swift", "payment_systems", "alternatives", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "SWIFT alternative systems emerging: Russia's SPFS (System for Transfer of Financial Messages) - 20% domestic share. China's CIPS (Cross-Border Interbank Payment System) - growing but still processes <3% of global transactions. Bilateral arrangements expanding. Fragmentation risk long-term threat to dollar system efficiency.",
        "source": "bis_payment_report",
        "source_url": "https://www.bis.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.89
    },
    {
        "id": "frag_eco_GEO_swift_exclusion_latest_020",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["swift", "payment_systems", "sanctions", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "SWIFT developments 2024: Russia banks using UAE, Turkey, Kazakhstan intermediaries. CIPS volumes up 50% YoY but base small. Digital currency bridges (mBridge) testing CBDC alternatives. SWIFT implementing ISO 20022 migration. Geopolitical weaponization concerns driving diversification efforts by non-Western central banks.",
        "source": "imf_payment_systems",
        "source_url": "https://www.imf.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_asset_freezing_def_021",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["asset_freeze", "sovereign_assets", "sanctions", "legal", "definition"],
        "reasoning_role": "definition",
        "content": "Asset freezing: Blocking access to financial assets held in foreign jurisdictions. Legal basis varies: emergency powers (IEEPA in US), UN Security Council resolutions, EU Common Foreign Security Policy. Sovereign assets present unique challenges - central bank reserves traditionally immune. Russia case unprecedented in scale (~$300B frozen).",
        "source": "cfr_legal_analysis",
        "source_url": "https://www.cfr.org/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_asset_freezing_counter_021",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["asset_freeze", "sovereign_assets", "legal_challenges", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Sovereign asset freeze legal issues: Central bank immunity under customary international law debated. Repurposing frozen assets (as proposed for Ukraine reconstruction) requires legislation, faces legal challenges. Precedent concerns - other countries may reduce Western asset holdings. Euroclear windfall profits tax compromise reached for Ukraine aid.",
        "source": "just_security_law",
        "source_url": "https://www.justsecurity.org/",
        "credibility_class": "legal_analysis",
        "year": 2024,
        "weight": 0.88
    },
    {
        "id": "frag_eco_GEO_asset_freezing_latest_021",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["asset_freeze", "sovereign_assets", "russia", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Russian asset freeze 2024: G7 agreement to use windfall profits (~$3B annually) as loan collateral for Ukraine. US $10B loan announced. EU facing internal legal debates. Russia threatening counter-measures against Western assets in Russia. China watching closely - holds $800B+ in Western reserves. Reserve diversification accelerating globally.",
        "source": "reuters_financial",
        "source_url": "https://www.reuters.com/",
        "credibility_class": "financial_news",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_iran_sanctions_def_022",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["iran", "sanctions", "nuclear", "middle_east", "definition"],
        "reasoning_role": "definition",
        "content": "Iran sanctions regime: Among longest-standing comprehensive sanctions programs. Nuclear-related sanctions intensified 2006-2015, eased under JCPOA (2015), reimposed after US withdrawal (2018). Cover oil exports, banking, shipping, nuclear technology. Secondary sanctions target third-country entities doing business with Iran. 'Maximum pressure' campaign ongoing.",
        "source": "state_department",
        "source_url": "https://www.state.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.95
    },
    {
        "id": "frag_eco_GEO_iran_sanctions_counter_022",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["iran", "sanctions", "effectiveness", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Iran sanctions effectiveness limits: Oil exports recovered to 1.5M bpd via shadow fleet, barter arrangements. China primary buyer. Domestic adaptation through smuggling networks, crypto, hawala. Regime consolidated control over economy via Revolutionary Guard. Humanitarian exemptions insufficient - medicine shortages documented. Nuclear program advanced despite sanctions.",
        "source": "crs_iran_report",
        "source_url": "https://crs.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.91
    },
    {
        "id": "frag_eco_GEO_iran_sanctions_latest_022",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["iran", "sanctions", "nuclear", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Iran sanctions 2024: Enrichment at 60% purity, nearing weapons-grade. Regional tensions elevated following Gaza conflict. Sanctions enforcement tightened on Gulf intermediaries. Snapback mechanism threatened by E3. Economic growth modest (~2%) despite oil revenue recovery. Presidential transition (Pejeshkian) creating policy uncertainty.",
        "source": "isis_nuclear_watch",
        "source_url": "https://isis-online.org/",
        "credibility_class": "research_organization",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_sanctions_evasion_def_023",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["sanctions_evasion", "shell_companies", "trade_based_money_laundering", "definition"],
        "reasoning_role": "definition",
        "content": "Sanctions evasion methods: Shell companies, front entities, flag-hopping vessels, ship-to-ship transfers, falsified documents, trade-based money laundering (over/under-invoicing), crypto assets, barter arrangements. Third-country intermediaries critical. Dark fleet of aging tankers for sanctioned oil. Estimated $50-100B annual evasion globally.",
        "source": "global_witness_report",
        "source_url": "https://www.globalwitness.org/",
        "credibility_class": "ngo_research",
        "year": 2024,
        "weight": 0.91
    },
    {
        "id": "frag_eco_GEO_sanctions_evasion_counter_023",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["sanctions_evasion", "enforcement", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Evasion enforcement challenges: Resource constraints at OFAC, customs agencies. Jurisdictional limitations. Complicity of professional enablers (lawyers, accountants). Technology outpacing regulation. Political will varies by administration. Private sector compliance uneven. Successful cases often require multi-year investigations. Deterrence incomplete.",
        "source": "gaov_enforcement_audit",
        "source_url": "https://www.gao.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.88
    },
    {
        "id": "frag_eco_GEO_sanctions_evasion_latest_023",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["sanctions_evasion", "dark_fleet", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Sanctions evasion 2024: Russian dark fleet 600+ vessels. Iranian oil exports via Malaysia transshipment. Venezuelan gold through UAE. DPRK cyber theft funding weapons programs. US Treasury designating enablers more frequently. Blockchain analytics improving crypto tracking. AI-powered transaction monitoring being deployed by major banks.",
        "source": "rusi_financial_crime",
        "source_url": "https://rusi.org/",
        "credibility_class": "research_institute",
        "year": 2024,
        "weight": 0.90
    },
    {
        "id": "frag_eco_GEO_dollar_weaponization_def_024",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["dollar_hegemony", "weaponization", "reserve_currency", "definition"],
        "reasoning_role": "definition",
        "content": "Dollar weaponization debate: US leveraging dollar's reserve currency status (58% of global reserves, 88% of FX transactions) for foreign policy goals. Access to dollar clearing (CHIPS, Fedwire) becomes coercive tool. Critics argue overuse undermines trust, accelerates dedollarization. Defenders say it's legitimate statecraft, dollar dominance reflects fundamentals.",
        "source": "zoltan_pozsar_analysis",
        "source_url": "https://www.credit-suisse.com/",
        "credibility_class": "investment_bank",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_dollar_weaponization_counter_024",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["dollar_hegemony", "weaponization", "dedollarization", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Dollar dominance persistence factors: Network effects, deep liquid markets, rule of law, no viable alternative. Euro fragmented, yuan not fully convertible, gold impractical for large transactions. Weaponization concerns real but alternatives worse. BRICS currency proposals lack detail. Dedollarization rhetoric exceeds reality. TINA - There Is No Alternative.",
        "source": "fed_international_finance",
        "source_url": "https://www.federalreserve.gov/",
        "credibility_class": "central_bank",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_dollar_weaponization_latest_024",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["dollar_hegemony", "dedollarization", "reserve_currency", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Dollar status 2024: Share of reserves declined modestly to 58% from 71% (2000). Still dominant in trade invoicing, FX, sovereign debt. Sanctions driving diversification at margins - central banks buying gold (record 2022-23). Bilocal currency arrangements expanding but small scale. Digital dollar projects advancing. Exorbitant privilege persists.",
        "source": "imf_cofER_data",
        "source_url": "https://www.imf.org/external/np/sta/cofer/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_sovereign_default_def_025",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["sovereign_debt", "default", "restructuring", "creditors", "definition"],
        "reasoning_role": "definition",
        "content": "Sovereign default process: Failure to meet debt service obligations. Triggers: economic shock, political crisis, debt overhang. Restructuring involves creditor negotiations, haircuts, maturity extensions. Paris Club (official creditors), London Club (commercial banks), bondholders. Collective action clauses prevent holdouts. IMF typically involved in program design.",
        "source": "paris_club_official",
        "source_url": "http://www.clubdeparis.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_sovereign_default_counter_025",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["sovereign_debt", "default", "creditor_coordination", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Sovereign restructuring challenges: Creditor fragmentation complicates deals - bilateral (China), multilateral, private bondholders have different interests. China not Paris Club member, opaque lending terms. Vulture funds litigate for full repayment. Lengthy negotiations (Argentina 15 years). Moral hazard vs. debt sustainability tension. Orderly resolution mechanisms inadequate.",
        "source": "odci_sovereign_debt",
        "source_url": "https://www.odci.org/",
        "credibility_class": "research_organization",
        "year": 2024,
        "weight": 0.89
    },
    {
        "id": "frag_eco_GEO_sovereign_default_latest_025",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["sovereign_debt", "default", "crisis", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Sovereign debt crises 2024: Sri Lanka defaulted 2022, restructuring ongoing. Ghana, Zambia in process. Pakistan borderline. Debt distress in 60+ developing countries. Interest rate hikes, strong dollar, COVID aftermath drivers. China debt relief criticized as insufficient. Common Framework proving slow. Default wave risk elevated if recession hits developed economies.",
        "source": "world_bank_ids",
        "source_url": "https://www.worldbank.org/en/data/interactive/2024/01/18/international-debt-report-2024",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.93
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
    print("Building GEO Sector Fragments - Part 3 (Sanctions & Financial Warfare)")
    print("=" * 80)
    
    created = 0
    for frag_data in GEO_FRAGMENTS_PART3:
        save_fragment(frag_data)
        created += 1
    
    print(f"\n{'='*80}")
    print(f"Created {created} GEO sector fragments in Part 3")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
