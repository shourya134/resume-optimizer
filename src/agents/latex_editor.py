"""
LaTeX Editor Agent

Responsible for applying recommendations to the LaTeX resume.
"""

import json
from typing import List, Dict, Any
from ..graph.state import AgentState
from ..llm.claude_client import get_claude_client
from ..llm.prompts import get_agent_prompt, get_system_prompt


class LaTeXEditorAgent:
    """Agent for editing LaTeX resumes based on recommendations"""

    def __init__(self):
        self.client = get_claude_client()

    def apply_recommendations(self, state: AgentState) -> AgentState:
        """
        Apply approved recommendations to the LaTeX resume.

        Args:
            state: Current agent state with recommendations

        Returns:
            Updated state with modified_resume_tex
        """
        try:
            # Update workflow stage
            state["current_agent"] = "latex_editor"
            state["workflow_stage"] = "editing"

            # Get data
            resume_tex = state["resume_tex"]
            recommendations = state.get("recommendations", [])
            resume_sections = state.get("resume_sections", [])

            # Filter for accepted recommendations (if user has selected)
            accepted_ids = state.get("user_accepted_recommendations")
            if accepted_ids is not None:
                recommendations = [
                    r for r in recommendations
                    if r["recommendation_id"] in accepted_ids
                ]

            # If no recommendations to apply, return original
            if not recommendations:
                print("[WARNING] No recommendations to apply")
                state["modified_resume_tex"] = resume_tex
                state["applied_changes"] = []
                return state

            # Prepare data for prompt
            recommendations_str = json.dumps([
                {
                    "id": r["recommendation_id"],
                    "priority": r["priority"],
                    "action": r["specific_action"],
                    "latex_modification": r.get("latex_modification", "")
                }
                for r in recommendations
            ], indent=2)
            # add a checker for none because most parameters pass none as values
            sections_str = json.dumps([
                {
                    "section": s["section_name"],
                    "content": s["content"][:300]  # Truncate for context
                }
                for s in resume_sections
            ], indent=2)

            # Create prompt
            prompt = get_agent_prompt(
                "latex_editor",
                resume_tex=resume_tex,
                recommendations=recommendations_str,
                resume_sections=sections_str
            )

            # Get system prompt
            system_prompt = get_system_prompt("latex_editor")

            # Call Claude to apply edits
            response = self.client.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=8192  # Larger for full resume
            )

            # Extract results
            modified_resume_tex = response.get("modified_resume_tex", resume_tex)
            applied_changes = response.get("applied_changes", [])

            # Update state
            state["modified_resume_tex"] = modified_resume_tex
            state["applied_changes"] = applied_changes

            print(f"[OK] Applied {len(applied_changes)} changes to resume")

            return state

        except Exception as e:
            error_msg = f"LaTeX Editor error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"[X] {error_msg}")
            # Fallback to original resume
            state["modified_resume_tex"] = state["resume_tex"]
            state["applied_changes"] = []
            return state


def apply_recommendations_node(state: AgentState) -> AgentState:
    """
    LangGraph node function for applying recommendations.

    Args:
        state: Current agent state

    Returns:
        Updated state
    """
    agent = LaTeXEditorAgent()
    return agent.apply_recommendations(state)
