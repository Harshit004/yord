import re
from typing import Dict, List, Tuple
try:
    from .state.bus import YordState
except ImportError:
    from state.bus import YordState

# Keyword lists for fast zero-LLM classification
MATH_KEYWORDS = {"sympy", "equation", "prove", "calculate", "math", "integrate", "derivative"}
WEB_KEYWORDS = {"search", "latest", "news", "trending", "today", "current", "update"}
CREATIVE_KEYWORDS = {"write", "draft", "blog", "story", "poem", "generate", "create"}
MARKETING_KEYWORDS = {"post", "engage", "audience", "social", "campaign", "marketing", "seo"}

def calculate_ambiguity(query: str, query_type: str) -> float:
    """
    Calculates ambiguity score using heuristics.
    RAM Impact: Negligible. Uses basic string operations.
    
    Args:
        query: The user query string
        query_type: The identified query type
        
    Returns:
        float: Ambiguity score between 0.0 and 1.0.
    """
    words = query.lower().split()
    word_count = len(words)
    
    score = 0.0
    
    # Very short queries are often ambiguous unless they are very specific
    if word_count < 3:
        score += 0.4
        
    # Check for presence of domain keywords
    domain_keywords = set()
    if query_type == "math": domain_keywords = MATH_KEYWORDS
    elif query_type == "web": domain_keywords = WEB_KEYWORDS
    elif query_type == "creative": domain_keywords = CREATIVE_KEYWORDS
    elif query_type == "marketing": domain_keywords = MARKETING_KEYWORDS
    
    overlap = len(set(words).intersection(domain_keywords))
    if overlap == 0:
        score += 0.3
    else:
        score -= 0.1 * overlap
        
    # Simple check for explicit parameters like numbers or specific nouns
    param_count = sum(1 for word in words if word.isalnum() and not word.isalpha())
    if param_count > 0:
        score -= 0.2
        
    return max(0.0, min(1.0, score))

def route_query(state: YordState) -> YordState:
    """
    Deterministic Zero-LLM Router.
    Routes queries to appropriate handlers based on regex and keywords.
    Completes in < 5ms.
    RAM Impact: Near zero. Operates purely on simple dictionaries and sets.
    
    Args:
        state: The current execution state
        
    Returns:
        YordState: Updated state with determined query_type and ambiguity_score
    """
    query = state.get("raw_query", "").lower()
    
    query_type = "rag" # Default to RAG
    
    if any(kw in query for kw in MATH_KEYWORDS):
        query_type = "math"
    elif any(kw in query for kw in WEB_KEYWORDS):
        query_type = "web"
    elif any(kw in query for kw in CREATIVE_KEYWORDS):
        query_type = "creative"
    elif any(kw in query for kw in MARKETING_KEYWORDS):
        query_type = "marketing"
        
    ambiguity_score = calculate_ambiguity(query, query_type)
    
    if ambiguity_score > 0.6:
        query_type = "triage"
        
    state["query_type"] = query_type
    state["ambiguity_score"] = ambiguity_score
    
    return state
