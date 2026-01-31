#!/bin/bash
# Start a local ClusterML cluster for development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting ClusterML Local Cluster..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/venv"
fi

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Install dependencies
echo "Installing dependencies..."
pip install -q -e "$PROJECT_ROOT[dev]"

# Start master in background
echo "Starting master node..."
cd "$PROJECT_ROOT/master"
python main.py &
MASTER_PID=$!
echo "Master PID: $MASTER_PID"

# Wait for master to be ready
echo "Waiting for master to be ready..."
sleep 3

# Start worker
echo "Starting worker node..."
cd "$PROJECT_ROOT/worker"
python main.py --master-url http://localhost:8080 &
WORKER_PID=$!
echo "Worker PID: $WORKER_PID"

echo ""
echo "ClusterML Local Cluster Started!"
echo "================================"
echo "Master: http://localhost:8080"
echo "API Docs: http://localhost:8080/docs"
echo ""
echo "To stop the cluster, run: ./scripts/cleanup.sh"
echo "Or press Ctrl+C"

# Save PIDs for cleanup
echo "$MASTER_PID" > "$PROJECT_ROOT/.master.pid"
echo "$WORKER_PID" > "$PROJECT_ROOT/.worker.pid"

# Wait for interrupt
trap "echo 'Stopping...'; kill $MASTER_PID $WORKER_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
