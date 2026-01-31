# CLI Commands

## Installation

```bash
pip install clusterml-cli
```

## Configuration

```bash
# Configure cluster connection
clusterml config set master-url https://master.example.com:8443
clusterml config set api-key your-api-key
```

## Commands

### Job Management

```bash
# Submit a job
clusterml job submit --spec job.yaml
clusterml job submit --image pytorch:2.0 --command "python train.py"

# List jobs
clusterml job list
clusterml job list --status running

# Get job details
clusterml job get <job-id>

# View job logs
clusterml job logs <job-id>
clusterml job logs <job-id> --follow

# Cancel a job
clusterml job cancel <job-id>
```

### Node Management

```bash
# List nodes
clusterml node list

# Get node details
clusterml node get <node-id>

# Drain a node (no new jobs)
clusterml node drain <node-id>

# Remove a node
clusterml node remove <node-id>
```

### Cluster Status

```bash
# Cluster overview
clusterml status

# Resource usage
clusterml resources
```

## Global Options

```bash
--master-url    Override master URL
--api-key       Override API key
--output, -o    Output format (table, json, yaml)
--verbose, -v   Verbose output
```
