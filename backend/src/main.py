import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import json

try:
    from .state.bus import YordState
    from .router import route_query
    from .interrogator import generate_triage_questions
    from .state.memory_guardian import memory_guardian_task
    from .config import SYSTEM_CONFIG
except ImportError:
    from state.bus import YordState
    from router import route_query
    from interrogator import generate_triage_questions
    from state.memory_guardian import memory_guardian_task
    from config import SYSTEM_CONFIG

app = FastAPI(title="YORD Local AI Harness", description="Minimal viable backend for YORD")

class QueryRequest(BaseModel):
    query: str

@app.on_event("startup")
async def startup_event():
    """
    Initializes background tasks on startup.
    RAM Impact: Minimal. Spawns asyncio tasks.
    """
    asyncio.create_task(memory_guardian_task())

@app.get("/health")
async def health_check():
    """
    Standard health check endpoint.
    Includes hardware config.
    """
    return JSONResponse(content={
        "status": "ok",
        "hardware": SYSTEM_CONFIG
    })

@app.post("/api/query")
async def process_query(req: QueryRequest):
    """
    REST endpoint for simple non-streaming queries.
    RAM Impact: Low. Creates initial state and passes through router.
    """
    state: YordState = {
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
        "pdf_requested": False,
        "iteration_count": 0
    }
    
    state = route_query(state)
    
    if state["query_type"] == "triage":
        state = generate_triage_questions(state)
        
    return JSONResponse(content=state)

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming responses to UI.
    RAM Impact: Moderate per connection, but scalable for local single-user use.
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
                await websocket.send_json({"event": "triage", "status": "started"})
                state = generate_triage_questions(state)
                await websocket.send_json({
                    "event": "triage_questions",
                    "questions": state["triage_questions"]
                })
            else:
                # Placeholder for actual engine execution (LangGraph)
                await websocket.send_json({"event": "execution", "status": "simulated", "message": f"Processing as {state['query_type']}..."})
                
    except WebSocketDisconnect:
        pass
