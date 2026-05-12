# Sector-Based Fragment Organization

## Overview

The Autonomous Signal-Pulse Swarm now implements **sector-based fragment organization**, creating a self-updating knowledge base that automatically categorizes harvested data by domain sector and manages fragment expiration.

## Architecture

### Domain Sectors

All harvested fragments are automatically classified into one of these sectors:

| Sector | Description | Examples | TTL Default |
|--------|-------------|----------|-------------|
| **ECO** | Economy, Finance, Crypto, Commodities | Bitcoin prices, exchange rates, stock tickers | 6 hours |
| **GOV** | Government, Policy, Regulations | Whitehouse policies, federal regulations | 24 hours |
| **HC** | Healthcare, Medical, Pharmaceuticals | Medical research, drug info, clinical trials | 12 hours |
| **TECH** | Technology, Software, Hardware | Tech news, API docs, software releases | 12 hours |
| **NEWS** | General News, Media | RSS feeds, blog posts, articles | 6 hours |
| **GENERAL** | Everything else | Unclassified sources | 24 hours |

### Key Features

#### 1. Automatic Sector Classification
```python
# Harvester agents automatically classify URLs
sector = agent._classify_domain_sector("https://api.coindesk.com/v1/bpi/currentprice.json")
# Returns: "ECO"
```

Classification keywords:
- **ECO**: crypto, bitcoin, btc, eth, coin, binance, coindesk, exchange, forex, rate, currency, usd, eur, gbp, stock, ticker, alphavantage, gold, silver, commodity, finance, trading, market
- **GOV**: gov, policy, regulation, legislation, congress, parliament, federal, ministry, department, official, whitehouse
- **HC**: health, medical, hospital, clinic, pharma, drug, medicine, patient, disease, covid, vaccine, clinical, healthcare, med, nih, who, fda
- **TECH**: tech, software, hardware, api, github, dev, code, programming, ai, ml, blockchain, cloud, server, hackernoon, techcrunch
- **NEWS**: news, rss, feed, media, press, article, blog, cointelegraph, reuters, bloomberg

#### 2. Time-To-Live (TTL) Expiration
```python
# Write fragment with 6-hour TTL (for volatile financial data)
await wal_buffer.write(
    agent_id="harvester_42",
    data_type="tokenized_content",
    content="As of May 13, 2026, Bitcoin price is $67,842.50 USD",
    tokens={"hash": "abc123", "source": "coindesk"},
    domain_sector="ECO",
    ttl_hours=6  # Expires in 6 hours
)
```

TTL rationale:
- **6 hours**: High-volatility data (crypto, exchange rates, breaking news)
- **12 hours**: Medium-volatility data (tech updates, medical research)
- **24 hours**: Stable data (government policies, general knowledge)

#### 3. Expired Fragment Archival
Every 15 minutes, Organizer agents:
1. Query WAL buffer for expired fragments (`expiry_time < NOW`)
2. Group fragments by sector
3. Flag for archival (move to long-term storage)
4. Update TF-IDF scores based on remaining active fragments

```python
# Organizer processes expired fragments
expired = await wal_buffer.get_expired_fragments()
# Returns: [{"id": 1, "domain_sector": "ECO", "content": "..."}, ...]

# Group by sector
by_sector = {"ECO": [...], "HC": [...]}

# Archive each sector separately
for sector, fragments in by_sector.items():
    print(f"Archiving {len(fragments)} expired {sector} fragments")
```

### Database Schema

```sql
CREATE TABLE wal_buffer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT,
    timestamp TEXT,
    data_type TEXT,
    content TEXT,
    tokens_json TEXT,
    domain_sector TEXT,      -- NEW: ECO, GOV, HC, TECH, NEWS, GENERAL
    is_expired INTEGER DEFAULT 0,  -- NEW: Flag for archiver
    expiry_time TEXT,        -- NEW: When fragment expires
    processed INTEGER DEFAULT 0
);

-- Indexes for fast queries
CREATE INDEX idx_sector ON wal_buffer(domain_sector);
CREATE INDEX idx_expired ON wal_buffer(is_expired);
CREATE INDEX idx_unprocessed ON wal_buffer(processed);
```

## Benefits

### 1. Organized Knowledge Base
- Fragments are immediately categorized by domain
- Query routing can prioritize relevant sectors
- Easy to purge/archive entire sectors if needed

### 2. Data Freshness Guarantee
- Volatile data (crypto, exchange rates) auto-expires in 6 hours
- System always serves recent, relevant information
- No stale data polluting query results

### 3. Efficient Archival
- Expired fragments flagged automatically
- Organizers process archival in batches by sector
- Long-term storage can compress historical data

### 4. Self-Updating System
- New data continuously replaces old data
- TF-IDF scores recalculated on active fragments only
- Rules engine updates based on fresh data patterns

## Usage Example

```python
from openeyes.swarm.autonomous_pulse_swarm import AutonomousSwarm

# Create swarm with sector-based organization
swarm = AutonomousSwarm.create_default(
    num_harvesters=800,
    num_workers=180,
    num_organizers=20
)

# Start autonomous operation
await swarm.start_continuous(num_cycles=-1)

# Behind the scenes:
# 1. Harvesters fetch data → classify by sector → write to WAL
# 2. Workers tokenize content → add integer tokens
# 3. Organizers run every 15 min → archive expired fragments by sector
# 4. System maintains fresh, organized knowledge base
```

## Query Integration

When a user queries the system:
1. **Domain Router** identifies query sector (ECO, GOV, HC, etc.)
2. **Fragment Retrieval** searches ONLY relevant sector fragments
3. **Confidence Scoring** weights recent fragments higher
4. **Answer Generation** uses freshest data from correct sector

Example:
```
Query: "What is Bitcoin price currently?"
→ Domain: ECO
→ Search: ECO sector fragments only
→ Filter: Exclude expired fragments (>6 hours old)
→ Result: "As of May 13, 2026, Bitcoin price is $67,842.50 USD"
→ Confidence: 78% (based on 3 fresh ECO fragments)
```

## Monitoring

Check sector distribution:
```sql
SELECT domain_sector, COUNT(*) as fragment_count
FROM wal_buffer
WHERE is_expired = 0
GROUP BY domain_sector;
```

Expected output:
```
ECO     | 2847
HC      | 1523
TECH    | 1891
NEWS    | 3204
GOV     | 892
GENERAL | 456
```

Check expiration queue:
```sql
SELECT domain_sector, COUNT(*) as expired_count
FROM wal_buffer
WHERE is_expired = 0 AND expiry_time < datetime('now')
GROUP BY domain_sector;
```

## Best Practices

1. **Set appropriate TTLs**: Match TTL to data volatility
   - Crypto/forex: 1-6 hours
   - News: 6-12 hours
   - Research papers: 24-48 hours
   - Policies/regulations: 72+ hours

2. **Monitor sector balance**: Ensure no single sector dominates
   - Adjust harvester distribution if needed
   - 800 harvesters should cover all sectors proportionally

3. **Archive regularly**: Run archival during sleep phase
   - Minimizes memory pressure
   - Keeps WAL buffer size manageable

4. **Sector-specific confidence thresholds**:
   - ECO: Require ≥3 fresh fragments (high volatility)
   - GOV: Require ≥2 fragments (stable but verify)
   - HC: Require ≥3 fragments (critical accuracy)

## Future Enhancements

- [ ] Cross-sector correlation detection
- [ ] Sector-specific compression algorithms
- [ ] Automated TTL adjustment based on data change rate
- [ ] Sector-aware query expansion
- [ ] Historical trend analysis per sector
