# Internet Connectivity

## Overview

ClusterML supports various network topologies for connecting workers to the master.

## Connectivity Scenarios

### 1. All Nodes on Public Internet

```
Worker (Public IP) ──── Internet ────▶ Master (Public IP)
```

Requirements:
- Master has public IP/domain
- Workers have outbound internet access

### 2. Workers Behind NAT

```
Worker (Private IP) ──── NAT ────▶ Internet ────▶ Master (Public IP)
```

Configuration:
- Workers use pull-based job fetching
- Long-polling or WebSocket connections
- No inbound ports needed on workers

### 3. Hybrid Cloud

```
┌─────────────────┐
│  Cloud (AWS)    │
│  ┌───────────┐  │
│  │  Master   │  │
│  └─────┬─────┘  │
└────────│────────┘
         │ VPN/Tunnel
┌────────▼────────┐
│  On-Premises    │
│  ┌───────────┐  │
│  │  Workers  │  │
│  └───────────┘  │
└─────────────────┘
```

## Troubleshooting

### Connection Issues

```bash
# Test connectivity from worker
curl -v https://master.example.com:8443/health

# Check DNS resolution
nslookup master.example.com

# Test with telnet
telnet master.example.com 8443
```

### Firewall Issues

Ensure these ports are open:
- Master: TCP 8080, 8443 inbound
- Workers: TCP 8080, 8443 outbound
