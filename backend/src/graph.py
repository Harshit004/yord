"""
LangGraph StateGraph Workflow Definition for YORD.
Orchestrates the sequential and conditional execution flow across:
Router -> (Interrogator if ambiguous) -> PM Agent -> Synthesizer -> Critic -> (Distiller if valid) -> Final Output.
RAM Impact: Negligible (<5MB). Pure Graph structure.
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

try:
    from .state.bus import YordState
    from .router import route_query
    from .interrogator import generate_triage_questions
    from .agents.pm_agent import pm_plan_step
    from .agents.synthesizer import synthesize_response
    from .agents.critic import evaluate_critic
    from .agents.distiller import distill_skill
except ImportError:
    from state.bus import YordState
    from router import route_query
    from interrogator import generate_triage_questions
    from agents.pm_agent import pm_plan_step
    from agents.synthesizer import synthesize_response
    from agents.critic import evaluate_critic
    from agents.distiller import distill_skill

def router_node(state: YordState) -> YordState:
    """Node wrapper for Zero-LLM Router."""
    return route_query(state)

def interrogator_node(state: YordState) -> YordState:
    """Node wrapper for Interrogation Node."""
    return generate_triage_questions(state)

def pm_node(state: YordState) -> YordState:
    """Node wrapper for PM Agent planner."""
    return pm_plan_step(state)

def synthesizer_node(state: YordState) -> YordState:
    """Node wrapper for Research Synthesizer."""
    return synthesize_response(state)

def critic_node(state: YordState) -> YordState:
    """Node wrapper for Adversarial Critic."""
    return evaluate_critic(state)

def distiller_node(state: YordState) -> YordState:
    """Node wrapper for Skill Distiller."""
    return distill_skill(state)

def route_decision(state: YordState) -> Literal["interrogator", "pm_agent"]:
    """Conditional edge decision after routing."""
    if state.get("query_type") == "triage":
        return "interrogator"
    return "pm_agent"

def critic_decision(state: YordState) -> Literal["synthesizer", "distiller"]:
    """Conditional edge decision after critic evaluation."""
    score = state.get("contradiction_score", 0.0)
    iteration = state.get("iteration_count", 0)
    
    # If high contradiction and under max iterations, re-synthesize
    if score > 0.5 and iteration < 3:
        return "synthesizer"
    return "distiller"

def build_yord_graph() -> StateGraph:
    """
    Constructs the compiled LangGraph execution graph.
    """
    workflow = StateGraph(YordState)

    # Add Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("interrogator", interrogator_node)
    workflow.add_node("pm_agent", pm_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("distiller", distiller_node)

    # Set Entry Point
    workflow.set_entry_point("router")

    # Conditional Branching after Router
    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "interrogator": "interrogator",
            "pm_agent": "pm_agent"
        }
    )

    workflow.add_edge("interrogator", END)
    workflow.add_edge("pm_agent", "synthesizer")
    workflow.add_edge("synthesizer", "critic")

    # Conditional Branching after Critic
    workflow.add_conditional_edges(
        "critic",
        critic_decision,
        {
            "synthesizer": "synthesizer",
            "distiller": "distiller"
        }
    )

    workflow.add_edge("distiller", END)

    return workflow.compile()

# Singleton compiled graph instance
YORD_GRAPH = build_yord_graph()
