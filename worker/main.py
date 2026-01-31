"""ClusterML Worker Node - Main Entry Point."""

import argparse
import asyncio
import logging
import os
import signal
import sys
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WorkerAgent:
    """ClusterML Worker Agent."""

    def __init__(self, master_url: str, token: Optional[str] = None):
        self.master_url = master_url
        self.token = token or os.getenv("WORKER_TOKEN")
        self.running = False
        self.worker_id: Optional[str] = None

    async def register(self) -> bool:
        """Register with the master node."""
        logger.info(f"Registering with master at {self.master_url}")
        # TODO: Implement registration logic
        # - Send worker capabilities (CPU, memory, GPU)
        # - Receive worker ID and configuration
        self.worker_id = "worker-001"  # Placeholder
        logger.info(f"Registered as {self.worker_id}")
        return True

    async def heartbeat(self):
        """Send periodic heartbeat to master."""
        while self.running:
            try:
                # TODO: Send heartbeat with resource usage
                logger.debug("Sending heartbeat...")
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                await asyncio.sleep(5)

    async def poll_jobs(self):
        """Poll for and execute jobs."""
        while self.running:
            try:
                # TODO: Poll master for assigned jobs
                # TODO: Execute jobs using executor
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Job polling failed: {e}")
                await asyncio.sleep(5)

    async def run(self):
        """Main worker loop."""
        self.running = True

        if not await self.register():
            logger.error("Failed to register with master")
            return

        # Run heartbeat and job polling concurrently
        await asyncio.gather(
            self.heartbeat(),
            self.poll_jobs()
        )

    def stop(self):
        """Stop the worker."""
        logger.info("Stopping worker...")
        self.running = False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ClusterML Worker Agent")
    parser.add_argument(
        "--master-url",
        default=os.getenv("MASTER_URL", "http://localhost:8080"),
        help="Master node URL"
    )
    parser.add_argument(
        "--token",
        default=os.getenv("WORKER_TOKEN"),
        help="Worker authentication token"
    )
    parser.add_argument(
        "--dev-mode",
        action="store_true",
        help="Run in development mode"
    )
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()

    worker = WorkerAgent(
        master_url=args.master_url,
        token=args.token
    )

    # Handle shutdown signals
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.stop)

    logger.info("Starting ClusterML Worker...")
    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
        sys.exit(0)
