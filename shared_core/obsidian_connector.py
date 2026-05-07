"""
Obsidian Connector - Phase 1: Write-only ledger for evolutionary tracking

This module automatically tracks:
- Surviving compositions after each run
- Failed patterns and why they failed
- Primitive lineage (weight evolution over time)
- Emergent idioms and patterns
- Run metadata and aggregate statistics

Usage: Call report_to_obsidian() after each Monte Carlo evolution cycle.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class ObsidianReporter:
    """Write-only reporter that pushes markdown files to Obsidian vault."""
    
    def __init__(self, vault_path: str = None):
        """
        Initialize Obsidian reporter.
        
        Args:
            vault_path: Path to Obsidian vault. If None, uses E_PLUS_OBSIDIAN_VAULT env var
                       or defaults to ./obsidian_vault
        """
        self.vault_path = Path(
            vault_path or 
            os.getenv("E_PLUS_OBSIDIAN_VAULT", "./obsidian_vault")
        )
        self.reports_dir = self.vault_path / "E-AR Reports"
        self.primitives_dir = self.vault_path / "Primitive Lineage"
        self.idioms_dir = self.vault_path / "Emergent Idioms"
        self.failures_dir = self.vault_path / "Failed Patterns"
        
        # Create directories if they don't exist
        for directory in [self.reports_dir, self.primitives_dir, 
                         self.idioms_dir, self.failures_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _generate_timestamp(self) -> str:
        """Generate ISO format timestamp for filenames."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _format_primitive_list(self, primitives: List[Dict]) -> str:
        """Format primitive list as markdown table."""
        if not primitives:
            return "_No primitives_"
        
        lines = ["| ID | Name | Weight | Role |", "|---|---|---|---|"]
        for p in primitives:
            pid = p.get("id", "unknown")
            name = p.get("name", p.get("code", "unnamed")[:30])
            weight = p.get("weight", 0)
            role = p.get("role", "primitive")
            lines.append(f"| {pid} | {name} | {weight} | {role} |")
        
        return "\n".join(lines)
    
    def report_run(self, mc_result: Dict[str, Any], run_metadata: Dict[str, Any] = None):
        """
        Report a complete Monte Carlo evolution run.
        
        Args:
            mc_result: Result from monte_carlo_evolve()
            run_metadata: Optional additional metadata (cycle number, task description, etc.)
        """
        timestamp = self._generate_timestamp()
        filename = f"run_{timestamp}.md"
        filepath = self.reports_dir / filename
        
        winner = mc_result
        aggregate = mc_result.get("aggregate_stats", {})
        
        # Build markdown report
        md_content = f"""# E-AR Evolution Run Report

**Timestamp:** {datetime.now().isoformat()}
**Cycle:** {run_metadata.get('cycle', 'N/A') if run_metadata else 'N/A'}
**Task:** {run_metadata.get('task', 'General evolution') if run_metadata else 'General evolution'}

## Summary

- **Total Samples:** {aggregate.get('total_samples', 0)}
- **Stable Samples:** {aggregate.get('stable_samples', 0)}
- **Viable Samples:** {aggregate.get('viable_samples', 0)}
- **Best Score:** {winner.get('mean_score', 0)}
- **Average Score:** {aggregate.get('average_score', 0)}
- **Survival Decision:** {'✅ PASSED' if mc_result.get('survived', False) else '❌ FAILED'}

## Winning Composition

### Metrics
- **Mean Score:** {winner.get('mean_score', 0)}
- **Variance (Stability):** {winner.get('variance', 0)}
- **Worst Case:** {winner.get('worst_case', 0)}
- **Survival Probability:** {winner.get('survival_probability', 0)}

### Primitives Used

{self._format_primitive_list(winner.get('composition', []))}

### Simulator Scores
{self._format_simulator_scores(winner.get('pressure_result', {}))}

## Distribution Statistics

- **Min Score:** {aggregate.get('score_distribution', {}).get('min', 0)}
- **Max Score:** {aggregate.get('score_distribution', {}).get('max', 0)}
- **Std Dev:** {aggregate.get('score_distribution', {}).get('std_dev', 0)}

## Survival Criteria Breakdown

{self._format_survival_criteria(mc_result)}

---
*Generated automatically by E-AR Obsidian Reporter*
"""
        
        with open(filepath, 'w') as f:
            f.write(md_content)
        
        # Track failures separately
        if not mc_result.get('survived', False):
            self._report_failure(winner, timestamp, run_metadata)
        
        return filepath
    
    def _format_simulator_scores(self, pressure_result: Dict) -> str:
        """Format simulator scores as markdown list."""
        if not pressure_result or 'simulators' not in pressure_result:
            return "_No simulator data_"
        
        lines = []
        for sim in pressure_result['simulators']:
            for key, value in sim.items():
                if isinstance(value, (int, float)) and key.endswith('_score'):
                    sim_name = key.replace('_score', '').replace('_', ' ').title()
                    lines.append(f"- **{sim_name}:** {value}")
        
        return "\n".join(lines) if lines else "_No scores recorded_"
    
    def _format_survival_criteria(self, result: Dict) -> str:
        """Format survival criteria breakdown."""
        # Handle both nested and flat structures
        criteria = result.get('criteria', {})
        metrics = result.get('metrics', {})
        thresholds = result.get('thresholds', {})
        
        # If criteria is empty but we have direct fields, use those
        if not criteria and 'survived' in result:
            # Fallback to direct access for backward compatibility
            score = result.get('mean_score', result.get('score', 0))
            variance = result.get('variance', 0)
            survival_prob = result.get('survival_probability', 0)
            
            score_threshold = 60
            variance_threshold = 50
            survival_prob_threshold = 0.7
            
            score_ok = score >= score_threshold
            stability_ok = variance < variance_threshold
            probability_ok = survival_prob >= survival_prob_threshold
            
            return (
                f"1. **Score Check:** {'✅' if score_ok else '❌'} "
                f"(score={score}, threshold={score_threshold})\n"
                f"2. **Stability Check:** {'✅' if stability_ok else '❌'} "
                f"(variance={variance}, threshold={variance_threshold})\n"
                f"3. **Probability Check:** {'✅' if probability_ok else '❌'} "
                f"(prob={survival_prob}, threshold={survival_prob_threshold})"
            )
        
        if not criteria:
            return "_No criteria data available_"
        
        lines = [
            f"1. **Score Check:** {'✅' if criteria.get('score_ok') else '❌'} "
            f"(score={metrics.get('score', 0)}, threshold={thresholds.get('score_threshold', 60)})",
            f"2. **Stability Check:** {'✅' if criteria.get('stability_ok') else '❌'} "
            f"(variance={metrics.get('variance', 0)}, threshold={thresholds.get('variance_threshold', 50)})",
            f"3. **Probability Check:** {'✅' if criteria.get('probability_ok') else '❌'} "
            f"(prob={metrics.get('survival_probability', 0)}, threshold={thresholds.get('survival_prob_threshold', 0.7)})"
        ]
        
        return "\n".join(lines)
    
    def _report_failure(self, result: Dict, timestamp: str, metadata: Dict = None):
        """Report failed composition to failures directory."""
        filename = f"failure_{timestamp}.md"
        filepath = self.failures_dir / filename
        
        md_content = f"""# Failed Composition

**Timestamp:** {datetime.now().isoformat()}
**Cycle:** {metadata.get('cycle', 'N/A') if metadata else 'N/A'}

## Why It Failed

{self._format_survival_criteria(result)}

## Composition Details

### Primitives
{self._format_primitive_list(result.get('composition', []))}

### Metrics
- Mean Score: {result.get('mean_score', 0)} (required: ≥60)
- Variance: {result.get('variance', 0)} (required: <50)
- Survival Probability: {result.get('survival_probability', 0)} (required: ≥0.7)

## Learning Points

_Analyze this failure to identify:_
- Which primitives consistently appear in failures?
- What composition patterns lead to high variance?
- Are there incompatible primitive combinations?

---
*Auto-generated failure report*
"""
        
        with open(filepath, 'w') as f:
            f.write(md_content)
    
    def track_primitive_lineage(self, gene_pool: Dict[str, Dict]):
        """
        Track weight evolution of primitives over time.
        
        Args:
            gene_pool: Current state of gene pool from survival.py
        """
        timestamp = self._generate_timestamp()
        filename = f"lineage_{timestamp}.json"
        filepath = self.primitives_dir / filename
        
        # Convert to time-series format
        lineage_data = {
            "timestamp": datetime.now().isoformat(),
            "primitives": {}
        }
        
        for pid, pdata in gene_pool.items():
            lineage_data["primitives"][pid] = {
                "weight": pdata.get("weight", 0),
                "name": pdata.get("name", "unknown"),
                "usage_count": pdata.get("usage_count", 0)
            }
        
        with open(filepath, 'w') as f:
            json.dump(lineage_data, f, indent=2)
        
        return filepath
    
    def record_emergent_idiom(self, idiom_name: str, pattern: List[str], 
                             frequency: int, avg_score: float, examples: List[Dict]):
        """
        Record an emergent idiom/pattern discovered through evolution.
        
        Args:
            idiom_name: Human-readable name for the pattern
            pattern: List of primitive IDs that form the pattern
            frequency: How often this pattern appears
            avg_score: Average score when this pattern is used
            examples: Example compositions using this pattern
        """
        timestamp = self._generate_timestamp()
        filename = f"idiom_{idiom_name.replace(' ', '_').lower()}_{timestamp}.md"
        filepath = self.idioms_dir / filename
        
        md_content = f"""# Emergent Idiom: {idiom_name}

**Discovered:** {datetime.now().isoformat()}
**Frequency:** {frequency} occurrences
**Average Score:** {avg_score:.2f}

## Pattern Definition

Primitives involved:
{chr(10).join(f'- `{pid}`' for pid in pattern)}

## Characteristics

- Appears in {frequency} compositions
- Maintains average score of {avg_score:.2f}
- Shows stability across multiple runs

## Example Compositions

{self._format_examples(examples)}

## Hypothesis

_Why does this pattern work well? What makes it stable?_

---
*Auto-detected emergent pattern*
"""
        
        with open(filepath, 'w') as f:
            f.write(md_content)
        
        return filepath
    
    def _format_examples(self, examples: List[Dict]) -> str:
        """Format example compositions."""
        if not examples:
            return "_No examples recorded_"
        
        lines = []
        for i, ex in enumerate(examples[:3], 1):  # Show max 3 examples
            lines.append(f"### Example {i}")
            lines.append(f"**Score:** {ex.get('mean_score', 0)}")
            lines.append(f"**Primitives:** {', '.join(str(p.get('id')) for p in ex.get('composition', []))}")
            lines.append("")
        
        return "\n".join(lines)


def report_to_obsidian(mc_result: Dict, metadata: Dict = None, vault_path: str = None):
    """
    Convenience function to report a run to Obsidian.
    
    Args:
        mc_result: Result from monte_carlo_evolve()
        metadata: Optional run metadata
        vault_path: Optional custom vault path
    """
    reporter = ObsidianReporter(vault_path)
    return reporter.report_run(mc_result, metadata)


def track_gene_pool(gene_pool: Dict, vault_path: str = None):
    """
    Convenience function to track gene pool state.
    
    Args:
        gene_pool: Current gene pool state
        vault_path: Optional custom vault path
    """
    reporter = ObsidianReporter(vault_path)
    return reporter.track_primitive_lineage(gene_pool)
