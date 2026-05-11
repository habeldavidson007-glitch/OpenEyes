#!/usr/bin/env python3
"""
Fix legacy fragment naming patterns (frag_endo_*, frag_eng_*, frag_med_*, frag_onc_*, frag_tox_*).
Map these to proper domain/sector format.
"""

import os
import json
import re
from pathlib import Path

FRAGMENTS_DIR = Path("/workspace/openeyes/fragment_library/fragments")

# Legacy prefix to sector mapping
LEGACY_MAP = {
    'endo': ('healthcare', 'MED'),  # Endocrinology -> Medical
    'eng': ('economy', 'REG'),       # Engineering -> Regulatory (or create ENG sector)
    'med': ('healthcare', 'PHR'),    # Medical general -> Pharmacology
    'onc': ('healthcare', 'MED'),    # Oncology -> Medical
    'tox': ('healthcare', 'MED'),    # Toxicology -> Medical
}

def fix_legacy_filename(filename):
    """Convert legacy filenames to standard format."""
    name = filename.replace('.json', '')
    
    for prefix, (domain, sector) in LEGACY_MAP.items():
        if name.startswith(f'frag_{prefix}_'):
            remainder = name[len(f'frag_{prefix}_'):]
            
            # Determine role and number from suffix
            role = 'definition'
            num = '001'
            topic = remainder
            
            if remainder.endswith('_counter') or remainder.endswith('_counter_001'):
                role = 'counter_argument'
                match = re.search(r'_(\d+)$', remainder)
                if match:
                    num = match.group(1).zfill(3)
                topic = remainder.replace('_counter', '').replace(f'_{num}', '').strip('_')
            elif remainder.endswith('_latest') or re.search(r'_latest_\d+$', remainder):
                role = 'latest_data'
                match = re.search(r'_latest_(\d+)$', remainder)
                if match:
                    num = match.group(1).zfill(3)
                topic = remainder.replace('_latest', '').replace(f'_{num}', '').strip('_')
            else:
                # Extract number from end if present
                match = re.search(r'_(\d+)$', remainder)
                if match:
                    num = match.group(1).zfill(3)
                    topic = remainder.replace(f'_{num}', '').strip('_')
            
            num_len = 3 if domain == 'economy' else 4
            domain_short = 'eco' if domain == 'economy' else 'hc'
            
            return f"frag_{domain_short}_{sector}_{topic}_{role}_{num.zfill(num_len)}.json"
    
    return None

def main():
    json_files = list(FRAGMENTS_DIR.glob("*.json"))
    print(f"Checking {len(json_files)} files for legacy fixes...\n")
    
    fixes = []
    for f in json_files:
        # Skip already correct files
        if re.match(r'^frag_(eco|hc)_[A-Z]+_.+_(definition|counter_argument|latest_data)_\d+\.json$', f.name):
            continue
        if f.name.startswith('frag_cook_'):
            continue
        
        new_name = fix_legacy_filename(f.name)
        if new_name:
            fixes.append((f.name, new_name))
    
    print(f"Legacy files to fix: {len(fixes)}")
    
    if fixes:
        print("\nSample fixes:")
        for old, new in fixes[:20]:
            print(f"  {old}")
            print(f"    -> {new}")
        
        # Execute fixes
        print(f"\nApplying fixes...")
        success = 0
        failed = 0
        for old_name, new_name in fixes:
            old_path = FRAGMENTS_DIR / old_name
            new_path = FRAGMENTS_DIR / new_name
            
            if old_path.exists():
                try:
                    if new_path.exists():
                        # Conflict - add _dup
                        base = new_name.replace('.json', '')
                        new_name = f"{base}_dup.json"
                        new_path = FRAGMENTS_DIR / new_name
                    
                    old_path.rename(new_path)
                    success += 1
                except Exception as e:
                    print(f"Failed: {old_name} -> {new_name}: {e}")
                    failed += 1
        
        print(f"Fixed: {success}/{len(fixes)} (failed: {failed})")
    
    # Final stats
    final_files = list(FRAGMENTS_DIR.glob("*.json"))
    correct = sum(1 for f in final_files if re.match(r'^frag_(eco|hc)_[A-Z]+_.+_(definition|counter_argument|latest_data)_\d+\.json$', f.name))
    cook = sum(1 for f in final_files if f.name.startswith('frag_cook_'))
    other = len(final_files) - correct - cook
    
    print(f"\n=== Final Stats ===")
    print(f"Total files: {len(final_files)}")
    print(f"Correct format (frag_eco/hc_*): {correct}")
    print(f"Cooking (frag_cook_*): {cook}")
    print(f"Remaining issues: {other}")
    
    if other > 0:
        print("\nRemaining problematic files:")
        for f in final_files:
            if not re.match(r'^frag_(eco|hc)_[A-Z]+_.+_(definition|counter_argument|latest_data)_\d+\.json$', f.name) and not f.name.startswith('frag_cook_'):
                print(f"  - {f.name}")

if __name__ == '__main__':
    main()
