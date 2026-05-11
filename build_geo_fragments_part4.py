#!/usr/bin/env python3
"""
Build GEO (Geopolitics & Trade Policy) sector fragments - Part 4.
Currency and Monetary Geopolitics topics.
"""

import json
from pathlib import Path

FRAGMENTS_DIR = Path("/workspace/openeyes/fragment_library/fragments")

GEO_FRAGMENTS_PART4 = [
    # ==================== CURRENCY AND MONETARY GEOPOLITICS ====================
    {
        "id": "frag_eco_GEO_dollar_dominance_def_026",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["dollar", "reserve_currency", "hegemony", "definition"],
        "reasoning_role": "definition",
        "content": "Dollar dominance pillars: 58% of global reserves, 88% of FX transactions, 60% of trade invoicing, 50% of international debt. Backed by US economic size, deep liquid markets, rule of law, military power. Exorbitant privilege: ~$100-150B annual seigniorage. System established at Bretton Woods 1944, persisted after Nixon ended gold convertibility 1971.",
        "source": "fed_international_finance",
        "source_url": "https://www.federalreserve.gov/",
        "credibility_class": "central_bank",
        "year": 2024,
        "weight": 0.96
    },
    {
        "id": "frag_eco_GEO_dollar_dominance_counter_026",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["dollar", "reserve_currency", "challenges", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Dollar vulnerability factors: US fiscal deficits unsustainable long-term ($34T debt, 7%+ deficit). Political polarization risks debt ceiling crises. Sanctions weaponization creating incentives for alternatives. Rising US-China decoupling fragments system. Digital currencies could bypass traditional channels. However, no near-term replacement viable.",
        "source": "cfr_dollar_analysis",
        "source_url": "https://www.cfr.org/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.89
    },
    {
        "id": "frag_eco_GEO_dollar_dominance_latest_026",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["dollar", "reserve_currency", "trends", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Dollar trends 2024: DXY index elevated (~103) on rate differentials. Foreign holdings of US Treasuries at $7.6T (China $775B, Japan $1.1T). Dollar funding stress episodes rare but impactful (2019 repo crisis, March 2020). Fed swap lines with 14 central banks provide backstop. De-dollarization narrative overblown but marginal diversification occurring.",
        "source": "treasury TIC_data",
        "source_url": "https://home.treasury.gov/policy-issues/financing-the-government/statistics/treasury-international-capital-tic-system",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_yuan_internationalization_def_027",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["yuan", "renminbi", "internationalization", "china", "definition"],
        "reasoning_role": "definition",
        "content": "Yuan internationalization: China's strategy to increase RMB use in trade, finance, reserves. Launched 2009. Progress: 3% of global payments (SWIFT), 2.6% of reserves (IMF COFER). Mechanisms: Cross-Border Interbank Payment System (CIPS), currency swap lines (40+ countries), offshore centers (Hong Kong, London). Capital account remains partially closed.",
        "source": "pboc_official",
        "source_url": "http://www.pbc.gov.cn/",
        "credibility_class": "central_bank",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_yuan_internationalization_counter_027",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["yuan", "renminbi", "obstacles", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Yuan internationalization obstacles: Capital controls limit fungibility. Rule of law concerns deter long-term holders. Transparency issues with PBOC operations. Geopolitical tensions reduce willingness to depend on China. Property crisis, growth slowdown undermine confidence. Triffin dilemma - China reluctant to run persistent deficits needed for reserve currency status.",
        "source": "peterson_institute_china",
        "source_url": "https://www.piie.com/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.90
    },
    {
        "id": "frag_eco_GEO_yuan_internationalization_latest_027",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["yuan", "renminbi", "trends", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Yuan progress 2024: Record 47% of China's trade settled in RMB (up from 15% in 2015). Russia, Saudi Arabia accepting yuan for energy. Argentina, Pakistan using yuan for bilateral trade. Digital yuan (e-CNY) pilots expanding. CIPS processing 5M+ transactions annually. Still far from reserve currency status but reducing dollar dependency in specific corridors.",
        "source": "swift_rmb_tracker",
        "source_url": "https://www.swift.com/market-insights/rmb-tracker",
        "credibility_class": "financial_infrastructure",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_brics_currency_def_028",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["brics", "alternative_currency", "reserve_system", "definition"],
        "reasoning_role": "definition",
        "content": "BRICS currency proposals: Discussed since 2011, renewed post-2022 sanctions. Concept: common trade settlement currency, potentially backed by commodity basket or gold. 2023 expansion added Egypt, Ethiopia, Iran, UAE (Saudi paused). Combined GDP 37% global (PPP). No concrete mechanism agreed. Technical, political hurdles substantial.",
        "source": "brics_summit_declaration",
        "source_url": "https://brics2023.gov.za/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.91
    },
    {
        "id": "frag_eco_GEO_brics_currency_counter_028",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["brics", "alternative_currency", "feasibility", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "BRICS currency feasibility problems: No fiscal union, no central bank, divergent national interests. China dominates bloc economically (70% of GDP) - other members reluctant to substitute yuan for dollar. Gold backing impractical (insufficient reserves, price volatility). Historical precedent poor (Euro required deep integration). More likely: bilateral local currency arrangements, not unified currency.",
        "source": "goldman_sachs_brics",
        "source_url": "https://www.goldmansachs.com/",
        "credibility_class": "investment_bank",
        "year": 2024,
        "weight": 0.88
    },
    {
        "id": "frag_eco_GEO_brics_currency_latest_028",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["brics", "alternative_currency", "developments", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "BRICS currency developments 2024: New Development Bank approved local currency lending expansion. Contingent Reserve Arrangement ($100B) activated for some members. BRICS Pay digital platform piloting. However, no serious progress on common currency. Members pursuing individual strategies (Russia yuan-heavy, India rupee promotion, UAE dollar peg maintained).",
        "source": "ndb_annual_report",
        "source_url": "https://www.ndb.int/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.90
    },
    {
        "id": "frag_eco_GEO_currency_manipulation_def_029",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["currency_manipulation", "fx_policy", "trade", "definition"],
        "reasoning_role": "definition",
        "content": "Currency manipulation definition: Deliberate intervention to weaken currency for trade advantage. IMF criteria: material current account surplus, persistent one-sided FX intervention (>2% GDP annually), net purchases >6 months. US Treasury monitors major partners semiannually. Label triggers bilateral negotiations, potential countervailing duties.",
        "source": "treasury_fx_report",
        "source_url": "https://home.treasury.gov/policy-issues/international-policy/exchange-rate-policies-and-analysis",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.95
    },
    {
        "id": "frag_eco_GEO_currency_manipulation_counter_029",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["currency_manipulation", "criticism", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Currency manipulation label critique: Politicized application - allies treated differently than adversaries. Intervention often defensive (countering speculative attacks). Current account imbalances reflect savings-investment gaps, not just FX policy. Quantitative easing by Fed, ECB also affects exchange rates. WTO rules don't explicitly cover currency manipulation. Enforcement mechanisms weak.",
        "source": "piie_currency_analysis",
        "source_url": "https://www.piie.com/",
        "credibility_class": "think_tank",
        "year": 2024,
        "weight": 0.87
    },
    {
        "id": "frag_eco_GEO_currency_manipulation_latest_029",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["currency_manipulation", "monitoring_list", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Currency monitoring 2024: Treasury watchlist includes China, Japan, Germany, India, Italy, Korea, Mexico, Singapore, Switzerland, Taiwan, Thailand, Vietnam. No formal manipulator designation since 2020 (China briefly labeled). Yen weakness (150+/USD) drawing scrutiny but BoJ intervention limited. China managing gradual depreciation amid property crisis.",
        "source": "treasury_fx_report_2024",
        "source_url": "https://home.treasury.gov/",
        "credibility_class": "government_agency",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_carry_trade_def_030",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["carry_trade", "emerging_markets", "capital_flows", "definition"],
        "reasoning_role": "definition",
        "content": "Carry trade dynamics: Borrowing in low-yield currencies (JPY, CHF historically) to invest in high-yield EM assets. Creates capital inflow cycles, asset appreciation, credit booms. Unwinds violently when risk sentiment shifts or funding currency strengthens. Classic examples: 1997 Asian Crisis, 2008 EM selloff, 2013 Taper Tantrum. Vulnerability indicator: external debt/FX reserves ratio.",
        "source": "bis_carry_trade_study",
        "source_url": "https://www.bis.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_carry_trade_counter_030",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["carry_trade", "vulnerability", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "EM carry trade resilience improved: Larger FX reserves buffers ($12T aggregate). Reduced USD-denominated debt vs. 1990s. Flexible exchange rates absorb shocks better. Macroprudential tools (capital flow management) deployed proactively. However, frontier markets remain vulnerable. Fed tightening cycle 2022-24 tested but avoided systemic crisis.",
        "source": "iif_em_outlook",
        "source_url": "https://www.iif.com/",
        "credibility_class": "industry_organization",
        "year": 2024,
        "weight": 0.88
    },
    {
        "id": "frag_eco_GEO_carry_trade_latest_030",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["carry_trade", "yen", "unwind", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Carry trade 2024: JPY carry trade estimated $800B-1T. BoJ policy normalization (rate hikes, QT) triggering partial unwind. August 2024 volatility spike as yen strengthened sharply. EM FX under pressure but contained. Turkish lira, Mexican peso, Indonesian rupiah most exposed. Hedging costs rising. Fed pivot timing critical for EM stability.",
        "source": "morgan_stanley_research",
        "source_url": "https://www.morganstanley.com/",
        "credibility_class": "investment_bank",
        "year": 2024,
        "weight": 0.91
    },
    {
        "id": "frag_eco_GEO_capital_controls_def_031",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["capital_controls", "financial_stability", "policy", "definition"],
        "reasoning_role": "definition",
        "content": "Capital controls: Government restrictions on cross-border financial flows. Types: inflow controls (reserve requirements, taxes), outflow controls (approval requirements, holding periods). Goals: prevent overheating, maintain monetary autonomy, stabilize currency. IMF view evolved from opposition to 'institutional view' accepting temporary, targeted use. Effectiveness varies by enforcement capacity.",
        "source": "imf_capital_flows",
        "source_url": "https://www.imf.org/en/Topics/macroeconomic-management-and-financial-stability/capital-flows",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_capital_controls_counter_031",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["capital_controls", "effectiveness", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Capital controls limitations: Leakage through misinvoicing, crypto, informal channels. Deters legitimate investment alongside speculation. Signals policy desperation, can trigger panic. Long-term use creates distortions, corruption. Research shows modest effectiveness for short-term stabilization but doesn't address root causes (fiscal deficits, weak institutions). Market access penalties persist.",
        "source": "nber_capital_controls",
        "source_url": "https://www.nber.org/",
        "credibility_class": "academic_research",
        "year": 2024,
        "weight": 0.89
    },
    {
        "id": "frag_eco_GEO_capital_controls_latest_031",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["capital_controls", "examples", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Capital controls 2024: Nigeria tightened FX restrictions amid naira crisis. Egypt multiple devaluations + controls. Argentina maintains strict cepo cambiario. China's 'macroprudential' measures function as targeted controls. Iceland lifted remaining post-2008 controls. Overall trend: fewer formal controls but increased use of macroprudential measures achieving similar goals.",
        "source": "chinn_itour_index",
        "source_url": "https://web.pdx.edu/~ito/Chinn-Ito_website.htm",
        "credibility_class": "academic_research",
        "year": 2024,
        "weight": 0.91
    },
    {
        "id": "frag_eco_GEO_eurodollar_def_032",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["eurodollar", "offshore_dollars", "shadow_banking", "definition"],
        "reasoning_role": "definition",
        "content": "Eurodollar system: Dollar-denominated deposits held outside US jurisdiction. Originated in Cold War (Soviet dollars in Europe). Now global offshore dollar market estimated $13-20T. Banks engage in maturity transformation without Fed backstop. Repo markets, FX swaps key funding sources. Zoltan Pozsar's 'Bretton Woods III' thesis highlights systemic importance and vulnerabilities.",
        "source": "fed_eurodollar_study",
        "source_url": "https://www.federalreserve.gov/",
        "credibility_class": "central_bank",
        "year": 2024,
        "weight": 0.94
    },
    {
        "id": "frag_eco_GEO_eurodollar_counter_032",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["eurodollar", "stability", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Eurodollar stability improvements: Post-2008 reforms increased bank capital, liquidity buffers. Fed swap lines provide emergency backstop for major central banks. LCR, NSFR requirements reduced maturity mismatch. However, non-bank shadow banking less regulated. 2019 repo crisis showed fragility persists. QE unwinding creates collateral scarcity. System remains prone to runs in stress scenarios.",
        "source": "nyfed_shadow_banking",
        "source_url": "https://www.newyorkfed.org/",
        "credibility_class": "central_bank",
        "year": 2024,
        "weight": 0.88
    },
    {
        "id": "frag_eco_GEO_eurodollar_latest_032",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["eurodollar", "cross_border", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Eurodollar markets 2024: Cross-border claims $13T (BIS data). London still largest center despite Brexit. Asia growing share. Basis swap spreads normalized post-2020 stress. FRA-OIS spread stable. Fed RRP facility absorbing excess liquidity. Regulatory arbitrage continues as banks optimize G-SIB surcharges. CBDC developments could reshape architecture long-term.",
        "source": "bis_locational_banking",
        "source_url": "https://www.bis.org/statistics/bankstats.htm",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.92
    },
    {
        "id": "frag_eco_GEO_dedollarization_def_033",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["dedollarization", "reserve_diversification", "trends", "definition"],
        "reasoning_role": "definition",
        "content": "Dedollarization: Process of reducing dollar dependence in trade, finance, reserves. Drivers: sanctions concerns, geopolitical realignment, desire for monetary autonomy. Manifestations: bilateral local currency agreements, alternative payment systems (CIPS, SPFS), CBDC bridges, gold accumulation. Measured by declining dollar share in reserves, trade invoicing, FX turnover.",
        "source": "imf_dedollarization_paper",
        "source_url": "https://www.imf.org/",
        "credibility_class": "international_organization",
        "year": 2024,
        "weight": 0.93
    },
    {
        "id": "frag_eco_GEO_dedollarization_counter_033",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["dedollarization", "timeline", "counter_argument"],
        "reasoning_role": "counter_argument",
        "content": "Dedollarization timeline reality check: Network effects create extreme inertia. Dollar share declined only 13 percentage points over 24 years (71% to 58%). At this pace, parity with euro would take centuries. Sectors most affected: sanctioned economies (Russia, Iran), commodity trade (partial yuan adoption). Core functions (reserves, vehicle currency, anchor) remain dollar-dominated. Gradual erosion, not sudden collapse.",
        "source": "barry_eichengreen_analysis",
        "source_url": "https://econ.berkeley.edu/",
        "credibility_class": "academic_research",
        "year": 2024,
        "weight": 0.91
    },
    {
        "id": "frag_eco_GEO_dedollarization_latest_033",
        "domain": "economy",
        "subdomain": "GEO",
        "sector": "GEO",
        "tags": ["dedollarization", "gold", "cbdc", "latest_data"],
        "reasoning_role": "latest_data",
        "content": "Dedollarization indicators 2024: Central bank gold purchases record 1,136t (2022), 1,037t (2023). China reserves 2,264t gold. BRICS local currency trade ~30%. mBridge CBDC pilot successful. However, dollar share in reserves stabilized ~58%. Euro flat at 20%. Yuan gains marginal. Sanctions accelerate alternatives but fundamentals (liquidity, institutions) favor dollar persistence.",
        "source": "wgc_gold_demand",
        "source_url": "https://www.gold.org/goldhub/data/gold-demand-trends",
        "credibility_class": "industry_organization",
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
    print("Building GEO Sector Fragments - Part 4 (Currency & Monetary Geopolitics)")
    print("=" * 80)
    
    created = 0
    for frag_data in GEO_FRAGMENTS_PART4:
        save_fragment(frag_data)
        created += 1
    
    print(f"\n{'='*80}")
    print(f"Created {created} GEO sector fragments in Part 4")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
