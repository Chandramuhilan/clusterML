#!/bin/bash
# Cleanup script for ClusterML local cluster

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Cleaning up ClusterML Local Cluster..."

# Stop master
if [ -f "$PROJECT_ROOT/.master.pid" ]; then
    MASTER_PID=$(cat "$PROJECT_ROOT/.master.pid")
    if kill -0 "$MASTER_PID" 2>/dev/null; then
        echo "Stopping master (PID: $MASTER_PID)..."
        kill "$MASTER_PID" 2>/dev/null || true
    fi
    rm "$PROJECT_ROOT/.master.pid"
fi

# Stop worker
if [ -f "$PROJECT_ROOT/.worker.pid" ]; then
    WORKER_PID=$(cat "$PROJECT_ROOT/.worker.pid")
    if kill -0 "$WORKER_PID" 2>/dev/null; then
        echo "Stopping worker (PID: $WORKER_PID)..."
        kill "$WORKER_PID" 2>/dev/null || true
    fi
    rm "$PROJECT_ROOT/.worker.pid"
fi

# Kill any remaining Python processes (be careful with this)
echo "Checking for orphaned processes..."
pkill -f "clusterml" 2>/dev/null || true

# Clean up temp files
echo "Cleaning up temporary files..."
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

echo "Cleanup complete!"
