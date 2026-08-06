import asyncio
import json
import logging
import os
import psutil
from typing import NoReturn
from datetime import datetime

# Setup minimal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MemoryGuardian")

LOG_DIR = os.path.join(os.path.dirname(__file__), "../../../logs")
os.makedirs(LOG_DIR, exist_ok=True)
EVENTS_LOG = os.path.join(LOG_DIR, "memory_events.jsonl")

def log_event(level: str, memory_percent: float, action: str) -> None:
    """Helper to log memory events to JSONL."""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "memory_percent": memory_percent,
        "action": action
    }
    try:
        with open(EVENTS_LOG, "a") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.error(f"Failed to write memory log: {e}")

def flush_kv_cache() -> None:
    """Mock implementation of KV cache flush."""
    logger.info("Triggering KV Cache flush...")
    # In a real scenario, this would interface with the inference engine
    
def kill_heaviest_non_essential() -> None:
    """Finds and kills the heaviest non-essential process to save RAM."""
    logger.warning("Emergency! Attempting to kill heaviest non-essential process.")
    
    current_pid = os.getpid()
    heaviest_proc = None
    max_memory = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            # Avoid killing ourselves or critical system processes
            if proc.info['pid'] == current_pid:
                continue
                
            name = proc.info['name'].lower()
            if any(critical in name for critical in ['systemd', 'kernel', 'launchd', 'docker']):
                continue
                
            mem = proc.info['memory_info'].rss
            if mem > max_memory:
                max_memory = mem
                heaviest_proc = proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    if heaviest_proc:
        logger.warning(f"Killing process {heaviest_proc.info['name']} (PID {heaviest_proc.info['pid']}) using {max_memory / (1024*1024):.2f} MB")
        try:
            heaviest_proc.terminate()
            heaviest_proc.wait(timeout=3)
        except Exception as e:
            logger.error(f"Failed to kill process: {e}")

async def memory_guardian_task() -> NoReturn:
    """
    Background asyncio task that continuously monitors system RAM.
    RAM Impact: Extremely low (<5MB). Sleeps most of the time.
    """
    logger.info("Memory Guardian started.")
    
    while True:
        try:
            mem = psutil.virtual_memory()
            percent = mem.percent
            
            if percent < 75.0:
                pass # Normal
            elif 75.0 <= percent < 85.0:
                # Warning
                log_event("WARNING", percent, "Logged warning")
            elif 85.0 <= percent < 92.0:
                # Critical
                log_event("CRITICAL", percent, "Triggered KV cache flush")
                flush_kv_cache()
                # Notify UI logic would go here
            elif percent >= 92.0:
                # Emergency
                log_event("EMERGENCY", percent, "Killing heaviest non-essential process and saving state")
                kill_heaviest_non_essential()
                
        except Exception as e:
            logger.error(f"Memory Guardian encountered an error: {e}")
            
        await asyncio.sleep(5) # Check every 5 seconds
