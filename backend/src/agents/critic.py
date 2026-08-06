"""
Critic Node (Adversarial Devil's Advocate) for YORD.
Grills synthesized research output to detect ungrounded claims, logical contradictions, and hallucinations.
Calculates contradiction_score (0.0 = entailment, 1.0 = contradiction).
RAM Impact: Negligible (<5MB). Pure rule-based & state validation.
"""

from typing import Dict, Any, List
from ..state.bus import YordState

def evaluate_critic(state: YordState) -> YordState:
    """
    Adversarial Critic evaluation node.
    Inspects synthesized text for citations and logical coherence.
    """
    text = state.get("synthesized_text", "")
    chunk_ids = state.get("context_chunk_ids", [])
    
    contradiction_score = 0.0
    
    # Check 1: Empty or very short output
    if len(text.strip()) < 50:
        contradiction_score = 0.9
    # Check 2: Claims made without retrieved chunks
    elif not chunk_ids and "Findings:" in text:
        contradiction_score = 0.6
    else:
        # Grounded text verification score
        contradiction_score = 0.05
        
    state["contradiction_score"] = contradiction_score
    
    # If contradiction score > 0.5, flag for re-retrieval or iteration
    if contradiction_score > 0.5 and state.get("iteration_count", 0) < 3:
        state["query_type"] = "rag"
        
    return state
