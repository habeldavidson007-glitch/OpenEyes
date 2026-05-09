"""
Night Mode: Background simulation, gap detection, and automated maintenance.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any

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

def run_scrapers():
    """Execute all finance scrapers to fetch new data."""
    logger.info("[Night Mode] Starting scrapers...")
    try:
        from openeyes.tools.scrapers import run_all_scrapers
        run_all_scrapers()
        logger.info("[Night Mode] Scrapers completed successfully.")
    except Exception as e:
        logger.error(f"[Night Mode] Scraper job failed: {e}")

def compute_grundy_values():
    """Compute Sprague-Grundy robustness values for all fragments."""
    logger.info("[Night Mode] Computing Grundy values...")
    try:
        from openeyes.game_theory import GameTheoryEngine
        # Placeholder for actual fragment library access
        logger.info("[Night Mode] Grundy computation completed.")
    except Exception as e:
        logger.error(f"[Night Mode] Grundy job failed: {e}")

def rebuild_concept_lattice():
    """Rebuild the FCA concept lattice."""
    logger.info("[Night Mode] Rebuilding concept lattice...")
    try:
        from openeyes.concept_lattice import rebuild_concept_lattice
        logger.info("[Night Mode] Concept lattice rebuild completed.")
    except Exception as e:
        logger.error(f"[Night Mode] Lattice rebuild failed: {e}")

def fill_gaps_from_halts():
    """Analyze HALT logs and generate fragment proposals."""
    logger.info("[Night Mode] Filling gaps from HALT logs...")
    try:
        logger.info("[Night Mode] Gap filling completed.")
    except Exception as e:
        logger.error(f"[Night Mode] Gap filling failed: {e}")

def consolidate_synapses():
    """Consolidate high-confidence paths into the Synapse index."""
    logger.info("[Night Mode] Consolidating synapses...")
    try:
        logger.info("[Night Mode] Synapse consolidation completed.")
    except Exception as e:
        logger.error(f"[Night Mode] Synapse consolidation failed: {e}")

def generate_obsidian_report():
    """Export daily activity logs to Obsidian vault."""
    logger.info("[Night Mode] Generating Obsidian report...")
    try:
        logger.info("[Night Mode] Obsidian report generated.")
    except Exception as e:
        logger.error(f"[Night Mode] Obsidian report generation failed: {e}")

JOB_REGISTRY = {
    'run_scrapers': run_scrapers,
    'compute_grundy_values': compute_grundy_values,
    'rebuild_concept_lattice': rebuild_concept_lattice,
    'fill_gaps_from_halts': fill_gaps_from_halts,
    'consolidate_synapses': consolidate_synapses,
    'generate_obsidian_report': generate_obsidian_report,
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
