# Python SDK Usage

## Installation

```bash
pip install clusterml-sdk
```

## Quick Start

```python
from clusterml_sdk import ClusterClient, Job

# Connect to cluster
client = ClusterClient(
    master_url="https://master.example.com:8443",
    api_key="your-api-key"
)

# Submit a job
job = Job(
    name="my-training-job",
    image="pytorch/pytorch:2.0",
    command=["python", "train.py"],
    resources={"cpu": "4", "memory": "16Gi", "gpu": 1}
)

result = client.submit(job)
print(f"Job ID: {result.job_id}")

# Wait for completion
result.wait()
print(f"Status: {result.status}")
```

## API Reference

### ClusterClient

```python
client = ClusterClient(master_url, api_key)

# Job operations
client.submit(job)          # Submit a job
client.get(job_id)          # Get job status
client.cancel(job_id)       # Cancel a job
client.logs(job_id)         # Get job logs

# Cluster operations
client.nodes()              # List worker nodes
client.status()             # Cluster status
```

### Job

```python
job = Job(
    name="job-name",
    image="docker-image",
    command=["cmd"],
    args=["arg1", "arg2"],
    resources={"cpu": "4", "memory": "16Gi"},
    env={"KEY": "value"},
    labels={"team": "ml"}
)
```

## Examples

See `sdk/examples/` for more examples.
