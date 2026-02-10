"""ClusterML Shared Data Models.

Defines all Pydantic models used across master, worker, SDK, and CLI.
These models enforce a consistent API contract across the system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ─── Enums ──────────────────────────────────────────────────────────────────


class JobStatus(str, Enum):
    """Lifecycle states for a job."""
    PENDING = "pending"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeStatus(str, Enum):
    """Health states for a worker node."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    DRAINING = "draining"


# ─── Resource Models ────────────────────────────────────────────────────────


class ResourceRequirements(BaseModel):
    """Resources requested by a job."""
    cpu: str = Field(default="1", description="CPU cores, e.g. '4' or '4000m'")
    memory: str = Field(default="1Gi", description="Memory, e.g. '16Gi'")
    gpu: int = Field(default=0, description="Number of GPUs required")


class ResourceInfo(BaseModel):
    """Resource snapshot reported by a worker node."""
    cpu_cores: int = Field(description="Total CPU cores")
    cpu_usage_percent: float = Field(default=0.0, description="Current CPU usage %")
    memory_total_mb: int = Field(description="Total RAM in MB")
    memory_used_mb: int = Field(default=0, description="Used RAM in MB")
    gpu_count: int = Field(default=0, description="Number of GPUs")
    gpu_names: List[str] = Field(default_factory=list, description="GPU model names")
    gpu_memory_total_mb: int = Field(default=0, description="Total GPU memory in MB")
    gpu_memory_used_mb: int = Field(default=0, description="Used GPU memory in MB")


# ─── Job Models ─────────────────────────────────────────────────────────────


class EnvVar(BaseModel):
    """An environment variable key-value pair."""
    name: str
    value: str


class VolumeMount(BaseModel):
    """A volume mount specification."""
    name: str
    mount_path: str = Field(alias="mountPath")
    source: str

    class Config:
        populate_by_name = True


class DistributedConfig(BaseModel):
    """Configuration for distributed/multi-node jobs."""
    workers: int = Field(ge=1, description="Number of worker processes")
    type: str = Field(description="Framework type: pytorch, horovod, mpi")


class JobSpec(BaseModel):
    """The spec section of a job definition."""
    image: str = Field(description="Docker image to run")
    command: List[str] = Field(default_factory=list, description="Entrypoint override")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    resources: ResourceRequirements = Field(default_factory=ResourceRequirements)
    env: List[EnvVar] = Field(default_factory=list)
    volumes: List[VolumeMount] = Field(default_factory=list)
    distributed: Optional[DistributedConfig] = None


class JobCreate(BaseModel):
    """Request body for creating a new job."""
    name: str = Field(min_length=1, max_length=128, description="Job name")
    labels: Dict[str, str] = Field(default_factory=dict)
    spec: JobSpec


class JobUpdate(BaseModel):
    """Request body for updating a job (e.g. status change)."""
    status: Optional[JobStatus] = None
    result: Optional[Dict[str, Any]] = None
    logs: Optional[str] = None


class Job(BaseModel):
    """Full job representation stored in the system."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    labels: Dict[str, str] = Field(default_factory=dict)
    spec: JobSpec
    status: JobStatus = JobStatus.PENDING
    worker_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    logs: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


# ─── Node Models ────────────────────────────────────────────────────────────


class NodeRegister(BaseModel):
    """Request body when a worker registers with the master."""
    hostname: str
    ip_address: str
    port: int = Field(default=8081)
    resources: ResourceInfo
    labels: Dict[str, str] = Field(default_factory=dict)
    version: str = Field(default="0.1.0")


class Node(BaseModel):
    """Full worker node representation stored in the system."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    hostname: str
    ip_address: str
    port: int = 8081
    status: NodeStatus = NodeStatus.ONLINE
    resources: ResourceInfo
    labels: Dict[str, str] = Field(default_factory=dict)
    current_jobs: List[str] = Field(default_factory=list)
    max_concurrent_jobs: int = Field(default=2)
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_heartbeat: Optional[datetime] = None
    version: str = "0.1.0"


# ─── Communication Models ──────────────────────────────────────────────────


class HeartbeatRequest(BaseModel):
    """Heartbeat payload sent by worker to master."""
    worker_id: str
    resources: ResourceInfo
    active_jobs: List[str] = Field(default_factory=list)
    uptime_seconds: float = 0


class JobAssignment(BaseModel):
    """A job assigned to a worker for execution."""
    job_id: str
    spec: JobSpec


class HeartbeatResponse(BaseModel):
    """Response from master to worker heartbeat."""
    acknowledged: bool = True
    assigned_jobs: List[JobAssignment] = Field(default_factory=list)
    commands: List[str] = Field(default_factory=list, description="Control commands (e.g. 'drain', 'cancel:job-id')")


class ClusterStatus(BaseModel):
    """Aggregated cluster status."""
    total_nodes: int = 0
    online_nodes: int = 0
    total_jobs: int = 0
    running_jobs: int = 0
    pending_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    total_cpu_cores: int = 0
    total_gpu_count: int = 0
    total_memory_mb: int = 0
