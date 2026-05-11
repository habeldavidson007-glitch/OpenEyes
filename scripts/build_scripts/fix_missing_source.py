#!/usr/bin/env python3
"""
Fix all fragments missing required 'source' field.
Adds source based on domain/sector if missing.
"""

import json
from pathlib import Path

def fix_missing_source():
    """Add missing source field to all fragments."""
    fragments_path = Path('openeyes/fragment_library/fragments')
    fixed_count = 0
    
    for fpath in fragments_path.glob('*.json'):
        try:
            data = json.loads(fpath.read_text())
            
            # Skip if source already exists
            if 'source' in data and data['source']:
                continue
            
            # Determine appropriate source based on domain/sector
            domain = data.get('domain', '')
            subdomain = data.get('subdomain', '')
            sector = data.get('sector', '')
            source_url = data.get('source_url', '')
            
            # Default source based on domain
            if domain == 'healthcare':
                if subdomain == 'MED' or sector == 'MED':
                    data['source'] = 'PubMed'
                elif subdomain == 'PH' or sector == 'PH':
                    data['source'] = 'CDC'
                elif subdomain == 'PHR' or sector == 'PHR':
                    data['source'] = 'FDA'
                elif subdomain == 'MH' or sector == 'MH':
                    data['source'] = 'NIMH'
                else:
                    data['source'] = 'NIH'
            elif domain == 'economy':
                if subdomain == 'FIN' or sector == 'FIN':
                    data['source'] = 'SEC'
                elif subdomain == 'MAC' or sector == 'MAC':
                    data['source'] = 'Federal Reserve'
                elif subdomain == 'REG' or sector == 'REG':
                    data['source'] = 'SEC'
                elif subdomain == 'ENR' or sector == 'ENR':
                    data['source'] = 'EIA'
                elif subdomain == 'COM' or sector == 'COM':
                    data['source'] = 'CME'
                elif subdomain == 'GEO' or sector == 'GEO':
                    data['source'] = 'IMF'
                else:
                    data['source'] = 'Bureau of Economic Analysis'
            else:
                data['source'] = 'Primary Source'
            
            # Write back
            fpath.write_text(json.dumps(data, indent=2))
            fixed_count += 1
            
        except Exception as e:
            print(f'Error processing {fpath.name}: {e}')
    
    print(f'Fixed {fixed_count} fragments with missing source field')
    return fixed_count

if __name__ == '__main__':
    fix_missing_source()
