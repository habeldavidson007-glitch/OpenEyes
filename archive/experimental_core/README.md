# Experimental Core Modules - Archive

## Purpose

This directory contains experimental core modules that were **not integrated** into the main OpenEyes runtime pipeline as of May 2026.

These modules represent innovative features and advanced reasoning capabilities that were developed but never fully connected to the main engine. They are preserved here for:
- Future reference and inspiration
- Potential integration in later versions
- Research and development purposes
- Learning from architectural experiments

## Archived Modules

### ❌ Unused (Not Imported by Runtime)

| Module | Lines | Description | Integration Status |
|--------|-------|-------------|-------------------|
| `axioms.py` | 522 | Formal logic axioms and inference rules | Never integrated |
| `internal_consensus_engine.py` | 517 | Multi-agent consensus building | Never integrated |
| `cross_domain_mapper.py` | 470 | Cross-domain knowledge mapping | Never integrated |
| `iterative_refinement.py` | 468 | Iterative answer refinement loop | Never integrated |
| `streaming_orchestrator.py` | 320 | Streaming response orchestration | Never integrated |
| `bayesian_intent.py` | 312 | Bayesian query intent classification | Never integrated |
| `variational_optimizer.py` | 288 | Variational inference optimization | Never integrated |
| `concept_graph.py` | 234 | Concept graph construction | Never integrated |
| `reasoning_narrator.py` | 188 | Natural language reasoning explanations | Never integrated |

**Total:** 3,217 lines of unused code

### ✅ Restored to Active Core

These modules were temporarily archived but **restored** because they are required by the runtime:

| Module | Lines | Used By | Reason for Restore |
|--------|-------|---------|-------------------|
| `kap.py` | 353 | swarm, query_interface | Knowledge Acquisition Plan builder |
| `ekd.py` | 354 | query_interface | Episodic Knowledge Database store |
| `domain_validator.py` | 468 | router | Query domain validation |

**Total:** 1,175 lines restored

## Why Weren't These Integrated?

Common reasons for non-integration:

1. **Premature Optimization**: Built scalable architectures before data pipelines existed
2. **Complexity vs. Value**: Added significant complexity without proportional benefit
3. **Incomplete Testing**: Never reached test coverage thresholds for production
4. **Alternative Approaches**: Simpler solutions proved adequate for current needs
5. **Dependency Chains**: Required other unfinished modules to be useful

## How to Integrate a Module

If you want to integrate one of these modules:

1. **Identify the Value**: What specific problem does it solve?
2. **Check Dependencies**: Does it require other archived modules?
3. **Simplify**: Remove unnecessary abstractions and complexity
4. **Add Tests**: Achieve ≥80% test coverage
5. **Update Imports**: Add to appropriate `__init__.py` files
6. **Document**: Add docstrings explaining WHY, not just WHAT
7. **Performance Test**: Ensure no significant latency increase
8. **Move to Core**: Relocate to `/workspace/openeyes/core/`

## Recommended Integration Candidates

Based on potential value vs. complexity:

### High Priority
- **`reasoning_narrator.py`** (188 lines): Could improve user experience with natural language explanations
- **`bayesian_intent.py`** (312 lines): Could enhance query understanding accuracy

### Medium Priority
- **`iterative_refinement.py`** (468 lines): Could improve answer quality through refinement loops
- **`concept_graph.py`** (234 lines): Could enable better semantic reasoning

### Low Priority
- **`variational_optimizer.py`** (288 lines): Likely overkill for current use cases
- **`internal_consensus_engine.py`** (517 lines): Complex, unclear benefit over current approach

## Historical Context

**Date Archived:** May 12, 2026  
**Reason:** Code audit revealed 65.8% of `/core/` was dead code (never imported)  
**Action:** Moved to archive to reduce cognitive load and improve maintainability  
**Result:** Core reduced from 6,165 lines to 2,843 lines (53.4% reduction)

## Contact

For questions about these modules or integration proposals, refer to the main OpenEyes documentation at `/workspace/DEVELOPMENT.md`.

---

**Status:** 📦 ARCHIVED  
**Maintain:** Read-only (copy to core before modifying for integration)  
**Last Updated:** 2026-05-12
