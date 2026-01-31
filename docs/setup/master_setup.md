# Master Setup

## Requirements

- Python 3.10+
- PostgreSQL 14+ (for production)
- Redis (for job queue)

## Installation

### From PyPI

```bash
pip install clusterml-master
```

### From Source

```bash
git clone https://github.com/your-org/clusterml.git
cd clusterml/master
pip install -e .
```

## Configuration

Create `/etc/clusterml/master.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 8080
  workers: 4

database:
  url: postgresql://user:pass@localhost:5432/clusterml

redis:
  url: redis://localhost:6379

auth:
  secret_key: ${SECRET_KEY}
  token_expiry: 3600

scheduler:
  algorithm: resource-fit
  max_retries: 3
```

## Database Setup

```bash
# Create database
createdb clusterml

# Run migrations
clusterml-master migrate
```

## Running

### Development

```bash
clusterml-master run --dev
```

### Production

```bash
gunicorn master.app:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Docker Deployment

```bash
docker build -t clusterml-master .
docker run -p 8080:8080 -v /etc/clusterml:/etc/clusterml clusterml-master
```
