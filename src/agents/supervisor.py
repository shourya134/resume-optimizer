"""
Supervisor Agent

Responsible for orchestrating the workflow and handling coordination.
"""

from typing import Literal
from ..graph.state import AgentState
from ..llm.prompts import get_system_prompt


class SupervisorAgent:
    """Supervisor agent for workflow orchestration"""

    def __init__(self):
        self.system_prompt = get_system_prompt("supervisor")

    def validate_inputs(self, state: AgentState) -> AgentState:
        """
        Validate input data before starting workflow.

        Args:
            state: Current agent state

        Returns:
            Updated state with validation results
        """
        state["current_agent"] = "supervisor"

        errors = []

        # Validate resume
        if not state.get("resume_tex"):
            errors.append("Resume LaTeX content is empty")
        elif len(state["resume_tex"]) < 100:
            errors.append("Resume appears too short (less than 100 characters)")

        # Validate job description
        if not state.get("job_description"):
            errors.append("Job description is empty")
        elif len(state["job_description"]) < 50:
            errors.append("Job description appears too short")

        if errors:
            state["errors"].extend(errors)
            print("[X] Input validation failed:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("[OK] Input validation passed")

        return state

    def should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """
        Determine if workflow should continue or end.

        Args:
            state: Current agent state

        Returns:
            "continue" or "end"
        """
        # Check for critical errors
        if state.get("errors"):
            return "end"

        # Check workflow stage
        stage = state.get("workflow_stage", "")

        if stage == "complete":
            return "end"

        return "continue"

    def finalize(self, state: AgentState) -> AgentState:
        """
        Finalize the workflow and prepare output.

        Args:
            state: Current agent state

        Returns:
            Updated state with workflow_stage set to complete
        """
        state["current_agent"] = "supervisor"
        state["workflow_stage"] = "complete"

        # Print summary
        print("\n" + "="*60)
        print("RESUME OPTIMIZATION COMPLETE")
        print("="*60)

        similarity = state.get("similarity_score", 0)
        gaps_count = len(state.get("identified_gaps", []))
        recs_count = len(state.get("recommendations", []))

        print(f"Similarity Score: {similarity:.1f}/100")
        print(f"Identified Gaps: {gaps_count}")
        print(f"Recommendations: {recs_count}")

        if state.get("modified_resume_tex"):
            changes_count = len(state.get("applied_changes", []))
            print(f"Applied Changes: {changes_count}")

        if state.get("errors"):
            print(f"\n[WARNING] Warnings/Errors: {len(state['errors'])}")

        print("="*60 + "\n")

        return state


def validate_inputs_node(state: AgentState) -> AgentState:
    """
    LangGraph node function for input validation.

    Args:
        state: Current agent state

    Returns:
        Updated state
    """
    supervisor = SupervisorAgent()
    return supervisor.validate_inputs(state)


def finalize_node(state: AgentState) -> AgentState:
    """
    LangGraph node function for workflow finalization.

    Args:
        state: Current agent state

    Returns:
        Updated state
    """
    supervisor = SupervisorAgent()
    return supervisor.finalize(state)
