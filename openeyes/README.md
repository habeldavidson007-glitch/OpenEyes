# 👁️ OpenEyes: High-Stakes Reasoning Engine

A sophisticated AI reasoning system that combines semantic search, Monte Carlo simulations, and multi-domain knowledge processing. Now with a powerful **Command-Line Interface (CLI)**.

## 🚀 Quick Start

```bash
# After installation, simply run:
openeyes

# Or run a single query:
openeyes query "What is factor investing?"
```

## System Requirements

- **OS**: Ubuntu/Xubuntu 20.04+ (tested on Xubuntu 22.04)
- **Python**: 3.11 or 3.12 (Python 3.14 not supported yet)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB free space

## Installation Steps for Xubuntu

### Step 1: Install System Dependencies
```bash
sudo apt update
sudo apt install -y software-properties-common build-essential libsqlite3-dev libblas-dev liblapack-dev gfortran
```

### Step 2: Install Python 3.11
```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

### Step 3: Clone and Setup
```bash
cd ~/OpenEyes
rm -rf venv  # Remove old venv if exists
mkdir -p workspace/openeyes/domains/{eco,his,gov,healthcare,sat}
mkdir -p workspace/openeyes/audit_logs
```

### Step 4: Create Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Step 5: Install Dependencies
```bash
pip install --upgrade pip
pip install -e .
```

### Step 6: Verify Installation
```bash
openeyes --version
```

## Usage

### Interactive Mode (Default)
Run without arguments to start the interactive CLI:
```bash
openeyes
```

**Interactive Commands:**
- Type any question to get an analysis
- `/help` - Show help message
- `/stats` - Show system statistics
- `/clear` - Clear screen
- `/exit` - Exit application

### Single Query Mode
```bash
# Basic query
openeyes query "How does dollar-cost averaging work?"

# With debug info
openeyes query "Explain modern portfolio theory" --explain

# JSON output for scripting
openeyes query "What are ETFs?" --json-output

# Suppress banner for clean output
openeyes query "Market volatility" --no-banner
```

### System Commands
```bash
# Check system status
openeyes status

# Run consolidation cycle
openeyes sleep

# Show version
openeyes --version
```

## Adding Custom Knowledge

Create text files in domain folders:
```
workspace/openeyes/domains/
├── eco/          # Economy & Finance
├── his/          # History
├── gov/          # Government & Policy
├── healthcare/   # Healthcare
└── sat/          # Satirical Content
```

Each `.txt` file should contain focused knowledge fragments.

## Troubleshooting

### Python Version Error
If you see package compatibility errors, ensure you're using Python 3.11:
```bash
python --version  # Should show 3.11.x
```

### Module Not Found
Reinstall in editable mode:
```bash
pip install -e .
```

### Permission Issues
```bash
sudo chown -R $USER:$USER workspace/
```

## Project Structure

```
OpenEyes/
├── cli.py                 # Main CLI entry point
├── openeyes/
│   ├── core/
│   │   └── engine.py      # Core reasoning engine
│   ├── swarm/             # Swarm intelligence
│   ├── monte_carlo/       # Simulation engine
│   └── domains/           # Domain-specific logic
└── workspace/
    └── openeyes/
        └── domains/       # Knowledge fragments
```

## License

MIT License - See LICENSE file for details.
