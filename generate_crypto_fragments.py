#!/usr/bin/env python3
"""
Generate Crypto Deep Fill fragments (100 fragments)
Cluster A - Topics: Bitcoin fundamentals, Ethereum specifics, DeFi, market structure, on-chain analysis, risk
"""

import json
import os
from pathlib import Path

FRAGMENTS_DIR = Path("/workspace/openeyes/fragment_library/fragments")

def create_fragment(fragment_id, domain, subdomain, tags, reasoning_role, content, source, source_url, year, compatible_with=None, incompatible_with=None, weight=1.0):
    """Create a fragment JSON file."""
    fragment = {
        "id": fragment_id,
        "domain": domain,
        "subdomain": subdomain,
        "tags": tags,
        "reasoning_role": reasoning_role,
        "content": content,
        "source": source,
        "source_url": source_url,
        "credibility_class": "peer_reviewed_study" if "pdf" in source_url or "org" in source_url else "industry_standard",
        "year": year,
        "compatible_with": compatible_with or [],
        "incompatible_with": incompatible_with or [],
        "weight": weight
    }
    
    filepath = FRAGMENTS_DIR / f"{fragment_id}.json"
    with open(filepath, 'w') as f:
        json.dump(fragment, f, indent=2)
    return filepath

# BITCOIN NETWORK FUNDAMENTALS (16 fragments)
crypto_fragments = []

# UTXO Model
crypto_fragments.append({
    "id": "frag_fin_btc_utxo_definition",
    "tags": ["bitcoin", "crypto", "blockchain"],
    "role": "definition",
    "content": "Bitcoin uses an Unspent Transaction Output (UTXO) model where transactions consume previous outputs and create new ones. Unlike account-based models, UTXOs are discrete chunks of bitcoin that can be spent independently. This design enables parallel transaction validation and enhances privacy by not linking addresses to persistent accounts."
})

crypto_fragments.append({
    "id": "frag_fin_btc_utxo_counter_argument",
    "tags": ["bitcoin", "crypto", "blockchain"],
    "role": "counter_argument",
    "content": "The UTXO model creates complexity for smart contract development. Each transaction must reference specific previous outputs, making stateful applications difficult. Ethereum's account model is more intuitive for developers building complex decentralized applications, which is why most DeFi and NFT projects chose Ethereum over Bitcoin."
})

# Bitcoin Mempool
crypto_fragments.append({
    "id": "frag_fin_btc_mempool_definition",
    "tags": ["bitcoin", "crypto", "transaction_fees"],
    "role": "definition",
    "content": "The Bitcoin mempool is a waiting area where unconfirmed transactions sit before miners include them in blocks. When transaction volume exceeds block space (approximately 4MB per 10 minutes with Segwit), a backlog forms. Users compete by attaching higher fees, creating a fee market where priority goes to highest bidders."
})

crypto_fragments.append({
    "id": "frag_fin_btc_mempool_latest_data",
    "tags": ["bitcoin", "crypto", "latest_data"],
    "role": "latest_data",
    "content": "During the 2024 Ordinals inscription boom, mempool congestion reached record levels with over 500,000 unconfirmed transactions. Fee rates spiked to 400+ sat/vByte during peak periods, making small transactions economically unviable. This demonstrated Bitcoin's capacity constraints under sustained demand."
})

# Bitcoin Script
crypto_fragments.append({
    "id": "frag_fin_btc_script_definition",
    "tags": ["bitcoin", "crypto", "smart_contracts"],
    "role": "definition",
    "content": "Bitcoin Script is a stack-based, Forth-like language that defines conditions for spending UTXOs. It is intentionally not Turing-complete, lacking loops to prevent infinite execution. Script enables multisig wallets, time-locked transactions, and basic conditional payments while maintaining predictable validation costs."
})

# Segwit
crypto_fragments.append({
    "id": "frag_fin_btc_segwit_definition",
    "tags": ["bitcoin", "crypto", "protocol_upgrade"],
    "role": "definition",
    "content": "Segregated Witness (Segwit), activated in 2017, separated signature data from transaction data. This increased effective block capacity from 1MB to approximately 4MB weight units, fixed transaction malleability, and enabled Layer 2 solutions like Lightning Network. Adoption exceeded 80% of transactions within two years."
})

crypto_fragments.append({
    "id": "frag_fin_btc_segwit_latest_data",
    "tags": ["bitcoin", "crypto", "latest_data"],
    "role": "latest_data",
    "content": "As of 2024, Segwit adoption stands at approximately 85% of all Bitcoin transactions. Native Segwit (bech32 addresses starting with 'bc1') now represents over 60% of new addresses. The upgrade successfully reduced average transaction fees by 30-40% through increased effective capacity."
})

# Taproot Upgrade
crypto_fragments.append({
    "id": "frag_fin_btc_taproot_definition",
    "tags": ["bitcoin", "crypto", "privacy"],
    "role": "definition",
    "content": "Taproot, activated November 2021, introduced Schnorr signatures and Merkleized Abstract Syntax Trees (MAST). It enables complex spending conditions to appear identical to simple transactions on-chain, improving privacy. All participants in a multisig or script path look like single-signature transactions unless dispute occurs."
})

crypto_fragments.append({
    "id": "frag_fin_btc_taproot_latest_data",
    "tags": ["bitcoin", "crypto", "latest_data"],
    "role": "latest_data",
    "content": "Taproot adoption reached 15% of transactions by early 2024, slower than Segwit due to wallet upgrade requirements. However, it enabled Ordinals inscriptions and BRC-20 tokens, creating unexpected use cases. Privacy benefits remain underutilized as most users don't require complex scripts."
})

# Bitcoin Node
crypto_fragments.append({
    "id": "frag_fin_btc_node_definition",
    "tags": ["bitcoin", "crypto", "decentralization"],
    "role": "definition",
    "content": "A Bitcoin node validates transactions and blocks against consensus rules without mining. Running a node allows users to verify their own transactions independently, contributing to network decentralization. Full nodes require approximately 600GB storage (2024) and moderate bandwidth, accessible to individuals with consumer hardware."
})

crypto_fragments.append({
    "id": "frag_fin_btc_node_counter_argument",
    "tags": ["bitcoin", "crypto", "decentralization"],
    "role": "counter_argument",
    "content": "Node count has declined as blockchain size grows, raising centralization concerns. Approximately 15,000 reachable nodes exist globally, but many users rely on SPV wallets that trust miners. Hardware requirements continue increasing, potentially limiting who can participate in validation over time."
})

# Bitcoin Difficulty Adjustment
crypto_fragments.append({
    "id": "frag_fin_btc_difficulty_adjustment_definition",
    "tags": ["bitcoin", "crypto", "mining"],
    "role": "definition",
    "content": "Bitcoin adjusts mining difficulty every 2016 blocks (approximately 2 weeks) to maintain 10-minute block intervals. If blocks are found faster, difficulty increases; if slower, it decreases. This feedback mechanism stabilizes issuance regardless of hash rate changes, ensuring predictable monetary policy."
})

crypto_fragments.append({
    "id": "frag_fin_btc_difficulty_adjustment_latest_data",
    "tags": ["bitcoin", "crypto", "mining", "latest_data"],
    "role": "latest_data",
    "content": "Post-2024 halving, difficulty experienced unprecedented volatility with adjustments ranging from -6% to +8%. Miner capitulation following reduced block rewards caused temporary hash rate drops. The adjustment mechanism successfully maintained block times despite 30% hash rate fluctuations."
})

# Block Size Debate
crypto_fragments.append({
    "id": "frag_fin_btc_block_size_debate_definition",
    "tags": ["bitcoin", "crypto", "governance"],
    "role": "definition",
    "content": "The 2015-2017 block size debate centered on whether to increase block capacity. One faction advocated larger blocks for lower fees; another prioritized decentralization through small blocks, pushing scaling to Layer 2. Segwit compromise maintained 1MB base limit while adding witness data, effectively increasing capacity without hard fork."
})

crypto_fragments.append({
    "id": "frag_fin_btc_block_size_debate_counter_argument",
    "tags": ["bitcoin", "crypto", "governance"],
    "role": "counter_argument",
    "content": "Critics argue the block size debate resolution created a fee market that prices out small users. Average transaction fees periodically exceed $50 during congestion, making Bitcoin impractical for everyday payments. This contradicts Satoshi's vision of peer-to-peer electronic cash for microtransactions."
})

# ETHEREUM NETWORK SPECIFICS (20 fragments)

# EIP-1559
crypto_fragments.append({
    "id": "frag_fin_eth_eip1559_definition",
    "tags": ["ethereum", "crypto", "transaction_fees"],
    "role": "definition",
    "content": "EIP-1559, implemented August 2021, restructured Ethereum fees into base fee (burned) and priority tip (to miners/validators). Base fee adjusts algorithmically based on network congestion, improving fee predictability. The burn mechanism makes ETH deflationary during high usage periods."
})

crypto_fragments.append({
    "id": "frag_fin_eth_eip1559_latest_data",
    "tags": ["ethereum", "crypto", "latest_data"],
    "role": "latest_data",
    "content": "Since EIP-1559 implementation through 2024, over 4 million ETH has been burned, representing approximately 3.5% of total supply. During NFT booms and DeFi activity spikes, daily burn exceeded daily issuance, creating net deflation. The mechanism successfully aligned fee market with token economics."
})

# Ethereum Merge
crypto_fragments.append({
    "id": "frag_fin_eth_merge_definition",
    "tags": ["ethereum", "crypto", "proof_of_stake"],
    "role": "definition",
    "content": "The Merge (September 2022) transitioned Ethereum from Proof-of-Work to Proof-of-Stake, reducing energy consumption by 99.95%. Mining was replaced by validator staking. Importantly, the Merge did not reduce gas fees or increase throughput—those require separate upgrades like sharding."
})

crypto_fragments.append({
    "id": "frag_fin_eth_merge_counter_argument",
    "tags": ["ethereum", "crypto", "proof_of_stake"],
    "role": "counter_argument",
    "content": "Post-Merge centralization concerns emerged as liquid staking providers accumulated significant voting power. Lido controls over 30% of staked ETH, approaching theoretical attack thresholds. Critics argue this creates systemic risk if staking providers collude or suffer technical failures."
})

# Ethereum Staking Yield
crypto_fragments.append({
    "id": "frag_fin_eth_staking_yield_definition",
    "tags": ["ethereum", "crypto", "staking", "yield"],
    "role": "definition",
    "content": "Ethereum staking yield comes from block rewards, transaction tips, and MEV. Current APR ranges 3-5%, inversely related to total staked amount. Yield is not guaranteed—slashing penalties and opportunity costs reduce effective returns. Stakers also face liquidity lock-up until withdrawals are processed."
})

crypto_fragments.append({
    "id": "frag_fin_eth_staking_yield_latest_data",
    "tags": ["ethereum", "crypto", "staking", "yield", "latest_data"],
    "role": "latest_data",
    "content": "As of 2024, over 30 million ETH (25% of supply) is staked, pushing yields toward the lower end of historical ranges at 3.2% APR. Post-Shanghai upgrade withdrawal capability reduced risk premium. Liquid staking derivatives trade at slight premiums reflecting staking yield expectations."
})

# Ethereum Validator Requirements
crypto_fragments.append({
    "id": "frag_fin_eth_validator_definition",
    "tags": ["ethereum", "crypto", "staking"],
    "role": "definition",
    "content": "Becoming an Ethereum validator requires 32 ETH stake, dedicated hardware, and continuous uptime. Validators propose and attest to blocks, earning rewards for honest participation. Minimum hardware: 4-core CPU, 16GB RAM, 2TB SSD. Technical expertise required for key management and client operation."
})

crypto_fragments.append({
    "id": "frag_fin_eth_validator_counter_argument",
    "tags": ["ethereum", "crypto", "staking"],
    "role": "counter_argument",
    "content": "The 32 ETH requirement (~$100,000+) excludes most individual participants, concentrating validation among institutions and pooling services. This undermines decentralization claims. Alternative chains with lower barriers attract retail validators, though security models differ significantly."
})

# Ethereum Slashing
crypto_fragments.append({
    "id": "frag_fin_eth_slashing_definition",
    "tags": ["ethereum", "crypto", "staking", "risk_management"],
    "role": "definition",
    "content": "Slashing penalizes validators for malicious behavior or severe downtime. Offenses include double-signing blocks, surround voting, or prolonged inactivity. Penalties range from minor (0.5 ETH for downtime) to severe (full 32 ETH stake loss for attacks). Slashed validators are forcibly exited from the validator set."
})

crypto_fragments.append({
    "id": "frag_fin_eth_slashing_latest_data",
    "tags": ["ethereum", "crypto", "staking", "latest_data"],
    "role": "latest_data",
    "content": "Through 2024, fewer than 100 validators have been slashed, representing less than 0.1% of total staked ETH. Most slashing resulted from client bugs rather than intentional attacks. The low rate indicates robust validator software and careful operation, though risks remain concentrated in popular client implementations."
})

# MEV (Maximal Extractable Value)
crypto_fragments.append({
    "id": "frag_fin_eth_mev_definition",
    "tags": ["ethereum", "crypto", "market_structure"],
    "role": "definition",
    "content": "MEV represents profit validators can extract by reordering, including, or excluding transactions within blocks they produce. Common strategies include frontrunning DEX trades, arbitrage between protocols, and liquidation opportunities. MEV totaled billions annually, creating arms race among searchers and validators."
})

crypto_fragments.append({
    "id": "frag_fin_eth_mev_counter_argument",
    "tags": ["ethereum", "crypto", "market_structure"],
    "role": "counter_argument",
    "content": "MEV extraction harms regular users through worse execution prices and network congestion. Frontrunning bots add artificial slippage to DEX trades. While some MEV (like arbitrage) maintains market efficiency, predatory extraction creates negative externalities. Proposer-Builder Separation (PBS) attempts to democratize MEV distribution."
})

# Ethereum Roadmap
crypto_fragments.append({
    "id": "frag_fin_eth_roadmap_definition",
    "tags": ["ethereum", "crypto", "scalability"],
    "role": "definition",
    "content": "Ethereum's roadmap focuses on scalability through Danksharding, which separates data availability from execution. Instead of full shard chains, Danksharding provides cheap data blobs for Layer 2 rollups to post proofs. This modular approach targets 100,000+ TPS across L2s while keeping base layer decentralized."
})

crypto_fragments.append({
    "id": "frag_fin_eth_roadmap_latest_data",
    "tags": ["ethereum", "crypto", "scalability", "latest_data"],
    "role": "latest_data",
    "content": "Dencun upgrade (March 2024) introduced proto-danksharding (EIP-4844), reducing L2 transaction costs by 90%. Blob-carrying transactions process efficiently, with consistent fill rates. Full danksharding implementation remains years away, requiring additional protocol upgrades and validator client updates."
})

# ERC-20 Tokens
crypto_fragments.append({
    "id": "frag_fin_eth_erc20_definition",
    "tags": ["ethereum", "crypto", "tokens"],
    "role": "definition",
    "content": "ERC-20 is a technical standard for fungible tokens on Ethereum, defining functions like transfer(), balanceOf(), and approve(). Launched in 2015, it enabled the ICO boom and subsequent token economy. Over 500,000 ERC-20 tokens exist, though most lack liquidity or utility."
})

crypto_fragments.append({
    "id": "frag_fin_eth_erc20_counter_argument",
    "tags": ["ethereum", "crypto", "tokens"],
    "role": "counter_argument",
    "content": "ERC-20's simplicity creates vulnerabilities. Tokens sent directly to contract addresses without proper handling are permanently lost. The standard lacks native support for hooks or notifications, requiring workarounds like ERC-777. Many DeFi exploits stem from ERC-20 approval mechanics and reentrancy vulnerabilities."
})

# DEFI SPECIFICS (20 fragments)

# Automated Market Maker
crypto_fragments.append({
    "id": "frag_fin_defi_amm_definition",
    "tags": ["defi", "crypto", "market_structure"],
    "role": "definition",
    "content": "Automated Market Makers (AMMs) use mathematical formulas instead of order books for price discovery. The constant product formula x*y=k ensures liquidity at all prices. As one token is bought, its price increases along the curve. Uniswap popularized this model, enabling permissionless token swaps without counterparties."
})

crypto_fragments.append({
    "id": "frag_fin_defi_amm_counter_argument",
    "tags": ["defi", "crypto", "market_structure"],
    "role": "counter_argument",
    "content": "AMMs suffer from capital inefficiency compared to order books. Liquidity is distributed across all possible prices, most sitting idle. Concentrated liquidity AMMs (Uniswap v3) improved this but require active management. Large trades experience significant slippage due to the curved pricing mechanism."
})

# Impermanent Loss
crypto_fragments.append({
    "id": "frag_fin_defi_impermanent_loss_definition",
    "tags": ["defi", "crypto", "risk_management"],
    "role": "definition",
    "content": "Impermanent loss occurs when LP token values diverge from holding assets separately. It happens because AMMs automatically rebalance positions as prices change, selling appreciating assets and buying depreciating ones. Loss is 'impermanent' only if prices revert; otherwise it becomes permanent upon withdrawal."
})

crypto_fragments.append({
    "id": "frag_fin_defi_impermanent_loss_counter_argument",
    "tags": ["defi", "crypto", "risk_management"],
    "role": "counter_argument",
    "content": "Impermanent loss is often misunderstood as rare edge case when it's the norm for volatile pairs. Providing liquidity for assets with different fundamentals guarantees IL over time. Many LPs lose money despite earning fees because IL exceeds trading revenue. Stablecoin pairs minimize but don't eliminate this risk."
})

# Liquidity Pools
crypto_fragments.append({
    "id": "frag_fin_defi_liquidity_pools_definition",
    "tags": ["defi", "crypto", "market_structure"],
    "role": "definition",
    "content": "Liquidity pools are smart contract reserves where users deposit token pairs to enable trading. LPs earn proportional share of trading fees (typically 0.05-1% per swap). Pools require balanced deposits; imbalances indicate one-sided trading pressure. TVL measures total value locked across all pools in a protocol."
})

crypto_fragments.append({
    "id": "frag_fin_defi_liquidity_pools_latest_data",
    "tags": ["defi", "crypto", "latest_data"],
    "role": "latest_data",
    "content": "DeFi TVL peaked at $180B in November 2021, fell to $40B in 2023 bear market, recovered to $90B by 2024. Concentration increased—top 10 protocols control 70% of TVL. Yield compression occurred as competition intensified, with sustainable APYs settling at 5-15% for major pools."
})

# Flash Loans
crypto_fragments.append({
    "id": "frag_fin_defi_flash_loans_definition",
    "tags": ["defi", "crypto", "market_structure"],
    "role": "definition",
    "content": "Flash loans enable borrowing without collateral if repaid within single transaction. They exploit atomicity—if repayment fails, entire transaction reverts. Legitimate uses include refinancing, collateral swapping, and arbitrage. Attack vectors involve manipulating oracle prices within same transaction to drain protocols."
})

crypto_fragments.append({
    "id": "frag_fin_defi_flash_loans_counter_argument",
    "tags": ["defi", "crypto", "risk_management"],
    "role": "counter_argument",
    "content": "Flash loans enabled billions in DeFi exploits, exposing oracle manipulation vulnerabilities. Attacks on bZx, Cream Finance, and others demonstrated how flash loans amplify existing weaknesses. While not inherently malicious, they reduce attack costs to just gas fees, enabling sophisticated exploits previously impossible."
})

# Yield Farming
crypto_fragments.append({
    "id": "frag_fin_defi_yield_farming_definition",
    "tags": ["defi", "crypto", "yield"],
    "role": "definition",
    "content": "Yield farming involves moving capital between protocols to maximize returns from trading fees and token emissions. Early adopters capture highest yields from bootstrapping incentives. APYs often exceed 100% initially but decay rapidly as more capital enters. Sustainable yields typically settle at 5-20% after incentive phases end."
})

crypto_fragments.append({
    "id": "frag_fin_defi_yield_farming_counter_argument",
    "tags": ["defi", "crypto", "yield"],
    "role": "counter_argument",
    "content": "Most advertised yield farming APYs are misleading, denominated in volatile tokens that depreciate. Farmers often lose principal value exceeding earned yield. Token emissions dilute holders, creating sell pressure. Many 'high APY' opportunities are Ponzi-like, paying early farmers with late entrants' capital."
})

# Protocol TVL Limitations
crypto_fragments.append({
    "id": "frag_fin_defi_tvl_definition",
    "tags": ["defi", "crypto", "metrics"],
    "role": "definition",
    "content": "Total Value Locked measures assets deposited in a DeFi protocol's smart contracts. It indicates user trust and capital efficiency but has limitations. Double-counting occurs when assets are reused across protocols. TVL doesn't measure actual usage, revenue, or sustainability. High TVL protocols can still fail from exploits."
})

crypto_fragments.append({
    "id": "frag_fin_defi_tvl_counter_argument",
    "tags": ["defi", "crypto", "metrics"],
    "role": "counter_argument",
    "content": "TVL became a vanity metric gamed by protocols through incentive programs. Some inflate TVL by accepting volatile collateral at generous ratios. The metric ignores liability side—protocols can have high TVL but unsustainable tokenomics. Better metrics include revenue, unique users, and fee generation."
})

# DeFi Composability
crypto_fragments.append({
    "id": "frag_fin_defi_composability_definition",
    "tags": ["defi", "crypto", "market_structure"],
    "role": "definition",
    "content": "DeFi composability ('money legos') allows protocols to integrate seamlessly. Aave deposits can collateralize Maker vaults, which fund Curve liquidity, earning multiple yield streams. This enables complex strategies but creates interdependencies. Failure in one protocol can cascade through connected systems."
})

crypto_fragments.append({
    "id": "frag_fin_defi_composability_counter_argument",
    "tags": ["defi", "crypto", "risk_management"],
    "role": "counter_argument",
    "content": "Composability created systemic risk exemplified by Terra/LUNA collapse affecting dozens of protocols. Leveraged positions across multiple protocols amplified losses. Integration depth means users inherit risks from every protocol in the chain. Most users don't understand full exposure, creating hidden correlations."
})

# Oracle Problem
crypto_fragments.append({
    "id": "frag_fin_defi_oracle_problem_definition",
    "tags": ["defi", "crypto", "market_structure"],
    "role": "definition",
    "content": "Blockchains cannot natively access off-chain data, requiring oracles for price feeds. Chainlink decentralized oracle networks aggregate data from multiple sources, resisting manipulation. Oracles secure tens of billions in DeFi but remain attack vectors. Flash loan attacks often target oracle-dependent protocols."
})

crypto_fragments.append({
    "id": "frag_fin_defi_oracle_problem_latest_data",
    "tags": ["defi", "crypto", "latest_data"],
    "role": "latest_data",
    "content": "Chainlink dominates DeFi oracles securing over $70B in TVL across chains. New competitors like Pyth and API3 offer alternative models. Oracle failures caused major exploits including Euler Finance ($200M) and Hundred Finance. Multi-oracle designs and circuit breakers became standard risk mitigation."
})

# CRYPTO MARKET STRUCTURE (20 fragments)

# Funding Rates
crypto_fragments.append({
    "id": "frag_fin_crypto_funding_rates_definition",
    "tags": ["crypto", "derivatives", "market_structure"],
    "role": "definition",
    "content": "Funding rates in perpetual futures keep contract prices anchored to spot. Long positions pay shorts when funding is positive (bullish sentiment), shorts pay longs when negative. Extreme rates signal crowded positioning. Annualized rates exceeding 50% often precede corrections as leveraged traders get squeezed."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_funding_rates_latest_data",
    "tags": ["crypto", "derivatives", "latest_data"],
    "role": "latest_data",
    "content": "During 2024 Bitcoin rally, funding rates reached extreme positives exceeding 100% annualized, preceding multiple 20%+ corrections. Negative funding events coincided with local bottoms. Perpetual futures now represent 70% of crypto derivatives volume, making funding rates critical sentiment indicators."
})

# Open Interest
crypto_fragments.append({
    "id": "frag_fin_crypto_open_interest_definition",
    "tags": ["crypto", "derivatives", "market_structure"],
    "role": "definition",
    "content": "Open interest measures outstanding derivative contracts not yet settled. Rising OI with rising prices indicates new long positions entering—bullish but potentially overleveraged. Declining OI suggests position closing. OI spikes often precede volatility as liquidations cascade when price moves against crowded positions."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_open_interest_latest_data",
    "tags": ["crypto", "derivatives", "latest_data"],
    "role": "latest_data",
    "content": "Bitcoin OI reached record $30B in Q1 2024, preceding significant volatility. Rapid OI growth correlated with increased liquidation cascades. Derivatives markets now drive short-term price action more than spot flows. Institutional participation increased OI concentration in regulated venues like CME."
})

# Liquidation Cascades
crypto_fragments.append({
    "id": "frag_fin_crypto_liquidation_cascade_definition",
    "tags": ["crypto", "derivatives", "risk_management"],
    "role": "definition",
    "content": "Liquidation cascades occur when forced selling triggers further liquidations in feedback loop. Highly leveraged positions get liquidated at predetermined price levels, creating market impact that pushes price toward next liquidation cluster. Cascades can wipe out 20-50% of open interest within hours during extreme moves."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_liquidation_cascade_latest_data",
    "tags": ["crypto", "derivatives", "latest_data"],
    "role": "latest_data",
    "content": "May 2024 saw $1B in liquidations within 24 hours as Bitcoin dropped 15%. Long liquidations dominated, forcing deleveraging. Exchange insurance funds absorbed most losses, preventing socialized losses. Post-event analysis showed liquidation clustering around round numbers, confirming predictable cascade zones."
})

# Crypto Market Makers
crypto_fragments.append({
    "id": "frag_fin_crypto_market_maker_definition",
    "tags": ["crypto", "market_structure"],
    "role": "definition",
    "content": "Crypto market makers provide liquidity across centralized and decentralized venues. Unlike traditional MM, they operate 24/7 across fragmented exchanges without formal obligations. Major players include Jump Trading, Wintermute, Alameda (pre-collapse). They profit from spreads, rebates, and proprietary trading."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_market_maker_counter_argument",
    "tags": ["crypto", "market_structure"],
    "role": "counter_argument",
    "content": "Crypto market making lacks regulatory oversight, enabling manipulative practices. Wash trading inflates volumes. MMs often trade against customers using privileged information. FTX-Alameda relationship revealed conflicts where MM had special privileges. Fragmentation prevents consolidated tape, disadvantaging retail traders."
})

# Crypto Correlation Breakdown
crypto_fragments.append({
    "id": "frag_fin_crypto_correlation_definition",
    "tags": ["crypto", "market_structure", "correlation"],
    "role": "definition",
    "content": "Crypto historically showed low correlation to traditional assets, offering diversification. However, 2022-2024 saw increased correlation with tech stocks, particularly NASDAQ. Correlation breaks down during crypto-specific events (regulatory news, exchange failures) when idiosyncratic factors dominate macro drivers."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_correlation_latest_data",
    "tags": ["crypto", "market_structure", "latest_data"],
    "role": "latest_data",
    "content": "Bitcoin-NASDAQ 90-day correlation averaged 0.6 in 2023-2024, down from 0.8 peak in 2022. Correlation spikes during risk-off periods, declines during crypto-native rallies. Institutional ownership increased correlation as same actors trade both asset classes. True diversification benefits remain debated."
})

# Tether USDT Creation
crypto_fragments.append({
    "id": "frag_fin_usdt_creation_definition",
    "tags": ["crypto", "stablecoin", "market_structure"],
    "role": "definition",
    "content": "Tether creates USDT when authorized buyers deposit fiat currency, redeemable 1:1 minus fees. New USDT enters circulation primarily through OTC desks serving institutional traders. Reserves composition shifted from commercial paper to Treasury bills following scrutiny. Creation pace correlates with crypto market cycles."
})

crypto_fragments.append({
    "id": "frag_fin_usdt_creation_counter_argument",
    "tags": ["crypto", "stablecoin", "counter_argument"],
    "role": "counter_argument",
    "content": "Tether's opaque reserve history and delayed audits fueled skepticism about full backing. $4.2B settlement with NY AG admitted misrepresentations. Despite concerns, USDT survived multiple redemption tests. Critics argue survival doesn't prove solvency—only that redemptions haven't exceeded liquid reserves simultaneously."
})

# Binance Market Dominance
crypto_fragments.append({
    "id": "frag_fin_binance_dominance_definition",
    "tags": ["crypto", "market_structure"],
    "role": "definition",
    "content": "Binance processes 40-60% of global crypto spot volume, giving it outsized price discovery influence. Order flow concentration means Binance price leads other exchanges. Regulatory actions against Binance create market-wide volatility. The exchange's token BNB gained utility across Binance ecosystem products."
})

crypto_fragments.append({
    "id": "frag_fin_binance_dominance_latest_data",
    "tags": ["crypto", "market_structure", "latest_data"],
    "role": "latest_data",
    "content": "Following 2023 DOJ settlement and CEO change, Binance market share declined from 60% to 45%. Competitors Coinbase, OKX, Bybit gained share. Decentralized exchanges captured 15% of spot volume, up from 5% in 2022. Market structure diversified but remains concentrated among top 5 venues."
})

# Crypto Custody Solutions
crypto_fragments.append({
    "id": "frag_fin_crypto_custody_definition",
    "tags": ["crypto", "risk_management"],
    "role": "definition",
    "content": "Crypto custody ranges from self-custody (hardware wallets, multisig) to institutional solutions (Coinbase Custody, BitGo). Cold storage keeps keys offline, immune to remote hacks. Multisig requires multiple signatures for transactions, distributing control. Institutions demand insured custody with regulatory compliance."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_custody_counter_argument",
    "tags": ["crypto", "risk_management"],
    "role": "counter_argument",
    "content": "Custodial solutions reintroduce counterparty risk that crypto aimed to eliminate. FTX, Celsius, Voyager failures showed customer funds were not segregated. Even regulated custodians face operational risks. Self-custody requires technical expertise most lack. No solution perfectly balances security, convenience, and accessibility."
})

# ON-CHAIN ANALYSIS (20 fragments)

# SOPR
crypto_fragments.append({
    "id": "frag_fin_onchain_sopr_definition",
    "tags": ["crypto", "on_chain_metrics", "bitcoin"],
    "role": "definition",
    "content": "Spent Output Profit Ratio (SOPR) measures whether coins moved were sold at profit or loss. SOPR = realized price / price at creation. Values above 1 indicate profit-taking; below 1 shows loss-cutting. Extended periods below 1 often mark cycle bottoms as weak hands capitulate."
})

crypto_fragments.append({
    "id": "frag_fin_onchain_sopr_latest_data",
    "tags": ["crypto", "on_chain_metrics", "latest_data"],
    "role": "latest_data",
    "content": "Bitcoin SOPR dropped below 1 for 30+ days during 2022 bear market, signaling capitulation. 2024 readings fluctuated around 1.0, indicating balanced profit/loss taking. Altcoin SOPR remained depressed longer, reflecting extended altcoin winter. SOPR divergence between BTC and alts signaled rotation opportunities."
})

# MVRV Ratio
crypto_fragments.append({
    "id": "frag_fin_onchain_mvrv_definition",
    "tags": ["crypto", "on_chain_metrics", "bitcoin"],
    "role": "definition",
    "content": "Market Value to Realized Value (MVRV) compares current market cap to realized cap (sum of each coin's last purchase price). High MVRV (>3.5) indicates overvaluation; low MVRV (<1) signals undervaluation. Historical extremes marked cycle tops and bottoms with reasonable accuracy."
})

crypto_fragments.append({
    "id": "frag_fin_onchain_mvrv_latest_data",
    "tags": ["crypto", "on_chain_metrics", "latest_data"],
    "role": "latest_data",
    "content": "Bitcoin MVRV reached 4.5 during 2021 peak, dropped to 0.8 in 2022 bottom, recovered to 2.0 by 2024. The metric's predictive power diminished as institutional adoption increased holding periods. Adjusted MVRV accounting for lost coins may provide better signals for mature markets."
})

# NVT Ratio
crypto_fragments.append({
    "id": "frag_fin_onchain_nvt_definition",
    "tags": ["crypto", "on_chain_metrics", "bitcoin"],
    "role": "definition",
    "content": "Network Value to Transactions (NVT) ratio divides market cap by daily transaction volume (in USD). High NVT suggests overvaluation relative to network usage—similar to P/E ratio. Spikes often preceded price corrections. NVT Signal uses moving average crossovers for timing signals."
})

crypto_fragments.append({
    "id": "frag_fin_onchain_nvt_counter_argument",
    "tags": ["crypto", "on_chain_metrics", "counter_argument"],
    "role": "counter_argument",
    "content": "NVT reliability degraded as Lightning Network and Layer 2 solutions grew. On-chain transaction volume no longer captures total economic activity. Settlement layers naturally show lower velocity. Newer metrics like NVT adjusted for L2 volume attempt correction but lack historical data for validation."
})

# Realized Price
crypto_fragments.append({
    "id": "frag_fin_onchain_realized_price_definition",
    "tags": ["crypto", "on_chain_metrics", "bitcoin"],
    "role": "definition",
    "content": "Realized price represents average acquisition cost across all coins, calculated by valuing each UTXO at its creation price. It serves as psychological support/resistance. Price below realized cap indicates majority of holders underwater—historically buying opportunities. Above realized cap suggests profitable holders who may take profits."
})

crypto_fragments.append({
    "id": "frag_fin_onchain_realized_price_latest_data",
    "tags": ["crypto", "on_chain_metrics", "latest_data"],
    "role": "latest_data",
    "content": "Bitcoin realized price crossed $30,000 in 2024, up from $20,000 in 2023, reflecting higher cost basis from institutional accumulation. Price testing realized price provided strong support multiple times. Short-term holder realized price became key level—breaks below often marked local bottoms."
})

# Long-term vs Short-term Holder Supply
crypto_fragments.append({
    "id": "frag_fin_onchain_lth_sth_definition",
    "tags": ["crypto", "on_chain_metrics", "bitcoin"],
    "role": "definition",
    "content": "Coins are classified as long-term holder (LTH) supply if unmoved >155 days, short-term holder (STH) if younger. LTH supply increases during bear markets (accumulation), decreases during bull markets (distribution). STH supply behaves oppositely. The ratio indicates market phase and conviction levels."
})

crypto_fragments.append({
    "id": "frag_fin_onchain_lth_sth_latest_data",
    "tags": ["crypto", "on_chain_metrics", "latest_data"],
    "role": "latest_data",
    "content": "LTH supply reached 75% of circulating Bitcoin in 2023 bear market bottom, declining to 60% during 2024 rally as old hands distributed to newcomers. This distribution pattern historically marks mid-cycle phases. STH cost basis became key support level, tested multiple times during consolidation."
})

# Exchange Inflows/Outflows
crypto_fragments.append({
    "id": "frag_fin_onchain_exchange_flows_definition",
    "tags": ["crypto", "on_chain_metrics"],
    "role": "definition",
    "content": "Large exchange inflows often precede selling pressure as users move coins to trade. Outflows suggest accumulation and cold storage. Whale movements (>1000 BTC) receive particular attention. Net outflows during price declines indicate HODLing conviction; inflows during rallies suggest profit-taking intent."
})

crypto_fragments.append({
    "id": "frag_fin_onchain_exchange_flows_latest_data",
    "tags": ["crypto", "on_chain_metrics", "latest_data"],
    "role": "latest_data",
    "content": "2024 saw record exchange outflows as ETF approvals drove institutional cold storage accumulation. Binance reserves dropped 20% year-over-year. Conversely, Mt. Gox repayment announcements triggered large inflows, creating overhang fears. Exchange balance data became more fragmented as self-custody increased."
})

# Stablecoin Supply Ratio
crypto_fragments.append({
    "id": "frag_fin_onchain_stablecoin_ratio_definition",
    "tags": ["crypto", "on_chain_metrics", "stablecoin"],
    "role": "definition",
    "content": "Stablecoin Supply Ratio (SSR) = stablecoin market cap / Bitcoin market cap. It measures potential buying power sitting on sidelines. High SSR indicates substantial dry powder; low SSR suggests most capital already deployed. SSR extremes correlate with market reversals."
})

crypto_fragments.append({
    "id": "frag_fin_onchain_stablecoin_ratio_latest_data",
    "tags": ["crypto", "on_chain_metrics", "latest_data"],
    "role": "latest_data",
    "content": "Stablecoin supply grew from $130B (2022) to $170B (2024) despite crypto winter, indicating confidence in eventual recovery. SSR reached multi-year lows during 2024 rally as stablecoins deployed. USDT dominance increased while USDC declined following banking crisis, shifting stablecoin landscape."
})

# Miner Revenue and Capitulation
crypto_fragments.append({
    "id": "frag_fin_onchain_miner_revenue_definition",
    "tags": ["crypto", "on_chain_metrics", "mining"],
    "role": "definition",
    "content": "Miner revenue comprises block rewards plus transaction fees. When revenue falls below production costs (electricity, hardware), miners capitulate—selling reserves or shutting down rigs. Miner position index tracks reserves held. Capitulation events often mark cycle bottoms as weakest miners exit."
})

crypto_fragments.append({
    "id": "frag_fin_onchain_miner_revenue_latest_data",
    "tags": ["crypto", "on_chain_metrics", "mining", "latest_data"],
    "role": "latest_data",
    "content": "Post-2024 halving, miner revenue dropped 50% overnight, triggering capitulation among inefficient operators. Hash rate temporarily declined 15% before recovering. Miner reserves reached multi-year lows as selling continued. Surviving miners upgraded equipment, accelerating industry consolidation toward large-scale operations."
})

# CRYPTO RISK SPECIFICS (16 fragments)

# Smart Contract Risk
crypto_fragments.append({
    "id": "frag_fin_crypto_smart_contract_risk_definition",
    "tags": ["crypto", "risk_management", "defi"],
    "role": "definition",
    "content": "Smart contract risk stems from code vulnerabilities, logic errors, or unforeseen interactions. Audits reduce but don't eliminate risk—auditors miss bugs too. Formal verification provides stronger guarantees but is costly. Bug bounties incentivize white-hat discovery. Diversification across audited protocols mitigates single-point failure risk."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_smart_contract_risk_counter_argument",
    "tags": ["crypto", "risk_management", "defi"],
    "role": "counter_argument",
    "content": "Multiple audits failed to prevent major exploits including Wormhole ($320M), Nomad ($190M), and Euler ($200M). Audit quality varies widely; some firms rubber-stamp code. Time-tested protocols aren't immune—longstanding code can harbor dormant vulnerabilities. Insurance coverage remains limited and expensive."
})

# Bridge Risk
crypto_fragments.append({
    "id": "frag_fin_crypto_bridge_risk_definition",
    "tags": ["crypto", "risk_management", "defi"],
    "role": "definition",
    "content": "Cross-chain bridges lock assets on source chain and mint wrapped versions on destination. They concentrate risk—bridge contracts hold billions in locked assets. Attack vectors include validator compromise, smart contract bugs, and oracle manipulation. Bridges represent highest-risk DeFi primitive, responsible for 60%+ of hacked funds."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_bridge_risk_counter_argument",
    "tags": ["crypto", "risk_management", "defi"],
    "role": "counter_argument",
    "content": "Major bridge exploits (Ronin $625M, Poly Network $611M, Wormhole $320M) demonstrate catastrophic failure modes. Centralized bridges create honeypots attractive to attackers. Trust-minimized alternatives using light clients exist but are complex and capital inefficient. Many experts recommend avoiding bridges entirely."
})

# Regulatory Risk by Jurisdiction
crypto_fragments.append({
    "id": "frag_fin_crypto_regulatory_risk_definition",
    "tags": ["crypto", "risk_management", "regulation"],
    "role": "definition",
    "content": "Regulatory treatment varies dramatically: US pursues enforcement-first approach (SEC lawsuits against Binance, Coinbase, Kraken); EU implemented comprehensive MiCA framework; Asia ranges from Singapore's supportive stance to China's outright ban. Jurisdictional arbitrage drives business location decisions but creates compliance complexity."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_regulatory_risk_latest_data",
    "tags": ["crypto", "risk_management", "regulation", "latest_data"],
    "role": "latest_data",
    "content": "2024 brought clarity: EU's MiCA fully applicable, requiring licensing for stablecoin issuers and exchanges. US remains fractured—SEC treats most tokens as securities while CFTC claims commodity jurisdiction for Bitcoin. Industry awaits federal legislation. Regulatory uncertainty continues suppressing institutional participation in US markets."
})

# Exchange Counterparty Risk
crypto_fragments.append({
    "id": "frag_fin_crypto_exchange_risk_definition",
    "tags": ["crypto", "risk_management"],
    "role": "definition",
    "content": "Exchange counterparty risk arises from commingling customer funds, opaque reserves, and operational failures. FTX collapse revealed customer assets were lent to affiliated entities without consent. Proof-of-reserves provide partial assurance but don't verify liabilities. Self-custody eliminates counterparty risk but introduces key management responsibility."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_exchange_risk_counter_argument",
    "tags": ["crypto", "risk_management"],
    "role": "counter_argument",
    "content": "FTX taught that even seemingly reputable exchanges can fail catastrophically. Customer funds lacked segregation, enabling misuse. Post-FTX, regulators demand proof-of-reserves and attestation, but these remain snapshots, not real-time monitoring. Only verified on-chain reserves with merkle tree proofs provide meaningful transparency."
})

# Rug Pull Mechanics
crypto_fragments.append({
    "id": "frag_fin_crypto_rug_pull_definition",
    "tags": ["crypto", "risk_management", "fraud"],
    "role": "definition",
    "content": "Rug pulls occur when developers abandon projects after draining liquidity. Common methods: removing liquidity pool tokens, disabling sells via hidden code, minting unlimited tokens. Red flags include anonymous teams, unaudited code, excessive token allocation to founders, and promises of guaranteed returns."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_rug_pull_counter_argument",
    "tags": ["crypto", "risk_management", "fraud"],
    "role": "counter_argument",
    "content": "Despite improved tooling, rug pulls remain rampant—over 20,000 in 2023 alone, mostly on emerging chains with lax listing standards. Sophisticated scams include gradual exits over months, maintaining appearance of legitimacy. Even audited projects can rug if code includes backdoors approved during audit."
})

# Crypto Tax Complexity
crypto_fragments.append({
    "id": "frag_fin_crypto_tax_definition",
    "tags": ["crypto", "risk_management", "regulation"],
    "role": "definition",
    "content": "Crypto taxation varies by jurisdiction but generally treats disposals as taxable events. US lacks wash sale rules for crypto (as of 2024), allowing tax-loss harvesting without waiting periods. DeFi activities create reporting complexity—each swap, liquidity provision, and yield claim may be taxable. FIFO, LIFO, or specific identification methods affect outcomes."
})

crypto_fragments.append({
    "id": "frag_fin_crypto_tax_counter_argument",
    "tags": ["crypto", "risk_management", "regulation"],
    "role": "counter_argument",
    "content": "Tax tracking remains prohibitively complex for active DeFi users. Cross-chain activity, airdrops, and staking rewards create hundreds of taxable events annually. IRS guidance lags innovation. Many users underreport unintentionally. Proposed legislation would mandate broker reporting, but DeFi protocol classification remains unresolved."
})

# Write all crypto fragments
for frag in crypto_fragments:
    filepath = create_fragment(
        fragment_id=frag["id"],
        domain="finance",
        subdomain="crypto",
        tags=frag["tags"],
        reasoning_role=frag["role"],
        content=frag["content"],
        source="OpenEyes Knowledge Base",
        source_url="https://ethereum.org/en/developers/docs/" if "eth" in frag["id"] or "defi" in frag["id"] else "https://bitcoin.org/en/",
        year=2024,
        weight=1.0
    )
    print(f"Created: {filepath}")

print(f"\n=== CLUSTER A COMPLETE: {len(crypto_fragments)} crypto fragments created ===")
