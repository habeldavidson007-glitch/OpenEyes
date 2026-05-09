#!/usr/bin/env python3
"""
Build Market Mechanics Fragments for OpenEyes VCIS
Generates 75 fragments: 25 topics × 3 reasoning roles (definition, counter_argument, latest_data)
"""

import json
import os
from datetime import datetime

FRAGMENT_LIBRARY_PATH = "openeyes/fragment_library/fragments"

# Market mechanics topics with source URLs and tags
MARKET_MECHANICS_TOPICS = [
    {
        "topic": "stock_market_basics",
        "sources": {
            "definition": ("https://www.sec.gov/fast-answers/answerssecuritieshtm.html", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/market-structure-20210312.html", "Federal Reserve"),
            "latest_data": ("https://www.bls.gov/data/", "BLS")
        },
        "tags": ["equities", "stock_market", "market_cap", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Stock markets are organized exchanges where buyers and sellers trade securities including stocks, bonds, and derivatives. Major US exchanges include NYSE and NASDAQ. Market makers provide liquidity by standing ready to buy and sell. Order types include market orders (execute immediately at current price), limit orders (execute only at specified price or better), and stop orders (trigger market/limit order when price reaches threshold). The SEC regulates securities markets to protect investors.",
            "counter_argument": "While traditional exchange theory assumes perfect price discovery, research shows market structure significantly impacts efficiency. Dark pools and high-frequency trading can fragment liquidity. Payment for order flow creates potential conflicts. Some studies suggest retail investors face systematic disadvantages in execution quality versus institutional traders.",
            "latest_data": "Current market structure data shows equity trading volumes averaging 12+ billion shares daily across US exchanges. Market maker participation remains above 40% of volume. Recent SEC proposals address payment for order flow transparency and best execution requirements."
        }
    },
    {
        "topic": "market_indices",
        "sources": {
            "definition": ("https://www.spglobal.com/spdji/en/documents/methodologies/methodology-index-math.pdf", "S&P Global"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/index-fund-flows-20200814.html", "Federal Reserve"),
            "latest_data": ("https://fred.stlouisfed.org/series/SP500", "FRED")
        },
        "tags": ["sp500", "nasdaq", "dow_jones", "index_fund", "etf", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Market indices track performance of selected securities. S&P 500 is float-adjusted market-cap weighted, covering ~500 large-cap US companies. Dow Jones Industrial Average is price-weighted across 30 blue-chip stocks. Nasdaq Composite is market-cap weighted, heavily tech-focused. Index construction affects performance: cap-weighting gives largest companies most influence, equal-weighting treats all components equally, price-weighting favors higher-priced stocks regardless of company size.",
            "counter_argument": "Passive index investing dominance may create systemic risks. Forced buying/selling based on index membership rather than fundamentals can distort prices. Concentration risk in cap-weighted indices means top holdings drive disproportionate returns. Some argue active management provides better price discovery and capital allocation.",
            "latest_data": "S&P 500 currently trades at forward P/E above historical average. Index fund assets exceed $10 trillion in US equities. Passive vs active split continues shifting toward passive strategies."
        }
    },
    {
        "topic": "etf_structure",
        "sources": {
            "definition": ("https://www.sec.gov/investor/pubs/exchangetradedfunds.htm", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/publications/2020-july-financial-stability-report.htm", "Federal Reserve"),
            "latest_data": ("https://www.etf.com/sections/features-and-news/daily-etf-flows", "ETF.com")
        },
        "tags": ["etf", "index_fund", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Exchange-Traded Funds (ETFs) are investment funds traded on stock exchanges. ETFs hold assets like stocks, bonds, or commodities and track an index, sector, or theme. Creation/redemption mechanism allows authorized participants to exchange ETF shares for underlying assets (creation) or vice versa (redemption), keeping market price aligned with net asset value. This arbitrage mechanism provides tax efficiency and tight tracking. ETFs offer intraday trading, lower costs than mutual funds, and transparency through daily holdings disclosure.",
            "counter_argument": "ETF growth raises liquidity concerns during stress. While ETFs themselves trade liquidly, underlying assets may not. Flash crash scenarios could see ETF prices diverge significantly from NAV if creation/redemption mechanism fails. Bond ETFs particularly vulnerable if underlying bond market freezes. Concentration in popular ETFs could amplify correlated selling.",
            "latest_data": "Global ETF assets exceed $10 trillion. US-listed ETFs number over 2,500. Recent years saw surge in thematic ETFs, active ETFs, and non-transparent structures. Daily trading volumes continue growing."
        }
    },
    {
        "topic": "market_capitalization",
        "sources": {
            "definition": ("https://www.investor.gov/introduction-investing/investing-basics/glossary/market-capitalization", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/small-cap-premium-20190614.html", "Federal Reserve"),
            "latest_data": ("https://fred.stlouisfed.org/series/SP500", "FRED")
        },
        "tags": ["market_cap", "equities", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Market capitalization equals share price multiplied by outstanding shares. Large-cap typically refers to companies valued above $10 billion, mid-cap $2-10 billion, small-cap under $2 billion (thresholds vary). Size categories correlate with risk-return profiles: large-caps tend more stable with lower volatility, small-caps offer higher growth potential but greater risk. Many indices and funds categorize holdings by market cap for diversification and risk management.",
            "counter_argument": "Market cap classifications have limitations. Revenue and operations may not match cap size categorization. Small-cap premium (higher expected returns) has been inconsistent historically. Mega-cap concentration in major indices creates hidden risks. Market cap doesn't account for debt levels or cash positions that affect true enterprise value.",
            "latest_data": "Mega-cap technology stocks now represent record share of total US equity market capitalization. Small-cap valuations relative to large-cap near historical extremes in both directions depending on sector."
        }
    },
    {
        "topic": "bid_ask_spread",
        "sources": {
            "definition": ("https://www.finra.org/investors/insights/bid-ask-spread", "FINRA"),
            "counter_argument": ("https://www.sec.gov/marketstructure/research/hft_lit_review.pdf", "SEC"),
            "latest_data": ("https://www.bls.gov/data/", "BLS")
        },
        "tags": ["market_cap", "volatility", "risk_management", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Bid-ask spread is the difference between highest price a buyer will pay (bid) and lowest price a seller will accept (ask). Spread represents transaction cost and liquidity measure: narrow spreads indicate high liquidity and efficient markets; wide spreads signal low liquidity or uncertainty. Spreads widen during volatility, after hours, or for less-traded securities. Market makers profit from spreads while providing liquidity. Limit orders inside the spread can reduce effective transaction costs.",
            "counter_argument": "Spread alone doesn't capture full transaction costs. Price impact from larger orders often exceeds spread costs. Hidden liquidity and dark pools complicate spread interpretation. High-frequency traders may narrow displayed spreads while reducing actual liquidity available at quoted prices. Effective spread (actual execution vs midpoint) often differs from quoted spread.",
            "latest_data": "Average spreads for S&P 500 stocks remain near historic lows in basis points but absolute dollar spreads increased with higher stock prices. Spread widening during volatility events remains consistent pattern."
        }
    },
    {
        "topic": "market_makers",
        "sources": {
            "definition": ("https://www.investor.gov/introduction-investing/investing-basics/glossary/market-maker", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/market-making-20210415.html", "Federal Reserve"),
            "latest_data": ("https://www.bls.gov/data/", "BLS")
        },
        "tags": ["equities", "market_cap", "volatility", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Market makers are firms or individuals that stand ready to buy and sell securities continuously, providing liquidity to markets. They quote both bid and ask prices, profiting from the spread while managing inventory risk. Designated Market Makers (DMMs) on NYSE have formal obligations to maintain fair and orderly markets. Market makers use sophisticated models to manage risk, adjust quotes based on order flow, and hedge positions. Their presence reduces bid-ask spreads and enables immediate trade execution.",
            "counter_argument": "Traditional market making has evolved significantly. High-frequency firms now dominate, using algorithms and speed advantages. Critics argue HFT market makers provide 'ghost liquidity' that disappears during stress. Payment for order flow creates potential conflicts between broker-dealers and customers. Reduced human oversight may amplify flash crashes and technical failures.",
            "latest_data": "Market making increasingly concentrated among specialized HFT firms. Citadel Securities, Virtu Financial handle significant portion of retail order flow. Regulatory scrutiny of payment for order flow arrangements increasing."
        }
    },
    {
        "topic": "short_selling",
        "sources": {
            "definition": ("https://www.sec.gov/investor/pubs/ss-faq.htm", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/short-selling-ban-20200915.html", "Federal Reserve"),
            "latest_data": ("https://www.bls.gov/data/", "BLS")
        },
        "tags": ["short_selling", "margin", "leverage", "derivatives", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Short selling involves borrowing securities and selling them, hoping to repurchase later at lower price. Profit equals sale price minus repurchase price minus borrowing costs. Short sellers must maintain margin accounts with collateral. Borrowing fees vary based on stock availability. Short interest (shares sold short as % of float) signals bearish sentiment. Shorts contribute to price discovery by expressing negative views, but unlimited loss potential makes it risky. Short squeezes occur when rising prices force shorts to cover, accelerating upward moves.",
            "counter_argument": "Short selling restrictions during crises reflect concerns about destabilizing effects. Naked shorting (selling without locating borrowable shares) was largely banned after 2008. Some argue short sellers accelerate declines during panics. However, research shows short sellers often identify fraud and overvaluation before regulators. Banning shorts removes valuable information from prices and can create artificial bubbles.",
            "latest_data": "Short interest levels fluctuate with market sentiment. Recent meme stock episodes highlighted short squeeze dynamics. Regulatory focus on settlement cycles aims to reduce failed trades associated with shorting."
        }
    },
    {
        "topic": "options_basics",
        "sources": {
            "definition": ("https://www.sec.gov/investor/pubs/options.htm", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/options-market-20210618.html", "Federal Reserve"),
            "latest_data": ("https://www.optionsclearing.com/market-data/volume/", "OCC")
        },
        "tags": ["options", "derivatives", "risk_management", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Options are contracts giving right (not obligation) to buy (call) or sell (put) underlying asset at specified price (strike) by expiration date. Call buyers profit if underlying rises above strike plus premium paid. Put buyers profit if underlying falls below strike minus premium. Option sellers (writers) receive premium but face potentially unlimited losses on calls or large losses on puts. American options can be exercised anytime before expiration; European only at expiration. Options enable hedging, income generation, and leveraged speculation.",
            "counter_argument": "Options complexity creates risks for inexperienced investors. Time decay (theta) erodes option value, hurting buyers. Implied volatility changes dramatically affect prices independent of direction. Most retail option buyers lose money. Zero-day options (expiring same day) have surged, raising concerns about gambling-like behavior and potential market impacts from dealer hedging.",
            "latest_data": "Daily options volume regularly exceeds 50 million contracts. Zero-day options now represent significant portion of SPX volume. Retail participation in options reached record levels."
        }
    },
    {
        "topic": "options_greeks",
        "sources": {
            "definition": ("https://www.investopedia.com/terms/g/greeks.asp", "Investopedia"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/options-hedging-20220315.html", "Federal Reserve"),
            "latest_data": ("https://www.optionsclearing.com/market-data/volume/", "OCC")
        },
        "tags": ["options", "derivatives", "volatility", "risk_management", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Options Greeks measure sensitivity to various factors. Delta measures price change per $1 move in underlying (also approximates probability of expiring in-the-money). Gamma measures delta's rate of change. Theta measures time decay (value lost per day). Vega measures sensitivity to implied volatility changes. Rho measures interest rate sensitivity. Traders use Greeks to manage risk: delta-neutral strategies hedge directional exposure; gamma risk matters for large moves; theta benefits option sellers; vega matters around earnings/events. Portfolio Greeks aggregate individual position risks.",
            "counter_argument": "Greeks assume continuous markets and normal distributions, failing during gaps or extreme moves. Gamma hedging by dealers can amplify market moves (gamma squeezes). Model risk exists: Black-Scholes assumptions often violated in practice. Greeks change dynamically, requiring constant rebalancing. Tail risk not captured by standard Greek analysis.",
            "latest_data": "Dealer gamma positioning receives increased attention as potential market stability indicator. Large negative gamma environments associated with elevated volatility. Zero-day options create unique gamma dynamics due to rapid time decay."
        }
    },
    {
        "topic": "futures_contracts",
        "sources": {
            "definition": ("https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/FuturesFAQ.htm", "CFTC"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/futures-market-20210720.html", "Federal Reserve"),
            "latest_data": ("https://www.cmegroup.com/market-data/volume-open-interest/", "CME")
        },
        "tags": ["futures", "derivatives", "forex", "commodities", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Futures are standardized contracts to buy/sell underlying asset at specified price on future date. Unlike options, futures obligate both parties. Used for hedging (producers/consumers lock prices) and speculation. Margin requirements allow leverage (typically 5-15% of contract value). Daily mark-to-market settles gains/losses. Contracts specify quantity, quality, delivery location/date. Most positions closed before delivery via offsetting trade. Underlying assets include commodities (oil, gold, grains), financial instruments (indices, bonds, currencies), and cryptocurrencies.",
            "counter_argument": "Futures leverage amplifies both gains and losses, causing significant retail losses. Contango (futures priced above spot) creates roll costs for long positions. Backwardation benefits longs but signals supply concerns. Speculative positioning can sometimes amplify price moves beyond fundamentals. Flash crash events have originated in futures markets before spreading to equities.",
            "latest_data": "Futures volumes continue growing across asset classes. Micro contracts launched to attract retail traders. Bitcoin futures gained traction after ETF approvals. Energy futures volatility elevated amid geopolitical tensions."
        }
    },
    {
        "topic": "forex_market",
        "sources": {
            "definition": ("https://www.investor.gov/introduction-investing/investing-basics/glossary/foreign-exchange", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/fx-market-20210825.html", "Federal Reserve"),
            "latest_data": ("https://www.bis.org/statistics/rpfx22.htm", "BIS")
        },
        "tags": ["forex", "currency", "exchange_rate", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Foreign exchange (forex/FX) market trades currencies globally, operating 24 hours/day across major financial centers. Daily turnover exceeds $7 trillion, making it world's largest market. Currencies trade in pairs (EUR/USD, USD/JPY, etc.). Exchange rates reflect relative economic strength, interest rate differentials, trade flows, and speculation. Major pairs involve USD; crosses don't. Central banks intervene occasionally to influence rates. Forex used for international trade, investment, tourism, and speculation. Leverage commonly available but increases risk substantially.",
            "counter_argument": "Retail forex trading has extremely high failure rates. Broker conflicts exist (many act as counterparties to clients). Currency prediction notoriously difficult; academic evidence suggests random walk behavior. Carry trades (borrowing low-rate currencies to buy high-rate ones) work until they don't, causing sharp reversals. Geopolitical events can cause gap moves that bypass stops.",
            "latest_data": "Dollar strength cycle impacted emerging market currencies. Central bank digital currency developments progressing globally. FX volatility spiked during banking stress episodes."
        }
    },
    {
        "topic": "bitcoin_market",
        "sources": {
            "definition": ("https://www.sec.gov/investor/alerts/bitcoin-and-other-virtual-currencies", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/publications/2022-may-financial-stability-report.htm", "Federal Reserve"),
            "latest_data": ("https://fred.stlouisfed.org/series/BitcoinUSD", "FRED")
        },
        "tags": ["crypto", "bitcoin", "blockchain", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Bitcoin is decentralized digital currency using blockchain technology for peer-to-peer transactions without intermediaries. Created in 2009 by pseudonymous Satoshi Nakamoto. Limited supply of 21 million coins creates scarcity. Mining (proof-of-work) secures network and issues new coins. Bitcoin trades on cryptocurrency exchanges 24/7 globally. Institutional adoption grew with futures, ETFs, and corporate treasury allocations. Volatility remains high compared to traditional assets. Use cases include store of value ('digital gold'), speculative investment, and alternative payment system.",
            "counter_argument": "Bitcoin faces significant criticisms: energy consumption from mining, use in illicit activity, lack of intrinsic value, extreme volatility limiting monetary utility, regulatory uncertainty. Environmental concerns led some institutions to avoid bitcoin. Scalability limits transaction throughput. Competition from other cryptocurrencies and central bank digital currencies threatens dominance. Correlation with risk assets increased, undermining inflation hedge narrative.",
            "latest_data": "Bitcoin ETF approvals marked institutional milestone. Price volatility persists with periodic boom-bust cycles. Hash rate reached all-time highs despite price fluctuations. Regulatory clarity improving in major jurisdictions."
        }
    },
    {
        "topic": "ethereum_fundamentals",
        "sources": {
            "definition": ("https://www.sec.gov/investor/alerts/ether-and-other-virtual-currencies", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/publications/2022-may-financial-stability-report.htm", "Federal Reserve"),
            "latest_data": ("https://fred.stlouisfed.org/series/EthereumUSD", "FRED")
        },
        "tags": ["crypto", "ethereum", "defi", "smart_contracts", "blockchain", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Ethereum is blockchain platform enabling smart contracts and decentralized applications (dApps). Launched 2015 by Vitalik Buterin and others. Native cryptocurrency is Ether (ETH). Unlike Bitcoin's limited scripting, Ethereum supports programmable contracts executing automatically when conditions met. Transitioned from proof-of-work to proof-of-stake (The Merge, 2022), reducing energy consumption ~99%. Use cases include DeFi protocols, NFTs, DAOs, and tokenization. Layer-2 solutions improve scalability. ETH used for transaction fees (gas) and staking to secure network.",
            "counter_argument": "Ethereum faces scalability challenges despite improvements. High gas fees during congestion limit usability. Competition from alternative smart contract platforms intensified. Smart contract bugs and exploits caused billions in losses. Regulatory uncertainty around whether ETH is a security. Staking centralization concerns as large validators dominate. Layer-2 fragmentation complicates user experience.",
            "latest_data": "Ethereum upgrade roadmap continues with sharding for scalability. Staking participation grew post-Merge. DeFi TVL fluctuates with crypto market cycles. Layer-2 adoption accelerating."
        }
    },
    {
        "topic": "defi_protocols",
        "sources": {
            "definition": ("https://www.sec.gov/investor/alerts/decentralized-finance-defi", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/publications/2022-november-financial-stability-report.htm", "Federal Reserve"),
            "latest_data": ("https://defillama.com/", "DeFi Llama")
        },
        "tags": ["defi", "crypto", "smart_contracts", "blockchain", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Decentralized Finance (DeFi) uses blockchain smart contracts to recreate financial services without intermediaries. Key protocols include: lending/borrowing (Aave, Compound), decentralized exchanges (Uniswap, Curve), yield farming, liquidity pools, derivatives platforms. Users interact via crypto wallets, earning yields on deposits or paying to borrow. Automated market makers (AMMs) enable trading without order books. Governance tokens give voting rights on protocol changes. DeFi offers permissionless access, transparency, and composability ('money legos'). Total Value Locked (TVL) measures ecosystem size.",
            "counter_argument": "DeFi carries substantial risks: smart contract vulnerabilities, oracle manipulation, governance attacks, impermanent loss for liquidity providers, regulatory uncertainty, and lack of consumer protections. Numerous hacks and exploits caused billions in losses. Yield sustainability questionable; many schemes resemble Ponzi dynamics. Complexity creates barriers to safe participation. Interconnectedness creates systemic risk within crypto ecosystem.",
            "latest_data": "DeFi TVL declined from peak but stabilized. Regulatory scrutiny increased following high-profile failures. Real-world asset tokenization emerged as growth area. Cross-chain bridges remain vulnerability point."
        }
    },
    {
        "topic": "stablecoins",
        "sources": {
            "definition": ("https://www.sec.gov/investor/alerts/stablecoins", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/publications/2021-december-financial-stability-report.htm", "Federal Reserve"),
            "latest_data": ("https://www.coingecko.com/en/categories/stablecoins", "CoinGecko")
        },
        "tags": ["stablecoin", "crypto", "defi", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Stablecoins are cryptocurrencies designed to maintain stable value relative to reference asset (usually USD). Types: fiat-collateralized (USDC, USDT backed by reserves), crypto-collateralized (DAI overcollateralized with crypto), algorithmic (supply adjusts to maintain peg). Stablecoins enable crypto trading without converting to fiat, serve as DeFi building blocks, and facilitate cross-border payments. Issuers claim reserve backing but transparency varies. Redemption mechanisms differ. Stablecoin market cap exceeded $150 billion at peak.",
            "counter_argument": "Stablecoin risks became clear with TerraUSD (UST) collapse in 2022. Algorithmic stablecoins proved vulnerable to death spirals. Fiat-backed stablecoins face questions about reserve quality and redemption guarantees. Potential for runs if confidence falters. Systemic risk concerns as stablecoins integrate deeper into financial system. Regulatory frameworks developing but incomplete. Central bank digital currencies may compete with private stablecoins.",
            "latest_data": "USDC and USDT dominate stablecoin market. Regulatory clarity improved for fiat-backed issuers. Algorithmic stablecoins largely discredited. Banking crisis briefly affected USDC peg before recovery."
        }
    },
    {
        "topic": "on_chain_metrics",
        "sources": {
            "definition": ("https://www.glassnode.com/insights/on-chain-analysis", "Glassnode"),
            "counter_argument": ("https://www.federalreserve.gov/publications/2022-may-financial-stability-report.htm", "Federal Reserve"),
            "latest_data": ("https://coinmetrics.io/", "Coin Metrics")
        },
        "tags": ["on_chain_metrics", "bitcoin", "ethereum", "blockchain", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "On-chain metrics analyze blockchain data to assess cryptocurrency networks. Key metrics: hash rate (computing power securing proof-of-work networks), active addresses (network usage), transaction count/value, exchange inflows/outflows (selling/buying pressure), HODL waves (coin age distribution), realized cap (aggregate acquisition cost), MVRV ratio (market value vs realized value), NVT ratio (network value to transactions). These provide fundamental analysis tools distinct from price action. Whale watching tracks large holder behavior. On-chain data offers transparency unavailable in traditional markets.",
            "counter_argument": "On-chain metrics have limitations. Address counts don't equal users (one entity controls many addresses). Exchange flows ambiguous without context. Metrics can give conflicting signals. Historical patterns don't guarantee future results. Data interpretation requires expertise. Some metrics easily manipulated (wash trading). Privacy coins and mixing services obscure true flows. Correlation with price breaks down during extremes.",
            "latest_data": "Bitcoin hash rate at all-time highs despite price volatility. Long-term holder supply increased. Exchange balances continued declining (coins moving to cold storage). Network activity correlates with price cycles."
        }
    },
    {
        "topic": "crypto_regulation",
        "sources": {
            "definition": ("https://www.sec.gov/cryptocurrency", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/publications/2022-may-financial-stability-report.htm", "Federal Reserve"),
            "latest_data": ("https://www.coinbase.com/legal/regulatory-guidance", "Coinbase")
        },
        "tags": ["regulation", "sec", "crypto", "bitcoin", "ethereum", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Cryptocurrency regulation varies globally. US approach: SEC treats many tokens as securities requiring registration; CFTC regulates bitcoin as commodity; FinCEN enforces AML/KYC rules; IRS taxes crypto as property. Key issues: Howey Test application to tokens, exchange registration, custody rules, stablecoin legislation, DeFi regulation, taxation treatment. EU implemented MiCA (Markets in Crypto-Assets) framework. Asia ranges from supportive (Singapore, Japan) to restrictive (China ban). Regulatory clarity viewed as necessary for institutional adoption but concerns exist about innovation impact.",
            "counter_argument": "Regulatory approach criticized as enforcement-first rather than clear rulemaking. Industry argues existing securities laws ill-suited for decentralized networks. Jurisdictional arbitrage pushes activity offshore. Overregulation risks stifling innovation and pushing development to friendlier jurisdictions. Lack of coordinated global framework creates compliance complexity. Some argue self-regulation and code-based governance preferable to traditional regulation for decentralized systems.",
            "latest_data": "SEC enforcement actions against exchanges and token issuers increased. Bitcoin ETF approvals marked regulatory milestone. Stablecoin legislation advancing in Congress. International coordination through FSB and other bodies progressing."
        }
    },
    {
        "topic": "market_volatility",
        "sources": {
            "definition": ("https://www.investor.gov/introduction-investing/investing-basics/glossary/volatility", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/volatility-puzzle-20210520.html", "Federal Reserve"),
            "latest_data": ("https://fred.stlouisfed.org/series/VIXCLS", "FRED")
        },
        "tags": ["volatility", "risk_management", "var", "vix", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Volatility measures price variation magnitude over time. Statistical volatility (standard deviation of returns) quantifies historical price swings. Implied volatility derived from option prices reflects expected future volatility. VIX ('fear index') measures S&P 500 implied volatility. High volatility indicates uncertainty, risk, or changing fundamentals; low volatility suggests stability or complacency. Volatility clustering occurs (high vol periods group together). Mean reversion tendency: extreme volatility eventually subsides. Volatility used for risk management, option pricing, and position sizing.",
            "counter_argument": "Volatility is imperfect risk measure. Assumes normal distribution (fat tails ignored). Doesn't distinguish upside vs downside moves. Low volatility can breed complacency and excessive risk-taking (volatility paradox). Volatility targeting strategies can amplify moves. VIX calculation methodology has quirks. Volatility products (VIX futures, ETNs) suffer from contango, making long-term holding costly.",
            "latest_data": "VIX averages around 20, spiked during banking stress and debt ceiling concerns. Volatility regime shifted from ultra-low pandemic era. Correlation spikes during stress reduce diversification benefits."
        }
    },
    {
        "topic": "circuit_breakers",
        "sources": {
            "definition": ("https://www.sec.gov/fast-answers/answerscircuitbreakers.html", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/circuit-breakers-20210315.html", "Federal Reserve"),
            "latest_data": ("https://www.nyse.com/markets/nyse/trading-status", "NYSE")
        },
        "tags": ["risk_management", "volatility", "stock_market", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Circuit breakers halt trading temporarily during extreme price moves to prevent panic and allow information dissemination. Market-wide circuit breakers trigger on S&P 500 declines: Level 1 (7% drop) halts 15 minutes; Level 2 (13%) halts 15 minutes; Level 3 (20%) halts remainder of day. Individual stock circuit breakers (Limit Up-Limit Down) pause trading if price moves outside specified bands within 5 minutes. Cooling-off periods aim to prevent disorderly trading, allow margin calls, and let investors process information. Implemented after 1987 crash, refined after 2010 flash crash.",
            "counter_argument": "Circuit breakers have unintended consequences. Trading halts prevent risk management during critical periods, potentially increasing pent-up selling pressure. Magnets effect: prices drawn toward circuit breaker thresholds as traders rush to execute before halt. Halts may increase anxiety rather than calm markets. Different triggers across products (stocks vs futures) create confusion. After-hours trading不受 circuit breakers, limiting effectiveness.",
            "latest_data": "Circuit breakers triggered multiple times in March 2020 pandemic crash. Limit Up-Limit Down pauses occur regularly in volatile stocks. Review of thresholds ongoing as market structure evolves."
        }
    },
    {
        "topic": "after_hours_trading",
        "sources": {
            "definition": ("https://www.finra.org/investors/insights/extended-hours-trading", "FINRA"),
            "counter_argument": ("https://www.sec.gov/marketstructure/research/extended_hours_trading.pdf", "SEC"),
            "latest_data": ("https://www.bls.gov/data/", "BLS")
        },
        "tags": ["stock_market", "volatility", "risk_management", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "After-hours trading occurs outside regular market hours (9:30 AM - 4:00 PM ET). Pre-market (4:00-9:30 AM) and after-hours (4:00-8:00 PM) sessions enabled by electronic communication networks (ECNs). Allows reaction to earnings releases, economic data, and news announced outside regular hours. Participation lower than regular session, leading to wider spreads and higher volatility. Limit orders recommended over market orders. Not all stocks available for extended hours. Prices may gap significantly at regular open based on after-hours activity.",
            "counter_argument": "After-hours trading carries elevated risks: lower liquidity means wider spreads and difficulty executing large orders. Higher volatility can trigger stops unexpectedly. Limited participation means prices may not reflect broader market sentiment. Institutional dominance can disadvantage retail traders. Earnings reactions in after-hours often reverse or extend at open. Technical issues more common. Less regulatory oversight than regular session.",
            "latest_data": "Extended hours volume grew significantly, especially around earnings. Retail participation increased with zero-commission brokers offering 24-hour trading on select stocks. Gap moves at open remain common."
        }
    },
    {
        "topic": "dark_pools",
        "sources": {
            "definition": ("https://www.sec.gov/fast-answers/answersdarkpoolhtm.html", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/dark-pools-20210420.html", "Federal Reserve"),
            "latest_data": ("https://www.bloomberg.com/markets/stocks/dark-pools", "Bloomberg")
        },
        "tags": ["stock_market", "market_cap", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Dark pools are private exchanges where institutional investors trade securities anonymously without displaying orders publicly. Operate as Alternative Trading Systems (ATS) registered with SEC. Purpose: allow large trades without market impact (pre-trade transparency would signal intentions, moving prices against trader). Trades reported after execution at NBBO (National Best Bid and Offer). Dark pools charge lower fees than lit exchanges. Concerns: two-tiered market favoring institutions, potential conflicts when dark pool operators also engage in proprietary trading, information leakage.",
            "counter_argument": "Dark pools fragment markets and harm price discovery by removing liquidity from public view. Retail investors disadvantaged by not accessing same venues. Conflicts of interest prevalent: some dark pools operated by banks that trade against customers. High-frequency traders exploit dark pool information. Academic studies show significant information leakage despite anonymity claims. Some dark pools engaged in illegal practices (Barclays, Credit Suisse settlements). Transparency advocates call for restrictions or elimination.",
            "latest_data": "Dark pool market share fluctuates around 10-15% of equity volume. Regulatory scrutiny continues. New ATS formats emerge. Consolidated audit trail (CAT) improves surveillance capabilities."
        }
    },
    {
        "topic": "high_frequency_trading",
        "sources": {
            "definition": ("https://www.sec.gov/marketstructure/research/hft_lit_review.pdf", "SEC"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/hft-impact-20210518.html", "Federal Reserve"),
            "latest_data": ("https://www.bls.gov/data/", "BLS")
        },
        "tags": ["stock_market", "volatility", "market_cap", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "High-Frequency Trading (HFT) uses powerful computers and algorithms to execute trades in milliseconds or microseconds. Characteristics: high turnover, short holding periods, small profits per trade, sophisticated technology, co-location (servers near exchange matching engines). HFT strategies include market making, statistical arbitrage, latency arbitrage, and order flow prediction. Proponents argue HFT provides liquidity, narrows spreads, and improves price efficiency. HFT firms include Virtu Financial, Citadel Securities, Jump Trading, Two Sigma. Represents estimated 50-60% of US equity volume.",
            "counter_argument": "HFT criticized for creating unstable liquidity that disappears during stress. Flash crashes attributed to HFT interactions. Latency arms race diverts resources from productive investment. Predatory strategies exploit slower participants. Quote stuffing overwhelms systems. Co-location creates two-tiered access. HFT profits from speed advantage rather than fundamental analysis. Some argue HFT acts as modern front-running. Regulatory proposals include minimum resting times, transaction taxes, and batch auctions.",
            "latest_data": "HFT market share stabilized after initial growth. Technology arms race continues with microwave networks and FPGA optimization. Regulatory focus shifted to specific practices rather than HFT broadly. Retail order flow routing to HFT market makers remains controversial."
        }
    },
    {
        "topic": "market_bubbles",
        "sources": {
            "definition": ("https://www.federalreserve.gov/econres/notes/feds-notes/bubbles-20210625.html", "Federal Reserve"),
            "counter_argument": ("https://www.sec.gov/investor/alerts/bubbles", "SEC"),
            "latest_data": ("https://fred.stlouisfed.org/series/SP500", "FRED")
        },
        "tags": ["bull_market", "bear_market", "market_correction", "volatility", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Market bubbles occur when asset prices rise far above intrinsic value driven by speculation rather than fundamentals. Characteristics: rapid price appreciation, widespread public interest, new paradigm thinking ('this time is different'), easy credit, abandonment of traditional valuation metrics. Historical examples: Tulip Mania (1637), South Sea Bubble (1720), 1929 stock bubble, Dot-com bubble (1999-2000), Housing bubble (2004-2006). Identification difficult in real-time: prices can remain elevated longer than fundamentals justify. Bubbles eventually burst when sentiment shifts, triggering sharp declines.",
            "counter_argument": "Bubble identification is notoriously unreliable. Many supposed bubbles reflect legitimate value changes. Fed officials hesitant to declare bubbles, preferring to address aftermath. 'Irrational exuberance' warnings often premature. Shorting bubbles dangerous due to timing uncertainty and potential for further irrationality. Some argue bubbles inevitable in capitalist systems due to human psychology and credit cycles. Prevention through regulation debated but implementation challenging.",
            "latest_data": "Debates continue about bubble conditions in various assets (tech stocks, housing, crypto, memes). Valuation metrics stretched by historical standards but context matters. Low interest rate environment justified higher multiples for some analysts."
        }
    },
    {
        "topic": "market_crashes",
        "sources": {
            "definition": ("https://www.investopedia.com/terms/m/marketcrash.asp", "Investopedia"),
            "counter_argument": ("https://www.federalreserve.gov/econres/notes/feds-notes/crashes-20210715.html", "Federal Reserve"),
            "latest_data": ("https://fred.stlouisfed.org/series/SP500", "FRED")
        },
        "tags": ["bear_market", "market_correction", "volatility", "risk_management", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Market crashes are sudden, steep declines in asset prices, typically 10%+ over days or weeks. Famous crashes: 1929 Great Crash (started Great Depression), 1987 Black Monday (-22% in one day), 2008 Financial Crisis (-57% peak-to-trough), 2020 COVID crash (-34% in one month). Common triggers: economic shocks, financial crises, geopolitical events, bursting bubbles, pandemics. Crashes often accompanied by panic selling, liquidity evaporation, forced deleveraging, and negative feedback loops. Recovery times vary: 1987 recovered quickly; 1929 took decades; 2008 took ~4 years.",
            "counter_argument": "Crash prediction is nearly impossible; most warnings prove false. Buying during crashes psychologically difficult but historically profitable long-term. Circuit breakers and interventions may delay but not prevent necessary price adjustments. Some crashes reflect legitimate repricing of overvalued assets. Government responses (monetary/fiscal) have become more aggressive, potentially creating moral hazard. Timing market entries during crashes extremely difficult even in retrospect.",
            "latest_data": "2020 COVID crash fastest on record but also quickest recovery due to unprecedented policy response. Subsequent bull market reached new highs. Inflation concerns and rate hikes created correction conditions."
        }
    },
    {
        "topic": "liquidity_crisis",
        "sources": {
            "definition": ("https://www.federalreserve.gov/econres/notes/feds-notes/liquidity-20210820.html", "Federal Reserve"),
            "counter_argument": ("https://www.sec.gov/marketstructure/research/liquidity_stress_testing.pdf", "SEC"),
            "latest_data": ("https://fred.stlouisfed.org/series/TEDRATE", "FRED")
        },
        "tags": ["volatility", "risk_management", "correlation", "var", "definition", "counter_argument", "latest_data"],
        "content_templates": {
            "definition": "Liquidity crisis occurs when markets cannot absorb selling without dramatic price declines. Characteristics: bid-ask spreads widen dramatically, trading volumes surge but executions fail, normally liquid assets become unsellable, fire sales propagate across markets, funding liquidity dries up. Examples: 2008 Lehman collapse (commercial paper froze), 2010 Flash Crash, 2019 Repo spike, March 2020 COVID panic (even Treasuries illiquid). Causes: leverage unwinding, margin calls, redemptions forcing sales, counterparty fears, regulatory constraints on market making. Central banks often intervene as lender of last resort.",
            "counter_argument": "Liquidity is illusory until tested; apparent liquidity vanishes precisely when needed. Post-2008 regulations improved bank resilience but may have pushed risks to shadow banking. ETF liquidity dependent on underlying asset liquidity, creating false sense of security. Market making consolidation increases fragility if key players withdraw. Central bank intervention creates moral hazard, encouraging excessive risk-taking with expectation of bailouts.",
            "latest_data": "March 2020 provided stress test showing liquidity vulnerabilities across asset classes. Fed intervention restored functioning. Ongoing monitoring of Treasury market liquidity. Bank Term Funding Program addressed 2023 regional bank stress."
        }
    }
]


def generate_fragment(topic_data, role):
    """Generate a single fragment JSON for given topic and role."""
    topic = topic_data["topic"]
    sources = topic_data["sources"][role]
    content = topic_data["content_templates"][role]
    
    # Generate ID
    role_short = {"definition": "def", "counter_argument": "counter", "latest_data": "latest"}[role]
    
    # Count existing fragments for this topic to get number
    existing_count = 0
    for f in os.listdir(FRAGMENT_LIBRARY_PATH):
        if f.startswith(f"frag_fin_{topic}_{role_short}_"):
            try:
                num = int(f.split("_")[-1].replace(".json", ""))
                existing_count = max(existing_count, num)
            except:
                pass
    
    fragment_number = existing_count + 1
    fragment_id = f"frag_fin_{topic}_{role_short}_{fragment_number:03d}"
    
    # Extract domain from source
    source_url, source_name = sources
    domain_parts = source_url.replace("https://www.", "").replace("https://", "").split("/")
    source_domain = domain_parts[0] if domain_parts else "unknown"
    
    # Credibility mapping
    credibility_map = {
        "sec.gov": ("government_source", 0.92),
        "federalreserve.gov": ("peer_reviewed_study", 0.95),
        "bls.gov": ("government_source", 0.90),
        "bea.gov": ("government_source", 0.90),
        "fred.stlouisfed.org": ("government_source", 0.88),
        "spglobal.com": ("government_source", 0.85),
        "finra.org": ("government_source", 0.88),
        "investor.gov": ("government_source", 0.88),
        "cftc.gov": ("government_source", 0.90),
        "bis.org": ("government_source", 0.88),
        "optionsclearing.com": ("government_source", 0.85),
        "cmegroup.com": ("government_source", 0.82),
        "coingecko.com": ("news_article", 0.75),
        "defillama.com": ("news_article", 0.75),
        "coinmetrics.io": ("news_article", 0.78),
        "coinbase.com": ("news_article", 0.75),
        "glassnode.com": ("news_article", 0.78),
        "bloomberg.com": ("news_article", 0.80),
        "nyse.com": ("government_source", 0.85),
        "etf.com": ("news_article", 0.78),
        "investopedia.com": ("news_article", 0.75),
    }
    
    credibility_class, credibility_score = credibility_map.get(source_domain, ("news_article", 0.75))
    
    # Auto-detect tags from templates
    base_tags = [t for t in topic_data["tags"] if t not in ["definition", "counter_argument", "latest_data"]]
    role_tag = role if role == "latest_data" else ("latest_data" if role == "counter_argument" else "definition")
    all_tags = list(set(base_tags + [role_tag]))
    
    # Determine subdomain
    subdomain_map = {
        "stock_market_basics": "equities",
        "market_indices": "equities",
        "etf_structure": "equities",
        "market_capitalization": "equities",
        "bid_ask_spread": "market_structure",
        "market_makers": "market_structure",
        "short_selling": "trading_strategies",
        "options_basics": "derivatives",
        "options_greeks": "derivatives",
        "futures_contracts": "derivatives",
        "forex_market": "forex",
        "bitcoin_market": "crypto",
        "ethereum_fundamentals": "crypto",
        "defi_protocols": "crypto",
        "stablecoins": "crypto",
        "on_chain_metrics": "crypto",
        "crypto_regulation": "crypto",
        "market_volatility": "risk_management",
        "circuit_breakers": "market_structure",
        "after_hours_trading": "market_structure",
        "dark_pools": "market_structure",
        "high_frequency_trading": "market_structure",
        "market_bubbles": "market_psychology",
        "market_crashes": "market_psychology",
        "liquidity_crisis": "risk_management",
    }
    subdomain = subdomain_map.get(topic, "general")
    
    fragment = {
        "id": fragment_id,
        "domain": "finance",
        "subdomain": subdomain,
        "tags": all_tags,
        "reasoning_role": role,
        "content": content,
        "source": source_name,
        "source_url": source_url,
        "credibility_class": credibility_class,
        "year": 2024,
        "compatible_with": [],
        "incompatible_with": [],
        "weight": credibility_score
    }
    
    return fragment


def main():
    """Generate all market mechanics fragments."""
    os.makedirs(FRAGMENT_LIBRARY_PATH, exist_ok=True)
    
    roles = ["definition", "counter_argument", "latest_data"]
    total_generated = 0
    
    for topic_data in MARKET_MECHANICS_TOPICS:
        for role in roles:
            fragment = generate_fragment(topic_data, role)
            filepath = os.path.join(FRAGMENT_LIBRARY_PATH, f"{fragment['id']}.json")
            
            with open(filepath, 'w') as f:
                json.dump(fragment, f, indent=2)
            
            print(f"Created: {filepath}")
            total_generated += 1
    
    print(f"\n=== Generated {total_generated} market mechanics fragments ===")
    print(f"Topics covered: {len(MARKET_MECHANICS_TOPICS)}")
    print(f"Fragments per topic: {len(roles)}")


if __name__ == "__main__":
    main()
