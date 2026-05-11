#!/usr/bin/env python3
"""
Execute the fragment renaming with proper handling for all edge cases.
"""

import os
import json
import re
from pathlib import Path

FRAGMENTS_DIR = Path("/workspace/openeyes/fragment_library/fragments")

ECONOMY_SECTORS = {'FIN', 'ENR', 'COM', 'MAC', 'GEO', 'REG'}
HEALTHCARE_SECTORS = {'PHR', 'MED', 'MH', 'PH'}

# Role abbreviations mapping
ROLE_ABBREVS = {
    'def': 'definition',
    'counter': 'counter_argument',
    'latest': 'latest_data',
}

def infer_sector_from_content(filepath):
    """Infer sector from JSON content."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if 'subdomain' in data and data['subdomain']:
                return data['subdomain']
            if 'sector' in data and data['sector']:
                return data['sector']
    except:
        pass
    return None

def normalize_role(role):
    """Normalize role abbreviations to full names."""
    role = role.lower().strip('_')
    return ROLE_ABBREVS.get(role, role)

def parse_any_filename(filename):
    """Parse any filename format and return standardized components."""
    name = filename.replace('.json', '')
    
    # Already correct: frag_eco_SECTOR_topic_role_NUM or frag_hc_SECTOR_topic_role_NUM
    match = re.match(r'^frag_(eco|hc)_([A-Z]+)_(.+?)_(definition|counter_argument|latest_data)_(\d+)$', name)
    if match:
        return None  # Already correct
    
    # Pattern: frag_eco_SECTOR_topic_abbrev_NUM (e.g., frag_eco_GEO_topic_def_043)
    match = re.match(r'^frag_eco_([A-Z]+)_(.+)_(def|counter|latest)_(\d+)$', name)
    if match:
        sector = match.group(1)
        topic = match.group(2)
        role = normalize_role(match.group(3))
        num = match.group(4).zfill(3)
        return ('economy', sector, topic, role, num)
    
    # Pattern: frag_{lowercase_sector}_* (e.g., frag_fin_*, frag_med_*)
    sector_map = {
        'fin': 'FIN', 'enr': 'ENR', 'com': 'COM', 'mac': 'MAC', 'geo': 'GEO', 'reg': 'REG',
        'phr': 'PHR', 'med': 'MED', 'mh': 'MH', 'ph': 'PH'
    }
    
    for prefix, sector in sector_map.items():
        if name.startswith(f'frag_{prefix}_'):
            remainder = name[len(f'frag_{prefix}_'):]
            parts = remainder.split('_')
            
            # Try to find role at end
            role = 'definition'
            num = '001'
            topic = remainder
            
            if len(parts) >= 2:
                last_part = parts[-1].lower()
                second_last = parts[-2].lower() if len(parts) >= 2 else ''
                
                if second_last in ['definition', 'counter_argument', 'latest_data']:
                    role = second_last
                    num = parts[-1].zfill(3)
                    topic = '_'.join(parts[:-2])
                elif last_part in ['definition', 'counter_argument', 'latest_data']:
                    role = last_part
                    topic = '_'.join(parts[:-1])
                elif second_last in ['def', 'counter', 'latest']:
                    role = normalize_role(second_last)
                    num = parts[-1].zfill(3)
                    topic = '_'.join(parts[:-2])
                elif last_part in ['def', 'counter', 'latest']:
                    role = normalize_role(last_part)
                    topic = '_'.join(parts[:-1])
            
            domain = 'economy' if sector in ECONOMY_SECTORS else 'healthcare'
            num_len = 3 if domain == 'economy' else 4
            return (domain, sector, topic, role, num.zfill(num_len))
    
    # Pattern: PREFIX-NUM_topic (e.g., FIN-147_behavioral_finance)
    match = re.match(r'^([A-Z]+)-(\d+)_(.+)$', name)
    if match:
        prefix = match.group(1)
        num = match.group(2)
        topic = match.group(3)
        
        if prefix == 'HC':
            inferred = infer_sector_from_content(FRAGMENTS_DIR / filename)
            sector = inferred if inferred in HEALTHCARE_SECTORS else 'MH'
            return ('healthcare', sector, topic, 'definition', num.zfill(4))
        elif prefix in ECONOMY_SECTORS:
            return ('economy', prefix, topic, 'definition', num.zfill(3))
        elif prefix in HEALTHCARE_SECTORS:
            return ('healthcare', prefix, topic, 'definition', num.zfill(4))
    
    # Pattern: COM-NUM_topic_role (e.g., COM-1919_market_structure_analysis_definition)
    match = re.match(r'^([A-Z]+)-(\d+)_(.+?)_(definition|counter_argument|latest_data)$', name)
    if match:
        prefix = match.group(1)
        num = match.group(2)
        topic = match.group(3)
        role = match.group(4)
        if prefix in ECONOMY_SECTORS:
            return ('economy', prefix, topic, role, num.zfill(3))
    
    return None

def generate_filename(components):
    """Generate standardized filename from components."""
    if not components:
        return None
    
    domain, sector, topic, role, num = components
    domain_short = 'eco' if domain == 'economy' else 'hc'
    topic_clean = topic.replace('__', '_').strip('_').lower()
    if not topic_clean:
        topic_clean = 'unknown'
    
    return f"frag_{domain_short}_{sector}_{topic_clean}_{role}_{num}.json"

def main():
    json_files = list(FRAGMENTS_DIR.glob("*.json"))
    print(f"Processing {len(json_files)} files...\n")
    
    renames = []
    errors = []
    
    for f in json_files:
        components = parse_any_filename(f.name)
        if components:
            new_name = generate_filename(components)
            if new_name and new_name != f.name:
                renames.append((f.name, new_name))
        else:
            # Check if already correct format
            if re.match(r'^frag_(eco|hc)_[A-Z]+_.+_(definition|counter_argument|latest_data)_\d+\.json$', f.name):
                pass  # Already correct
            else:
                errors.append(f.name)
    
    print(f"Files to rename: {len(renames)}")
    print(f"Unparseable files: {len(errors)}")
    
    if errors:
        print(f"\nUnparseable (first 20):")
        for e in errors[:20]:
            print(f"  - {e}")
    
    # Execute renames
    print(f"\nExecuting renames...")
    success = 0
    failed = 0
    
    for old_name, new_name in renames:
        old_path = FRAGMENTS_DIR / old_name
        new_path = FRAGMENTS_DIR / new_name
        
        if old_path.exists():
            try:
                # Handle potential conflicts by checking if target exists
                if new_path.exists():
                    # Add timestamp to avoid conflict
                    base = new_name.replace('.json', '')
                    new_name = f"{base}_dup.json"
                    new_path = FRAGMENTS_DIR / new_name
                
                old_path.rename(new_path)
                success += 1
            except Exception as e:
                print(f"Failed: {old_name} -> {new_name}: {e}")
                failed += 1
    
    print(f"\n=== Results ===")
    print(f"Successfully renamed: {success}")
    print(f"Failed: {failed}")
    print(f"Already correct: {len(json_files) - len(renames) - len(errors)}")
    
    # Save log
    with open('/workspace/rename_execution_log.json', 'w') as f:
        json.dump({
            'renames': [{'old': old, 'new': new} for old, new in renames],
            'errors': errors,
            'success_count': success,
            'failed_count': failed
        }, f, indent=2)
    
    print(f"\nLog saved to /workspace/rename_execution_log.json")

if __name__ == '__main__':
    main()
