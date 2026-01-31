# System Overview

## Architecture

ClusterML follows a master-worker architecture for distributed ML job execution.

```
┌─────────────────┐     ┌─────────────────┐
│     Client      │     │    Dashboard    │
│   (CLI/SDK)     │     │    (Web UI)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │   Master    │
              │  (API/Sched)│
              └──────┬──────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
│  Worker 1 │  │  Worker 2 │  │  Worker N │
└───────────┘  └───────────┘  └───────────┘
```

## Components

### Master Node
- REST API for job submission
- Job scheduler
- Worker node management
- Job state tracking

### Worker Nodes
- Job executor
- Resource monitoring
- Result reporting
- Local caching

## Communication

All communication uses HTTP/HTTPS with JSON payloads.
