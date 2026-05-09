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

---

## Core Principles

1. **Determinism over drift** — reproducible seeds and replay metadata.
2. **Evidence over eloquence** — fragments, credibility, provenance.
3. **Abstain over bluff** — explicit HALT classes when confidence is insufficient.
4. **Structure over sprawl** — modular architecture and domain-aware thresholds.

---

## Architecture at a Glance

```text
openeyes/
├── cli.py                  # query/sleep/status/serve commands
├── config.py               # vault root + structured runtime paths
├── core/
│   ├── decomposition.py    # query decomposition
│   └── engine.py           # orchestration + answer/HALT flow
├── monte_carlo/
│   ├── rng.py              # Sobol, PCG, Box-Muller
│   ├── evaluator.py        # dual-roll scoring
│   └── engine.py           # deterministic swarm evolution + abstention
├── knowledge/
│   ├── fragments.py        # fragment schema + provenance checks
│   └── hierarchies.py      # domain credibility hierarchy
├── domains/rules.py        # domain-specific confidence thresholds
└── storage/
    ├── vault.py            # signed audit logs
    └── binary_lib.py       # binary persistence + vault cleanup
```

---

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

---

## Quick Start

### 1) Ask a query
```bash
openeyes query "Pancreatic Cancer Symptoms" --domain medical
```

### 2) Trigger consolidation/cleanup
```bash
openeyes sleep
```

### 3) Check runtime status
```bash
openeyes status
```

### 4) API placeholder
```bash
openeyes serve --port 8080
```

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

---

## Who is this for?

- Teams building **high-stakes assistants** (medical, legal, engineering)
- Researchers exploring **deterministic Monte Carlo reasoning**
- Builders who value **verifiability and abstention** over overconfident generation

---

## Roadmap (Next Hardening)

- richer retrieval and evidence indexing
- stronger contradiction/counter-argument scoring
- calibration harness by domain/risk tier
- broader reproducibility and red-team safety suites

---

## License

MIT (see `LICENSE`).
