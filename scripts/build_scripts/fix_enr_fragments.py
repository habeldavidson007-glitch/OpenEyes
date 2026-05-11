#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

fragments_dir = Path('/workspace/openeyes/fragment_library/fragments')

# Find all ENR fragments and fix schema
fixed = 0
for fpath in fragments_dir.glob('frag_eco_ENR_*.json'):
    try:
        data = json.loads(fpath.read_text())
        
        # Remove fields not in schema
        data.pop('grundy_value', None)
        data.pop('robustness_status', None)
        
        # Ensure required fields exist
        if 'last_verified' not in data:
            data['last_verified'] = datetime.now().strftime("%Y-%m-%d")
        
        # Write back
        fpath.write_text(json.dumps(data, indent=2))
        fixed += 1
    except Exception as e:
        print(f"Error on {fpath.name}: {e}")

print(f"Fixed {fixed} ENR fragments")
