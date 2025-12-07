"""
Gap Selector Agent

Responsible for interactive gap selection (pausing workflow for user input).
"""

from typing import List
from ..graph.state import AgentState, Gap
from ..ui.gap_selection_interface import interactive_gap_selection


class GapSelectorAgent:
    """Agent for interactive gap selection"""

    def select_gaps(self, state: AgentState) -> AgentState:
        """
        Present gaps to user for selection.

        Args:
            state: Current agent state with identified gaps

        Returns:
            Updated state with user_selected_gaps
        """
        try:
            # Update workflow stage
            state["current_agent"] = "gap_selector"
            state["workflow_stage"] = "selecting_gaps"

            # Get identified gaps
            gaps = state.get("identified_gaps", [])

            if not gaps:
                print("[WARNING] No gaps identified, skipping selection")
                state["user_selected_gaps"] = []
                return state

            # Check if auto-selection by severity
            auto_severity = state.get("auto_select_gap_severity")

            if auto_severity:
                # Auto-select by severity
                selected_indices = []
                severity_order = {"high": 1, "medium": 2, "low": 3}
                max_severity_value = severity_order.get(auto_severity.lower(), 3)

                for i, gap in enumerate(gaps):
                    gap_severity_value = severity_order.get(gap["severity"].lower(), 3)
                    if gap_severity_value <= max_severity_value:
                        selected_indices.append(f"gap_{i}")

                state["user_selected_gaps"] = selected_indices
                print(f"[OK] Auto-selected {len(selected_indices)} gaps (severity <= {auto_severity})")
            else:
                # Interactive selection
                selected_ids = interactive_gap_selection(gaps, auto_severity or "low")
                state["user_selected_gaps"] = selected_ids
                print(f"[OK] User selected {len(selected_ids)} gaps")

            return state

        except Exception as e:
            error_msg = f"Gap Selector error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"[X] {error_msg}")
            # On error, select all gaps to continue workflow
            state["user_selected_gaps"] = [f"gap_{i}" for i in range(len(gaps))]
            return state


def select_gaps_node(state: AgentState) -> AgentState:
    """
    LangGraph node function for gap selection.

    Args:
        state: Current agent state

    Returns:
        Updated state
    """
    agent = GapSelectorAgent()
    return agent.select_gaps(state)
