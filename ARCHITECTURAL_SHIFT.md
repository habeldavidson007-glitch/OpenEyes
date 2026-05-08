# OpenEyes Architectural Shift: From Stateless Verifier to Stateful Learner

## Executive Summary

OpenEyes is undergoing a fundamental architectural transformation from a **Stateless Verifier** (calculates everything from scratch every time) to a **Stateful Learner** (accumulates wisdom into its structure). This shift enables the system to develop "instincts" through experience, mimicking how the human brain consolidates knowledge from deliberate thought to automatic behavior.

**Core Philosophy:** No LLM, no probabilistic models. Pure deterministic learning through structured knowledge evolution.

---

## The Neuroscience Inspiration

### Human Cognitive Architecture
1. **Prefrontal Cortex (PFC)**: Energy-expensive deliberation for novel situations
2. **Basal Ganglia**: Efficient habit/instinct execution for familiar patterns
3. **Hippocampus**: Short-term memory formation
4. **Sleep Consolidation**: Moves data from short-term to long-term, strengthens synaptic connections
5. **Reticular Activating System (RAS)**: Adaptive filtering based on learned importance

### OpenEyes Parallel
| Human Brain | OpenEyes Component | Function |
|-------------|-------------------|----------|
| Prefrontal Cortex | Monte Carlo Simulator | Deliberate verification for novel queries |
| Basal Ganglia | Compiled Synapses | Instant retrieval for familiar patterns |
| Hippocampus | Daily Query Logs | Short-term experience tracking |
| Sleep/Night Mode | Consolidation Engine | Long-term structure updates |
| RAS | Adaptive Semantic Index | Priority-based retrieval filtering |

---

## The Four-Phase Implementation Roadmap

### Phase 1: The "Sleep" Cycle (Night Mode & Consolidation) ✅ IMPLEMENTED

**Goal:** Build the foundation for experience-based learning.

**Components:**
- `ConsolidationEngine` (`/workspace/openeyes/night_mode/__init__.py`)
- Daily log analysis (success/halt patterns)
- Fragment performance tracking
- Knowledge gap identification
- Synapse proposal generation

**Key Functions:**
```python
from openeyes.night_mode import run_night_mode

# Runs consolidation for today's logs
run_night_mode()

# Or specify a date
run_night_mode("20250101")
```

**Outputs:**
- `night_report_YYYYMMDD_HHMMSS.json`: Comprehensive analysis with:
  - Fragment performance metrics (avg score, consistency, success count)
  - Knowledge gap reports (missing topics, roles, frequency)
  - Synapse proposals (high-success fragment chains for compilation)
  - Gene Pool weight update recommendations
  - Prioritized action list

**Neuroscience Parallel:** This is the "sleep" phase where the brain reviews the day's experiences, identifies patterns, and strengthens important neural pathways.

---

### Phase 2: The "Instinct" Layer (Logic Hardening) 🚧 NEXT

**Goal:** Compile frequently-verified logic chains into instant-retrieval Synapses.

**Concept:** When a fragment combination consistently survives Monte Carlo with high scores, it becomes a pre-compiled "Synapse" that bypasses simulation.

**Implementation Plan:**
1. Create `CompiledLogicIndex` class
2. Define Synapse structure:
   ```python
   {
       "synapse_id": "synapse_med_cancer_definition_counter_latest",
       "trigger_keywords": ["pancreatic", "cancer", "symptoms"],
       "fragment_chain": [
           "frag_onc_pancreatic_cancer_001",  # definition
           "frag_onc_pancreatic_cancer_002",  # counter_argument
           "frag_onc_pancreatic_cancer_003"   # latest_data
       ],
       "compiled_confidence": 0.89,
       "usage_count": 47,
       "last_verified": "2025-01-15"
   }
   ```
3. Modify assembly pipeline:
   - Check CompiledLogicIndex FIRST (instinct)
   - Fall back to Monte Carlo simulation if no synapse matches (deliberation)

**Benefit:** Common queries become 10-100x faster while maintaining verification integrity.

---

### Phase 3: The "RAS" Filter (Adaptive Retrieval) 🚧 PLANNED

**Goal:** Make the Semantic Index evolve based on usage patterns.

**Concept:** Fragments that frequently contribute to successful answers get higher retrieval priority. Fragments associated with HALTs get deprioritized.

**Implementation Plan:**
1. Add dynamic weight field to inverted index entries
2. Update weights nightly based on ConsolidationEngine reports:
   ```python
   new_priority = old_priority * 0.7 + performance_score * 0.3
   ```
3. Modify `search_by_semantic_index()` to sort by priority-weighted relevance

**Result:** The system "learns to pay attention" to what matters without external training.

---

### Phase 4: Ontological Safety (Structural Constraints) 🚧 PLANNED

**Goal:** Embed safety into the combinatorial logic of answer assembly.

**Concept:** Safety isn't a post-hoc filter—it's built into the Würfelspiel structure itself.

**Implementation Plan:**
1. Define answer templates per domain/stake-level:
   ```python
   MEDICAL_TIER1_TEMPLATE = {
       "position_1": {"role": "definition", "min_credibility": 80},
       "position_2": {"role": "evidence", "min_credibility": 85},
       "position_3": {"role": "counter_argument", "required": True},
       "position_4": {"role": "safety_warning", "auto_inject": True},
       "position_5": {"role": "latest_data", "max_age_years": 3}
   }
   ```
2. Modify Dice Table assembler to enforce template constraints
3. If template cannot be filled → HALT with specific missing-slot report

**Result:** Unsafe answers become structurally impossible to construct.

---

## The Evolution of Confidence Scoring

### Before (Random Monte Carlo)
```python
score = random.gauss(0, 15)  # Meaningless noise
```

### After (Deterministic Evidence-Based)
```python
# Credibility base score
base = CREDIBILITY_LOOKUP[fragment.credibility_class]  # peer_reviewed=95, guideline=90

# Recency decay
decay_rate = DOMAIN_DECAY[domain]  # medical=5pts/year, engineering=2pts/year
recency_bonus = max(0, 100 - (current_year - fragment.year) * decay_rate)

# Consistency bonus
if fragment.compatible_with in survivors:
    consistency_bonus = +10
if fragment.incompatible_with in survivors:
    consistency_penalty = -20

# Cross-source validation
source_count = count_unique_sources(survivors_with_similar_tags)
cross_source_bonus = min(10, (source_count - 1) * 3)

final_score = base * 0.5 + recency_bonus * 0.3 + consistency_bonus + cross_source_bonus
```

**Impact:** Scores now reflect actual evidence quality, not randomness.

---

## The HALT Message Evolution

### Before (Vague)
```
HALT: Insufficient confidence
```

### After (Structured Knowledge Gap Report)
```
HALT: Position 1 (definition) — no fragments found matching query
      Position 2 (evidence) — 3 candidates found, all failed Monte Carlo
        - frag_x: score 41, failed credibility (source: forum post, 2019)
        - frag_y: score 38, failed recency (7 years old, high-decay domain)
        - frag_z: score 55, failed consistency (conflicts with survivor frag_a)
      
      To answer this query, the library needs:
        - A definition fragment tagged [antibiotic, penicillin, allergy]
        - A peer_reviewed_study from 2022 or later
        - A counter_argument fragment addressing contraindications
      
      This gap has occurred 12 times in the last 30 days.
      Priority: CRITICAL
```

**Impact:** HALT messages become actionable intelligence for Night Mode.

---

## The Learning Loop

```
┌─────────────────────────────────────────────────────────────┐
│                    DAYTIME OPERATION                        │
│  Query → Retrieve → Monte Carlo → Verify → Answer/HALT     │
│  (Logs written to success_YYYYMMDD.jsonl / halt_*.jsonl)   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    NIGHT MODE (SLEEP)                       │
│  1. Load daily logs                                         │
│  2. Analyze fragment performance                            │
│  3. Identify knowledge gaps                                 │
│  4. Propose Synapses for Logic Hardening                    │
│  5. Calculate Gene Pool weight updates                      │
│  6. Generate night_report_*.json                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    STRUCTURAL UPDATES                       │
│  - Compile high-value Synapses → CompiledLogicIndex         │
│  - Update Semantic Index priorities                         │
│  - Adjust Gene Pool weights                                 │
│  - Refine Philosophy Guard rules                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
              (System wakes up smarter than yesterday)
```

---

## Key Differentiators vs. LLMs

| Feature | LLM/LBM | OpenEyes (New Architecture) |
|---------|---------|----------------------------|
| **Knowledge Source** | Probabilistic weights in neural net | Explicit, sourced fragments |
| **Verification** | None (trust the model) | Deterministic Monte Carlo + Philosophy Guard |
| **Learning** | Retraining/fine-tuning (expensive, opaque) | Structural evolution (transparent, auditable) |
| **Confidence** | Calibrated post-hoc (often wrong) | Computed from evidence hierarchy |
| **Safety** | Prompt engineering (brittle) | Structural constraints (unbreakable) |
| **Hallucination** | Possible (inherent to architecture) | Impossible (no generation, only retrieval) |
| **Audit Trail** | None (black box) | Complete chain: claim → fragment → source → score |
| **Improvement** | More data + compute | Better fragments + smarter consolidation |

---

## Success Metrics

### Short-Term (Phase 1-2)
- [ ] Night Mode generates actionable reports daily
- [ ] First Synapses compiled and tested
- [ ] Common queries show 50%+ latency reduction
- [ ] HALT messages include specific gap details

### Medium-Term (Phase 3)
- [ ] Semantic Index shows measurable priority evolution
- [ ] Recurring knowledge gaps decrease by 30% over 30 days
- [ ] Gene Pool weights stabilize around high-performing fragments

### Long-Term (Phase 4)
- [ ] Zero safety violations in high-stakes domains
- [ ] System can articulate why it halted with prescriptive recommendations
- [ ] Library grows autonomously via Night Mode prioritization

---

## Getting Started

### Run Night Mode Manually
```bash
cd /workspace
python -c "from openeyes.night_mode import run_night_mode; run_night_mode()"
```

### Integrate into Daily Pipeline
```python
# At end of daily operation
from openeyes.night_mode import ConsolidationEngine

engine = ConsolidationEngine()
engine.load_daily_logs()  # Loads today's logs
report = engine.generate_night_report()

# Review recommended actions
for action in report['recommended_actions']:
    print(f"[{action['priority']}] {action['action']}")
```

### Monitor System Evolution
```bash
# View latest night report
cat /workspace/logs/night_report_*.json | jq '.summary'

# Track knowledge gaps over time
cat /workspace/logs/night_report_*.json | jq '.knowledge_gaps[] | {topic: .topic_keywords, frequency: .frequency}'
```

---

## Philosophical Foundation

> **"Rules become Instincts through verified repetition."**

OpenEyes does not "learn" in the statistical sense (adjusting weights via gradient descent). It learns in the structural sense:
- Successful patterns are **compiled** into faster pathways
- Failed patterns are **analyzed** for gaps
- Safety constraints are **hardened** into unbreakable rules
- Knowledge evolves like science: established views challenged by counter-arguments, updated by latest data

This is **epistemological learning**, not statistical learning. The system becomes wiser, not just more accurate.

---

## Next Steps

1. **Immediate:** Test Night Mode with existing logs
2. **Week 1:** Implement Phase 2 (Logic Hardening / Synapse Compilation)
3. **Week 2-3:** Implement Phase 3 (Adaptive RAS Filtering)
4. **Week 4:** Implement Phase 4 (Ontological Safety Constraints)
5. **Ongoing:** Expand fragment library using Night Mode gap reports

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-15  
**Status:** Phase 1 Implemented, Phases 2-4 In Progress
