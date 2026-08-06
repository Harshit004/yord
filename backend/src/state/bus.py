from typing import TypedDict, Optional

class YordState(TypedDict):
    """
    State object for LangGraph execution in YORD.
    RAM Impact: Very low (~1-2KB per instance). Stores scalar metrics and pointers, not heavy objects.
    """
    query_id: str
    raw_query: str
    query_type: str  # 'rag' | 'web' | 'math' | 'creative' | 'marketing'
    ambiguity_score: float  # 0.0 (clear) to 1.0 (vague)
    triage_questions: list[str]
    triage_answers: list[str]
    context_chunk_ids: list[str]  # UUIDs pointing to Qdrant (NOT raw text)
    context_token_count: int
    synthesized_text: str
    contradiction_score: float  # 0.0 = entailment, 1.0 = contradiction
    sandbox_stdout: Optional[str]
    figures: list[str]  # File paths to matplotlib PNGs
    final_output: str
    pdf_requested: bool
    iteration_count: int  # Hard cap: 3
