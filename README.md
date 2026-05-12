# OpenEyes

> **Deterministic reasoning for high‑stakes questions.**  
> OpenEyes combines fragment-based logic, quasi-random exploration, and strict abstention rules to answer only when confidence is earned.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
[![NumPy](https://img.shields.io/badge/NumPy-Required-013243.svg)](#)
[![SciPy](https://img.shields.io/badge/SciPy-Required-8CAAE6.svg)](#)
[![Status](https://img.shields.io/badge/Mode-Safety%20First-success.svg)](#)

---

## Why OpenEyes?

Most systems are optimized to always respond. OpenEyes is optimized to **respond responsibly**.

- 🧠 **Brain vs. Muscle**: Python orchestrates reasoning; NumPy/SciPy performs the numerical evolution.
- 🛡️ **Safety-first abstention**: If evidence, provenance, or convergence is weak, OpenEyes returns `HALT_*` instead of hallucinating.
- 🎯 **Deterministic chaos**: Sobol + PCG + Box-Muller provide broad, reproducible exploration without naive randomness.
- 🧾 **Auditability built-in**: Every run can produce signed, canonical audit artifacts for traceability.
- 🔄 **Signal-Pulse Swarm**: Autonomous cyclic evidence circulation keeps fragments hydrated before queries arrive.

---

## Core Principles

1. **Determinism over drift** — reproducible seeds and replay metadata.
2. **Evidence over eloquence** — fragments, credibility, provenance.
3. **Abstain over bluff** — explicit HALT classes when confidence is insufficient.
4. **Structure over sprawl** — modular architecture and domain-aware thresholds.
5. **Hydration over real-time scraping** — evidence circulates autonomously so queries retrieve instantly.

---

## Architecture at a Glance

```text
openeyes/
├── cli.py                  # query/sleep/status/serve/pulse commands
├── config.py               # vault root + structured runtime paths
├── core/
│   ├── decomposition.py    # query decomposition
│   └── engine.py           # orchestration + answer/HALT flow
├── swarm/
│   ├── pulse_scheduler.py  # autonomous WAKE→HARVEST→PROCESS→ARCHIVE→HIBERNATE cycles
│   ├── harvesters.py       # dormant agents that collect evidence when triggered
│   └── processors.py       # validate and archive fragments with WAL buffering
├── monte_carlo/
│   ├── rng.py              # Sobol, PCG, Box-Muller
│   ├── evaluator.py        # dual-roll scoring
│   └── engine.py           # deterministic swarm evolution + abstention
├── knowledge/
│   ├── fragments.py        # fragment schema + provenance checks
│   └── hierarchies.py      # domain credibility hierarchy
├── fragment_library/       # persistent fragment storage (JSON files)
├── domains/rules.py        # domain-specific confidence thresholds
└── storage/
    ├── vault.py            # signed audit logs
    └── binary_lib.py       # binary persistence + vault cleanup
```

---

## Installation

### Recommended (Ubuntu/Debian with PEP 668)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

### Alternative: run without installing globally
```bash
python -m openeyes.cli --help
```

> If you see `externally-managed-environment`, do **not** use system `pip` for this project. Use a virtual environment as above.

---

## Quick Start

### 1) Ask a query
```bash
openeyes query "Pancreatic Cancer Symptoms" --domain medical
```

### 2) Run autonomous pulse loop (evidence circulation)
```bash
# Run 1 cycle with default timings (60s total)
openeyes pulse --cycles 1

# Run continuous loop (infinite cycles until Ctrl+C)
openeyes pulse --cycles -1

# Customize phase durations for testing
openeyes pulse --cycles 3 --cycle-duration 30 --harvest-duration 10 --process-duration 8 --archive-duration 5 --hibernation-duration 7
```

### 3) Trigger consolidation/cleanup
```bash
openeyes sleep
```

### 4) Check runtime status
```bash
openeyes status
```

### 5) API placeholder
```bash
openeyes serve --port 8080
```

---

## Signal-Pulse Swarm Architecture

The autonomous pulse loop transforms OpenEyes from query-triggered retrieval to continuously hydrated evidence circulation.

### Lifecycle Phases

1. **WAKE** — Staggered activation of agents (prevents CPU/network spikes)
2. **HARVEST** — Collect evidence from fragment directories and knowledge sources
3. **PROCESS** — Validate fragments, check quality scores, deduplicate
4. **ARCHIVE** — Persist fragments with WAL-friendly batched writes
5. **HIBERNATE** — Aggressive memory release, garbage collection, queue cleanup

### Agent Types

- **PulseScheduler**: Orchestrates cyclic operation and state transitions
- **Harvester Agents** (5): Scan filesystem and library for new evidence
- **Processor Agents** (2): Validate and convert evidence to fragments
- **Archiver Agent** (1): Persist fragments with buffered writes
- **Consolidator Agent** (1): Track fragment statistics and compatibilities

### Design Philosophy

- **Event-driven, not thread-spam**: Uses asyncio queues and lightweight signals
- **Dormant by default**: Agents activate only during their phase
- **Staggered activation**: Prevents resource contention on weak hardware (4GB RAM target)
- **Write-first architecture**: Append-oriented buffering for stable I/O
- **Mandatory hibernation**: Ensures long-running stability on low-resource machines

---

## Output Modes

OpenEyes may return:

- `ANSWER`
- `HALT_LOW_EVIDENCE`
- `HALT_PROVENANCE`
- `HALT_NO_COUNTERARG`
- `HALT_LOW_CONFIDENCE`
- `HALT_NON_CONVERGENCE`

This is intentional: **no unsafe confidence theater**.

---

## Vault & Audit Trail

OpenEyes writes runtime artifacts under:

- `OPENEYES_VAULT_ROOT` (default: `.openeyes/vault`)
- `audit/` for signed audit logs and latest snapshot behavior

This design keeps repo roots clean while preserving operational traceability.

---

## Testing

Run end-to-end validation:

```bash
pytest -q tests/test_e2e.py
```

Current tests validate:
- repeated medical query behavior
- deterministic seed stability
- audit file retention behavior

Test the pulse scheduler directly:

```bash
PYTHONPATH=/workspace python openeyes/swarm/pulse_scheduler.py
PYTHONPATH=/workspace python openeyes/swarm/harvesters.py
PYTHONPATH=/workspace python openeyes/swarm/processors.py
```

---

## Who is this for?

- Teams building **high-stakes assistants** (medical, legal, engineering)
- Researchers exploring **deterministic Monte Carlo reasoning**
- Builders who value **verifiability and abstention** over overconfident generation
- Operators needing **autonomous evidence hydration** on low-resource hardware

---

## Roadmap (Next Hardening)

- richer retrieval and evidence indexing
- stronger contradiction/counter-argument scoring
- calibration harness by domain/risk tier
- broader reproducibility and red-team safety suites
- adaptive pulse timing based on fragment growth rate

---

## License

MIT (see `LICENSE`).
