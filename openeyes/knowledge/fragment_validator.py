#!/usr/bin/env python3
"""
Fragment Directory Validator & Auto-Redirect System

Ensures all fragments are in correct Domain/Sector directories.
Automatically moves misfiled fragments on startup or when triggered.

Directory Structure:
/workspace/openeyes/knowledge/fragments/
├── gov/
│   ├── govt/  (Political Systems)
│   ├── leg/   (Legislation)
│   ├── jud/   (Judicial)
│   └── ...
├── eco/
│   ├── fin/   (Finance)
│   ├── mac/   (Macroeconomics)
│   └── ...
├── hc/
│   ├── med/   (Clinical Medicine)
│   ├── phr/   (Pharmaceuticals)
│   └── ...
└── eng/
    └── ...
"""

import os
import shutil
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dynamic path resolution based on package location
import openeyes
_package_dir = Path(openeyes.__file__).parent
BASE_DIR = _package_dir / 'knowledge' / 'fragments'
TEMP_DIR = _package_dir / 'knowledge' / 'fragments_temp'

# Valid domain codes
VALID_DOMAINS = {'gov', 'eco', 'hc', 'eng'}

# Valid sector codes by domain (lowercase for matching)
VALID_SECTORS = {
    'gov': {'gov', 'leg', 'jud', 'sub', 'ipl', 'int', 'sec', 'ele', 'gel'},
    'eco': {'fin', 'enr', 'com', 'mac', 'geo', 'reg'},
    'hc': {'med', 'ph', 'phr', 'mh'},
    'eng': {'mech', 'elec', 'civil', 'chem'}  # Example engineering sectors
}


def parse_fragment_filename(filename: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse fragment filename to extract domain and sector.
    Expected format: frag_{domain}_{sector}_{topic}_{role}_{num}.json
    
    Returns:
        (domain, sector) tuple or (None, None) if unparseable
    """
    if not filename.endswith('.json'):
        return None, None
    
    # Remove .json extension
    name = filename[:-5]
    
    # Split by underscore
    parts = name.split('_')
    
    # Must have at least: frag, domain, sector, topic, role, num
    if len(parts) < 6:
        return None, None
    
    # Check for 'frag' prefix
    if parts[0] != 'frag':
        return None, None
    
    domain = parts[1].lower()  # Normalize to lowercase
    sector = parts[2].lower()  # Normalize to lowercase
    
    # Validate domain
    if domain not in VALID_DOMAINS:
        logger.warning(f"Unknown domain '{domain}' in file: {filename}")
        return None, None
    
    # Validate sector for this domain
    if sector not in VALID_SECTORS.get(domain, set()):
        logger.warning(f"Unknown sector '{sector}' for domain '{domain}' in file: {filename}")
        # Still return it, but it might need special handling
        return domain, sector
    
    return domain, sector


def get_all_fragments(directory: Path) -> List[Path]:
    """Recursively find all JSON files in directory."""
    fragments = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                fragments.append(Path(root) / file)
    return fragments


def validate_and_redirect(dry_run: bool = False) -> Dict[str, int]:
    """
    Validate all fragments are in correct locations and move misfiled ones.
    
    Args:
        dry_run: If True, only report what would be moved without actually moving
        
    Returns:
        Dictionary with statistics about the operation
    """
    stats = {
        'total_found': 0,
        'correctly_placed': 0,
        'moved': 0,
        'errors': 0,
        'unknown_domain': 0
    }
    
    # Create temp directory if needed
    if not dry_run and TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    if not dry_run:
        TEMP_DIR.mkdir(exist_ok=True)
    
    # Step 1: Collect all fragments recursively
    logger.info("Scanning for all fragments...")
    all_fragments = get_all_fragments(BASE_DIR)
    stats['total_found'] = len(all_fragments)
    
    # Step 2: Consolidate to temp (flatten structure)
    logger.info(f"Consolidating {len(all_fragments)} fragments to temp...")
    for frag_path in all_fragments:
        if not dry_run:
            dest = TEMP_DIR / frag_path.name
            if frag_path != dest:
                shutil.move(str(frag_path), str(dest))
    
    # Step 3: Sort from temp into correct Domain/Sector structure
    logger.info("Sorting fragments into Domain/Sector hierarchy...")
    
    for temp_file in TEMP_DIR.iterdir():
        if not temp_file.name.endswith('.json'):
            continue
            
        domain, sector = parse_fragment_filename(temp_file.name)
        
        if domain is None:
            # Unparseable filename - move to unknown/misc
            logger.warning(f"Could not parse: {temp_file.name}, moving to unknown/misc")
            domain = 'unknown'
            sector = 'misc'
            stats['unknown_domain'] += 1
        else:
            # Check if already in correct location
            expected_path = BASE_DIR / domain / sector / temp_file.name
            # Note: Since we moved everything to temp, nothing is in correct location yet
            pass
        
        # Create target directory
        target_dir = BASE_DIR / domain / sector
        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Move file
            dest = target_dir / temp_file.name
            shutil.move(str(temp_file), str(dest))
        
        stats['moved'] += 1
    
    # Cleanup temp
    if not dry_run and TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    
    # Calculate correctly placed (those that didn't need moving from their original spot)
    # Since we moved everything, this is an estimate
    stats['correctly_placed'] = stats['total_found'] - stats['moved'] + stats['correctly_placed']
    
    return stats


def get_structure_report() -> str:
    """Generate a report of the current directory structure."""
    report = ["Fragment Directory Structure:", "=" * 40]
    
    if not BASE_DIR.exists():
        return "ERROR: Base directory does not exist!"
    
    total_frags = 0
    for domain in sorted(BASE_DIR.iterdir()):
        if not domain.is_dir():
            continue
            
        domain_total = 0
        sectors_info = []
        
        for sector in sorted(domain.iterdir()):
            if not sector.is_dir():
                continue
                
            frag_count = len(list(sector.glob('*.json')))
            domain_total += frag_count
            sectors_info.append(f"{sector.name}({frag_count})")
        
        total_frags += domain_total
        if sectors_info:
            report.append(f"  {domain.name}/ ({domain_total} frags)")
            report.append(f"    Sectors: {', '.join(sectors_info)}")
    
    report.append("=" * 40)
    report.append(f"TOTAL: {total_frags} fragments")
    
    return "\n".join(report)


def run_validation_on_startup():
    """
    Main entry point - called on OpenEyes startup.
    Validates structure and auto-corrects any misfiled fragments.
    """
    logger.info("Running fragment directory validation...")
    
    try:
        stats = validate_and_redirect(dry_run=False)
        
        logger.info(f"Validation complete:")
        logger.info(f"  Total fragments found: {stats['total_found']}")
        logger.info(f"  Fragments processed: {stats['moved']}")
        logger.info(f"  Unparseable files: {stats['unknown_domain']}")
        
        # Generate and log structure report
        report = get_structure_report()
        logger.info("\n" + report)
        
        return True
        
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        logger.info("DRY RUN MODE - No changes will be made")
        stats = validate_and_redirect(dry_run=True)
        print(get_structure_report())
    elif len(sys.argv) > 1 and sys.argv[1] == '--report':
        print(get_structure_report())
    else:
        success = run_validation_on_startup()
        sys.exit(0 if success else 1)
