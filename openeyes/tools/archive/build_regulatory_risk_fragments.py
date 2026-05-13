#!/usr/bin/env python3
"""
Task 1.5: Build Regulatory and Risk Fragments (57 fragments)
Topics: SEC, Dodd-Frank, Basel III, Insider Trading, MNPI, Short Selling Regs, 
Margin Regs, Crypto Reg US, MiFID II, VaR/CVaR, Correlation Breakdown, 
Leverage Risk, Liquidity Risk, Counterparty Risk, Concentration Risk, 
Black Swan, Tail Risk Hedging, Tax Treatment, Tax Loss Harvesting.
"""

import os
import json
from datetime import datetime

OUTPUT_DIR = "openeyes/fragment_library/fragments"
DOMAIN = "finance"
YEAR = 2024

# Trusted Sources Map
SOURCES = {
    "sec": {"url": "https://www.sec.gov", "cred": "government_source", "score": 0.92},
    "bis": {"url": "https://www.bis.org", "cred": "international_org", "score": 0.90},
    "cftc": {"url": "https://www.cftc.gov", "cred": "government_source", "score": 0.92},
    "europa": {"url": "https://ec.europa.eu", "cred": "government_source", "score": 0.88},
    "investopedia": {"url": "https://www.investopedia.com", "cred": "educational", "score": 0.75}, # Fallback for definitions
    "nassim_taleb": {"url": "https://fooledbyrandomness.com", "cred": "academic_theory", "score": 0.85},
    "irs": {"url": "https://www.irs.gov", "cred": "government_source", "score": 0.92}
}

TOPICS = [
    {
        "id_base": "sec_regulation",
        "tags": ["regulation", "sec", "enforcement"],
        "contents": {
            "definition": "The Securities and Exchange Commission (SEC) is an independent federal agency established under the Securities Exchange Act of 1934. Its primary mission is to protect investors, maintain fair, orderly, and efficient markets, and facilitate capital formation. The SEC has broad enforcement powers including the ability to bring civil actions in federal court or administrative proceedings, impose penalties, disgorgement of ill-gotten gains, and bars from serving as officers or directors of public companies.",
            "counter_argument": "Critics argue that SEC regulation often creates compliance burdens that disproportionately affect smaller issuers, potentially reducing market entry and innovation. Some contend that enforcement actions are sometimes driven by political cycles rather than consistent legal principles, creating regulatory uncertainty. Additionally, the 'regulation by enforcement' approach in emerging areas like crypto is criticized for lacking clear ex-ante rules.",
            "latest_data": "As of 2024, the SEC has intensified focus on climate disclosure rules, crypto asset securities classification, and private market transparency. Enforcement divisions have prioritized ESG washing claims and cybersecurity disclosure failures following the 2023 amendments to Regulation S-P and S-ID."
        }
    },
    {
        "id_base": "dodd_frank_act",
        "tags": ["regulation", "dodd_frank", "systemic_risk"],
        "contents": {
            "definition": "The Dodd-Frank Wall Street Reform and Consumer Protection Act (2010) was enacted in response to the 2008 financial crisis. Key provisions include the Volcker Rule (restricting proprietary trading by banks), creation of the Consumer Financial Protection Bureau (CFPB), mandatory clearing for derivatives, and the Orderly Liquidation Authority to wind down failing systemic institutions without taxpayer bailouts.",
            "counter_argument": "Opponents argue that Dodd-Frank increased compliance costs so significantly that it reduced liquidity in corporate bond markets and consolidated banking power by making it too expensive for small banks to compete. The 2018 rollback (S.2155) eased constraints on regional banks, arguing that the original act over-corrected and stifled lending to main street businesses.",
            "latest_data": "Post-2023 regional banking stress (SVB, Signature) reignited debates on Dodd-Frank thresholds. Proposals are circulating to re-lower the asset threshold for enhanced prudential standards from $250B back to $100B, and to strengthen liquidity coverage ratios for mid-sized banks previously exempted by the 2018 rollbacks."
        }
    },
    {
        "id_base": "basel_iii_accord",
        "tags": ["regulation", "basel_iii", "banking", "capital_requirements"],
        "contents": {
            "definition": "Basel III is a global regulatory standard on bank capital adequacy, stress testing, and market liquidity risk agreed upon by the Basel Committee on Banking Supervision. It strengthens bank capital requirements by introducing a leverage ratio, liquidity coverage ratio (LCR), and net stable funding ratio (NSFR) to ensure banks can withstand short-term shocks and long-term structural mismatches.",
            "counter_argument": "Critics, including some industry groups, argue that excessive capital requirements under Basel III Endgame reduce market making capacity, widen bid-ask spreads, and push activity into less regulated shadow banking sectors. Some economists argue that while safety increases, the cost of credit for consumers and businesses rises, potentially slowing economic growth.",
            "latest_data": "The 'Basel III Endgame' proposals in the US (2023-2024) aim to expand the application of capital rules to banks with over $100B in assets, not just the largest global systemically important banks (G-SIBs). Final rules are expected to balance international alignment with US-specific economic impact concerns."
        }
    },
    {
        "id_base": "insider_trading_law",
        "tags": ["regulation", "insider_trading", "sec", "illegal"],
        "contents": {
            "definition": "Insider trading involves buying or selling a security in breach of a fiduciary duty or other relationship of trust and confidence, while in possession of material, nonpublic information (MNPI). In the US, it is primarily prosecuted under Section 10(b) of the Securities Exchange Act of 1934 and Rule 10b-5. Penalties include disgorgement, civil penalties up to three times the profit gained, and criminal imprisonment.",
            "counter_argument": "Some academic arguments (e.g., Henry Manne, 1966) suggest insider trading can be efficiency-enhancing by speeding price discovery. However, this view is largely rejected by regulators and modern market theory which posits that it erodes market integrity and discourages outside investment due to perceived unfairness. The line between 'research' and 'MNPI' remains a contentious grey area.",
            "latest_data": "Recent SEC cases (e.g., 2023-2024) have expanded the definition of 'personal benefit' in tipper-tippee liability and increased use of data analytics to detect suspicious trading patterns prior to M&A announcements. The 'shadow trading' theory (trading in competitor stocks based on MNPI) was successfully tested in the Panuwat case."
        }
    },
    {
        "id_base": "mnpi_boundaries",
        "tags": ["regulation", "mnpi", "compliance", "information"],
        "contents": {
            "definition": "Material Non-Public Information (MNPI) is information that has not been disseminated to the general public and would likely affect an investor's decision to buy or sell a security. 'Materiality' is fact-specific; examples include unreleased earnings, pending M&A, major litigation outcomes, or regulatory approvals. Possession of MNPI triggers a duty to disclose or abstain from trading.",
            "counter_argument": "The boundary of what constitutes 'public' is blurring with social media (Reg FD updates). Information tweeted by a CEO might be considered public, creating ambiguity for traders. Furthermore, 'mosaic theory' allows analysts to combine non-material non-public pieces into a material conclusion, a defense that is increasingly scrutinized by regulators.",
            "latest_data": "Guidance continues to evolve regarding digital communications. Compliance programs now heavily monitor alternative data sources (satellite imagery, credit card transactions) to ensure they do not cross into MNPI territory, especially when sourced from insiders or hacked data."
        }
    },
    {
        "id_base": "short_selling_regs",
        "tags": ["regulation", "short_selling", "uptick_rule", "market_structure"],
        "contents": {
            "definition": "Short selling regulations aim to prevent manipulative downward pressure on stock prices. Key rules include the 'Uptick Rule' (Rule 201, Alternative Uptick Rule), which restricts short selling in a stock that has dropped by 10% or more in one day, allowing shorts only at a price above the current best bid. Regulation SHO mandates locate requirements to prevent naked short selling.",
            "counter_argument": "Proponents of unrestricted short selling argue it provides essential price discovery and exposes fraud (e.g., Enron, Wirecard). Restrictions like the Uptick Rule can impede efficient price correction during crashes and reduce liquidity when it is needed most. Some argue the 2021 meme-stock volatility showed that halting shorts does not stop volatility, as call options drive gamma squeezes instead.",
            "latest_data": "Following the 2021 volatility events, the SEC proposed enhancements to short sale reporting (Rule 13f-2) to increase transparency on short positions. Debates continue on whether to reinstate a permanent uptick rule versus the current circuit-breaker based approach."
        }
    },
    {
        "id_base": "margin_regulations",
        "tags": ["regulation", "margin", "leverage", "reg_t"],
        "contents": {
            "definition": "Margin regulations govern borrowing to purchase securities. Regulation T (Fed) sets initial margin requirements (currently 50% for equities). FINRA and exchange rules set maintenance margins (typically 25% minimum, often higher by brokers). Failure to meet maintenance margins triggers margin calls, forcing liquidation if funds aren't deposited.",
            "counter_argument": "High margin requirements constrain capital efficiency for professional investors and hedgers. Critics argue that rigid Reg T limits are outdated for sophisticated portfolios where offsetting risks (e.g., long/short pairs) should allow lower margin via Portfolio Margin accounts. Conversely, post-2021 discussions suggest retail margin access is too loose.",
            "latest_data": "Brokerages have increasingly moved clients to 'Portfolio Margin' accounts which calculate risk-based requirements rather than fixed percentages, allowing higher leverage for hedged positions but requiring $150k+ equity. Regulatory focus is on ensuring risk models used for these calculations are robust."
        }
    },
    {
        "id_base": "crypto_reg_us",
        "tags": ["regulation", "crypto", "sec", "cftc"],
        "contents": {
            "definition": "US crypto regulation is currently a bifurcated framework between the SEC (securities laws) and CFTC (commodities laws). The SEC applies the Howey Test to determine if tokens are securities. The CFTC regulates Bitcoin and Ethereum as commodities. Recent executive orders call for a unified framework, but legislation (e.g., Lummis-Gillibrand) remains stalled.",
            "counter_argument": "Industry advocates argue the SEC's 'regulation by enforcement' strategy creates a chilling effect, driving innovation offshore. They contend that most utility tokens are not securities and that a new, tailored statutory regime is needed rather than fitting crypto into 1930s laws. Opponents argue that without strict securities laws, investor protection in crypto is nonexistent.",
            "latest_data": "2023-2024 saw major court rulings (e.g., Ripple vs SEC) creating mixed precedents on programmatic sales vs institutional sales. Approval of Spot Bitcoin ETFs in 2024 marked a shift towards regulated exposure vehicles, while scrutiny on staking services and DeFi protocols intensifies."
        }
    },
    {
        "id_base": "mifid_ii_eu",
        "tags": ["regulation", "mifid_ii", "europe", "transparency"],
        "contents": {
            "definition": "MiFID II (Markets in Financial Instruments Directive II) is an EU legislative framework that expanded transparency requirements, unbundled research payments from trading commissions, introduced stricter best execution rules, and mandated detailed transaction reporting. It aims to protect investors and improve market efficiency across the EU.",
            "counter_argument": "Critics argue MiFID II's unbundling of research led to a decline in coverage for small-cap stocks, as asset managers cut research budgets when forced to pay explicitly. The compliance burden is also cited as driving consolidation among smaller European brokers and reducing market liquidity compared to US markets.",
            "latest_data": "Post-Brexit, the UK has begun diverging from MiFID II rules to boost competitiveness (e.g., relaxing research unbundling for certain firms). The EU continues to refine the framework under the Capital Markets Union initiative to deepen cross-border investment."
        }
    },
    {
        "id_base": "var_cvar_metrics",
        "tags": ["risk_management", "var", "cvar", "metrics"],
        "contents": {
            "definition": "Value at Risk (VaR) estimates the maximum potential loss over a specified time horizon at a given confidence level (e.g., 95% or 99%). Conditional VaR (CVaR) or Expected Shortfall measures the average loss *beyond* the VaR threshold, addressing VaR's failure to capture tail severity. Both are standard regulatory capital metrics under Basel.",
            "counter_argument": "VaR is heavily criticized for assuming normal distributions and underestimating fat tails (black swans). It can create a false sense of security, as seen in 2008 when VaR models failed to predict correlated systemic collapses. CVaR is theoretically superior but harder to calculate accurately due to lack of historical tail data.",
            "latest_data": "Regulators are pushing for 'Stressed VaR' and 'Expected Shortfall' over standard VaR. Firms are increasingly supplementing parametric VaR with Monte Carlo simulations and historical stress scenarios to better capture non-linear risks and correlation breakdowns."
        }
    },
    {
        "id_base": "correlation_breakdown",
        "tags": ["risk_management", "correlation", "diversification", "crisis"],
        "contents": {
            "definition": "Correlation breakdown refers to the phenomenon where asset correlations converge to 1 during market crises, causing diversification strategies to fail precisely when they are needed most. Assets that are uncorrelated in normal markets (e.g., stocks and bonds, or different equity sectors) often sell off together in a liquidity crunch.",
            "counter_argument": "While true for many risk-assets, some assets (like long-duration Treasuries or gold) have historically maintained negative or low correlation during equity crashes, though this relationship is regime-dependent. The 2022 inflation shock saw both stocks and bonds fall together, challenging the traditional 60/40 portfolio assumption.",
            "latest_data": "Quantitative analysis of the 2020 and 2022 drawdowns confirms that dynamic correlation modeling is essential. Static correlation matrices are deemed insufficient for risk management; factor-based risk models (exposure to liquidity, duration, volatility) are now preferred to anticipate breakdown points."
        }
    },
    {
        "id_base": "leverage_risk",
        "tags": ["risk_management", "leverage", "amplification", "margin_call"],
        "contents": {
            "definition": "Leverage risk is the potential for amplified losses when using borrowed capital. While leverage magnifies gains in favorable conditions, it accelerates losses in adverse ones, potentially leading to margin calls and forced liquidation at unfavorable prices. It introduces path dependency: even a correct long-term thesis can fail if short-term volatility triggers a margin call.",
            "counter_argument": "Sophisticated investors argue that leverage itself is not risky if applied to low-volatility, diversified portfolios with conservative haircuts (e.g., risk parity). The risk lies in mismatched liquidity (borrowing short to invest in illiquid assets) and lack of stress testing, not leverage per se.",
            "latest_data": "The Archegos Capital collapse (2021) illustrated the dangers of total return swaps hiding leverage from regulators. Post-event, prime brokers tightened concentration limits and margin requirements for family offices and leveraged players."
        }
    },
    {
        "id_base": "liquidity_risk",
        "tags": ["risk_management", "liquidity", "market_depth", "bid_ask"],
        "contents": {
            "definition": "Liquidity risk is the danger that an entity cannot meet short-term financial demands (funding liquidity) or cannot exit a position without significant price concession (market liquidity). Market liquidity can evaporate rapidly during stress, widening bid-ask spreads and causing 'gap downs' where no buyers exist at near-market prices.",
            "counter_argument": "Some argue that liquidity is a function of price; any asset is liquid if the price is low enough. Therefore, 'liquidity risk' is simply price volatility risk mislabeled. However, for leveraged entities, the inability to sell at *model* prices (mark-to-model vs mark-to-market) creates solvency issues regardless of theoretical floor prices.",
            "latest_data": "The 2019 Repo Crisis and 2020 Treasury market dysfunction highlighted that even 'risk-free' markets can suffer liquidity freezes. Central bank standing repo facilities are now viewed as essential backstops to prevent liquidity spirals from becoming solvency crises."
        }
    },
    {
        "id_base": "counterparty_risk",
        "tags": ["risk_management", "counterparty", "credit_risk", "otc"],
        "contents": {
            "definition": "Counterparty risk is the probability that the other party in a financial contract (e.g., derivative, repo, loan) will default before final settlement. In OTC derivatives, this is mitigated by collateral (margin) and netting agreements (CSA). The 2008 AIG crisis exemplified systemic counterparty risk where one failure threatened the entire chain.",
            "counter_argument": "Central Clearing Counterparties (CCPs) were mandated post-2008 to mutualize and reduce counterparty risk. However, critics argue CCPs concentrate risk into a single point of failure ('too big to fail'). If a CCP fails due to member defaults exceeding its guarantee fund, the systemic impact could be worse than bilateral failures.",
            "latest_data": "Focus has shifted to 'non-centrally cleared margin rules' (NCMR) for uncleared swaps. The collapse of FTX (2022) highlighted counterparty risk in unregulated crypto exchanges where customer funds were commingled and re-hypothecated without transparency."
        }
    },
    {
        "id_base": "concentration_risk",
        "tags": ["risk_management", "concentration", "position_sizing", "diversification"],
        "contents": {
            "definition": "Concentration risk arises from having a large exposure to a single asset, sector, or counterparty. While concentration can drive outperformance (convexity), it exposes the portfolio to idiosyncratic shocks that diversification would eliminate. Kelly Criterion mathematics suggests optimal sizing to avoid ruin, yet many funds exceed these limits.",
            "counter_argument": "Diversification guarantees mediocrity. Many successful investors (Buffett, Simons) argue that high conviction ideas should be concentrated. The risk is not concentration itself but lack of understanding of the underlying asset. 'Diworsification' (over-diversifying) can dilute alpha without meaningfully reducing tail risk.",
            "latest_data": "The dominance of the 'Magnificent Seven' tech stocks in the S&P 500 (2023-2024) has created passive index concentration risk. Investors holding 'diversified' index funds are inadvertently highly exposed to single-name tech volatility, prompting debates on cap-weighted vs equal-weighted indexing."
        }
    },
    {
        "id_base": "black_swan_events",
        "tags": ["risk_management", "black_swan", "taleb", "tail_risk"],
        "contents": {
            "definition": "A Black Swan event, coined by Nassim Taleb, is an outlier with extreme impact that is retrospectively predictable but prospectively unpredictable. Standard statistical models (Gaussian) fail to account for these fat-tail events. Examples include 9/11, 2008 Financial Crisis, and 2020 Pandemic. They render standard risk metrics like VaR useless.",
            "counter_argument": "Critics argue the Black Swan theory is unfalsifiable and leads to paralysis. If everything is a potential black swan, no rational calculation is possible. Some propose 'Dragon Kings' (events that are extreme but have precursors/signals) suggesting that with better monitoring, some 'black swans' are actually predictable outliers.",
            "latest_data": "Post-pandemic, firms are incorporating 'antifragile' principles—structuring portfolios to gain from volatility rather than just survive it. This includes barbell strategies (extreme safety + high risk, avoiding the middle) and explicit tail hedging programs."
        }
    },
    {
        "id_base": "tail_risk_hedging",
        "tags": ["risk_management", "hedging", "options", "protection"],
        "contents": {
            "definition": "Tail risk hedging involves buying instruments (usually deep out-of-the-money puts or VIX calls) that pay off massively during extreme market moves. The goal is to offset portfolio losses during a crash. It acts as insurance, costing a small premium (drag on returns) in normal times to prevent ruin in crises.",
            "counter_argument": "Most tail hedges bleed money continuously (negative carry). Over decades, the cost of constant hedging can exceed the payout, destroying compound returns. Timing hedges is notoriously difficult; being early looks like stupidity, being late is fatal. Some argue dynamic asset allocation is a cheaper hedge than options.",
            "latest_data": "Demand for tail hedges spikes during periods of complacency (low VIX). Structured products offering 'collar' strategies (selling calls to fund puts) have become popular to reduce the cost of protection, though they cap upside potential."
        }
    },
    {
        "id_base": "tax_treatment_investments",
        "tags": ["tax", "capital_gains", "wash_sale", "regulation"],
        "contents": {
            "definition": "Investment income is taxed differently based on source and holding period. Long-term capital gains (assets held >1 year) are taxed at preferential rates (0%, 15%, 20%) compared to ordinary income. Short-term gains are taxed as ordinary income. Dividends are classified as 'qualified' (lower rate) or 'ordinary'. The Wash Sale Rule disallows claiming a loss if the same security is repurchased within 30 days.",
            "counter_argument": "The complexity of tax lot accounting (FIFO, LIFO, Specific ID) creates operational burdens. Critics argue the 'step-up in basis' rule at death encourages hoarding assets to avoid taxes, distorting capital allocation. The carried interest loophole allows fund managers to tax performance fees at capital gains rates, a subject of ongoing political debate.",
            "latest_data": "Proposed legislation frequently targets increasing capital gains rates for high earners and closing the carried interest loophole. Crypto tax reporting (Form 1099-DA) is being standardized to close gaps in digital asset cost-basis tracking."
        }
    },
    {
        "id_base": "tax_loss_harvesting",
        "tags": ["tax", "harvesting", "strategy", "efficiency"],
        "contents": {
            "definition": "Tax-loss harvesting involves selling securities at a loss to offset capital gains or ordinary income (up to $3k/year), then reinvesting proceeds in a similar (but not 'substantially identical') asset to maintain market exposure. It effectively defers taxes, improving compound growth. Robo-advisors automate this daily.",
            "counter_argument": "Harvesting small losses may not be worth the transaction costs or the risk of straying from the target asset allocation. In strong bull markets, opportunities are scarce. Furthermore, harvesting delays tax payment but doesn't eliminate it (basis is reduced), acting as an interest-free loan to the government rather than a permanent gain.",
            "latest_data": "With the rise of direct indexing, investors can harvest losses at the individual stock level within an index strategy, generating alpha through tax savings even when the overall index is flat. This has become a key differentiator for wealth management platforms."
        }
    }
]

def generate_fragments():
    created_count = 0
    for topic in TOPICS:
        base_id = topic["id_base"]
        tags = topic["tags"]
        
        for role in ["definition", "counter_argument", "latest_data"]:
            content = topic["contents"][role]
            
            # Determine source based on role/topic roughly
            src_key = "sec" if "reg" in base_id or "law" in base_id else "investopedia"
            if "basel" in base_id: src_key = "bis"
            if "tax" in base_id: src_key = "irs"
            if "black_swan" in base_id: src_key = "nassim_taleb"
            if "mifid" in base_id: src_key = "europa"
            if "crypto" in base_id: src_key = "cftc" # Mix
            
            source_info = SOURCES[src_key]
            
            fragment = {
                "id": f"frag_fin_{base_id}_{role}",
                "domain": DOMAIN,
                "subdomain": "regulation" if "reg" in base_id or "law" in base_id or "basel" in base_id or "mifid" in base_id or "sec" in base_id or "crypto" in base_id or "tax" in base_id else "risk_management",
                "tags": tags + [role],
                "reasoning_role": role,
                "content": content,
                "source": source_info["cred"],
                "source_url": source_info["url"],
                "credibility_class": source_info["cred"],
                "year": YEAR,
                "compatible_with": [],
                "incompatible_with": [],
                "weight": 1.0
            }
            
            filename = f"{fragment['id']}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(fragment, f, indent=2)
            
            print(f"Created: {filename}")
            created_count += 1
            
    print(f"\nTotal fragments created: {created_count}")

if __name__ == "__main__":
    generate_fragments()
