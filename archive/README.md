# Archive Directory

This directory contains standalone scripts, historical generators, and manual utilities that are **not connected to the main runtime pipeline**.

## Contents

### ipl_generators/
**Purpose:** One-time fragment generation scripts for IPL (In-Process Learning) fragments.
**Status:** Historical/Batch processing - Not called by runtime pipeline.
**Files:**
- `generate_ipl_complete.py` - Complete IPL fragment generation
- `generate_ipl_fragments.py` - Basic IPL fragment generator
- `regen_ipl_all.py` - Regenerate all IPL fragments
- `generate_ipl_remaining.py` - Generate remaining IPL fragments
- `create_gel_fragments.py` - GEL fragment creation
- `final_ipl_gen.py` - Final IPL generation pass

**When to use:** Only when regenerating or migrating IPL fragments. Run manually as needed.

---

### build_scripts/
**Purpose:** Fragment building and migration utilities.
**Status:** One-time migration/generation - Not in runtime path.
**Files:**
- `build_geo_fragments_part[1-5].py` - Geographic fragment building (multi-part)
- `build_geo_final.py` - Final geographic fragment build
- `migrate_healthcare_fragments.py` - Healthcare fragment migration
- `migrate_fragments.py` - General fragment migration
- `fix_missing_source.py` - Fix fragments missing source metadata
- `generate_ta_fragments.py` - Technical analysis fragment generation
- `create_mac_fragments.py` - MAC fragment creation
- `build_all_enr.py` - Build all ENR fragments
- `fix_enr_fragments.py` - Fix ENR fragment issues
- `build_reg_fragments.py` - Regulatory fragment building
- `generate_crypto_fragments.py` - Cryptocurrency fragment generation
- `build_enr_final.py` - Final ENR build pass

**When to use:** Only during fragment migrations, bulk updates, or schema changes. Run manually as needed.

---

### test_scripts/
**Purpose:** Ad-hoc test runners and production test suites.
**Status:** Manual testing - Not integrated into CI/CD or pytest suite.
**Files:**
- `run_adversarial_50_suite.py` - Adversarial 50-query test suite
- `test_healthcare_50.py` - Healthcare domain 50-query test
- `test_production_healthcare.py` - Production healthcare testing
- `test_ekd_pipeline.py` - EKD pipeline testing
- `run_50_query_test.py` - Generic 50-query test runner
- `run_production_hardening_test_50.py` - Production hardening test (v1)
- `run_production_hardening_test_v2.py` - Production hardening test (v2)
- `test_suite_50.py` - 50-query test suite
- `test_dual_domain.py` - Dual domain testing
- `run_economy_test_50x.py` - Economy domain 50x test
- `run_query_test_5x.py` - 5-query test runner

**When to use:** For manual production testing, adversarial testing, or domain-specific validation. Consider migrating to pytest format for CI/CD integration.

---

### utilities/
**Purpose:** Operational maintenance tools.
**Status:** Operational utilities - Run manually as needed.
**Files:**
- `fix_all_fragments.py` - Comprehensive fragment fixing
- `fix_legacy_fragments.py` - Fix legacy fragment issues
- `fix_immediate_blockers.py` - Fix immediate production blockers
- `fix_ipl_trademark.py` - Fix IPL trademark issues
- `fix_remaining_fragments.py` - Fix remaining fragment issues
- `execute_rename.py` - Execute file renames
- `file_organizer.py` - File organization utility
- `standardize_fragments.py` - Standardize fragment format
- `night_mode_daemon.py` - Night mode daemon script

**When to use:** For maintenance tasks, fragment fixes, or operational adjustments. Run manually as needed.

---

## Migration Notes

These scripts were moved to archive on **2024** to:
1. Clarify the runtime pipeline boundaries
2. Reduce confusion about which code is actively used
3. Prepare for CI/CD integration with cleaner structure
4. Document historical/batch operations separately

**Important:** Do NOT delete these scripts without verifying they are no longer needed for maintenance or migration tasks.
