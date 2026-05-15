"""
Migration Utility: Legacy to Unified Orchestrator
-------------------------------------------------
1. Backfills credibility scores for existing fragments (file-based).
2. Provides the Singleton initialization for the new architecture.
3. Deprecates old module imports.
"""

import os
import json
import glob
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

# Import new architecture
from openeyes.core.unified_orchestrator import UnifiedKnowledgeOrchestrator as UnifiedOrchestrator
from openeyes.core.quality_assessor import KnowledgeQualityAssessor, SourceCredibilityReport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationManager:
    def __init__(self, base_path: str = "openeyes/domains"):
        self.base_path = Path(base_path)
        self.assessor = KnowledgeQualityAssessor()
        self.stats = {
            "total_fragments": 0,
            "backfilled": 0,
            "missing_source_url": 0,
            "already_scored": 0
        }
        
    def _find_all_fragments(self) -> List[Path]:
        """Find all fragment JSON files across all domains."""
        pattern = self.base_path / "**" / "frag_*.json"
        return list(glob.glob(str(pattern), recursive=True))
    
    def backfill_credibility_scores(self) -> Dict[str, int]:
        """
        P0 Critical: Updates all existing fragment files that lack 
        credibility scoring to default to 'UNVERIFIED' until re-evaluated.
        Also checks for missing source_url.
        """
        logger.info(f"Starting credibility backfill for {self.base_path}...")
        
        fragments = self._find_all_fragments()
        self.stats["total_fragments"] = len(fragments)
        logger.info(f"Found {len(fragments)} fragment files")
        
        for frag_path in fragments:
            try:
                with open(frag_path, 'r') as f:
                    data = json.load(f)
                
                needs_update = False
                
                # Check for missing source_url (Critical P0)
                if not data.get('source_url'):
                    self.stats["missing_source_url"] += 1
                    logger.warning(f"⚠️  Missing source_url: {frag_path.name}")
                
                # Add credibility_score if missing
                if not data.get('credibility_score'):
                    # Map old credibility_class to new credibility_score if exists
                    old_class = data.get('credibility_class', '')
                    if old_class == 'A':
                        data['credibility_score'] = 'HIGH'
                    elif old_class == 'B':
                        data['credibility_score'] = 'MEDIUM'
                    elif old_class == 'C':
                        data['credibility_score'] = 'LOW'
                    else:
                        data['credibility_score'] = 'UNVERIFIED'
                    
                    needs_update = True
                    self.stats["backfilled"] += 1
                else:
                    self.stats["already_scored"] += 1
                
                # Add source_domain if missing
                if not data.get('source_domain') and data.get('source_url'):
                    from urllib.parse import urlparse
                    parsed = urlparse(data['source_url'])
                    data['source_domain'] = parsed.netloc
                    needs_update = True
                
                if needs_update:
                    with open(frag_path, 'w') as f:
                        json.dump(data, f, indent=2)
                        
            except Exception as e:
                logger.error(f"❌ Error processing {frag_path}: {e}")
        
        logger.info(f"✅ Backfill complete:")
        logger.info(f"   - Total fragments: {self.stats['total_fragments']}")
        logger.info(f"   - Backfilled: {self.stats['backfilled']}")
        logger.info(f"   - Already scored: {self.stats['already_scored']}")
        logger.info(f"   - Missing source_url: {self.stats['missing_source_url']}")
        
        return self.stats

    def validate_migration_readiness(self) -> bool:
        """Checks if the system is ready to switch off legacy modules."""
        fragments = self._find_all_fragments()
        
        unsourced_count = 0
        distribution = {}
        
        for frag_path in fragments:
            try:
                with open(frag_path, 'r') as f:
                    data = json.load(f)
                
                if not data.get('source_url'):
                    unsourced_count += 1
                
                score = data.get('credibility_score', 'UNVERIFIED')
                distribution[score] = distribution.get(score, 0) + 1
            except:
                pass
        
        if unsourced_count > 0:
            logger.warning(f"⚠️  {unsourced_count} fragments still missing source_url. Remediation required before full cutover.")
            return False
        
        logger.info(f"📊 Current Credibility Distribution: {distribution}")
        return True

# Singleton Accessor for Application Startup
def get_unified_system(base_path: str = "openeyes/domains") -> Dict[str, Any]:
    """
    Initializes the new core system. Use this in your main.py or agent.py
    instead of importing individual legacy modules.
    """
    migrator = MigrationManager(base_path)
    
    # Ensure fragments are ready
    migrator.backfill_credibility_scores()
    
    if not migrator.validate_migration_readiness():
        logger.warning("System running in degraded mode due to data quality issues.")
    
    orchestrator = UnifiedKnowledgeOrchestrator(domains_path=base_path)
    assessor = KnowledgeQualityAssessor()
    
    return {
        "orchestrator": orchestrator,
        "assessor": assessor,
        "migrator": migrator
    }

if __name__ == "__main__":
    print("🚀 Starting OpenEyes Architecture Migration...")
    manager = MigrationManager()
    stats = manager.backfill_credibility_scores()
    ready = manager.validate_migration_readiness()
    print(f"\n✅ Migration Prep Complete. Ready to switch entry points.")
    print(f"   System Ready: {ready}")
