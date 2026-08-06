import os
import subprocess
import psutil
from typing import Dict, Any

def detect_gpu() -> str:
    """
    Detects the presence of a GPU (NVIDIA or Apple Silicon/Metal).
    RAM Impact: Very low. Runs a subprocess and parses output.
    """
    try:
        # Check for NVIDIA
        subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return "NVIDIA"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check for Apple Silicon / Metal
    import platform
    if platform.system() == "Darwin" and platform.processor() == "arm":
        return "Metal"
        
    return "None"

def get_hardware_config() -> Dict[str, Any]:
    """
    Detects hardware specs and calculates resource limits.
    RAM Impact: Very low.
    
    Returns:
        Dict containing hardware specifications and derived limits.
    """
    mem = psutil.virtual_memory()
    total_ram_gb = mem.total / (1024 ** 3)
    cpu_count = psutil.cpu_count(logical=True)
    gpu_type = detect_gpu()
    
    # Base configuration for 8GB
    max_kv_cache_gb = 2.8
    max_context_tokens = 80000
    qdrant_max_segments = 2
    
    # Scale proportionally if RAM is significantly higher
    if total_ram_gb >= 15.0:
        scale_factor = total_ram_gb / 8.0
        max_kv_cache_gb = round(max_kv_cache_gb * scale_factor, 1)
        max_context_tokens = int(max_context_tokens * (scale_factor * 0.8)) # Slightly sub-linear scaling for context
        qdrant_max_segments = int(qdrant_max_segments * scale_factor)
        
    return {
        "total_ram_gb": round(total_ram_gb, 2),
        "cpu_count": cpu_count,
        "gpu_type": gpu_type,
        "max_kv_cache_gb": max_kv_cache_gb,
        "max_context_tokens": max_context_tokens,
        "qdrant_max_segments": qdrant_max_segments
    }

# Export singleton config
SYSTEM_CONFIG = get_hardware_config()
