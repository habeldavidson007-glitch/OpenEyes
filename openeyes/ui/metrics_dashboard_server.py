"""
Metrics Dashboard UI for OpenEyes
Real-time web interface for monitoring knowledge quality, system health, and performance metrics.
Built with Flask for simplicity, can be replaced with FastAPI/React for production.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from flask import Flask, render_template_string, jsonify, request
import logging

from .database_client import get_database
from .quality_assessor import get_assessor

logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML Template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenEyes Metrics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { 
            color: white; 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .metric:last-child { border-bottom: none; }
        .metric-label { color: #666; font-weight: 500; }
        .metric-value { 
            font-size: 1.4em; 
            font-weight: bold;
            color: #333;
        }
        .metric-value.good { color: #10b981; }
        .metric-value.warning { color: #f59e0b; }
        .metric-value.bad { color: #ef4444; }
        .chart-container {
            position: relative;
            height: 250px;
            margin-top: 15px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-good { background: #10b981; }
        .status-warning { background: #f59e0b; }
        .status-bad { background: #ef4444; }
        .refresh-btn {
            background: white;
            color: #667eea;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            display: block;
            margin: 20px auto;
            transition: all 0.3s ease;
        }
        .refresh-btn:hover {
            background: #f0f0f0;
            transform: scale(1.05);
        }
        .last-updated {
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 20px;
            font-size: 0.9em;
        }
        .feedback-section {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-top: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .feedback-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 15px;
        }
        .feedback-form input, .feedback-form textarea, .feedback-form select {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1em;
        }
        .feedback-form button {
            grid-column: span 2;
            background: #667eea;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 6px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
        }
        .feedback-form button:hover {
            background: #5568d3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>👁️ OpenEyes Metrics Dashboard</h1>
        
        <div class="grid">
            <!-- System Health Card -->
            <div class="card">
                <h2>📊 System Health</h2>
                <div class="metric">
                    <span class="metric-label">Overall Status</span>
                    <span class="metric-value good" id="overall-status">
                        <span class="status-indicator status-good"></span>HEALTHY
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Fragments</span>
                    <span class="metric-value" id="total-fragments">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Avg Quality Score</span>
                    <span class="metric-value good" id="avg-quality">0.00</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Hallucinations Blocked</span>
                    <span class="metric-value good" id="hallucinations-blocked">0</span>
                </div>
            </div>

            <!-- Credibility Distribution Card -->
            <div class="card">
                <h2>🎯 Source Credibility</h2>
                <div class="chart-container">
                    <canvas id="credibility-chart"></canvas>
                </div>
            </div>

            <!-- Domain Activity Card -->
            <div class="card">
                <h2>🌐 Domain Activity</h2>
                <div class="chart-container">
                    <canvas id="domain-chart"></canvas>
                </div>
            </div>

            <!-- Performance Metrics Card -->
            <div class="card">
                <h2>⚡ Performance</h2>
                <div class="metric">
                    <span class="metric-label">Avg Latency (ms)</span>
                    <span class="metric-value good" id="avg-latency">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Cache Hit Rate</span>
                    <span class="metric-value" id="cache-hit-rate">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Queries (24h)</span>
                    <span class="metric-value" id="queries-24h">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">API Success Rate</span>
                    <span class="metric-value good" id="api-success">100%</span>
                </div>
            </div>
        </div>

        <!-- Feedback Section -->
        <div class="feedback-section">
            <h2>💬 Submit Feedback</h2>
            <p style="color: #666; margin-bottom: 15px;">Help improve OpenEyes by providing feedback on query results.</p>
            <form class="feedback-form" id="feedback-form">
                <input type="text" id="query-id" placeholder="Query ID (optional)" />
                <select id="domain">
                    <option value="Healthcare">Healthcare</option>
                    <option value="Economy">Economy</option>
                    <option value="Governance">Governance</option>
                    <option value="Investment">Investment</option>
                    <option value="General">General</option>
                </select>
                <select id="accuracy">
                    <option value="true">✅ Accurate</option>
                    <option value="false">❌ Inaccurate</option>
                </select>
                <input type="number" id="rating" min="1" max="5" placeholder="Rating (1-5)" />
                <textarea id="comments" rows="2" placeholder="Additional comments..." style="grid-column: span 2;"></textarea>
                <button type="submit">Submit Feedback</button>
            </form>
            <div id="feedback-message" style="margin-top: 15px; padding: 10px; border-radius: 6px; display: none;"></div>
        </div>

        <button class="refresh-btn" onclick="loadMetrics()">🔄 Refresh Metrics</button>
        <div class="last-updated" id="last-updated">Last updated: Never</div>
    </div>

    <script>
        let credibilityChart, domainChart;

        function initCharts() {
            // Credibility Chart
            const credCtx = document.getElementById('credibility-chart').getContext('2d');
            credibilityChart = new Chart(credCtx, {
                type: 'doughnut',
                data: {
                    labels: ['High', 'Medium', 'Low'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });

            // Domain Chart
            const domainCtx = document.getElementById('domain-chart').getContext('2d');
            domainChart = new Chart(domainCtx, {
                type: 'bar',
                data: {
                    labels: ['Healthcare', 'Economy', 'Governance', 'Investment', 'General'],
                    datasets: [{
                        label: 'Queries',
                        data: [0, 0, 0, 0, 0],
                        backgroundColor: '#667eea'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }

        async function loadMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();

                // Update System Health
                document.getElementById('total-fragments').textContent = data.total_fragments || 0;
                document.getElementById('avg-quality').textContent = (data.average_quality_score || 0).toFixed(2);
                document.getElementById('hallucinations-blocked').textContent = data.hallucinations_blocked || 0;

                // Update Credibility Chart
                if (data.credibility_distribution) {
                    credibilityChart.data.datasets[0].data = [
                        data.credibility_distribution.high || 0,
                        data.credibility_distribution.medium || 0,
                        data.credibility_distribution.low || 0
                    ];
                    credibilityChart.update();
                }

                // Update Domain Chart
                if (data.domain_activity) {
                    const domains = ['Healthcare', 'Economy', 'Governance', 'Investment', 'General'];
                    const values = domains.map(d => data.domain_activity[d] || 0);
                    domainChart.data.datasets[0].data = values;
                    domainChart.update();
                }

                // Update Performance
                document.getElementById('avg-latency').textContent = (data.avg_latency_ms || 0).toFixed(1);
                document.getElementById('cache-hit-rate').textContent = (data.cache_hit_rate || 0).toFixed(1) + '%';
                document.getElementById('queries-24h').textContent = data.queries_24h || 0;

                // Update timestamp
                document.getElementById('last-updated').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
            } catch (error) {
                console.error('Error loading metrics:', error);
            }
        }

        // Feedback form handler
        document.getElementById('feedback-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const feedback = {
                query_id: document.getElementById('query-id').value || null,
                domain: document.getElementById('domain').value,
                was_accurate: document.getElementById('accuracy').value === 'true',
                user_rating: parseInt(document.getElementById('rating').value) || null,
                comments: document.getElementById('comments').value
            };

            try {
                const response = await fetch('/api/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(feedback)
                });
                const result = await response.json();
                
                const msgDiv = document.getElementById('feedback-message');
                msgDiv.style.display = 'block';
                if (result.success) {
                    msgDiv.style.background = '#d1fae5';
                    msgDiv.style.color = '#065f46';
                    msgDiv.textContent = '✅ Thank you for your feedback!';
                } else {
                    msgDiv.style.background = '#fee2e2';
                    msgDiv.style.color = '#991b1b';
                    msgDiv.textContent = '❌ Error submitting feedback. Please try again.';
                }
                
                setTimeout(() => { msgDiv.style.display = 'none'; }, 3000);
                e.target.reset();
            } catch (error) {
                console.error('Error submitting feedback:', error);
            }
        });

        // Initialize on page load
        window.onload = () => {
            initCharts();
            loadMetrics();
            // Auto-refresh every 30 seconds
            setInterval(loadMetrics, 30000);
        };
    </script>
</body>
</html>
"""

class MetricsDashboard:
    """
    Web-based metrics dashboard for monitoring OpenEyes system health and performance.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        self.db = get_database()
        self.assessor = get_assessor()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes for the dashboard."""
        
        @app.route('/')
        def dashboard():
            """Render the main dashboard."""
            return render_template_string(DASHBOARD_HTML)
        
        @app.route('/api/metrics')
        def get_metrics():
            """API endpoint for metrics data."""
            try:
                db_metrics = self.db.get_metrics_summary(hours=24)
                assessor_data = self.assessor.get_metrics_dashboard_data()
                
                # Combine metrics
                metrics = {
                    'total_fragments': assessor_data.get('total_fragments', 0),
                    'average_quality_score': assessor_data.get('average_quality_score', 0.0),
                    'hallucinations_blocked': assessor_data.get('hallucinations_blocked', 0),
                    'credibility_distribution': assessor_data.get('credibility_distribution', {}),
                    'domain_activity': assessor_data.get('domain_activity', {}),
                    'avg_latency_ms': 0.0,  # Would calculate from db_metrics
                    'cache_hit_rate': 0.0,  # Would calculate from cache stats
                    'queries_24h': sum(db_metrics.get('domain_counts', {}).values()),
                    'timestamp': time.time()
                }
                
                return jsonify(metrics)
            except Exception as e:
                logger.error(f"Error getting metrics: {e}")
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/feedback', methods=['POST'])
        def submit_feedback():
            """API endpoint for submitting user feedback."""
            try:
                data = request.json
                feedback_id = self.db.store_feedback(
                    query_id=data.get('query_id'),
                    domain=data.get('domain', 'General'),
                    was_accurate=data.get('was_accurate', True),
                    user_rating=data.get('user_rating'),
                    comments=data.get('comments')
                )
                
                return jsonify({
                    'success': True,
                    'feedback_id': feedback_id,
                    'message': 'Feedback recorded successfully'
                })
            except Exception as e:
                logger.error(f"Error submitting feedback: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @app.route('/api/health')
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time()
            })
    
    def run(self, debug: bool = False):
        """Start the dashboard server."""
        logger.info(f"Starting Metrics Dashboard on http://{self.host}:{self.port}")
        app.run(host=self.host, port=self.port, debug=debug)


def start_dashboard(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Convenience function to start the metrics dashboard."""
    dashboard = MetricsDashboard(host, port)
    dashboard.run(debug)


if __name__ == '__main__':
    start_dashboard(debug=True)
