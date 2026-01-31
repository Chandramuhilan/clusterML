<div align="center">

# 🚀 ClusterML

[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](#)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg?style=flat-square)](#)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg?style=flat-square)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)

**A distributed machine learning system built for developers, not clusters**

[Features](#-features) •
[Quick Start](#-quick-start) •
[Architecture](#-architecture) •
[For Contributors](#-whos-this-project-for) •
[Documentation](#-documentation)

---

<img src="https://img.shields.io/badge/Train%20ML%20Models-Across%20Multiple%20Machines-orange?style=for-the-badge" alt="Train ML Models">

</div>

---

## 🌟 What is ClusterML?

ClusterML makes it easy to train and run machine learning models using multiple machines — whether they are on the same Wi-Fi network or connected over the internet.

> 💡 **No Kubernetes. No complex setup. Just plug and play.**

<table>
<tr>
<td>✅ Simple setup</td>
<td>✅ Developer-friendly tools</td>
</tr>
<tr>
<td>✅ Support for most ML frameworks</td>
<td>✅ Full visibility through dashboard</td>
</tr>
</table>

---

## 🎯 What Problem Does ClusterML Solve?

Many developers and students have access to multiple laptops, PCs, or GPUs — but using them together is painful.

| Challenge                  | ClusterML Solution                       |
| -------------------------- | ---------------------------------------- |
| 🔧 Complex cluster setup   | Simple CLI-based configuration           |
| 💻 Unused computing power  | Combine all machines into one cluster    |
| 📊 No visibility into jobs | Real-time monitoring dashboard           |
| 🐘 Heavy platforms (K8s)   | Lightweight, developer-friendly approach |

---

## 🏗️ Architecture

ClusterML follows a **Master–Worker architecture**:

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                         │
├──────────────────┬──────────────────┬──────────────────────────┤
│    💻 CLI        │    📦 SDK        │      🖥️ Dashboard        │
└────────┬─────────┴────────┬─────────┴─────────────┬────────────┘
         │                  │                       │
         └──────────────────┼───────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      🎛️ MASTER ORCHESTRATOR                     │
│  • Job Scheduling  • Node Management  • Dataset Storage         │
└─────────────────────────────┬───────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  👷 WORKER 1    │  │  👷 WORKER 2    │  │  👷 WORKER N    │
│  GPU: RTX 3080  │  │  GPU: A100      │  │  CPU Only       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 🧩 Key Components

| Component | Description |
|-----------|-------------|
| 👷 **Worker Agent** | Runs on each machine. Reports CPU/RAM/GPU usage, executes jobs in containers, uploads logs & checkpoints |
| 🎛️ **Master Orchestrator** | The brain of the system. Handles node registration, job scheduling, dataset & artifact management |
| 💻 **Terminal CLI** | Simple commands: `clusterml nodes list`, `clusterml job submit job.yaml` |
| 📦 **Python SDK** | Programmatic access: `client = Client(); job = client.submit("train.py")` |

---

## 🚀 Quick Start

```bash
# Install CLI
pip install clusterml

# Start a local cluster
clusterml cluster start

# List available nodes
clusterml nodes list

# Submit a job
clusterml job submit examples/pytorch_single_node/job.yaml
```

---

## 👥 Who's This Project For?

> **Find Your Role & Start Contributing!**

| Developer Type | Work Available | Areas to Contribute | Needed? |
|----------------|----------------|---------------------|---------|
| 🤖 **AI/ML Engineers** | Distributed training, new ML frameworks, checkpointing, gradient sync | `worker/executor/`, `examples/`, `sdk/` | ✅ Yes! |
| 🌐 **Full Stack Devs** | Dashboard UI, REST APIs, real-time monitoring, CLI experience | `dashboard/`, `cli/`, `master/api/` | ✅ Yes! |
| 🔒 **Security Engineers** | Auth, encryption, node security, RBAC, vulnerability fixes | `core/auth/`, `master/app/api/` | ✅ Yes! |
| ⚙️ **DevOps/Infra** | Docker configs, K8s deployments, CI/CD, resource monitoring | `Dockerfile`, `scripts/`, `.github/` | ✅ Yes! |
| 🐍 **Python Devs** | Core system, SDK improvements, testing, performance | `core/`, `sdk/`, `master/`, `worker/` | ✅ Yes! |
| 📝 **Technical Writers** | Tutorials, API docs, examples, architecture docs | `docs/`, `examples/`, `README.md` | ✅ Yes! |

> 💡 **Not sure where to start?** Check our [CONTRIBUTING.md](CONTRIBUTING.md) for a step-by-step guide!

---

## 📁 Project Structure

```
ClusterML/
├── 🎛️  master/       → Orchestrator (scheduling, APIs, storage)
├── 👷  worker/       → Worker agent (execution, monitoring)
├── 💻  cli/          → Command-line interface
├── 📦  sdk/          → Python SDK for programmatic access
├── 🖥️  dashboard/    → Web UI (React frontend + FastAPI backend)
├── 🔐  core/         → Shared utilities (auth, config, protocols)
├── 📖  docs/         → Documentation
├── 📂  examples/     → Example ML jobs
└── 🔧  scripts/      → Utility & setup scripts
```

---

## 📚 Documentation

| Topic                    | Link                                  |
| ------------------------ | ------------------------------------- |
| 🏗️ System Architecture | [docs/architecture/](docs/architecture/) |
| 🚀 Setup Guides          | [docs/setup/](docs/setup/)               |
| 💻 CLI Commands          | [docs/cli/](docs/cli/)                   |
| 📦 Python SDK            | [docs/sdk/](docs/sdk/)                   |
| 🖥️ Dashboard           | [docs/dashboard/](docs/dashboard/)       |
| 📋 Job Specification     | [docs/job-spec/](docs/job-spec/)         |

---

## 🤝 Contributing

We welcome contributions from everyone! Whether you're fixing a bug, adding a feature, or improving docs — every contribution matters.

<div align="center">

[![Read Contributing Guide](https://img.shields.io/badge/Read-Contributing%20Guide-blue?style=for-the-badge)](CONTRIBUTING.md)

</div>

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by the ClusterML Community**

⭐ **Star this repo** if you find it useful!

</div>
