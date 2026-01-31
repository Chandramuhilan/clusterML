# Local Setup

## Prerequisites

- Python 3.10+
- Docker (optional, for containerized execution)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/clusterml.git
cd clusterml
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Start Local Cluster

```bash
# Start master
cd master
python main.py

# In another terminal, start worker
cd worker
python main.py --master-url http://localhost:8080
```

### 5. Submit a Test Job

```bash
clusterml job submit --spec examples/pytorch_single_node/job.yaml
```

## Development Mode

For development with auto-reload:

```bash
# Master
uvicorn master.app:app --reload --port 8080

# Worker
python worker/main.py --dev-mode
```
