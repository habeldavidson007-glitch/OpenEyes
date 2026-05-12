# OpenEyes Development Guide

## Quick Start

### Installation
```bash
pip install -r requirements.txt
pip install -e .  # Install in development mode
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=openeyes --cov-report=term-missing

# Run specific test categories
pytest tests/unit/ -v          # Unit tests only
pytest tests/integration/ -v   # Integration tests only
pytest tests/test_e2e.py -v    # End-to-end tests only
```

### Code Quality
```bash
# Linting
flake8 openeyes/ tests/

# Format checking
black --check openeyes/ tests/
isort --check-only openeyes/ tests/

# Auto-format
black openeyes/ tests/
isort openeyes/ tests/
```

## Project Structure

```
openeyes/
├── core/                    # Core reasoning engine components
│   ├── engine.py           # Main OpenEyes engine
│   ├── reasoning_engine.py # Reasoning logic
│   ├── intent_router.py    # Query intent routing
│   └── ...
├── knowledge/              # Knowledge management
│   ├── fragments.py        # Fragment handling
│   ├── retrieval.py        # Knowledge retrieval
│   └── live_fetch.py       # Live web fetching
├── storage/                # Storage layer
│   ├── vault.py            # Audit logging
│   └── memory.py           # Memory management
├── monte_carlo/            # Monte Carlo evaluation
├── ingestion/              # Data ingestion
└── tools/                  # Supporting tools

tests/
├── unit/                   # Unit tests
│   ├── test_monte_carlo.py
│   ├── test_vault.py
│   └── test_philosophy_guard.py
├── integration/            # Integration tests
│   └── test_engine_domains.py
└── test_e2e.py            # End-to-end tests

archive/                    # Archived standalone scripts
├── ipl_generators/        # Historical fragment generators
├── build_scripts/         # One-time migration scripts
├── test_scripts/          # Manual test runners
└── utilities/             # Operational utilities
```

## Test Coverage

Current coverage: **~26%** (as of latest run)

### Key Covered Areas
- ✅ Monte Carlo engine (87% covered)
- ✅ Storage vault (100% covered)
- ✅ Philosophy Guard validation
- ✅ Engine domain integration tests
- ✅ End-to-end workflows

### Areas Needing Coverage
- ❌ Query interface (9% covered)
- ❌ Swarm intelligence (21% covered)
- ❌ Language synthesizer (0% covered)
- ❌ Ontological safety (0% covered)
- ❌ Streaming orchestrator (0% covered)

## CI/CD Pipeline

GitHub Actions workflow configured in `.github/workflows/ci.yml`:
- Runs on push to main/master and pull requests
- Tests Python 3.9, 3.10, 3.11
- Runs pytest with coverage
- Performs linting checks (flake8, black, isort)

## Architecture Overview

### Core Pipeline Flow
1. **Query Input** → `cli.py` or API
2. **Intent Routing** → `core/intent_router.py`
3. **Domain Validation** → `core/domain_validator.py`
4. **Knowledge Retrieval** → `knowledge/retrieval.py` + `knowledge/live_fetch.py`
5. **Fragment Validation** → `shared_core/philosophy_guard.py`
6. **Monte Carlo Evaluation** → `monte_carlo/engine.py`
7. **Reasoning & Synthesis** → `core/reasoning_engine.py`
8. **Response Generation** → `core/narrative.py`
9. **Audit Logging** → `storage/vault.py`

### Key Components

#### OpenEyesEngine (`core/engine.py`)
Main entry point for query processing. Handles:
- Domain-specific routing
- Memory ingestion
- Confidence tracking
- Response generation

#### PhilosophyGuard (`shared_core/philosophy_guard.py`)
Rule-based validation system:
- Enforces domain-specific rules
- Validates fragment quality
- Blocks policy violations

#### MonteCarloEngine (`monte_carlo/engine.py`)
Probabilistic evaluation:
- Deterministic seeding for reproducibility
- Credibility scoring
- Scenario generation

## Development Guidelines

### Adding New Tests
1. Place unit tests in `tests/unit/`
2. Place integration tests in `tests/integration/`
3. Follow naming convention: `test_*.py`
4. Use pytest fixtures (`tmp_path`, etc.)
5. Aim for >80% coverage on new code

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings for public APIs
- Keep functions <50 lines when possible

### Commit Messages
```
feat: Add new feature
fix: Fix bug in component
test: Add tests for functionality
docs: Update documentation
refactor: Refactor code without changing behavior
```

## Archive Scripts

The `archive/` directory contains standalone scripts not connected to the main runtime pipeline:

### When to Use Archive Scripts
- **ipl_generators/**: Only when regenerating IPL fragments
- **build_scripts/**: During fragment migrations or schema changes
- **test_scripts/**: For manual production testing (consider migrating to pytest)
- **utilities/**: For maintenance tasks and operational adjustments

**Important**: These are NOT part of the automated pipeline. Run manually as needed.

## Troubleshooting

### Common Issues

**Deprecation Warnings**
- Fixed: `datetime.utcnow()` → `datetime.now(timezone.utc)` in `storage/vault.py`

**Philosophy Guard Failures**
- Check fragment schema matches domain rules
- Verify required fields are present
- Review `openeyes/domain_rules/` configuration

**Low Test Coverage**
- Start with critical paths (engine, retrieval, validation)
- Add integration tests for domain-specific behavior
- Use `--cov-report=html` for detailed coverage analysis

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/my-feature`)
3. Make changes with tests
4. Run full test suite: `pytest tests/ -v --cov=openeyes`
5. Ensure linting passes: `flake8`, `black --check`, `isort --check-only`
6. Submit pull request

## License

MIT License - see LICENSE file for details
