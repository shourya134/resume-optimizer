"""
Recommendation Generator Agent

Responsible for generating actionable recommendations for resume improvement.
"""

import json
from typing import List
from ..graph.state import AgentState, Recommendation
from ..llm.claude_client import get_claude_client
from ..llm.prompts import get_agent_prompt, get_system_prompt


class RecommendationGeneratorAgent:
    """Agent for generating resume improvement recommendations"""

    def __init__(self):
        self.client = get_claude_client()

    def generate_recommendations(self, state: AgentState) -> AgentState:
        """
        Generate prioritized recommendations for resume improvement.

        Args:
            state: Current agent state with gaps and analysis

        Returns:
            Updated state with recommendations
        """
        try:
            # Update workflow stage
            state["current_agent"] = "recommendation_generator"
            state["workflow_stage"] = "generating"

            # Get analysis data
            gaps = state.get("identified_gaps", [])
            resume_sections = state.get("resume_sections", [])
            job_requirements = state.get("job_requirements", [])
            similarity_score = state.get("similarity_score", 0)

            # Prepare data for prompt
            gaps_str = json.dumps([
                {
                    "type": g["gap_type"],
                    "description": g["description"],
                    "severity": g["severity"]
                }
                for g in gaps
            ], indent=2)

            sections_str = json.dumps([
                {"section": s["section_name"], "content": str(s.get("content", ""))[:200]}
                for s in resume_sections
            ], indent=2)

            requirements_str = json.dumps([
                {"requirement": r["requirement"], "priority": r["priority"]}
                for r in job_requirements[:10]  # Top 10 requirements
            ], indent=2)

            # Create prompt
            prompt = get_agent_prompt(
                "recommendation_generator",
                gaps=gaps_str,
                resume_sections=sections_str,
                job_requirements=requirements_str,
                similarity_score=similarity_score
            )

            # Get system prompt
            system_prompt = get_system_prompt("recommendation_generator")

            # Call Claude to generate recommendations
            response = self.client.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )

            # Extract recommendations
            recommendations_data = response.get("recommendations", [])

            # Convert to Recommendation objects
            recommendations: List[Recommendation] = []
            for i, rec in enumerate(recommendations_data):
                recommendations.append(Recommendation(
                    recommendation_id=rec.get("recommendation_id", f"rec_{i+1:03d}"),
                    priority=int(rec.get("priority", 3)),
                    category=rec.get("category", "other"),
                    description=rec.get("description", ""),
                    specific_action=rec.get("specific_action", ""),
                    rationale=rec.get("rationale", ""),
                    latex_modification=rec.get("latex_modification")
                ))

            # Sort by priority (1 is highest)
            recommendations.sort(key=lambda r: r["priority"])

            # Update state
            state["recommendations"] = recommendations  # This will append due to operator.add

            # Count by priority
            p1 = sum(1 for r in recommendations if r["priority"] == 1)
            p2 = sum(1 for r in recommendations if r["priority"] == 2)
            p3 = sum(1 for r in recommendations if r["priority"] == 3)

            print(f"[OK] Generated {len(recommendations)} recommendations")
            print(f"  Priority 1 (Critical): {p1}")
            print(f"  Priority 2 (Important): {p2}")
            print(f"  Priority 3 (Suggested): {p3}")

            return state

        except Exception as e:
            error_msg = f"Recommendation Generator error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"[X] {error_msg}")
            return state


def generate_recommendations_node(state: AgentState) -> AgentState:
    """
    LangGraph node function for generating recommendations.

    Args:
        state: Current agent state

    Returns:
        Updated state
    """
    agent = RecommendationGeneratorAgent()
    return agent.generate_recommendations(state)
