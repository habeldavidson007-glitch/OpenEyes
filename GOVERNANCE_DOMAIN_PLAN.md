# GOVERNANCE DOMAIN EXPANSION PLAN

## Executive Summary
Adding **GOVERNANCE** as the third Tier 1 domain (alongside Healthcare and Economy) creates a powerful "triad of societal infrastructure" that enables cross-domain reasoning about how societies function.

## Domain Architecture

### Hierarchy Structure
```
ROOT: openeyes/
├── domains/
│   ├── eco/ (Economy - Existing)
│   ├── hc/  (Healthcare - Existing)
│   └── gov/ (Governance - NEW)
│       ├── gov/     → Political Systems & Institutions (200 frags)
│       ├── leg/     → Legislation & Policy Process (150 frags)
│       ├── jud/     → Judicial Systems & Legal Process (150 frags)
│       ├── sub/     → Substantive Law (250 frags)
│       ├── ipl/     → Intellectual Property (100 frags)
│       ├── int/     → International Relations & Law (200 frags)
│       ├── sec/     → Security & Conflict (150 frags)
│       ├── ele/     → Electoral Systems & Democracy (100 frags)
│       └── gel/     → Geopolitical Analysis (150 frags)
└── total: 1,450 fragments
```

### Fragment Naming Convention
Following the established pattern: `frag_gov_{sector}_{topic}_{role}_{num}.json`

Examples:
- `frag_gov_gov_federalism_descriptive_001.json`
- `frag_gov_leg_rulemaking_procedural_045.json`
- `frag_gov_jud_civilprocedure_explanatory_012.json`
- `frag_gov_sub_contractlaw_definitional_089.json`
- `frag_gov_ipl_patents_instructional_003.json`
- `frag_gov_int_treatylaw_analytical_067.json`
- `frag_gov_sec_cybersecurity_descriptive_024.json`
- `frag_gov_ele_votingsystems_comparative_008.json`
- `frag_gov_gel_alliances_strategic_031.json`

## Source Evaluation

### Proposed Primary Sources ✅

#### 1. **Archive.org (Internet Archive)**
**Verdict: EXCELLENT ADDITION**

**Strengths:**
- Historical legislative texts, defunct government websites
- Captured congressional hearings, policy drafts over time
- Wayback Machine provides temporal context for policy evolution
- Out-of-print CRS reports, historical legal documents
- Neutral archival mission aligns with "describe what is" philosophy

**Use Cases:**
- Track evolution of electoral laws (1990s→present)
- Recover superseded regulations for historical context
- Access defunct agency guidance documents
- Preserve institutional memory of governance changes

**Integration Strategy:**
- Use as secondary verification for historical claims
- Timestamp all archive.org citations with capture dates
- Cross-reference with current official sources

#### 2. **World Bank Worldwide Governance Indicators (WGI)**
**Verdict: CRITICAL QUANTITATIVE SOURCE**

**Strengths:**
- 6 composite indicators covering 200+ countries (1996-present):
  1. Voice & Accountability
  2. Political Stability & Absence of Violence
  3. Government Effectiveness
  4. Regulatory Quality
  5. Rule of Law
  6. Control of Corruption
- Rigorous methodology, peer-reviewed
- Enables cross-national comparative analysis
- Time-series data for trend analysis
- Completely descriptive (no normative claims)

**Use Cases:**
- Quantify "rule of law" differences between nations
- Track corruption perception trends
- Compare regulatory quality across jurisdictions
- Validate qualitative claims with empirical data

**Integration Strategy:**
- Create quantitative fragments with specific WGI scores
- Include methodology notes in fragment metadata
- Link to underlying source datasets
- Use for comparative politics fragments (GOV sector)

### Recommended Additional Sources

#### Official Government Sources (Primary Authority)
| Source | Sector | Content Type |
|--------|--------|--------------|
| Congress.gov | LEG | Bills, statutes, committee reports, hearings |
| Federal Register | LEG | Proposed/final rules, notices, executive orders |
| SupremeCourt.gov | JUD | Opinions, briefs, orders, argument transcripts |
| USCode.house.gov | SUB | Codified federal law |
| State.gov | INT | Treaties, diplomatic cables (FOIA), country reports |
| Defense.gov | SEC | Defense strategy docs, budget justifications |
| EAC.gov | ELE | Election administration data, voting system standards |

#### International Organizations
| Source | Sector | Content Type |
|--------|--------|--------------|
| UN Treaty Collection | INT | Registered treaties, status tracking |
| ICJ-CIJ.org | INT | Court judgments, advisory opinions |
| WTO.org | INT/LEG | Trade agreements, dispute settlements |
| IPU.org | ELE | Parliamentary data, electoral statistics |
| FreedomHouse.org | GOV/ELE | Freedom indices (descriptive metrics) |

#### Think Tanks & Research Institutions
| Source | Sector | Notes |
|--------|--------|-------|
| CRS Reports (via EveryCRSReport.com) | ALL | Non-partisan congressional research |
| RAND Corporation | SEC/INT | Defense policy, conflict analysis |
| Brookings Institution | GOV/LEG | Policy analysis, governance studies |
| CFR.org | INT/SEC | Council on Foreign Relations analysis |
| Brennan Center | ELE | Voting rights, campaign finance data |

## Philosophy Guard Implementation

### The "Is vs. Ought" Test
Every fragment must pass this validation:

**✅ ACCEPTABLE (Descriptive):**
- "The US Senate requires 60 votes to invoke cloture on most legislation"
- "Countries with proportional representation systems have higher party fragmentation"
- "The Supreme Court applied strict scrutiny in Regents v. Bakke (1978)"
- "WGI Rule of Law scores range from -2.5 to +2.5; Denmark scored 2.14 in 2022"

**❌ REJECTED (Normative):**
- "The filibuster should be abolished" → Reformulate: "Critics argue the filibuster impedes legislative efficiency; proponents claim it protects minority interests"
- "Proportional representation is better than first-past-the-post" → Reformulate: "PR systems produce more coalition governments; FPTP systems tend toward two-party dominance"
- "The Court was wrong to decide Citizens United this way" → Reformulate: "The decision held that political spending is protected speech under the First Amendment; dissenting justices argued it would increase corporate influence"

### Validation Checklist for Fragment Authors
```markdown
- [ ] Does this describe an existing institution, process, or outcome?
- [ ] Can this be verified against primary sources?
- [ ] Would reasonable observers across the political spectrum agree this is factually accurate?
- [ ] Am I using verbs like "is," "requires," "prohibits," "established" rather than "should," "ought," "must"?
- [ ] If discussing debates, do I present multiple positions descriptively?
- [ ] Are all quantitative claims sourced and dated?
```

## Cross-Domain Synergies

### Economy ↔ Governance Connections
- **REG (Economy) + LEG (Gov)**: How administrative rulemaking affects business regulation
- **MAC (Economy) + GOV (Gov)**: Central bank independence as political institution
- **FIN (Economy) + SUB (Gov)**: Contract law enforcement in financial markets

### Healthcare ↔ Governance Connections
- **PHR (HC) + LEG (Gov)**: ACA legislative history, Medicaid expansion legal challenges
- **MED (HC) + JUD (Gov)**: Medical malpractice litigation, informed consent case law
- **MH (HC) + SUB (Gov)**: Mental health commitment procedures, disability rights law

### Three-Way Intersections
- **IP (Economy) + IPL (Gov) + MED (HC)**: Pharmaceutical patent law, drug pricing policy
- **Labor (Economy) + SUB (Gov) + PHR (HC)**: Occupational safety regulations, workers' compensation
- **Trade (Economy) + INT (Gov) + PHR (HC)**: TRIPS agreement, vaccine distribution treaties

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Create directory structure
- [ ] Develop fragment templates for each sector
- [ ] Write 50 seed fragments (high-priority topics)
- [ ] Integrate WGI data pipeline
- [ ] Set up archive.org API access

### Phase 2: Core Build (Weeks 3-6)
- [ ] Generate 800 fragments from primary sources
- [ ] Implement cross-referencing with economy/healthcare
- [ ] Build sector-specific entity recognizers
- [ ] Create comparative politics dataset

### Phase 3: Expansion (Weeks 7-10)
- [ ] Complete remaining 600 fragments
- [ ] Add historical depth via archive.org
- [ ] Integrate international law databases
- [ ] Build geopolitical scenario models

### Phase 4: Integration Testing (Weeks 11-12)
- [ ] 100-query test suite (governance-only)
- [ ] 200-query cross-domain test suite
- [ ] Safety halt calibration for political content
- [ ] Bias detection and mitigation

## Risk Mitigation

### Potential Issues & Solutions

| Risk | Mitigation |
|------|------------|
| **Perceived Political Bias** | Strict adherence to descriptive claims; cite multiple sources representing different perspectives |
| **Rapidly Changing Information** | Version fragments with timestamps; flag time-sensitive content |
| **International Law Complexity** | Distinguish between treaty obligations, customary law, and soft law |
| **Data Gaps in Authoritarian Regimes** | Acknowledge limitations; use multiple democracy indices for triangulation |
| **Controversial Topics** | Present competing claims descriptively; avoid resolution claims |

## Success Metrics

### Quantity Targets
- 1,450 fragments across 9 sectors
- Average 15-20 citations per fragment
- 100% coverage of core topics per sector description

### Quality Targets
- 0 normative claims detected in QA review
- 95%+ inter-rater reliability on "descriptive vs. normative" classification
- All fragments pass source verification
- Cross-domain linkages established for 40%+ of fragments

### Performance Targets
- Query response time <500ms for governance questions
- 85%+ success rate on 100-query test suite
- Confidence scores calibrated to accuracy rates

## Conclusion

**Archive.org and World Bank WGI are exceptional additions** that bring:
1. **Historical depth** (archive.org) - temporal dimension missing from current domains
2. **Quantitative rigor** (WGI) - empirical grounding for comparative claims

These sources perfectly complement the existing primary sources and align with the philosophical guardrails. The governance domain will complete the "societal infrastructure triad" and enable OpenEyes to answer complex questions about how power, resources, and health intersect in modern societies.

**Recommendation: PROCEED WITH GOVERNANCE DOMAIN** using the architecture and sources outlined above.
