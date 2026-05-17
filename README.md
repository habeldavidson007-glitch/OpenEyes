# 👁️ OpenEyes - High-Stakes Reasoning Engine

A sophisticated AI reasoning engine designed for high-stakes question answering across multiple domains including economics, healthcare, governance, history, and satellite data analysis.

## Features

- **Multi-Domain Knowledge Base**: Pre-indexed fragments across economy, healthcare, governance, history, and more
- **Monte Carlo Confidence Evaluation**: Statistical confidence scoring for all answers
- **Procedural Linguistic Manifestor**: Generates natural, varied human-like responses from verified facts
- **Live Audit Logging**: Complete traceability of all reasoning decisions
- **Graceful Degradation**: Handles incomplete information safely with appropriate warnings
- **Fragment-Based Retrieval**: Efficient semantic search across thousands of knowledge fragments

## System Requirements

- **Operating System**: Linux (tested on Ubuntu/Xubuntu), macOS, or Windows with WSL
- **Python**: Version 3.10 or higher (3.12 recommended)
- **RAM**: Minimum 2GB, 4GB+ recommended
- **Disk Space**: ~500MB for code and knowledge base

## Step-by-Step Installation Guide for Xubuntu

### Step 1: Update Your System

Open a terminal and update your package lists:

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install Python and Required Dependencies

Xubuntu may not have Python 3.10+ installed by default. Install it along with pip and development tools:

```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev git
```

Verify Python version (must be 3.10 or higher):

```bash
python3 --version
```

If your Xubuntu version has an older Python, you may need to install from a PPA:

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

### Step 3: Clone or Navigate to the OpenEyes Directory

If you haven't already cloned the repository:

```bash
cd ~
git clone <repository-url> openeyes
cd openeyes
```

Or if you're already in the project directory:

```bash
cd /workspace/openeyes
```

### Step 4: Create a Virtual Environment

It's highly recommended to use a virtual environment to avoid conflicts with system packages:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your terminal prompt.

### Step 5: Install Project Dependencies

Install all required Python packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If you encounter any errors, try installing dependencies individually:

```bash
pip install numpy requests beautifulsoup4 lxml
```

### Step 6: Install OpenEyes in Development Mode

Install the openeyes package itself:

```bash
pip install -e .
```

This installs the package in "editable" mode, so changes to the code are immediately reflected.

### Step 7: Verify Installation

Run a simple test to ensure everything is working:

```bash
python -c "from openeyes.core.engine import OpenEyesEngine; print('✓ OpenEyes installed successfully')"
```

### Step 8: Run the Engine

You can now run OpenEyes queries. Create a test script or run directly:

```bash
python -c "
from openeyes.core.engine import OpenEyesEngine
engine = OpenEyesEngine()
result = engine.answer('What is inflation?')
print(result['answer'])
"
```

## Usage Examples

### Basic Query

```python
from openeyes.core.engine import OpenEyesEngine

engine = OpenEyesEngine()
result = engine.answer('How does the Federal Reserve control interest rates?')

print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Domain: {result['domain']}")
```

### Investment Strategy Query

```python
from openeyes.core.engine import OpenEyesEngine

engine = OpenEyesEngine()
query = "What are practical investment strategies for long-term wealth building?"
result = engine.answer(query)

print(f"Answer: {result['answer']}")
print(f"Confidence Score: {result['confidence']:.1%}")
print(f"Fragments Used: {result['fragments_used']}")
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

- **Answer**: The generated response based on verified facts
- **Confidence Score**: Statistical confidence (0.0 to 1.0) based on Monte Carlo evaluation
- **Domain**: The knowledge domain used (economy, healthcare, etc.)
- **Status**: Response classification (ANSWER_HIGH_CONFIDENCE, ANSWER_LOW_CONFIDENCE, etc.)
- **Fragments Used**: Number of knowledge fragments retrieved
- **Data Recency**: Age of the underlying data in years

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'openeyes'"

**Solution**: Make sure you've activated the virtual environment and installed the package:

```bash
source venv/bin/activate
pip install -e .
```

### Issue: "Linguistic DNA file not found"

**Solution**: Ensure you're running from the project root directory where the `openeyes` folder exists:

```bash
cd /path/to/openeyes
python your_script.py
```

### Issue: "WAL buffer not found"

**Note**: This is a warning, not an error. The system will fall back to local fragment indexing automatically. You can ignore this message or pre-build the index:

```bash
python -c "from openeyes.knowledge.local_index import build_index; build_index()"
```

### Issue: Low confidence scores or irrelevant answers

**Possible causes**:
1. Query is outside the domains covered in the knowledge base
2. Insufficient fragments for the topic
3. Query phrasing doesn't match indexed content

**Solutions**:
- Try rephrasing your query
- Check which domains are available in `openeyes/domains/`
- Add more fragments to relevant domain folders

## Project Structure

```
openeyes/
├── core/               # Main reasoning engine and routing
├── cognitive/          # Procedural linguistic manifestor
├── domains/            # Knowledge fragments by domain
│   ├── economy/
│   ├── healthcare/
│   ├── governance/
│   └── ...
├── knowledge/          # Linguistic DNA and retrieval logic
├── monte_carlo/        # Confidence evaluation engine
├── storage/            # Memory and audit logging
└── ui/                 # Control deck and interface components
```

## Adding Custom Knowledge Fragments

You can extend OpenEyes by adding JSON fragment files to the appropriate domain directory:

```json
{
  "id": "unique-fragment-id",
  "domain": "economy",
  "subdomain": "FIN",
  "content": "Your factual content here",
  "year": 2024,
  "source": "Authoritative Source Name",
  "source_url": "https://example.com/source",
  "reasoning_role": "definition",
  "credibility_class": "government_agency"
}
```

## Performance Notes

- First query may be slower as indexes are built
- Subsequent queries benefit from cached indexes
- Complex queries with many fragments take longer
- Typical response time: 0.5-2 seconds

## License

See the LICENSE file in the root directory.

## Support

For issues or questions, please check the existing documentation or raise an issue in the project repository.
