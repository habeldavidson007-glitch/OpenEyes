# OpenEyes Refactor & Productization Plan

## Is OpenEyes "good yet"?
Short answer: **promising architecture, but not yet product-ready**.

Current strengths visible in the repository:
- Modular core split (`openeyes/core`, `openeyes/cognitive`, `shared_core`)
- Meaningful test surface (`tests/unit`, `tests/integration`, multiple E2E scripts)
- Existing packaging metadata (`pyproject.toml`, `setup.py`, `requirements.txt`)

Current blockers to a smooth user experience:
- Large amount of archive/legacy code creates cognitive load
- Several overlapping entry points and harness scripts
- CLI/UI boundary is not cleanly defined for future desktop shell
- Installation path is not yet "one obvious way" for non-technical users

## Overengineered or not?
**Partially overengineered for current stage**, mostly in project surface area rather than core design.

What looks overengineered today:
- Too many historical artifacts and reports mixed with runtime code
- Multiple parallel experimental engines in-tree for users
- Broad domain data and tooling coupled directly to main package

What does *not* look overengineed:
- A layered architecture intention exists and can be tightened
- Tests indicate you care about correctness/regression safety

## Product Direction Recommendation
You are right: start with a clean CLI, then wrap as desktop.

### Phase 1 — Stabilize CLI as the source of truth
1. Define one public command: `openeyes`.
2. Create subcommands: `ask`, `doctor`, `version`, `config`.
3. Standardize machine-readable output mode (`--json`) for GUI reuse.
4. Introduce stable API boundary in Python package (service layer).

### Phase 2 — Refactor internals without changing behavior
1. Move legacy/experimental code into clearly excluded namespaces.
2. Create strict module contracts:
   - `openeyes/app` (entrypoints)
   - `openeyes/services` (business orchestration)
   - `openeyes/adapters` (filesystem/network)
   - `openeyes/core` (reasoning primitives)
3. Add deprecation map and module ownership.
4. Keep each change guarded by snapshot tests.

### Phase 3 — Make installation easy
1. Ship with a lockfile-backed installer story:
   - `pipx install openeyes` for users
   - optional standalone binaries later
2. Add a single "quickstart" path in README with 3 commands max.
3. Add diagnostics command: `openeyes doctor`.
4. Add preflight checks (Python version, data presence, permissions).

### Phase 4 — Desktop app from the same engine
1. Keep CLI/service layer unchanged.
2. Build desktop shell (Tauri or Electron) that calls local service/CLI.
3. Reuse CLI JSON protocol so desktop is a thin client.
4. Add update and crash-reporting pipeline only after MVP is stable.

## Surgical fixes to start immediately
Priority order:
1. **Entrypoint unification**: one package entry path.
2. **Repository hygiene**: archive isolation + clear runtime folders.
3. **Config centralization**: one config loader with env overrides.
4. **Error taxonomy**: user-facing vs developer-facing exceptions.
5. **Logging policy**: predictable log directory + verbosity flags.
6. **Test pyramid cleanup**: deterministic unit tests first, E2E smoke second.

## Definition of "good" (release gate)
OpenEyes is "good" when all are true:
- Fresh install + first query in under 5 minutes
- `openeyes doctor` reports green in a clean machine
- Core CLI commands have stable flags for 2 consecutive releases
- Unit/integration smoke tests pass in CI reliably
- Desktop shell can be removed without affecting engine behavior

## Suggested 2-week execution sprint
Week 1:
- CLI contract and service boundary
- Entrypoint cleanup
- README quickstart rewrite

Week 2:
- Archive isolation
- `doctor` command
- Packaging polish (`pipx` path), release candidate

## Non-goals right now
- Perfect architecture
- Full plugin ecosystem
- Aggressive multi-agent runtime complexity

Focus on: **boring reliability + easy install + clear CLI UX**.
