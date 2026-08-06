import json
from typing import Dict, Any, List
try:
    from .state.bus import YordState
except ImportError:
    from state.bus import YordState

# Hardcoded decision tree to avoid I/O blocking and RAM overhead
DECISION_TREE: Dict[str, Any] = {
    "math": {
        "round_1": "Are you looking for a symbolic proof or a numerical calculation?",
        "options_1": ["Symbolic proof", "Numerical calculation"],
        "round_2": "Do you have specific variables/parameters in mind?"
    },
    "web": {
        "round_1": "Are you looking for recent news or general factual information?",
        "options_1": ["Recent news", "General facts"],
        "round_2": "Which specific domains or websites should I focus on?"
    },
    "creative": {
        "round_1": "What tone should the content have? (e.g., professional, casual, humorous)",
        "options_1": ["Professional", "Casual", "Humorous"],
        "round_2": "Is there a specific target length (e.g., short tweet vs long article)?"
    },
    "marketing": {
        "round_1": "Which platform is this for? (e.g., LinkedIn, Twitter, Email)",
        "options_1": ["LinkedIn", "Twitter", "Email"],
        "round_2": "Who is the target audience?"
    },
    "rag": {
        "round_1": "Could you provide more specific keywords or clarify the context?",
        "options_1": ["Provide more context", "Use default search"],
        "round_2": "Are there any specific documents I should prioritize?"
    }
}

def generate_triage_questions(state: YordState) -> YordState:
    """
    The Interrogation Node.
    Zero-LLM based diagnostic question generator to handle ambiguous queries.
    RAM Impact: Very low. Uses a small static dictionary for branching logic.
    
    Args:
        state: The current execution state
        
    Returns:
        YordState: Updated state with triage questions populated
    """
    query_type = state.get("query_type", "rag")
    # If it was marked as triage, we might need to fall back to looking at the query 
    # to guess the original domain, but for now we just use a generic fallback.
    # In practice, router might store original_query_type, but we'll infer it here
    # or just use rag if not found.
    
    # Simple original type inference if it was set to triage
    inferred_type = "rag"
    if query_type == "triage":
        query = state.get("raw_query", "").lower()
        if any(kw in query for kw in ["sympy", "equation", "prove", "math"]): inferred_type = "math"
        elif any(kw in query for kw in ["search", "latest", "news", "web"]): inferred_type = "web"
        elif any(kw in query for kw in ["write", "draft", "story", "creative"]): inferred_type = "creative"
        elif any(kw in query for kw in ["post", "audience", "social", "marketing"]): inferred_type = "marketing"
    else:
        inferred_type = query_type
        
    tree = DECISION_TREE.get(inferred_type, DECISION_TREE["rag"])
    
    # Generate 2 rounds of questioning
    questions: List[str] = [
        tree.get("round_1", "Can you clarify your request?"),
        tree.get("round_2", "Any specific constraints I should know about?")
    ]
    
    # State update
    state["triage_questions"] = questions
    
    # If the user has provided answers (e.g., from UI), we would process them here.
    # For now, we assume the pipeline will pause or UI will handle it.
    if "triage_answers" not in state or not state["triage_answers"]:
        state["triage_answers"] = []
        
    return state
