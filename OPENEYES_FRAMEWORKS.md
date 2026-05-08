# OpenEyes — Mathematical Frameworks & Implementation Plan

> **Status**: Theoretical → Engineering Translation in Progress  
> **Taxonomy**: Verified Combinatorial Inference System (VCIS)  
> **Core Principle**: Intelligence emerges from composition, not scale.

---

## Part I — What OpenEyes Is (And Isn't)

### Not an LLM

OpenEyes does not belong in the LLM family tree. It has:
- **No weights** to train
- **No token prediction**
- **No neural components**
- **No probabilistic generation**

### Four Defining Properties

1. **Knowledge is separable from reasoning**  
   Fragment library (what it knows) is physically separate from evaluation engines (how it reasons).

2. **Confidence is computable, not emergent**  
   Every digit in the confidence score traces to: credibility class + recency decay + cross-source consistency + reasoning chain completeness.

3. **The system can prove its silence**  
   When OpenEyes halts, it specifies exactly what fragment types, reasoning roles, and credibility classes are missing.

4. **Intelligence emerges from composition**  
   A library of 100 perfectly curated fragments in a narrow domain outperforms a million random fragments.

### Competitive Position

| Domain | OpenEyes | LLM |
|--------|----------|-----|
| High-stakes narrow domains | ✅ Proven robust, citable, auditable | ❌ Variable accuracy, no verifiability |
| Consistency under rephrasing | ✅ Identical answers for equivalent queries | ❌ Sensitive to word order |
| Auditability | ✅ Full reasoning chain logged | ❌ Black box |
| Adversarial resistance | ✅ Structurally impossible to jailbreak | ❌ Prompt injection vulnerable |
| Hallucination | ✅ Architectural impossibility within scope | ❌ Inherent risk |
| Breadth | ❌ Limited to fragment library | ✅ Entire internet training data |
| Open-ended conversation | ❌ Requires fragments | ✅ Handles ambiguity well |

**Framing**: OpenEyes is a scalpel. LLMs are Swiss Army knives. In domains where precision matters, you reach for the scalpel.

---

## Part II — Mathematical Frameworks Priority Queue

### Priority 1: Group Theory — Query Normalization ✅ IMPLEMENTED

**Problem**: Same question phrased differently produces different retrieval paths and potentially different answers.

**Solution**: Define a Query Normalization Group — meaning-preserving transformations that reduce queries to canonical form.

**Implementation**: `/workspace/openeyes/query_normalizer/__init__.py`

```python
# Meaning-preserving transformations:
# - Active ↔ Passive voice
# - Subject-object swaps  
# - Synonym substitution (UTI ↔ urinary tract infection)
# - Clause reordering
# - Question form normalization

canonical_form("What antibiotic for penicillin-allergic UTI?") 
== canonical_form("For UTI patients allergic to penicillin, which antibiotic?")
```

**Benefits**:
- Fixes inconsistent answers across rephrased queries
- Multiplies Synapse coverage exponentially (one simulation covers entire equivalence class)
- Enables perfect Instinct Mode matching

**Status**: ✅ Complete and tested

---

### Priority 2: Combinatorial Game Theory — Grundy Values

**Problem**: Monte Carlo evaluates fragments statistically, but "is this fragment challenged by a stronger counter-argument?" is a game theory question.

**Solution**: Model fragment validation as a two-player game (Anchor vs Challenger). Compute Sprague-Grundy values at index-time.

**Implementation Target**: `shared_core/monte_carlo_engine.py`

```python
def compute_grundy_value(fragment, challenger_pool, domain_rules):
    """
    Grundy = 0: No challenger can defeat it (PROVEN_ROBUST)
    Grundy > 0: Can be challenged (CHALLENGED, include with caution note)
    """
    defeats = []
    for challenger in challenger_pool:
        if challenger_defeats_anchor(challenger, fragment, domain_rules):
            defeats.append(compute_grundy_value(challenger, challenger_pool, domain_rules))
    
    mex = 0
    while mex in defeats:
        mex += 1
    return mex
```

**Benefits**:
- Creates a new confidence class: "Undefeatable within library scope"
- Pre-computed at index-time → instant lookup during queries
- Formal property, not statistical estimate

**Next Steps**: Implement `compute_grundy_value()`, add pre-computation to library loading, store Grundy values in fragment JSON.

---

### Priority 3: Cellular Automata — Fragment Interaction

**Problem**: Fragments evaluated in isolation, but knowledge is contextual. A contraindication fragment means something different when adjacent to a treatment fragment vs. a pregnancy fragment.

**Solution**: Run Cellular Automata generations on fragment assemblies before final output. Local interaction rules produce global behavior.

**Implementation Target**: `openeyes/dice_table/__init__.py` → `_sequence_fragments()`

```python
# Local interaction rules:
Rule A (Activation): [contraindication] adjacent to [treatment] → double weight
Rule B (Suppression): Two [first_line] fragments overlap → suppress lower-scoring one
Rule C (Amplification): [latest_data] + [definition] same topic → +10 consistency bonus
Rule D (Incompatibility): A lists B as incompatible → eject B regardless of score

# Run N generations, assembly = survivors
```

**Benefits**:
- Makes Würfelspiel genuinely combinatorial
- Same fragments produce different assemblies based on context
- Emergent reasoning from simple local rules

**Next Steps**: Replace static priority sort with CA evolution loop in `_sequence_fragments()`.

---

### Priority 4: Formal Concept Analysis — Auto-Compatibility

**Problem**: `compatible_with` and `incompatible_with` manually specified. Impossible to maintain at scale (thousands of fragments).

**Solution**: Use FCA lattice theory to automatically derive compatibility from tag structure.

**Implementation Target**: `openeyes/fragment_library/__init__.py`

```python
from concepts import Context  # pip install concepts

def build_concept_lattice(fragment_library):
    """
    Objects = fragment IDs, Attributes = all tags
    Returns: lattice of (fragment_set, shared_tags) pairs
    """
    objects = list(fragment_library._fragments.keys())
    attributes = list(fragment_library._tag_index.keys())
    
    table = [[tag in frag.tags for tag in attributes] 
             for frag in fragment_library._fragments.values()]
    
    ctx = Context(objects, attributes, table)
    return ctx.lattice

def derive_compatibility(lattice, fragment_id):
    """
    Fragments in same/sub-concepts → compatible
    Fragments in disjoint concepts → incompatible
    """
    ...
```

**Benefits**:
- Solves manual maintenance at scale
- Auto-populates `compatible_with` / `incompatible_with`
- New fragments immediately placed in relationship context

**Next Steps**: Add `rebuild_concept_lattice()` called after every `add_fragment()`, store in `concept_lattice.json`.

---

### Priority 5: Category Theory — Cross-Domain Transfer

**Problem**: Each domain (medical, engineering, cooking) built independently. No formal mechanism for applying knowledge structure across domains.

**Solution**: Define domain functors that map relationship structures between categories.

**Implementation Target**: New module `openeyes/domain_transfer/__init__.py` (6-12 months out)

```python
# Medical Category → Legal Category via Functor F:
F(clinical_guideline)     = statutory_law
F(peer_reviewed_study)    = case_precedent  
F(contraindication)       = legal_prohibition
F(dosage_threshold)       = sentencing_guideline
F(counter_argument)       = dissenting_opinion
F(latest_data)            = recent_amendment

# Transfer architecture of relationships, not content
```

**Benefits**:
- Domain transfer without training
- Clone relationship structure, populate new fragments
- Exponential acceleration of new domain onboarding

**Prerequisites**: At least two deeply-built domains (medical + engineering) to define concrete functor.

---

## Part III — Unified Architecture (Post-Implementation)

```
User submits query
        │
        ▼
[Query Normalizer] — Group Theory ✅
  Compute canonical form
  Check Synapse index (Instinct Mode if hit)
        │
        ▼
[Swarm] — Semantic Index (FCA-derived compatibility)
  Anchor Agent: highest credibility fragment
  Challenger Agent: counter_argument fragments  
  Recency Agent: latest_data fragments
  Compatibility Agent: FCA lattice traversal
        │
        ▼
[Monte Carlo] — Deterministic evaluator + CGT Grundy lookup
  Credibility scoring
  Recency decay (domain-specific)
  Cross-source consistency
  Grundy value: PROVEN_ROBUST vs CHALLENGED
        │
        ▼
[Ontological Safety] — Structural constraint check
  If safety fragments missing → HALT (answer cannot be constructed)
        │
        ▼
[RAS Filter] — Co-occurrence weights
  Adjust scores by historical success patterns
        │
        ▼
[Würfelspiel / CA Assembly] — Cellular Automata
  Run N generations of local interaction rules
  Fragment set that survives = final assembly
  Fixed positions: definition → evidence → counter → latest → constraint
        │
        ▼
[Philosophy Guard] — Domain rules veto
        │
        ▼
[Compiled Logic Index] — Logic Hardening
  If confidence ≥ 70% AND Grundy = 0 → compile to Synapse
        │
        ▼
Output: Verified answer with full reasoning chain
        + Fragment IDs, scores, sources, Grundy values, CA generation count
        + Canonical form match (for audit trail)
```

---

## Part IV — Implementation Status

| Priority | Framework | Status | Location |
|----------|-----------|--------|----------|
| 1 | Group Theory — Query Normalizer | ✅ Complete | `openeyes/query_normalizer/` |
| 2 | CGT — Grundy Values | 🔄 Next | `shared_core/monte_carlo_engine.py` |
| 3 | CA — Fragment Interaction | ⏳ Pending | `openeyes/dice_table/` |
| 4 | FCA — Auto-Compatibility | ⏳ Pending | `openeyes/fragment_library/` |
| 5 | Category Theory — Domain Transfer | 🔮 Long-term | New module |

---

## Part V — Pioneer Position

OpenEyes arrived at Neuro-Symbolic AI from a different direction than academic research:
- Academic systems hybridize neural networks with formal reasoning
- OpenEyes removes the neural component entirely
- Replaces it with mathematically governed combinatorial engine
- Learns through evolutionary weight adjustment, not backpropagation

**Unique Combination** (no prior art):
- Musikalisches Würfelspiel as knowledge assembly mechanism
- Monte Carlo as statistical verifier (not generator)
- Swarm decomposition as query-to-knowledge mapping
- Evolutionary gene pool as learning mechanism
- E+ as formal foundation language

**Compound Advantage**: E-AR improves E+, OpenEyes uses E+ as foundation. Second-order advantage no replication effort can shortcut.

---

*Living specification — updated as frameworks move from theory to implementation.*  
*Last updated: 2026-05-08 (Priority 1 Complete)*
