"""
Consolidation Engine - Phase 1: The "Sleep" Cycle

This module implements the Night Mode logic where OpenEyes transitions from
a Stateless Verifier to a Stateful Learner. It analyzes daily operation logs
to identify patterns for Logic Hardening and Gene Pool Evolution.

Core Functions:
1. Log Analysis: Parses success and halt logs to find recurring patterns
2. Synapse Proposal: Identifies high-success fragment combinations to compile
3. Gap Detection: Analyzes halt reasons to prioritize library expansion
4. Gene Pool Update: Adjusts fragment weights based on real-world performance
"""

import os
import json
import glob
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple, Optional
import statistics

class ConsolidationEngine:
    """
    The 'Sleep' component of OpenEyes.
    Runs periodically (Night Mode) to consolidate learning from daily operations.
    """
    
    def __init__(self, logs_dir: str = "/workspace/logs", vault_dir: str = "/workspace/openeyes_vault"):
        self.logs_dir = logs_dir
        self.vault_dir = vault_dir
        self.success_logs_path = os.path.join(logs_dir, "success")
        self.halt_logs_path = os.path.join(logs_dir, "halt")
        
        # Memory structures for consolidation
        self.fragment_performance: Dict[str, List[float]] = defaultdict(list)
        self.fragment_combinations: Dict[str, int] = Counter()
        self.halt_patterns: Dict[str, int] = Counter()
        self.domain_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "success_count": 0,
            "halt_count": 0,
            "avg_confidence": 0.0,
            "common_gaps": []
        })
        
    def run_night_mode(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the full Night Mode consolidation cycle.
        
        Args:
            date_str: Date string (YYYY-MM-DD) to process. Defaults to yesterday.
            
        Returns:
            Consolidation report with proposed synapses and identified gaps.
        """
        if date_str is None:
            # Default to processing all available logs for now
            # In production, this would be yesterday's date
            date_str = datetime.now().strftime("%Y-%m-%d")
            
        print(f"🌙 [Night Mode] Starting consolidation cycle for {date_str}...")
        
        # Step 1: Parse Logs
        success_data = self._parse_success_logs()
        halt_data = self._parse_halt_logs()
        
        # Step 2: Analyze Patterns
        print("📊 [Night Mode] Analyzing fragment performance...")
        gene_pool_updates = self._analyze_fragment_performance(success_data)
        
        print("🔗 [Night Mode] Identifying high-success combinations (Synapse candidates)...")
        synapse_candidates = self._identify_synapse_candidates(success_data)
        
        print("🕳️ [Night Mode] Detecting knowledge gaps from halts...")
        gap_report = self._analyze_halt_patterns(halt_data)
        
        # Step 3: Generate Consolidation Report
        report = {
            "date": date_str,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_successes": len(success_data),
                "total_halts": len(halt_data),
                "fragments_analyzed": len(self.fragment_performance),
                "synapses_proposed": len(synapse_candidates),
                "gaps_identified": len(gap_report)
            },
            "gene_pool_updates": gene_pool_updates,
            "synapse_candidates": synapse_candidates,
            "gap_report": gap_report,
            "domain_stats": dict(self.domain_stats)
        }
        
        # Step 4: Save Report
        report_path = os.path.join(self.logs_dir, f"consolidation_{date_str}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"✅ [Night Mode] Consolidation complete. Report saved to {report_path}")
        print(f"   - Proposed {len(synapse_candidates)} new synapses for Logic Hardening")
        print(f"   - Identified {len(gap_report)} knowledge gaps for Night Mode expansion")
        print(f"   - Updated weights for {len(gene_pool_updates)} fragments")
        
        return report

    def _parse_success_logs(self) -> List[Dict[str, Any]]:
        """Parse all success log files."""
        success_data = []
        pattern = os.path.join(self.success_logs_path, "*.json")
        
        for log_file in glob.glob(pattern):
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        success_data.extend(data)
                    else:
                        success_data.append(data)
            except Exception as e:
                print(f"⚠️ Error parsing {log_file}: {e}")
                
        return success_data

    def _parse_halt_logs(self) -> List[Dict[str, Any]]:
        """Parse all halt log files."""
        halt_data = []
        pattern = os.path.join(self.halt_logs_path, "*.json")
        
        for log_file in glob.glob(pattern):
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        halt_data.extend(data)
                    else:
                        halt_data.append(data)
            except Exception as e:
                print(f"⚠️ Error parsing {log_file}: {e}")
                
        return halt_data

    def _analyze_fragment_performance(self, success_data: List[Dict]) -> Dict[str, float]:
        """
        Analyze fragment performance across successful queries.
        Returns recommended weight adjustments for the Gene Pool.
        """
        updates = {}
        
        for entry in success_data:
            domain = entry.get("domain", "unknown")
            confidence = entry.get("confidence", 0.0)
            fragments = entry.get("answer_fragments", [])
            
            self.domain_stats[domain]["success_count"] += 1
            self.domain_stats[domain]["avg_confidence"] = (
                (self.domain_stats[domain]["avg_confidence"] * (self.domain_stats[domain]["success_count"] - 1) + confidence) 
                / self.domain_stats[domain]["success_count"]
            )
            
            # Track individual fragment performance
            for frag in fragments:
                frag_id = frag.get("fragment_id", "unknown")
                score = frag.get("score", 0.0)
                
                self.fragment_performance[frag_id].append(score)
                
                # Track combinations (for synapse detection)
                frag_ids = tuple(sorted([f.get("fragment_id") for f in fragments]))
                self.fragment_combinations[frag_ids] += 1
        
        # Calculate weight updates based on performance consistency
        for frag_id, scores in self.fragment_performance.items():
            if len(scores) >= 1:
                avg_score = statistics.mean(scores)
                variance = statistics.variance(scores) if len(scores) > 1 else 0
                
                # High average + low variance = reliable fragment → increase weight
                # Low average or high variance = unreliable → decrease weight
                if avg_score >= 75 and variance < 100:
                    adjustment = min(0.1, len(scores) * 0.01)  # Cap at 10% increase
                    updates[frag_id] = round(adjustment, 4)
                elif avg_score < 60 or variance > 400:
                    adjustment = max(-0.1, -len(scores) * 0.005)  # Cap at 10% decrease
                    updates[frag_id] = round(adjustment, 4)
                    
        return updates

    def _identify_synapse_candidates(self, success_data: List[Dict]) -> List[Dict]:
        """
        Identify fragment combinations that consistently succeed together.
        These become candidates for "Logic Hardening" (compiled synapses).
        """
        candidates = []
        threshold = 3  # Minimum occurrences to consider
        
        for combination, count in self.fragment_combinations.most_common():
            if count >= threshold:
                # Calculate average confidence for this combination
                combo_scores = []
                for entry in success_data:
                    entry_frags = tuple(sorted([f.get("fragment_id") for f in entry.get("answer_fragments", [])]))
                    if entry_frags == combination:
                        combo_scores.append(entry.get("confidence", 0.0))
                
                avg_confidence = statistics.mean(combo_scores) if combo_scores else 0.0
                
                candidates.append({
                    "fragment_ids": list(combination),
                    "occurrence_count": count,
                    "avg_confidence": round(avg_confidence, 2),
                    "recommendation": "COMPILE_TO_SYNAPSE" if avg_confidence > 80 else "MONITOR",
                    "reasoning": f"Appeared {count} times with {avg_confidence:.1f}% avg confidence"
                })
                
        return candidates

    def _analyze_halt_patterns(self, halt_data: List[Dict]) -> List[Dict]:
        """
        Analyze halt reasons to identify systematic knowledge gaps.
        """
        gap_report = []
        halt_reasons = Counter()
        domain_halts = defaultdict(list)
        
        for entry in halt_data:
            domain = entry.get("domain", "unknown")
            reason = entry.get("halt_reason", "unknown")
            query = entry.get("query", "")
            
            halt_reasons[reason] += 1
            domain_halts[domain].append({
                "reason": reason,
                "query": query,
                "missing_keywords": entry.get("missing_keywords", [])
            })
            
            self.domain_stats[domain]["halt_count"] += 1
        
        # Group by pattern
        for reason, count in halt_reasons.most_common():
            affected_domains = [d for d, halts in domain_halts.items() 
                              if any(h["reason"] == reason for h in halts)]
            
            # Extract common missing keywords
            all_keywords = []
            for domain in affected_domains:
                for halt in domain_halts[domain]:
                    if halt["reason"] == reason:
                        all_keywords.extend(halt.get("missing_keywords", []))
            
            common_keywords = [kw for kw, _ in Counter(all_keywords).most_common(5)]
            
            gap_report.append({
                "gap_type": reason,
                "occurrence_count": count,
                "affected_domains": affected_domains,
                "missing_keywords": common_keywords,
                "recommended_action": self._generate_recommended_action(reason, common_keywords),
                "priority": "HIGH" if count > 5 else "MEDIUM" if count > 2 else "LOW"
            })
            
        return gap_report

    def _generate_recommended_action(self, reason: str, keywords: List[str]) -> str:
        """Generate specific action recommendation for a gap."""
        if "no_fragments_found" in reason.lower():
            return f"Create new fragments covering keywords: {', '.join(keywords[:3])}"
        elif "monte_carlo" in reason.lower():
            return f"Add higher credibility fragments (peer_reviewed_study) for: {', '.join(keywords[:3])}"
        elif "philosophy_guard" in reason.lower():
            return f"Review safety rules for domain; add counter_argument fragments for: {', '.join(keywords[:3])}"
        elif "reasoning_role" in reason.lower():
            return f"Add missing reasoning roles (counter_argument/latest_data) for: {', '.join(keywords[:3])}"
        else:
            return f"Investigate fragments for: {', '.join(keywords[:3])}"


def main():
    """Run Night Mode consolidation."""
    engine = ConsolidationEngine()
    report = engine.run_night_mode()
    
    # Print summary
    print("\n" + "="*60)
    print("CONSOLIDATION SUMMARY")
    print("="*60)
    print(f"Date: {report['date']}")
    print(f"Successes: {report['summary']['total_successes']} | Halts: {report['summary']['total_halts']}")
    print(f"\nTop Synapse Candidates:")
    for i, syn in enumerate(report['synapse_candidates'][:3], 1):
        print(f"  {i}. {syn['fragment_ids']} ({syn['occurrence_count']}x, {syn['avg_confidence']}% conf)")
    
    print(f"\nTop Knowledge Gaps:")
    for i, gap in enumerate(report['gap_report'][:3], 1):
        print(f"  {i}. [{gap['priority']}] {gap['gap_type']} - {gap['recommended_action']}")


if __name__ == "__main__":
    main()
