"""
Emergent Knowledge Domain (EKD) System

Crystallizes successful query-answer fragment combinations into
reusable knowledge clusters. Clusters evolve with each activation —
gaining new fragments, losing decayed ones, tracking version history.

This is the system's long-term memory layer, sitting above the
fragment library and below the Synapse compiled logic index.

Hierarchy:
  Fragment Library (facts)
       ↓
  Emergent Knowledge Domains (proven fragment combinations)
       ↓  
  Synapse Index (pre-compiled instant answers)
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class EKDVersion:
    """A snapshot of a cluster at a point in time."""
    version: int
    created_at: str
    fragment_ids: List[str]
    confidence: float
    query_count: int  # How many queries activated this version
    trigger_queries: List[str]  # Sample queries that created/updated this


@dataclass  
class EmergentKnowledgeDomain:
    """
    A knowledge cluster that emerged from successful query resolution.
    
    Not manually curated. Created automatically when a query succeeds
    with high confidence. Evolves with each activation.
    """
    cluster_id: str
    canonical_query_form: str  # The normalized query that created this
    domain: str
    primary_tags: List[str]   # Core topic tags
    kap_intent_type: str      # What kind of query created this
    
    current_version: int
    versions: List[EKDVersion]
    
    # Current active fragment set
    fragment_ids: List[str]
    confidence: float
    
    # Usage tracking
    activation_count: int
    last_activated: str
    avg_confidence_over_time: float
    
    # Evolution tracking  
    fragments_gained: int   # Fragments added across all versions
    fragments_lost: int     # Fragments that decayed out


class EKDStore:
    """
    Persistent store for Emergent Knowledge Domains.
    Manages creation, activation, evolution, and retrieval of clusters.
    """
    
    def __init__(self, store_path: str = "openeyes/data/ekd_store.json"):
        self.store_path = Path(store_path)
        self.clusters: Dict[str, EmergentKnowledgeDomain] = {}
        self.load()
    
    def load(self):
        """Load existing clusters from disk."""
        if self.store_path.exists():
            try:
                data = json.loads(self.store_path.read_text())
                for cluster_id, cluster_data in data.get('clusters', {}).items():
                    # Reconstruct EKD objects from stored dicts
                    versions = [EKDVersion(**v) for v in cluster_data.pop('versions', [])]
                    self.clusters[cluster_id] = EmergentKnowledgeDomain(
                        **cluster_data,
                        versions=versions
                    )
            except Exception as e:
                print(f"[EKD] Error loading store: {e}")
                self.clusters = {}
    
    def save(self):
        """Persist all clusters to disk."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'last_updated': datetime.now().isoformat(),
            'cluster_count': len(self.clusters),
            'clusters': {
                cid: asdict(cluster) 
                for cid, cluster in self.clusters.items()
            }
        }
        self.store_path.write_text(json.dumps(data, indent=2))
    
    def _generate_cluster_id(self, canonical_query: str, domain: str) -> str:
        """Generate stable cluster ID from canonical query."""
        content = f"{domain}::{canonical_query}"
        return "EKD_" + hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def crystallize(
        self,
        canonical_query: str,
        domain: str,
        fragment_ids: List[str],
        confidence: float,
        primary_tags: List[str],
        kap_intent_type: str,
        trigger_query: str,
        fragment_library=None  # For Improvement 1: Fragment Confidence Inheritance
    ) -> Optional[EmergentKnowledgeDomain]:
        """
        Create or update an EKD from a successful query resolution.
        
        Only called when confidence >= CRYSTALLIZATION_THRESHOLD.
        Returns the created/updated cluster.
        """
        CRYSTALLIZATION_THRESHOLD = 65.0
        MIN_FRAGMENT_COUNT = 8  # FIX 1: Minimum fragment gate
        
        if confidence < CRYSTALLIZATION_THRESHOLD:
            return None
        
        if not fragment_ids:
            return None
        
        # FIX 1: Require minimum 8 fragments to crystallize
        if len(fragment_ids) < MIN_FRAGMENT_COUNT:
            print(f"[EKD] Crystallization blocked: only {len(fragment_ids)} fragments "
                  f"(minimum {MIN_FRAGMENT_COUNT} required)")
            return None
        
        cluster_id = self._generate_cluster_id(canonical_query, domain)
        now = datetime.now().isoformat()
        
        if cluster_id in self.clusters:
            # Evolve existing cluster
            cluster = self.clusters[cluster_id]
            cluster.activation_count += 1
            cluster.last_activated = now
            
            # Check for fragment changes
            old_set = set(cluster.fragment_ids)
            new_set = set(fragment_ids)
            gained = new_set - old_set
            lost = old_set - new_set
            
            if gained or lost or abs(confidence - cluster.confidence) > 5.0:
                # Meaningful change — create new version
                cluster.current_version += 1
                new_version = EKDVersion(
                    version=cluster.current_version,
                    created_at=now,
                    fragment_ids=fragment_ids,
                    confidence=confidence,
                    query_count=1,
                    trigger_queries=[trigger_query]
                )
                cluster.versions.append(new_version)
                cluster.fragment_ids = fragment_ids
                cluster.fragments_gained += len(gained)
                cluster.fragments_lost += len(lost)
            else:
                # No meaningful change — just update usage count
                if cluster.versions:
                    cluster.versions[-1].query_count += 1
                    if trigger_query not in cluster.versions[-1].trigger_queries:
                        cluster.versions[-1].trigger_queries.append(trigger_query)
            
            # Update rolling confidence average
            n = cluster.activation_count
            cluster.avg_confidence_over_time = (
                (cluster.avg_confidence_over_time * (n - 1) + confidence) / n
            )
            cluster.confidence = confidence
            
        else:
            # Create new cluster
            first_version = EKDVersion(
                version=1,
                created_at=now,
                fragment_ids=fragment_ids,
                confidence=confidence,
                query_count=1,
                trigger_queries=[trigger_query]
            )
            
            cluster = EmergentKnowledgeDomain(
                cluster_id=cluster_id,
                canonical_query_form=canonical_query,
                domain=domain,
                primary_tags=primary_tags,
                kap_intent_type=kap_intent_type,
                current_version=1,
                versions=[first_version],
                fragment_ids=fragment_ids,
                confidence=confidence,
                activation_count=1,
                last_activated=now,
                avg_confidence_over_time=confidence,
                fragments_gained=len(fragment_ids),
                fragments_lost=0
            )
            self.clusters[cluster_id] = cluster
            print(f"[EKD] New cluster crystallized: {cluster_id} "
                  f"({len(fragment_ids)} fragments, confidence {confidence:.1f}%)")
        
        # IMPROVEMENT 1: Fragment Confidence Inheritance
        # When a fragment contributes to a successful cluster, boost its weight
        if fragment_library is not None:
            self._apply_fragment_confidence_inheritance(fragment_ids, confidence, fragment_library)
        
        self.save()
        return cluster
    
    def _apply_fragment_confidence_inheritance(
        self, 
        fragment_ids: List[str], 
        confidence: float,
        fragment_library
    ) -> None:
        """
        IMPROVEMENT 1: Fragment Confidence Inheritance
        
        When a fragment contributes to a successful EKD cluster, that success
        propagates back to the fragment's individual weight in the gene pool.
        
        - Successful cluster (crystallizes): +0.03 bonus to each fragment
        - This creates feedback loop where fragments learn from co-survival history
        """
        from shared_core.survival_and_weights import load_gene_pool, save_gene_pool
        
        pool = load_gene_pool()
        bonus = 0.03  # Small boost for contributing to successful cluster
        
        for frag_id in fragment_ids:
            if frag_id in pool:
                current_weight = pool[frag_id].get("weight", 1.0)
                new_weight = min(current_weight + bonus, 2.0)  # Cap at max weight
                pool[frag_id]["weight"] = round(new_weight, 2)
                print(f"[EKD] Fragment {frag_id[:20]}... weight boosted: "
                      f"{current_weight:.2f} → {new_weight:.2f} (+{bonus})")
            else:
                # Initialize new entry if fragment not in gene pool
                pool[frag_id] = {"id": frag_id, "weight": 1.0 + bonus}
                print(f"[EKD] Fragment {frag_id[:20]}... added to gene pool with weight {1.0 + bonus:.2f}")
        
        save_gene_pool(pool)
    
    def find_matching_cluster(
        self, 
        canonical_query: str, 
        domain: str,
        primary_tags: List[str],
        min_tag_overlap: float = 0.4
    ) -> Optional[EmergentKnowledgeDomain]:
        """
        Find the best matching cluster for a new query.
        
        Matching criteria:
        1. Same domain
        2. Canonical query match (exact)
        3. Tag overlap >= min_tag_overlap (fuzzy match)
        
        Returns the best match or None.
        """
        # Check exact canonical match first
        cluster_id = self._generate_cluster_id(canonical_query, domain)
        if cluster_id in self.clusters:
            return self.clusters[cluster_id]
        
        # Fuzzy match by tag overlap
        query_tags = set(primary_tags)
        best_match = None
        best_overlap = 0.0
        
        for cluster in self.clusters.values():
            if cluster.domain != domain:
                continue
            
            cluster_tags = set(cluster.primary_tags)
            if not cluster_tags:
                continue
            
            overlap = len(query_tags & cluster_tags) / max(len(query_tags), len(cluster_tags))
            
            if overlap >= min_tag_overlap and overlap > best_overlap:
                best_overlap = overlap
                best_match = cluster
        
        if best_match:
            print(f"[EKD] Fuzzy match: {best_match.cluster_id} "
                  f"(tag overlap: {best_overlap:.1%}, "
                  f"v{best_match.current_version}, "
                  f"confidence: {best_match.confidence:.1f}%)")
        
        return best_match
    
    def get_cluster_fragments(
        self, 
        cluster: EmergentKnowledgeDomain,
        fragment_library
    ) -> List[Any]:
        """
        Retrieve the actual fragment objects for a cluster.
        Validates that fragments still exist and haven't been removed.
        """
        valid_fragments = []
        stale_ids = []
        
        for frag_id in cluster.fragment_ids:
            frag = fragment_library._fragments.get(frag_id)
            if frag:
                valid_fragments.append(frag)
            else:
                stale_ids.append(frag_id)
        
        if stale_ids:
            # Remove stale fragment IDs from cluster
            cluster.fragment_ids = [
                fid for fid in cluster.fragment_ids 
                if fid not in stale_ids
            ]
            cluster.fragments_lost += len(stale_ids)
            print(f"[EKD] Removed {len(stale_ids)} stale fragments from {cluster.cluster_id}")
            self.save()
        
        return valid_fragments
    
    def get_statistics(self) -> Dict:
        """Return EKD store statistics."""
        if not self.clusters:
            return {
                'total_clusters': 0,
                'by_domain': {},
                'by_intent_type': {},
                'avg_confidence': 0,
                'most_activated': []
            }
        
        by_domain = {}
        by_intent = {}
        confidences = []
        
        for cluster in self.clusters.values():
            by_domain[cluster.domain] = by_domain.get(cluster.domain, 0) + 1
            by_intent[cluster.kap_intent_type] = by_intent.get(cluster.kap_intent_type, 0) + 1
            confidences.append(cluster.confidence)
        
        most_activated = sorted(
            self.clusters.values(),
            key=lambda c: c.activation_count,
            reverse=True
        )[:5]
        
        return {
            'total_clusters': len(self.clusters),
            'by_domain': by_domain,
            'by_intent_type': by_intent,
            'avg_confidence': sum(confidences) / len(confidences),
            'most_activated': [
                {
                    'id': c.cluster_id,
                    'activations': c.activation_count,
                    'confidence': c.confidence,
                    'version': c.current_version
                }
                for c in most_activated
            ]
        }
