#!/usr/bin/env python3
"""
Build GEO (Geopolitics & Trade Policy) sector fragments - Part 5.
Regional Economic Blocs topics.
"""

import json
from pathlib import Path

FRAGMENTS_DIR = Path("/workspace/openeyes/fragment_library/fragments")

GEO_FRAGMENTS_PART5 = [
    # ==================== REGIONAL ECONOMIC BLOCS ====================
    {
        "id": "frag_eco_GEO_eu_single_market_def_034",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["eu", "single_market", "regional_integration", "definition"],
        "reasoning_role": "definition",
        "content": "EU Single Market: Four freedoms - goods, services, capital, people move freely. 27 members, 450M consumers, $17T GDP. Customs union eliminates internal tariffs, common external tariff. Harmonized regulations, mutual recognition. Eurozone 20 members share currency. Single Market adds 8-9% to EU GDP vs. no integration scenario.",
        "source": "europa_official",
        "source_url": "https://single-market-economy.ec.europa.eu/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.96
    },
    {
        "id": "frag_eco_GEO_eu_single_market_counter_034",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["eu", "single_market", "limitations", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Single Market incomplete: Services integration lags (only 60% of potential gains realized). Digital single market fragmented by national rules. Energy markets not fully integrated. Labor mobility constrained by language, credential recognition. Brexit demonstrated exit costs but also sovereignty trade-offs. Enlargement fatigue limits expansion.",
        "source": "bruegel_analysis",
        "source_url": "https://www.bruegel.org/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.89
    },
    {
        "id": "frag_eco_GEO_eu_single_market_latest_034",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["eu", "single_market", "developments", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "EU Single Market 2024: Capital Markets Union progressing slowly. Digital Services Act, Digital Markets Act harmonizing tech regulation. CBAM carbon border tax implementing. Ukraine accession negotiations opened. Rule of law disputes with Hungary, Poland partially resolved. NextGenerationEU recovery fund ($800B) driving convergence.",
        "source": "ec_progress_report",
        "source_url": "https://commission.europa.eu/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_asean_def_035",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["asean", "southeast_asia", "regional_bloc", "definition"],
        "reasoning_role": "definition",
        "content": "ASEAN (Association of Southeast Asian Nations): 10 members, 675M people, $3.6T GDP. Founded 1967. ASEAN Economic Community launched 2015. Goals: single market, production base, equitable development. Trade intra-ASEAN ~22%. Consensus-based decision making ('ASEAN Way'). Centrality in regional architecture (ASEAN+3, EAS, ARF).",
        "source": "asean_secretariat",
        "source_url": "https://asean.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_asean_counter_035",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["asean", "integration_limits", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "ASEAN integration limitations: Non-interference principle constrains collective action. Development gaps wide (Singapore GDP/capita 50x Myanmar). NTBs persist despite tariff elimination. Services liberalization limited. South China Sea disputes divide members. Consensus requirement enables obstruction. 'ASEAN centrality' challenged by US-China rivalry.",
        "source": "iseas_yusof_ishak",
        "source_url": "https://www.iseas.edu.sg/",
        "credibility_class": "research_institute",
        "year": 2024,
        "weight": 0.88
    },
    {
        "id": "frag_eco_GEO_asean_latest_035",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["asean", "china_relations", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "ASEAN dynamics 2024: China largest trading partner ($975B annually). RCEP implementation advancing. US IPEF engagement mixed. Myanmar crisis unresolved. Indonesia G20 presidency elevated profile. Vietnam, Philippines balancing China relations. Digital economy framework agreement signed. Supply chain diversification beneficiary (China+1 strategy).",
        "source": "asean_stats",
        "source_url": "https://stats.asean.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_rcep_def_036",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["rcep", "trade_agreement", "asia", "definition"],
        "reasoning_role": "definition",
        "content": "RCEP (Regional Comprehensive Economic Partnership): 15 members (ASEAN+5: China, Japan, Korea, Australia, NZ). Entered force 2022. Covers 30% global GDP, population. Tariff elimination on 90% goods over 20 years. Rules of origin cumulation. Less ambitious than CPTPP on labor, environment, SOEs. First FTA linking China-Japan-Korea.",
        "source": "rcep_official",
        "source_url": "https://rcepsec.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_rcep_counter_036",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["rcep", "impact_assessment", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "RCEP impact limitations: Modest economic gains estimated (+0.2% GDP by 2030 per Peterson Institute). Many tariffs already low under existing FTAs. Exclusions limit coverage. Implementation varies by country. Doesn't address non-tariff barriers significantly. India opted out over manufacturing concerns. More symbolic (Asian integration) than transformative economically.",
        "source": "piie_rcep_analysis",
        "source_url": "https://www.piie.com/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.89
    },
    {
        "id": "frag_eco_GEO_rcep_latest_036",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["rcep", "implementation", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "RCEP implementation 2024: All 15 members ratified. Tariff cuts proceeding on schedule. Rules of origin certificates issued 1M+. South Korea reporting increased exports to China, Japan. Philippines, Thailand utilizing preferences for agriculture. Indonesia concerned about Chinese manufacturing competition. Expansion discussions ongoing (India rejoining?, other applicants).",
        "source": "rcep_secretariat",
        "source_url": "https://rcepsec.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_cptpp_def_037",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["cptpp", "trade_agreement", "high_standard", "definition"],
        "reasoning_role": "definition",
        "content": "CPTPP (Comprehensive and Progressive Agreement for Trans-Pacific Partnership): 12 members after UK accession 2024. Originally TPP (US withdrew 2017). Covers 15% global GDP. High-standard provisions: labor rights, environmental protection, SOE discipline, digital trade, IP. Tariff elimination on 99% goods. Suspension clauses for some TPP provisions.",
        "source": "cptpp_official",
        "source_url": "https://www.mfat.govt.nz/en/trade/free-trade-agreements/free-trade-agreements-in-force/cptpp/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.95
    },
    {
        "id": "frag_eco_GEO_cptpp_counter_037",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["cptpp", "challenges", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "CPTPP challenges: China applied 2021 but faces member skepticism (SOE practices, human rights). Taiwan application creates diplomatic complications. US not returning under Biden. Economic benefits concentrated among larger members. Compliance costs burden smaller economies. Some provisions (investor-state dispute settlement) controversial domestically.",
        "source": "lowy_institute",
        "source_url": "https://www.lowyinstitute.org/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.88
    },
    {
        "id": "frag_eco_GEO_cptpp_latest_037",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["cptpp", "uk_accession", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "CPTPP developments 2024: UK formally acceded July 2024 (first European member). Costa Rica, Uruguay, Ecuador, China, Taiwan seeking membership. Accession process lengthy (UK took 3 years). Members evaluating balance between expansion benefits and dilution risks. Economic impact modest but strategic significance high (rules-setting, Indo-Pacific architecture).",
        "source": "uk_gov_cptpp",
        "source_url": "https://www.gov.uk/government/news/uk-officially-joins-cptpp-trade-deal",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_afcfta_def_038",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["afcfta", "africa", "free_trade", "definition"],
        "reasoning_role": "definition",
        "content": "African Continental Free Trade Area (AfCFTA): 54 signatories, 1.3B people, $3.4T GDP. Launched 2021, trading began 2022. Goal: create single African market. Tariff elimination on 90% goods, services liberalization, free movement protocol. Potential gains: +7% income by 2035 (World Bank). Intra-Africa trade only 15% currently vs. 60% Europe.",
        "source": "afcfta_secretariat",
        "source_url": "https://afcfta.au.int/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_afcfta_counter_038",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["afcfta", "implementation_challenges", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "AfCFTA implementation hurdles: Infrastructure deficits (transport, energy) constrain trade. Overlapping RECs create complexity. Rules of origin negotiations slow. Non-tariff barriers pervasive. Political instability in some regions. Revenue loss concerns (tariffs significant fiscal source). Manufacturing capacity limited - risk of developed country dominance. Guided trade initiative pilot phase ongoing.",
        "source": "uneca_analysis",
        "source_url": "https://unece.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.89
    },
    {
        "id": "frag_eco_GEO_afcfta_latest_038",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["afcfta", "progress", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "AfCFTA progress 2024: 47 countries ratified. Guided Trade Initiative launched with 8 participating countries. Pan-African Payment Settlement System operational. Rules of origin agreed for 88% tariff lines. Free movement protocol slow ratification. Afreximbank $10B facility supporting implementation. Nigeria, South Africa key markets yet to fully engage.",
        "source": "afreximbank",
        "source_url": "https://www.afreximbank.com/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_gcc_def_039",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["gcc", "gulf", "oil", "regional_bloc", "definition"],
        "reasoning_role": "definition",
        "content": "Gulf Cooperation Council (GCC): 6 members (Saudi Arabia, UAE, Kuwait, Qatar, Bahrain, Oman). 60M people, $2T GDP. Established 1981. Customs union 2003, common market 2008. Currency union stalled (Qatar, Oman out). Oil wealth recycling via sovereign wealth funds ($3T+ combined). Vision 2030 diversification strategies across members.",
        "source": "gcc_secretariat",
        "source_url": "https://www.gcc-sg.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_gcc_counter_039",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["gcc", "integration_limits", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "GCC integration constraints: Intra-GCC trade only 8% (low vs. EU 60%). Currency union failed due to sovereignty concerns. 2017-21 Qatar blockade exposed political fragility. Labor markets segmented by nationality. Diversification creating competition rather than complementarity (tourism, finance, logistics). Defense coordination limited despite shared threats.",
        "source": "carnegie_gulf_analysis",
        "source_url": "https://carnegieendowment.org/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.87
    },
    {
        "id": "frag_eco_GEO_gcc_latest_039",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["gcc", "vision_2030", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "GCC developments 2024: Saudi Vision 2030 accelerating (NEOM, PIF $700B+ AUM). UAE diversification advanced (non-oil 70% GDP). Qatar post-blockade relations normalized. Oman pursuing neutral diplomacy. GCC-India FTA negotiations ongoing. Climate commitments (UAE COP28, Saudi Green Initiative). Regional tensions (Iran, Yemen) affecting investment climate.",
        "source": "gcc_statistical_center",
        "source_url": "https://www.gccstat.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.91
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
    print("Building GEO Sector Fragments - Part 5 (Regional Economic Blocs)")
    print("=" * 80)
    
    created = 0
    for frag_data in GEO_FRAGMENTS_PART5:
        save_fragment(frag_data)
        created += 1
    
    print(f"\n{'='*80}")
    print(f"Created {created} GEO sector fragments in Part 5")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
