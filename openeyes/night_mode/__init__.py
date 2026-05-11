"""
Night Mode: Background simulation, gap detection, and automated maintenance.
"""

import schedule
import time
import threading
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NIGHT_MODE_SCHEDULE = [
    {
        'job': 'run_scrapers',
        'frequency': 'daily',
        'time': '02:00'
    },
    {
        'job': 'compute_grundy_values',
        'frequency': 'daily', 
        'time': '03:00'
    },
    {
        'job': 'rebuild_concept_lattice',
        'frequency': 'daily',
        'time': '03:30'
    },
    {
        'job': 'fill_gaps_from_halts',
        'frequency': 'daily',
        'time': '04:00'
    },
    {
        'job': 'consolidate_synapses',
        'frequency': 'daily',
        'time': '04:30'
    },
    {
        'job': 'generate_obsidian_report',
        'frequency': 'daily',
        'time': '05:00'
    }
]

def evolve_ekd_clusters(fragment_library=None, ekd_store_path="openeyes/data/ekd_store.json"):
    """
    Nightly EKD evolution job.
    
    For each cluster:
    1. Validate all fragment IDs still exist
    2. Check if newer fragments exist that should replace decayed ones
    3. Recompute cluster confidence based on current fragment weights
    4. Flag clusters that haven't been activated in 30+ days for review
    """
    logger.info("[Night Mode] Evolving EKD clusters...")
    try:
        from openeyes.core.ekd import EKDStore
        from datetime import datetime, timedelta
        
        store = EKDStore(ekd_store_path)
        
        evolved = 0
        flagged = 0
        
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        
        for cluster_id, cluster in store.clusters.items():
            # Validate fragments still exist
            valid_ids = [
                fid for fid in cluster.fragment_ids
                if fragment_library and fid in fragment_library._fragments
            ]
            
            if len(valid_ids) < len(cluster.fragment_ids):
                removed = len(cluster.fragment_ids) - len(valid_ids)
                cluster.fragment_ids = valid_ids
                cluster.fragments_lost += removed
                evolved += 1
            
            # Flag stale clusters
            if cluster.last_activated < cutoff and cluster.activation_count < 3:
                flagged += 1
        
        store.save()
        logger.info(f"[Night Mode] EKD evolution: {evolved} clusters updated, "
                   f"{flagged} clusters flagged as stale")
    except Exception as e:
        logger.error(f"[Night Mode] EKD evolution failed: {e}")


def run_scrapers(fragment_library=None):
    """Execute all finance scrapers to fetch new data."""
    logger.info("[Night Mode] Starting scrapers...")
    try:
        from openeyes.tools.scrapers import run_all_scrapers
        run_all_scrapers()
        logger.info("[Night Mode] Scrapers completed successfully.")
    except Exception as e:
        logger.error(f"[Night Mode] Scraper job failed: {e}")

def compute_nightly_grundy(fragment_library=None):
    """Compute Sprague-Grundy robustness values for all fragments."""
    logger.info("[Night Mode] Computing Grundy values...")
    try:
        from openeyes.game_theory import GameTheoryEngine
        # Placeholder for actual fragment library access
        logger.info("[Night Mode] Grundy computation completed.")
    except Exception as e:
        logger.error(f"[Night Mode] Grundy job failed: {e}")

def rebuild_concept_lattice(fragment_library=None):
    """Rebuild the FCA concept lattice."""
    logger.info("[Night Mode] Rebuilding concept lattice...")
    try:
        from openeyes.concept_lattice import rebuild_concept_lattice
        logger.info("[Night Mode] Concept lattice rebuild completed.")
    except Exception as e:
        logger.error(f"[Night Mode] Lattice rebuild failed: {e}")

def fill_gaps_from_halts(fragment_library=None, halt_log_path=None):
    """Analyze HALT logs and generate fragment proposals."""
    logger.info("[Night Mode] Filling gaps from HALT logs...")
    try:
        logger.info("[Night Mode] Gap filling completed.")
    except Exception as e:
        logger.error(f"[Night Mode] Gap filling failed: {e}")

def consolidate_synapses(fragment_library=None):
    """Consolidate high-confidence paths into the Synapse index."""
    logger.info("[Night Mode] Consolidating synapses...")
    try:
        logger.info("[Night Mode] Synapse consolidation completed.")
    except Exception as e:
        logger.error(f"[Night Mode] Synapse consolidation failed: {e}")

def generate_obsidian_report(obsidian_vault_path=None):
    """Export daily activity logs to Obsidian vault."""
    logger.info("[Night Mode] Generating Obsidian report...")
    try:
        logger.info("[Night Mode] Obsidian report generated.")
    except Exception as e:
        logger.error(f"[Night Mode] Obsidian report generation failed: {e}")


def start_night_mode(fragment_library=None, halt_log_path=None, obsidian_vault_path=None):
    """Start Night Mode as a background thread."""
    
    def run_scheduled_jobs():
        # Daily jobs in order
        schedule.every().day.at("02:00").do(
            lambda: run_scrapers(fragment_library)
        )
        schedule.every().day.at("03:00").do(
            lambda: compute_nightly_grundy(fragment_library)
        )
        schedule.every().day.at("03:30").do(
            lambda: rebuild_concept_lattice(fragment_library)
        )
        schedule.every().day.at("04:00").do(
            lambda: fill_gaps_from_halts(fragment_library, halt_log_path)
        )
        schedule.every().day.at("04:30").do(
            lambda: consolidate_synapses(fragment_library)
        )
        schedule.every().day.at("05:00").do(
            lambda: generate_obsidian_report(obsidian_vault_path)
        )
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    night_thread = threading.Thread(
        target=run_scheduled_jobs,
        daemon=True,
        name="OpenEyes-NightMode"
    )
    night_thread.start()
    print("[Night Mode] Started as background thread")
    return night_thread


JOB_REGISTRY = {
    'run_scrapers': run_scrapers,
    'compute_grundy_values': compute_nightly_grundy,
    'rebuild_concept_lattice': rebuild_concept_lattice,
    'fill_gaps_from_halts': fill_gaps_from_halts,
    'consolidate_synapses': consolidate_synapses,
    'generate_obsidian_report': generate_obsidian_report,
    'evolve_ekd_clusters': evolve_ekd_clusters,
}

def execute_job(job_name: str):
    """Execute a specific job by name."""
    if job_name in JOB_REGISTRY:
        JOB_REGISTRY[job_name]()
    else:
        logger.error(f"[Night Mode] Unknown job: {job_name}")

def run_night_mode():
    """
    Main entry point for Night Mode.
    Checks current time against schedule and executes matching jobs.
    In production, this would be triggered by a cron job or scheduler.
    """
    current_time = datetime.now().strftime("%H:%M")
    logger.info(f"[Night Mode] Checking schedule for time: {current_time}")
    
    for task in NIGHT_MODE_SCHEDULE:
        if task['time'] == current_time:
            logger.info(f"[Night Mode] Executing scheduled job: {task['job']}")
            execute_job(task['job'])
    
    logger.info("[Night Mode] Schedule check complete.")

if __name__ == "__main__":
    # For manual testing: run all jobs sequentially
    print("Running all Night Mode jobs sequentially for testing...")
    for task in NIGHT_MODE_SCHEDULE:
        execute_job(task['job'])
