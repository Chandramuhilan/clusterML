"""Utility functions for resource parsing and comparison."""

import re
from typing import Tuple


def parse_cpu(cpu_str: str) -> float:
    """Parse CPU string to number of cores.

    Supports formats: '4' (cores), '4000m' (millicores).

    Args:
        cpu_str: CPU resource string.

    Returns:
        Number of CPU cores as a float.
    """
    cpu_str = cpu_str.strip()
    if cpu_str.endswith("m"):
        return float(cpu_str[:-1]) / 1000.0
    return float(cpu_str)


def parse_memory(mem_str: str) -> int:
    """Parse memory string to megabytes.

    Supports formats: '16Gi', '512Mi', '4G', '1024M', '1073741824' (bytes).

    Args:
        mem_str: Memory resource string.

    Returns:
        Memory in megabytes.
    """
    mem_str = mem_str.strip()

    match = re.match(r"^(\d+(?:\.\d+)?)\s*([A-Za-z]*)$", mem_str)
    if not match:
        raise ValueError(f"Cannot parse memory string: {mem_str}")

    value = float(match.group(1))
    unit = match.group(2)

    multipliers = {
        "": 1 / (1024 * 1024),       # bytes → MB
        "Ki": 1 / 1024,              # KiB → MB
        "Mi": 1,                      # MiB → MB
        "Gi": 1024,                   # GiB → MB
        "Ti": 1024 * 1024,           # TiB → MB
        "K": 1 / 1000,               # KB → MB (decimal)
        "M": 1,                       # MB
        "G": 1000,                    # GB → MB (decimal)
        "T": 1000 * 1000,            # TB → MB
    }

    if unit not in multipliers:
        raise ValueError(f"Unknown memory unit: {unit}")

    return int(value * multipliers[unit])


def check_resources_fit(
    required_cpu: str,
    required_memory: str,
    required_gpu: int,
    available_cpu_cores: int,
    available_memory_mb: int,
    available_gpu: int,
) -> Tuple[bool, str]:
    """Check if required resources fit in available capacity.

    Returns:
        (fits, reason) - True if resources fit, else (False, reason string).
    """
    cpu_needed = parse_cpu(required_cpu)
    mem_needed = parse_memory(required_memory)

    if cpu_needed > available_cpu_cores:
        return False, f"CPU: need {cpu_needed}, have {available_cpu_cores}"
    if mem_needed > available_memory_mb:
        return False, f"Memory: need {mem_needed}MB, have {available_memory_mb}MB"
    if required_gpu > available_gpu:
        return False, f"GPU: need {required_gpu}, have {available_gpu}"

    return True, "ok"
