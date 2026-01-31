# Worker Setup

## Requirements

- Python 3.10+
- Docker (for containerized job execution)
- GPU drivers (optional, for GPU workloads)

## Installation

### From PyPI

```bash
pip install clusterml-worker
```

### From Source

```bash
git clone https://github.com/your-org/clusterml.git
cd clusterml/worker
pip install -e .
```

## Configuration

Create `/etc/clusterml/worker.yaml`:

```yaml
master:
  url: https://master.example.com:8443
  token: ${WORKER_TOKEN}

worker:
  name: worker-01
  labels:
    gpu: nvidia-a100
    region: us-west-1

resources:
  cpu: 16
  memory: 64Gi
  gpu: 2

executor:
  type: docker
  runtime: nvidia  # for GPU support
```

## Running as a Service

### Systemd (Linux)

```bash
sudo cp scripts/clusterml-worker.service /etc/systemd/system/
sudo systemctl enable clusterml-worker
sudo systemctl start clusterml-worker
```

## Verifying Registration

```bash
clusterml node list
# Should show your worker in the list
```
