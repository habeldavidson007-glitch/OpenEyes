#!/usr/bin/env python3
"""
Migrate healthcare fragments from nested format to flat Fragment format.

Healthcare files currently have structure:
{
  "domain": "healthcare",
  "subdomain": "MED",
  "sector": "MED",
  "topic": "...",
  "fragments": [
    {"role": "definition", "content": "...", "tags": [...], "source": "...", ...},
    ...
  ]
}

Need to convert to flat format matching economy fragments:
{
  "id": "frag_med_topic_role_001",
  "domain": "healthcare",
  "subdomain": "MED",
  "sector": "MED",
  "tags": [...],
  "reasoning_role": "definition",
  "content": "...",
  "source": "...",
  "source_url": "...",
  "credibility_class": "...",
  "year": 2024,
  ...
}
"""

import json
from pathlib import Path
import re

def slugify(text):
    """Convert text to slug format."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text.strip())
    return text.strip('_')

def migrate_healthcare_fragments():
    """Migrate all healthcare fragments to flat format."""
    healthcare_path = Path('healthcare')
    output_path = Path('openeyes/fragment_library/fragments_healthcare')
    output_path.mkdir(parents=True, exist_ok=True)
    
    migrated_count = 0
    fragment_counter = 1
    
    for hc_file in healthcare_path.glob('**/*.json'):
        try:
            data = json.loads(hc_file.read_text())
            
            domain = data.get('domain', 'healthcare')
            subdomain = data.get('subdomain', 'MED')
            sector = data.get('sector', subdomain)
            topic = data.get('topic', 'unknown')
            topic_slug = slugify(topic)
            
            fragments = data.get('fragments', [])
            
            for frag in fragments:
                role = frag.get('role', 'definition')
                content = frag.get('content', '')
                tags = frag.get('tags', [])
                source = frag.get('source', '')
                credibility_class = frag.get('credibility_class', 'A')
                year = frag.get('year', 2024)
                
                # Extract URL from source if it's a URL, otherwise use as source name
                source_url = source if source.startswith('http') else ''
                source_name = source if not source.startswith('http') else 'PubMed'
                
                # Create flat fragment
                flat_fragment = {
                    'id': f'frag_{subdomain.lower()}_{topic_slug}_{role}_{fragment_counter:04d}',
                    'domain': domain,
                    'subdomain': subdomain,
                    'sector': sector,
                    'tags': tags,
                    'reasoning_role': role,
                    'content': content,
                    'source': source_name,
                    'source_url': source_url,
                    'credibility_class': credibility_class,
                    'year': year,
                    'compatible_with': [],
                    'incompatible_with': [],
                    'weight': 1.0
                }
                
                # Write individual file
                output_file = output_path / f'{flat_fragment["id"]}.json'
                output_file.write_text(json.dumps(flat_fragment, indent=2))
                
                migrated_count += 1
                fragment_counter += 1
                
        except Exception as e:
            print(f'Error processing {hc_file}: {e}')
    
    print(f'Migrated {migrated_count} healthcare fragments to {output_path}')
    return migrated_count

if __name__ == '__main__':
    migrate_healthcare_fragments()
