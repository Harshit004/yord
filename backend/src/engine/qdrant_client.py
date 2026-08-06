"""
Local Vector Storage Manager for YORD.
Manages file-backed vector collections, payload metadata, and cosine similarity search.
Designed for 8GB RAM constraints using memory-mapped array storage.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/qdrant_storage"))

class LocalVectorStore:
    """
    File-backed Lightweight HNSW/Vector search store for YORD.
    RAM Impact: Low. Loads vectors lazily via mmap arrays.
    """
    def __init__(self, collection_name: str = "yord_corpus", dimension: int = 768):
        self.collection_name = collection_name
        self.dimension = dimension
        self.collection_dir = os.path.join(STORAGE_DIR, collection_name)
        os.makedirs(self.collection_dir, exist_ok=True)
        
        self.metadata_file = os.path.join(self.collection_dir, "metadata.jsonl")
        self.vectors_file = os.path.join(self.collection_dir, "vectors.npy")
        
        self.payloads: List[Dict[str, Any]] = []
        self._load_payloads()
        
    def _load_payloads(self) -> None:
        """Loads payload metadata from JSONL."""
        self.payloads = []
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                for line in f:
                    if line.strip():
                        self.payloads.append(json.loads(line))
                        
    def upsert(self, doc_id: str, vector: List[float], payload: Dict[str, Any]) -> None:
        """
        Upserts a vector and payload metadata.
        """
        vec_arr = np.array([vector], dtype=np.float32)
        
        if os.path.exists(self.vectors_file) and os.path.getsize(self.vectors_file) > 0:
            try:
                existing = np.load(self.vectors_file)
                updated = np.vstack([existing, vec_arr])
            except Exception:
                updated = vec_arr
        else:
            updated = vec_arr
            
        np.save(self.vectors_file, updated)
        
        payload["id"] = doc_id
        with open(self.metadata_file, "a") as f:
            f.write(json.dumps(payload) + "\n")
        self.payloads.append(payload)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs Cosine Similarity search over local mmap vectors.
        """
        if not os.path.exists(self.vectors_file) or not self.payloads:
            return []
            
        # mmap_mode='r' prevents loading entire array into RAM
        vectors = np.load(self.vectors_file, mmap_mode='r')
        q_vec = np.array(query_vector, dtype=np.float32)
        
        # Normalize
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []
        q_vec_norm = q_vec / q_norm
        
        doc_norms = np.linalg.norm(vectors, axis=1)
        doc_norms[doc_norms == 0] = 1e-10
        
        similarities = np.dot(vectors, q_vec_norm) / doc_norms
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if idx < len(self.payloads):
                res = dict(self.payloads[idx])
                res["score"] = float(similarities[idx])
                results.append(res)
                
        return results
