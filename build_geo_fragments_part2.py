#!/usr/bin/env python3
"""
Build GEO (Geopolitics & Trade Policy) sector fragments - Part 2.
Global Trade Architecture topics.
"""

import json
from pathlib import Path

FRAGMENTS_DIR = Path("/workspace/openeyes/fragment_library/fragments")

GEO_FRAGMENTS_PART2 = [
    # ==================== GLOBAL TRADE ARCHITECTURE ====================
    {
        "id": "frag_eco_GEO_wto_function_def_009",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["wto", "trade_organization", "dispute_resolution", "definition"],
        "reasoning_role": "definition",
        "content": "WTO (World Trade Organization): Established 1995, 164 members. Core functions: administer trade agreements, forum for negotiations, dispute settlement, monitoring national trade policies. Most-favored-nation and national treatment are founding principles. Budget: ~$200M annually.",
        "source": "wto_official",
        "source_url": "https://www.wto.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.96
    },
    {
        "id": "frag_eco_GEO_wto_dispute_def_010",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["wto", "dispute_settlement", "trade_law", "definition"],
        "reasoning_role": "definition",
        "content": "WTO Dispute Settlement Mechanism: Three stages - consultations, panel ruling, Appellate Body review. Rulings binding; non-compliance allows authorized retaliation. Appellate Body paralyzed since 2019 due to US blocking appointments. Alternative MPIA established by EU, Canada, others.",
        "source": "wto_legal_texts",
        "source_url": "https://www.wto.org/english/tratop_e/dispu_e.htm",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.95
    },
    {
        "id": "frag_eco_GEO_wto_dysfunction_counter_010",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["wto", "dispute_settlement", "trade_law", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "WTO dysfunction critique: Appellate Body crisis reflects deeper issues. Consensus requirement enables single-member obstruction. Rules haven't updated for digital trade, state capitalism, climate measures. Major powers bypass WTO via regional agreements. Reform prospects dim without US-China cooperation.",
        "source": "piie_analysis",
        "source_url": "https://www.piie.com/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.90
    },
    {
        "id": "frag_eco_GEO_wto_latest_010",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["wto", "dispute_settlement", "trade_law", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "WTO status 2024: MC13 (Abu Dhabi) produced limited outcomes. Fisheries subsidies agreement entered into force. E-commerce moratorium extended. Appellate Body remains inactive. 60+ disputes pending. Plurilateral initiatives on investment facilitation, services regulation progressing outside consensus framework.",
        "source": "wto_news",
        "source_url": "https://www.wto.org/english/news_e/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_bilateral_trade_def_011",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["bilateral_trade", "fta", "trade_agreements", "definition"],
        "reasoning_role": "definition",
        "content": "Bilateral trade agreements: Treaties between two countries reducing trade barriers. Typical coverage: tariff elimination schedules, rules of origin, services, investment, IP, labor/environmental standards. Examples: USMCA, EU-Japan EPA, Australia-UK FTA. Average negotiation time: 3-7 years.",
        "source": "ustr_government",
        "source_url": "https://ustr.gov/trade-agreements/free-trade-agreements",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_bilateral_trade_counter_011",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["bilateral_trade", "fta", "trade_agreements", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Bilateral FTA limitations: Spaghetti bowl effect - overlapping rules increase compliance costs. Trade diversion from more efficient non-members. Small economies face power asymmetry in negotiations. Enforcement mechanisms weak. Studies show modest GDP impacts (+0.5-2% typically), concentrated in specific sectors.",
        "source": "world_bank_study",
        "source_url": "https://www.worldbank.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.88
    },
    {
        "id": "frag_eco_GEO_bilateral_trade_latest_011",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["bilateral_trade", "fta", "trade_agreements", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Bilateral FTAs 2024: 355 RTAs notified to WTO. Trend toward 'deep' agreements covering digital trade, SOEs, regulatory coherence. UK pursuing post-Brexit deals (CPTPP accession, India negotiations). US focusing on IPEF (non-traditional framework). Africa's AfCFTA implementation accelerating.",
        "source": "wto_rta_database",
        "source_url": "https://rtais.wto.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_reshoring_friendshoring_def_012",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["reshoring", "friendshoring", "supply_chain", "definition"],
        "reasoning_role": "definition",
        "content": "Reshoring vs friendshoring: Reshoring brings production back to home country. Friendshoring relocates to politically aligned nations. Drivers: supply chain resilience, geopolitical risk, ESG concerns. IMF estimates friendshoring could reduce long-term output by 0.2-7% depending on scenario.",
        "source": "imf_working_paper",
        "source_url": "https://www.imf.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_reshoring_friendshoring_counter_012",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["reshoring", "friendshoring", "supply_chain", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Reshoring economics critique: Labor cost differentials often outweigh resilience benefits. Automation reduces labor arbitrage but increases capital intensity. Friendshoring pool limited - few countries combine scale, stability, low costs. Mexico, Vietnam capacity constraints emerging. Consumer prices likely to rise.",
        "source": "mckinsey_global_institute",
        "source_url": "https://www.mckinsey.com/mgi",
        "credibility_class": "consulting_research",
        "year": 2024,
        "weight": 0.87
    },
    {
        "id": "frag_eco_GEO_reshoring_friendshoring_latest_012",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["reshoring", "friendshoring", "supply_chain", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Reshoring trends 2024: US manufacturing construction up 80% since 2021 (CHIPS Act driven). Nearshoring to Mexico at record levels - surpassed China as top US trading partner. Vietnam, India gaining share. However, China still accounts for 30% of global manufacturing value-add. Full decoupling economically unfeasible.",
        "source": "census_bureau",
        "source_url": "https://www.census.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_supply_chain_concentration_def_013",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["supply_chain", "concentration_risk", "resilience", "definition"],
        "reasoning_role": "definition",
        "content": "Supply chain concentration risk: Critical dependencies on single sources or geographies. Examples: Taiwan semiconductors (90%+ advanced nodes), China rare earths (60% mining, 85% processing), India pharmaceuticals (20%+ generic drugs). COVID exposed vulnerabilities, triggering policy responses globally.",
        "source": "white_house_supply_chain_report",
        "source_url": "https://www.whitehouse.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.95
    },
    {
        "id": "frag_eco_GEO_supply_chain_concentration_counter_013",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["supply_chain", "concentration_risk", "resilience", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Concentration risk mitigation limits: Diversification costly and slow. Some concentration reflects genuine comparative advantage (geology, cluster effects). Redundancy conflicts with efficiency mandates. SMEs lack resources for multi-sourcing. Strategic stockpiles expensive. Complete supply chain sovereignty unrealistic for most economies.",
        "source": "bcg_supply_chain_analysis",
        "source_url": "https://www.bcg.com/",
        "credibility_class": "consulting_firm",
        "year": 2024,
        "weight": 0.86
    },
    {
        "id": "frag_eco_GEO_supply_chain_concentration_latest_013",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["supply_chain", "concentration_risk", "resilience", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Supply chain policy 2024: US CHIPS Act, IRA driving semiconductor, battery reshoring. EU Critical Raw Materials Act targeting 10% domestic extraction, 40% processing by 2030. Japan subsidizing TSMC fab. India PLI schemes attracting electronics assembly. Progress measurable but concentration remains high in critical areas.",
        "source": "csis_supply_chain_report",
        "source_url": "https://www.csis.org/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_container_shipping_def_014",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["container_shipping", "logistics", "trade_infrastructure", "definition"],
        "reasoning_role": "definition",
        "content": "Container shipping: Backbone of global trade - 90% of goods by volume. Three alliances control 80%+ capacity. Rate volatility extreme: Shanghai-LA rates ranged from $1,500 to $20,000+ per FEU during COVID. Bottlenecks at ports, canals (Suez, Panama) create cascading delays. Fleet orderbook at record highs 2024.",
        "source": "unctad_review",
        "source_url": "https://unctad.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_container_shipping_counter_014",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["container_shipping", "logistics", "rate_volatility", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Shipping rate volatility drivers: Pandemic disruptions were exceptional, not structural. Overcapacity returning as new vessels delivered. Rate normalization expected 2024-25. Alliance system maintains pricing power but faces antitrust scrutiny. Port automation, canal expansions reducing bottleneck risks long-term.",
        "source": "drewry_shipping_analytics",
        "source_url": "https://www.drewry.co.uk/",
        "credibility_class": "industry_analysis",
        "year": 2024,
        "weight": 0.88
    },
    {
        "id": "frag_eco_GEO_container_shipping_latest_014",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["container_shipping", "logistics", "rate_volatility", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Container shipping 2024: Red Sea attacks forcing Cape rerouting, adding 10-14 days transit time. Rates up 150-200% on Asia-Europe routes. Panama Canal drought restrictions easing. New vessel deliveries creating overcapacity concerns. Port strikes avoided at US East Coast. Digitalization (bill of lading) progressing slowly.",
        "source": "lloyds_list",
        "source_url": "https://lloydslist.maritimeintelligence.informa.com/",
        "credibility_class": "industry_publication",
        "year": 2024,
        "weight": 0.91
    },
    {
        "id": "frag_eco_GEO_trade_finance_def_015",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["trade_finance", "letters_of_credit", "global_trade", "definition"],
        "reasoning_role": "definition",
        "content": "Trade finance: Instruments facilitating international commerce. Letters of credit (LCs) guarantee payment upon document presentation. Banker's acceptances, export credit agencies, factoring also used. Trade finance gap: $2.5T annually, concentrated in SMEs, developing countries. ICC estimates 80-90% of trade uses some form of financing.",
        "source": "icc_banking_commission",
        "source_url": "https://iccwbo.org/",
        "credibility_class": "industry_organization",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_trade_finance_counter_015",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["trade_finance", "letters_of_credit", "global_trade", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Trade finance gap persistence: AML/KYC regulations increased compliance costs, de-risking reduced correspondent banking relationships. Digital solutions (blockchain LCs) slow adoption due to legal uncertainty, network effects. Export credit agencies fill gaps but introduce political considerations. SME access remains constrained.",
        "source": "adb_trade_finance_report",
        "source_url": "https://www.adb.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.89
    },
    {
        "id": "frag_eco_GEO_trade_finance_latest_015",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["trade_finance", "letters_of_credit", "global_trade", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Trade finance 2024: Digital LC platforms (Contour, Komgo) gaining traction but still <5% market share. Sanctions compliance complexity increasing (Russia, Iran). Interest rate environment raising financing costs. Green trade finance emerging - sustainability-linked LCs. Supply chain finance volumes recovering post-COVID.",
        "source": "baft_annual_report",
        "source_url": "https://www.baft.org/",
        "credibility_class": "industry_organization",
        "year": 2024,
        "weight": 0.91
    },
    {
        "id": "frag_eco_GEO_mfn_status_def_016",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["mfN", "most_favored_nation", "wto", "trade_policy", "definition"],
        "reasoning_role": "definition",
        "content": "Most-Favored-Nation (MFN) status: WTO principle requiring members extend equal tariff treatment to all other members. Exceptions: FTAs, GSP preferences for developing countries, national security. Revocation rare - historically used against Soviet Union (Jackson-Vanik), Myanmar. US revoked Russia MFN (PNTR) status in 2022.",
        "source": "wto_legal_texts",
        "source_url": "https://www.wto.org/english/tratop_e/region_e/region_e.htm",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.95
    },
    {
        "id": "frag_eco_GEO_mfn_status_counter_016",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["mfN", "most_favored_nation", "wto", "trade_policy", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "MFN erosion critique: Proliferation of FTAs creates discriminatory trading system. National security exceptions increasingly abused for economic protectionism. De facto MFN violations through non-tariff barriers common. Developing countries disadvantaged by preference erosion as tariffs decline. System moving toward managed trade.",
        "source": "cfr_trade_analysis",
        "source_url": "https://www.cfr.org/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.88
    },
    {
        "id": "frag_eco_GEO_mfn_status_latest_016",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["mfN", "most_favored_nation", "wto", "trade_policy", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "MFN status developments 2024: Russia faces highest tariff rates among major economies post-MFN revocation. US-China trade operates under MFN despite tensions (PNTR granted 2000). UK applying WTO terms post-Brexit while negotiating FTAs. Debate continues over whether China should retain MFN given state capitalist practices.",
        "source": "peterson_institute",
        "source_url": "https://www.piie.com/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_free_trade_zones_def_017",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["ftz", "free_trade_zone", "special_economic_zone", "definition"],
        "reasoning_role": "definition",
        "content": "Free Trade Zones (FTZs): Designated areas with reduced customs barriers, taxes, regulations to attract investment. Types: export processing zones, bonded logistics parks, comprehensive pilot zones. Global count: 5,400+ across 147 countries. China's SEZs pioneered model. US has 195 active FTZs.",
        "source": "world_bank_ftz_study",
        "source_url": "https://www.worldbank.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_free_trade_zones_counter_017",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["ftz", "free_trade_zone", "special_economic_zone", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "FTZ effectiveness debate: Mixed results - success depends on location, governance, linkages to domestic economy. Many zones become enclaves with limited spillover. Race-to-bottom tax competition erodes revenue. Labor rights concerns in some zones. Recent trend toward integration with national reforms rather than isolated preferential treatment.",
        "source": "unctad_investment_report",
        "source_url": "https://unctad.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.87
    },
    {
        "id": "frag_eco_GEO_free_trade_zones_latest_017",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["ftz", "free_trade_zone", "special_economic_zone", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "FTZ evolution 2024: UAE leading with 40+ zones (Dubai Multi Commodities Centre, ADGM). Saudi Arabia establishing King Abdullah Economic City. China upgrading to free trade pilot zones with broader reforms. US FTZ Board approving more manufacturing activities. Digital FTZs emerging with virtual boundaries.",
        "source": "fias_world_bank",
        "source_url": "https://www.fias.net/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.90
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
    print("Building GEO Sector Fragments - Part 2 (Global Trade Architecture)")
    print("=" * 80)
    
    created = 0
    for frag_data in GEO_FRAGMENTS_PART2:
        save_fragment(frag_data)
        created += 1
    
    print(f"\n{'='*80}")
    print(f"Created {created} GEO sector fragments in Part 2")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
