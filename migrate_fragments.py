import json
from pathlib import Path

fragments_path = Path('openeyes/fragment_library/fragments')

fixed = 0
for fpath in fragments_path.glob('*.json'):
    changed = False
    try:
        d = json.loads(fpath.read_text())
        
        # Fix domain label
        if d.get('domain') == 'finance':
            d['domain'] = 'economy'
            changed = True
        
        # Fix missing reasoning_role
        if not d.get('reasoning_role'):
            # Infer from content or default to definition
            content = d.get('content', '').lower()
            if any(w in content for w in ['however', 'limitation', 'criticism', 'challenge', 'but', 'fails']):
                d['reasoning_role'] = 'counter_argument'
            elif any(w in content for w in ['recently', '2024', '2025', 'new', 'latest', 'updated']):
                d['reasoning_role'] = 'latest_data'
            else:
                d['reasoning_role'] = 'definition'
            changed = True
        
        # Fix missing subdomain for economy fragments
        if d.get('domain') == 'economy' and not d.get('subdomain'):
            tags = d.get('tags', [])
            if any(t in tags for t in ['crypto', 'bitcoin', 'ethereum', 'defi', 'blockchain']):
                d['subdomain'] = 'FIN'
            elif any(t in tags for t in ['inflation', 'gdp', 'fed', 'monetary_policy', 'employment']):
                d['subdomain'] = 'MAC'
            elif any(t in tags for t in ['regulation', 'sec', 'compliance', 'law']):
                d['subdomain'] = 'REG'
            elif any(t in tags for t in ['oil', 'energy', 'renewable', 'power']):
                d['subdomain'] = 'ENR'
            elif any(t in tags for t in ['gold', 'commodity', 'agriculture', 'metals']):
                d['subdomain'] = 'COM'
            elif any(t in tags for t in ['geopolitic', 'trade', 'tariff', 'sanction', 'forex']):
                d['subdomain'] = 'GEO'
            else:
                d['subdomain'] = 'FIN'  # Default to FIN for unclassified economy fragments
            changed = True
        
        # Fix missing subdomain for healthcare fragments
        if d.get('domain') == 'healthcare' and not d.get('subdomain'):
            d['subdomain'] = 'MED'
            changed = True
        
        if changed:
            fpath.write_text(json.dumps(d, indent=2))
            fixed += 1
    except Exception as e:
        print(f'Error on {fpath.name}: {e}')

print(f'Fixed {fixed} fragments')
