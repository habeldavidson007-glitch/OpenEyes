# OpenEyes CLI Metrics Guide

## Overview
OpenEyes uses a **CLI-first approach** for metrics and monitoring. All quality metrics, confidence scores, and system health data are available directly through command-line interfaces and database queries.

---

## Quick Start

### 1. Run Query with Metrics
```bash
python -m openeyes.main "What is the current inflation rate?" --verbose
```

**Output includes:**
- Answer with source citations
- Confidence score (0-100%)
- Source credibility rating (HIGH/MEDIUM/LOW/UNVERIFIED)
- Retrieval method used (Cache/Local/API)
- Execution time

### 2. View Recent Metrics from Database
```bash
sqlite3 /workspace/openeyes_data/openeyes.db \
  "SELECT timestamp, domain, confidence_score, source_credibility, latency_ms \
   FROM metrics ORDER BY timestamp DESC LIMIT 10;"
```

### 3. Check Feedback Statistics
```bash
sqlite3 /workspace/openeyes_data/openeyes.db \
  "SELECT rating, COUNT(*) as count, AVG(confidence_score) as avg_confidence \
   FROM feedback f JOIN metrics m ON f.query_id = m.query_id \
   GROUP BY rating ORDER BY rating;"
```

### 4. System Health Check
```bash
sqlite3 /workspace/openeyes_data/openeyes.db \
  "SELECT \
     COUNT(*) as total_queries, \
     AVG(confidence_score) as avg_confidence, \
     AVG(latency_ms) as avg_latency, \
     SUM(CASE WHEN source_credibility='HIGH' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as high_cred_pct \
   FROM metrics \
   WHERE timestamp >= datetime('now', '-24 hours');"
```

---

## Key Metrics Available

### Source Credibility Distribution
```sql
SELECT source_credibility, COUNT(*) as count, 
       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM metrics) as percentage
FROM metrics 
GROUP BY source_credibility;
```

**Expected Output:**
| source_credibility | count | percentage |
|-------------------|-------|------------|
| HIGH              | 450   | 45.0%      |
| MEDIUM            | 350   | 35.0%      |
| LOW               | 150   | 15.0%      |
| UNVERIFIED        | 50    | 5.0%       |

### Domain Activity
```sql
SELECT domain, COUNT(*) as queries, 
       AVG(confidence_score) as avg_confidence,
       AVG(latency_ms) as avg_latency
FROM metrics 
GROUP BY domain 
ORDER BY queries DESC;
```

### Performance Metrics
```sql
SELECT 
  AVG(latency_ms) as avg_latency_ms,
  MIN(latency_ms) as min_latency_ms,
  MAX(latency_ms) as max_latency_ms,
  SUM(CASE WHEN retrieval_method='cache' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as cache_hit_rate
FROM metrics 
WHERE timestamp >= datetime('now', '-1 hour');
```

### Hallucination Blocks
```sql
SELECT COUNT(*) as hallucinations_blocked 
FROM metrics 
WHERE hallucination_detected = 1;
```

---

## Submit Feedback

### Via Python Script
```bash
python -c "
from openeyes.core.database_client import DatabaseClient
db = DatabaseClient()
db.submit_feedback(
    query_id='your-query-id',
    rating=5,  # 1-5 scale
    comment='Answer was accurate and well-sourced'
)
"
```

### Direct SQL
```sql
INSERT INTO feedback (query_id, rating, comment, timestamp)
VALUES ('query-123', 5, 'Very accurate answer', datetime('now'));
```

---

## Adaptive Learning Status

Check how feedback is affecting confidence calibration:

```sql
SELECT 
  d.domain_name,
  COUNT(f.feedback_id) as feedback_count,
  AVG(f.rating) as avg_rating,
  d.accuracy_factor,
  CASE 
    WHEN d.accuracy_factor > 1.0 THEN 'Boosted'
    WHEN d.accuracy_factor < 1.0 THEN 'Penalized'
    ELSE 'Neutral'
  END as calibration_status
FROM domains d
LEFT JOIN feedback f ON d.domain_name = (
  SELECT domain FROM metrics WHERE query_id = f.query_id
)
GROUP BY d.domain_name;
```

---

## Common CLI Workflows

### Daily Health Report
```bash
#!/bin/bash
echo "=== OpenEyes Daily Report ==="
echo ""
echo "📊 Queries (24h):"
sqlite3 /workspace/openeyes_data/openeyes.db \
  "SELECT COUNT(*) FROM metrics WHERE timestamp >= datetime('now', '-24 hours');"

echo ""
echo "🎯 Avg Confidence:"
sqlite3 /workspace/openeyes_data/openeyes.db \
  "SELECT ROUND(AVG(confidence_score), 2) FROM metrics WHERE timestamp >= datetime('now', '-24 hours');"

echo ""
echo "⚡ Avg Latency (ms):"
sqlite3 /workspace/openeyes_data/openeyes.db \
  "SELECT ROUND(AVG(latency_ms), 2) FROM metrics WHERE timestamp >= datetime('now', '-24 hours');"

echo ""
echo "✅ High Credibility Sources:"
sqlite3 /workspace/openeyes_data/openeyes.db \
  "SELECT ROUND(SUM(CASE WHEN source_credibility='HIGH' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) FROM metrics WHERE timestamp >= datetime('now', '-24 hours');"
```

### Weekly Feedback Analysis
```bash
sqlite3 /workspace/openeyes_data/openeyes.db <<EOF
.mode column
.headers on
SELECT 
  strftime('%Y-%m-%d', timestamp) as date,
  COUNT(*) as feedback_count,
  ROUND(AVG(rating), 2) as avg_rating,
  ROUND(AVG(m.confidence_score), 2) as predicted_confidence
FROM feedback f
JOIN metrics m ON f.query_id = m.query_id
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY date
ORDER BY date;
