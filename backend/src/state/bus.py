from typing import TypedDict, Optional, List, Dict

class YordState(TypedDict):
    """
    State object for LangGraph execution in YORD.
    RAM Impact: Very low (~1-2KB per instance). Stores scalar metrics and pointers, not heavy objects.
    """
    query_id: str
    raw_query: str
    query_type: str  # 'rag' | 'math' | 'code' | 'triage' | 'distill'
    ambiguity_score: float  # 0.0 (clear) to 1.0 (vague)
    triage_questions: List[str]
    triage_answers: List[str]
    context_chunk_ids: List[str]  # UUIDs pointing to Qdrant (NOT raw text)
    context_token_count: int
    synthesized_text: str
    contradiction_score: float  # 0.0 = entailment, 1.0 = contradiction
    sandbox_stdout: Optional[str]
    figures: List[str]  # File paths to matplotlib PNGs
    final_output: str
    pdf_requested: bool
    pdf_artifacts: List[Dict[str, str]]  # List of {"title": str, "path": str, "url": str}
    iteration_count: int  # Hard cap: 3
