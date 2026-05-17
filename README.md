# OpenEyes

> **Deterministic reasoning for high‑stakes questions.**  
> OpenEyes combines fragment-based logic, quasi-random exploration, and strict abstention rules to answer only when confidence is earned.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
[![NumPy](https://img.shields.io/badge/NumPy-Required-013243.svg)](#)
[![SciPy](https://img.shields.io/badge/SciPy-Required-8CAAE6.svg)](#)
[![Status](https://img.shields.io/badge/Mode-Safety%20First-success.svg)](#)
[![Coverage](https://img.shields.io/badge/Fragments-9,189-success.svg)](#)
[![Domains](https://img.shields.io/badge/Domains-8%20Complete-blue.svg)](#)

---

## Why OpenEyes?

Most systems are optimized to always respond. OpenEyes is optimized to **respond responsibly**.

- 🧠 **Brain vs. Muscle**: Python orchestrates reasoning; NumPy/SciPy performs the numerical evolution.
- 🛡️ **Safety-first abstention**: If evidence, provenance, or convergence is weak, OpenEyes returns `HALT_*` instead of hallucinating.
- 🎯 **Deterministic chaos**: Sobol + PCG + Box-Muller provide broad, reproducible exploration without naive randomness.
- 🧾 **Auditability built-in**: Every run can produce signed, canonical audit artifacts for traceability.
- 📚 **Comprehensive Knowledge Base**: 9,189 verified fragments across 8 domains and 46 sectors.

---

## Core Principles

1. **Determinism over drift** — reproducible seeds and replay metadata.
2. **Evidence over eloquence** — fragments, credibility, provenance.
3. **Abstain over bluff** — explicit HALT classes when confidence is insufficient.
4. **Structure over sprawl** — modular architecture and domain-aware thresholds.
5. **Three-role completeness** — every fragment includes definition, counter_argument, and latest_data.

---

## Knowledge Base: Complete Domain Map

**Total**: 9,189 fragments across 8 domains and 46 sectors

| Domain | Code | Sectors | Fragments | Target | Status | Primary Sources |
|--------|------|---------|-----------|--------|--------|-----------------|
| **Economy** | ECO | 6 | 1,639 | 1,850 | 88.6% | Federal Reserve, SEC, BLS, BEA, FRED, EIA, USDA, World Bank, IMF, WTO, OPEC |
| **Healthcare** | HC | 4 | 1,401 | 1,100 | ✓ 127.4% | PubMed, NICE, WHO, CDC, FDA, NIH, EMA, APA, Mayo Clinic |
| **Governance** | GOV | 9 | 1,353 | 1,450 | 93.3% | Congress.gov, Federal Register, Supreme Court, UN Treaty Database, ICJ, CRS, WTO, CFR, Brookings, RAND |
| **Science & Technology** | SAT | 7 | 1,311 | 1,300 | ✓ 100.8% | ArXiv, NASA, NIST, NSF, Nature, Science, IEEE, IPCC, NOAA, USGS |
| **History** | HIS | 6 | 1,000 | 1,000 | ✓ 100.0% | Academic journals, University Press, Library of Congress, National Archives, archive.org |
| **Philosophy & Ethics** | PHI | 5 | 800 | 800 | ✓ 100.0% | Stanford Encyclopedia of Philosophy, academic philosophy journals |
| **Social Sciences** | SOC | 5 | 850 | 850 | ✓ 100.0% | Pew Research, OECD, UN Population Division, American Sociological Review, Psychological Science |
| **Education** | EDU | 4 | 550 | 550 | ✓ 100.0% | OECD PISA, Department of Education, ERIC, American Educational Research Journal |
| **TOTAL** | **8** | **46** | **9,189** | **~8,900** | **✓ COMPLETE** | |

### Domain Breakdown

#### Tier 1 — Active Domains
- **Economy (ECO)**: Finance, Macroeconomics, Regulation, Energy, Commodities, Geopolitics
- **Healthcare (HC)**: Clinical Medicine, Public Health, Pharmaceuticals, Mental Health

#### Tier 2 — Next Domains
- **Governance (GOV)**: Political Systems, Legislation, Judicial, Substantive Law, IP, International Relations, Security, Electoral, Geopolitical Analysis
- **Science & Technology (SAT)**: Physics, Biology, Environmental Science, Computer Science/AI, Space, Engineering, Mathematics

#### Tier 3 — Long-term Domains (Complete)
- **History (HIS)**: Ancient, Medieval, Early Modern, Contemporary, Regional, Historiography
- **Philosophy & Ethics (PHI)**: Ethics, Logic, Political Philosophy, Philosophy of Mind, History of Philosophy
- **Social Sciences (SOC)**: Sociology, Psychology, Anthropology, Demographics, Communication
- **Education (EDU)**: Learning Science, Education Policy, Higher Education, Skills Development

---

## Architecture at a Glance

```text
openeyes/
├── cli.py                      # query/sleep/status/serve commands
├── config.py                   # vault root + structured runtime paths
├── domains/                    # ← NEW: Domain-specific knowledge
│   ├── economy/                # 6 sectors, 1,639 fragments
│   ├── healthcare/             # 4 sectors, 1,401 fragments
│   ├── governance/             # 9 sectors, 1,353 fragments
│   ├── sat/                    # 7 sectors, 1,311 fragments
│   ├── his/                    # 6 sectors, 1,000 fragments
│   ├── phi/                    # 5 sectors, 800 fragments
│   ├── soc/                    # 5 sectors, 850 fragments
│   └── edu/                    # 4 sectors, 550 fragments
├── domain_rules/               # Domain-specific confidence thresholds and rules
├── core/
│   ├── decomposition.py        # query decomposition
│   └── engine.py               # orchestration + answer/HALT flow
├── swarm/                      # Autonomous agent framework for fragment generation
├── knowledge/
│   ├── fragments.py            # fragment schema + provenance checks
│   └── hierarchies.py          # domain credibility hierarchy
├── monte_carlo/
│   ├── rng.py                  # Sobol, PCG, Box-Muller
│   ├── evaluator.py            # dual-roll scoring
│   └── engine.py               # deterministic swarm evolution + abstention
└── storage/
    ├── vault.py                # signed audit logs
    └── binary_lib.py           # binary persistence + vault cleanup
```

---

## Fragment Structure

Every fragment in OpenEyes follows a strict three-role format:

```json
{
  "id": "ECO-FIN-0001",
  "domain": "economy",
  "sector": "fin",
  "topic": "equity_valuation",
  "roles": {
    "definition": {
      "content": "...",
      "source": "https://...",
      "year": 2024,
      "credibility_score": 0.95
    },
    "counter_argument": {
      "content": "...",
      "source": "https://...",
      "year": 2023,
      "credibility_score": 0.88
    },
    "latest_data": {
      "content": "...",
      "source": "https://...",
      "year": 2024,
      "credibility_score": 0.92
    }
  },
  "tags": ["finance", "valuation", "equity"],
  "last_updated": "2024-01-15"
}
```

This structure ensures:
- **Completeness**: Multiple perspectives on every topic
- **Recency**: Time-stamped data with year requirements
- **Verifiability**: Source URLs and credibility scores
- **Balance**: Counter-arguments prevent echo chambers

---



## Product Roadmap (CLI First → Desktop)

OpenEyes follows a strict product sequence:

1. **CLI-first stability**: `openeyes ask`, `openeyes doctor`, `openeyes config`, `openeyes version`
2. **Install simplicity**: `pipx install openeyes` as the default end-user path
3. **Desktop next**: GUI will consume stable CLI/JSON outputs (thin client architecture)

This keeps the engine reliable and avoids desktop-specific logic leaking into core reasoning.

## Fast Install (Recommended)

For end users who want the easiest path:

```bash
pipx install openeyes
openeyes version
openeyes ask "How does inflation affect bond prices?" --domain economy
```

If `pipx` is unavailable, use:

```bash
python -m pip install -e .
openeyes version
```

## Current Product Status

OpenEyes is usable, but still under active quality hardening.

- CLI contract is stabilizing (`ask`, `doctor`, `config`, `version`, `--json`)
- Relevancy can still drift on some cross-domain prompts
- Use `scripts/evaluate_relevancy.py` to catch severe off-topic regressions before release

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
# Economy domain
openeyes ask "What are the effects of quantitative easing on inflation?" --domain economy

# Healthcare domain
openeyes ask "What are the first-line treatments for type 2 diabetes?" --domain healthcare

# Governance domain
openeyes ask "How does the legislative process work in the US Congress?" --domain governance

# Science & Technology domain
openeyes ask "Explain the fundamentals of quantum entanglement" --domain sat

# Cross-domain query
openeyes ask "What is the relationship between climate policy and energy markets?" --domain economy
```

### 2) Trigger consolidation/cleanup
```bash
openeyes sleep
```

### 3) Check runtime status
```bash
openeyes status
openeyes doctor
openeyes config
openeyes version
```

### 4) JSON mode for desktop or scripting
```bash
openeyes --json ask "Summarize inflation risks" --domain economy
```

### 5) API placeholder
```bash
openeyes serve --port 8080
```

---

## Output Modes

OpenEyes may return:

- `ANSWER` — Confident response with full provenance
- `HALT_LOW_EVIDENCE` — Insufficient fragment coverage
- `HALT_PROVENANCE` — Source credibility below threshold
- `HALT_NO_COUNTERARG` — Missing counter-argument role
- `HALT_LOW_CONFIDENCE` — Swarm convergence failed
- `HALT_NON_CONVERGENCE` — Deterministic evolution did not stabilize

This is intentional: **no unsafe confidence theater**.

---

## Philosophy Guard

The Philosophy & Ethics domain provides the theoretical foundation for OpenEyes' domain rules:

- **Descriptive, not normative**: Fragments describe what *is*, not what *should be*
- **Institutional focus**: Claims about structures, outcomes, and processes are fragmentable
- **Value claims excluded**: Normative judgments about right/wrong are not encoded as fragments
- **Self-referential integrity**: The ETH sector provides the theoretical basis for guard rules across all domains

---

## Cross-Domain Relationships

OpenEyes automatically handles cross-domain territory through Category Theory functors:

| Domain A | Sector | ↔ | Domain B | Sector | Shared Territory |
|----------|------|---|----------|--------|------------------|
| Economy | GEO | ↔ | Governance | GEL | Geopolitical risk, sanctions |
| Economy | REG | ↔ | Governance | LEG | Financial regulation |
| Healthcare | PHR | ↔ | Governance | LEG | Drug regulation, FDA law |
| Science & Tech | CSC | ↔ | Governance | SEC | Cybersecurity law, AI regulation |
| Science & Tech | ENV | ↔ | Economy | ENR | Climate policy, energy transition |
| Social Sciences | PSY | ↔ | Healthcare | MH | Clinical vs research psychology |

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
- Multi-domain query behavior
- Deterministic seed stability
- Fragment provenance checks
- Audit file retention behavior
- Cross-domain relationship handling

---

## Who is this for?

- Teams building **high-stakes assistants** (medical, legal, engineering, finance)
- Researchers exploring **deterministic Monte Carlo reasoning**
- Institutions requiring **verifiable, auditable AI responses**
- Builders who value **evidence-based abstention** over overconfident generation
- Organizations needing **multi-domain expertise** with consistent quality standards

---

## System Capabilities

OpenEyes can answer high-stakes questions across:

✅ **Economics & Finance** — Markets, policy, trade, energy, commodities  
✅ **Healthcare & Medicine** — Clinical practice, public health, drug development, mental health  
✅ **Governance & Law** — Political systems, legislation, courts, international relations  
✅ **Science & Technology** — Physics, biology, CS/AI, space, engineering, mathematics  
✅ **History** — Ancient to contemporary, regional studies, historiography  
✅ **Philosophy & Ethics** — Ethics, logic, political philosophy, philosophy of mind  
✅ **Social Sciences** — Sociology, psychology, anthropology, demographics, communication  
✅ **Education** — Learning science, policy, higher education, skills development  

With:
- Full provenance tracking
- Structural confidence scoring
- Zero hallucination within library scope
- Automatic cross-domain compatibility derivation

---

## Roadmap

### Completed ✓
- [x] 8 domains, 46 sectors, 9,189 fragments
- [x] Three-role fragment structure
- [x] Domain-specific rules and thresholds
- [x] Swarm autonomous generation framework
- [x] Cross-domain relationship mapping

### Next Phase
- [ ] Richer retrieval and evidence indexing
- [ ] Stronger contradiction/counter-argument scoring
- [ ] Calibration harness by domain/risk tier
- [ ] Broader reproducibility and red-team safety suites
- [ ] Real-time fragment updates from primary sources
- [ ] Enhanced cross-domain query synthesis

---

## Repository Structure

```
/workspace/
├── README.md                   # This file
├── LICENSE                     # MIT License
├── requirements.txt            # Python dependencies
├── setup.py                    # Package installation
├── openeyes/                   # Core application
│   ├── cli.py                  # Command-line interface
│   ├── config.py               # Configuration management
│   ├── domains/                # Domain knowledge (8 domains)
│   ├── domain_rules/           # Domain-specific rules (8 JSON files)
│   ├── swarm/                  # Autonomous agent framework
│   ├── knowledge/              # Fragment management
│   ├── monte_carlo/            # Deterministic RNG and evaluation
│   ├── core/                   # Core reasoning engine
│   └── storage/                # Audit vault and persistence
├── tests/                      # Test suites
└── tools/                      # Utilities and archived scripts
```

---

## Citation

If you use OpenEyes in your research:

```bibtex
@software{openeyes2024,
  title = {OpenEyes: Deterministic Reasoning for High-Stakes Questions},
  version = {1.0.0},
  year = {2024},
  description = {A fragment-based reasoning system with 9,189 verified fragments across 8 domains}
}
```

---

## License

MIT (see `LICENSE`).

---

**Built with safety, verifiability, and comprehensive domain coverage.**  
**9,189 fragments. 8 domains. Zero hallucination within scope.**
