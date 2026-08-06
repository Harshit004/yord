import asyncio
import os
import uuid
import json
import psutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict

try:
    from .state.bus import YordState
    from .router import route_query
    from .interrogator import generate_triage_questions
    from .state.memory_guardian import memory_guardian_task
    from .config import SYSTEM_CONFIG
    from .graph import YORD_GRAPH
    from .engine.ingestion import DocumentIngestionEngine
    from .engine.pdf_exporter import generate_pdf_report
    from .engine.skill_installer import SKILL_INSTALLER
except ImportError:
    from state.bus import YordState
    from router import route_query
    from interrogator import generate_triage_questions
    from state.memory_guardian import memory_guardian_task
    from config import SYSTEM_CONFIG
    from graph import YORD_GRAPH
    from engine.ingestion import DocumentIngestionEngine
    from engine.pdf_exporter import generate_pdf_report
    from engine.skill_installer import SKILL_INSTALLER

app = FastAPI(title="YORD Local AI Harness", description="Local-first 12M Token Research Harness Backend")

ingestion_engine = DocumentIngestionEngine()

# Session-level PDF Artifact Registry: session_id -> List[Dict[str, str]]
SESSION_PDF_REGISTRY: Dict[str, List[Dict[str, str]]] = {}

class QueryRequest(BaseModel):
    session_id: Optional[str] = "default_session"
    query: str
    export_pdf: Optional[bool] = False

class SkillInstallRequest(BaseModel):
    query_or_name: str

@app.on_event("startup")
async def startup_event():
    """Starts background RAM monitoring on server boot."""
    asyncio.create_task(memory_guardian_task())

@app.get("/health")
async def health_check():
    """Health check endpoint returning dynamic hardware and physical RAM constraints."""
    mem = psutil.virtual_memory()
    used_gb = round(mem.used / (1024**3), 2)
    total_gb = round(mem.total / (1024**3), 2)
    percent = mem.percent

    return JSONResponse(content={
        "status": "ok",
        "ram": {
            "used_gb": used_gb,
            "total_gb": total_gb,
            "percent": percent,
            "display": f"RAM: {used_gb} GB / {total_gb} GB ({percent}% - {'Normal' if percent < 75 else 'Warning'})"
        },
        "hardware": SYSTEM_CONFIG
    })

@app.post("/api/query")
async def process_query(req: QueryRequest):
    """
    Executes a query through the LangGraph research state machine.
    Tracks per-chat PDF artifacts and handles skill installation commands.
    """
    session_id = req.session_id or "default_session"
    if session_id not in SESSION_PDF_REGISTRY:
        SESSION_PDF_REGISTRY[session_id] = []

    # Check if query is an explicit skill installation prompt
    if req.query.lower().startswith("install skill") or req.query.lower().startswith("find skill"):
        install_res = SKILL_INSTALLER.search_and_install(req.query)
        return JSONResponse(content={
            "query_id": str(uuid.uuid4()),
            "raw_query": req.query,
            "query_type": "distill",
            "synthesized_text": f"### Skill Installation Result\n\n✨ **New Skill Registered:** `{install_res['skill_name']}`\n- **Status:** {install_res['status'].upper()}\n- **Path:** {install_res['path']}",
            "contradiction_score": 0.0,
            "pdf_artifacts": SESSION_PDF_REGISTRY[session_id]
        })

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
        "pdf_artifacts": SESSION_PDF_REGISTRY[session_id],
        "iteration_count": 0
    }
    
    final_state = YORD_GRAPH.invoke(initial_state)
    
    # Generate PDF Report if requested or generated during synthesis
    if req.export_pdf:
        pdf_name = f"Report_{final_state['query_id'][:8]}.pdf"
        pdf_out = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../logs/{pdf_name}"))
        pdf_path = generate_pdf_report(f"Research: {req.query[:40]}", final_state.get("synthesized_text", ""), pdf_out)
        
        artifact_entry = {
            "title": f"Report: {req.query[:30]}...",
            "filename": pdf_name,
            "path": pdf_path,
            "url": f"/api/pdf/download?path={pdf_path}"
        }
        SESSION_PDF_REGISTRY[session_id].append(artifact_entry)
        final_state["pdf_artifacts"] = SESSION_PDF_REGISTRY[session_id]
        
    return JSONResponse(content=final_state)

@app.post("/api/skills/install")
async def install_skill_endpoint(req: SkillInstallRequest):
    """Antigravity-style endpoint for finding & installing new skills."""
    res = SKILL_INSTALLER.search_and_install(req.query_or_name)
    return JSONResponse(content=res)

@app.get("/api/pdf/download")
async def download_pdf_artifact(path: str):
    """
    Downloads a PDF artifact file with native file save headers.
    """
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path) and abs_path.endswith(".pdf"):
        filename = os.path.basename(abs_path)
        return FileResponse(abs_path, filename=filename, media_type="application/pdf")
    return JSONResponse(status_code=404, content={"error": "PDF file not found"})

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
    Real-time streaming WebSocket endpoint for token-by-token UI updates.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            raw_query = payload.get("query", "")
            session_id = payload.get("session_id", "default_session")
            
            if session_id not in SESSION_PDF_REGISTRY:
                SESSION_PDF_REGISTRY[session_id] = []
            
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
                "pdf_artifacts": SESSION_PDF_REGISTRY[session_id],
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
                full_text = final_state.get("synthesized_text", "")
                
                # Token-by-token streaming chunk simulation over WebSocket
                words = full_text.split()
                chunk_size = 5
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i+chunk_size]) + " "
                    await websocket.send_json({
                        "event": "token_chunk",
                        "chunk": chunk
                    })
                    await asyncio.sleep(0.02)
                
                await websocket.send_json({
                    "event": "graph_execution",
                    "status": "completed",
                    "synthesized_text": full_text,
                    "contradiction_score": final_state.get("contradiction_score", 0.0),
                    "pdf_artifacts": SESSION_PDF_REGISTRY[session_id]
                })
    except WebSocketDisconnect:
        pass

# Serve static figures directory
figures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static/figures"))
os.makedirs(figures_dir, exist_ok=True)
app.mount("/figures", StaticFiles(directory=figures_dir), name="figures")

# Serve Antigravity Glassmorphism Web App at root
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
