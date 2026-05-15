#!/usr/bin/env python3
"""
P1: Validation Metrics Dashboard

Strategic Recommendation #2: Real-time visibility into knowledge quality, source credibility,
and system performance.

This dashboard provides:
- Source credibility distribution
- Fragment validation metrics
- Confidence score trends
- Domain-specific performance
- Hallucination attempt tracking
- System health indicators

Usage:
    from openeyes.ui.metrics_dashboard import MetricsDashboard
    
    dashboard = MetricsDashboard()
    dashboard.generate_report()
    dashboard.get_web_dashboard()  # Returns HTML for web UI
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MetricSnapshot:
    """Point-in-time metric snapshot."""
    timestamp: float
    total_fragments: int
    high_credibility_pct: float
    avg_confidence: float
    hallucination_blocks: int
    queries_processed: int
    avg_latency_ms: float


@dataclass
class DashboardData:
    """Complete dashboard data structure."""
    summary_metrics: Dict[str, Any]
    credibility_distribution: Dict[str, int]
    credibility_percentages: Dict[str, float] = None
    domain_performance: Dict[str, Dict[str, float]] = None
    confidence_trends: List[float] = None
    recent_activity: List[Dict[str, Any]] = None
    alerts: List[str] = None
    system_health: str = "UNKNOWN"
    last_updated: float = None


class MetricsDashboard:
    """
    Real-time metrics dashboard for OpenEyes knowledge quality.
    
    Aggregates data from:
    - KnowledgeQualityAssessor
    - UnifiedKnowledgeOrchestrator  
    - SourceCredibilityScorer
    - ValidationGate
    """
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / 'data' / 'metrics'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.data_dir / 'metrics_history.json'
        self.alerts_file = self.data_dir / 'alerts.json'
        
        # Load historical data
        self.history: List[MetricSnapshot] = []
        self.alerts: List[Dict[str, Any]] = []
        self._load_history()
    
    def _load_history(self):
        """Load metrics history from disk."""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    self.history = [MetricSnapshot(**s) for s in data.get('snapshots', [])]
                    self.alerts = data.get('alerts', [])
        except Exception as e:
            print(f"[DASHBOARD] Warning: Could not load history: {e}")
    
    def _save_history(self):
        """Persist metrics history to disk."""
        try:
            data = {
                'snapshots': [s.__dict__ for s in self.history[-1000:]],  # Keep last 1000
                'alerts': self.alerts[-100:]  # Keep last 100
            }
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[DASHBOARD] Warning: Could not save history: {e}")
    
    def collect_metrics(self) -> DashboardData:
        """
        Collect current metrics from all system components.
        
        Returns:
            DashboardData with complete system state
        """
        # Initialize collectors
        try:
            from openeyes.core.quality_assessor import KnowledgeQualityAssessor
            from openeyes.core.unified_orchestrator import get_orchestrator
            
            assessor = KnowledgeQualityAssessor()
            orchestrator = get_orchestrator()
            
            # Get orchestrator metrics
            orch_metrics = orchestrator.get_metrics()
            
            # Get assessor metrics
            assessor_metrics = assessor.metrics
            
            # Calculate credibility distribution
            credibility_dist = {
                'HIGH': assessor_metrics.high_credibility_count,
                'MEDIUM': assessor_metrics.medium_credibility_count,
                'LOW': assessor_metrics.low_credibility_count,
                'UNVERIFIED': assessor_metrics.total_fragments_processed - 
                             (assessor_metrics.high_credibility_count + 
                              assessor_metrics.medium_credibility_count + 
                              assessor_metrics.low_credibility_count)
            }
            
            # Calculate percentages
            total = max(1, sum(credibility_dist.values()))
            credibility_pct = {k: round(v / total * 100, 1) for k, v in credibility_dist.items()}
            
            # Domain performance
            domain_perf = {}
            for domain, count in assessor_metrics.domain_breakdown.items():
                domain_perf[domain] = {
                    'fragment_count': count,
                    'avg_confidence': 0.75,  # Would calculate from actual data
                    'success_rate': 0.95
                }
            
            # Confidence trends (last 10 snapshots)
            confidence_trends = []
            for snapshot in self.history[-10:]:
                confidence_trends.append(snapshot.avg_confidence)
            
            # If no history, use current
            if not confidence_trends:
                confidence_trends = [assessor_metrics.average_confidence] * 10
            
            # Generate alerts
            alerts = []
            if credibility_pct.get('LOW', 0) > 20:
                alerts.append("⚠️ High percentage of low-credibility sources detected")
            if orch_metrics.get('avg_latency_ms', 0) > 1000:
                alerts.append("⚠️ High average latency detected")
            if assessor_metrics.hallucination_attempts_blocked > 10:
                alerts.append(f"🛡️ {assessor_metrics.hallucination_attempts_blocked} hallucination attempts blocked")
            
            # Determine system health
            system_health = "HEALTHY"
            if len(alerts) > 2:
                system_health = "DEGRADED"
            if assessor_metrics.hallucination_attempts_blocked > 50:
                system_health = "CRITICAL"
            
            # Build dashboard data
            dashboard = DashboardData(
                summary_metrics={
                    'total_fragments': assessor_metrics.total_fragments_processed,
                    'queries_processed': orch_metrics.get('queries_processed', 0),
                    'avg_confidence': assessor_metrics.average_confidence,
                    'avg_latency_ms': orch_metrics.get('avg_latency_ms', 0),
                    'cache_hit_rate': 0.0,  # Would calculate from cache stats
                    'hallucination_blocks': assessor_metrics.hallucination_attempts_blocked,
                },
                credibility_distribution=credibility_dist,
                credibility_percentages=credibility_pct,
                domain_performance=domain_perf,
                confidence_trends=confidence_trends,
                recent_activity=[],  # Would populate from query log
                alerts=alerts,
                system_health=system_health,
                last_updated=time.time()
            )
            
            # Save snapshot to history
            snapshot = MetricSnapshot(
                timestamp=time.time(),
                total_fragments=dashboard.summary_metrics['total_fragments'],
                high_credibility_pct=credibility_pct.get('HIGH', 0),
                avg_confidence=assessor_metrics.average_confidence,
                hallucination_blocks=assessor_metrics.hallucination_attempts_blocked,
                queries_processed=orch_metrics.get('queries_processed', 0),
                avg_latency_ms=orch_metrics.get('avg_latency_ms', 0)
            )
            self.history.append(snapshot)
            self._save_history()
            
            return dashboard
            
        except Exception as e:
            print(f"[DASHBOARD] Error collecting metrics: {e}")
            # Return minimal dashboard on error
            return DashboardData(
                summary_metrics={'error': str(e)},
                credibility_distribution={},
                domain_performance={},
                confidence_trends=[],
                recent_activity=[],
                alerts=[f"Error collecting metrics: {e}"],
                system_health="UNKNOWN",
                last_updated=time.time()
            )
    
    def generate_report(self, output_file: str = None) -> str:
        """
        Generate human-readable metrics report.
        
        Args:
            output_file: Optional file path to save report
        
        Returns:
            Formatted report string
        """
        data = self.collect_metrics()
        
        report = []
        report.append("=" * 80)
        report.append("OPENEYES METRICS DASHBOARD")
        report.append(f"Generated: {datetime.fromtimestamp(data.last_updated).isoformat()}")
        report.append(f"System Health: {data.system_health}")
        report.append("=" * 80)
        
        # Summary metrics
        report.append("\n📊 SUMMARY METRICS")
        report.append("-" * 40)
        for key, value in data.summary_metrics.items():
            if isinstance(value, float):
                report.append(f"  {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                report.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Credibility distribution
        report.append("\n🎯 SOURCE CREDIBILITY DISTRIBUTION")
        report.append("-" * 40)
        for level, count in data.credibility_distribution.items():
            pct = data.credibility_percentages.get(level, 0)
            bar = "█" * int(pct / 5)
            report.append(f"  {level:12} {count:6} ({pct:5.1f}%) {bar}")
        
        # Domain performance
        if data.domain_performance:
            report.append("\n🌐 DOMAIN PERFORMANCE")
            report.append("-" * 40)
            for domain, metrics in data.domain_performance.items():
                report.append(f"  {domain.upper()}:")
                for key, value in metrics.items():
                    if isinstance(value, float):
                        report.append(f"    {key.replace('_', ' ').title()}: {value:.2f}")
                    else:
                        report.append(f"    {key.replace('_', ' ').title()}: {value}")
        
        # Confidence trend
        if data.confidence_trends:
            report.append("\n📈 CONFIDENCE TREND (Last 10 snapshots)")
            report.append("-" * 40)
            trend_str = " → ".join([f"{c:.2f}" for c in data.confidence_trends[-5:]])
            report.append(f"  {trend_str}")
            
            # Calculate trend direction
            if len(data.confidence_trends) >= 2:
                change = data.confidence_trends[-1] - data.confidence_trends[0]
                if change > 0.05:
                    report.append("  Trend: ⬆️ Improving")
                elif change < -0.05:
                    report.append("  Trend: ⬇️ Declining")
                else:
                    report.append("  Trend: ➡️ Stable")
        
        # Alerts
        if data.alerts:
            report.append("\n⚠️ ALERTS")
            report.append("-" * 40)
            for alert in data.alerts:
                report.append(f"  {alert}")
        else:
            report.append("\n✅ No active alerts")
        
        report.append("\n" + "=" * 80)
        
        report_str = "\n".join(report)
        
        # Save to file if requested
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(report_str)
                print(f"[DASHBOARD] Report saved to {output_file}")
            except Exception as e:
                print(f"[DASHBOARD] Error saving report: {e}")
        
        return report_str
    
    def get_web_dashboard(self) -> str:
        """
        Generate HTML dashboard for web UI.
        
        Returns:
            Complete HTML page with interactive charts
        """
        data = self.collect_metrics()
        
        # Prepare chart data
        confidence_labels = list(range(len(data.confidence_trends)))
        confidence_values = data.confidence_trends
        
        cred_labels = list(data.credibility_distribution.keys())
        cred_values = list(data.credibility_distribution.values())
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenEyes Metrics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .health-badge {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
        .health-healthy {{ background: #48bb78; }}
        .health-degraded {{ background: #ed8936; }}
        .health-critical {{ background: #f56565; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .alert {{ background: #fff5f5; border-left: 4px solid #f56565; padding: 10px; margin: 10px 0; }}
        h2 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👁️ OpenEyes Metrics Dashboard</h1>
            <p>Last Updated: {datetime.fromtimestamp(data.last_updated).strftime('%Y-%m-%d %H:%M:%S')}</p>
            <span class="health-badge health-{data.system_health.lower()}">{data.system_health}</span>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📊 Key Metrics</h2>
                <div class="metric-value">{data.summary_metrics.get('total_fragments', 0):,}</div>
                <div class="metric-label">Total Fragments</div>
                <br>
                <div class="metric-value">{data.summary_metrics.get('queries_processed', 0):,}</div>
                <div class="metric-label">Queries Processed</div>
                <br>
                <div class="metric-value">{data.summary_metrics.get('avg_confidence', 0):.2f}</div>
                <div class="metric-label">Average Confidence</div>
                <br>
                <div class="metric-value">{data.summary_metrics.get('avg_latency_ms', 0):.1f}ms</div>
                <div class="metric-label">Avg Latency</div>
            </div>
            
            <div class="card">
                <h2>🎯 Source Credibility</h2>
                <canvas id="credibilityChart"></canvas>
            </div>
            
            <div class="card">
                <h2>📈 Confidence Trend</h2>
                <canvas id="trendChart"></canvas>
            </div>
            
            <div class="card">
                <h2>⚠️ Alerts</h2>
                {''.join([f'<div class="alert">{alert}</div>' for alert in data.alerts]) or '<p>No active alerts ✅</p>'}
            </div>
        </div>
    </div>
    
    <script>
        // Credibility Distribution Chart
        const credCtx = document.getElementById('credibilityChart').getContext('2d');
        new Chart(credCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(cred_labels)},
                datasets: [{{
                    data: {json.dumps(cred_values)},
                    backgroundColor: ['#48bb78', '#4299e1', '#ed8936', '#f56565']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
        
        // Confidence Trend Chart
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        new Chart(trendCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(confidence_labels)},
                datasets: [{{
                    label: 'Confidence Score',
                    data: {json.dumps(confidence_values)},
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ min: 0, max: 1 }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        return html
    
    def export_metrics(self, format: str = 'json', output_file: str = None) -> str:
        """
        Export metrics in various formats.
        
        Args:
            format: 'json', 'csv', or 'html'
            output_file: Optional file path
        
        Returns:
            Exported data string
        """
        data = self.collect_metrics()
        
        if format == 'json':
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'summary': data.summary_metrics,
                'credibility': data.credibility_distribution,
                'domains': data.domain_performance,
                'trends': data.confidence_trends,
                'alerts': data.alerts,
                'health': data.system_health
            }
            result = json.dumps(export_data, indent=2)
        
        elif format == 'csv':
            lines = ['metric,value']
            for key, value in data.summary_metrics.items():
                lines.append(f'{key},{value}')
            result = '\n'.join(lines)
        
        else:
            result = self.get_web_dashboard()
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(result)
            print(f"[DASHBOARD] Exported to {output_file}")
        
        return result


# Singleton instance
_dashboard: Optional[MetricsDashboard] = None


def get_dashboard() -> MetricsDashboard:
    """Get or create dashboard singleton."""
    global _dashboard
    if _dashboard is None:
        _dashboard = MetricsDashboard()
    return _dashboard


if __name__ == '__main__':
    # Test the dashboard
    print("=" * 80)
    print("OPENEYES METRICS DASHBOARD - Test")
    print("=" * 80)
    
    dashboard = get_dashboard()
    
    # Generate text report
    report = dashboard.generate_report()
    print(report)
    
    # Export to JSON
    json_export = dashboard.export_metrics('json', '/workspace/test_results/metrics_export.json')
    print(f"\nJSON Export Preview: {json_export[:200]}...")
    
    # Save HTML dashboard
    html_dashboard = dashboard.get_web_dashboard()
    with open('/workspace/test_results/dashboard.html', 'w') as f:
        f.write(html_dashboard)
    print("\nHTML Dashboard saved to /workspace/test_results/dashboard.html")
    
    print("\n" + "=" * 80)
    print("Dashboard test complete!")
    print("=" * 80)
