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
from ..agents.gap_selector import select_gaps_node
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
    # Check for critical errors - stop on FIRST error
    errors = state.get("errors", [])
    if len(errors) > 0:
        print(f"[X] Stopping workflow due to error: {errors[-1]}")
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


def should_select_gaps(state: AgentState) -> Literal["select_gaps", "generate_recommendations"]:
    """
    Routing function to determine if user should select gaps interactively.

    Args:
        state: Current agent state

    Returns:
        "select_gaps" for interactive mode, "generate_recommendations" for auto mode
    """
    gaps = state.get("identified_gaps", [])

    # If no gaps, skip to recommendations (which will be empty)
    if len(gaps) == 0:
        return "generate_recommendations"

    # If user has already selected gaps (resuming workflow), skip selection
    if state.get("user_selected_gaps") is not None:
        return "generate_recommendations"

    # Check if interactive mode is enabled
    # Default to interactive mode unless explicitly disabled
    interactive_mode = state.get("interactive_gap_selection", True)

    if interactive_mode:
        return "select_gaps"
    else:
        # Auto mode: skip gap selection, use all gaps
        return "generate_recommendations"


def check_for_errors(state: AgentState) -> Literal["continue", "abort"]:
    """
    Check if any errors occurred and abort workflow if so.

    Args:
        state: Current agent state

    Returns:
        "continue" if no errors, "abort" if errors detected
    """
    errors = state.get("errors", [])
    if len(errors) > 0:
        print(f"[X] Error detected: {errors[-1]}")
        print(f"[X] Aborting workflow to prevent token waste")
        return "abort"
    return "continue"


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
    workflow.add_node("select_gaps", select_gaps_node)
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

    # Parse resume - check for errors before continuing
    workflow.add_conditional_edges(
        "parse_resume",
        check_for_errors,
        {
            "continue": "analyze_job",
            "abort": "finalize"
        }
    )

    # After job analysis - check for errors before continuing
    workflow.add_conditional_edges(
        "analyze_job",
        check_for_errors,
        {
            "continue": "analyze_gaps",
            "abort": "finalize"
        }
    )

    # After gap analysis - check for errors, then decide on gap selection
    def check_errors_then_select_gaps(state: AgentState) -> Literal["abort", "select_gaps", "generate_recommendations"]:
        """First check errors, then route to gap selection or recommendations."""
        if check_for_errors(state) == "abort":
            return "abort"
        return should_select_gaps(state)

    workflow.add_conditional_edges(
        "analyze_gaps",
        check_errors_then_select_gaps,
        {
            "abort": "finalize",
            "select_gaps": "select_gaps",
            "generate_recommendations": "generate_recommendations"
        }
    )

    # After gap selection, proceed to recommendations
    workflow.add_edge("select_gaps", "generate_recommendations")

    # After recommendations - check for errors, then decide on applying edits
    def check_errors_then_apply(state: AgentState) -> Literal["abort", "apply_edits", "skip_edits"]:
        """First check errors, then route to apply or skip."""
        if check_for_errors(state) == "abort":
            return "abort"
        return should_apply_edits(state)

    workflow.add_conditional_edges(
        "generate_recommendations",
        check_errors_then_apply,
        {
            "abort": "finalize",
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


def create_apply_workflow() -> StateGraph:
    """
    Create a minimal workflow that ONLY applies recommendations.

    Use this when you already have recommendations from a previous run
    and just need to apply user-selected ones. This avoids re-parsing,
    re-analyzing, and re-generating recommendations, saving ~3000 tokens.

    Returns:
        Compiled StateGraph with only apply and finalize nodes
    """
    workflow = StateGraph(AgentState)

    # Only two nodes needed!
    workflow.add_node("apply_recommendations", apply_recommendations_node)
    workflow.add_node("finalize", finalize_node)

    workflow.set_entry_point("apply_recommendations")
    workflow.add_edge("apply_recommendations", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


def run_workflow(resume_tex: str,
                 job_description: str,
                 resume_path: str,
                 job_path: str,
                 interactive_gap_selection: bool = True,
                 auto_select_gap_severity: str = "") -> AgentState:
    """
    Run the complete resume optimization workflow.

    Args:
        resume_tex: LaTeX resume content
        job_description: Job description text
        resume_path: Path to resume file
        job_path: Path to job description file
        interactive_gap_selection: Enable interactive gap selection
        auto_select_gap_severity: Auto-select gaps by severity (high, medium, low)

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
    initial_state["interactive_gap_selection"] = interactive_gap_selection
    if auto_select_gap_severity:
        initial_state["auto_select_gap_severity"] = auto_select_gap_severity

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
    resume_path: str,
    job_path: str,
    previous_state: AgentState = None,
    selected_gap_ids: list = None
) -> AgentState:
    """
    Apply user-selected recommendations WITHOUT re-running analysis.

    This function uses the previous state to avoid re-parsing, re-analyzing,
    and re-generating recommendations. This saves approximately 3000 tokens
    by only running the apply_recommendations and finalize nodes.

    Args:
        resume_tex: LaTeX resume content
        job_description: Job description text
        accepted_recommendation_ids: List of recommendation IDs to apply
        resume_path: Path to resume file
        job_path: Path to job description file
        previous_state: State from phase 1 (with recommendations already generated)
        selected_gap_ids: List of selected gap IDs (optional)

    Returns:
        Final agent state with results
    """
    from .state import create_initial_state

    if previous_state:
        # REUSE previous state! Don't recreate from scratch
        state = dict(previous_state)  # Make a copy
        state["user_accepted_recommendations"] = accepted_recommendation_ids
        print("[OK] Reusing previous analysis state (saves ~3000 tokens)")
    else:
        # Fallback: create initial state (expensive, only if previous_state not provided)
        print("[WARNING] No previous state provided, creating new state")
        state = create_initial_state(
            resume_tex=resume_tex,
            job_description=job_description,
            resume_path=resume_path,
            job_path=job_path
        )
        state["user_accepted_recommendations"] = accepted_recommendation_ids

        if selected_gap_ids:
            state["user_selected_gaps"] = selected_gap_ids

    print("\n" + "="*60)
    print("APPLYING SELECTED RECOMMENDATIONS")
    print("="*60 + "\n")

    # Use minimal workflow - ONLY apply and finalize (saves tokens!)
    app = create_apply_workflow()
    final_state = app.invoke(state)

    return final_state
