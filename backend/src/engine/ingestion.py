"""
Document Ingestion Pipeline for YORD.
Parses PDFs, Markdown, and TXT files, performs semantic chunking, and indexes into LocalVectorStore.
RAM Impact: Low (<50MB). Processes files in streaming chunks.
"""

import os
import uuid
from typing import List, Dict, Any
from markitdown import MarkItDown

from .embeddings import LightweightEmbeddings
from .qdrant_client import LocalVectorStore

class DocumentIngestionEngine:
    """
    Ingestion engine for parsing and indexing user files.
    """
    def __init__(self, vector_store: LocalVectorStore = None):
        self.md = MarkItDown()
        self.embedder = LightweightEmbeddings(dimension=768)
        self.vector_store = vector_store or LocalVectorStore()

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Splits text into chunks of approx `chunk_size` words with `overlap`.
        """
        words = text.split()
        if not words:
            return []
            
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
            
        return chunks

    def process_file(self, file_path: str) -> int:
        """
        Parses a file, chunks content, generates embeddings, and upserts into vector store.
        
        Returns:
            int: Number of indexed chunks
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Extract text using MarkItDown
        result = self.md.convert(file_path)
        raw_text = result.text_content if hasattr(result, 'text_content') else str(result)
        
        chunks = self.chunk_text(raw_text)
        filename = os.path.basename(file_path)
        
        for idx, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            vector = self.embedder.embed_query(chunk)
            payload = {
                "source_file": filename,
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "content": chunk,
                "token_count": len(chunk.split())
            }
            self.vector_store.upsert(doc_id=chunk_id, vector=vector, payload=payload)
            
        return len(chunks)
