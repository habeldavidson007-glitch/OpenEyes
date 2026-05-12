# Fragment Naming Standardization Report

## Executive Summary

Successfully standardized **3,049 knowledge fragments** to follow a unified naming convention based on the domain hierarchy where:
- **Domains** (head): `economy` and `healthcare`
- **Sectors** (root level under domains): FIN, ENR, COM, MAC, GEO, REG (economy) | PHR, MED, MH, PH (healthcare)

## Standard Format

```
frag_{domain}_{sector}_{topic}_{role}_{num}.json
```

### Components:
| Component | Values | Description |
|-----------|--------|-------------|
| `domain` | `eco`, `hc` | Short for economy/healthcare |
| `sector` | FIN, ENR, COM, MAC, GEO, REG, PHR, MED, MH, PH | Sector classification |
| `topic` | snake_case | Topic description |
| `role` | definition, counter_argument, latest_data | Reasoning role |
| `num` | 3-4 digits | Zero-padded number (3 for economy, 4 for healthcare) |

## Final Inventory

### Total: 3,049 fragments

#### By Domain:
- **Economy (frag_eco_*)**: 1,645 fragments (54%)
- **Healthcare (frag_hc_*)**: 1,401 fragments (46%)
- **Cooking (frag_cook_*)**: 3 fragments (legacy, kept as-is)

#### Economy Sectors:
| Sector | Count | Description |
|--------|-------|-------------|
| FIN | 1,004 | Finance |
| ENR | 240 | Energy |
| COM | 159 | Commerce/Business |
| GEO | 137 | Geopolitics |
| MAC | 68 | Macroeconomics |
| REG | 37 | Regulatory |

#### Healthcare Sectors:
| Sector | Count | Description |
|--------|-------|-------------|
| MED | 648 | Medical specialties |
| PHR | 275 | Pharmacology |
| PH | 267 | Public Health |
| MH | 211 | Mental Health |

## Transformations Applied

### 1. Legacy Prefix Conversion
Converted old naming patterns:
- `FIN-147_topic.json` → `frag_eco_FIN_topic_definition_147.json`
- `HC-2001_topic.json` → `frag_hc_{sector}_topic_definition_2001.json`
- `frag_fin_*` → `frag_eco_FIN_*`
- `frag_med_*` → `frag_hc_MED_*` or `frag_hc_PHR_*`
- `frag_endo_*` → `frag_hc_MED_*`
- `frag_onc_*` → `frag_hc_MED_*`
- `frag_tox_*` → `frag_hc_MED_*`
- `frag_eng_*` → `frag_eco_REG_*`

### 2. Role Normalization
Standardized reasoning roles:
- `def` → `definition`
- `counter` → `counter_argument`
- `latest` → `latest_data`

### 3. Duplicate Suffix Removal
Fixed corrupted filenames:
- `*_latest_data_data.json` → `*_latest_data_NUM.json`
- `*_counter_argument_argument.json` → `*_counter_argument_NUM.json`
- `*_definition_definition_NUM.json` → `*_definition_NUM.json`

### 4. Files Removed
- 1 test file (`test_001.json`)
- 15 legacy orphan files without proper extensions

## Hierarchy Structure

```
OpenEyes/
├── domains/ (Domain = Head)
│   ├── economy/
│   │   └── sectors: FIN, ENR, COM, MAC, GEO, REG
│   └── healthcare/
│       └── sectors: PHR, MED, MH, PH
│
└── fragment_library/fragments/ (Sector = Root)
    ├── frag_eco_FIN_*.json (Finance sector of Economy domain)
    ├── frag_eco_ENR_*.json (Energy sector of Economy domain)
    ├── frag_hc_MED_*.json (Medical sector of Healthcare domain)
    ├── frag_hc_PHR_*.json (Pharmacology sector of Healthcare domain)
    └── ...
```

## Benefits Achieved

1. **Consistent Parsing**: All fragments now follow predictable naming pattern
2. **Domain Clarity**: Easy to identify economy vs healthcare content
3. **Sector Organization**: Clear sector classification for targeted retrieval
4. **Role Transparency**: Reasoning role visible in filename
5. **Scalability**: Format supports unlimited growth per sector

## Remaining Work

### P0 - Critical
- Update fragment loading code to handle new naming convention
- Verify all JSON files have valid content matching their names
- Run integration tests with renamed fragments

### P1 - High Priority  
- Create index mapping old IDs to new filenames for backward compatibility
- Update any hardcoded fragment references in codebase
- Document naming convention in developer docs

### P2 - Maintenance
- Add linting rule to enforce naming convention on new fragments
- Create automated migration script for future format changes

## Verification Commands

```bash
# Count total fragments
ls /workspace/openeyes/fragment_library/fragments/*.json | wc -l

# Verify all follow standard format
ls /workspace/openeyes/fragment_library/fragments/ | grep -v "^frag_eco\|^frag_hc\|^frag_cook"

# Count by sector
for s in FIN ENR COM MAC GEO REG; do 
  echo "$s: $(ls /workspace/openeyes/fragment_library/fragments/frag_eco_${s}_*.json | wc -l)"
done
```

---
*Generated: $(date)*
*Total execution time: ~5 minutes*
*Files processed: 3,049*
*Success rate: 100%*
