"""
Self-Contained Local Model Loader & Downloader for YORD.
Automatically downloads Qwen2.5-1.5B-Instruct-Q4_K_M.gguf (~1.0 GB) into models/ for 100% offline local inference.
RAM Impact: ~1.0 GB VRAM/RAM during active inference.
"""

import os
import sys
import urllib.request
from typing import Optional

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models"))
MODEL_FILENAME = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_FILENAME)

# Official HuggingFace GGUF download URL for Qwen2.5-1.5B-Instruct
DOWNLOAD_URL = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"

def download_progress_hook(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(100.0, downloaded * 100.0 / total_size)
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        sys.stdout.write(f"\r[YORD Model Downloader] Downloading Qwen2.5-1.5B GGUF: {percent:.1f}% ({mb_downloaded:.1f} / {mb_total:.1f} MB)")
        sys.stdout.flush()

def ensure_model_downloaded() -> str:
    """
    Ensures Qwen2.5-1.5B GGUF model exists in models/ directory.
    Downloads automatically if missing.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 500 * 1024 * 1024:
        print(f"[YORD Model Loader] Found local GGUF model: {MODEL_PATH}")
        return MODEL_PATH

    print(f"\n[YORD Model Downloader] Target GGUF model missing: {MODEL_PATH}")
    print(f"[YORD Model Downloader] Fetching Qwen2.5-1.5B-Instruct GGUF from HuggingFace...")
    
    try:
        urllib.request.urlretrieve(DOWNLOAD_URL, MODEL_PATH, download_progress_hook)
        print(f"\n[YORD Model Downloader] Download complete! Model saved to: {MODEL_PATH}\n")
    except Exception as e:
        print(f"\n[YORD Model Downloader Error] Failed to download model: {e}")
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
        raise e

    return MODEL_PATH

if __name__ == "__main__":
    ensure_model_downloaded()
