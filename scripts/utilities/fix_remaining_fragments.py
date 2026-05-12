#!/usr/bin/env python3
"""
Fix remaining unparseable fragments with edge cases.
"""

import os
import json
import re
from pathlib import Path

FRAGMENTS_DIR = Path("/workspace/openeyes/fragment_library/fragments")

def fix_filename(filename):
    """Fix problematic filename patterns."""
    name = filename.replace('.json', '')
    
    # Pattern: ..._latest_data_data.json -> ..._latest_data_NUM.json
    if name.endswith('_latest_data_data'):
        base = name.replace('_latest_data_data', '')
        # Try to extract number or use 001
        match = re.search(r'(\d+)$', base)
        if match:
            num = match.group(1).zfill(3)
            base = base.rstrip('0123456789')
        else:
            num = '001'
        return f"{base}_latest_data_{num}.json"
    
    # Pattern: ..._counter_argument_argument.json -> ..._counter_argument_NUM.json
    if name.endswith('_counter_argument_argument'):
        base = name.replace('_counter_argument_argument', '')
        match = re.search(r'(\d+)$', base)
        if match:
            num = match.group(1).zfill(3)
            base = base.rstrip('0123456789')
        else:
            num = '001'
        return f"{base}_counter_argument_{num}.json"
    
    # Pattern: ..._definition_definition_NUM.json -> ..._definition_NUM.json
    match = re.match(r'^(.+?)_definition_definition_(\d+)$', name)
    if match:
        base = match.group(1)
        num = match.group(2).zfill(3)
        return f"{base}_definition_{num}.json"
    
    # Pattern: frag_eco_ENR_ccus_analysis_0042.json -> needs role
    match = re.match(r'^frag_eco_ENR_(.+)_analysis_(\d+)$', name)
    if match:
        topic = match.group(1)
        num = match.group(2).zfill(3)
        return f"frag_eco_ENR_{topic}_latest_data_{num}.json"
    
    # Pattern: frag_cook_* - keep as is (cooking domain)
    if name.startswith('frag_cook_'):
        return None  # Keep as is
    
    return None

def main():
    json_files = list(FRAGMENTS_DIR.glob("*.json"))
    print(f"Checking {len(json_files)} files for fixes...\n")
    
    fixes = []
    for f in json_files:
        new_name = fix_filename(f.name)
        if new_name and new_name != f.name:
            fixes.append((f.name, new_name))
    
    print(f"Files to fix: {len(fixes)}")
    
    if fixes:
        print("\nSample fixes:")
        for old, new in fixes[:20]:
            print(f"  {old}")
            print(f"    -> {new}")
        
        # Execute fixes
        print(f"\nApplying fixes...")
        success = 0
        for old_name, new_name in fixes:
            old_path = FRAGMENTS_DIR / old_name
            new_path = FRAGMENTS_DIR / new_name
            
            if old_path.exists() and not new_path.exists():
                try:
                    old_path.rename(new_path)
                    success += 1
                except Exception as e:
                    print(f"Failed: {old_name} -> {new_name}: {e}")
        
        print(f"Fixed: {success}/{len(fixes)}")
    
    # Show final stats
    final_files = list(FRAGMENTS_DIR.glob("*.json"))
    print(f"\n=== Final Stats ===")
    print(f"Total files: {len(final_files)}")
    
    # Count by pattern
    correct = sum(1 for f in final_files if re.match(r'^frag_(eco|hc)_[A-Z]+_.+_(definition|counter_argument|latest_data)_\d+\.json$', f.name))
    cook = sum(1 for f in final_files if f.name.startswith('frag_cook_'))
    other = len(final_files) - correct - cook
    
    print(f"Correct format: {correct}")
    print(f"Cooking (frag_cook_*): {cook}")
    print(f"Other/Issues: {other}")

if __name__ == '__main__':
    main()
