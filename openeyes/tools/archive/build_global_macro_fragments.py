"""
OpenEyes Fragment Generator: Task 1.4 - Central Bank & Global Macro
Generates 57 fragments (19 topics x 3 roles) for global macroeconomics.
"""

import os
import json
from datetime import datetime

# Configuration
OUTPUT_DIR = "openeyes/fragment_library/fragments"
DOMAIN = "finance"
SUBDOMAIN = "global_macro"
YEAR = 2024

# Trusted Sources for Global Macro
SOURCES = {
    "ecb": {"url": "https://www.ecb.europa.eu/home/html/index.en.html", "cred": "government_source", "weight": 0.92},
    "boj": {"url": "https://www.boj.or.jp/en/", "cred": "government_source", "weight": 0.90},
    "pboc": {"url": "http://www.pbc.gov.cn/english/", "cred": "government_source", "weight": 0.88},
    "boe": {"url": "https://www.bankofengland.co.uk/", "cred": "government_source", "weight": 0.92},
    "bis": {"url": "https://www.bis.org/", "cred": "peer_reviewed_study", "weight": 0.94},
    "imf": {"url": "https://www.imf.org/", "cred": "government_source", "weight": 0.93},
    "worldbank": {"url": "https://www.worldbank.org/", "cred": "government_source", "weight": 0.93},
    "fed": {"url": "https://www.federalreserve.gov/", "cred": "government_source", "weight": 0.95},
}

# Canonical Tags Subset for Macro
MACRO_TAGS = [
    "macro", "monetary_policy", "central_bank", "fed", "ecb", "boj", "pboc", "bank_of_england",
    "currency", "exchange_rate", "forex", "dollar", "emerging_markets", "sovereign_debt",
    "global_trade", "commodities", "oil", "geopolitical_risk", "recession", "inflation",
    "definition", "counter_argument", "latest_data", "warning", "first_line"
]

TOPICS = [
    {
        "id": "ecb_mandate",
        "title": "ECB Mandate and Structure",
        "source_key": "ecb",
        "tags": ["ecb", "monetary_policy", "eurozone"],
        "content_def": "The European Central Bank (ECB) primary mandate is price stability, defined as inflation below but close to 2% over the medium term. Unlike the Fed's dual mandate, the ECB focuses primarily on inflation, with secondary support for EU economic policies. Structure includes the Governing Council, Executive Board, and General Council.",
        "content_counter": "Critics argue the ECB's strict inflation focus ignores employment disparities across the Eurozone. The 'one size fits all' monetary policy often conflicts with divergent fiscal needs of member states (e.g., Germany vs. Greece), limiting effectiveness during asymmetric shocks.",
        "content_data": "As of 2024, the ECB balance sheet stands at approx €7.5T. Recent rate hikes brought deposit facility rate to 4.0% to combat post-pandemic inflation. Quantitative Tightening (QT) began in 2023, reducing APP portfolio by €15bn/month."
    },
    {
        "id": "boj_ycc",
        "title": "Bank of Japan Yield Curve Control",
        "source_key": "boj",
        "tags": ["boj", "yield_curve", "monetary_policy", "japan"],
        "content_def": "Yield Curve Control (YCC) is a monetary policy where the central bank targets specific yields on government bonds (e.g., 10-year JGB at 0%) rather than just quantity. The BoJ buys/sells unlimited bonds to maintain the target, keeping borrowing costs ultra-low to stimulate inflation and growth.",
        "content_counter": "YCC distorts market price discovery and reduces liquidity in the JGB market. It traps the BoJ in a corner: exiting YCC risks spiking debt servicing costs for Japan's 260% debt-to-GDP ratio, while continuing it fuels yen depreciation and imported inflation.",
        "content_data": "In Dec 2023/Jan 2024, BoJ adjusted YCC band to +/- 0.5% then effectively abandoned strict caps, allowing 10y yields to rise above 1%. Net sales of JGBs turned negative for first time in years, signaling potential policy normalization."
    },
    {
        "id": "pboc_ops",
        "title": "PBOC Operations and Yuan Management",
        "source_key": "pboc",
        "tags": ["pboc", "china", "currency", "monetary_policy"],
        "content_def": "The People's Bank of China (PBOC) uses a mix of reserve requirement ratios (RRR), MLF (Medium-term Lending Facility), and daily yuan fixing (USDCNY) to manage liquidity and exchange rates. Unlike Western QE, PBOC often injects liquidity via targeted lending to specific sectors.",
        "content_counter": "PBOC policy is often subordinated to state industrial policy rather than pure macro stability. Heavy intervention in the forex market to prevent rapid depreciation creates tension with US Treasury and limits capital account liberalization efforts.",
        "content_data": "2023-2024 saw multiple RRR cuts totaling 100bps to support property sector. PBOC balance sheet expanded to $6.2T. Yuan fixed near 7.1-7.2 per USD despite pressure, using state bank flows to stabilize currency."
    },
    {
        "id": "boe_mandate",
        "title": "Bank of England Mandate and Brexit Impact",
        "source_key": "boe",
        "tags": ["bank_of_england", "uk", "monetary_policy", "brexit"],
        "content_def": "BoE mandate is CPI inflation target of 2%. Post-Brexit, BoE faces unique challenges: reduced labor mobility causing wage stickiness, new trade frictions impacting supply chains, and sterling volatility affecting import prices independently of domestic demand.",
        "content_counter": "Brexit structural impacts make traditional inflation modeling difficult. BoE's tightrope walk between curbing inflation and avoiding deep recession is harder than Fed/ECB due to UK's specific energy dependence and post-Brexit productivity stagnation.",
        "content_data": "BoE raised rates to 5.25% in 2023, highest since 2008. UK inflation peaked at 11.1% in late 2022. GDP growth remains stagnant (~0%), raising stagflation fears. Gilts market volatility in 2022 (LDI crisis) forced emergency BoE intervention."
    },
    {
        "id": "em_central_banks",
        "title": "Emerging Market Central Banks",
        "source_key": "imf",
        "tags": ["emerging_markets", "central_bank", "inflation", "currency"],
        "content_def": "EM central banks often face 'impossible trinity': cannot simultaneously have free capital flow, fixed exchange rate, and independent monetary policy. When Fed hikes, EMs often must follow to prevent capital flight and currency collapse, importing recession.",
        "content_counter": "Not all EMs are equal. Those with low external debt in local currency (e.g., Mexico, Brazil recently) have more autonomy than those with high USD debt (e.g., Argentina, Turkey). Premature tightening can crush growth without stabilizing currency if fundamentals are weak.",
        "content_data": "2022-2023 cycle saw EMs front-run Fed: Brazil/South Africa hiked earlier. Result: Many EM currencies stabilized or appreciated vs USD in late 2023 despite high US rates. Inflation in EMs averaged 8% in 2023, down from 12% peak."
    },
    {
        "id": "currency_wars",
        "title": "Currency Wars and Competitive Devaluation",
        "source_key": "bis",
        "tags": ["forex", "currency", "geopolitical_risk", "trade"],
        "content_def": "Currency wars occur when countries competitively devalue currencies to boost exports. Mechanisms include direct FX intervention, verbal jawboning, or monetary easing. Historically seen in 1930s Great Depression and 2010-2015 post-GFC era.",
        "content_counter": "Modern 'currency war' rhetoric often oversimplifies. Most major economies now prefer stable currencies for trade certainty. Aggressive devaluation risks retaliation, capital controls, and loss of reserve status trust. True competitive devaluation is rare today.",
        "content_data": "2023-2024: Japan intervened to support Yen (spent ~$60bn). China allowed gradual depreciation but avoided crash. US Treasury 'monitoring list' includes Japan, Switzerland, Vietnam. No formal 'war' but tensions over industrial subsidies impacting real exchange rates."
    },
    {
        "id": "carry_trade",
        "title": "Global Carry Trade Mechanics",
        "source_key": "bis",
        "tags": ["forex", "leverage", "risk_management", "japan"],
        "content_def": "Carry trade involves borrowing in low-yield currency (e.g., JPY, CHF) to invest in high-yield assets (e.g., USD bonds, EM equities). Profit = interest rate differential. Unwinds violently when funding currency appreciates or volatility spikes (VIX > 20).",
        "content_counter": "Carry trades create hidden systemic leverage. When unwound, they cause correlated asset crashes across unrelated markets (equities, crypto, EM bonds). Risk models often underestimate correlation during unwind events, leading to liquidity gaps.",
        "content_data": "Aug 2024 carry trade unwind triggered by BoJ hike + weak US jobs data caused Nikkei -12% day, VIX spike to 65, BTC drop. Estimated $1T+ leveraged positions forced to deleverage rapidly."
    },
    {
        "id": "dollar_milkshake",
        "title": "Dollar Milkshake Theory",
        "source_key": "fed",
        "tags": ["dollar", "macro", "liquidity", "counter_argument"],
        "content_def": "Theory posits that global dollar shortage forces capital repatriation to US regardless of US fundamentals. As global economy weakens, dollar strengthens because world needs dollars to service debt, creating a feedback loop sucking liquidity into US Treasuries.",
        "content_counter": "Critics argue theory ignores US twin deficits and potential loss of confidence. If US fiscal path becomes unsustainable, foreign buyers may demand higher premiums or diversify, breaking the milkshake loop. Multipolar reserve system could dilute effect.",
        "content_data": "DXY hit 114 in 2022, retreated to 102 in 2023, rebounded to 106 in 2024. US share of global reserves declined slowly (58% -> 54% over decade) but no viable alternative (Euro fragmentation, Gold limited, Crypto nascent)."
    },
    {
        "id": "global_debt",
        "title": "Global Debt Levels",
        "source_key": "imf",
        "tags": ["sovereign_debt", "macro", "risk_management"],
        "content_def": "Global debt reached $307T in 2023 (336% of global GDP). Breakdown: Governments $93T, Corporates $120T, Households $94T. High debt limits fiscal response to crises and increases sensitivity to interest rate changes.",
        "content_counter": "Debt sustainability depends on r-g differential (interest rate minus growth). If nominal growth > interest rates, debt burdens shrink organically. Japan sustains 260% debt because JGB yields < nominal GDP growth. Context matters more than absolute level.",
        "content_data": "2023-2024 rate hikes increased debt servicing costs sharply. US interest payments exceeded $1T annually. Emerging markets debt distress rose: 60% of low-income countries in/near debt distress (Zambia, Ghana, Pakistan restructurings)."
    },
    {
        "id": "sovereign_crisis",
        "title": "Sovereign Debt Crisis Patterns",
        "source_key": "worldbank",
        "tags": ["sovereign_debt", "emerging_markets", "warning"],
        "content_def": "Sovereign crises typically follow: 1) External shock (commodity drop, rate hike), 2) Currency depreciation, 3) Inability to roll over USD debt, 4) Default or IMF bailout. Triggers include sudden stops in capital flows and banking sector fragility.",
        "content_counter": "Not all high-debt nations crisis. Domestic debt in local currency allows inflation/debasement escape valve (UK, Japan). Crises concentrate in EMs with foreign-currency debt. 'Original Sin' hypothesis: inability to borrow abroad in own currency is root cause.",
        "content_data": "Recent defaults/restructurings: Sri Lanka (2022), Ghana (2022), Zambia (2020), Lebanon (2020). Argentina in perpetual restructuring cycle. Europe 2010-2012 crisis resolved via ECB 'whatever it takes' backstop, not fiscal union."
    },
    {
        "id": "reserve_currency",
        "title": "Reserve Currency Status",
        "source_key": "imf",
        "tags": ["dollar", "macro", "global_trade"],
        "content_def": "Reserve currency status means central banks hold asset for international transactions and stability. Benefits: Seigniorage, lower borrowing costs, sanction power. Costs: 'Exorbitant privilege' leads to strong currency hurting exporters (Triffin Dilemma).",
        "content_counter": "Network effects make reserve status sticky. Despite US sanctions weaponization, no single alternative exists. Euro lacks fiscal union, Yuan has capital controls, Gold lacks yield/settlement speed. Fragmentation likely (blocs) rather than replacement.",
        "content_data": "USD share of reserves: 58% (2024). EUR: 20%. CNY: 2.3% (growing slowly). Gold holdings by central banks hit record highs in 2022-2023 (China, Poland, Singapore buying) as diversification hedge."
    },
    {
        "id": "de_dollarization",
        "title": "De-dollarization Trends",
        "source_key": "bis",
        "tags": ["dollar", "geopolitical_risk", "currency"],
        "content_def": "De-dollarization refers to reducing USD dependence in trade settlement and reserves. Drivers: US sanctions (Russia, Iran), desire for strategic autonomy. Methods: Bilateral local currency swaps, CBDC bridges, gold accumulation.",
        "content_counter": "Hype exceeds reality. USD share of trade invoicing remains ~50% (vs 15% US trade share). Network effects, liquidity depth, and rule of law make USD irreplaceable short-term. 'De-dollarization' often just diversification at margins, not systemic shift.",
        "content_data": "BRICS trade in local currencies rose to 35% (from 20% in 2015). Russia-China trade 90% non-USD. However, global SWIFT USD share remains >40%. Digital Yuan pilot expanded but volume negligible vs USD CHIPS system."
    },
    {
        "id": "global_trade_flows",
        "title": "Global Trade Flows Impact",
        "source_key": "worldbank",
        "tags": ["global_trade", "macro", "currency"],
        "content_def": "Trade flows drive currency demand and capital allocation. Surplus nations (China, Germany) accumulate reserves/claims; deficit nations (US, UK) consume and issue liabilities. Shifts in supply chains (friend-shoring) alter long-term FX and bond flows.",
        "content_counter": "Trade balances matter less in floating fiat regime with deep capital markets. Capital flows (investment) dominate FX moves, not trade balances. US runs deficit but attracts equity/VC inflows, offsetting trade drag. Services surplus (US) also undercounted.",
        "content_data": "2023-2024: China exports shifted to EVs/batteries/solar ('New Three'). EU imposed tariffs. Mexico surpassed China as top US trading partner. Red Sea disruptions added freight costs, delaying goods. Global trade volume growth slowed to 1.5% (below GDP)."}
]

# Additional Topics (Continued to reach 19)
EXTRA_TOPICS = [
    {
        "id": "geopolitical_premium",
        "title": "Geopolitical Risk Premium",
        "source_key": "imf",
        "tags": ["geopolitical_risk", "oil", "macro"],
        "content_def": "Geopolitical risk premium is the extra return investors demand for holding assets exposed to conflict zones or sanctions risk. Manifests in oil prices, defense stocks, gold, and sovereign spreads. Hard to quantify but visible in volatility spikes.",
        "content_counter": "Markets often 'look through' geopolitical noise if supply chains remain intact. Premium decays quickly unless physical disruption occurs (e.g., Strait of Hormuz closure). Overestimating geopolitical risk leads to missed opportunities in beaten-down assets.",
        "content_data": "2022 Ukraine invasion: Brent spiked to $139, settled to $85 as Russian oil found buyers. 2023 Israel-Hamas: Muted oil reaction ($90 range) due to ample spare capacity. 2024 Red Sea attacks: Freight rates up 300%, oil impact contained."
    },
    {
        "id": "oil_markets",
        "title": "Oil Price Dynamics",
        "source_key": "worldbank",
        "tags": ["oil", "commodities", "inflation"],
        "content_def": "Oil prices driven by OPEC+ supply management, global demand (China/US), and inventory levels. $80-90/barrel is 'Goldilocks' zone: profitable for producers, not inflationary for consumers. Shale revolution made US swing producer, capping upside.",
        "content_counter": "Energy transition creates 'underinvestment trap'. Capex discipline prevents supply surge even at high prices, risking spikes if demand surprises. Conversely, EV adoption acceleration could strand assets faster than models predict, crashing prices.",
        "content_data": "2024 Brent avg $82. OPEC+ extended voluntary cuts (2.2M bpd). US production record 13.3M bpd. Strategic Petroleum Reserve (SPR) refilling at $70-75 range. China demand growth slowed to 1% vs historical 5%."
    },
    {
        "id": "commodity_supercycle",
        "title": "Commodity Supercycles",
        "source_key": "worldbank",
        "tags": ["commodities", "macro", "inflation"],
        "content_def": "Commodity supercycles are decade-long periods of above-trend prices driven by structural demand shifts (e.g., China urbanization 2000s). Current thesis: Energy transition (copper, lithium) + deglobalization + underinvestment = new supercycle.",
        "content_counter": "Past supercycles required massive industrialization of a large population (China 1.4B). Green transition demand is real but incremental. Recycling, substitution, and tech efficiency may cap prices. Financialization of commodities also creates artificial bubbles.",
        "content_data": "Copper hit $11k/ton in 2024 on AI datacenter/EV grid demand. Lithium crashed 80% from 2022 peak on supply surge. BCOM index flat 2023-2024. No broad-based supercycle yet, only selective shortages."
    },
    {
        "id": "china_economy",
        "title": "China Economy Structural Challenges",
        "source_key": "worldbank",
        "tags": ["china", "recession", "macro"],
        "content_def": "China faces 'balance sheet recession': property sector collapse (30% of household wealth), local government debt ($9T+), demographic decline (population peaked 2022), and deflationary pressure. Shift from investment-led to consumption-led growth is painful.",
        "content_counter": "China state control allows directed stimulus invisible to Western models. EV/tech export surge offsets property drag. Rural-urban migration room remains. 'Japanification' narrative may be overstated; China income per capita still 1/6 of Japan's at peak.",
        "content_data": "2023 GDP grew 5.2% (official), likely ~3-4% real. Property sales -10% YoY. Youth unemployment paused reporting after hitting 21%. Deflation: CPI <1%, PPI negative 14 months. Stimulus focused on manufacturing, not household transfers."
    },
    {
        "id": "europe_economy",
        "title": "European Economy Slowdown",
        "source_key": "ecb",
        "tags": ["eurozone", "recession", "energy"],
        "content_def": "Eurozone stagnating due to energy shock aftermath (loss of cheap Russian gas), tight ECB policy, and weak China demand for German exports. Germany, former engine, entered technical recession. Structural issues: bureaucracy, lagging tech adoption, aging demographics.",
        "content_counter": "Europe adapted faster than expected: LNG infrastructure built in 12 months, inflation fell quicker than US. Services PMI remains expansionary. Periphery (Spain, Greece) outperforming core. 'Sick man of Europe' narrative may be cyclical, not structural.",
        "content_data": "2023 Eurozone GDP +0.1%. Germany -0.3%. Inflation fell from 10.6% to 2.4% (May 2024). Natural gas prices normalized to pre-war levels. ECB cut rates June 2024 (first since launch), ahead of Fed."
    },
    {
        "id": "em_contagion",
        "title": "Emerging Markets Contagion Risk",
        "source_key": "imf",
        "tags": ["emerging_markets", "sovereign_debt", "warning"],
        "content_def": "EM contagion spreads via: 1) Trade links (China slowdown hits commodity exporters), 2) Financial links (common lenders pull back), 3) Sentiment (risk-off causes blanket EM selling). Vulnerable nations: high external debt, current account deficit, political instability.",
        "content_counter": "EM heterogeneity is key. Latin America (high rates, commodities) resilient. Asia (China-dependent) vulnerable. Frontiers (debt distress) at risk. Diversified EMs with FX reserves (Indonesia, Mexico) weather storms better than 1997/2008 episodes.",
        "content_data": "2023-2024: No systemic contagion despite high US rates. EM FX stable, some rallied (Real, Peso). Bond spreads tightened. Exception: Frontier markets (Egypt, Pakistan, Kenya) under stress. China property drag impacted Australia/LatAm metals but contained."
    }
]

ALL_TOPICS = TOPICS + EXTRA_TOPICS

def generate_fragments():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    count = 0
    for topic in ALL_TOPICS:
        source_info = SOURCES[topic["source_key"]]
        
        # 1. Definition Fragment
        frag_def = {
            "id": f"frag_fin_{topic['id']}_def_01",
            "domain": DOMAIN,
            "subdomain": SUBDOMAIN,
            "tags": topic["tags"] + ["definition", "first_line"],
            "reasoning_role": "definition",
            "content": topic["content_def"],
            "source": source_info["cred"],
            "source_url": source_info["url"],
            "credibility_class": source_info["cred"],
            "year": YEAR,
            "compatible_with": [],
            "incompatible_with": [],
            "weight": source_info["weight"]
        }
        
        # 2. Counter Argument Fragment
        frag_counter = {
            "id": f"frag_fin_{topic['id']}_counter_01",
            "domain": DOMAIN,
            "subdomain": SUBDOMAIN,
            "tags": topic["tags"] + ["counter_argument", "warning"],
            "reasoning_role": "counter_argument",
            "content": topic["content_counter"],
            "source": source_info["cred"],
            "source_url": source_info["url"],
            "credibility_class": source_info["cred"],
            "year": YEAR,
            "compatible_with": [f"frag_fin_{topic['id']}_def_01"],
            "incompatible_with": [],
            "weight": source_info["weight"] * 0.95  # Slightly lower weight for counter views
        }
        
        # 3. Latest Data Fragment
        frag_data = {
            "id": f"frag_fin_{topic['id']}_data_01",
            "domain": DOMAIN,
            "subdomain": SUBDOMAIN,
            "tags": topic["tags"] + ["latest_data"],
            "reasoning_role": "latest_data",
            "content": topic["content_data"],
            "source": source_info["cred"],
            "source_url": source_info["url"],
            "credibility_class": source_info["cred"],
            "year": YEAR,
            "compatible_with": [f"frag_fin_{topic['id']}_def_01"],
            "incompatible_with": [],
            "weight": source_info["weight"] * 0.98  # High weight but decays fast
        }
        
        # Save files
        for frag in [frag_def, frag_counter, frag_data]:
            filename = f"{frag['id']}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, 'w') as f:
                json.dump(frag, f, indent=2)
            print(f"Created: {filename}")
            count += 1
            
    print(f"\n=== Task 1.4 Complete ===")
    print(f"Generated {count} fragments for Central Bank & Global Macro")
    print(f"Topics covered: {len(ALL_TOPICS)}")
    print(f"Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_fragments()
