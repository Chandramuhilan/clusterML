# Networking

## Network Requirements

### Master Node
- Public IP or domain name (for worker connections)
- Open ports: 8080 (API), 8443 (HTTPS)

### Worker Nodes
- Outbound internet access to master
- No inbound ports required (pull-based)

## Connection Modes

### Direct Connection
Workers connect directly to master's public IP/domain.

### NAT Traversal
For workers behind NAT:
- Workers initiate outbound connections
- Long-polling or WebSocket for job assignments

### VPN/Private Network
For enterprise deployments:
- All nodes on same private network
- Internal DNS for service discovery

## Security

- TLS encryption for all communication
- API key authentication
- Optional mTLS for worker authentication

## Firewall Configuration

```
# Master node
Allow inbound TCP 8080, 8443 from workers
Allow inbound TCP 8080, 8443 from clients

# Worker nodes
Allow outbound TCP 8080, 8443 to master
```
