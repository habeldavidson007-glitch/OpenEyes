"""
OpenEyes Swarm Integration Layer

Connects the Autonomous Signal-Pulse Swarm to the main query pipeline.
Allows queries to retrieve pre-computed data from the WAL buffer and known_hashes DB.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from openeyes.knowledge.fragments import Fragment


class SwarmRetrievalEngine:
    """
    Retrieves data from the autonomous swarm's WAL buffer and hash database.
    
    This enables zero-latency answers by accessing pre-computed, tokenized,
    and archived data from the swarm's active harvest cycles.
    """
    
    def __init__(self, wal_db_path: str = "wal_buffer.db", 
                 hashes_db_path: str = "known_hashes.db"):
        self.wal_db_path = Path(wal_db_path)
        self.hashes_db_path = Path(hashes_db_path)
        self._wal_conn: Optional[sqlite3.Connection] = None
        self._hash_conn: Optional[sqlite3.Connection] = None
    
    def _ensure_wal_initialized(self):
        """Ensure WAL database connection exists."""
        if self._wal_conn is None and self.wal_db_path.exists():
            self._wal_conn = sqlite3.connect(str(self.wal_db_path))
            self._wal_conn.row_factory = sqlite3.Row
    
    def _ensure_hashes_initialized(self):
        """Ensure hashes database connection exists."""
        if self._hash_conn is None and self.hashes_db_path.exists():
            self._hash_conn = sqlite3.connect(str(self.hashes_db_path))
            self._hash_conn.row_factory = sqlite3.Row
    
    def query_swarm_data(self, query: str, domain: str, limit: int = 10) -> List[Fragment]:
        """
        Query the swarm's WAL buffer for pre-harvested data.
        
        Args:
            query: User's query string
            domain: Domain code (eco, hc, gov, etc.)
            limit: Maximum number of fragments to return
            
        Returns:
            List of Fragment objects from swarm data
        """
        self._ensure_wal_initialized()
        
        if self._wal_conn is None:
            print(f"[SWARM_RETRIEVAL] WAL buffer not found at {self.wal_db_path}")
            return []
        
        try:
            # Build keyword search from query
            # Extract key terms: "bitcoin price" -> ["bitcoin", "price"]
            # "exchange rate" -> ["exchange", "rate"]
            import re
            query_terms = re.findall(r'\b\w+\b', query.lower())
            # Filter out common stop words
            stop_words = {'what', 'is', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'current', 'currently'}
            search_terms = [t for t in query_terms if t not in stop_words and len(t) > 2]
            
            if not search_terms:
                search_terms = query_terms  # Fallback to all terms
            
            # Build SQL WHERE clause with OR conditions for each term
            where_clauses = []
            params = []
            for term in search_terms[:5]:  # Limit to 5 terms max
                where_clauses.append("LOWER(content) LIKE ?")
                params.append(f"%{term}%")
            
            where_sql = " OR ".join(where_clauses) if where_clauses else "1=1"
            
            # CRITICAL FIX: Search WAL buffer using query keywords
            # Only get tokenized_content (high confidence) first, then new_content
            cursor = self._wal_conn.execute(f"""
                SELECT agent_id, timestamp, data_type, content, tokens_json
                FROM wal_buffer
                WHERE data_type = 'tokenized_content'
                AND ({where_sql})
                ORDER BY timestamp DESC
                LIMIT ?
            """, params + [limit])
            
            rows = cursor.fetchall()
            
            # If no tokenized results, try new_content as fallback
            if not rows:
                cursor = self._wal_conn.execute(f"""
                    SELECT agent_id, timestamp, data_type, content, tokens_json
                    FROM wal_buffer
                    WHERE data_type = 'new_content'
                    AND ({where_sql})
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, params + [limit])
                rows = cursor.fetchall()
            
            # If still no results, return latest data for economy/finance domain
            if not rows and domain.lower() in ['eco', 'economy', 'finance', 'financial']:
                # Get most recent price/exchange data regardless of query match
                cursor = self._wal_conn.execute("""
                    SELECT agent_id, timestamp, data_type, content, tokens_json
                    FROM wal_buffer
                    WHERE data_type = 'tokenized_content'
                    AND (LOWER(content) LIKE '%price%' OR LOWER(content) LIKE '%rate%' OR LOWER(content) LIKE '%usd%' OR LOWER(content) LIKE '%eur%')
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
            
            fragments = []
            
            for row in rows:
                tokens = json.loads(row['tokens_json']) if row['tokens_json'] else {}
                
                # Create fragment from swarm data
                fragment = Fragment(
                    claim=row['content'],
                    evidence=f"Swarm Agent: {row['agent_id']}",
                    limitations=[],
                    sub_questions=[],
                    source_url=tokens.get('source', ''),
                    published_on=row['timestamp'],
                    evidence_level='high' if row['data_type'] == 'tokenized_content' else 'moderate',
                    source_id=f"swarm_{row['agent_id']}"
                )
                
                # Add confidence score as a custom attribute (not in __init__)
                fragment.confidence_score = 0.85 if row['data_type'] == 'tokenized_content' else 0.70
                
                # Add swarm metadata
                fragment.swarm_metadata = {
                    'agent_id': row['agent_id'],
                    'data_type': row['data_type'],
                    'tokens': tokens,
                    'harvested_at': row['timestamp']
                }
                
                fragments.append(fragment)
            
            if fragments:
                print(f"[SWARM_RETRIEVAL] Found {len(fragments)} fragments from swarm WAL buffer for query '{query}'")
            else:
                print(f"[SWARM_RETRIEVAL] No matching fragments found for query '{query}' (searched terms: {search_terms})")
            
            return fragments
            
        except Exception as e:
            print(f"[SWARM_RETRIEVAL] Error querying WAL buffer: {e}")
            return []
    
    def get_recent_harvest_count(self, hours: int = 24) -> int:
        """Get count of items harvested in the last N hours."""
        self._ensure_wal_initialized()
        
        if self._wal_conn is None:
            return 0
        
        try:
            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            cursor = self._wal_conn.execute("""
                SELECT COUNT(*) FROM wal_buffer
                WHERE timestamp > ? AND processed = 0
            """, (cutoff,))
            
            count = cursor.fetchone()[0]
            print(f"[SWARM_RETRIEVAL] {count} items harvested in last {hours} hours")
            return count
            
        except Exception as e:
            print(f"[SWARM_RETRIEVAL] Error counting harvests: {e}")
            return 0
    
    def mark_as_retrieved(self, agent_ids: List[str]):
        """Mark WAL entries as processed/retrieved."""
        self._ensure_wal_initialized()
        
        if self._wal_conn is None or not agent_ids:
            return
        
        try:
            # Mark all entries from these agents as processed
            for agent_id in agent_ids:
                self._wal_conn.execute("""
                    UPDATE wal_buffer SET processed = 1
                    WHERE agent_id = ? AND processed = 0
                """, (agent_id,))
            
            self._wal_conn.commit()
            
        except Exception as e:
            print(f"[SWARM_RETRIEVAL] Error marking as retrieved: {e}")
    
    def get_known_hash_count(self) -> int:
        """Get total number of unique hashes in swarm memory."""
        self._ensure_hashes_initialized()
        
        if self._hash_conn is None:
            # Try to estimate from WAL buffer instead
            self._ensure_wal_initialized()
            if self._wal_conn:
                try:
                    cursor = self._wal_conn.execute("""
                        SELECT COUNT(DISTINCT tokens_json) FROM wal_buffer
                        WHERE tokens_json IS NOT NULL
                    """)
                    return cursor.fetchone()[0]
                except:
                    pass
            return 0
        
        try:
            cursor = self._hash_conn.execute("SELECT COUNT(*) FROM known_hashes")
            return cursor.fetchone()[0]
        except:
            return 0
    
    def close(self):
        """Close database connections."""
        if self._wal_conn:
            self._wal_conn.close()
            self._wal_conn = None
        if self._hash_conn:
            self._hash_conn.close()
            self._hash_conn = None


def integrate_swarm_with_retrieval(query: str, domain: str, limit: int = 10) -> List[Fragment]:
    """
    Standalone function to integrate swarm data into retrieval pipeline.
    
    This is called by the main engine BEFORE falling back to live scraping.
    
    Args:
        query: User query
        domain: Domain code
        limit: Max fragments to retrieve
        
    Returns:
        List of fragments from swarm + traditional sources
    """
    swarm_engine = SwarmRetrievalEngine()
    
    # First, try to get data from swarm WAL buffer
    swarm_fragments = swarm_engine.query_swarm_data(query, domain, limit)
    
    if swarm_fragments:
        print(f"[INTEGRATION] Swarm provided {len(swarm_fragments)} pre-computed fragments")
        # Mark as retrieved so we don't fetch again
        agent_ids = list(set(f.swarm_metadata['agent_id'] for f in swarm_fragments 
                           if hasattr(f, 'swarm_metadata')))
        swarm_engine.mark_as_retrieved(agent_ids)
    
    swarm_engine.close()
    return swarm_fragments


if __name__ == "__main__":
    # Test swarm retrieval
    print("Testing Swarm Retrieval Engine...")
    
    engine = SwarmRetrievalEngine()
    
    # Test query
    frags = engine.query_swarm_data("exchange rate", "eco", limit=5)
    print(f"Retrieved {len(frags)} fragments")
    
    for frag in frags:
        print(f"  - {frag.claim[:80]}... (confidence: {frag.confidence_score})")
    
    # Stats
    harvest_count = engine.get_recent_harvest_count(hours=24)
    hash_count = engine.get_known_hash_count()
    
    print(f"\nSwarm Statistics:")
    print(f"  Harvested (24h): {harvest_count} items")
    print(f"  Known Hashes: {hash_count}")
    
    engine.close()
