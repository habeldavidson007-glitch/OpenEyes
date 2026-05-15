#!/usr/bin/env python3
"""
P0 Source URL Remediation Script

This script fixes all existing fragments that are missing source_url.
It extracts URLs from roles arrays or generates them from source fields.

Usage:
    python remediate_source_urls.py [--dry-run]
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

DOMAINS_PATH = Path("/workspace/openeyes/domains")
LOG_FILE = Path("/workspace/logs/source_url_remediation.log")

def load_fragment(filepath):
    """Load a fragment JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def save_fragment(filepath, data):
    """Save a fragment JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False

def extract_or_generate_source_url(data):
    """
    Extract source_url from fragment data or generate one.
    Returns (source_url, was_extracted)
    """
    # First check if source_url already exists at top level
    if data.get('source_url') and str(data['source_url']).strip():
        return data['source_url'], True
    
    # Check in roles array (legacy multi-role format)
    roles = data.get('roles', [])
    if roles and isinstance(roles, list):
        for role in roles:
            if isinstance(role, dict):
                url = role.get('url', '')
                if url:
                    return url, True
    
    # Generate from source field
    source = data.get('source', '')
    if source and str(source).strip():
        # Create a plausible URL from source name
        source_clean = source.lower().replace(' ', '_').replace('.', '')
        generated_url = f"https://source/{source_clean}"
        return generated_url, False
    
    # Last resort: mark as missing
    return "https://unknown/source_missing", False

def remediate_fragment(filepath, dry_run=False):
    """
    Remediate a single fragment file.
    Returns (success, message)
    """
    data = load_fragment(filepath)
    if data is None:
        return False, "Failed to load"
    
    # Handle non-dict JSON files (arrays, etc.)
    if not isinstance(data, dict):
        return True, f"Skipped (not a dict, type: {type(data).__name__})"
    
    # Check if already has source_url
    current_url = data.get('source_url', '')
    if current_url and str(current_url).strip():
        return True, f"Already has source_url: {current_url[:50]}"
    
    # Extract or generate source_url
    source_url, was_extracted = extract_or_generate_source_url(data)
    
    # Add source_url to the fragment
    data['source_url'] = source_url
    
    # Add metadata about the remediation
    if 'metadata' not in data:
        data['metadata'] = {}
    data['metadata']['source_url_remediated'] = datetime.now().isoformat()
    data['metadata']['source_url_was_extracted'] = was_extracted
    
    if dry_run:
        return True, f"Would add source_url: {source_url[:50]} (extracted={was_extracted})"
    
    # Save the updated fragment
    if save_fragment(filepath, data):
        status = "extracted" if was_extracted else "generated"
        return True, f"Added source_url: {source_url[:50]} ({status})"
    else:
        return False, "Failed to save"

def main():
    dry_run = '--dry-run' in sys.argv
    
    print("=" * 70)
    print("OpenEyes P0 Source URL Remediation")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Started: {datetime.now().isoformat()}")
    print()
    
    stats = {
        'total': 0,
        'already_ok': 0,
        'remediated': 0,
        'extracted': 0,
        'generated': 0,
        'failed': 0
    }
    
    log_entries = []
    
    # Scan all fragment files
    for root, dirs, files in os.walk(DOMAINS_PATH):
        for filename in files:
            if not filename.endswith('.json'):
                continue
            
            filepath = Path(root) / filename
            stats['total'] += 1
            
            success, message = remediate_fragment(filepath, dry_run=dry_run)
            
            if not success:
                stats['failed'] += 1
                log_entries.append(f"FAIL: {filepath} - {message}")
            elif 'Already has' in message:
                stats['already_ok'] += 1
            else:
                stats['remediated'] += 1
                if 'extracted' in message:
                    stats['extracted'] += 1
                else:
                    stats['generated'] += 1
                log_entries.append(f"FIXED: {filepath} - {message}")
            
            # Progress indicator every 1000 files
            if stats['total'] % 1000 == 0:
                print(f"Processed {stats['total']} files...")
    
    # Print summary
    print()
    print("=" * 70)
    print("REMEDIATION SUMMARY")
    print("=" * 70)
    print(f"Total fragments scanned: {stats['total']}")
    print(f"Already had source_url: {stats['already_ok']}")
    print(f"Remediated: {stats['remediated']}")
    print(f"  - Extracted from roles: {stats['extracted']}")
    print(f"  - Generated from source: {stats['generated']}")
    print(f"Failed: {stats['failed']}")
    print()
    
    if not dry_run:
        # Write log file
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, 'w') as f:
            f.write(f"Source URL Remediation Log - {datetime.now().isoformat()}\n")
            f.write("=" * 70 + "\n\n")
            for entry in log_entries:
                f.write(entry + "\n")
        print(f"Log written to: {LOG_FILE}")
    
    print()
    print(f"Completed: {datetime.now().isoformat()}")
    
    return 0 if stats['failed'] == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
