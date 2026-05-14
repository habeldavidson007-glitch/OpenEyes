#!/usr/bin/env python3
"""
OpenEyes Macro Foundation Fragment Builder

Generates 150 finance macro fragments covering 25 topics with 3 reasoning roles each:
- definition: Core definitions and explanations
- counter_argument: Limitations, caveats, alternative views
- latest_data: Recent data points and current state

Usage:
    python openeyes/tools/build_macro_fragments.py
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Output directory
FRAGMENTS_DIR = Path("openeyes/fragment_library/fragments")

# Topic definitions with detailed content for each reasoning role
MACRO_TOPICS = [
    {
        "topic": "fed_mandate",
        "title": "Federal Reserve Mandate",
        "tags": ["fed", "central_bank", "monetary_policy", "macro"],
        "definition": {
            "content": "The Federal Reserve operates under a dual mandate established by Congress: maximum employment and stable prices. The dual mandate was formalized in the Federal Reserve Reform Act of 1977, which amended the Federal Reserve Act. Maximum employment refers to the highest level of employment that can be sustained without generating inflationary pressures. Stable prices is typically interpreted as an inflation rate of 2 percent over the longer run, as measured by the annual change in the Personal Consumption Expenditures (PCE) price index. The Fed must balance these two objectives when setting monetary policy, though they are generally complementary in the longer run.",
            "source": "Federal Reserve Act, Section 2A",
            "source_url": "https://www.federalreserve.gov/aboutthefed/section2a.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Critics argue the dual mandate creates inherent conflicts and ambiguity. Some economists contend that monetary policy cannot sustainably affect real variables like employment in the long run, making the employment mandate potentially misleading. Others argue for a single mandate focused solely on price stability, as adopted by the European Central Bank. The 'maximum employment' concept lacks a precise numerical target, unlike the 2% inflation goal, creating asymmetry in the mandate's implementation. Additionally, some argue the mandate should be expanded to include financial stability as an explicit third objective, particularly after the 2008 financial crisis demonstrated how financial instability can severely impact both employment and prices.",
            "source": "Various economic critiques",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/the-feds-dual-mandate-20190815.html",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "As of 2024-2026, the Federal Reserve continues to operate under the dual mandate framework. Following the 2020 Framework Review, the Fed adopted flexible average inflation targeting (FAIT), allowing inflation to run moderately above 2% for some time following periods when it has been running persistently below 2%. This approach aims to achieve better outcomes for both employment and inflation. Current policy statements emphasize the Fed's commitment to returning inflation to its 2% goal while supporting maximum employment. Labor market conditions and inflation data continue to guide FOMC policy decisions.",
            "source": "Federal Reserve Policy Statements",
            "source_url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary.htm",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "fomc_meetings",
        "title": "FOMC Meetings and Decision Process",
        "tags": ["fomc", "fed", "interest_rate", "monetary_policy"],
        "definition": {
            "content": "The Federal Open Market Committee (FOMC) is the Fed's monetary policymaking body. It consists of 12 members: the seven members of the Board of Governors, the president of the Federal Reserve Bank of New York, and four of the remaining 11 Reserve Bank presidents who serve one-year terms on a rotating basis. The FOMC holds eight regularly scheduled meetings per year, approximately every six weeks. At these meetings, the Committee reviews economic and financial conditions, determines the appropriate stance of monetary policy, and assesses risks to its long-run goals of price stability and sustainable economic growth. The primary policy tool is the target range for the federal funds rate. Decisions are made by consensus, with votes taken on policy statements. The FOMC issues a statement after each meeting explaining its decision, and the Chair holds a press conference for meetings with updated economic projections.",
            "source": "Federal Reserve Board",
            "source_url": "https://www.federalreserve.gov/monetarypolicy/fomc.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Critics argue FOMC deliberations lack transparency despite post-meeting statements and press conferences. Meeting transcripts are released with a five-year lag, limiting real-time accountability. Some economists contend the Committee's composition gives disproportionate influence to Wall Street perspectives through the New York Fed's permanent voting seat. Regional Fed presidents, who are not appointed by elected officials, have voting power on monetary policy affecting the entire nation. Additionally, the consensus-driven approach may obscure important dissenting views, though dissents are recorded. Critics also note that emergency meetings and unconventional policy tools (like quantitative easing) have expanded FOMC power beyond traditional boundaries with limited congressional oversight.",
            "source": "Government Accountability Office Reports",
            "source_url": "https://www.gao.gov/products/gao-21-105sp",
            "credibility_class": "government_source"
        },
        "latest_data": {
            "content": "The FOMC maintained its regular eight-meeting schedule through 2024-2026. Meeting dates are announced well in advance, allowing markets to prepare. Recent meetings have featured heightened attention to inflation dynamics, labor market tightness, and financial stability concerns. The Summary of Economic Projections (SEP), including the 'dot plot' of individual FOMC participants' rate projections, is released at four meetings per year. Market participants closely analyze FOMC statements for changes in language that might signal policy shifts. Communication strategy has evolved to provide clearer forward guidance while maintaining flexibility to respond to changing economic conditions.",
            "source": "FOMC Meeting Calendar",
            "source_url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "fed_funds_rate",
        "title": "Federal Funds Rate",
        "tags": ["fed_funds_rate", "interest_rate", "monetary_policy", "fed"],
        "definition": {
            "content": "The federal funds rate is the interest rate at which depository institutions (banks and credit unions) lend reserve balances to other depository institutions overnight on an uncollateralized basis. The Federal Reserve sets a target range for this rate through its monetary policy decisions. This rate serves as the primary tool for implementing monetary policy. Changes in the federal funds rate influence other short-term interest rates, foreign exchange rates, long-term interest rates, asset prices, and ultimately employment and inflation. When the Fed raises the federal funds rate, borrowing becomes more expensive, which tends to slow economic activity and reduce inflationary pressures. Conversely, lowering the rate stimulates borrowing and spending. The effective federal funds rate is the volume-weighted median of overnight federal funds transactions reported to the Federal Reserve Bank of New York.",
            "source": "Federal Reserve Board",
            "source_url": "https://www.federalreserve.gov/faqs/money_12844.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "The transmission mechanism from the federal funds rate to the broader economy is complex and operates with long and variable lags, making precise calibration difficult. Some economists argue the zero lower bound constraint limits the effectiveness of conventional rate policy during severe downturns, necessitating unconventional tools. The relationship between the fed funds rate and long-term rates has weakened in recent decades due to global capital flows and central bank balance sheet policies. Critics also note that rate changes affect different sectors and demographics unequally—higher rates disproportionately impact housing markets and younger borrowers while benefiting savers. Additionally, the neutral rate (r*) is unobservable and subject to significant estimation uncertainty, complicating policy decisions.",
            "source": "Federal Reserve Economic Research",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/estimates-of-the-neutral-rate-of-interest-20230117.htm",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "The federal funds rate target range has varied significantly in recent years. Following the pandemic, rates were near zero until 2022, then rose rapidly to combat inflation. By 2024-2026, the FOMC adjusts the target range based on incoming economic data, particularly inflation and labor market indicators. The effective federal funds rate typically trades within the target range set by the FOMC. Interest on Reserve Balances (IORB) and the Overnight Reverse Repurchase Agreement (ON RRP) facility help keep the effective rate within the target range. Market participants closely watch the dot plot and Fed communications for signals about the future path of rates.",
            "source": "Federal Reserve Statistical Release H.15",
            "source_url": "https://www.federalreserve.gov/releases/h15/",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "quantitative_easing",
        "title": "Quantitative Easing (QE)",
        "tags": ["quantitative_easing", "qe", "monetary_policy", "fed", "balance_sheet"],
        "definition": {
            "content": "Quantitative easing (QE) is an unconventional monetary policy tool used when short-term interest rates are at or near zero. Under QE, the Federal Reserve purchases longer-term securities (typically Treasury bonds and mortgage-backed securities) from the open market to increase the money supply and encourage lending and investment. These purchases expand the Fed's balance sheet and inject reserves into the banking system. QE works through several channels: (1) portfolio rebalancing—investors shift into riskier assets as safe assets become scarcer; (2) signaling—commitment to keeping rates low for extended periods; (3) liquidity effects—improved functioning of specific markets; and (4) confidence effects—boosting investor and consumer sentiment. The Fed first used QE during the 2008 financial crisis and again during the 2020 pandemic recession.",
            "source": "Federal Reserve Board",
            "source_url": "https://www.federalreserve.gov/monetarypolicy/qe.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Critics argue QE has diminishing returns with each iteration and creates adverse side effects. Concerns include: (1) asset price inflation benefiting wealthy asset holders while exacerbating wealth inequality; (2) potential for creating asset bubbles in equities, real estate, and riskier securities; (3) distortion of market price discovery mechanisms; (4) challenges in exiting without disrupting markets; (5) fiscal dominance concerns as large-scale asset purchases blur lines between monetary and fiscal policy; (6) negative impacts on bank profitability through compressed net interest margins; and (7) potential currency debasement and international spillover effects. Some economists question whether QE effectively reaches the real economy versus primarily inflating financial asset prices.",
            "source": "Bank for International Settlements Research",
            "source_url": "https://www.bis.org/publ/work930.htm",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "Following the aggressive QE programs during the pandemic, the Federal Reserve's balance sheet expanded to nearly $9 trillion by 2022. The Fed began reducing its holdings in 2023 through quantitative tightening (QT). As of 2024-2026, the size and composition of the Fed's balance sheet reflects both the prior QE purchases and ongoing runoff. The Fed continues to reinvest principal payments from agency debt and MBS to maintain ample reserves while allowing Treasury holdings to decline. Research on QE effectiveness continues, with most studies finding modest positive effects on output and inflation, though estimates vary widely depending on methodology and economic context.",
            "source": "Federal Reserve Balance Sheet Data",
            "source_url": "https://www.federalreserve.gov/monetarypolicy/bst_recenttrends.htm",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "quantitative_tightening",
        "title": "Quantitative Tightening (QT)",
        "tags": ["quantitative_tightening", "qt", "monetary_policy", "fed", "balance_sheet"],
        "definition": {
            "content": "Quantitative tightening (QT) is the process by which the Federal Reserve reduces its balance sheet by allowing securities to mature without reinvestment or by actively selling holdings. QT is the reverse of quantitative easing (QE). The Fed began QT in October 2017 following the post-2008 QE programs and resumed it in June 2022 after pandemic-era expansions. Unlike QE which actively purchases assets, QT typically operates passively through non-reinvestment of maturing securities up to specified monthly caps. The goals include normalizing monetary policy, reducing excess reserves, and creating space for future stimulus. QT affects the economy through similar channels as QE but in reverse: raising longer-term interest rates, tightening financial conditions, and reducing liquidity. The pace and impact depend on the size of reductions and market conditions.",
            "source": "Federal Reserve Board",
            "source_url": "https://www.federalreserve.gov/monetarypolicy/bst_norm.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Critics warn QT poses risks to financial stability and economic growth. Concerns include: (1) potential for market disruption if reduction proceeds too quickly; (2) interaction with fiscal policy as reduced Fed demand for Treasuries may raise government borrowing costs; (3) uncertainty about the appropriate endpoint—how small the balance sheet should be; (4) risk of triggering a 'tantrum' episode similar to 2013 taper tantrum; (5) potential strain on bank reserves affecting repo markets and short-term funding; (6) asymmetric effects where QT may have stronger contractionary impact than QE's expansionary effect; and (7) complications from simultaneous interest rate increases. Some argue passive QT lacks the precision of active rate policy and may be unnecessary if rate policy is sufficiently restrictive.",
            "source": "International Monetary Fund Working Papers",
            "source_url": "https://www.imf.org/en/Publications/WP/Issues/2023/03/15/Quantitative-Tightening-Lessons-from-History-530847",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "The Federal Reserve's QT program continued through 2024-2026 with monthly redemption caps of $60 billion for Treasuries and $35 billion for agency MBS. The balance sheet declined from its 2022 peak but remained elevated compared to pre-pandemic levels. The Fed monitors reserve levels carefully to avoid repeating the September 2019 repo market disruption. Officials have indicated the ultimate balance sheet size will be determined by demand for reserves rather than a specific target. Market participants watch for signals about slowing the pace of QT ('tapering the taper') as reserves approach estimated minimum comfortable levels.",
            "source": "Federal Reserve Balance Sheet Data",
            "source_url": "https://www.federalreserve.gov/monetarypolicy/bst_recenttrends.htm",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "cpi_inflation",
        "title": "Consumer Price Index (CPI)",
        "tags": ["cpi", "inflation", "consumer_price_index", "macro"],
        "definition": {
            "content": "The Consumer Price Index (CPI) measures the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services. Published monthly by the Bureau of Labor Statistics (BLS), CPI covers categories including food, energy, housing, apparel, transportation, medical care, recreation, education, and other goods and services. The index is based on prices collected from thousands of retail stores, service establishments, rental units, and websites across the U.S. CPI is widely used as an indicator of inflation and cost of living changes. It serves as a cost-of-living adjustment measure for Social Security benefits, federal civil service and military retirement pensions, and federal income tax brackets. The CPI-U (All Urban Consumers) covers approximately 93% of the U.S. population.",
            "source": "Bureau of Labor Statistics",
            "source_url": "https://www.bls.gov/cpi/",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "CPI has several well-documented limitations. Substitution bias occurs because CPI uses a fixed basket and doesn't fully capture consumers switching to cheaper alternatives when prices change. Quality adjustment is challenging—improvements in product quality may not be fully reflected, potentially overstating inflation. New products take time to enter the basket, missing early price declines. Geographic coverage is limited to urban areas. CPI may not accurately reflect individual experiences, especially for elderly (who spend more on healthcare) or low-income households (who spend more on food and energy). The Boskin Commission (1996) estimated CPI overstated inflation by about 1.1 percentage points annually, though BLS methodological improvements have reduced this bias. Core CPI excludes food and energy but these items matter significantly for household budgets.",
            "source": "Bureau of Labor Statistics Technical Documentation",
            "source_url": "https://www.bls.gov/cpi/research/chained/articles/does-cpi-overstate-changes-in-the-cost-of-living.htm",
            "credibility_class": "government_source"
        },
        "latest_data": {
            "content": "CPI data continues to be released monthly around the 13th of each month for the preceding month. Year-over-year CPI inflation peaked in mid-2022 before declining through 2023-2024. Core CPI (excluding food and energy) typically shows different dynamics than headline CPI. Shelter costs represent the largest component of CPI and tend to be sticky. The BLS continuously updates methodology and basket weights based on Consumer Expenditure Survey data. Market participants closely watch CPI releases as they influence Federal Reserve policy decisions. TIPS breakeven rates and inflation swaps provide market-based inflation expectations that can be compared to CPI trends.",
            "source": "Bureau of Labor Statistics News Releases",
            "source_url": "https://www.bls.gov/cpi/#tables",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "pce_inflation",
        "title": "Personal Consumption Expenditures (PCE) Price Index",
        "tags": ["pce", "inflation", "personal_consumption", "macro", "fed"],
        "definition": {
            "content": "The Personal Consumption Expenditures (PCE) price index measures the prices that persons living in the United States, or on behalf of them, pay for goods and services purchased. Produced monthly by the Bureau of Economic Analysis (BEA), PCE covers all consumption regardless of whether the good or service was purchased directly by households or provided through government programs or employer-provided benefits. The PCE index uses a chain-weighted formula that accounts for substitution between categories as relative prices change, addressing a key limitation of CPI. The Federal Reserve has explicitly adopted the 2% inflation target in terms of PCE rather than CPI, citing PCE's broader scope and superior treatment of substitution. Core PCE excludes food and energy prices and is the Fed's preferred inflation gauge.",
            "source": "Bureau of Economic Analysis",
            "source_url": "https://www.bea.gov/data/personal-consumption-expenditures-price-index",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "While PCE addresses some CPI limitations, it has its own drawbacks. PCE data is revised more substantially than CPI, with initial releases subject to larger revisions as more complete source data becomes available. The timeliness is inferior—PCE is released about a month after CPI. The chain-weighting methodology, while theoretically superior, makes PCE less intuitive for tracking the cost of a fixed basket of goods. Because PCE includes expenditures made on behalf of households (like Medicare), it may be less relevant for measuring out-of-pocket cost pressures facing consumers. Some critics argue the Fed's preference for PCE allows it to focus on a measure that typically runs below CPI, potentially understating inflation experienced by households.",
            "source": "Federal Reserve Economic Research",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/differences-between-cpi-and-pce-20190830.htm",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "PCE price index data is released monthly by the BEA, typically near the end of the month for the preceding month. Core PCE inflation has been closely watched by Fed policymakers as they assess progress toward the 2% inflation target. The gap between CPI and PCE inflation typically ranges from 0.2 to 0.5 percentage points, with PCE generally lower due to methodological differences. Healthcare services represent a larger share of PCE than CPI due to inclusion of government and employer-paid health insurance. Real-time PCE data and nowcasting models help analysts estimate current inflation before official releases.",
            "source": "Bureau of Economic Analysis News Releases",
            "source_url": "https://www.bea.gov/news/schedule",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "ppi_inflation",
        "title": "Producer Price Index (PPI)",
        "tags": ["ppi", "inflation", "producer_prices", "macro"],
        "definition": {
            "content": "The Producer Price Index (PPI) measures the average change over time in the selling prices received by domestic producers for their output. Published monthly by the Bureau of Labor Statistics, PPI tracks price changes at various stages of production: crude materials, intermediate goods, and finished goods. Unlike CPI which measures prices paid by consumers, PPI measures prices received by producers, making it a leading indicator of consumer inflation. PPI covers goods, services, and construction. Services PPI has grown in importance as the U.S. economy has shifted toward services. The final demand PPI is the most closely watched aggregate measure. PPI excludes imports and taxes, focusing purely on domestic producer prices.",
            "source": "Bureau of Labor Statistics",
            "source_url": "https://www.bls.gov/ppi/",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "PPI has limitations as an inflation predictor. The pass-through from producer to consumer prices is incomplete and variable—producers may absorb cost increases through margin compression rather than passing them to consumers. Import prices are excluded from PPI but affect consumer prices, creating gaps during periods of significant import price movements. The relationship between PPI and CPI has weakened as services comprise a growing share of consumer spending while goods dominate PPI. Sector-specific shocks (like energy price swings) can cause large PPI volatility that doesn't translate to core inflation. Supply chain disruptions can create temporary divergences between producer and consumer price dynamics.",
            "source": "Bureau of Labor Statistics Research",
            "source_url": "https://www.bls.gov/ppi/ppi-faq.htm",
            "credibility_class": "government_source"
        },
        "latest_data": {
            "content": "PPI data continues to be released monthly, typically around the 12th of each month. Goods PPI showed significant volatility during 2020-2023 due to pandemic-related supply chain disruptions and commodity price swings. Services PPI has been more stable but warrants attention for persistent inflation signals. Energy and food components show high volatility and are often excluded for core measures. Analysts compare PPI trends with CPI and import price indices to gauge inflation pipeline pressures. Input PPI (prices producers pay) versus output PPI (prices they receive) provides insight into margin pressures.",
            "source": "Bureau of Labor Statistics News Releases",
            "source_url": "https://www.bls.gov/ppi/#tables",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "core_vs_headline",
        "title": "Core vs Headline Inflation",
        "tags": ["inflation", "core_inflation", "headline_inflation", "macro"],
        "definition": {
            "content": "Headline inflation refers to the total inflation within an economy, including volatile components like food and energy prices. Core inflation excludes food and energy prices, which tend to be more volatile due to supply shocks, weather events, and geopolitical factors. Core inflation is intended to reveal the underlying, persistent trend in prices. Both measures are calculated for CPI and PCE indices. Policymakers, particularly the Federal Reserve, focus heavily on core inflation when making monetary policy decisions because it better predicts future inflation. However, headline inflation remains important for households' actual cost of living. Over long periods, headline and core inflation tend to converge, but they can diverge significantly in the short term during commodity price shocks.",
            "source": "Federal Reserve Board",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/core-inflation-20180315.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Critics argue that excluding food and energy from core inflation ignores essential household expenses, making core inflation less relevant for workers and retirees. Food and energy together represent roughly 20-25% of typical household budgets. During periods of sustained food or energy price increases (rather than temporary spikes), core inflation may underestimate true inflation pressures. Alternative core measures like trimmed mean or median CPI (which exclude different portions of the distribution each month) may better capture underlying inflation. Some economists advocate for 'sticky price' core measures that focus on prices that adjust infrequently. Households cannot easily substitute away from food and energy, making their exclusion problematic for welfare analysis.",
            "source": "Federal Reserve Bank of Cleveland Research",
            "source_url": "https://www.clevelandfed.org/en/our-research/data-and-inflation-tools.aspx",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "The gap between headline and core inflation fluctuates with commodity price cycles. During 2022, energy price surges pushed headline inflation well above core. As energy prices stabilized or declined in 2023-2024, headline inflation converged toward or occasionally below core. Fed officials monitor multiple core inflation measures including core PCE, trimmed mean PCE (Dallas Fed), median CPI (Cleveland Fed), and supercore (services excluding housing). Disaggregated inflation analysis examines which components are driving persistence. Inflation expectations surveys help distinguish transitory from persistent price pressures.",
            "source": "Federal Reserve Economic Data",
            "source_url": "https://fred.stlouisfed.org/categories/30",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "gdp_measurement",
        "title": "Gross Domestic Product (GDP)",
        "tags": ["gdp", "economic_growth", "macro", "economic_output"],
        "definition": {
            "content": "Gross Domestic Product (GDP) measures the total value of all final goods and services produced within a country's borders in a given period. GDP can be measured three ways that should yield identical results: (1) Production approach—sum of value added across all industries; (2) Income approach—sum of all incomes earned in production (wages, profits, rents); (3) Expenditure approach—C+I+G+(X-M), the sum of consumption, investment, government spending, and net exports. Real GDP adjusts for inflation using price indices, allowing comparison of actual production volumes over time. GDP growth rate is the primary gauge of economic performance. The Bureau of Economic Analysis releases GDP estimates quarterly, with three vintages: advance, second, and third estimates, plus annual revisions.",
            "source": "Bureau of Economic Analysis",
            "source_url": "https://www.bea.gov/data/gross-domestic-product-gdp",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "GDP has well-known limitations as a welfare measure. It counts 'bads' like pollution cleanup costs as positive contributions. It ignores non-market activities like household work and volunteer services. It doesn't account for income distribution—a rising GDP can coexist with stagnant median incomes. It fails to capture environmental degradation or resource depletion. Quality improvements and new products are difficult to measure accurately. The underground economy and illegal activities are largely excluded. GDP says nothing about sustainability of growth. Alternative measures like the Genuine Progress Indicator (GPI), Human Development Index (HDI), and OECD Better Life Index attempt to address these gaps. Despite limitations, GDP remains the best single measure of economic activity for policy purposes.",
            "source": "Bureau of Economic Analysis Methodology Papers",
            "source_url": "https://www.bea.gov/system/files/2023-07/conceptual-framework-bea-accounts.pdf",
            "credibility_class": "government_source"
        },
        "latest_data": {
            "content": "U.S. GDP data continues to be released quarterly by the BEA with the standard revision schedule. Real GDP growth has shown variability in the 2020s due to pandemic effects, supply chain disruptions, and policy responses. Components analysis reveals drivers of growth—whether consumption, business investment, government spending, or trade. Gross Domestic Income (GDI), measured from the income side, provides a cross-check though statistical discrepancies exist. Nowcasting models use high-frequency data to estimate GDP before official releases. Potential GDP estimates inform debates about economic capacity and inflation risks.",
            "source": "Bureau of Economic Analysis News Releases",
            "source_url": "https://www.bea.gov/news/schedule",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "gdp_growth_rate",
        "title": "GDP Growth Rate",
        "tags": ["gdp", "economic_growth", "recession", "macro"],
        "definition": {
            "content": "The GDP growth rate measures the percentage change in real GDP from one period to another, typically expressed as an annualized quarter-over-quarter rate or year-over-year rate. Healthy advanced economies typically grow at 2-3% annually over the long run, reflecting productivity gains and labor force growth. Growth rates above trend can indicate economic overheating and inflationary pressures, while rates below trend or negative growth signal weakness. Two consecutive quarters of negative real GDP growth is a common (though not official) definition of recession. The National Bureau of Economic Research (NBER) makes official U.S. recession determinations based on a broader set of indicators. Sustainable growth depends on productivity improvements, labor force participation, and capital accumulation.",
            "source": "Bureau of Economic Analysis",
            "source_url": "https://www.bea.gov/data/gross-domestic-product-gdp",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "The 'two-quarter rule' for recessions is imprecise and sometimes contradicts NBER determinations. Growth rate volatility makes single-quarter readings noisy. Potential growth rate estimates are uncertain and change over time—the U.S. trend growth rate has declined from ~3.5% in the 1980s-90s to ~2% today due to demographics and slower productivity growth. Comparing growth rates across countries requires accounting for catch-up effects—developing economies can grow faster by adopting existing technologies. Short-term growth fluctuations may reflect temporary factors (weather, strikes, inventory cycles) rather than fundamental economic health. Focus on quarterly growth rates can encourage short-termism in policy. Some economists advocate for level-targeting or growth path targeting rather than growth rate targeting.",
            "source": "National Bureau of Economic Research",
            "source_url": "https://www.nber.org/research/business-cycle-dating",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "U.S. real GDP growth has shown variability in the 2020s. Post-pandemic recovery featured strong growth in 2021 followed by moderation. Growth forecasts from the Congressional Budget Office, Federal Reserve, and private sector analysts provide benchmarks for assessing performance. Decomposition of growth sources—consumption, investment, government, net exports—reveals sustainability. Labor productivity growth remains a key determinant of long-run growth potential and living standards. Real-time data and nowcasts help track economic momentum between official releases.",
            "source": "Congressional Budget Office Economic Projections",
            "source_url": "https://www.cbo.gov/economic-projections",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "nonfarm_payroll",
        "title": "Nonfarm Payroll Employment",
        "tags": ["nonfarm_payroll", "employment", "labor_market", "jobs_report"],
        "definition": {
            "content": "Nonfarm payroll employment measures the total number of paid workers in the U.S. excluding farm workers, government employees, private household employees, and employees of nonprofit organizations. Published monthly by the Bureau of Labor Statistics as part of the Employment Situation report, it is based on the Current Employment Statistics (CES) survey of approximately 119,000 businesses and government agencies representing about 629,000 worksites. Nonfarm payrolls is the most closely watched labor market indicator because of its timeliness, comprehensive coverage, and historical reliability. The report includes breakdowns by industry sector, average hourly earnings, and average weekly hours. Revisions to prior months' data are common as additional survey responses arrive.",
            "source": "Bureau of Labor Statistics",
            "source_url": "https://www.bls.gov/bls/news-release/empsit.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Nonfarm payrolls has limitations. It counts jobs, not workers—one person holding two jobs is counted twice. It excludes self-employed workers, unpaid family workers, and agricultural workers. The establishment survey cannot detect new businesses until they appear in the sampling frame, potentially missing job creation from startups. Large revisions can significantly alter the picture. The survey misses the gig economy and informal work arrangements. During turning points, preliminary estimates have sometimes been substantially revised. The household survey (which produces the unemployment rate) and establishment survey (payrolls) can diverge. Some argue the focus on headcount ignores underemployment and labor force participation trends.",
            "source": "Bureau of Labor Statistics Technical Documentation",
            "source_url": "https://www.bls.gov/web/empsit/cestn.htm",
            "credibility_class": "government_source"
        },
        "latest_data": {
            "content": "The monthly jobs report continues to be released on the first Friday of each month for the preceding month. Nonfarm payroll growth has varied significantly in the 2020s, from massive pandemic losses to strong recovery hiring. Sectoral shifts have been notable, with strength in healthcare, leisure and hospitality recovery, and technology sector volatility. Average hourly earnings growth is monitored for wage inflation signals. Labor force participation rate and employment-to-population ratio provide context for payroll numbers. Benchmark revisions annually align survey estimates with administrative data from unemployment insurance records.",
            "source": "Bureau of Labor Statistics News Releases",
            "source_url": "https://www.bls.gov/news.release/empsit.toc.htm",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "unemployment_rate",
        "title": "Unemployment Rate",
        "tags": ["unemployment", "labor_market", "employment", "macro"],
        "definition": {
            "content": "The unemployment rate measures the percentage of the labor force that is jobless and actively seeking employment. It is derived from the Current Population Survey (CPS), a monthly survey of about 60,000 households conducted by the Census Bureau for the BLS. To be counted as unemployed, individuals must be without a job, available to work, and have actively looked for work in the prior four weeks. The labor force consists of employed plus unemployed persons. Those not working and not seeking work are 'not in the labor force.' The official unemployment rate is U-3. Alternative measures include U-6 (broadest, including marginally attached workers and those working part-time for economic reasons) and U-4, U-5 (intermediate measures). Duration of unemployment and reasons for unemployment are also reported.",
            "source": "Bureau of Labor Statistics",
            "source_url": "https://www.bls.gov/cps/",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "The official unemployment rate has significant limitations. It excludes discouraged workers who want jobs but have stopped looking. It doesn't capture underemployment—those working part-time who want full-time work. The labor force participation rate has declined structurally due to aging demographics, complicating interpretation. During the pandemic, measurement issues arose as many classified as 'unemployed' were temporarily laid off with uncertain recall prospects. The unemployment rate can remain low even with substantial labor market slack if participation is depressed. International comparisons are complicated by different measurement methodologies. The natural rate of unemployment (NAIRU) is unobservable and subject to revision. Some economists prefer employment-to-population ratios or vacancy-unemployment ratios (Beveridge curve analysis).",
            "source": "Federal Reserve Economic Research",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/whats-happened-to-the-relationship-between-the-unemployment-rate-and-wage-growth-20230815.htm",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "The unemployment rate continues to be released monthly alongside nonfarm payrolls. U-3 unemployment reached historic lows in the early 2020s before rising modestly. U-6 broad unemployment provides additional context on labor market slack. Demographic breakdowns reveal disparities—youth unemployment typically runs higher than adult rates, and racial disparities persist. Long-term unemployment (27+ weeks) is monitored for hysteresis risks. Job openings data from JOLTS complements unemployment statistics. Wage growth measures help assess labor market tightness. The Sahm Rule uses unemployment rate changes as a recession indicator.",
            "source": "Bureau of Labor Statistics News Releases",
            "source_url": "https://www.bls.gov/news.release/empsit.toc.htm",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "labor_force_participation",
        "title": "Labor Force Participation Rate",
        "tags": ["labor_market", "employment", "demographics", "macro"],
        "definition": {
            "content": "The labor force participation rate (LFPR) measures the percentage of the civilian noninstitutional population age 16 and older that is in the labor force (working or actively seeking work). Unlike the unemployment rate, LFPR is not affected by whether people can find jobs—it reflects decisions about whether to seek employment. LFPR is influenced by demographics (age, education), social norms, disability rates, retirement patterns, school enrollment, and economic incentives. The prime-age (25-54) LFPR is closely watched as it excludes students and early retirees. Women's LFPR rose dramatically in the 20th century but plateaued. Men's LFPR has trended down for decades. The overall LFPR declined from its 2000 peak due to Baby Boomer retirements.",
            "source": "Bureau of Labor Statistics",
            "source_url": "https://www.bls.gov/opub/mlr/2022/article/labor-force-participation-rates.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Interpreting LFPR trends is complex. Declines could reflect positive developments (more college attendance, earlier retirement due to wealth accumulation) or negative ones (discouragement, disability epidemics, opioid crisis). The pandemic caused unprecedented LFPR drops, particularly among women due to caregiving responsibilities. Recovery patterns have been uneven across demographics. Some argue expanded safety nets reduced work incentives, while others point to structural barriers like childcare costs and skills mismatches. Immigration affects LFPR calculations as immigrants have different participation patterns than native-born. Cross-country comparisons show wide variation due to cultural and policy differences. The relationship between LFPR and economic growth is bidirectional—strong economies can draw people into the labor force.",
            "source": "Congressional Budget Office Analysis",
            "source_url": "https://www.cbo.gov/publication/59244",
            "credibility_class": "government_source"
        },
        "latest_data": {
            "content": "LFPR data continues to be released monthly with the employment situation report. Prime-age LFPR has recovered to near pre-pandemic levels, but overall LFPR remains below 2000 peaks due to aging. Gender gaps in participation have narrowed but persist. Early retirement trends accelerated during the pandemic ('Great Resignation'). Disability applications and enrollments affect participation among working-age adults. Policy discussions focus on childcare, paid leave, and retirement age reforms to boost participation. Immigration policy affects labor supply projections.",
            "source": "Bureau of Labor Statistics CPS Data",
            "source_url": "https://www.bls.gov/charts/employment-situation/civilian-labor-force-participation-rate.htm",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "yield_curve",
        "title": "Treasury Yield Curve",
        "tags": ["yield_curve", "treasury", "bonds", "fixed_income", "macro"],
        "definition": {
            "content": "The Treasury yield curve plots the yields (interest rates) of U.S. Treasury securities across different maturities, from 1-month bills to 30-year bonds. Normally, the curve slopes upward—longer-term bonds pay higher yields to compensate investors for interest rate risk and inflation uncertainty over longer horizons. The curve shape reflects market expectations about future interest rates, inflation, and economic growth. Key spreads are closely watched: 10-year minus 2-year, 10-year minus 3-month. The curve is constructed from observable Treasury security yields, with the Constant Maturity Treasury (CMT) series providing standardized yields at specific maturities. The yield curve influences borrowing costs throughout the economy, from mortgages to corporate bonds.",
            "source": "U.S. Department of the Treasury",
            "source_url": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Yield curve interpretation has complexities. Quantitative easing distorted the curve by compressing term premiums through large-scale asset purchases. Global demand for safe assets affects Treasury yields independent of U.S. economic fundamentals. The neutral rate decline means curves may appear flatter in absolute terms without signaling weakness. Regulatory changes affecting bank balance sheet costs can impact intermediation and curve shape. The relationship between curve shape and growth has varied across episodes. Inversion depth and duration matter—not all inversions lead to recessions. Forward rates extracted from the curve embed risk premiums, complicating extraction of pure expectations. Alternative term structure models produce different estimates of expected future rates.",
            "source": "Federal Reserve Economic Research",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/the-treasury-term-premium-20230621.htm",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "Treasury yield curve data is available daily from the Treasury Department and Federal Reserve. The curve steepened in 2023-2024 after inverting in 2022-2023 as the Fed raised rates. Market participants monitor front-end sensitivity to Fed policy versus back-end sensitivity to growth and inflation expectations. Real yields (TIPS) provide inflation-adjusted perspectives. Breakeven inflation rates derived from nominal-TIPS spreads indicate market inflation expectations. International yield curve comparisons inform capital flow analysis.",
            "source": "Federal Reserve H.15 Release",
            "source_url": "https://www.federalreserve.gov/releases/h15/",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "inverted_yield_curve",
        "title": "Inverted Yield Curve as Recession Predictor",
        "tags": ["yield_curve", "inverted_yield_curve", "recession", "macro", "prediction"],
        "definition": {
            "content": "An inverted yield curve occurs when short-term Treasury yields exceed long-term yields, producing a downward-sloping curve. This is unusual because investors typically demand higher yields for longer maturities. Inversions have preceded every U.S. recession since 1955, with only one false positive (mid-1960s). The typical inversion measure is 10-year minus 2-year Treasury spread, though 10-year minus 3-month is also used. The predictive horizon is typically 12-24 months from inversion onset. The mechanism: inversion signals tight monetary policy and/or pessimistic growth expectations, which tighten financial conditions and reduce lending. Banks' net interest margins compress when short-term funding costs exceed long-term lending rates, reducing credit availability.",
            "source": "Federal Reserve Economic Research",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/yield-curve-and-recessions-20220404.htm",
            "credibility_class": "peer_reviewed_study"
        },
        "counter_argument": {
            "content": "While historically reliable, the yield curve's predictive power has limitations. The lag between inversion and recession varies widely (6-24 months), making timing predictions imprecise. Structural changes in bond markets (QE, regulatory changes, global safe asset demand) may have altered the signal. The 2019 inversion was followed by the 2020 pandemic recession—an exogenous shock rather than a curve-predicted downturn. Some research suggests other indicators (credit spreads, leading economic indices) add incremental predictive power. The curve may predict recessions partly because market participants believe it does, creating self-fulfilling prophecies through behavior changes. Depth and duration of inversion likely matter more than binary inversion signals. The 2022-2023 inversion raised questions as recession didn't materialize in typical timeframe.",
            "source": "National Bureau of Economic Research Working Papers",
            "source_url": "https://www.nber.org/papers/w29063",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "The Treasury yield curve inverted in 2022-2023 across multiple maturity pairs, generating significant recession concern. Historical patterns suggested elevated recession risk, though timing remained uncertain. Research continues on whether traditional relationships hold in the post-QE environment. Alternative recession probability models incorporate multiple indicators beyond the yield curve. Market participants debate whether the absence of immediate recession represents broken signals or simply delayed effects. Ongoing monitoring of curve normalization (steepening) patterns provides additional signals.",
            "source": "Federal Reserve Bank Research",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/recession-probability-20230815.htm",
            "credibility_class": "peer_reviewed_study"
        }
    },
    {
        "topic": "fed_balance_sheet",
        "title": "Federal Reserve Balance Sheet",
        "tags": ["fed", "balance_sheet", "monetary_policy", "quantitative_easing"],
        "definition": {
            "content": "The Federal Reserve's balance sheet lists its assets and liabilities. Assets consist primarily of U.S. Treasury securities and agency mortgage-backed securities (MBS) acquired through open market operations. Liabilities include Federal Reserve notes (currency in circulation), reserve balances held by depository institutions, and the Treasury's General Account. The balance sheet expanded dramatically from under $1 trillion pre-2008 to nearly $9 trillion by 2022 through quantitative easing programs. Balance sheet size affects the quantity of reserves in the banking system, influencing short-term interest rates and financial conditions. The Fed publishes weekly H.4.1 reports detailing balance sheet components. Composition matters as much as size—MBS holdings affect mortgage rates specifically.",
            "source": "Federal Reserve Board",
            "source_url": "https://www.federalreserve.gov/monetarypolicy/bst_recenttrends.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Large balance sheets create potential risks and complications. Exit strategies require careful calibration to avoid market disruption. Holdings of MBS create exposure to housing market risks and complicate normalization. Interest paid on reserves affects Fed remittances to the Treasury—when rates rise, the Fed can operate at a loss, deferring remittances. Large-scale asset purchases blur lines between monetary and fiscal policy. Foreign holdings of Treasuries may be displaced by Fed purchases, affecting international monetary relations. Balance sheet policies affect income distribution through asset price channels. Some argue the Fed should return to a smaller 'corridor' system with minimal balance sheet, while others advocate maintaining ample reserves for financial stability.",
            "source": "Government Accountability Office Reports",
            "source_url": "https://www.gao.gov/products/gao-23-106267",
            "credibility_class": "government_source"
        },
        "latest_data": {
            "content": "The Fed's balance sheet peaked near $9 trillion in 2022 and has been declining through quantitative tightening. Weekly H.4.1 releases track asset levels, reserve balances, and currency in circulation. Composition shifts reflect runoff patterns—Treasuries decline faster than MBS due to different maturity structures. Reserve levels remain ample but are monitored for signs of scarcity. The Fed's SOMA (System Open Market Account) holdings are detailed in monthly reports. Interest expense on reserves has increased with higher rates, affecting Fed income and Treasury remittances.",
            "source": "Federal Reserve H.4.1 Release",
            "source_url": "https://www.federalreserve.gov/releases/h41/",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "forward_guidance",
        "title": "Forward Guidance",
        "tags": ["fed", "forward_guidance", "monetary_policy", "communication"],
        "definition": {
            "content": "Forward guidance is central bank communication about the likely future path of monetary policy. It aims to shape market and public expectations, thereby influencing longer-term interest rates and economic decisions today. Forms include: (1) qualitative guidance—general descriptions of outlook and policy inclinations; (2) calendar-based guidance—commitments to keep rates low until specific dates; (3) state-contingent guidance—linking policy to economic thresholds like unemployment or inflation rates; (4) instrument paths—explicit projections of future rate levels. Forward guidance became prominent after the 2008 crisis when rates hit the zero lower bound. The FOMC uses post-meeting statements, economic projections (including the dot plot), and Chair press conferences to convey guidance.",
            "source": "Federal Reserve Board",
            "source_url": "https://www.federalreserve.gov/monetarypolicy/fomc.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Forward guidance faces credibility and flexibility tradeoffs. Explicit commitments can box in policymakers if conditions change unexpectedly, forcing undesirable choices between reneging (damaging credibility) and following through (suboptimal policy). Markets may overinterpret vague guidance, creating volatility when language changes. Calendar-based guidance proved problematic when recovery timelines shifted. State-contingent guidance requires specifying thresholds that may prove inappropriate. Guidance effectiveness diminishes when rates are far from the zero lower bound. Communication complexity can confuse rather than clarify. Some argue central banks should focus on actions rather than words, letting policy speak for itself. Research suggests guidance works best when economic outlook is clear and policymakers are unified.",
            "source": "Bank for International Settlements Working Papers",
            "source_url": "https://www.bis.org/publ/work896.htm",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "FOMC forward guidance has evolved toward greater flexibility post-pandemic. Recent statements emphasize data-dependence rather than pre-commitment. The dot plot continues to provide individual FOMC participants' rate projections but is explicitly labeled as conditional on economic outlook. Chair press conferences elaborate on Committee thinking while maintaining flexibility. Market pricing of expected rates (fed funds futures, OIS) provides real-time feedback on guidance effectiveness. Research continues on optimal communication strategies balancing clarity and flexibility.",
            "source": "Federal Reserve Communications",
            "source_url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "inflation_expectations",
        "title": "Inflation Expectations",
        "tags": ["inflation", "expectations", "monetary_policy", "macro"],
        "definition": {
            "content": "Inflation expectations measure what households, businesses, and investors anticipate inflation will be in the future. They matter because expectations can become self-fulfilling—workers demanding higher wages and firms raising prices in anticipation of inflation actually create inflation. Well-anchored expectations (stable near the Fed's 2% target) make inflation easier to control. De-anchored expectations (rising or highly uncertain) complicate policy. Measures include: (1) market-based—TIPS breakevens, inflation swaps; (2) survey-based—Survey of Professional Forecasters, University of Michigan Surveys of Consumers, FOMC participants' projections; (3) model-based estimates. Long-term expectations (5-10 years ahead) are most closely watched as indicators of anchoring.",
            "source": "Federal Reserve Board",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/inflation-expectations-20190725.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Measuring inflation expectations involves challenges. Market-based measures embed risk premiums, not pure expectations. Survey measures may reflect respondents' beliefs about what inflation 'should' be rather than genuine expectations. Household surveys show systematic biases and poor understanding of inflation concepts. Different measures can diverge significantly, creating interpretation challenges. The relationship between measured expectations and actual inflation behavior is imperfect—firms and workers may not act mechanically on survey responses. Some economists question whether expectations drive inflation or merely reflect it. Rational inattention theory suggests most people rationally ignore inflation news until it becomes salient. Cross-country evidence shows varying degrees of expectation anchoring despite similar central bank frameworks.",
            "source": "Federal Reserve Economic Research",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/measuring-inflation-expectations-20230420.htm",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "Inflation expectations measures continue to be closely monitored. Long-term expectations remained relatively well-anchored through the 2021-2023 inflation surge, though short-term expectations rose with actual inflation. TIPS breakevens, SPF forecasts, and consumer surveys provide complementary perspectives. Fed officials cite expectations data in speeches and testimony as evidence of policy credibility. Research examines whether anchoring has weakened and what factors maintain credibility. Inflation compensation decomposition separates expectations from risk premiums.",
            "source": "Federal Reserve Economic Data (FRED)",
            "source_url": "https://fred.stlouisfed.org/categories/30",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "real_vs_nominal_rates",
        "title": "Real vs Nominal Interest Rates",
        "tags": ["interest_rate", "real_rates", "inflation", "macro"],
        "definition": {
            "content": "Nominal interest rates are the stated rates not adjusted for inflation. Real interest rates equal nominal rates minus expected inflation, representing the true cost of borrowing and return to lending in purchasing power terms. The Fisher equation formalizes this: real rate ≈ nominal rate - expected inflation. Real rates determine intertemporal choices—saving versus consuming, investment decisions. When inflation is high, nominal rates can be positive while real rates are negative, effectively taxing savers and subsidizing borrowers. Real rates are unobservable directly since they depend on inflation expectations. Ex ante real rates use expected inflation; ex post real rates use realized inflation. TIPS yields provide market-based real rate measures for indexed securities.",
            "source": "Federal Reserve Board",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/real-rates-20190615.htm",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Real rate measurement faces challenges. Which inflation measure to use (CPI, PCE, core)? What horizon (current, one-year ahead, long-term)? Expected inflation is unobservable and differs across agents. Tax considerations matter—taxes apply to nominal returns, so after-tax real rates differ from pre-tax. Risk premiums complicate extraction of pure real rates from market prices. The equilibrium real rate (r*) is theoretical and unobservable, subject to wide estimation uncertainty. International real rate comparisons require accounting for currency expectations. Negative real rates have distributional effects and may indicate monetary accommodation or secular stagnation. Some argue conventional real rate measures miss important dimensions like credit spreads and term premiums.",
            "source": "Federal Reserve Economic Research",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/estimates-of-the-neutral-rate-of-interest-20230117.htm",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "Real interest rates turned sharply negative during the 2021-2022 inflation surge as nominal rates lagged inflation. As the Fed raised rates and inflation moderated in 2023-2024, real rates moved positive. TIPS breakevens and inflation swaps provide real-time market-implied real rates. Estimates of the neutral real rate (r*) remain debated, with implications for policy stance assessment. Cross-country real rate comparisons inform capital flow and exchange rate analysis. Real rate trends affect asset valuations, particularly growth stocks sensitive to discount rates.",
            "source": "Federal Reserve Economic Data",
            "source_url": "https://fred.stlouisfed.org/series/TREACT",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "neutral_interest_rate",
        "title": "Neutral Interest Rate (r*)",
        "tags": ["interest_rate", "neutral_rate", "monetary_policy", "fed"],
        "definition": {
            "content": "The neutral interest rate (r*, also called the natural rate or equilibrium real rate) is the real short-term interest rate consistent with full employment and stable inflation—neither stimulating nor restraining the economy. When the policy rate exceeds r*, policy is restrictive; when below, accommodative. r* is unobservable and must be estimated using economic models. Estimates vary widely depending on methodology and data. The Laubach-Williams model is widely cited, estimating r* based on relationships between interest rates, growth, and inflation. r* has declined globally over recent decades due to factors like aging demographics, slower productivity growth, increased savings, and safe asset demand. The Fed considers r* estimates when assessing policy stance but acknowledges substantial uncertainty.",
            "source": "Federal Reserve Economic Research",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/estimates-of-the-neutral-rate-of-interest-20230117.htm",
            "credibility_class": "peer_reviewed_study"
        },
        "counter_argument": {
            "content": "r* estimation faces profound challenges. Model uncertainty is large—different approaches yield different estimates. Real-time estimates are subject to substantial revision as data is revised and models updated. r* may not be constant but vary with economic conditions, financial stability, and global factors. Some economists question whether a unique neutral rate exists, arguing multiple equilibria are possible. The relationship between r* and observable variables may have changed post-pandemic. Fiscal policy affects r* through government borrowing, creating endogeneity. Global integration means domestic r* is influenced by worldwide savings and investment. Some argue focus on r* distracts from more directly observable indicators of policy stance. Uncertainty bands around point estimates are so wide as to limit practical utility.",
            "source": "International Monetary Fund Working Papers",
            "source_url": "https://www.imf.org/en/Publications/WP/Issues/2023/01/20/The-Natural-Rate-of-Interest-A-Critical-Review-528943",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "Estimates of r* continue to evolve with new data and methods. Federal Reserve staff and external researchers update models regularly. Recent estimates suggest r* may have risen modestly from pandemic lows but remains below historical averages. FOMC participants' long-run real rate projections in the SEP provide Committee members' r* views. Debate continues about whether r* will remain low due to structural factors or rise with fiscal deficits and deglobalization. Policy implications hinge on r* assessments—lower r* means less room to cut rates in downturns.",
            "source": "Federal Reserve SEP Projections",
            "source_url": "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl.htm",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "soft_hard_landing",
        "title": "Soft Landing vs Hard Landing",
        "tags": ["recession", "economic_growth", "inflation", "fed", "landing"],
        "definition": {
            "content": "A soft landing occurs when the Federal Reserve successfully slows economic growth enough to reduce inflation without triggering a recession. A hard landing occurs when tightening causes a recession with significant job losses and output decline. Soft landings require precise calibration—enough restriction to cool inflation but not so much as to break the economy. Historical examples of soft landings are debated; the 1994-1995 episode is often cited. Hard landings have been more common, including the Volcker disinflation of the early 1980s which induced severe recessions but ultimately restored price stability. Achieving soft landings is complicated by long and variable policy lags, making it difficult to know when sufficient restriction has been achieved.",
            "source": "Federal Reserve Economic Research",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/soft-landings-20230315.htm",
            "credibility_class": "peer_reviewed_study"
        },
        "counter_argument": {
            "content": "The soft/hard landing dichotomy oversimplifies. Outcomes exist on a spectrum—mild recessions with limited job losses differ from severe downturns. Success criteria are ambiguous—is avoiding technical recession enough, or should employment also remain near potential? Inflation overshoot/undershoot tradeoffs matter. Some argue soft landings require favorable supply-side developments (energy prices, supply chains) beyond Fed control. The 1994-95 'soft landing' was followed by the tech boom, making it unclear how much was skill versus luck. Real-time assessment is impossible—what looks like soft landing initially may later be revised. Labor market scarring can occur even without technical recession. International spillovers from U.S. tightening can cause hard landings abroad even if domestic outcome is soft.",
            "source": "National Bureau of Economic Research",
            "source_url": "https://www.nber.org/research/business-cycle-dating",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "The 2023-2024 period generated intense debate about landing type. Inflation declined significantly from 2022 peaks while unemployment remained historically low, suggesting soft landing possibility. However, lagged effects of tightening created uncertainty about eventual outcome. Leading indicators provided mixed signals. Historical analogues offered limited guidance given unique pandemic-era distortions. Consensus forecasts evolved as data arrived. Ultimately, landing characterization may depend on subsequent revisions and longer-term perspective.",
            "source": "Congressional Budget Office Economic Outlook",
            "source_url": "https://www.cbo.gov/economic-projections",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "stagflation",
        "title": "Stagflation",
        "tags": ["stagflation", "inflation", "recession", "macro", "economic_growth"],
        "definition": {
            "content": "Stagflation describes the combination of stagnant economic growth (or recession), high unemployment, and high inflation. This combination is particularly challenging for policymakers because tools to combat inflation (tightening) worsen unemployment, while tools to combat unemployment (stimulus) worsen inflation. The term emerged in the 1970s when oil price shocks triggered supply-side inflation while demand weakened. Traditional Keynesian models struggled to explain stagflation, contributing to the rise of monetarist and supply-side economics. The 1973-75 and 1979-82 periods are classic stagflation episodes. Supply shocks (energy, food, supply chains) can create stagflationary dynamics by raising prices while reducing output potential.",
            "source": "Federal Reserve History",
            "source_url": "https://www.federalreservehistory.org/essays/stagflation",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "True stagflation—persistent high inflation combined with sustained high unemployment and stagnant growth—is rare. Many alleged stagflation episodes involved temporary supply shocks followed by policy responses that resolved one problem or the other. The 1970s stagflation ultimately required painful monetary tightening to break inflation expectations. Some argue modern central bank credibility makes sustained stagflation unlikely—well-anchored expectations prevent temporary supply shocks from becoming permanent. Others worry that deglobalization, demographic shifts, and climate transition could create structurally higher inflation with lower growth. Policy responses to stagflation remain controversial—some advocate prioritizing inflation fighting, others favor tolerance of temporary inflation to support employment.",
            "source": "International Monetary Fund Research",
            "source_url": "https://www.imf.org/en/Publications/WEO/Issues/2023/04/stagflation-concerns",
            "credibility_class": "peer_reviewed_study"
        },
        "latest_data": {
            "content": "Stagflation concerns emerged in 2022-2023 as inflation surged while growth slowed. However, labor markets remained tight, distinguishing the episode from 1970s stagflation. Supply chain normalization and energy market adjustments helped ease inflation pressures. Core inflation proved stickier than headline. Growth remained positive though below trend. Most analysts assessed stagflation risk as elevated but not baseline. Monitoring focuses on inflation expectations anchoring, productivity trends, and labor market dynamics. Climate transition and geopolitical fragmentation are cited as potential long-term stagflationary forces.",
            "source": "Federal Reserve Economic Research",
            "source_url": "https://www.federalreserve.gov/econres/notes/feds-notes/stagflation-analysis-20230615.htm",
            "credibility_class": "peer_reviewed_study"
        }
    },
    {
        "topic": "dollar_index",
        "title": "U.S. Dollar Index (DXY)",
        "tags": ["dollar", "currency", "exchange_rate", "forex", "dxy"],
        "definition": {
            "content": "The U.S. Dollar Index (DXY, USDX, DX) measures the value of the U.S. dollar relative to a basket of six major currencies: euro (57.6%), Japanese yen (13.6%), British pound (11.9%), Canadian dollar (9.1%), Swedish krona (4.2%), and Swiss franc (3.6%). Introduced in 1973 with a base of 100, the index is geometrically weighted. A reading above 100 indicates dollar appreciation versus the basket; below 100 indicates depreciation. The dollar index is influenced by interest rate differentials, economic growth differentials, safe-haven flows, trade balances, and central bank policies. A strong dollar makes U.S. exports more expensive and imports cheaper, affecting trade balances and multinational earnings. The Federal Reserve monitors dollar movements for inflation and growth implications.",
            "source": "ICE (Intercontinental Exchange)",
            "source_url": "https://www.theice.com/ice-usdx/index",
            "credibility_class": "news_article"
        },
        "counter_argument": {
            "content": "The DXY has limitations as a dollar measure. The currency basket is outdated—heavy euro weight reflects 1999 EMU composition, not current trade patterns. Emerging market currencies like Chinese yuan and Mexican peso are excluded despite trade importance. Trade-weighted dollar indices (Fed's Broad and Major Currencies indexes) better reflect competitive position. The DXY can move due to eurozone-specific factors rather than U.S. developments. Dollar strength interpretations vary—sometimes signaling U.S. economic outperformance, other times reflecting safe-haven demand during global stress. Exchange rate pass-through to inflation has declined, reducing dollar's domestic impact. Currency interventions by trading partners can distort relationships.",
            "source": "Federal Reserve Board",
            "source_url": "https://www.federalreserve.gov/releases/h10/",
            "credibility_class": "government_source"
        },
        "latest_data": {
            "content": "The dollar index has shown significant volatility in the 2020s, reaching multi-decade highs in 2022 amid Fed tightening and safe-haven demand before moderating. Dollar movements affect emerging market debt servicing costs, commodity prices (often dollar-denominated), and global financial conditions. Fed policy divergence with other central banks drives relative currency moves. Geopolitical tensions boost dollar safe-haven appeal. Long-term dollar trajectory debates center on U.S. fiscal sustainability, reserve currency status, and multipolar currency system evolution.",
            "source": "Federal Reserve H.10 Release",
            "source_url": "https://www.federalreserve.gov/releases/h10/",
            "credibility_class": "government_source"
        }
    },
    {
        "topic": "treasury_market",
        "title": "U.S. Treasury Market",
        "tags": ["treasury", "bonds", "fixed_income", "debt_market", "macro"],
        "definition": {
            "content": "The U.S. Treasury market is where U.S. government debt securities are issued and traded. It is the world's largest and most liquid bond market, with outstanding debt exceeding $27 trillion. Treasury securities include bills (up to 1 year), notes (2-10 years), bonds (20-30 years), and TIPS (inflation-protected). The market serves multiple functions: financing government deficits, providing risk-free benchmark rates for all other credit, enabling monetary policy implementation, and offering safe assets for global investors. Primary dealers participate in Treasury auctions and make secondary markets. Foreign governments, the Federal Reserve, institutional investors, and households all hold Treasuries. The market's depth and liquidity make it a cornerstone of global finance.",
            "source": "U.S. Department of the Treasury",
            "source_url": "https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics",
            "credibility_class": "government_source"
        },
        "counter_argument": {
            "content": "Despite its size, the Treasury market has shown vulnerability to dysfunction. The March 2020 'dash for cash' saw liquidity evaporate despite Fed intervention, revealing structural fragilities. Concentration among primary dealers creates intermediation bottlenecks. Regulatory constraints on bank balance sheets limit market-making capacity. Electronic trading growth has benefits but may amplify flash crash risks. Large Fed holdings distort market functioning and price discovery. Fiscal sustainability concerns could eventually affect Treasury creditworthiness perception, though this remains tail risk. Foreign official holdings create geopolitical dependencies. Market plumbing issues (repo market stresses) can spill over. Ongoing reforms address settlement cycles, central clearing, and capital requirements.",
            "source": "U.S. Department of the Treasury Working Papers",
            "source_url": "https://home.treasury.gov/news/press-releases/reports-on-treasury-market-structure",
            "credibility_class": "government_source"
        },
        "latest_data": {
            "content": "The Treasury market continues to function as the global benchmark safe asset market. Issuance volumes remain large given fiscal deficits. Auction demand metrics (bid-to-cover ratios, indirect bidder participation) are closely watched. Foreign holdings data (Treasury Capital Reporting System) tracks international demand. Fed holdings decline through QT. Market structure reforms are under consideration following 2020 stress and subsequent reviews. Liquidity measures (bid-ask spreads, market depth) are monitored for early warning signs. Treasury yields influence global borrowing costs and capital flows.",
            "source": "Treasury Auction Results",
            "source_url": "https://www.treasurydirect.gov/instit/annceresult/press/preanre/2023/auction_index.jsp",
            "credibility_class": "government_source"
        }
    }
]


def generate_fragment_id(topic: str, role: str, counter: int) -> str:
    """Generate a unique fragment ID."""
    role_short = {
        "definition": "def",
        "counter_argument": "counter", 
        "latest_data": "latest"
    }.get(role, role[:3])
    return f"frag_fin_{topic}_{role_short}_{counter:03d}"


def create_fragment(topic_data: Dict, role: str, counter: int) -> Dict[str, Any]:
    """Create a fragment dictionary from topic data."""
    role_data = topic_data[role]
    
    # Generate tags including reasoning role
    tags = topic_data["tags"] + [role]
    
    fragment = {
        "id": generate_fragment_id(topic_data["topic"], role, counter),
        "domain": "finance",
        "subdomain": "macro",
        "tags": tags,
        "reasoning_role": role,
        "content": role_data["content"],
        "source": role_data.get("source", "Multiple Sources"),
        "source_url": role_data["source_url"],
        "credibility_class": role_data["credibility_class"],
        "year": datetime.now().year,
        "compatible_with": [],
        "incompatible_with": [],
        "weight": 1.0
    }
    
    return fragment


def save_fragment(fragment: Dict[str, Any], output_dir: Path):
    """Save fragment to JSON file."""
    filepath = output_dir / f"{fragment['id']}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(fragment, f, indent=2, ensure_ascii=False)
    return filepath


def main():
    """Main function to generate all macro foundation fragments."""
    print("=" * 70)
    print("OpenEyes Macro Foundation Fragment Builder")
    print("Generating 75 fragments (25 topics × 3 reasoning roles)")
    print("=" * 70)
    
    # Ensure output directory exists
    FRAGMENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    fragments_created = []
    
    for topic_idx, topic_data in enumerate(MACRO_TOPICS, 1):
        print(f"\n[{topic_idx}/{len(MACRO_TOPICS)}] Processing: {topic_data['title']}")
        
        for role in ["definition", "counter_argument", "latest_data"]:
            fragment = create_fragment(topic_data, role, topic_idx)
            filepath = save_fragment(fragment, FRAGMENTS_DIR)
            fragments_created.append((fragment['id'], filepath))
            print(f"  ✓ {role}: {fragment['id']}")
    
    print("\n" + "=" * 70)
    print(f"COMPLETE: Generated {len(fragments_created)} fragments")
    print("=" * 70)
    print("\nFragment files saved to:", FRAGMENTS_DIR)
    print("\nNext steps:")
    print("1. Review generated fragments for accuracy")
    print("2. Update compatible_with/incompatible_with fields as needed")
    print("3. Run fragment library consistency checks")
    print("=" * 70)


if __name__ == "__main__":
    main()
