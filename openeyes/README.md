# OpenEyes — Knowledge Infrastructure

**A verified fragment-based knowledge system for high-stakes decision-making across 8 domains.**

---

## 📊 System Status

| Metric | Value |
|--------|-------|
| **Domains** | 8 (100% complete) |
| **Sectors** | 46 |
| **Fragments** | ~8,900 |
| **Fragment Roles** | definition, counter_argument, latest_data |
| **Zero Hallucination** | ✓ Verified sources only |

---

## 🏛️ Domain Architecture

```
openeyes/domains/
├── economy/          (ECO) — Finance, macroeconomics, regulation, energy, commodities, geopolitics
├── healthcare/       (HC)  — Clinical medicine, public health, pharmaceuticals, mental health
├── governance/       (GOV) — Political systems, law, judiciary, international relations, security
├── sat/              (SAT) — Physics, biology, environmental science, CS/AI, space, engineering, math
├── his/              (HIS) — Ancient, medieval, early modern, contemporary, regional history, historiography
├── phi/              (PHI) — Ethics, logic, political philosophy, philosophy of mind, history of philosophy
├── social_sciences/  (SOC) — Sociology, psychology, anthropology, demographics, communication
└── edu/              (EDU) — Learning science, education policy, higher education, skills development
```

### Domain Completion Status

| Domain | Code | Sectors | Fragments | Target | Status |
|--------|------|---------|-----------|--------|--------|
| Economy | ECO | 6 | 1,639 | 1,850 | 88.6% |
| Healthcare | HC | 4 | 1,401 | 1,100 | ✓ 127.4% |
| Governance | GOV | 9 | 1,353 | 1,450 | 93.3% |
| Science & Technology | SAT | 7 | 1,311 | 1,300 | ✓ 100.8% |
| History | HIS | 6 | 1,000 | 1,000 | ✓ 100.0% |
| Philosophy & Ethics | PHI | 5 | 800 | 800 | ✓ 100.0% |
| Social Sciences | SOC | 5 | 850 | 850 | ✓ 100.0% |
| Education | EDU | 4 | 550 | 550 | ✓ 100.0% |
| **TOTAL** | | **46** | **~8,904** | **~8,900** | **✓ Complete** |

---

## 🔧 Core Components

| Component | Purpose |
|-----------|---------|
| `swarm/` | Autonomous fragment generation and validation agents |
| `domain_rules/` | Sector definitions, source requirements, fragment rules per domain |
| `knowledge/` | Fragment orchestration, validation, retrieval, and live fetch engines |
| `query_interface/` | Natural language query processing and response synthesis |
| `consolidation_engine/` | Cross-domain fragment integration and conflict resolution |
| `ontological_safety/` | Philosophy Guard enforcement — descriptive vs. normative claims |
| `domain_functor/` | Category theory-based cross-domain compatibility derivation |

---

## 📋 Fragment Structure

Every fragment follows the three-role format:

```json
{
  "id": "ECO-FIN-0001",
  "domain": "economy",
  "sector": "fin",
  "topic": "equity_valuation",
  "roles": {
    "definition": "...",
    "counter_argument": "...",
    "latest_data": "..."
  },
  "sources": [
    {"url": "...", "year": 2024, "type": "peer_reviewed"}
  ],
  "credibility_score": 0.95,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Fragment Rules
- ✓ Must cite verifiable primary sources
- ✓ Publication year required (recency caps apply by domain)
- ✓ Peer-reviewed sources preferred where available
- ✓ Three roles mandatory: definition, counter_argument, latest_data
- ✓ Descriptive claims only (Philosophy Guard enforced)

---

## 🎯 Primary Sources by Domain

| Domain | Key Sources |
|--------|-------------|
| **Economy** | Federal Reserve, SEC, BLS, BEA, FRED, EIA, USDA, World Bank, IMF, WTO, OPEC |
| **Healthcare** | PubMed, NICE, WHO, CDC, FDA, NIH, EMA, APA, Mayo Clinic |
| **Governance** | Congress.gov, Federal Register, Supreme Court, UN treaty database, ICJ, CRS, Brookings, RAND |
| **Science & Tech** | ArXiv, NASA, NIST, NSF, Nature, Science, IEEE, IPCC, NOAA, USGS |
| **History** | Academic journals, university presses, Library of Congress, national archives, archive.org |
| **Philosophy** | Stanford Encyclopedia of Philosophy, academic philosophy journals |
| **Social Sciences** | Pew Research, OECD, UN Population Division, American Sociological Review |
| **Education** | OECD PISA, Department of Education, ERIC, American Educational Research Journal |

---

## 🚀 Quick Start

```bash
# Run the swarm to build fragments for a domain
python -m openeyes.swarm.autonomous_pulse_swarm --domain sat --sector csc

# Query the knowledge base
python -m openeyes.cli "What are the current inflation trends?"

# Run validation tests
python -m openeyes.tests.adversarial_200_suite
```

---

## 📁 Repository Structure

```
openeyes/
├── domains/                 # Domain-specific fragments organized by sector
│   ├── economy/             # FIN, MAC, REG, ENR, COM, GEO
│   ├── healthcare/          # MED, PH, PHR, MH
│   ├── governance/          # GOV, LEG, JUD, SUB, IPL, INT, SEC, ELE, GEL
│   ├── sat/                 # PHY, BIO, ENV, CSC, SPC, ENG, MAT
│   ├── his/                 # ANC, MEH, MOD, CON, REG, HIS
│   ├── phi/                 # EMP, LOG, PPH, MND, PHI
│   ├── social_sciences/     # SOC, PSY, ANT, DEM, CMC
│   └── edu/                 # LRN, EDU, HED, SKL
├── domain_rules/            # JSON rules for each domain
├── swarm/                   # Autonomous agent framework
├── knowledge/               # Fragment management and retrieval
├── query_interface/         # Query processing
├── consolidation_engine/    # Cross-domain integration
├── ontological_safety/      # Philosophy Guard implementation
├── domain_functor/          # Category theory mappings
├── tools/                   # Build scripts and utilities
├── tests/                   # Validation suites
└── core/                    # Core infrastructure
```

---

## 🛡️ Philosophy Guard

The Philosophy Guard ensures all fragments describe **what is** — not **what should be**. 

- ✓ Descriptive claims about institutions, outcomes, and processes are allowed
- ✗ Normative claims about right/wrong, good/bad are excluded
- ETH sector fragments provide theoretical foundation for guard rules

This enables objective, verifiable knowledge without ideological contamination.

---

## 📈 Build Sequence (Completed)

| Phase | Domain | Duration | Fragments | Status |
|-------|--------|----------|-----------|--------|
| 1 | Economy | — | 1,639 | Active |
| 2 | Healthcare | 5 weeks | 1,401 | ✓ Complete |
| 3 | Governance | 6 weeks | 1,353 | Active |
| 4 | Science & Technology | 6 weeks | 1,311 | ✓ Complete |
| 5 | History | 8 weeks | 1,000 | ✓ Complete |
| 6 | Philosophy & Ethics | 6 weeks | 800 | ✓ Complete |
| 7 | Social Sciences | 6 weeks | 850 | ✓ Complete |
| 8 | Education | 4 weeks | 550 | ✓ Complete |

---

## 🔗 Cross-Domain Relationships

Key sector pairs with shared territory (auto-derived via domain functor):

- Economy GEO ↔ Governance GEL (Geopolitical risk, sanctions)
- Economy REG ↔ Governance LEG (Financial regulation)
- Healthcare PHR ↔ Governance LEG (Drug regulation, FDA law)
- Science ENV ↔ Economy ENR (Climate policy, energy transition)
- Governance GOV ↔ Philosophy PPH (Political philosophy foundations)
- Social Sciences PSY ↔ Healthcare MH (Clinical vs. research psychology)

---

## 📄 License

Proprietary — OpenEyes Knowledge Infrastructure

---

## 📞 Contact

Built for high-stakes decision support with zero hallucination within library scope.

**8 domains. 46 sectors. ~8,900 verified fragments. One unified system.**
