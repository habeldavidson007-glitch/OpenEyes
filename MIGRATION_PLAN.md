# OpenEyes Unified System Migration Plan

## Objective
Fully migrate from fragmented legacy modules to the unified system consisting of:
1. **Unified Knowledge Orchestrator** (`core/unified_orchestrator.py`)
2. **Knowledge Quality Assessor** (`core/quality_assessor.py`)

## Legacy Modules to Retire
- `knowledge/local_retrieval.py` (631 lines)
- `knowledge/live_fetch.py` (608 lines)
- `knowledge/fragment_orchestrator.py` (337 lines)
- `knowledge/graceful_degradation.py` (570 lines)
- `knowledge/retrieval.py` (113 lines)
- **Total: 2,259 lines of fragmented code**

## Migration Phases

### Phase 1: Core Integration (CURRENT)
- [x] Unified orchestrator created with cascading retrieval
- [x] Quality assessor implemented with credibility scoring
- [ ] Integrate into query_interface as primary retrieval layer
- [ ] Update client applications (cli.py, main_unified.py)

### Phase 2: Testing & Validation
- [ ] Migrate test suites to use unified orchestrator
- [ ] Run end-to-end tests across all domains
- [ ] Validate cross-domain fusion capabilities
- [ ] Verify adaptive confidence calibration

### Phase 3: Legacy Retirement
- [ ] Archive legacy modules
- [ ] Update documentation
- [ ] Final production cutover

## Implementation Steps

1. **Update Query Interface** - Replace swarm retrieval with unified orchestrator
2. **Update CLI** - Use new orchestrator interface
3. **Create Migration Tests** - Ensure backward compatibility
4. **Deploy Cross-Domain Fusion** - Enable multi-domain queries
5. **Enable Adaptive Confidence** - Activate ML-based calibration
6. **Archive Legacy Code** - Move to /archive/legacy/

## Success Criteria
- All existing tests pass with new system
- Cross-domain queries work seamlessly
- Confidence scores adapt based on feedback
- 75%+ reduction in code complexity
- Improved performance (lower latency)
