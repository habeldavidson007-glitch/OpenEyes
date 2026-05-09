#!/usr/bin/env python3
"""
Review Queue Interface for OpenEyes.
Provides a CLI to approve, reject, or edit fragment proposals from scrapers.
"""

import os
import json
import shutil
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configuration
REVIEW_QUEUE_DIR = Path(__file__).parent.parent / "fragment_library" / "review_queue"
FRAGMENTS_DIR = Path(__file__).parent.parent / "fragment_library" / "fragments"
REJECTED_DIR = Path(__file__).parent.parent / "fragment_library" / "rejected"
LOG_FILE = Path(__file__).parent / "logs" / "review_decisions.log"

# Ensure directories exist
REVIEW_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
FRAGMENTS_DIR.mkdir(parents=True, exist_ok=True)
REJECTED_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_pending_fragments():
    """List all pending fragment JSON files in the review queue."""
    if not REVIEW_QUEUE_DIR.exists():
        return []
    return sorted([f for f in REVIEW_QUEUE_DIR.iterdir() if f.suffix == '.json'])


def load_fragment(filepath):
    """Load and parse a fragment JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def display_fragment(fragment_data, filepath):
    """Pretty print fragment details for review."""
    print("\n" + "="*60)
    print(f"REVIEWING: {filepath.name}")
    print("="*60)
    print(f"ID:               {fragment_data.get('id', 'N/A')}")
    print(f"Domain:           {fragment_data.get('domain', 'N/A')}")
    print(f"Subdomain:        {fragment_data.get('subdomain', 'N/A')}")
    print(f"Tags:             {', '.join(fragment_data.get('tags', []))}")
    print(f"Reasoning Role:   {fragment_data.get('reasoning_role', 'N/A')}")
    print(f"Source:           {fragment_data.get('source', 'N/A')}")
    print(f"Source URL:       {fragment_data.get('source_url', 'N/A')}")
    print(f"Credibility:      {fragment_data.get('credibility_class', 'N/A')}")
    print(f"Year:             {fragment_data.get('year', 'N/A')}")
    print("-"*60)
    print("CONTENT:")
    print(fragment_data.get('content', 'No content'))
    print("="*60)


def approve_fragment(filepath):
    """Move fragment to main library and log decision."""
    try:
        dest = FRAGMENTS_DIR / filepath.name
        shutil.move(str(filepath), str(dest))
        logger.info(f"APPROVED: {filepath.name} -> {dest}")
        print(f"[OK] Fragment approved and moved to library: {dest}")
        
        # Trigger lattice rebuild if available
        try:
            from openeyes.concept_lattice import rebuild_concept_lattice
            from openeyes.fragment_library import FragmentLibrary
            lib = FragmentLibrary()
            stats = rebuild_concept_lattice(lib)
            if stats.get('status') == 'success':
                print(f"[FCA] Lattice updated: {stats['updated']} compatibilities, {stats['gaps_identified']} gaps")
        except Exception as e:
            print(f"[WARN] Could not trigger lattice rebuild: {e}")
            
        return True
    except Exception as e:
        logger.error(f"ERROR approving {filepath.name}: {e}")
        print(f"[ERROR] Failed to approve: {e}")
        return False


def reject_fragment(filepath, reason=""):
    """Move fragment to rejected archive and log decision."""
    try:
        dest = REJECTED_DIR / filepath.name
        shutil.move(str(filepath), str(dest))
        logger.info(f"REJECTED: {filepath.name} -> {dest}. Reason: {reason}")
        print(f"[OK] Fragment rejected and archived: {dest}")
        return True
    except Exception as e:
        logger.error(f"ERROR rejecting {filepath.name}: {e}")
        print(f"[ERROR] Failed to reject: {e}")
        return False


def edit_fragment(filepath):
    """Open fragment in system editor for manual changes."""
    try:
        editor = os.environ.get('EDITOR', 'nano')
        subprocess.run([editor, str(filepath)])
        print(f"[OK] Fragment edited. Please review again.")
        return True
    except Exception as e:
        logger.error(f"ERROR editing {filepath.name}: {e}")
        print(f"[ERROR] Failed to edit: {e}")
        return False


def review_loop():
    """Main interactive loop for reviewing fragments."""
    print("Starting OpenEyes Review Queue Interface...")
    print("Commands: [a]pprove, [r]eject, [e]dit, [s]kip, [q]uit")
    
    pending = get_pending_fragments()
    if not pending:
        print("No pending fragments in review queue.")
        return
    
    print(f"Found {len(pending)} pending fragment(s).")
    
    i = 0
    while i < len(pending):
        filepath = pending[i]
        
        # Reload in case it was edited
        try:
            fragment_data = load_fragment(filepath)
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON in {filepath.name}. Skipping.")
            i += 1
            continue
        
        display_fragment(fragment_data, filepath)
        
        while True:
            cmd = input("\nAction (a/r/e/s/q): ").strip().lower()
            
            if cmd in ['a', 'approve']:
                if approve_fragment(filepath):
                    pending.pop(i)  # Remove from list since it's moved
                else:
                    continue  # Stay on this fragment if move failed
                break
                
            elif cmd in ['r', 'reject']:
                reason = input("Rejection reason (optional): ").strip()
                if reject_fragment(filepath, reason):
                    pending.pop(i)
                else:
                    continue
                break
                
            elif cmd in ['e', 'edit']:
                edit_fragment(filepath)
                # Loop back to display again after edit
                continue
                
            elif cmd in ['s', 'skip']:
                print(f"Skipping {filepath.name}")
                i += 1
                break
                
            elif cmd in ['q', 'quit']:
                print("Exiting review session.")
                logger.info("SESSION ENDED by user")
                return
                
            else:
                print("Invalid command. Use: a (approve), r (reject), e (edit), s (skip), q (quit)")

    print("\nAll pending fragments processed.")
    logger.info("SESSION COMPLETED: All items processed")


if __name__ == "__main__":
    try:
        review_loop()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        logger.info("SESSION INTERRUPTED by Ctrl+C")
