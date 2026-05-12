#!/usr/bin/env python3
"""
Comprehensive fragment filename standardization.

Target format: frag_{domain}_{sector}_{topic}_{role}_{num}.json
- domain: eco (economy) or hc (healthcare)
- sector: FIN, ENR, COM, MAC, GEO, REG (economy) or PHR, MED, MH, PH (healthcare)
- topic: snake_case topic name
- role: definition, counter_argument, latest_data
- num: zero-padded number

Domain mapping from prefixes:
- Economy: FIN, ENR, COM, MAC, GEO, REG -> eco
- Healthcare: PHR, MED, MH, PH, HC -> hc
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict

FRAGMENTS_DIR = Path("/workspace/openeyes/fragment_library/fragments")

# Sector classifications
ECONOMY_SECTORS = {'FIN', 'ENR', 'COM', 'MAC', 'GEO', 'REG'}
HEALTHCARE_SECTORS = {'PHR', 'MED', 'MH', 'PH'}

def infer_sector_from_content(filepath):
    """Try to infer sector from file content if filename is ambiguous."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Check subdomain field first
            if 'subdomain' in data:
                return data['subdomain']
            # Check sector field
            if 'sector' in data:
                return data['sector']
            # Check domain field
            if 'domain' in data:
                if data['domain'] == 'economy':
                    return 'COM'  # Default economy sector
                elif data['domain'] == 'healthcare':
                    return 'MH'  # Default healthcare sector
    except:
        pass
    return None

def parse_filename_v2(filename):
    """Improved parser for various filename formats."""
    name = filename.replace('.json', '')
    
    # Pattern 1: Already correct format: frag_eco_SECTOR_topic_role_NUM
    match = re.match(r'^frag_(eco|hc)_([A-Z]+)_(.+?)_(definition|counter_argument|latest_data)_(\d+)$', name)
    if match:
        domain = 'economy' if match.group(1) == 'eco' else 'healthcare'
        return {
            'domain': domain,
            'sector': match.group(2),
            'topic': match.group(3),
            'role': match.group(4),
            'num': match.group(5).zfill(3) if domain == 'economy' else match.group(5).zfill(4),
            'already_correct': True
        }
    
    # Pattern 2: frag_eco_SECTOR_topic_role_NUM (economy existing correct)
    if name.startswith('frag_eco_'):
        parts = name.split('_')
        if len(parts) >= 5:
            sector = parts[2]
            # Find role from end
            if parts[-2] in ['definition', 'counter_argument', 'latest_data']:
                return {
                    'domain': 'economy',
                    'sector': sector,
                    'topic': '_'.join(parts[3:-2]),
                    'role': parts[-2],
                    'num': parts[-1].zfill(3)
                }
    
    # Pattern 3: frag_{sector}_* where sector is lowercase (WRONG - needs fixing)
    # e.g., frag_fin_..., frag_med_..., frag_ph_..., frag_mh_..., frag_phr_..., frag_enr_..., frag_com_..., frag_mac_..., frag_geo_..., frag_reg_...
    sector_prefixes = {
        'fin': 'FIN', 'enr': 'ENR', 'com': 'COM', 'mac': 'MAC', 'geo': 'GEO', 'reg': 'REG',
        'phr': 'PHR', 'med': 'MED', 'mh': 'MH', 'ph': 'PH'
    }
    
    for prefix, sector in sector_prefixes.items():
        if name.startswith(f'frag_{prefix}_'):
            remainder = name[len(f'frag_{prefix}_'):]
            # Try to extract role from end
            parts = remainder.split('_')
            role = 'definition'
            num = '001'
            topic = remainder
            
            # Check if ends with role_num pattern
            if len(parts) >= 2:
                if parts[-2] in ['definition', 'counter_argument', 'latest_data']:
                    role = parts[-2]
                    num = parts[-1].zfill(3)
                    topic = '_'.join(parts[:-2])
                elif parts[-1] in ['definition', 'counter_argument', 'latest_data']:
                    role = parts[-1]
                    topic = '_'.join(parts[:-1])
            
            domain = 'economy' if sector in ECONOMY_SECTORS else 'healthcare'
            return {
                'domain': domain,
                'sector': sector,
                'topic': topic,
                'role': role,
                'num': num.zfill(3) if domain == 'economy' else num.zfill(4)
            }
    
    # Pattern 4: PREFIX-NUM_topic (e.g., FIN-147_behavioral_finance, HC-2001_patient_safety)
    match = re.match(r'^([A-Z]+)-(\d+)_(.+)$', name)
    if match:
        prefix = match.group(1)
        num = match.group(2)
        topic = match.group(3)
        
        # Handle HC prefix - infer actual sector from content or default
        if prefix == 'HC':
            filepath = FRAGMENTS_DIR / filename
            inferred_sector = infer_sector_from_content(filepath)
            if inferred_sector and inferred_sector in HEALTHCARE_SECTORS:
                sector = inferred_sector
            else:
                # Try to infer from topic
                topic_lower = topic.lower()
                if 'drug' in topic_lower or 'pharm' in topic_lower or 'biologics' in topic_lower:
                    sector = 'PHR'
                elif 'cardio' in topic_lower or 'oncology' in topic_lower or 'endocrine' in topic_lower:
                    sector = 'MED'
                elif 'suicide' in topic_lower or 'personality' in topic_lower or 'disorder' in topic_lower:
                    sector = 'MH'
                elif 'epidemiology' in topic_lower or 'public health' in topic_lower or 'disease' in topic_lower:
                    sector = 'PH'
                else:
                    sector = 'MH'  # Default
            
            return {
                'domain': 'healthcare',
                'sector': sector,
                'topic': topic,
                'role': 'definition',
                'num': num.zfill(4)
            }
        
        if prefix in ECONOMY_SECTORS:
            return {
                'domain': 'economy',
                'sector': prefix,
                'topic': topic,
                'role': 'definition',
                'num': num.zfill(3)
            }
        elif prefix in HEALTHCARE_SECTORS:
            return {
                'domain': 'healthcare',
                'sector': prefix,
                'topic': topic,
                'role': 'definition',
                'num': num.zfill(4)
            }
    
    # Pattern 5: COM-NUM_topic_role (e.g., COM-1919_market_structure_analysis_definition)
    match = re.match(r'^([A-Z]+)-(\d+)_(.+?)_(definition|counter_argument|latest_data)$', name)
    if match:
        prefix = match.group(1)
        num = match.group(2)
        topic = match.group(3)
        role = match.group(4)
        
        if prefix in ECONOMY_SECTORS:
            return {
                'domain': 'economy',
                'sector': prefix,
                'topic': topic,
                'role': role,
                'num': num.zfill(3)
            }
    
    return None

def generate_standard_filename(parsed):
    """Generate standardized filename."""
    if not parsed:
        return None
    
    domain_short = 'eco' if parsed['domain'] == 'economy' else 'hc'
    sector = parsed['sector']
    topic = parsed['topic'].replace('__', '_').strip('_').lower()
    role = parsed['role']
    num = parsed['num']
    
    # Ensure topic is not empty
    if not topic:
        topic = 'unknown'
    
    return f"frag_{domain_short}_{sector}_{topic}_{role}_{num}.json"

def main():
    json_files = list(FRAGMENTS_DIR.glob("*.json"))
    print(f"Found {len(json_files)} fragment files\n")
    
    renames = []
    unchanged = 0
    unparseable = []
    
    for f in json_files:
        parsed = parse_filename_v2(f.name)
        if parsed:
            new_name = generate_standard_filename(parsed)
            if new_name and new_name != f.name:
                renames.append((f.name, new_name, parsed))
            elif parsed.get('already_correct'):
                unchanged += 1
            else:
                # File is parseable but generates same name (might already be correct)
                unchanged += 1
        else:
            unparseable.append(f.name)
    
    print(f"=== Analysis Results ===")
    print(f"Already correct: {unchanged}")
    print(f"To rename: {len(renames)}")
    print(f"Unparseable: {len(unparseable)}")
    
    if unparseable:
        print(f"\nUnparseable files (first 10):")
        for name in unparseable[:10]:
            print(f"  - {name}")
    
    if renames:
        print(f"\n=== Sample Renames (first 20) ===")
        for old, new, parsed in renames[:20]:
            print(f"{old}")
            print(f"  -> {new}")
            print(f"     [domain={parsed['domain']}, sector={parsed['sector']}, role={parsed['role']}]")
            print()
    
    # Check for conflicts
    new_names = [new for _, new, _ in renames]
    duplicates = [name for name in set(new_names) if new_names.count(name) > 1]
    if duplicates:
        print(f"\n⚠️  CONFLICTS DETECTED: {len(duplicates)} duplicate target names")
        for dup in duplicates[:10]:
            sources = [old for old, new, _ in renames if new == dup]
            print(f"  {dup} <- {sources}")
    else:
        print(f"\n✅ No naming conflicts detected")
    
    # Save rename plan
    with open('/workspace/rename_plan_v2.json', 'w') as f:
        json.dump({
            'renames': [{'old': old, 'new': new, 'parsed': parsed} for old, new, parsed in renames],
            'unparseable': unparseable,
            'unchanged_count': unchanged
        }, f, indent=2)
    
    print(f"\nRename plan saved to /workspace/rename_plan_v2.json")
    return renames, unparseable

if __name__ == '__main__':
    main()
