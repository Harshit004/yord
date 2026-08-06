"""
Comprehensive Pipeline Test Suite for YORD.
Verifies Router, Interrogator, Memory Guardian, Vector Store, LangGraph, PDF Exporter, and Universal Subagent Dispatcher.
"""

import sys
import os

# Ensure src directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from state.bus import YordState
from router import route_query
from interrogator import generate_triage_questions
from engine.embeddings import LightweightEmbeddings
from engine.qdrant_client import LocalVectorStore
from graph import YORD_GRAPH
from engine.pdf_exporter import generate_pdf_report
from agents.subagent_dispatcher import DISPATCHER

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

def test_interrogator():
    print("Testing Interrogator...")
    state: YordState = {
        "query_id": "test-2",
        "raw_query": "m",
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

def test_subagent_dispatcher():
    print("Testing Universal Subagent Dispatcher...")
    state: YordState = {
        "query_id": "test-subagent-1",
        "raw_query": "Analyze 16th-century Ottoman maritime law and Mediterranean trade routes",
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
    res = DISPATCHER.dispatch_subagent(state)
    assert "Subagent Execution" in res["synthesized_text"], "Subagent failed to execute"
    print("  [PASS] Universal Subagent Dispatcher dynamic persona execution")

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

def test_langgraph():
    print("Testing LangGraph Execution Pipeline...")
    initial_state: YordState = {
        "query_id": "test-graph-1",
        "raw_query": "Analyze attention mechanisms in transformers",
        "query_type": "rag",
        "ambiguity_score": 0.0,
        "triage_questions": [],
        "triage_answers": [],
        "context_chunk_ids": ["chunk-101", "chunk-102"],
        "context_token_count": 1000,
        "synthesized_text": "",
        "contradiction_score": 0.0,
        "sandbox_stdout": None,
        "figures": [],
        "final_output": "",
        "pdf_requested": False,
        "iteration_count": 0
    }
    result_state = YORD_GRAPH.invoke(initial_state)
    assert "synthesized_text" in result_state and len(result_state["synthesized_text"]) > 0, "Graph failed to synthesize text"
    assert "contradiction_score" in result_state, "Graph failed to compute contradiction score"
    print("  [PASS] LangGraph StateGraph compiled execution")

def test_pdf_export():
    print("Testing PDF Exporter...")
    out_file = "/Users/harshit/Desktop/yord/logs/test_report.pdf"
    res = generate_pdf_report("Test Research Report", "### Summary\nThis is a test PDF generation run.", out_file)
    assert os.path.exists(res), "PDF file was not created"
    print("  [PASS] PDF report generation")

if __name__ == "__main__":
    print("\n--- RUNNING YORD BACKEND INTEGRATION TESTS ---")
    test_router()
    test_interrogator()
    test_subagent_dispatcher()
    test_vector_store()
    test_langgraph()
    test_pdf_export()
    print("--- ALL TESTS PASSED SUCCESSFULLY! ---\n")
