"""
Real-Time Fragment Update Scheduler
Enables incremental updates from primary sources with scheduling support.
"""

import json
import os
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib


class FragmentUpdateScheduler:
    """
    Manages real-time fragment updates from primary sources.
    
    Features:
    - Incremental updates (only fetch changed content)
    - Scheduled daemon mode
    - Source-based prioritization
    - Change detection via content hashing
    """
    
    def __init__(
        self,
        domains_path: str = "domains",
        domain_rules_path: str = "domain_rules"
    ):
        self.domains_path = domains_path
        self.domain_rules_path = domain_rules_path
        self.domain_configs = self._load_domain_configs()
        self.update_log_path = "data/update_log.json"
        self.update_log = self._load_update_log()
    
    def _load_domain_configs(self) -> Dict:
        """Load domain configurations."""
        configs = {}
        if not os.path.exists(self.domain_rules_path):
            return configs
        
        for filename in os.listdir(self.domain_rules_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.domain_rules_path, filename)
                try:
                    with open(filepath, 'r') as f:
                        config = json.load(f)
                        code = config.get('code', '').lower()
                        if code:
                            configs[code] = config
                except (json.JSONDecodeError, IOError):
                    continue
        return configs
    
    def _load_update_log(self) -> Dict:
        """Load update history log."""
        if os.path.exists(self.update_log_path):
            try:
                with open(self.update_log_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"updates": [], "last_full_scan": None}
    
    def _save_update_log(self):
        """Save update history log."""
        os.makedirs(os.path.dirname(self.update_log_path), exist_ok=True)
        with open(self.update_log_path, 'w') as f:
            json.dump(self.update_log, f, indent=2)
    
    def _calculate_content_hash(self, fragment: Dict) -> str:
        """Calculate hash of fragment content for change detection."""
        content = json.dumps({
            'definition': fragment.get('definition', ''),
            'counter_argument': fragment.get('counter_argument', ''),
            'latest_data': fragment.get('latest_data', ''),
            'source_url': fragment.get('source_url', ''),
            'year': fragment.get('year')
        }, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_fragment_last_updated(self, fragment: Dict) -> Optional[datetime]:
        """Get last update timestamp for a fragment."""
        fragment_id = fragment.get('id')
        if not fragment_id:
            return None
        
        for update in self.update_log.get('updates', []):
            if update.get('fragment_id') == fragment_id:
                return datetime.fromisoformat(update['timestamp'])
        
        # Check file modification time as fallback
        return None
    
    def needs_update(self, fragment: Dict, max_age_days: int = 30) -> bool:
        """
        Check if a fragment needs updating.
        
        Criteria:
        - Never updated before
        - Older than max_age_days
        - Source has newer content (detected via hash change)
        """
        last_updated = self.get_fragment_last_updated(fragment)
        
        if not last_updated:
            return True
        
        age = datetime.now() - last_updated
        if age.days > max_age_days:
            return True
        
        # Check if content hash has changed (would require fetching)
        # This is a placeholder for actual source checking
        current_hash = self._calculate_content_hash(fragment)
        stored_hash = None
        
        for update in self.update_log.get('updates', []):
            if update.get('fragment_id') == fragment.get('id'):
                stored_hash = update.get('content_hash')
                break
        
        if stored_hash and stored_hash != current_hash:
            return True
        
        return False
    
    def get_priority_sectors(self, domain_code: str) -> List[str]:
        """
        Get sectors prioritized for updates based on risk tier and recency rules.
        """
        config = self.domain_configs.get(domain_code, {})
        rules = config.get('fragment_rules', {})
        recency_cap = rules.get('recency_cap_years', 5)
        risk_tier = config.get('risk_tier', 'medium')
        
        # Critical domains need more frequent updates
        if risk_tier == 'critical':
            priority_multiplier = 0.5  # Half the age threshold
        elif risk_tier == 'high':
            priority_multiplier = 0.75
        else:
            priority_multiplier = 1.0
        
        priority_sectors = []
        for sector in config.get('sectors', []):
            sector_code = sector.get('code', '').lower()
            priority_sectors.append(sector_code)
        
        return priority_sectors
    
    def scan_for_updates(
        self,
        domain_code: Optional[str] = None,
        incremental: bool = True
    ) -> Dict:
        """
        Scan fragments for needed updates.
        
        Args:
            domain_code: Specific domain to scan (None = all)
            incremental: Only check fragments due for update
        
        Returns:
            Dictionary with update candidates
        """
        update_candidates = []
        total_fragments = 0
        
        domains_to_scan = [domain_code] if domain_code else list(self.domain_configs.keys())
        
        for domain in domains_to_scan:
            domain_path = os.path.join(self.domains_path, domain)
            if not os.path.exists(domain_path):
                continue
            
            config = self.domain_configs.get(domain, {})
            rules = config.get('fragment_rules', {})
            recency_cap = rules.get('recency_cap_years', 5)
            max_age_days = min(recency_cap * 30, 90)  # Cap at 90 days for critical
            
            for sector_code in os.listdir(domain_path):
                sector_path = os.path.join(domain_path, sector_code)
                if not os.path.isdir(sector_path):
                    continue
                
                for filename in os.listdir(sector_path):
                    if not filename.endswith('.json'):
                        continue
                    
                    total_fragments += 1
                    filepath = os.path.join(sector_path, filename)
                    
                    try:
                        with open(filepath, 'r') as f:
                            fragment = json.load(f)
                        
                        if incremental and not self.needs_update(fragment, max_age_days):
                            continue
                        
                        update_candidates.append({
                            'fragment_id': fragment.get('id'),
                            'domain': domain,
                            'sector': sector_code,
                            'filepath': filepath,
                            'last_updated': str(self.get_fragment_last_updated(fragment)) if self.get_fragment_last_updated(fragment) else None,
                            'priority': 'high' if config.get('risk_tier') == 'critical' else 'medium'
                        })
                    
                    except (json.JSONDecodeError, IOError):
                        continue
        
        # Sort by priority
        update_candidates.sort(
            key=lambda x: (0 if x['priority'] == 'high' else 1, x['fragment_id'] or '')
        )
        
        return {
            'total_fragments_scanned': total_fragments,
            'update_candidates': update_candidates,
            'candidates_count': len(update_candidates),
            'scan_timestamp': datetime.now().isoformat()
        }
    
    def log_update(self, fragment_id: str, domain: str, sector: str, changes: Dict):
        """Log a fragment update."""
        update_entry = {
            'fragment_id': fragment_id,
            'domain': domain,
            'sector': sector,
            'timestamp': datetime.now().isoformat(),
            'changes': changes,
            'content_hash': changes.get('new_hash')
        }
        
        self.update_log['updates'].append(update_entry)
        
        # Keep only last 10000 updates
        if len(self.update_log['updates']) > 10000:
            self.update_log['updates'] = self.update_log['updates'][-10000:]
        
        self._save_update_log()
    
    def run_scheduled_update(
        self,
        domain_code: Optional[str] = None,
        incremental: bool = True,
        dry_run: bool = True
    ) -> Dict:
        """
        Run a scheduled update cycle.
        
        Args:
            domain_code: Specific domain to update
            incremental: Only update fragments due for refresh
            dry_run: Don't actually fetch, just report what would be updated
        
        Returns:
            Update summary
        """
        print(f"OpenEyes Fragment Update Scheduler")
        print(f"Mode: {'Incremental' if incremental else 'Full'} / {'Dry Run' if dry_run else 'Live'}")
        print("=" * 60)
        
        scan_result = self.scan_for_updates(domain_code, incremental)
        
        print(f"\nScan Results:")
        print(f"  Fragments scanned: {scan_result['total_fragments_scanned']}")
        print(f"  Candidates for update: {scan_result['candidates_count']}")
        
        if scan_result['candidates_count'] > 0:
            print(f"\nTop Priority Updates:")
            for candidate in scan_result['update_candidates'][:10]:
                print(f"  - {candidate['fragment_id']} ({candidate['domain']}/{candidate['sector']})")
                print(f"    Last updated: {candidate['last_updated'] or 'Never'}")
                print(f"    Priority: {candidate['priority']}")
        
        if not dry_run and scan_result['candidates_count'] > 0:
            print(f"\n[TODO: Integrate with swarm scrapers to fetch updates]")
            print(f"Call swarm runners with --incremental flag for each candidate")
        
        # Update last scan time
        self.update_log['last_full_scan'] = datetime.now().isoformat()
        self._save_update_log()
        
        return scan_result


def main():
    parser = argparse.ArgumentParser(description='OpenEyes Fragment Update Scheduler')
    parser.add_argument('--domain', type=str, help='Specific domain to update')
    parser.add_argument('--incremental', action='store_true', default=True,
                       help='Only update fragments due for refresh')
    parser.add_argument('--full', action='store_true',
                       help='Full update scan (ignore timestamps)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Preview updates without fetching')
    parser.add_argument('--live', action='store_true',
                       help='Actually perform updates (not implemented)')
    
    args = parser.parse_args()
    
    scheduler = FragmentUpdateScheduler()
    scheduler.run_scheduled_update(
        domain_code=args.domain,
        incremental=not args.full,
        dry_run=not args.live
    )


if __name__ == "__main__":
    main()
