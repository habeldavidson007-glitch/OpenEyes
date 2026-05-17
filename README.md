# 👁️ OpenEyes - High-Stakes Reasoning Engine

A sophisticated AI reasoning engine with autonomous swarm agents, designed for high-stakes question answering across multiple domains including economics, healthcare, governance, history, and satellite data analysis.

## Key Features

- **Autonomous Signal-Pulse Swarm**: 2000+ bio-inspired agents that continuously harvest and index knowledge
- **Multi-Domain Knowledge Base**: Pre-indexed fragments across economy, healthcare, governance, history, education, philosophy, social sciences, and satire
- **WAL Buffer System**: Write-Ahead Log for zero-latency access to pre-computed swarm data
- **Monte Carlo Confidence Evaluation**: Statistical confidence scoring for all answers
- **Procedural Linguistic Manifestor**: Generates natural, varied human-like responses from verified facts
- **Live Audit Logging**: Complete traceability of all reasoning decisions
- **Graceful Degradation**: Handles incomplete information safely with appropriate warnings
- **Fragment-Based Retrieval**: Efficient semantic search across thousands of knowledge fragments

## System Requirements

- **Operating System**: Linux (tested on Ubuntu/Xubuntu 20.04+), macOS, or Windows with WSL
- **Python**: Version 3.10 or higher (3.12 recommended)
- **RAM**: Minimum 4GB, 8GB+ recommended for swarm operations
- **Disk Space**: ~1GB for code, knowledge base, and WAL buffer
- **Dependencies**: Git, pip, SQLite3

## Step-by-Step Installation Guide for Xubuntu

### Step 1: Update Your System

Open a terminal and update your package lists:

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Python and Required Dependencies

Install Python 3.10+, pip, development tools, and SQLite support:

```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev git build-essential libsqlite3-dev
```

Verify Python version (must be 3.10 or higher):

```bash
python3 --version
```

**If your Xubuntu version has Python < 3.10**, install from PPA:

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

### Step 3: Clone the Repository

```bash
cd ~
git clone <repository-url> openeyes
cd openeyes
```

Or navigate to existing workspace:

```bash
cd /workspace/openeyes
```

### Step 4: Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your terminal prompt.

### Step 5: Install Project Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If you encounter errors, install core dependencies manually:

```bash
pip install numpy requests beautifulsoup4 lxml scikit-learn pandas
```

### Step 6: Install OpenEyes in Development Mode

```bash
pip install -e .
```

This installs the package in "editable" mode for immediate code reflection.

### Step 7: Initialize the Swarm WAL Buffer

The swarm will automatically create the WAL buffer on first run. To pre-populate with sample data:

```bash
python -c "
from openeyes.swarm.autonomous_pulse_swarm import WALBuffer
import asyncio

wal = WALBuffer('wal_buffer.db')
wal._ensure_initialized()
print('✓ WAL buffer initialized successfully')
"
```

### Step 8: Verify Installation

```bash
python -c "from openeyes.core.engine import OpenEyesEngine; print('✓ OpenEyes installed successfully')"
```

### Step 9: Run Your First Query

```bash
python -c "
from openeyes.core.engine import OpenEyesEngine
engine = OpenEyesEngine()
result = engine.answer('What are practical investment strategies?')
print(f\"Answer: {result['answer']}\")
print(f\"Confidence: {result['confidence']:.1%}\")
"
```

## Usage Examples

### Basic Investment Query

```python
from openeyes.core.engine import OpenEyesEngine

engine = OpenEyesEngine()
query = "How to get rich fast using investments with a practical plan?"
result = engine.answer(query)

print(f"Answer: {result['answer']}")
print(f"Confidence Score: {result['confidence']:.1%}")
print(f"Domain: {result['domain']}")
print(f"Fragments Used: {result['fragments_used']}")
```

### Multi-Domain Queries

```python
from openeyes.core.engine import OpenEyesEngine

engine = OpenEyesEngine()

queries = [
    "What are the historical patterns of market crashes?",
    "How do SEC regulations protect investors?",
    "What role does psychology play in investment decisions?",
    "How can I plan for healthcare costs in retirement?",
    "What is ethical investing and ESG criteria?",
]

for query in queries:
    result = engine.answer(query)
    print(f"\nQ: {query}")
    print(f"A: {result['answer'][:200]}...")
    print(f"Domain: {result['domain']}, Confidence: {result['confidence']:.1%}")
```

### Domain-Specific Query

```python
from openeyes.core.engine import OpenEyesEngine

engine = OpenEyesEngine()

# Healthcare query
result = engine.answer('What are the symptoms of type 2 diabetes?', domain='healthcare')
print(result['answer'])

# Governance query
result = engine.answer('How does parliamentary procedure work?', domain='governance')
print(result['answer'])
```

## Understanding the Output

When you run a query, OpenEyes provides:

- **Answer**: The generated response based on verified facts from swarm fragments
- **Confidence Score**: Statistical confidence (0.0 to 1.0) from Monte Carlo evaluation
- **Domain**: The knowledge domain used (economy, healthcare, governance, etc.)
- **Status**: Response classification (ANSWER_HIGH_CONFIDENCE, ANSWER_LOW_CONFIDENCE, etc.)
- **Fragments Used**: Number of knowledge fragments retrieved (swarm + local index)
- **Data Recency**: Age of the underlying data in years

## The Autonomous Swarm

OpenEyes features a bio-inspired swarm architecture with:

- **2000+ Agents**: Staggered wake-up cycles for continuous knowledge harvesting
- **Agent States**: SLEEPING → TRIGGERED → HARVESTING → ARCHIVING → SLEEPING
- **Token Bucket Limiter**: Global rate limiting (5 req/sec) to prevent overload
- **WAL Buffer**: Write-only during active phase, enabling zero-latency reads
- **Domain Sectors**: Automatic fragment categorization (ECO, GOV, HC, HIS, EDU, PHI, SOCIAL, SAT)

### Swarm Fragment Categories

The swarm maintains fragments across these domains:

| Sector | Description | Example Topics |
|--------|-------------|----------------|
| ECO | Economy & Finance | Investments, markets, inflation |
| HC | Healthcare | Medical costs, insurance, wellness |
| GOV | Governance | Regulations, policy, compliance |
| HIS | History | Market crashes, economic cycles |
| EDU | Education | Financial literacy, learning |
| PHI | Philosophy | Ethics, ESG, values-based investing |
| SOCIAL | Social Sciences | Behavioral finance, psychology |
| SAT | Satire | Cautionary tales, critical perspectives |

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'openeyes'"

**Solution**: Activate virtual environment and install package:

```bash
source venv/bin/activate
pip install -e .
```

### Issue: "WAL buffer not found at wal_buffer.db"

**Note**: This is normal on first run. The system falls back to local indexing automatically. To create the buffer:

```bash
python -c "from openeyes.swarm.autonomous_pulse_swarm import WALBuffer; wal = WALBuffer('wal_buffer.db'); wal._ensure_initialized()"
```

### Issue: Low confidence scores or irrelevant answers

**Possible causes**:
1. Query outside covered domains
2. Insufficient fragments for topic
3. Query phrasing doesn't match indexed content

**Solutions**:
- Rephrase your query with different keywords
- Check available domains in `openeyes/domains/`
- Add more fragments to relevant domain folders
- Run swarm to harvest fresh data

### Issue: Memory errors on low-RAM systems

**Solutions**:
- Close other applications
- Reduce swarm agent count in config
- Use smaller fragment batches
- Enable swap space: `sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`

## Project Structure

```
openeyes/
├── core/                   # Main reasoning engine and routing
├── cognitive/              # Procedural linguistic manifestor
├── swarm/                  # Autonomous pulse swarm (2000 agents)
│   ├── autonomous_pulse_swarm.py
│   ├── swarm_retrieval.py
│   └── realtime_updater.py
├── domains/                # Knowledge fragments by domain
│   ├── economy/
│   ├── healthcare/
│   ├── governance/
│   ├── his/
│   ├── edu/
│   ├── phi/
│   ├── social_sciences/
│   └── sat/
├── knowledge/              # Linguistic DNA and retrieval logic
├── monte_carlo/            # Confidence evaluation engine
├── storage/                # Memory and audit logging
└── ui/                     # Control deck and interface components
```

## Adding Custom Knowledge Fragments

Extend OpenEyes by adding JSON fragment files to domain directories:

```json
{
  "id": "unique-fragment-id",
  "domain": "economy",
  "subdomain": "FIN",
  "content": "Dollar-cost averaging reduces timing risk by investing fixed amounts regularly.",
  "year": 2024,
  "source": "Investment Authority",
  "source_url": "https://example.com/source",
  "reasoning_role": "strategy",
  "credibility_class": "financial_institution"
}
```

## Performance Notes

- First query builds indexes (may take 5-10 seconds)
- Subsequent queries: 0.5-2 seconds typical
- Swarm fragments provide zero-latency access
- Complex multi-domain queries take longer
- SSD storage recommended for optimal performance

## Recent Updates

- ✅ Fixed swarm retrieval logic (OR-based keyword matching)
- ✅ Added multi-domain fragment support for investment queries
- ✅ Improved WAL buffer sector categorization
- ✅ Enhanced confidence scoring with swarm integration

## License

See the LICENSE file in the root directory.

## Support

For issues or questions, check documentation or raise an issue in the repository.
