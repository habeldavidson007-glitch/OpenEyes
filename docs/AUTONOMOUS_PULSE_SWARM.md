# Autonomous Signal-Pulse Swarm

## Overview

The **Autonomous Signal-Pulse Swarm** is a bio-inspired, memory-efficient swarm architecture designed specifically for low-RAM systems (4GB laptops). It transforms OpenEyes from a reactive query-waiting system into a proactive, living data organism with a circadian rhythm.

## Key Features

### 🫀 Biological Circadian Rhythm
- **30-min wake-up** → **2-hour active harvest** → **sleep**
- Memory leak prevention through forced garbage collection
- Network ban avoidance via staggered agent activation

### ⚡ Zero Threading Overhead
- Uses **Asyncio Event Loop** as the "Signal Bus"
- Agents are registered callbacks waiting for signal flags
- State machine: `SLEEPING` → `TRIGGERED` → `HARVESTING` → `ARCHIVING` → `SLEEPING`

### 🎯 Staggered Pulse Activation
- Wakes **50 agents every 3 seconds** (not all 2,000 at once)
- Keeps CPU usage flat
- Prevents network spikes that look like DDoS attacks

### 💾 Write-Only WAL Buffer
- During active phase: agents write to temporary WAL buffer only
- No read contention on main database
- Flush to main DB during sleep phase

### 🔒 Token Bucket Rate Limiter
- Global limit: **Max 5 requests/second** across entire swarm
- Agents go back to sleep if bucket is empty
- Prevents rate-limiting bans from target websites

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CENTRAL SCHEDULER                        │
│                   (Global Clock / Heartbeat)                │
└───────────────┬─────────────────────────────────┬───────────┘
                │                                 │
        T+00:00 │                         T+02:00 │
     SIG_WAKE_UP                          SIG_HIBERNATE
                │                                 │
                ▼                                 ▼
    ┌───────────────────────┐         ┌───────────────────────┐
    │   STAGGERED WAKE-UP   │         │   FORCED SLEEP        │
    │  (50 agents / 3 sec)  │         │  - Drop connections   │
    │                       │         │  - GC sweep           │
    │                       │         │  - RAM → ~200MB       │
    └───────────┬───────────┘         └───────────────────────┘
                │
                ▼
    ┌───────────────────────┐
    │   ACTIVE HUNT         │
    │   T+00:05 - T+02:00   │
    │                       │
    │  Harvesters: Scan RSS │
    │  Workers: Tokenize    │
    │  Organizers: TF-IDF   │
    └───────────┬───────────┘
                │
                ▼
    ┌───────────────────────┐
    │   SLEEP PHASE         │
    │   T+02:00 - T+02:30   │
    │   - WAL flush to DB   │
    │   - Next cycle prep   │
    └───────────────────────┘
```

## Components

### Agent Types

| Type | Role | Wake Trigger |
|------|------|--------------|
| **HarvesterAgent** | Scans RSS feeds/APIs for new content hashes | SIG_WAKE_UP (staggered) |
| **WorkerAgent** | Converts text → Integer Tokens | SIG_PROCESS (from Harvester) |
| **OrganizerAgent** | Calculates TF-IDF, updates rules.py | Every 15 minutes |

### Signals

| Signal | Purpose | Fired By |
|--------|---------|----------|
| `SIG_WAKE_UP` | Start staggered agent activation | CentralScheduler |
| `SIG_PROCESS` | New data found, wake workers | HarvesterAgent |
| `SIG_ARCHIVE` | Run TF-IDF and rule updates | OrganizerAgent |
| `SIG_HIBERNATE` | Force sleep + GC sweep | CentralScheduler |

### Core Classes

```python
from openeyes.swarm import (
    # Configuration
    AgentConfig,          # Agent settings (ID, type, sources, priority)
    
    # Infrastructure
    SignalBus,            # Asyncio event loop for signal routing
    WALBuffer,            # Write-Ahead Log buffer
    TokenBucket,          # Global rate limiter (5 req/sec)
    
    # Agents
    BaseAgent,            # Abstract base with lazy loading
    HarvesterAgent,       # Content discovery
    WorkerAgent,          # Tokenization
    OrganizerAgent,       # TF-IDF and rules
    
    # Orchestration
    CentralScheduler,     # Manages wake-harvest-sleep cycles
    AutonomousSwarm       # Main entry point
)
```

## Usage

### Quick Demo

```python
import asyncio
from openeyes.swarm.autonomous_pulse_swarm import demo_swarm

# Run a shortened demo cycle (30 sec active, 10 sec sleep)
asyncio.run(demo_swarm())
```

### Production Deployment

```python
import asyncio
from openeyes.swarm import AutonomousSwarm, CentralScheduler
from datetime import timedelta

async def run_production_swarm():
    # Create swarm with 2000 agents (1000 harvesters, 800 workers, 200 organizers)
    swarm = AutonomousSwarm.create_default(
        num_harvesters=1000,
        num_workers=800,
        num_organizers=200
    )
    
    # Configure production timing (2hr active / 30min sleep)
    swarm.scheduler.active_duration = timedelta(minutes=120)
    swarm.scheduler.sleep_duration = timedelta(minutes=30)
    
    # Run continuously
    await swarm.start_continuous(num_cycles=-1)  # -1 = infinite

# Start the swarm
asyncio.run(run_production_swarm())
```

### Custom Agent Configuration

```python
from openeyes.swarm import (
    AgentConfig, HarvesterAgent, SignalBus, WALBuffer, TokenBucket
)

# Create custom harvester
config = AgentConfig(
    agent_id="crypto_harvester_1",
    agent_type="harvester",
    target_sources=[
        "https://feeds.example.com/crypto/rss",
        "https://api.example.com/blockchain/feed"
    ],
    wake_priority=5  # Lower = earlier in stagger queue
)

signal_bus = SignalBus()
known_hashes = set()

agent = HarvesterAgent(config, signal_bus, known_hashes)
```

## Memory Efficiency

### Sleeping State (Idle)
- **Memory per agent**: ~1KB (just function pointers)
- **2000 agents**: ~2MB total
- **System idle**: ~200MB with OS overhead

### Active State (Harvesting)
- **Memory per agent**: ~1MB (lazy-loaded logic modules)
- **Staggered activation**: Only 50 agents active at a time
- **Peak RAM**: ~50MB for agents + system overhead

### Comparison: Threaded vs Async Pulse

| Metric | Threaded Approach | Async Pulse Swarm |
|--------|------------------|-------------------|
| Idle RAM (2000 agents) | ~2GB | ~200MB |
| Context Switch Overhead | High (OS threads) | None (asyncio) |
| Network Spike Risk | All agents hit at once | Staggered pulses |
| GC Control | Unpredictable | Forced during sleep |

## Why This Beats "Waiting for Queries"

| Advantage | Reactive (Old) | Autonomous Pulse (New) |
|-----------|----------------|------------------------|
| **Latency** | Must scrape when queried | Answers pre-computed |
| **Data Freshness** | LLM training cutoff | Always ≤30 min old |
| **Hardware Safety** | Continuous load | 2hr ON / 30min OFF cooling |
| **RAM Usage** | Grows until crash | Capped by sleep GC |
| **Network Bans** | Looks like DDoS | Staggered, rate-limited |

## Configuration Options

### CentralScheduler Parameters

```python
scheduler = CentralScheduler(
    agents=agent_list,
    signal_bus=signal_bus,
    wal_buffer=wal_buffer,
    
    # Timing
    active_duration_minutes=120,      # 2 hours hunting
    sleep_duration_minutes=30,        # 30 min rest
    
    # Stagger configuration
    stagger_batch_size=50,            # Wake 50 at a time
    stagger_interval_seconds=3        # Wait 3 sec between batches
    
    # Results in: 2000 agents wake in ~2 minutes (not instantly)
)
```

### Token Bucket Tuning

```python
# Conservative (avoid any bans)
token_bucket = TokenBucket(capacity=3.0)  # 3 req/sec

# Aggressive (faster harvest, riskier)
token_bucket = TokenBucket(capacity=10.0)  # 10 req/sec

# Default (balanced)
token_bucket = TokenBucket(capacity=5.0)  # 5 req/sec
```

## Monitoring

### Get Swarm Status

```python
status = swarm.get_swarm_status()
print(f"Active agents: {status['active_agents']}")
print(f"Sleeping agents: {status['sleeping_agents']}")
print(f"Estimated RAM: {status['estimated_ram_mb']:.2f}MB")
print(f"Known content hashes: {status['known_hashes']}")
print(f"Next cycle: {status['next_cycle']}")
```

### Example Output

```json
{
  "running": true,
  "cycle_start": "2026-05-12T16:00:00",
  "active_agents": 150,
  "sleeping_agents": 1850,
  "known_hashes": 45230,
  "next_cycle": "2026-05-12T18:30:00",
  "total_agents": 2000,
  "agent_state_distribution": {
    "SLEEPING": 1850,
    "HARVESTING": 150
  },
  "estimated_ram_mb": 0.15
}
```

## Best Practices

### 1. Source Diversity
Don't point all harvesters at the same domain. Distribute across:
- RSS feeds
- Official APIs
- Government databases (.gov)
- Academic repositories (.edu)

### 2. Priority Assignment
Assign lower `wake_priority` to high-value sources:
```python
# Critical sources wake first
priority_0 = ["fed.gov", "cdc.gov", "sec.gov"]
# Secondary sources wake later
priority_5 = ["news-aggregator.com", "social-media.net"]
```

### 3. Hash Deduplication
Maintain global `known_hashes` set to prevent re-scraping:
```python
global_hashes = set()

# In harvester:
if content_hash not in global_hashes:
    global_hashes.add(content_hash)
    # Process new content
```

### 4. WAL Buffer Management
Flush WAL to main DB during sleep, then truncate:
```python
await wal_buffer.flush_to_main_db("knowledge_base.db")
# WAL automatically truncates after flush
```

## Troubleshooting

### Problem: Agents Not Waking
**Solution**: Check signal bus registration
```python
# Ensure listeners are registered before firing
signal_bus.register_listener(SignalType.SIG_WAKE_UP, agent.wake_up)
```

### Problem: Memory Not Releasing
**Solution**: Force explicit GC in hibernate
```python
import gc
gc.collect()  # Call in _forced_sleep phase
```

### Problem: Rate Limit Bans
**Solution**: Reduce token bucket capacity
```python
token_bucket = TokenBucket(capacity=2.0)  # Ultra-conservative
```

### Problem: WAL Buffer Growing Too Large
**Solution**: Reduce active phase duration or increase flush frequency
```python
scheduler.active_duration = timedelta(minutes=60)  # Shorter cycles
```

## Future Enhancements

- [ ] Adaptive stagger sizing based on system load
- [ ] Machine learning for optimal wake priorities
- [ ] Cross-agent communication for coordinated harvesting
- [ ] Real-time RAM monitoring with auto-throttling
- [ ] Distributed swarm across multiple machines

## License

Part of the OpenEyes project. See main LICENSE file.
