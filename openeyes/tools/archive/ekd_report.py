"""EKD Store analysis and reporting tool."""
from openeyes.core.ekd import EKDStore

def generate_ekd_report():
    store = EKDStore()
    stats = store.get_statistics()
    
    print("=" * 60)
    print("OPENEYES EMERGENT KNOWLEDGE DOMAIN REPORT")
    print("=" * 60)
    print(f"Total clusters: {stats['total_clusters']}")
    print(f"Average confidence: {stats['avg_confidence']:.1f}%")
    print(f"\nBy domain: {stats['by_domain']}")
    print(f"By intent type: {stats['by_intent_type']}")
    
    print(f"\nMost activated clusters:")
    for c in stats['most_activated']:
        print(f"  {c['id']}: {c['activations']} activations, "
              f"v{c['version']}, conf {c['confidence']:.1f}%")
    
    print("\nAll clusters:")
    for cluster in store.clusters.values():
        print(f"  {cluster.cluster_id}")
        print(f"    Query: {cluster.canonical_query_form[:60]}")
        print(f"    Domain: {cluster.domain} | Intent: {cluster.kap_intent_type}")
        print(f"    Version: {cluster.current_version} | "
              f"Activations: {cluster.activation_count}")
        print(f"    Fragments: {len(cluster.fragment_ids)} | "
              f"Confidence: {cluster.confidence:.1f}%")
        print()

if __name__ == '__main__':
    generate_ekd_report()
