"""
Night Mode: The Consolidation Engine for OpenEyes.

This module implements the "Sleep" phase of the cognitive cycle:
1. Analyzes daily success/failure logs (HALT reports)
2. Identifies high-success fragment patterns (Logic Hardening candidates)
3. Detects knowledge gaps requiring new fragments
4. Updates Gene Pool weights based on real-world performance
5. Proposes Synapses (pre-compiled logic chains) for frequent queries

Neuroscience Parallel: Moves decisions from energy-expensive deliberation 
(Prefrontal Cortex/Monte Carlo) to efficient instinct (Basal Ganglia/Compiled Logic).
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import statistics


class ConsolidationEngine:
    """
    The core engine that processes daily logs and updates system structure.
    
    Operates in three modes:
    - ANALYZE: Read logs and generate reports
    - PROPOSE: Identify candidate Synapses for Logic Hardening
    - EVOLVE: Update Gene Pool weights and index priorities
    """
    
    def __init__(self, logs_dir: str = "/workspace/logs", vault_path: str = None):
        self.logs_dir = logs_dir
        self.vault_path = vault_path or os.path.join(logs_dir, "obsidian_vault")
        self.success_logs = []
        self.halt_logs = []
        self.fragment_performance = defaultdict(list)  # fragment_id -> [scores]
        self.query_patterns = defaultdict(list)  # query_pattern -> [outcomes]
        
    def load_daily_logs(self, date_str: str = None):
        """
        Load success and halt logs for a specific date (or today if not specified).
        
        Log format expected:
        - success_YYYYMMDD.jsonl: {"query": "...", "fragments": [...], "confidence": float}
        - halt_YYYYMMDD.jsonl: {"query": "...", "reason": "...", "missing_slots": [...]}
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y%m%d")
            
        success_file = os.path.join(self.logs_dir, f"success_{date_str}.jsonl")
        halt_file = os.path.join(self.logs_dir, f"halt_{date_str}.jsonl")
        
        # Load success logs
        if os.path.exists(success_file):
            with open(success_file, 'r') as f:
                for line in f:
                    if line.strip():
                        self.success_logs.append(json.loads(line))
                        
        # Load halt logs
        if os.path.exists(halt_file):
            with open(halt_file, 'r') as f:
                for line in f:
                    if line.strip():
                        self.halt_logs.append(json.loads(line))
                        
        print(f"[Night Mode] Loaded {len(self.success_logs)} success logs, {len(self.halt_logs)} halt logs for {date_str}")
        
    def analyze_fragment_performance(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze how each fragment performed across all successful queries.
        
        Returns dict with:
        - fragment_id -> {avg_score, success_count, failure_count, consistency_ratio}
        """
        performance = {}
        
        for log in self.success_logs:
            confidence = log.get('confidence', 0)
            fragments = log.get('fragments', [])
            
            for frag in fragments:
                frag_id = frag.get('fragment_id') or frag.get('id')
                if not frag_id:
                    continue
                    
                if frag_id not in performance:
                    performance[frag_id] = {
                        'scores': [],
                        'success_count': 0,
                        'contexts': []
                    }
                    
                performance[frag_id]['scores'].append(confidence)
                performance[frag_id]['success_count'] += 1
                performance[frag_id]['contexts'].append(log.get('query', '')[:50])
                
        # Calculate statistics
        results = {}
        for frag_id, data in performance.items():
            scores = data['scores']
            results[frag_id] = {
                'avg_score': statistics.mean(scores) if scores else 0,
                'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0,
                'success_count': data['success_count'],
                'consistency_ratio': 1.0 - (statistics.stdev(scores) / 100 if len(scores) > 1 and statistics.mean(scores) > 0 else 0),
                'recent_contexts': data['contexts'][-3:]  # Last 3 queries
            }
            
        return results
        
    def identify_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """
        Analyze HALT logs to identify recurring knowledge gaps.
        
        Returns list of gap reports with:
        - missing_topic: The topic/keywords that caused halts
        - missing_role: Which reasoning_role is missing (definition, counter_argument, etc.)
        - frequency: How often this gap occurred
        - suggested_action: What type of fragment to add
        """
        gap_patterns = defaultdict(lambda: {'count': 0, 'roles_missing': set(), 'queries': []})
        
        for log in self.halt_logs:
            query = log.get('query', '')
            reason = log.get('reason', '')
            missing_slots = log.get('missing_slots', [])
            
            # Extract keywords from query (simple word extraction)
            keywords = self._extract_keywords(query)
            topic_key = tuple(sorted(keywords[:3]))  # Use top 3 keywords as topic identifier
            
            gap_patterns[topic_key]['count'] += 1
            gap_patterns[topic_key]['queries'].append(query)
            
            # Parse missing slots for reasoning roles
            for slot in missing_slots:
                if 'definition' in slot.lower():
                    gap_patterns[topic_key]['roles_missing'].add('definition')
                if 'counter' in slot.lower():
                    gap_patterns[topic_key]['roles_missing'].add('counter_argument')
                if 'latest' in slot.lower() or 'recent' in slot.lower():
                    gap_patterns[topic_key]['roles_missing'].add('latest_data')
                    
        # Convert to structured gap reports
        gap_reports = []
        for topic, data in sorted(gap_patterns.items(), key=lambda x: x[1]['count'], reverse=True):
            gap_reports.append({
                'topic_keywords': list(topic),
                'frequency': data['count'],
                'missing_roles': list(data['roles_missing']),
                'sample_queries': data['queries'][:3],
                'suggested_action': self._generate_suggested_action(data['roles_missing'])
            })
            
        return gap_reports
        
    def propose_synapses(self, min_success_threshold: int = 5, min_consistency: float = 0.85) -> List[Dict[str, Any]]:
        """
        Identify high-success fragment combinations that should be compiled into Synapses.
        
        A Synapse is a pre-verified logic chain that can bypass Monte Carlo simulation.
        
        Criteria:
        - Fragment combination appears together in >= min_success_threshold queries
        - Average confidence score >= 75
        - Consistency ratio >= min_consistency (low variance in performance)
        
        Returns list of proposed Synapses with fragment chains and trigger patterns.
        """
        # Group by fragment combination pattern
        combo_patterns = defaultdict(lambda: {'count': 0, 'scores': [], 'fragments': set()})
        
        for log in self.success_logs:
            fragments = log.get('fragments', [])
            frag_ids = tuple(sorted(f.get('fragment_id') or f.get('id') for f in fragments if f.get('fragment_id') or f.get('id')))
            
            if len(frag_ids) < 2:  # Need at least 2 fragments to form a chain
                continue
                
            combo_patterns[frag_ids]['count'] += 1
            combo_patterns[frag_ids]['scores'].append(log.get('confidence', 0))
            combo_patterns[frag_ids]['fragments'].update(frag_ids)
            
        # Filter for high-performing combinations
        synapse_proposals = []
        for combo, data in combo_patterns.items():
            if data['count'] < min_success_threshold:
                continue
                
            avg_score = statistics.mean(data['scores'])
            std_dev = statistics.stdev(data['scores']) if len(data['scores']) > 1 else 0
            consistency = 1.0 - (std_dev / 100) if avg_score > 0 else 0
            
            if avg_score >= 75 and consistency >= min_consistency:
                synapse_proposals.append({
                    'synapse_id': f"synapse_{'_'.join(combo[:3])}",  # Short ID from first 3 fragments
                    'fragment_chain': list(combo),
                    'occurrence_count': data['count'],
                    'avg_confidence': avg_score,
                    'consistency_ratio': consistency,
                    'trigger_keywords': self._extract_common_keywords(data['scores']),  # Infer from successful queries
                    'compilation_priority': 'HIGH' if data['count'] >= 10 else 'MEDIUM'
                })
                
        return sorted(synapse_proposals, key=lambda x: x['occurrence_count'], reverse=True)
        
    def update_gene_pool_weights(self, fragment_performance: Dict[str, Dict]) -> Dict[str, float]:
        """
        Calculate new weights for the Gene Pool based on real-world performance.
        
        Weight update formula:
        new_weight = old_weight * 0.7 + performance_score * 0.3
        
        Where performance_score = avg_confidence * consistency_ratio * log(success_count + 1)
        
        Returns dict of fragment_id -> new_weight
        """
        weight_updates = {}
        
        for frag_id, perf in fragment_performance.items():
            # Calculate performance score
            base_score = perf['avg_score'] / 100.0  # Normalize to 0-1
            consistency_bonus = perf['consistency_ratio']
            frequency_factor = min(2.0, statistics.log(perf['success_count'] + 1))  # Cap at 2x
            
            performance_score = base_score * consistency_bonus * frequency_factor
            
            # Blend with existing weight (70% old, 30% new performance)
            # Note: Actual weight application requires loading current gene pool
            weight_updates[frag_id] = round(performance_score, 4)
            
        return weight_updates
        
    def generate_night_report(self, output_path: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive Night Mode report with all findings.
        
        Report includes:
        - Fragment performance summary
        - Knowledge gap analysis
        - Synapse proposals for Logic Hardening
        - Gene Pool weight update recommendations
        """
        fragment_perf = self.analyze_fragment_performance()
        knowledge_gaps = self.identify_knowledge_gaps()
        synapse_proposals = self.propose_synapses()
        weight_updates = self.update_gene_pool_weights(fragment_perf)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_successful_queries': len(self.success_logs),
                'total_halted_queries': len(self.halt_logs),
                'unique_fragments_evaluated': len(fragment_perf),
                'synapses_proposed': len(synapse_proposals),
                'knowledge_gaps_identified': len(knowledge_gaps)
            },
            'fragment_performance': fragment_perf,
            'knowledge_gaps': knowledge_gaps,
            'synapse_proposals': synapse_proposals,
            'gene_pool_updates': weight_updates,
            'recommended_actions': self._prioritize_actions(knowledge_gaps, synapse_proposals)
        }
        
        # Save report
        if output_path is None:
            output_path = os.path.join(self.logs_dir, f"night_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"[Night Mode] Report saved to {output_path}")
        return report
        
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text (stop-word filtered)."""
        stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'when', 'where', 'why', 'which', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'and', 'or', 'but', 'if', 'then', 'else', 'that', 'this', 'it', 'as', 'be', 'has', 'have', 'was', 'were', 'been', 'being', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
        words = text.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2]
        
    def _generate_suggested_action(self, missing_roles: set) -> str:
        """Generate human-readable action recommendation based on missing roles."""
        actions = []
        if 'definition' in missing_roles:
            actions.append("Add definition fragment with authoritative source")
        if 'counter_argument' in missing_roles:
            actions.append("Add counter_argument fragment showing limitations/challenges")
        if 'latest_data' in missing_roles:
            actions.append("Add latest_data fragment with recent research/guidelines")
        return "; ".join(actions) if actions else "Review and expand fragment coverage"
        
    def _extract_common_keywords(self, scores: List[float]) -> List[str]:
        """Placeholder for keyword extraction from successful query contexts."""
        # In full implementation, this would analyze the actual queries
        # For now, returns empty list (to be populated when query context is tracked)
        return []
        
    def _prioritize_actions(self, gaps: List[Dict], synapses: List[Dict]) -> List[Dict[str, str]]:
        """Generate prioritized action list based on gaps and opportunities."""
        actions = []
        
        # High-frequency gaps get top priority
        for gap in gaps[:5]:  # Top 5 gaps
            actions.append({
                'priority': 'CRITICAL' if gap['frequency'] >= 3 else 'HIGH',
                'action': f"Create fragments for topic: {', '.join(gap['topic_keywords'])}",
                'details': gap['suggested_action'],
                'impact': f"Will resolve {gap['frequency']} halted queries"
            })
            
        # High-value synapses get compilation priority
        for synapse in synapses[:3]:  # Top 3 synapses
            actions.append({
                'priority': 'MEDIUM',
                'action': f"Compile Synapse: {synapse['synapse_id']}",
                'details': f"Chain {len(synapse['fragment_chain'])} fragments for instant retrieval",
                'impact': f"Will speed up {synapse['occurrence_count']} common queries"
            })
            
        return actions


def run_night_mode(date_str: str = None, logs_dir: str = "/workspace/logs"):
    """
    Main entry point for Night Mode execution.
    
    Usage:
        from openeyes.night_mode import run_night_mode
        run_night_mode()  # Runs for today
        run_night_mode("20250101")  # Runs for specific date
    """
    engine = ConsolidationEngine(logs_dir=logs_dir)
    engine.load_daily_logs(date_str)
    
    if not engine.success_logs and not engine.halt_logs:
        print("[Night Mode] No logs found for this date. Skipping consolidation.")
        return None
        
    report = engine.generate_night_report()
    
    # Print summary
    print("\n" + "="*60)
    print("NIGHT MODE CONSOLIDATION REPORT")
    print("="*60)
    print(f"Successful queries analyzed: {report['summary']['total_successful_queries']}")
    print(f"Halted queries analyzed: {report['summary']['total_halted_queries']}")
    print(f"Synapses proposed for Logic Hardening: {report['summary']['synapses_proposed']}")
    print(f"Knowledge gaps identified: {report['summary']['knowledge_gaps_identified']}")
    
    if report['recommended_actions']:
        print("\nTOP RECOMMENDED ACTIONS:")
        for i, action in enumerate(report['recommended_actions'][:5], 1):
            print(f"{i}. [{action['priority']}] {action['action']}")
            print(f"   → {action['details']}")
            
    print("="*60)
    
    return report


def compute_nightly_grundy(fragment_library):
    """
    Compute Sprague-Grundy values for all fragments during Night Mode.
    
    This function:
    1. Fetches all fragments from the library
    2. Runs GameTheoryEngine to compute Grundy values
    3. Updates each fragment JSON with grundy_value and robustness_status
    4. Logs completion status
    
    Args:
        fragment_library: FragmentLibrary instance or compatible object
        
    Returns:
        Dict of fragment_id -> grundy_value
    """
    from openeyes.game_theory import GameTheoryEngine
    
    fragments = fragment_library.get_all_fragments()
    engine = GameTheoryEngine(fragments)
    grundy_values = engine.compute_all_grundy_values()
    
    # Write grundy_value back to each fragment JSON
    for frag_id, grundy_val in grundy_values.items():
        fragment_library.update_fragment_field(frag_id, 'grundy_value', grundy_val)
        robustness = engine.get_robustness_status(frag_id)
        fragment_library.update_fragment_field(frag_id, 'robustness_status', robustness)
    
    print(f"[Night Mode] Grundy computation complete: {len(grundy_values)} fragments updated")
    return grundy_values


def parse_halt_logs(halt_log_path: str) -> List[Dict[str, Any]]:
    """
    Parse HALT logs to identify recurring gap patterns.
    
    Returns list of patterns sorted by frequency:
    - query: The query pattern that caused halts
    - count: How many times this pattern appeared
    - missing_slots: What reasoning roles were missing
    """
    gap_patterns = defaultdict(lambda: {'count': 0, 'missing_slots': set(), 'queries': []})
    
    if not os.path.exists(halt_log_path):
        print(f"[Night Mode] No halt log found at {halt_log_path}")
        return []
    
    with open(halt_log_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            log = json.loads(line)
            query = log.get('query', '')
            missing_slots = log.get('missing_slots', [])
            
            # Extract keywords from query
            keywords = [w for w in query.lower().split() if len(w) > 3 and w not in {'what', 'how', 'when', 'where', 'why', 'which', 'does', 'have', 'been', 'with', 'from', 'that', 'this', 'these', 'those'}]
            topic_key = tuple(sorted(keywords[:3]))
            
            gap_patterns[topic_key]['count'] += 1
            gap_patterns[topic_key]['missing_slots'].update(missing_slots)
            gap_patterns[topic_key]['queries'].append(query)
    
    # Convert to list format
    results = []
    for topic, data in sorted(gap_patterns.items(), key=lambda x: x[1]['count'], reverse=True):
        results.append({
            'query': ' '.join(topic),
            'count': data['count'],
            'missing_slots': list(data['missing_slots']),
            'sample_queries': data['queries'][:2]
        })
    
    return results


def save_proposals(proposals: List[Dict[str, Any]], output_dir: str = None):
    """Save fragment proposals to JSON file for human review."""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'proposals')
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"fragment_proposals_{timestamp}.json")
    
    with open(output_file, 'w') as f:
        json.dump(proposals, f, indent=2, default=str)
    
    print(f"[Night Mode] Saved {len(proposals)} proposals to {output_file}")
    return output_file


def fill_gaps_from_halts(fragment_library, halt_log_path: str, max_proposals: int = 10) -> List[Dict[str, Any]]:
    """
    Read recent HALT logs and propose fragments to fill gaps.
    
    This function:
    1. Parses halt logs to find common failure patterns
    2. Uses WebAgent to retrieve content from trusted sources
    3. Filters candidates by credibility threshold (>= 0.85)
    4. Generates proposals requiring human review
    
    Args:
        fragment_library: The FragmentLibrary instance
        halt_log_path: Path to the halt log file (JSONL format)
        max_proposals: Maximum number of proposals to generate
    
    Returns:
        List of fragment proposals with metadata
    """
    from openeyes.swarm import WebAgent
    
    proposals = []
    
    # Parse halt logs for common failure patterns
    gap_patterns = parse_halt_logs(halt_log_path)
    
    if not gap_patterns:
        print("[Night Mode] No gap patterns found in halt logs")
        return []
    
    web_agent = WebAgent()
    
    print(f"[Night Mode] Processing {len(gap_patterns)} gap patterns...")
    
    for pattern in gap_patterns[:max_proposals]:
        query_topic = pattern['query']
        print(f"[Night Mode] Retrieving for gap: {query_topic} (appeared {pattern['count']} times)")
        
        # Attempt retrieval for gap topic
        try:
            candidates = web_agent.retrieve(query_topic, domain='finance')
            
            for candidate in candidates:
                cred_estimate = getattr(candidate, 'credibility_estimate', 0)
                if cred_estimate >= 0.85:
                    proposals.append({
                        'suggested_fragment': candidate.to_dict() if hasattr(candidate, 'to_dict') else vars(candidate),
                        'gap_query': query_topic,
                        'halt_count': pattern['count'],
                        'auto_approve': False,  # Always require human review
                        'source_url': getattr(candidate, 'source_url', ''),
                        'credibility_estimate': cred_estimate
                    })
                    print(f"  -> Found candidate from {getattr(candidate, 'source', 'unknown')} (credibility: {cred_estimate})")
        except Exception as e:
            print(f"[Night Mode] Error retrieving for '{query_topic}': {e}")
            continue
    
    # Save proposals for review
    if proposals:
        save_proposals(proposals)
    
    print(f"[Night Mode] {len(proposals)} fragment proposals generated from {len(gap_patterns)} gap patterns")
    return proposals


if __name__ == "__main__":
    run_night_mode()
