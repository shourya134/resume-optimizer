"""
LangGraph Workflow Builder

Defines the multi-agent workflow graph for resume optimization.
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from .state import AgentState
from ..agents.supervisor import validate_inputs_node, finalize_node
from ..agents.latex_parser import parse_resume_node
from ..agents.job_analyzer import analyze_job_node
from ..agents.gap_analyzer import analyze_gaps_node
from ..agents.recommendation_generator import generate_recommendations_node
from ..agents.latex_editor import apply_recommendations_node


def should_continue_workflow(state: AgentState) -> Literal["continue", "end"]:
    """
    Routing function to determine if workflow should continue.

    Args:
        state: Current agent state

    Returns:
        "continue" to proceed with workflow, "end" to stop
    """
    # Check for critical errors
    if state.get("errors"):
        error_count = len(state["errors"])
        if error_count > 5:  # Too many errors
            print(f"✗ Stopping workflow due to {error_count} errors")
            return "end"

    # Check if we have required data from validation
    if not state.get("resume_tex") or not state.get("job_description"):
        return "end"

    return "continue"


def should_apply_edits(state: AgentState) -> Literal["apply_edits", "skip_edits"]:
    """
    Routing function to determine if we should apply edits.

    Args:
        state: Current agent state

    Returns:
        "apply_edits" if we have recommendations to apply, "skip_edits" otherwise
    """
    recommendations = state.get("recommendations", [])

    # If user has made selections, respect them
    if state.get("user_accepted_recommendations") is not None:
        accepted = state.get("user_accepted_recommendations", [])
        if len(accepted) > 0:
            return "apply_edits"
        else:
            print("[WARNING] No recommendations accepted by user, skipping edits")
            return "skip_edits"

    # If no user selection, check if we have any recommendations
    if len(recommendations) > 0:
        return "apply_edits"
    else:
        print("[WARNING] No recommendations generated, skipping edits")
        return "skip_edits"


def create_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow.

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("validate_inputs", validate_inputs_node)
    workflow.add_node("parse_resume", parse_resume_node)
    workflow.add_node("analyze_job", analyze_job_node)
    workflow.add_node("analyze_gaps", analyze_gaps_node)
    workflow.add_node("generate_recommendations", generate_recommendations_node)
    workflow.add_node("apply_recommendations", apply_recommendations_node)
    workflow.add_node("finalize", finalize_node)

    # Set entry point
    workflow.set_entry_point("validate_inputs")

    # Add edges
    # After validation, check if we should continue
    workflow.add_conditional_edges(
        "validate_inputs",
        should_continue_workflow,
        {
            "continue": "parse_resume",
            "end": "finalize"
        }
    )

    # Parse resume and analyze job can run in parallel conceptually,
    # but for simplicity we'll run them sequentially
    workflow.add_edge("parse_resume", "analyze_job")

    # After job analysis, run gap analysis
    workflow.add_edge("analyze_job", "analyze_gaps")

    # After gap analysis, generate recommendations
    workflow.add_edge("analyze_gaps", "generate_recommendations")

    # After recommendations, decide whether to apply edits
    workflow.add_conditional_edges(
        "generate_recommendations",
        should_apply_edits,
        {
            "apply_edits": "apply_recommendations",
            "skip_edits": "finalize"
        }
    )

    # After applying recommendations, finalize
    workflow.add_edge("apply_recommendations", "finalize")

    # Finalize always ends
    workflow.add_edge("finalize", END)

    # Compile the graph
    return workflow.compile()


def run_workflow(resume_tex: str, job_description: str,
                 resume_path: str = None, job_path: str = None) -> AgentState:
    """
    Run the complete resume optimization workflow.

    Args:
        resume_tex: LaTeX resume content
        job_description: Job description text
        resume_path: Optional path to resume file
        job_path: Optional path to job description file

    Returns:
        Final agent state with results
    """
    from .state import create_initial_state

    # Create initial state
    initial_state = create_initial_state(
        resume_tex=resume_tex,
        job_description=job_description,
        resume_path=resume_path,
        job_path=job_path
    )

    # Create and run workflow
    print("\n" + "="*60)
    print("STARTING RESUME OPTIMIZATION WORKFLOW")
    print("="*60 + "\n")

    app = create_workflow()
    final_state = app.invoke(initial_state)

    return final_state


def run_workflow_with_user_selection(
    resume_tex: str,
    job_description: str,
    accepted_recommendation_ids: list,
    resume_path: str = None,
    job_path: str = None
) -> AgentState:
    """
    Run workflow up to recommendations, then apply user-selected changes.

    This is a two-phase approach:
    1. Run workflow up to recommendation generation
    2. User reviews and selects recommendations
    3. Apply selected recommendations

    Args:
        resume_tex: LaTeX resume content
        job_description: Job description text
        accepted_recommendation_ids: List of recommendation IDs to apply
        resume_path: Optional path to resume file
        job_path: Optional path to job description file

    Returns:
        Final agent state with results
    """
    from .state import create_initial_state

    # Create initial state with user selections
    initial_state = create_initial_state(
        resume_tex=resume_tex,
        job_description=job_description,
        resume_path=resume_path,
        job_path=job_path
    )
    initial_state["user_accepted_recommendations"] = accepted_recommendation_ids

    print("\n" + "="*60)
    print("APPLYING SELECTED RECOMMENDATIONS")
    print("="*60 + "\n")

    # Run workflow
    app = create_workflow()
    final_state = app.invoke(initial_state)

    return final_state
