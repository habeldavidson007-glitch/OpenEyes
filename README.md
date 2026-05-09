# OpenEyes

Deterministic chaos Monte Carlo reasoning engine for high-stakes domains.

## Architecture
- **Brain**: `openeyes/core` and domain/safety decision logic.
- **Muscle**: `openeyes/monte_carlo` using NumPy/SciPy (Sobol, PCG, Box-Muller).
- **Safety**: domain thresholds and HALT behavior for low-confidence/high-stakes outputs.
- **Storage**: gzip+pickle binary persistence and Obsidian-style audit cleanup.

## CLI
```bash
openeyes query "Pancreatic Cancer Symptoms" --domain medical
openeyes sleep
openeyes status
openeyes serve --port 8080
```

## Testing
```bash
pytest -q tests/test_e2e.py
```
