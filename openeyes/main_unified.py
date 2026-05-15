"""
OpenEyes Entry Point - Fully Migrated to Unified Architecture
-------------------------------------------------------------
This is the new single entry point replacing legacy main.py.
It initializes the Unified Orchestrator and Quality Assessor.
"""

import asyncio
import logging
from openeyes.core.migration_manager import get_unified_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenEyesAgent:
    def __init__(self, domains_path: str = "openeyes/domains"):
        logger.info("🚀 Initializing OpenEyes with Unified Architecture...")
        
        # Get the new unified system components
        system = get_unified_system(domains_path)
        self.orchestrator = system["orchestrator"]
        self.assessor = system["assessor"]
        self.migrator = system["migrator"]
        
        logger.info("✅ System Ready: Unified Orchestrator + Quality Assessor Active")
    
    async def ask(self, query: str, domain: str = "general") -> dict:
        """
        Main query interface.
        Automatically handles routing, retrieval, live fetch fallback, 
        and confidence scoring.
        """
        logger.info(f"Processing query: '{query}' (Domain: {domain})")
        
        # Use the unified orchestrator for everything
        result = await self.orchestrator.process_query(query, domain)
        
        # Enrich with quality assessment if not already done
        if 'credibility_score' not in result:
            assessment = self.assessor.evaluate_fragment(result)
            result.update(assessment)
        
        return result

# CLI Entry Point
if __name__ == "__main__":
    agent = OpenEyesAgent()
    
    # Example usage
    test_query = "What are the latest trends in renewable energy investment?"
    
    print(f"\n🔍 Query: {test_query}")
    response = asyncio.run(agent.ask(test_query, domain="investment"))
    
    print(f"\n✅ Answer: {response.get('answer', 'No answer generated')}")
    print(f"📊 Confidence: {response.get('confidence_score', 0):.2f}")
    print(f"🛡️  Credibility: {response.get('credibility_score', 'UNKNOWN')}")
    print(f"📚 Sources: {len(response.get('sources', []))} fragments used")
