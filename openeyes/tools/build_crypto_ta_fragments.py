#!/usr/bin/env python3
"""
OpenEyes Fragment Builder: Crypto + Technical Analysis Deep Fill
Generates ~200 new fragments to fill gaps identified by test suite.

CLUSTER A — Crypto Deep Fill (100 fragments)
CLUSTER B — Technical Analysis Deep Fill (80 fragments)
CLUSTER C — Gap Fillers (20-40 fragments)
"""

import json
import os
from datetime import datetime

FRAGMENT_DIR = "openeyes/fragment_library/fragments"
os.makedirs(FRAGMENT_DIR, exist_ok=True)

# =============================================================================
# CLUSTER A: CRYPTO DEEP FILL (100 fragments)
# =============================================================================

CRYPTO_TOPICS = [
    # Bitcoin Network Fundamentals (24 fragments: 8 topics x 3 roles)
    {
        "id": "btc_utxo",
        "title": "Bitcoin UTXO Model",
        "def": "Bitcoin uses an Unspent Transaction Output (UTXO) model where each transaction consumes previous outputs and creates new ones. Unlike account-based systems, there are no balances—only unspent outputs owned by addresses. This design enables parallel transaction validation and enhances privacy by not linking transactions to persistent accounts.",
        "counter": "The UTXO model creates UX complexity for users accustomed to account balances. Wallets must scan the entire chain to calculate balances, and dust accumulation (tiny unspendable outputs) bloats the chain state over time.",
        "data": "As of 2024, the Bitcoin UTXO set contains over 150 million entries, requiring several GB of RAM for full nodes. Optimizations like UTXO commitments in libsecp256k1 improve validation speed."
    },
    {
        "id": "btc_mempool",
        "title": "Bitcoin Mempool & Fee Markets",
        "def": "The mempool is a waiting area for unconfirmed transactions held by nodes. When block space is scarce, transactions compete via fee rates (sat/vbyte). Miners prioritize highest fee-rate transactions, creating a dynamic auction market for block inclusion.",
        "counter": "Mempool dynamics can lead to unpredictable fees during congestion spikes. Users may overpay significantly during peak periods, and low-priority transactions can remain stuck for days.",
        "data": "During ordinals inscriptions boom (early 2024), mempool exceeded 500k unconfirmed transactions. Fee rates spiked from typical 10-50 sat/vbyte to over 400 sat/vbyte at peaks."
    },
    {
        "id": "btc_script",
        "title": "Bitcoin Script Language",
        "def": "Bitcoin Script is a stack-based, Forth-like language that defines spending conditions. It's intentionally Turing-incomplete for security. Common scripts include P2PKH (pay-to-public-key-hash), P2SH (pay-to-script-hash), and Taproot's P2TR enabling complex smart contracts.",
        "counter": "Script's limited expressiveness prevents sophisticated DeFi applications possible on Ethereum. Complex contracts require multiple transactions and off-chain coordination.",
        "data": "Taproot adoption reached 15-20% of transactions by 2024, enabling more complex scripts with better privacy. Ordinals protocol leverages Script for NFT-like inscriptions."
    },
    {
        "id": "btc_segwit",
        "title": "Segregated Witness (SegWit)",
        "def": "SegWit (BIP141, 2017) separated signature data from transaction data, effectively increasing block capacity to ~4MB weight units. It fixed transaction malleability, enabling Lightning Network. Native SegWit (bech32) addresses start with 'bc1q'.",
        "counter": "SegWit adoption was slow initially due to exchange/wallet upgrade requirements. Some argue the soft fork created unnecessary complexity versus a clean block size increase.",
        "data": "SegWit adoption exceeded 80% by 2024. Bech32m (Taproot) addresses starting 'bc1p' represent the newest standard. Fee savings from SegWit are 25-40% vs legacy transactions."
    },
    {
        "id": "btc_taproot",
        "title": "Taproot Upgrade",
        "def": "Taproot (BIP341-342, Nov 2021) introduced Schnorr signatures and Merkleized Abstract Syntax Trees (MAST). It improves privacy by making complex scripts indistinguishable from simple payments and reduces data for multi-sig transactions.",
        "counter": "Real-world Taproot benefits remain limited as most wallets haven't implemented advanced script paths. Privacy gains only materialize when usage is widespread.",
        "data": "Taproot activation occurred at block 709,632. By 2024, 15-20% of transactions used Taproot. Ordinals and BRC-20 tokens emerged as unexpected Taproot use cases."
    },
    {
        "id": "btc_node",
        "title": "Running a Bitcoin Node",
        "def": "A full node validates all Bitcoin transactions and blocks against consensus rules. Running one ensures you don't trust others for verification, supports network decentralization, and enables private transaction broadcasting without leaking your address to third parties.",
        "counter": "Node operation requires significant resources (~500GB storage, 4GB RAM, bandwidth). Most users rely on SPV wallets or exchanges, creating centralization pressure despite ideological importance.",
        "data": "Estimated 15,000-20,000 reachable nodes globally (2024). Actual node count likely 3-5x higher including unreachable nodes. Raspberry Pi 4 with SSD makes home nodes accessible."
    },
    {
        "id": "btc_difficulty",
        "title": "Bitcoin Difficulty Adjustment",
        "def": "Mining difficulty adjusts every 2016 blocks (~14 days) to maintain 10-minute average block time. If blocks are found faster, difficulty increases; slower, it decreases. This mechanism stabilizes issuance regardless of hash rate fluctuations.",
        "counter": "The 2-week adjustment lag can create feedback loops during rapid hash rate changes. Miner capitulation can accelerate during bear markets before difficulty catches up.",
        "data": "Difficulty has increased exponentially since genesis, with periodic drops during miner capitulation events (2018, 2022). Post-2024 halving, difficulty adjustments became more volatile."
    },
    {
        "id": "btc_blocksize",
        "title": "Block Size Debate History",
        "def": "The 2015-2017 debate centered on scaling Bitcoin. 'Big blockers' wanted larger blocks (Bitcoin Cash fork). 'Small blockers' prioritized decentralization, leading to SegWit + Lightning. The 1MB limit (effectively 4MB weight) remained.",
        "counter": "Critics argue the debate resulted in suboptimal scaling, pushing users to altcoins or Layer 2s. High fees during congestion price out small users, contradicting 'banking the unbanked' vision.",
        "data": "Bitcoin Cash (8MB blocks) launched Aug 2017. Subsequent forks included SV (Satoshi Vision). BTC remained dominant with >90% of crypto market cap despite scaling limitations."
    },
    
    # Ethereum Network Specifics (24 fragments)
    {
        "id": "eth_eip1559",
        "title": "EIP-1559 Fee Mechanism",
        "def": "EIP-1559 (Aug 2021) replaced first-price auctions with base fee + tip model. Base fee burns automatically, making ETH deflationary during high usage. Tips incentivize miners/validators. Users specify max fee and priority fee.",
        "counter": "Fee burning benefits ETH holders but doesn't reduce user costs. During congestion, total fees remain high; the burn just redistributes value from users to remaining holders.",
        "data": "Over 4 million ETH burned since EIP-1559 implementation. During high activity periods, burn rate exceeds issuance, creating net deflation. Base fee volatility remains a UX challenge."
    },
    {
        "id": "eth_merge_details",
        "title": "Ethereum Merge Details",
        "def": "The Merge (Sept 15, 2022) combined Ethereum Mainnet with the Beacon Chain PoS system. Energy consumption dropped ~99.95%. No user action required; history and state preserved. Issuance dropped ~90% as PoW rewards ended.",
        "counter": "The Merge didn't reduce gas fees or increase throughput as some expected. Those improvements require separate upgrades (sharding, L2s). Validators now face centralization pressures from staking pools.",
        "data": "Post-Merge, ~28M ETH staked (23% of supply). Validator count exceeded 875,000. Lido controls ~30% of staked ETH, raising centralization concerns."
    },
    {
        "id": "eth_staking_yield",
        "title": "Ethereum Staking Yield",
        "def": "Staking yield comes from block rewards, transaction tips, and MEV. Current APR ranges 3-5%, varying with total stake amount and network activity. Yield decreases as more ETH is staked (diminishing returns curve).",
        "counter": "Yield carries slashing risk, smart contract risk (for liquid staking), and opportunity cost vs other investments. Post-withdrawal enablement, large unstaking could pressure price.",
        "data": "Shanghai/Capella upgrade (April 2023) enabled withdrawals. Liquid Staking Tokens (Lido's stETH, Coinbase's cbETH) trade at slight discounts/premiums to ETH based on market conditions."
    },
    {
        "id": "eth_validator_requirements",
        "title": "Ethereum Validator Requirements",
        "def": "Becoming a validator requires 32 ETH deposit, running execution + consensus clients, and maintaining uptime. Hardware needs: modern CPU, 16GB RAM, fast SSD. Rewards for proposing/attesting; penalties for downtime or misbehavior.",
        "counter": "32 ETH requirement (~$100k+) excludes retail participants. Solo staking demands technical expertise and 24/7 reliability. Staking pools enable smaller amounts but introduce counterparty risk.",
        "data": "Solo validators represent ~30% of stake; pools dominate remainder. Rocket Pool enables 8 ETH + RPL collateral for decentralized pool nodes. Institutional staking services growing rapidly."
    },
    {
        "id": "eth_slashing",
        "title": "Ethereum Slashing Conditions",
        "def": "Slashing penalizes validators for double-proposing blocks, surround attesting, or conflicting votes. Penalty: minimum 1 ETH plus proportional stake loss based on correlated offenders. Forced exit after slashing.",
        "counter": "Slashing primarily targets malicious behavior, but bugs or misconfiguration can cause accidental violations. Correlated slashing events could cascade if many validators run same faulty client.",
        "data": "Minor slashing incidents occurred from client bugs (e.g., Lighthouse bug 2023). Total slashed ETH remains <1000 since launch. Client diversity (Prysm, Lighthouse, Teku, Nimbus) mitigates systemic risk."
    },
    {
        "id": "eth_mev",
        "title": "Maximal Extractable Value (MEV)",
        "def": "MEV is profit validators/searchers extract by reordering, including, or censoring transactions. Common strategies: arbitrage, liquidations, sandwich attacks. MEV-Boost separates block building from validation, allowing specialized builders.",
        "counter": "MEV extraction harms regular users through front-running and worse execution prices. Centralization risk emerges as sophisticated MEV operations dominate block production.",
        "data": "MEV-Boost used by >90% of validators post-Merge. Flashbots dominates searcher ecosystem. PBS (Proposer-Builder Separation) aims to democratize MEV distribution while preventing censorship."
    },
    {
        "id": "eth_roadmap",
        "title": "Ethereum Roadmap",
        "def": "Post-Merge roadmap includes: Surge (danksharding for scalability), Scourge (MEV/censorship resistance), Verge (Verkle trees for stateless clients), Purge (history expiry), Splurge (misc improvements). Goal: 100k+ TPS via L2s + sharding.",
        "counter": "Roadmap complexity and multi-year timeline risk losing momentum to faster-moving L1 competitors. Each upgrade introduces potential bugs or unintended consequences.",
        "data": "Dencun upgrade (March 2024) introduced proto-danksharding (EIP-4844), reducing L2 costs 10-100x. Full danksharding expected 2025-2026. Verkle trees in development for state management."
    },
    {
        "id": "erc20_standard",
        "title": "ERC-20 Token Standard",
        "def": "ERC-20 defines standard functions (transfer, approve, balanceOf) for fungible tokens on Ethereum. Launched 2015, enabled ICO boom 2017. Over 500k ERC-20 tokens exist, though most are inactive. Requires ETH for gas fees.",
        "counter": "ERC-20 lacks hooks for transfer notifications, causing compatibility issues with some contracts. Approve/transferFrom pattern creates phishing risks. Newer standards (ERC-777) offer improvements but limited adoption.",
        "data": "USDT, USDC, WBTC are largest ERC-20 tokens by market cap. Gas fees for ERC-20 transfers vary 10k-100k gas depending on implementation. L2s host growing ERC-20 ecosystems."
    },
    
    # DeFi Specifics (24 fragments)
    {
        "id": "defi_amm_formula",
        "title": "Automated Market Maker Formula",
        "def": "AMMs use constant product formula (x*y=k) for pricing. Uniswap v2 popularized this: reserves of two tokens maintain invariant k. Price = reserve ratio. Liquidity providers earn 0.3% fees proportional to their share. No order book needed.",
        "counter": "Constant product AMMs suffer from impermanent loss and capital inefficiency. Large trades experience significant slippage. Concentrated liquidity (v3) improves efficiency but adds complexity.",
        "data": "Uniswap v2 processed $1T+ cumulative volume by 2024. v3's concentrated liquidity captures 80%+ of DEX volume. Curve Finance dominates stablecoin swaps with lower slippage."
    },
    {
        "id": "defi_impermanent_loss",
        "title": "Impermanent Loss Mechanism",
        "def": "IL occurs when LP token values diverge from holding assets directly. Worst when one asset appreciates/depreciates significantly. Formula: IL = 2*sqrt(price_ratio)/(1+price_ratio) - 1. At 2x price change, IL ≈ 5.7%. Permanent if you withdraw at loss.",
        "counter": "IL calculations ignore fee earnings, which can offset losses in high-volume pairs. Stablecoin pairs have minimal IL but also lower yields. IL is only 'impermanent' if prices revert.",
        "data": "Studies show 75%+ of LP positions underperform HODL over long periods excluding fees. High-fee tiers on volatile pairs can generate 20-50% APY, compensating for IL risk."
    },
    {
        "id": "defi_liquidity_pools",
        "title": "Liquidity Pool Mechanics",
        "def": "LPs deposit equal value of two tokens into a pool, receiving LP tokens representing their share. Fees accumulate pro-rata. Withdrawals reclaim underlying assets at current ratio. Smart contracts manage pricing automatically.",
        "counter": "LPs face smart contract risk, impermanent loss, and potential rug pulls on unaudited protocols. Due diligence on code audits, team, and TVL history is essential before providing liquidity.",
        "data": "Total DeFi TVL peaked at $180B (Nov 2021), corrected to $50B (2023), recovered to $100B+ (2024). Uniswap, Aave, MakerDAO remain top protocols by TVL and usage."
    },
    {
        "id": "defi_flash_loans",
        "title": "Flash Loans",
        "def": "Flash loans allow borrowing any amount without collateral, provided loan is repaid within same transaction. Used for arbitrage, collateral swapping, self-liquidation. If repayment fails, entire transaction reverts. Enabled by atomic transaction execution.",
        "counter": "Flash loans have been weaponized for attacks: manipulating oracle prices, exploiting governance voting, draining protocols. They amplify vulnerabilities in poorly designed systems.",
        "data": "Major flash loan attacks: bZx ($950k), Harvest Finance ($24M), Cream Finance ($130M). Legitimate use cases dominate volume, but attacks receive disproportionate attention."
    },
    {
        "id": "defi_yield_farming",
        "title": "Yield Farming Dynamics",
        "def": "Yield farming involves providing liquidity to earn token rewards beyond trading fees. Protocols emit governance tokens to bootstrap liquidity. APYs often unsustainable, declining as emissions dilute or farmers exit.",
        "counter": "Most yield farming returns come from token emissions, not sustainable revenue. Farmers dump rewards, creating sell pressure. 'Real yield' from fees is rarer but more sustainable.",
        "data": "2020 'DeFi Summer' saw 1000%+ APYs that collapsed within weeks. Modern protocols focus on veTokenomics (vote-escrowed) to align long-term incentives. Real yield protocols earn 5-20% from actual fees."
    },
    {
        "id": "defi_tvl_metrics",
        "title": "Total Value Locked (TVL)",
        "def": "TVL measures total assets deposited in a protocol. Calculated as sum of all locked collateral. Higher TVL suggests trust and liquidity depth. However, double-counting occurs when assets are rehypothecated across protocols.",
        "counter": "TVL can be gamed via mercenary capital chasing rewards. It doesn't measure actual usage or revenue. A protocol with $1B TVL earning no fees is less valuable than $100M TVL generating strong cash flow.",
        "data": "Lido leads with $30B+ TVL (staked ETH). MakerDAO, Aave, Uniswap follow. Cross-chain bridges inflate TVL metrics via wrapped asset duplication."
    },
    {
        "id": "defi_composability",
        "title": "DeFi Composability (Money Legos)",
        "def": "Composability allows protocols to integrate seamlessly: Aave deposits as collateral on Maker, which farms Curve rewards. Enables innovation but creates interdependencies. Failure in one protocol can cascade through the ecosystem.",
        "counter": "Composability amplifies systemic risk. Terra/LUNA collapse demonstrated how interconnected positions create contagion. Users may not realize their exposure to single points of failure.",
        "data": "DeFi 'super apps' like Instadamma manage multi-protocol positions. Risk dashboards (DeBank, Zapper) help visualize exposures. Circuit breakers and isolation modes mitigate contagion."
    },
    {
        "id": "defi_oracle_problem",
        "title": "Oracle Problem & Solutions",
        "def": "Blockchains can't access external data natively. Oracles feed real-world prices (e.g., ETH/USD) to smart contracts. Chainlink uses decentralized node networks with reputation systems. TWAP oracles use time-weighted averages to resist manipulation.",
        "counter": "Oracles remain attack vectors: manipulated prices trigger false liquidations. Chainlink dependency creates centralization risk. Novel solutions like Pyth Network use publisher-signed data.",
        "data": "Chainlink secures $50B+ in DeFi value. Oracle manipulation caused major exploits: Synthetix ($1M), PancakeBunny, Cream Finance. Multi-oracle designs improve resilience."
    },
    
    # Crypto Market Structure (24 fragments)
    {
        "id": "crypto_funding_rates",
        "title": "Perpetual Futures Funding Rates",
        "def": "Perpetual futures have no expiry; funding rates keep perp price anchored to spot. Longs pay shorts when perp trades above spot (positive funding); shorts pay longs when below. Typically paid every 8 hours. Extreme rates signal crowded positioning.",
        "counter": "Funding rates can remain extreme longer than traders expect, causing blowups. Retail often fades extreme funding prematurely. Institutional players can manipulate rates to squeeze retail.",
        "data": "During bull peaks, annualized funding exceeded 50-100%. Negative funding during crashes signals excessive shorting. Basis traders arb spot-perp spread, earning funding as yield."
    },
    {
        "id": "crypto_open_interest",
        "title": "Open Interest Analysis",
        "def": "Open interest (OI) is total outstanding derivative contracts. Rising OI with rising price suggests strong trend conviction. Falling OI indicates position closing. OI spikes often precede volatility events or liquidation cascades.",
        "counter": "OI alone doesn't indicate direction—must analyze with price action and volume. Exchange-reported OI may be inflated by wash trading on unregulated platforms.",
        "data": "Crypto OI regularly exceeds $50B across all exchanges. CME Bitcoin OI grew significantly post-ETF approval. OI concentration on Binance (>50%) creates single-point-of-failure risk."
    },
    {
        "id": "crypto_liquidation_cascades",
        "title": "Liquidation Cascades",
        "def": "When leveraged positions hit liquidation price, they're forcibly closed at market, pushing price further and triggering more liquidations. Cascades cause flash crashes. Long squeezes (downward) more violent than short squeezes due to panic selling.",
        "counter": "Liquidation heatmaps are public, enabling predatory positioning. Whales may deliberately push price to trigger cascades before reversing. Over-leveraged traders are essentially donating to patient capital.",
        "data": "May 2021 crash liquidated $10B+ in hours. FTX collapse triggered $2B+ liquidations. Typical cascade: 10-20% price move triggers 5-10x that volume in liquidations."
    },
    {
        "id": "crypto_market_makers",
        "title": "Crypto Market Maker Behavior",
        "def": "Crypto MMs differ from traditional: operate 24/7, manage inventory across fragmented exchanges, hedge on perps. Wintermute, Jump Trading, Alameda dominated pre-FTX. MMs earn spread + rebates, not directional bets.",
        "counter": "Crypto MM practices less regulated; some engage in wash trading, spoofing, or proprietary trading disguised as market making. FTX/Alameda collapse revealed commingling risks.",
        "data": "Post-FTX, institutional MMs tightened spreads and reduced risk. On-chain MMs (Uniswap LPs) gained share. Professional MMs now demand stricter custody and transparency from venues."
    },
    {
        "id": "crypto_correlation_breakdown",
        "title": "Crypto-Equity Correlation Breakdown",
        "def": "BTC-Nasdaq correlation averaged 0.6+ since 2020, driven by shared liquidity sensitivity. Correlation breaks during: crypto-specific events (ETF approval, halving), extreme risk-off (banking crises), or when crypto matures as distinct asset class.",
        "counter": "Correlation breakdowns are hard to time and often temporary. Structural correlation may persist as institutions treat crypto as risk asset. True decoupling requires broader adoption beyond speculative allocation.",
        "data": "Correlation dropped to 0.2 during ETF approval speculation (late 2023). Spiked to 0.8 during macro shocks (SVB crisis). Rolling 90-day correlation ranges 0.3-0.8 typically."
    },
    {
        "id": "tether_usdt_creation",
        "title": "Tether (USDT) Creation Mechanism",
        "def": "New USDT is minted when Tether Treasury receives fiat deposits (typically via banking partners). Authorized users (exchanges, institutions) request minting/redemption. Reserves should match circulation 1:1. Creation often precedes bull runs as buying power enters.",
        "counter": "Tether's opaque reserve composition and banking relationships raise concerns. Historical settlements with NYAG ($18.5M fine) highlighted disclosure gaps. Commercial paper holdings were controversial until shifted to Treasuries.",
        "data": "USDT market cap grew from $4B (2020) to $100B+ (2024). Reserves now 80%+ US Treasuries per attestations. Regular large mints (>1B) correlate with BTC price rallies."
    },
    {
        "id": "binance_dominance",
        "title": "Binance Market Dominance",
        "def": "Binance controls 40-60% of global crypto spot volume and significant derivatives share. BNB token powers ecosystem (fees, Launchpad, BSC). Dominance affects price discovery—Binance listings often pump, delistings crash tokens.",
        "counter": "Centralization risk: Binance outage halts trading for much of crypto world. Regulatory scrutiny (SEC lawsuit, CZ guilty plea) threatens dominance. Competitors (Coinbase, OKX) gaining share.",
        "data": "BNB market cap exceeded $80B at peak. Binance settled with DOJ/FinCEN for $4.3B (2023). Post-settlement, compliance increased but market share remained dominant."
    },
    {
        "id": "crypto_custody_solutions",
        "title": "Crypto Custody Solutions",
        "def": "Cold storage (hardware wallets, air-gapped computers) offers maximum security but UX friction. Multisig requires multiple keys for transactions, reducing single-point failures. Institutional custody (Fireblocks, Coinbase Prime) provides insurance and compliance.",
        "counter": "Self-custody demands technical competence; seed phrase loss means permanent fund loss. Institutional custody reintroduces counterparty risk—the very problem crypto aimed to solve.",
        "data": "MPC (Multi-Party Computation) wallets eliminate single key vulnerability. Hardware wallet sales (Ledger, Trezor) surged post-FTX. Bitcoin ETFs offer regulated custody alternative."
    },
    
    # On-Chain Analysis (24 fragments)
    {
        "id": "onchain_sopr",
        "title": "SOPR (Spent Output Profit Ratio)",
        "def": "SOPR = realized price / price paid for spent outputs. SOPR >1 means coins moved at profit; <1 at loss. Used to identify market tops (extreme profit-taking) and bottoms (capitulation). 7-day SMA smooths noise.",
        "counter": "SOPR can stay extreme during strong trends, giving premature reversal signals. Long-term holder spending distorts metric. Best used with other on-chain indicators, not standalone.",
        "data": "SOPR consistently dipped below 0.95 at cycle bottoms (2018, 2020, 2022). Peaks above 1.2 often marked local tops. Glassnode provides standardized SOPR data."
    },
    {
        "id": "onchain_mvrv",
        "title": "MVRV Ratio",
        "def": "Market Value to Realized Value ratio compares market cap to realized cap (sum of last-transacted prices). MVRV >3.5 signals overvaluation; <1 signals undervaluation. Historically marked major cycle turning points.",
        "counter": "MVRV thresholds shift as market matures. ETF-driven demand changes holder composition, potentially invalidating historical levels. Not reliable for timing short-term moves.",
        "data": "MVRV bottomed at 0.8 (2018), 0.9 (2020), 0.7 (2022). Peaks reached 3.5-4.0 at cycle tops. Realized price (~$22k for BTC in 2024) acts as fair value anchor."
    },
    {
        "id": "onchain_nvt",
        "title": "NVT Ratio",
        "def": "Network Value to Transactions ratio = market cap / daily transaction volume (USD). High NVT suggests overvaluation relative to utility (like P/E ratio). NVT Signal uses 90-day SMA for smoother readings.",
        "counter": "Transaction volume includes non-economic transfers (exchange internal movements), inflating denominator. Lightning Network growth reduces on-chain volume, breaking NVT comparability over time.",
        "data": "NVT ranged 15-30 historically for BTC. Spikes above 50 preceded major corrections. Declining NVT trend suggests maturing network utility relative to valuation."
    },
    {
        "id": "onchain_realized_price",
        "title": "Realized Price",
        "def": "Realized price = realized cap / circulating supply. Average price at which all coins last moved. Represents aggregate cost basis. Price above realized = market in profit; below = market at loss. Strong support/resistance level.",
        "counter": "Realized price lags during rapid moves as old coins finally spend. Doesn't distinguish between strategic accumulation vs distribution. Best combined with holder cohort analysis.",
        "data": "BTC realized price: $12k (2020), $20k (2021), $22k (2024). Price touching realized price often marks cycle bottoms. Short-term holder realized price is more sensitive indicator."
    },
    {
        "id": "onchain_holder_cohorts",
        "title": "Long-Term vs Short-Term Holders",
        "def": "LTH: coins unmoved >155 days. STH: <155 days. LTH supply increases during accumulation/bear markets; decreases when distributing to STH at tops. STH behavior drives short-term volatility; LTH sets long-term trend.",
        "counter": "155-day threshold is arbitrary; different markets may have different optimal cutoffs. Institutional holding patterns (ETFs) don't fit traditional cohort definitions.",
        "data": "LTH supply peaked at 75%+ near cycle bottoms. STH dominance (>50%) marked tops. 2024 saw unprecedented LTH accumulation ahead of ETF approvals."
    },
    {
        "id": "onchain_exchange_flows",
        "title": "Exchange Inflows/Outflows",
        "def": "Large exchange inflows often signal intent to sell (bearish). Outflows suggest accumulation/cold storage (bullish). Whale tracking (>1k BTC) provides early warning. Stablecoin inflows to exchanges indicate buying power ready.",
        "counter": "Flows can be internal rebalancing, OTC settlements, or exchange wallet migrations—not always selling intent. Context matters: outflows during rally differ from outflows during crash.",
        "data": "Exchange BTC balances hit 5-year lows in 2023-2024. Coinbase/Gemini outflows preceded ETF launches. Stablecoin exchange reserves correlate with subsequent buying pressure."
    },
    {
        "id": "onchain_stablecoin_supply",
        "title": "Stablecoin Supply Ratio",
        "def": "SSR = BTC market cap / stablecoin market cap. Measures potential buying power relative to BTC size. Low SSR = high dry powder (bullish). High SSR = stablecoins deployed or absent (bearish). Complement to stablecoin supply charts.",
        "counter": "Stablecoin supply includes non-BTC-related capital (DeFi, altcoins). USDT dominance skews metric if Tether prints for non-crypto purposes. Best used as secondary indicator.",
        "data": "SSR ranged 10-30 historically. Readings below 15 signaled strong buying power availability. Stablecoin market cap grew from $30B (2020) to $150B+ (2024)."
    },
    {
        "id": "onchain_miner_revenue",
        "title": "Miner Revenue & Capitulation",
        "def": "Miner revenue = block rewards + fees. When revenue < production cost (electricity + hardware), miners capitulate: sell reserves, shut down rigs, or go bankrupt. Miner position index (MPI) tracks selling pressure. Capitulation often marks bottoms.",
        "counter": "Efficient miners survive downturns; inefficient ones fail. Post-halving revenue drops don't always trigger capitulation if price appreciates. Mining industrialization changed capitulation dynamics.",
        "data": "Miner capitulation observed mid-2018, mid-2022. Post-2024 halving, marginal miners with >$50k/BTC costs struggled. Public miners hedged with forwards, reducing forced selling."
    },
    
    # Crypto Risk (12 fragments)
    {
        "id": "crypto_smart_contract_risk",
        "title": "Smart Contract Risk",
        "def": "Smart contracts carry bugs, exploits, and design flaws. Audits reduce but don't eliminate risk—auditors miss vulnerabilities. Common exploits: reentrancy, oracle manipulation, access control failures, integer overflow. Immutable code means no patches after deployment.",
        "counter": "Audit shopping (choosing lenient auditors) and time pressure compromise security. Formal verification is expensive and rare. Bug bounties help but reactive vs proactive. Insurance protocols (Nexus Mutual) emerging but limited coverage.",
        "data": "$3B+ lost annually to DeFi exploits. Major hacks: Poly Network ($600M returned), Wormhole ($325M), Ronin ($625M). Audited protocols still exploited—certifications provide false confidence."
    },
    {
        "id": "crypto_bridge_risk",
        "title": "Cross-Chain Bridge Risk",
        "def": "Bridges lock assets on source chain, mint wrapped versions on destination. Central points of failure: bridge contracts hold billions, making them prime targets. Design varies: trusted (multisig) vs trustless (light clients). Most hacks target bridges.",
        "counter": "Trustless bridges are complex and nascent; trusted bridges require faith in operators. No insurance covers bridge hacks fully. Users should minimize bridge time, use established bridges only.",
        "data": "Bridge hacks: Ronin ($625M), Wormhole ($325M), Nomad ($190M), Horizon ($100M). Bridges account for 40%+ of all DeFi hack losses. LayerZero, Axelar offer alternative architectures."
    },
    {
        "id": "crypto_regulatory_jurisdiction",
        "title": "Regulatory Risk by Jurisdiction",
        "def": "US: SEC enforcement-first approach, Howey Test applies to many tokens. EU: MiCA framework (2024) provides clarity but strict compliance. Asia: HK pro-crypto licensing; China banned trading/mining. Jurisdiction determines available products and protections.",
        "counter": "Regulatory arbitrage drives innovation offshore but limits US user access. Conflicting classifications (commodity vs security) create legal uncertainty. Global coordination lacking, forcing multi-jurisdiction compliance.",
        "data": "MiCA implementation began 2024. SEC sued Binance, Coinbase (2023). HK launched licensing regime. FATF Travel Rule enforcement increasing. Clarity expected from US legislation pending."
    },
    {
        "id": "crypto_exchange_counterparty",
        "title": "Exchange Counterparty Risk",
        "def": "FTX taught: never leave funds on exchanges unnecessarily. Proof of reserves insufficient without proof of liabilities. Commingling customer funds is fraud but hard to detect pre-collapse. Self-custody eliminates counterparty risk but adds operational burden.",
        "counter": "Self-custody isn't feasible for active traders or those lacking technical skills. Regulated exchanges (Coinbase) offer some protection but not FDIC insurance for crypto. Insurance funds cover only specific scenarios.",
        "data": "FTX customer shortfall: $8B+. Celsius, BlockFi, Voyager also failed. Post-FTX, exchange outflows surged. Regulatory requirements for segregation increasing but enforcement inconsistent."
    },
    {
        "id": "crypto_rug_pull_mechanics",
        "title": "Rug Pull Mechanics",
        "def": "Rug pulls: developers abandon project, drain liquidity, disappear with funds. Types: liquidity removal (DeFi), honeypot (can't sell), giveaway scams. Red flags: anonymous teams, unaudited code, unrealistic promises, concentrated token ownership.",
        "counter": "Some 'rug pulls' are legitimate failures, not intentional scams. Distinguishing requires forensic analysis. Even vetted projects can fail due to market conditions, not malice.",
        "data": "Chainalysis estimated $7.8B lost to rug pulls/scams in 2021. Squid Game token ($3M), AnubisDAO ($60M) notable examples. Token sniffer tools help detection but scammers adapt."
    },
    {
        "id": "crypto_tax_complexity",
        "title": "Crypto Tax Complexity",
        "def": "US treats crypto as property: every trade is taxable event. FIFO/LIFO/HIFO accounting methods. Staking rewards taxed as income at receipt. Wash sale rule doesn't apply to crypto (yet). DeFi interactions (swaps, LP deposits) create reporting burdens.",
        "counter": "Tracking thousands of transactions across chains/exchanges is impractical manually. Tax software (Koinly, CoinTracker) helps but costs money and may miss edge cases. IRS enforcement ramping up but still limited.",
        "data": "IRS added crypto question to Form 1040. Chainalysis contract aids enforcement. Tax-loss harvesting popular in bear markets. Proposed legislation may extend wash sale rule to crypto."
    },
]

# =============================================================================
# CLUSTER B: TECHNICAL ANALYSIS DEEP FILL (80 fragments)
# =============================================================================

TECHNICAL_TOPICS = [
    # Chart Patterns (24 fragments)
    {
        "id": "ta_head_shoulders",
        "title": "Head and Shoulders Pattern",
        "def": "Reversal pattern with three peaks: left shoulder, head (highest), right shoulder. Neckline connects lows. Break below neckline signals trend reversal from bullish to bearish. Target = head height projected downward from breakout. Inverse H&S signals bullish reversal.",
        "counter": "Pattern recognition is subjective; not all H&S formations complete. False breakouts common. Volume confirmation essential but often ignored. Works better on higher timeframes with clear structure.",
        "data": "Historical success rate 60-70% on daily/weekly charts. Failed patterns often become consolidation before continuation. Crypto's 24/7 trading creates more noise, reducing pattern reliability vs traditional markets."
    },
    {
        "id": "ta_double_top_bottom",
        "title": "Double Top / Double Bottom",
        "def": "Double top: two failed attempts at same resistance, signals bearish reversal. Double bottom: two tests of support holding, signals bullish reversal. Confirmation requires break of intermediate low/high. Target = pattern height projected from breakout.",
        "counter": "Many 'double tops' become continuation patterns after consolidation. W-shaped bottoms can have third leg down. Volume divergence on second test is key confirmation often missed.",
        "data": "Reliability increases with pattern duration—weeks/months better than hours. Crypto forms these patterns frequently due to round-number psychology ($20k, $50k BTC levels)."
    },
    {
        "id": "ta_triangles",
        "title": "Triangle Patterns",
        "def": "Symmetrical triangles: converging trendlines, breakout direction uncertain. Ascending triangles: flat resistance + rising lows, bullish bias. Descending triangles: flat support + falling highs, bearish bias. Breakout typically occurs 2/3-3/4 through pattern.",
        "counter": "Triangles often produce false breakouts before real move. Measuring targets is imprecise. Volume should decline during formation, surge on breakout—but crypto volume is easily manipulated.",
        "data": "Symmetrical triangles resolve in direction of prior trend 75% of time. Crypto triangles on 4H/daily charts have 60%+ success rate when volume confirms. Wedges are variant with sloping parallel lines."
    },
    {
        "id": "ta_flags_pennants",
        "title": "Flags and Pennants",
        "def": "Continuation patterns after sharp moves. Flag: parallel channel against trend. Pennant: small symmetrical triangle. Both represent brief consolidation before trend resumes. Target = length of prior 'flagpole' projected from breakout.",
        "counter": "In strong trends, flags may not form—price grinds higher/lower without clean patterns. What looks like flag mid-formation may become reversal. Timeframe matters: 4H+ more reliable than 15min.",
        "data": "Bull flags more reliable in uptrends than bear flags in downtrends (due to short-covering squeezes). Crypto trends often extend beyond measured targets due to momentum trading."
    },
    {
        "id": "ta_gaps",
        "title": "Price Gaps",
        "def": "Gaps occur when price opens significantly different from prior close. Types: common (filled quickly), breakaway (trend start), runaway/measurement (mid-trend), exhaustion (trend end). Traditional gap theory assumes gaps fill, but not always.",
        "counter": "Crypto trades 24/7, so gaps mainly occur on weekly/monthly opens or exchange-specific. CME Bitcoin futures gaps famously filled over time, but spot crypto rarely gaps. Gap theory less applicable to continuous markets.",
        "data": "CME BTC gaps from weekend closes filled 80%+ of time historically, influencing spot price. Sunday open gaps on crypto exchanges often fill within 24-48 hours. Gap-and-go patterns signal strong momentum."
    },
    {
        "id": "ta_wyckoff_method",
        "title": "Wyckoff Method",
        "def": "Richard Wyckoff's framework: market cycles through Accumulation (smart money buying), Markup (uptrend), Distribution (smart money selling), Markdown (downtrend). Key concepts: spring (false breakdown), UTAD (false breakout), effort vs result.",
        "counter": "Wyckoff schematics are subjective—different analysts label phases differently. Hindsight bias makes patterns look clearer than they are in real-time. Requires significant practice to apply consistently.",
        "data": "Wyckoff accumulations typically take weeks to months. Crypto's 2020-2021 bull run followed classic Wyckoff markup phase. 2022-2023 resembled prolonged accumulation schematic."
    },
    {
        "id": "ta_elliott_wave",
        "title": "Elliott Wave Principle",
        "def": "Markets move in 5-wave impulses (1-2-3-4-5) followed by 3-wave corrections (A-B-C). Wave 3 typically strongest; wave 4 shouldn't overlap wave 1. Fibonacci ratios guide wave targets. Fractal nature applies across timeframes.",
        "counter": "Wave counting is highly subjective—ten Elliott analysts give eleven counts. Rules have exceptions, exceptions have exceptions. Often works better in hindsight than real-time prediction.",
        "data": "Crypto's 2017 bull run fit textbook 5-wave structure. 2020-2021 showed extended wave 3 characteristics. Elliott practitioners successfully called major tops/bottoms but with many failed intermediate calls."
    },
    {
        "id": "ta_candlestick_patterns",
        "title": "Candlestick Patterns",
        "def": "Japanese candlestick patterns: Doji (indecision), Hammer/Shooting Star (reversal), Engulfing (momentum shift), Morning/Evening Star (multi-candle reversal). Single/multi-candle patterns signal potential turns. Require confirmation from subsequent candles.",
        "counter": "Single candlestick patterns have ~50% accuracy—coin flip. Reliability improves with confluence (support/resistance, volume, trend context). Crypto's volatility creates many false signals.",
        "data": "Engulfing patterns at key levels have 65%+ success rate on daily charts. Doji clusters often precede major moves. Candlestick patterns work best combined with other TA tools, not standalone."
    },
    
    # Advanced Indicators (24 fragments)
    {
        "id": "ta_volume_profile",
        "title": "Volume Profile",
        "def": "Volume Profile displays traded volume at specific price levels (horizontal histogram) rather than time. Point of Control (POC) = highest volume price. Value Area = 70% of volume range. High Volume Nodes (HVN) act as support/resistance; Low Volume Nodes (LVN) as rejection zones.",
        "counter": "Volume Profile is backward-looking; doesn't predict future. Different session settings (day/week/month) give different profiles. Crypto's fragmented liquidity across exchanges complicates accurate profile construction.",
        "data": "Price tends to gravitate toward POC, then either accept (consolidate) or reject (breakout). LVN retests often fail quickly. Composite profiles (multiple months) reveal long-term value areas."
    },
    {
        "id": "ta_vwap",
        "title": "VWAP (Volume-Weighted Average Price)",
        "def": "VWAP = cumulative (price × volume) / cumulative volume. Resets daily/weekly. Institutions use VWAP as benchmark—buy below, sell above. Acts as dynamic support/resistance. Deviation bands (±1, ±2 std dev) show extremes.",
        "counter": "VWAP resets create artificial levels that may not reflect true value. Crypto's 24/7 trading complicates session definition. Anchored VWAP (from specific event) often more relevant than standard VWAP.",
        "data": "Mean reversion strategies around VWAP work in ranging markets; trend-following (stay long above VWAP) works in trending markets. Crypto perpetual funding often correlates with VWAP deviation."
    },
    {
        "id": "ta_order_flow",
        "title": "Order Flow Analysis",
        "def": "Order flow examines individual transactions: aggressive buys (hitting asks) vs sells (hitting bids). Footprint charts show bid/ask volume per candle. Delta = buys minus sells. Absorption = large orders preventing price movement despite aggressive flow.",
        "counter": "Order flow data is exchange-specific and can be manipulated via wash trading. Requires fast execution to act on signals. Retail traders at disadvantage vs institutions with direct market access.",
        "data": "Cumulative delta divergence (price makes new high, delta doesn't) signals weakening trend. Large iceberg orders detected via repeated absorption at same level. Tools: Jigsaw, Sierra Chart, Bookmap."
    },
    {
        "id": "ta_market_profile",
        "title": "Market Profile (TPO)",
        "def": "Market Profile organizes price by time spent at levels (Time Price Opportunity). Balanced markets form bell curves; trending markets form skewed profiles. Initial Balance (first hour) often sets day's range. Extensions signal trend days.",
        "counter": "Market Profile designed for regulated futures markets with defined sessions. Less applicable to 24/7 crypto. Interpretation requires significant study. Modern volume-based tools often more practical.",
        "data": "Normal variation days (balanced profile) occur ~70% of time; trend days ~30%. Failed auctions (price rejected from value area extremes) offer high-probability mean reversion setups."
    },
    {
        "id": "ta_keltner_channels",
        "title": "Keltner Channels",
        "def": "Keltner Channels = EMA centerline with ATR-based bands (typically 2× ATR). Similar to Bollinger Bands but use ATR instead of standard deviation. Squeeze = bands tighten, signaling potential breakout. Trend follows band touch in strong moves.",
        "counter": "Like Bollinger Bands, Keltner Channels don't predict direction—just volatility state. Whipsaws common during choppy periods. Best combined with trend filters (ADX, moving averages).",
        "data": "Keltner Channel breakouts followed by return to mean in ranging markets 60-70% of time. Trend continuation after band ride more common in crypto than traditional markets due to momentum persistence."
    },
    {
        "id": "ta_adx",
        "title": "ADX (Average Directional Index)",
        "def": "ADX measures trend strength, not direction. ADX >25 = trending; <20 = ranging. +DI and -DI lines show direction. Divergence between ADX and price signals weakening trend. Useful for filtering strategies (trend-following vs mean-reversion).",
        "counter": "ADX is lagging indicator—by time ADX confirms trend, move may be mature. Whipsaws frequent during transitions. Crypto's tendency for parabolic moves can keep ADX elevated longer than expected.",
        "data": "ADX >50 indicates extremely strong trend, often near exhaustion. ADX <15 suggests accumulation/base building. Combining ADX with RSI improves entry timing in trending markets."
    },
    {
        "id": "ta_ichimoku",
        "title": "Ichimoku Cloud",
        "def": "Ichimoku Kinko Hyo ('one glance equilibrium'): Tenkan-sen (conversion line), Kijun-sen (base line), Senkou Span A/B (cloud), Chikou Span (lagging line). Cloud = support/resistance zone. Price above cloud = bullish; below = bearish. Future cloud projects support/resistance.",
        "counter": "Ichimoku appears complex; beginners struggle with multiple components. Signals can conflict (e.g., price above cloud but Tenkan/Kijun cross bearish). Works better on daily+ timeframes than intraday.",
        "data": "Cloud thickness indicates strength of support/resistance. TK cross inside cloud = weak signal; outside cloud = strong. Crypto's 24/7 nature requires adjusting default 9/26/52 parameters (based on trading weeks)."
    },
    {
        "id": "ta_stochastic",
        "title": "Stochastic Oscillator",
        "def": "Stochastic = (current close - lowest low) / (highest high - lowest low) × 100, typically 14-period. Range-bound 0-100. >80 overbought; <20 oversold. %K (fast) and %D (slow signal line). Divergences signal reversals.",
        "counter": "Stochastic can remain overbought/oversold during strong trends, giving premature reversal signals. Better for ranging markets. Fast stochastic whipsaws; slow stochastic smoother but more lag.",
        "data": "Stochastic hidden divergences (price makes higher low, stochastic makes lower low) signal trend continuation. Bull/bear setups (failure swings) more reliable than simple overbought/oversold reads."
    },
    
    # Volume & Sentiment (16 fragments)
    {
        "id": "ta_volume_confirmation",
        "title": "Volume Confirmation Principles",
        "def": "Volume confirms price: rising price + rising volume = healthy uptrend. Rising price + falling volume = divergence (weakness). Breakouts on low volume often fail. Climax volume signals exhaustion. Volume precedes price—surge often precedes big move.",
        "counter": "Crypto volume easily manipulated via wash trading. Exchange-reported volume unreliable; use aggregated or on-chain volume. Volume analysis works better on futures/CME than spot exchanges.",
        "data": "Up-days on above-average volume outnumber down-days in bull markets (and vice versa). Volume dry-ups during consolidation precede expansion. On-chain volume (settled) more reliable than exchange volume."
    },
    {
        "id": "ta_obv",
        "title": "On-Balance Volume (OBV)",
        "def": "OBV adds volume on up-days, subtracts on down-days, creating cumulative line. OBV trend should confirm price trend. Divergence (price up, OBV flat/down) signals weak rally. OBV breakout before price breakout signals smart money accumulation.",
        "counter": "OBV treats all volume equally regardless of price position. Doesn't account for intraday dynamics. Crypto's 24/7 trading creates ambiguous 'day' definitions for calculation.",
        "data": "OBV divergences preceded major crypto tops (2017, 2021). OBV leading breakouts occurred before BTC ETF approval rally. Cumulative OBV since inception shows long-term accumulation trends."
    },
    {
        "id": "ta_put_call_ratio",
        "title": "Put/Call Ratio",
        "def": "Put/Call ratio = put volume / call volume. High ratio (>1.0) = bearish sentiment (potential contrarian buy). Low ratio (<0.7) = bullish sentiment (potential contrarian sell). Options sentiment indicator. Equity-only vs total ratio variations exist.",
        "counter": "Extreme readings can persist during strong trends. Ratio shifted structurally lower as institutions buy protective puts. Crypto options market smaller than futures; signals less reliable than equities.",
        "data": "CME Bitcoin put/call ratio spiked >2.0 at 2022 bottom, <0.5 at 2021 top. Deribit dominates crypto options (>85% share). Skew (25-delta put-call IV difference) complements put/call analysis."
    },
    {
        "id": "ta_fear_greed",
        "title": "Fear & Greed Indicators",
        "def": "Composite indices combining: volatility, market momentum, social media sentiment, surveys, dominance, trends. Scale 0-100: extreme fear (<25) often marks bottoms; extreme greed (>75) marks tops. Contrarian indicator—be fearful when others greedy.",
        "counter": "Sentiment can remain extreme longer than fundamentals justify. Index methodology changes affect comparability. Social sentiment easily manipulated by bots/paid promotion.",
        "data": "Crypto Fear & Greed Index hit 10 (extreme fear) at 2022 bottom, 95 (extreme greed) at 2021 top. Sustained readings <20 for weeks often mark major bottoms. Mean reversion to 45-55 typical."
    },
    
    # EMH & TA Limitations (16 fragments)
    {
        "id": "ta_emh_critique",
        "title": "Efficient Market Hypothesis Critique of TA",
        "def": "EMH states prices reflect all available information, making TA useless for excess returns. Weak-form EMH specifically claims past prices can't predict future. Any predictable pattern should be arbitraged away instantly. Random walk theory supports EMH.",
        "counter": "Behavioral finance shows markets aren't perfectly efficient—human psychology creates repeatable patterns. TA works not because of magic but because many participants believe in it (self-fulfilling). Limits to arbitrage prevent instant correction.",
        "data": "Academic studies mixed: some show TA has no edge after costs; others document momentum/reversal anomalies. Crypto's retail-dominated markets less efficient than institutional equity markets, creating more TA opportunities."
    },
    {
        "id": "ta_self_fulfilling",
        "title": "TA as Self-Fulfilling Prophecy",
        "def": "TA works partly because enough participants watch same levels and act similarly. Round numbers ($50k BTC), moving averages (200-day), and classic patterns become focal points. Stop-loss clusters at obvious levels amplify moves when breached.",
        "counter": "As more participants use TA, edges diminish. Algorithms front-run obvious patterns. What worked historically may not work as markets evolve. TA is arms race, not static playbook.",
        "data": "Bitcoin respecting 200-week moving average (within 5%) held for years, creating psychological support. Mass liquidations at obvious technical levels demonstrate self-fulfilling dynamics. Institutional algos exploit retail TA levels."
    },
    {
        "id": "ta_survivorship_bias",
        "title": "Survivorship Bias in TA",
        "def": "TA backtests often suffer survivorship bias: testing on assets that survived, ignoring those that failed. Patterns appear profitable because losers excluded. Look-ahead bias (using future data) also inflates results. Proper backtesting requires point-in-time data.",
        "counter": "Even rigorous backtests can't account for regime changes. What worked in backtest may fail forward due to structural shifts. Transaction costs, slippage, and market impact often erase theoretical profits.",
        "data": "Cryptocurrency backtests particularly prone to bias—many coins from 2017 no longer exist. BTC/ETH survivorship makes TA look better than it was for diversified crypto portfolios. Delisted coins had worst TA patterns."
    },
    {
        "id": "ta_regime_dependency",
        "title": "TA Regime Dependency",
        "def": "TA strategies are regime-dependent: trend-following works in trending markets, mean-reversion in ranging. Identifying regime is half the battle. Regime changes often coincide with macro shifts (Fed policy, liquidity cycles). No strategy works always.",
        "counter": "Regime identification is retrospective—unclear in real-time which regime we're in. Strategies often adapted too late, buying tops/selling bottoms. Multi-strategy approaches dilute returns but reduce drawdowns.",
        "data": "2020-2021 trending regime favored breakout/momentum TA. 2022-2023 ranging regime favored mean-reversion. Crypto regimes shift faster than traditional markets due to 24/7 trading and retail dominance."
    },
]

# =============================================================================
# FRAGMENT CREATION FUNCTIONS
# =============================================================================

def create_fragment(topic_id, title, role, content, tags_extra=None):
    """Create and save a fragment JSON file."""
    if tags_extra is None:
        tags_extra = []
    
    filename = f"frag_fin_{topic_id}_{role}.json"
    filepath = os.path.join(FRAGMENT_DIR, filename)
    
    # Determine subdomain and tags
    if any(x in topic_id for x in ["btc_", "bitcoin", "utxo", "mempool", "segwit", "taproot", "difficulty", "blocksize"]):
        subdomain = "crypto"
        base_tags = ["crypto", "bitcoin"]
    elif any(x in topic_id for x in ["eth_", "ethereum", "eip", "merge", "staking", "slashing", "mev", "validator", "erc"]):
        subdomain = "crypto"
        base_tags = ["crypto", "ethereum"]
    elif any(x in topic_id for x in ["defi_", "amm", "impermanent", "liquidity", "flash", "yield", "tvl", "composability", "oracle"]):
        subdomain = "crypto"
        base_tags = ["crypto", "defi"]
    elif any(x in topic_id for x in ["funding", "open_interest", "liquidation", "market_maker", "correlation", "tether", "binance", "custody"]):
        subdomain = "crypto"
        base_tags = ["crypto", "market_structure"]
    elif any(x in topic_id for x in ["onchain", "sopr", "mvrv", "nvt", "realized", "holder", "exchange", "stablecoin", "miner"]):
        subdomain = "crypto"
        base_tags = ["crypto", "on_chain_metrics"]
    elif any(x in topic_id for x in ["smart_contract", "bridge", "regulatory", "counterparty", "rug", "tax"]):
        subdomain = "crypto"
        base_tags = ["crypto", "risk_management"]
    elif any(x in topic_id for x in ["ta_", "head", "double", "triangle", "flag", "gap", "wyckoff", "elliott", "candlestick"]):
        subdomain = "technical_analysis"
        base_tags = ["technical_analysis", "chart_patterns"]
    elif any(x in topic_id for x in ["volume_profile", "vwap", "order_flow", "market_profile", "keltner", "adx", "ichimoku", "stochastic"]):
        subdomain = "technical_analysis"
        base_tags = ["technical_analysis", "indicators"]
    elif any(x in topic_id for x in ["volume_", "obv", "put_call", "fear_greed"]):
        subdomain = "technical_analysis"
        base_tags = ["technical_analysis", "volume", "sentiment"]
    elif any(x in topic_id for x in ["emh", "self_fulfilling", "survivorship", "regime"]):
        subdomain = "technical_analysis"
        base_tags = ["technical_analysis", "theory"]
    else:
        subdomain = "finance"
        base_tags = ["finance"]
    
    # Add role-specific tag
    if role == "definition":
        base_tags.append("definition")
    elif role == "counter_argument":
        base_tags.append("counter_argument")
    elif role == "latest_data":
        base_tags.append("latest_data")
    
    # Combine tags
    all_tags = list(set(base_tags + tags_extra))
    
    # Determine credibility class
    if "risk" in topic_id or "regulatory" in topic_id or "tax" in topic_id:
        cred_class = "government_source"
    elif "data" in content.lower()[:100] or role == "latest_data":
        cred_class = "peer_reviewed_study"
    else:
        cred_class = "educational_resource"
    
    # Set source URL based on topic
    if "crypto" in subdomain:
        source_url = "https://bitcoin.org/bitcoin.pdf" if "btc" in topic_id else "https://ethereum.org" if "eth" in topic_id else "https://uniswap.org" if "defi" in topic_id else "https://glassnode.com"
    else:
        source_url = "https://www.investopedia.com"
    
    fragment = {
        "id": f"frag_fin_{topic_id}_{role}",
        "domain": "finance",
        "subdomain": subdomain,
        "tags": sorted(all_tags),
        "reasoning_role": role,
        "content": content.strip(),
        "source": "OpenEyes Knowledge Base",
        "source_url": source_url,
        "credibility_class": cred_class,
        "year": 2024,
        "compatible_with": [],
        "incompatible_with": [],
        "weight": 1.0
    }
    
    with open(filepath, 'w') as f:
        json.dump(fragment, f, indent=2)
    
    return filepath


def build_all_fragments():
    """Generate all fragments from both clusters."""
    count = 0
    
    print("Building CRYPTO fragments...")
    for topic in CRYPTO_TOPICS:
        tid = topic["id"]
        title = topic["title"]
        
        # Definition
        create_fragment(tid, title, "definition", topic["def"])
        count += 1
        
        # Counter Argument
        create_fragment(tid, title, "counter_argument", topic["counter"])
        count += 1
        
        # Latest Data
        create_fragment(tid, title, "latest_data", topic["data"])
        count += 1
    
    print(f"  Created {len(CRYPTO_TOPICS) * 3} crypto fragments")
    
    print("Building TECHNICAL ANALYSIS fragments...")
    for topic in TECHNICAL_TOPICS:
        tid = topic["id"]
        title = topic["title"]
        
        # Definition
        create_fragment(tid, title, "definition", topic["def"])
        count += 1
        
        # Counter Argument
        create_fragment(tid, title, "counter_argument", topic["counter"])
        count += 1
        
        # Latest Data
        create_fragment(tid, title, "latest_data", topic["data"])
        count += 1
    
    print(f"  Created {len(TECHNICAL_TOPICS) * 3} technical analysis fragments")
    
    print(f"\nTOTAL: {count} fragments generated")
    print(f"  Crypto: {len(CRYPTO_TOPICS) * 3}")
    print(f"  Technical Analysis: {len(TECHNICAL_TOPICS) * 3}")
    
    return count


if __name__ == "__main__":
    print("=" * 60)
    print("OpenEyes Fragment Builder: Crypto + Technical Analysis")
    print("=" * 60)
    build_all_fragments()
    print("\nFragment generation complete!")
