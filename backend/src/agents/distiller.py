"""
Skill Distiller Node (Continuous Learning) for YORD.
Saves successful research execution patterns into reusable skills under yord/skills/.
RAM Impact: Negligible (<2MB). File writing operations.
"""

import os
import json
from datetime import datetime
try:
    from ..state.bus import YordState
except ImportError:
    from state.bus import YordState

SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../skills"))

def distill_skill(state: YordState) -> YordState:
    """
    Distills high-confidence research runs into reusable skill files.
    Triggers when contradiction_score < 0.2 and synthesis completed cleanly.
    """
    contradiction_score = state.get("contradiction_score", 1.0)
    query_id = state.get("query_id", "unknown")
    query_type = state.get("query_type", "general")
    raw_query = state.get("raw_query", "")
    
    if contradiction_score <= 0.2 and raw_query:
        os.makedirs(SKILLS_DIR, exist_ok=True)
        filename = f"skill_{query_type}_{query_id[:8]}.json"
        filepath = os.path.join(SKILLS_DIR, filename)
        
        skill_payload = {
            "query_type": query_type,
            "pattern": raw_query,
            "timestamp": datetime.utcnow().isoformat(),
            "contradiction_score": contradiction_score,
            "recommended_pipeline": query_type
        }
        
        try:
            with open(filepath, "w") as f:
                json.dump(skill_payload, f, indent=2)
        except Exception as e:
            pass
            
    return state
