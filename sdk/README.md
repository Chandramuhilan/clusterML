# ClusterML Python SDK

Python SDK for programmatic interaction with ClusterML.

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
```

## Documentation

See [docs/sdk/python_sdk_usage.md](../docs/sdk/python_sdk_usage.md) for full documentation.

## Examples

Check the `examples/` directory for sample code.
