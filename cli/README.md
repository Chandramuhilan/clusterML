# ClusterML CLI

Command-line interface for ClusterML.

## Installation

```bash
pip install clusterml-cli
```

## Quick Start

```bash
# Configure connection
clusterml config set master-url https://master.example.com:8443
clusterml config set api-key your-api-key

# Submit a job
clusterml job submit --spec job.yaml

# List jobs
clusterml job list

# View logs
clusterml job logs <job-id>
```

## Documentation

See [docs/cli/cli_commands.md](../docs/cli/cli_commands.md) for full documentation.
