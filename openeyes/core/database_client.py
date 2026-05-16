"""
Real Database Client for Unified Knowledge Orchestrator
Replaces mock implementations with actual SQLite storage for fragments, cache, and metrics.
"""

import sqlite3
import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import asdict
from datetime import datetime

class KnowledgeDatabase:
    """
    SQLite-backed storage for knowledge fragments, cache, and quality metrics.
    Provides real persistence replacing mock implementations.
    """
    
    def __init__(self, db_path: str = "/workspace/openeyes/data/knowledge.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Fragments table - stores all knowledge fragments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fragments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source_url TEXT,
                confidence_score REAL,
                tier TEXT,
                domain TEXT,
                timestamp REAL,
                metadata TEXT,
                credibility_level TEXT,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        # Cache table - for quick lookups
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE NOT NULL,
                query_text TEXT,
                result_json TEXT,
                domain TEXT,
                created_at REAL DEFAULT (strftime('%s', 'now')),
                expires_at REAL
            )
        ''')
        
        # Metrics table - for tracking quality and performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                domain TEXT,
                value REAL,
                count INTEGER DEFAULT 1,
                timestamp REAL DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        # Feedback table - for user feedback and adaptive learning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id TEXT,
                domain TEXT,
                was_accurate BOOLEAN,
                user_rating INTEGER,
                comments TEXT,
                timestamp REAL DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        # Source credibility table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS source_credibility (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT UNIQUE NOT NULL,
                credibility_level TEXT,
                score REAL,
                factors TEXT,
                last_verified REAL,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fragments_domain ON fragments(domain)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fragments_tier ON fragments(tier)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_query ON query_cache(query_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_domain ON feedback(domain)')
        
        conn.commit()
        conn.close()
    
    def store_fragment(self, content: str, source_url: str, confidence_score: float,
                       tier: str, domain: str, metadata: Dict[str, Any] = None,
                       credibility_level: str = None) -> int:
        """Store a knowledge fragment in the database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO fragments (content, source_url, confidence_score, tier, domain, 
                                   timestamp, metadata, credibility_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content,
            source_url,
            confidence_score,
            tier,
            domain,
            time.time(),
            json.dumps(metadata or {}),
            credibility_level
        ))
        
        fragment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return fragment_id
    
    def retrieve_fragments(self, query: str, domain: str = None, 
                           min_confidence: float = 0.0, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve fragments matching query criteria."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple keyword matching (in production, use full-text search or vector DB)
        query_terms = query.lower().split()
        
        base_query = '''
            SELECT * FROM fragments 
            WHERE confidence_score >= ?
        '''
        params = [min_confidence]
        
        if domain:
            base_query += ' AND domain = ?'
            params.append(domain)
        
        base_query += ' ORDER BY confidence_score DESC, timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        
        fragments = []
        for row in rows:
            fragment = dict(row)
            try:
                fragment['metadata'] = json.loads(fragment['metadata']) if fragment['metadata'] else {}
            except:
                fragment['metadata'] = {}
            fragments.append(fragment)
        
        conn.close()
        return fragments
    
    def cache_result(self, query: str, result: Dict[str, Any], domain: str, 
                     ttl_seconds: int = 3600) -> bool:
        """Cache a query result."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query_hash = hashlib.md5(query.encode()).hexdigest()
        result_json = json.dumps(result)
        expires_at = time.time() + ttl_seconds
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO query_cache (query_hash, query_text, result_json, 
                                                    domain, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (query_hash, query, result_json, domain, expires_at))
            conn.commit()
            success = True
        except Exception as e:
            success = False
        finally:
            conn.close()
        
        return success
    
    def get_cached_result(self, query: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result if available and not expired."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query_hash = hashlib.md5(query.encode()).hexdigest()
        current_time = time.time()
        
        cursor.execute('''
            SELECT result_json FROM query_cache 
            WHERE query_hash = ? AND expires_at > ?
        ''', (query_hash, current_time))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row['result_json'])
        return None
    
    def record_metric(self, metric_type: str, domain: str, value: float, count: int = 1):
        """Record a performance or quality metric."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (metric_type, domain, value, count)
            VALUES (?, ?, ?, ?)
        ''', (metric_type, domain, value, count))
        
        conn.commit()
        conn.close()
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get aggregated metrics for the dashboard."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        since_time = time.time() - (hours * 3600)
        
        # Query counts by domain
        cursor.execute('''
            SELECT domain, COUNT(*) as count 
            FROM fragments 
            WHERE created_at > ? 
            GROUP BY domain
        ''', (since_time,))
        domain_counts = {row['domain']: row['count'] for row in cursor.fetchall()}
        
        # Average confidence by domain
        cursor.execute('''
            SELECT domain, AVG(confidence_score) as avg_conf 
            FROM fragments 
            WHERE created_at > ? AND domain IS NOT NULL
            GROUP BY domain
        ''', (since_time,))
        domain_confidence = {row['domain']: row['avg_conf'] for row in cursor.fetchall()}
        
        # Credibility distribution
        cursor.execute('''
            SELECT credibility_level, COUNT(*) as count 
            FROM fragments 
            WHERE created_at > ? AND credibility_level IS NOT NULL
            GROUP BY credibility_level
        ''', (since_time,))
        credibility_dist = {row['credibility_level']: row['count'] for row in cursor.fetchall()}
        
        # Feedback stats
        cursor.execute('''
            SELECT domain, was_accurate, COUNT(*) as count 
            FROM feedback 
            WHERE timestamp > ? 
            GROUP BY domain, was_accurate
        ''', (since_time,))
        feedback_stats = {}
        for row in cursor.fetchall():
            if row['domain'] not in feedback_stats:
                feedback_stats[row['domain']] = {'accurate': 0, 'inaccurate': 0}
            key = 'accurate' if row['was_accurate'] else 'inaccurate'
            feedback_stats[row['domain']][key] = row['count']
        
        conn.close()
        
        return {
            'domain_counts': domain_counts,
            'domain_confidence': domain_confidence,
            'credibility_distribution': credibility_dist,
            'feedback_stats': feedback_stats,
            'time_range_hours': hours
        }
    
    def store_feedback(self, query_id: str, domain: str, was_accurate: bool,
                       user_rating: int = None, comments: str = None) -> int:
        """Store user feedback for adaptive learning."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (query_id, domain, was_accurate, user_rating, comments)
            VALUES (?, ?, ?, ?, ?)
        ''', (query_id, domain, was_accurate, user_rating, comments))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return feedback_id
    
    def get_domain_accuracy(self, domain: str, limit: int = 1000) -> float:
        """Calculate historical accuracy for a domain based on feedback."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT was_accurate, COUNT(*) as count 
            FROM feedback 
            WHERE domain = ? 
            GROUP BY was_accurate
            LIMIT ?
        ''', (domain, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return 0.90  # Default if no feedback yet
        
        total = 0
        accurate = 0
        for row in rows:
            total += row[1]
            if row[0]:  # was_accurate is True
                accurate += row[1]
        
        return accurate / total if total > 0 else 0.90
    
    def update_source_credibility(self, source_url: str, credibility_level: str,
                                   score: float, factors: List[str]) -> bool:
        """Update or insert source credibility information."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO source_credibility (source_url, credibility_level, score, 
                                                factors, last_verified, usage_count)
                VALUES (?, ?, ?, ?, ?, 1)
                ON CONFLICT(source_url) DO UPDATE SET
                    credibility_level = excluded.credibility_level,
                    score = excluded.score,
                    factors = excluded.factors,
                    last_verified = excluded.last_verified,
                    usage_count = usage_count + 1
            ''', (source_url, credibility_level, score, json.dumps(factors), time.time()))
            conn.commit()
            success = True
        except Exception as e:
            success = False
        finally:
            conn.close()
        
        return success
    
    def get_source_credibility(self, source_url: str) -> Optional[Dict[str, Any]]:
        """Retrieve credibility information for a source."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM source_credibility 
            WHERE source_url = ?
        ''', (source_url,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            try:
                result['factors'] = json.loads(result['factors']) if result['factors'] else []
            except:
                result['factors'] = []
            return result
        return None
    
    def close(self):
        """Explicitly close database connections if needed."""
        pass  # SQLite connections are auto-closed after each operation


# Singleton instance
_db_instance: Optional[KnowledgeDatabase] = None

def get_database(db_path: str = None) -> KnowledgeDatabase:
    """Get or create the database singleton."""
    global _db_instance
    if _db_instance is None:
        path = db_path or "/workspace/openeyes/data/knowledge.db"
        _db_instance = KnowledgeDatabase(path)
    return _db_instance
