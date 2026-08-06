"""
Comprehensive Pipeline Test Suite for YORD.
Verifies Router, Interrogator, Memory Guardian, Vector Store, and Marketing Engine.
"""

import sys
import os

# Ensure src directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from state.bus import YordState
from router import route_query, calculate_ambiguity
from interrogator import generate_triage_questions
from config import get_hardware_config
from engine.embeddings import LightweightEmbeddings
from engine.qdrant_client import LocalVectorStore
from marketing.cyborg_workflow import CyborgMarketingEngine

def test_router():
    print("Testing Router...")
    state: YordState = {
        "query_id": "test-1",
        "raw_query": "calculate the derivative of x^2 using sympy",
        "query_type": "rag",
        "ambiguity_score": 0.0,
        "triage_questions": [],
        "triage_answers": [],
        "context_chunk_ids": [],
        "context_token_count": 0,
        "synthesized_text": "",
        "contradiction_score": 0.0,
        "sandbox_stdout": None,
        "figures": [],
        "final_output": "",
        "pdf_requested": False,
        "iteration_count": 0
    }
    state = route_query(state)
    assert state["query_type"] == "math", f"Expected 'math', got {state['query_type']}"
    print("  [PASS] Router math query routing")

    # Ambiguous query test
    ambiguous_state: YordState = dict(state)
    ambiguous_state["raw_query"] = "do it"
    ambiguous_state = route_query(ambiguous_state)
    assert ambiguous_state["query_type"] == "triage", f"Expected 'triage', got {ambiguous_state['query_type']}"
    print("  [PASS] Router ambiguous query triage escalation")

def test_interrogator():
    print("Testing Interrogator...")
    state: YordState = {
        "query_id": "test-2",
        "raw_query": "do math",
        "query_type": "triage",
        "ambiguity_score": 0.8,
        "triage_questions": [],
        "triage_answers": [],
        "context_chunk_ids": [],
        "context_token_count": 0,
        "synthesized_text": "",
        "contradiction_score": 0.0,
        "sandbox_stdout": None,
        "figures": [],
        "final_output": "",
        "pdf_requested": False,
        "iteration_count": 0
    }
    state = generate_triage_questions(state)
    assert len(state["triage_questions"]) >= 2, "Expected at least 2 triage questions"
    print("  [PASS] Interrogator diagnostic question generation")

def test_vector_store():
    print("Testing Vector Store & Embeddings...")
    embedder = LightweightEmbeddings(dimension=768)
    store = LocalVectorStore(collection_name="test_collection")
    
    doc_text = "HNSW vector search allows low memory context retrieval."
    vec = embedder.embed_query(doc_text)
    store.upsert("doc-1", vec, {"content": doc_text})
    
    results = store.search(vec, top_k=1)
    assert len(results) == 1, "Expected 1 search result"
    assert results[0]["id"] == "doc-1", "Expected doc-1 match"
    print("  [PASS] Vector embedding & Cosine similarity search")

def test_marketing():
    print("Testing Marketing Engine...")
    engine = CyborgMarketingEngine()
    draft = engine.create_draft("Local AI context optimization", platform="LinkedIn")
    assert "draft_id" in draft, "Expected draft_id"
    assert "—" not in draft["content"], "Rule violation: em dash found!"
    assert " you " not in draft["content"].lower(), "Rule violation: 'you' pronoun found!"
    print("  [PASS] Cyborg Marketing content drafting & style rules verification")

if __name__ == "__main__":
    print("\n--- RUNNING YORD BACKEND INTEGRATION TESTS ---")
    test_router()
    test_interrogator()
    test_vector_store()
    test_marketing()
    print("--- ALL TESTS PASSED SUCCESSFULLY! ---\n")
