"""
PM Agent (Orchestration Coordinator) for YORD.
Plans research strategy, determines execution path across RAG, Web, Math, and Creative nodes.
RAM Impact: Negligible (<5MB). Pure control flow and prompt framing.
"""

from typing import Dict, Any
try:
    from ..state.bus import YordState
except ImportError:
    from state.bus import YordState

def pm_plan_step(state: YordState) -> YordState:
    """
    Evaluates current state and plans the next execution step.
    Prevents runaway loops by enforcing a hard iteration cap of 3.
    """
    query_type = state.get("query_type", "rag")
    iteration = state.get("iteration_count", 0)
    
    if iteration >= 3:
        # Force completion if max iterations reached
        state["final_output"] = state.get("synthesized_text", "Maximum research depth reached.")
        return state
        
    state["iteration_count"] = iteration + 1
    
    # Strategy selection based on query classification
    if query_type == "math":
        # Route to math execution path
        state["sandbox_stdout"] = "Math sandbox execution planned."
    elif query_type == "web":
        # Web search augmentation planned
        pass
    elif query_type == "marketing":
        # Marketing content pipeline
        pass
    else:
        # Default RAG pipeline
        pass
        
    return state
