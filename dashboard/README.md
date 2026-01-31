# ClusterML Dashboard

Web-based UI for ClusterML management and monitoring.

## Features

- Job submission and management
- Real-time log streaming
- Node monitoring
- Resource usage visualization
- User management

## Development

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Production Build

```bash
cd frontend
npm run build
```

## Documentation

See [docs/dashboard/dashboard_features.md](../docs/dashboard/dashboard_features.md) for more details.
