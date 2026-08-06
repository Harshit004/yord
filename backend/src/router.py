import re
from typing import Dict, List, Tuple
try:
    from .state.bus import YordState
except ImportError:
    from state.bus import YordState

# Keyword lists for specialized execution engines
MATH_KEYWORDS = {"sympy", "equation", "calculate", "integrate", "derivative", "matrix", "calculus"}
CODE_KEYWORDS = {"def ", "fn ", "struct", "impl", "function", "debug", "python", "rust", "javascript", "bug"}
DISTILL_KEYWORDS = {"distill", "extract skill", "save pattern"}

def calculate_ambiguity(query: str, query_type: str) -> float:
    """
    Calculates ambiguity score.
    Ensures open-domain general queries (history, philosophy, science, conversation)
    are treated as low-ambiguity open-ended synthesis requests.
    """
    words = [w for w in re.findall(r'\w+', query.lower())]
    word_count = len(words)
    
    # Extremely short single-word queries are genuinely ambiguous (e.g., "math", "help")
    if word_count < 2:
        return 0.8
        
    # General multi-word open-domain queries (>= 3 words) are well-formed open prompts
    if query_type == "rag":
        if word_count >= 3:
            return 0.1  # Low ambiguity, proceed directly to open-domain synthesis
        return 0.4

    # For specialized keywords, check overlap
    domain_keywords = set()
    if query_type == "math": domain_keywords = MATH_KEYWORDS
    elif query_type == "code": domain_keywords = CODE_KEYWORDS
    elif query_type == "distill": domain_keywords = DISTILL_KEYWORDS
    
    overlap = len(set(words).intersection(domain_keywords))
    if overlap > 0:
        return max(0.0, 0.3 - (0.1 * overlap))
        
    return 0.2

def route_query(state: YordState) -> YordState:
    """
    Deterministic Zero-LLM Router.
    Routes specialized tools when explicit intent is detected,
    otherwise defaults to Open-Domain RAG/Synthesis Engine for any topic.
    Completes in < 5ms.
    """
    query = state.get("raw_query", "").lower()
    
    query_type = "rag"  # Open-Domain General Synthesis (Default for all topics)
    
    if any(kw in query for kw in MATH_KEYWORDS):
        query_type = "math"
    elif any(kw in query for kw in CODE_KEYWORDS):
        query_type = "code"
    elif any(kw in query for kw in DISTILL_KEYWORDS):
        query_type = "distill"
        
    ambiguity_score = calculate_ambiguity(query, query_type)
    
    # Triage is reserved strictly for vague 1-word inputs (e.g., "math", "fix")
    if ambiguity_score > 0.7:
        query_type = "triage"
        
    state["query_type"] = query_type
    state["ambiguity_score"] = ambiguity_score
    
    return state
