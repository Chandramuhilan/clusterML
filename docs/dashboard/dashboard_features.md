# Dashboard Features

## Overview

The ClusterML Dashboard provides a web-based interface for cluster management.

## Features

### Job Management

- **Job List**: View all jobs with filtering and sorting
- **Job Details**: Detailed view of job status, logs, and metrics
- **Job Submission**: Submit new jobs via web form
- **Real-time Logs**: Stream logs from running jobs

### Node Monitoring

- **Node List**: View all worker nodes and their status
- **Resource Usage**: CPU, memory, GPU utilization graphs
- **Node Details**: Detailed node information and assigned jobs

### Cluster Overview

- **Dashboard Home**: Summary of cluster health and activity
- **Resource Graphs**: Historical resource usage charts
- **Job Statistics**: Success/failure rates, queue depth

### Administration

- **User Management**: Create and manage user accounts
- **API Keys**: Generate and revoke API keys
- **Audit Logs**: View cluster activity logs

## Access

```
https://master.example.com:8443/dashboard
```

## Screenshots

(Screenshots to be added)

## Configuration

Dashboard settings in `master.yaml`:

```yaml
dashboard:
  enabled: true
  path: /dashboard
  auth_required: true
```
