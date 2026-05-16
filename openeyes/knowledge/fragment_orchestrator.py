"""
Fragment Orchestrator: Auto-Redirect & Validation System

This module ensures all fragment files are in their correct domain directories.
It runs automatically on OpenEyes startup and performs:

1. VALIDATION: Check if fragments match their expected domain based on filename
2. AUTO-REDIRECT: Move misfiled fragments to correct directories
3. INDEXING: Load all fragments from canonical locations
4. REPORTING: Generate summary of actions taken

Naming Convention Enforcement:
- frag_gov_* → /workspace/openeyes/knowledge/fragments/gov/
- frag_hc_*  → /workspace/openeyes/knowledge/fragments/hc/
- frag_eco_* → /workspace/openeyes/knowledge/fragments/eco/
- frag_eng_* → /workspace/openeyes/knowledge/fragments/eng/
- frag_leg_* → /workspace/openeyes/knowledge/fragments/leg/
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class FragmentMove:
    """Record of a fragment file that was moved."""
    source_path: str
    dest_path: str
    reason: str
    domain_detected: str


class FragmentOrchestrator:
    """
    Manages fragment file organization and validation.
    
    Ensures fragments are stored in domain-appropriate directories
    and provides automatic correction when files are misplaced.
    """
    
    # Domain prefix to directory mapping
    DOMAIN_PREFIX_MAP = {
        'gov': 'gov',      # Governance
        'hc': 'hc',        # Healthcare
        'eco': 'eco',      # Economy
        'eng': 'eng',      # Engineering
        'leg': 'leg',      # Legal (if separate from gov)
    }
    
    def __init__(self):
        # Initialize paths dynamically based on package location
        import openeyes
        package_dir = Path(openeyes.__file__).parent
        self.FRAGMENTS_BASE = package_dir / 'knowledge' / 'fragments'
        self.LEGACY_LIBRARY = package_dir.parent / 'fragment_library' / 'fragments'
        
        self.moves_made: List[FragmentMove] = []
        self.errors: List[str] = []
        self.stats = {
            'total_scanned': 0,
            'correctly_placed': 0,
            'misfiled': 0,
            'moved': 0,
            'failed': 0,
            'legacy_migrated': 0,
        }
    
    def run_startup_check(self) -> bool:
        """
        Run complete startup validation and correction routine.
        
        Returns True if system is ready, False if critical errors exist.
        """
        print("=" * 70)
        print("FRAGMENT ORCHESTRATOR - Startup Validation")
        print("=" * 70)
        
        # Step 1: Ensure domain directories exist
        self._ensure_domain_directories()
        
        # Step 2: Migrate legacy fragments if they exist
        self._migrate_legacy_fragments()
        
        # Step 3: Validate and fix all existing fragments
        self._validate_and_fix_all_fragments()
        
        # Step 4: Report results
        self._print_summary()
        
        # Return success if no critical failures
        return len(self.errors) == 0
    
    def _ensure_domain_directories(self):
        """Create domain directories if they don't exist."""
        print("\n[STEP 1] Ensuring domain directories exist...")
        
        for domain in self.DOMAIN_PREFIX_MAP.values():
            dir_path = self.FRAGMENTS_BASE / domain
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✓ Created directory: {dir_path}")
            else:
                print(f"  ✓ Directory exists: {dir_path}")
    
    def _migrate_legacy_fragments(self):
        """Copy fragments from legacy library to new structure."""
        if not self.LEGACY_LIBRARY.exists():
            print("\n[STEP 2] No legacy library found, skipping migration.")
            return
        
        print(f"\n[STEP 2] Migrating legacy fragments from {self.LEGACY_LIBRARY}...")
        
        migrated_count = 0
        
        for json_file in self.LEGACY_LIBRARY.glob('*.json'):
            filename = json_file.name
            
            # Determine target domain from filename prefix
            target_domain = self._extract_domain_from_filename(filename)
            
            if not target_domain:
                continue  # Skip files without recognizable prefix
            
            target_dir = self.FRAGMENTS_BASE / target_domain
            target_path = target_dir / filename
            
            # Only copy if not already present
            if not target_path.exists():
                try:
                    shutil.copy2(json_file, target_path)
                    migrated_count += 1
                    
                    self.moves_made.append(FragmentMove(
                        source_path=str(json_file),
                        dest_path=str(target_path),
                        reason="Legacy migration",
                        domain_detected=target_domain
                    ))
                    
                except Exception as e:
                    self.errors.append(f"Failed to migrate {filename}: {e}")
                    self.stats['failed'] += 1
        
        print(f"  ✓ Migrated {migrated_count} legacy fragments")
        self.stats['legacy_migrated'] = migrated_count
    
    def _validate_and_fix_all_fragments(self):
        """Scan all fragments and move misfiled ones."""
        print("\n[STEP 3] Validating fragment placement...")
        
        # Scan all JSON files in fragments directory
        for json_file in self.FRAGMENTS_BASE.rglob('*.json'):
            # Skip domain_config.json and other metadata files
            if json_file.name in ['domain_config.json']:
                continue
            
            self.stats['total_scanned'] += 1
            
            filename = json_file.name
            current_parent = json_file.parent.name
            
            # Extract expected domain from filename
            expected_domain = self._extract_domain_from_filename(filename)
            
            if not expected_domain:
                # Can't determine domain from filename, check content
                expected_domain = self._infer_domain_from_content(json_file)
            
            if not expected_domain:
                self.errors.append(f"Cannot determine domain for: {filename}")
                self.stats['failed'] += 1
                continue
            
            # Check if file is in correct directory
            if current_parent == expected_domain:
                self.stats['correctly_placed'] += 1
                continue
            
            # File is misfiled - move it
            self.stats['misfiled'] += 1
            
            target_path = self.FRAGMENTS_BASE / expected_domain / filename
            
            # Handle potential naming conflicts
            if target_path.exists():
                # Files are identical - remove duplicate
                if self._files_identical(json_file, target_path):
                    try:
                        json_file.unlink()
                        print(f"  🗑 Removed duplicate: {filename}")
                        self.stats['moved'] += 1
                        continue
                    except Exception as e:
                        self.errors.append(f"Failed to remove duplicate {filename}: {e}")
                        continue
                else:
                    # Different content - generate unique name
                    target_path = self._generate_unique_path(target_path)
            
            # Move the file
            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(json_file), str(target_path))
                
                self.moves_made.append(FragmentMove(
                    source_path=str(json_file),
                    dest_path=str(target_path),
                    reason=f"Misfiled in {current_parent}/",
                    domain_detected=expected_domain
                ))
                
                self.stats['moved'] += 1
                print(f"  ↗ Moved: {filename} → {expected_domain}/")
                
            except Exception as e:
                self.errors.append(f"Failed to move {filename}: {e}")
                self.stats['failed'] += 1
    
    def _extract_domain_from_filename(self, filename: str) -> str | None:
        """Extract domain from fragment filename prefix."""
        # Pattern: frag_{domain}_{sector}_...
        if not filename.startswith('frag_'):
            return None
        
        parts = filename.replace('.json', '').split('_')
        
        if len(parts) >= 2:
            domain_prefix = parts[1].lower()
            
            # Map prefix to domain directory
            if domain_prefix in self.DOMAIN_PREFIX_MAP:
                return self.DOMAIN_PREFIX_MAP[domain_prefix]
            
            # Handle special cases
            if domain_prefix == 'jud':
                return 'gov'  # Judicial is part of governance
        
        return None
    
    def _infer_domain_from_content(self, filepath: Path) -> str | None:
        """Try to infer domain from fragment content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check for domain field
            domain = data.get('domain', '').lower()
            
            if domain in ['healthcare', 'hc']:
                return 'hc'
            elif domain in ['economy', 'eco']:
                return 'eco'
            elif domain in ['governance', 'gov']:
                return 'gov'
            elif domain in ['engineering', 'eng']:
                return 'eng'
            
        except Exception:
            pass
        
        return None
    
    def _files_identical(self, path1: Path, path2: Path) -> bool:
        """Check if two files have identical content."""
        try:
            with open(path1, 'rb') as f1, open(path2, 'rb') as f2:
                return f1.read() == f2.read()
        except Exception:
            return False
    
    def _generate_unique_path(self, base_path: Path) -> Path:
        """Generate a unique path by appending counter."""
        counter = 1
        stem = base_path.stem
        suffix = base_path.suffix
        parent = base_path.parent
        
        while True:
            new_path = parent / f"{stem}_v{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def _print_summary(self):
        """Print summary of orchestration results."""
        print("\n" + "=" * 70)
        print("ORCHESTRATION SUMMARY")
        print("=" * 70)
        
        print(f"\n📊 Statistics:")
        print(f"   Total fragments scanned: {self.stats['total_scanned']}")
        print(f"   Correctly placed:        {self.stats['correctly_placed']}")
        print(f"   Misfiled:                {self.stats['misfiled']}")
        print(f"   Successfully moved:      {self.stats['moved']}")
        print(f"   Legacy migrated:         {self.stats['legacy_migrated']}")
        print(f"   Failed:                  {self.stats['failed']}")
        
        if self.moves_made:
            print(f"\n📝 Recent Moves ({len(self.moves_made)} total):")
            for move in self.moves_made[:10]:  # Show first 10
                print(f"   • {Path(move.source_path).name}")
                print(f"     → {move.dest_path}")
                print(f"     Reason: {move.reason}")
            
            if len(self.moves_made) > 10:
                print(f"   ... and {len(self.moves_made) - 10} more moves")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors[:5]:  # Show first 5
                print(f"   • {error}")
            
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more errors")
        else:
            print("\n✅ No errors detected")
        
        print("\n" + "=" * 70)
        print("FRAGMENT ORCHESTRATOR - Complete")
        print("=" * 70)


def run_orchestrator() -> bool:
    """Convenience function to run orchestrator at startup."""
    orchestrator = FragmentOrchestrator()
    return orchestrator.run_startup_check()


if __name__ == '__main__':
    success = run_orchestrator()
    exit(0 if success else 1)
