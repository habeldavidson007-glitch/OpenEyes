#!/usr/bin/env python3
"""
Standardize all fragment filenames to follow the format:
frag_{domain}_{sector}_{topic}_{role}_{num}.json

Domain mapping:
- economy -> eco
- healthcare -> hc

Sector mapping:
- Economy sectors: FIN, ENR, COM, MAC, GEO, REG
- Healthcare sectors: PHR, MED, MH, PH

Role extraction from existing files or default to 'definition'
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict

FRAGMENTS_DIR = Path("/workspace/openeyes/fragment_library/fragments")

def parse_existing_filename(filename):
    """Parse existing filename to extract components."""
    name = filename.replace('.json', '')
    
    # Pattern 1: frag_eco_SECTOR_topic_role_NUM
    if name.startswith('frag_eco_'):
        parts = name.split('_')
        if len(parts) >= 5:
            return {
                'domain': 'economy',
                'sector': parts[2],
                'topic': '_'.join(parts[3:-2]),
                'role': parts[-2],
                'num': parts[-1]
            }
    
    # Pattern 2: frag_cook_*
    if name.startswith('frag_cook_'):
        return {
            'domain': 'cooking',
            'sector': 'COOK',
            'topic': name.replace('frag_cook_', ''),
            'role': 'definition',
            'num': '001'
        }
    
    # Pattern 3: PREFIX-NUM_topic (e.g., FIN-147_behavioral_finance)
    match = re.match(r'^([A-Z]+)-(\d+)_(.+)$', name)
    if match:
        prefix = match.group(1)
        num = match.group(2)
        topic = match.group(3)
        
        # Determine domain and sector from prefix
        economy_sectors = {'FIN', 'ENR', 'COM', 'MAC', 'GEO', 'REG'}
        healthcare_sectors = {'PHR', 'MED', 'MH', 'PH', 'HC'}
        
        if prefix in economy_sectors:
            return {
                'domain': 'economy',
                'sector': prefix,
                'topic': topic,
                'role': 'definition',
                'num': num.zfill(3)
            }
        elif prefix in healthcare_sectors or prefix == 'HC':
            # Map HC to appropriate sector based on content or default
            sector = prefix if prefix != 'HC' else 'MH'  # Default HC to MH
            return {
                'domain': 'healthcare',
                'sector': sector,
                'topic': topic,
                'role': 'definition',
                'num': num.zfill(4)
            }
    
    return None

def get_new_filename(parsed):
    """Generate new standardized filename."""
    if not parsed:
        return None
    
    domain_short = 'eco' if parsed['domain'] == 'economy' else 'hc' if parsed['domain'] == 'healthcare' else parsed['domain']
    sector = parsed['sector']
    topic = parsed['topic'].replace('__', '_').strip('_')
    role = parsed['role']
    num = parsed['num']
    
    return f"frag_{domain_short}_{sector}_{topic}_{role}_{num}.json"

def main():
    # Collect all JSON files
    json_files = list(FRAGMENTS_DIR.glob("*.json"))
    print(f"Found {len(json_files)} fragment files")
    
    # Analyze naming patterns
    patterns = defaultdict(list)
    for f in json_files:
        name = f.name.replace('.json', '')
        if name.startswith('frag_eco_'):
            patterns['frag_eco_SECTOR_topic_role_NUM'].append(f.name)
        elif name.startswith('frag_cook_'):
            patterns['frag_cook_topic'].append(f.name)
        elif re.match(r'^[A-Z]+-\d+_.+$', name):
            patterns['PREFIX-NUM_topic'].append(f.name)
        else:
            patterns['other'].append(f.name)
    
    print("\n=== Current Naming Patterns ===")
    for pattern, files in patterns.items():
        print(f"{pattern}: {len(files)} files")
        if files:
            print(f"  Examples: {files[:3]}")
    
    # Generate rename plan
    renames = []
    conflicts = set()
    new_names = set()
    
    for f in json_files:
        parsed = parse_existing_filename(f.name)
        if parsed:
            new_name = get_new_filename(parsed)
            if new_name and new_name != f.name:
                if new_name in new_names:
                    conflicts.add(new_name)
                    print(f"CONFLICT: {new_name} would be created multiple times")
                new_names.add(new_name)
                renames.append((f.name, new_name, parsed))
    
    print(f"\n=== Rename Plan ===")
    print(f"Files to rename: {len(renames)}")
    print(f"Potential conflicts: {len(conflicts)}")
    
    if renames[:10]:
        print("\nFirst 10 renames:")
        for old, new, parsed in renames[:10]:
            print(f"  {old}")
            print(f"    -> {new}")
    
    return renames, conflicts

if __name__ == '__main__':
    renames, conflicts = main()
    
    # Save rename plan
    with open('/workspace/rename_plan.json', 'w') as f:
        json.dump([{
            'old': old,
            'new': new,
            'parsed': parsed
        } for old, new, parsed in renames], f, indent=2)
    
    print(f"\nRename plan saved to /workspace/rename_plan.json")
    print(f"Total files to process: {len(renames)}")
