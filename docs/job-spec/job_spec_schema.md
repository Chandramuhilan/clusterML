# Job Specification Schema

## Overview

Jobs are defined using YAML specifications.

## Schema

```yaml
apiVersion: clusterml/v1
kind: Job
metadata:
  name: string          # Required: Job name
  labels: {}            # Optional: Key-value labels

spec:
  image: string         # Required: Docker image
  command: [string]     # Optional: Override entrypoint
  args: [string]        # Optional: Command arguments
  
  resources:
    cpu: string         # e.g., "4" or "4000m"
    memory: string      # e.g., "16Gi"
    gpu: int            # Number of GPUs
  
  env:                  # Environment variables
    - name: string
      value: string
  
  volumes:              # Volume mounts
    - name: string
      mountPath: string
      source: string    # URL or path
  
  distributed:          # For multi-node jobs
    workers: int
    type: string        # pytorch, horovod, mpi
```

## Examples

### Simple Training Job

```yaml
apiVersion: clusterml/v1
kind: Job
metadata:
  name: mnist-training

spec:
  image: pytorch/pytorch:2.0-cuda11.8
  command: ["python", "train.py"]
  resources:
    cpu: "4"
    memory: "16Gi"
    gpu: 1
```

### Distributed PyTorch Job

```yaml
apiVersion: clusterml/v1
kind: Job
metadata:
  name: distributed-training

spec:
  image: my-training-image:latest
  command: ["torchrun", "--nproc_per_node=2", "train.py"]
  resources:
    cpu: "8"
    memory: "32Gi"
    gpu: 2
  distributed:
    workers: 4
    type: pytorch
```
