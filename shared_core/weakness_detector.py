"""
Weakness Detector - Aggregates cross-run failure patterns and identifies language weaknesses.

The Weakness Detector transforms raw evolution data into actionable insights by:
- Tracking which primitives consistently fail across scenarios
- Identifying syntax gaps (missing constructs needed for scenarios)
- Detecting high-variance patterns (unstable under pressure)
- Finding philosophy violations that repeatedly occur
- Surfacing statistical signals from noise
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime


class WeaknessDetector:
    """Analyzes evolution history to detect systematic weaknesses."""
    
    def __init__(self, history_path: str = "evolution_data/history.json",
                 reports_dir: str = "reports/archive"):
        """
        Initialize Weakness Detector.
        
        Args:
            history_path: Path to gene pool history JSON
            reports_dir: Path to individual run reports (defaults to archive)
        """
        self.history_path = Path(history_path)
        self.reports_dir = Path(reports_dir)
        self.history: List[Dict] = []
        self.primitive_failures: Dict[str, List[Dict]] = defaultdict(list)
        self.scenario_failures: Dict[str, List[Dict]] = defaultdict(list)
        self.pattern_stats: Dict[str, Dict] = {}
        
        self.load_history()
    
    def load_history(self) -> None:
        """Load evolution history from file."""
        if not self.history_path.exists():
            print(f"⚠ History file not found: {self.history_path}")
            return
        
        try:
            with open(self.history_path, "r") as f:
                data = json.load(f)
                # Handle both list format and dict with 'runs' key
                if isinstance(data, list):
                    self.history = data
                elif isinstance(data, dict) and "runs" in data:
                    self.history = data["runs"]
                else:
                    self.history = [data] if data else []
            
            print(f"✓ Loaded {len(self.history)} evolution runs")
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠ Failed to load history: {e}")
            self.history = []
    
    def load_run_reports(self) -> List[Dict]:
        """Load individual run reports from the reports directory."""
        reports = []
        
        if not self.reports_dir.exists():
            return reports
        
        for file in self.reports_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    report = json.load(f)
                    # Add metadata from filename
                    report["_source_file"] = file.name
                    reports.append(report)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠ Failed to load report {file}: {e}")
        
        return reports
    
    def analyze_primitive_failures(self) -> Dict[str, Any]:
        """
        Analyze which primitives consistently appear in failed compositions.
        
        Returns:
            Dict mapping primitive IDs to failure statistics
        """
        primitive_stats = defaultdict(lambda: {
            "failure_count": 0,
            "success_count": 0,
            "total_appearances": 0,
            "failure_rate": 0.0,
            "avg_score_when_failed": 0.0,
            "scenarios_failed_in": []
        })
        
        # Load all run reports
        reports = self.load_run_reports()
        
        for report in reports:
            if report is None:
                continue
                
            survived = report.get("survives", report.get("survived", False))
            composition = report.get("selected", report.get("composition", []))
            score = report.get("score", report.get("mean_score", 0))
            scenario_data = report.get("scenario")
            scenario = scenario_data.get("id", "unknown") if scenario_data else "general"
            
            for primitive in composition:
                pid = primitive.get("id", "unknown")
                p_content = primitive.get("content", "unknown")
                
                stats = primitive_stats[pid]
                stats["total_appearances"] += 1
                
                if survived:
                    stats["success_count"] += 1
                else:
                    stats["failure_count"] += 1
                    stats["scenarios_failed_in"].append(scenario)
                    
                    # Track average score when this primitive was present in failures
                    old_avg = stats["avg_score_when_failed"]
                    count = stats["failure_count"]
                    stats["avg_score_when_failed"] = ((old_avg * (count - 1)) + score) / count
        
        # Calculate failure rates
        for pid, stats in primitive_stats.items():
            if stats["total_appearances"] > 0:
                stats["failure_rate"] = (
                    stats["failure_count"] / stats["total_appearances"]
                )
        
        # Identify high-risk primitives (failure rate > 60%)
        high_risk = {
            pid: stats for pid, stats in primitive_stats.items()
            if stats["failure_count"] >= 3 and stats["failure_rate"] > 0.6
        }
        
        return {
            "all_primitives": dict(primitive_stats),
            "high_risk_primitives": high_risk,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def analyze_scenario_patterns(self) -> Dict[str, Any]:
        """
        Analyze which scenarios consistently cause failures.
        
        Returns:
            Dict mapping scenario IDs to failure statistics
        """
        scenario_stats = defaultdict(lambda: {
            "run_count": 0,
            "failure_count": 0,
            "success_count": 0,
            "failure_rate": 0.0,
            "avg_score": 0.0,
            "common_failure_reasons": []
        })
        
        reports = self.load_run_reports()
        
        for report in reports:
            if report is None:
                continue
                
            survived = report.get("survives", report.get("survived", False))
            scenario_data = report.get("scenario")
            scenario_id = scenario_data.get("id", "general") if scenario_data else "general"
            score = report.get("score", report.get("mean_score", 0))
            
            stats = scenario_stats[scenario_id]
            stats["run_count"] += 1
            
            # Update running average score
            old_avg = stats["avg_score"]
            count = stats["run_count"]
            stats["avg_score"] = ((old_avg * (count - 1)) + score) / count
            
            if survived:
                stats["success_count"] += 1
            else:
                stats["failure_count"] += 1
                
                # Extract failure reasons
                criteria = report.get("criteria", {})
                if not criteria.get("score_ok", True):
                    stats["common_failure_reasons"].append("low_score")
                if not criteria.get("stability_ok", True):
                    stats["common_failure_reasons"].append("high_variance")
                if not criteria.get("probability_ok", True):
                    stats["common_failure_reasons"].append("low_survival_probability")
        
        # Calculate failure rates
        for sid, stats in scenario_stats.items():
            if stats["run_count"] > 0:
                stats["failure_rate"] = stats["failure_count"] / stats["run_count"]
        
        # Identify problematic scenarios (failure rate > 50% with min 3 runs)
        problematic = {
            sid: stats for sid, stats in scenario_stats.items()
            if stats["run_count"] >= 3 and stats["failure_rate"] > 0.5
        }
        
        return {
            "all_scenarios": dict(scenario_stats),
            "problematic_scenarios": problematic,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def detect_syntax_gaps(self) -> List[Dict]:
        """
        Detect missing syntax constructs by analyzing scenario requirements
        vs available primitives.
        
        Returns:
            List of detected gaps with evidence
        """
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        
        gaps = []
        
        # Load scenarios to check expected constructs
        from core.scenario_engine import ScenarioEngine
        engine = ScenarioEngine()
        
        # Count how often each construct is required
        construct_requirements = defaultdict(int)
        for scenario in engine.scenarios:
            for construct in scenario.get("expected_constructs", []):
                construct_requirements[construct] += 1
        
        # Load available primitives
        from evolution.primitive_registry import load_primitives
        primitives = load_primitives()
        
        # Map primitives to construct types via tags
        available_constructs = set()
        for p in primitives:
            for tag in p.get("tags", []):
                available_constructs.add(tag)
        
        # Find constructs that are frequently required but rarely available
        for construct, req_count in construct_requirements.items():
            if construct not in available_constructs and req_count >= 2:
                gaps.append({
                    "construct": construct,
                    "required_by_scenarios": req_count,
                    "evidence": f"Required by {req_count} scenarios but no primitive tagged with '{construct}'",
                    "severity": "high" if req_count >= 5 else "medium",
                    "recommendation": f"Add primitive supporting '{construct}' construct"
                })
        
        # Also check for forbidden patterns that appear frequently
        forbidden_patterns = defaultdict(int)
        reports = self.load_run_reports()
        
        for report in reports:
            if report is None:
                continue
            scenario_data = report.get("scenario")
            forbidden = scenario_data.get("forbidden_patterns", []) if scenario_data else []
            composition = report.get("selected", [])
            
            # Check if composition contains dangerous patterns
            for primitive in composition:
                tags = primitive.get("tags", [])
                if "danger" in tags:
                    forbidden_patterns["danger_primitive"] += 1
        
        for pattern, count in forbidden_patterns.items():
            if count >= 3:
                # Skip internal safeguard constructs - they're not real syntax gaps
                # The recommendation is to add constraints, not a new primitive
                gaps.append({
                    "construct": f"_internal_constraint_{pattern}",  # Mark as internal
                    "required_by_scenarios": count,
                    "evidence": f"Dangerous pattern appeared in {count} compositions",
                    "severity": "high",
                    "recommendation": f"Add constraints or safer alternatives for {pattern}",
                    "_is_constraint": True  # Flag for dashboard to skip syntax generation
                })
        
        return gaps
    
    def detect_philosophy_violations(self) -> List[Dict]:
        """
        Detect repeated philosophy violations across runs.
        
        Returns:
            List of violation patterns
        """
        violations = []
        violation_counts = defaultdict(int)
        
        reports = self.load_run_reports()
        
        for report in reports:
            if report is None:
                continue
            scenario_data = report.get("scenario")
            philosophy_checks = scenario_data.get("philosophy_checks", []) if scenario_data else []
            
            # Check for cognitive simplicity violations (high variance = confusing)
            variance = report.get("variance", 0)
            if variance > 50:  # High variance threshold
                violation_counts["cognitive_complexity"] += 1
            
            # Check for determinism violations
            simulator_scores = report.get("simulator_scores", [])
            if simulator_scores:
                score_range = max(simulator_scores) - min(simulator_scores)
                if score_range > 40:  # Large disagreement between simulators
                    violation_counts["inconsistent_behavior"] += 1
            
            # Check for danger patterns
            composition = report.get("selected", [])
            for primitive in composition:
                if "danger" in primitive.get("tags", []):
                    violation_counts["danger_primitive_usage"] += 1
        
        # Convert counts to violation reports
        for vtype, count in violation_counts.items():
            if count >= 3:  # Minimum threshold for pattern detection
                violations.append({
                    "type": vtype,
                    "occurrence_count": count,
                    "severity": "high" if count >= 10 else "medium",
                    "description": self._get_violation_description(vtype),
                    "recommendation": self._get_violation_recommendation(vtype)
                })
        
        return violations
    
    def _get_violation_description(self, vtype: str) -> str:
        """Get human-readable description for violation type."""
        descriptions = {
            "cognitive_complexity": "Compositions show high variance across simulators, indicating cognitive complexity",
            "inconsistent_behavior": "Large score disagreements between simulators suggest inconsistent language behavior",
            "danger_primitive_usage": "Dangerous primitives (e.g., 'repeat forever') appearing frequently in compositions"
        }
        return descriptions.get(vtype, f"Unknown violation type: {vtype}")
    
    def _get_violation_recommendation(self, vtype: str) -> str:
        """Get recommendation for addressing violation type."""
        recommendations = {
            "cognitive_complexity": "Simplify primitives or add constraints to reduce cognitive load",
            "inconsistent_behavior": "Clarify primitive semantics to ensure consistent interpretation",
            "danger_primitive_usage": "Replace dangerous primitives with safer alternatives or add mandatory guards"
        }
        return recommendations.get(vtype, "Review and address the violation pattern")
    
    def generate_weakness_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive weakness analysis report.
        
        Returns:
            Complete weakness report with all findings
        """
        primitive_analysis = self.analyze_primitive_failures()
        scenario_analysis = self.analyze_scenario_patterns()
        syntax_gaps = self.detect_syntax_gaps()
        philosophy_violations = self.detect_philosophy_violations()
        
        # Calculate overall health metrics
        total_runs = len(self.load_run_reports())
        failed_runs = sum(1 for r in self.load_run_reports() 
                         if not r.get("survives", r.get("survived", False)))
        
        survival_rate = (total_runs - failed_runs) / total_runs if total_runs > 0 else 0
        
        report = {
            "summary": {
                "total_runs_analyzed": total_runs,
                "overall_survival_rate": round(survival_rate, 2),
                "high_risk_primitives_count": len(primitive_analysis["high_risk_primitives"]),
                "problematic_scenarios_count": len(scenario_analysis["problematic_scenarios"]),
                "syntax_gaps_detected": len(syntax_gaps),
                "philosophy_violations_count": len(philosophy_violations)
            },
            "primitive_weaknesses": primitive_analysis,
            "scenario_weaknesses": scenario_analysis,
            "syntax_gaps": syntax_gaps,
            "philosophy_violations": philosophy_violations,
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def save_report(self, output_path: str = "reports/weakness_analysis.json") -> str:
        """
        Generate and save weakness report to file.
        
        Args:
            output_path: Path to save the report
        
        Returns:
            Path where report was saved
        """
        report = self.generate_weakness_report()
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Weakness report saved to {output}")
        return str(output)


# Convenience function
def detect_weaknesses(history_path: str = "evolution_data/history.json") -> Dict[str, Any]:
    """
    Quick function to detect weaknesses and return report.
    
    Args:
        history_path: Path to evolution history
    
    Returns:
        Weakness analysis report
    """
    detector = WeaknessDetector(history_path)
    return detector.generate_weakness_report()


if __name__ == "__main__":
    print("\n=== WEAKNESS DETECTOR ANALYSIS ===\n")
    
    detector = WeaknessDetector()
    report = detector.generate_weakness_report()
    
    print("SUMMARY:")
    print(f"  Total runs analyzed: {report['summary']['total_runs_analyzed']}")
    print(f"  Overall survival rate: {report['summary']['overall_survival_rate']:.0%}")
    print(f"  High-risk primitives: {report['summary']['high_risk_primitives_count']}")
    print(f"  Problematic scenarios: {report['summary']['problematic_scenarios_count']}")
    print(f"  Syntax gaps detected: {report['summary']['syntax_gaps_detected']}")
    print(f"  Philosophy violations: {report['summary']['philosophy_violations_count']}")
    
    if report["syntax_gaps"]:
        print("\nSYNTAX GAPS:")
        for gap in report["syntax_gaps"][:3]:
            print(f"  - {gap['construct']}: {gap['evidence']}")
    
    if report["philosophy_violations"]:
        print("\nPHILOSOPHY VIOLATIONS:")
        for violation in report["philosophy_violations"][:3]:
            print(f"  - {violation['type']}: {violation['description']}")
    
    # Save detailed report
    detector.save_report()
