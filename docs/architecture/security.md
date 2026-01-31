# Security

## Authentication

### API Keys
- Master generates API keys for clients
- Workers use node tokens for registration

### Token Types
- **Admin Token**: Full cluster access
- **User Token**: Job submission and monitoring
- **Worker Token**: Node registration and job execution

## Authorization

Role-based access control (RBAC):

| Role    | Permissions                          |
|---------|--------------------------------------|
| Admin   | All operations                       |
| User    | Submit jobs, view own jobs           |
| Viewer  | View cluster status, job logs        |

## Data Security

### In Transit
- TLS 1.3 for all API communication
- Optional mTLS for worker authentication

### At Rest
- Encrypted job specifications
- Secure storage for credentials

## Job Isolation

- Container-based execution
- Resource limits (CPU, memory, GPU)
- Network isolation between jobs

## Audit Logging

All operations are logged with:
- Timestamp
- User/token identity
- Action performed
- Resource affected
