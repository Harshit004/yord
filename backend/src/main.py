import asyncio
import os
import uuid
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

try:
    from .state.bus import YordState
    from .router import route_query
    from .interrogator import generate_triage_questions
    from .state.memory_guardian import memory_guardian_task
    from .config import SYSTEM_CONFIG
    from .graph import YORD_GRAPH
    from .engine.ingestion import DocumentIngestionEngine
    from .engine.pdf_exporter import generate_pdf_report
except ImportError:
    from state.bus import YordState
    from router import route_query
    from interrogator import generate_triage_questions
    from state.memory_guardian import memory_guardian_task
    from config import SYSTEM_CONFIG
    from graph import YORD_GRAPH
    from engine.ingestion import DocumentIngestionEngine
    from engine.pdf_exporter import generate_pdf_report

app = FastAPI(title="YORD Local AI Harness", description="Local-first 12M Token Research Harness Backend")

ingestion_engine = DocumentIngestionEngine()

class QueryRequest(BaseModel):
    query: str
    export_pdf: Optional[bool] = False

@app.on_event("startup")
async def startup_event():
    """Starts background RAM monitoring on server boot."""
    asyncio.create_task(memory_guardian_task())

@app.get("/health")
async def health_check():
    """Health check endpoint returning dynamic hardware constraints."""
    return JSONResponse(content={
        "status": "ok",
        "hardware": SYSTEM_CONFIG
    })

@app.post("/api/query")
async def process_query(req: QueryRequest):
    """
    Executes a query through the LangGraph research state machine.
    """
    initial_state: YordState = {
        "query_id": str(uuid.uuid4()),
        "raw_query": req.query,
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
        "pdf_requested": req.export_pdf,
        "iteration_count": 0
    }
    
    final_state = YORD_GRAPH.invoke(initial_state)
    
    pdf_path = None
    if req.export_pdf:
        pdf_out = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../logs/report_{final_state['query_id'][:8]}.pdf"))
        pdf_path = generate_pdf_report(f"Research: {req.query}", final_state.get("synthesized_text", ""), pdf_out)
        final_state["pdf_path"] = pdf_path
        
    return JSONResponse(content=final_state)

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads and indexes a document (PDF, Markdown, TXT) into the local vector database.
    """
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/user_uploads"))
    os.makedirs(upload_dir, exist_ok=True)
    
    save_path = os.path.join(upload_dir, file.filename)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    chunk_count = ingestion_engine.process_file(save_path)
    return JSONResponse(content={
        "filename": file.filename,
        "chunks_indexed": chunk_count,
        "status": "success"
    })

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    Real-time streaming WebSocket endpoint for UI updates.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            raw_query = payload.get("query", "")
            
            state: YordState = {
                "query_id": str(uuid.uuid4()),
                "raw_query": raw_query,
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
            
            await websocket.send_json({"event": "routing", "status": "started"})
            state = route_query(state)
            await websocket.send_json({"event": "routing", "status": "completed", "type": state["query_type"]})
            
            if state["query_type"] == "triage":
                state = generate_triage_questions(state)
                await websocket.send_json({
                    "event": "triage_questions",
                    "questions": state["triage_questions"]
                })
            else:
                await websocket.send_json({"event": "graph_execution", "status": "started"})
                final_state = YORD_GRAPH.invoke(state)
                await websocket.send_json({
                    "event": "graph_execution",
                    "status": "completed",
                    "synthesized_text": final_state.get("synthesized_text", ""),
                    "contradiction_score": final_state.get("contradiction_score", 0.0)
                })
    except WebSocketDisconnect:
        pass
