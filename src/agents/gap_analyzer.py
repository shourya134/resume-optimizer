"""
Gap Analyzer Agent

Responsible for comparing resume against job requirements and identifying gaps.
"""

import json
from typing import List
from ..graph.state import AgentState, Gap
from ..llm.claude_client import get_claude_client
from ..llm.prompts import get_agent_prompt, get_system_prompt


class GapAnalyzerAgent:
    """Agent for analyzing gaps between resume and job requirements"""

    def __init__(self):
        self.client = get_claude_client()

    def analyze_gaps(self, state: AgentState) -> AgentState:
        """
        Analyze gaps between resume and job requirements.

        Args:
            state: Current agent state with parsed resume and job data

        Returns:
            Updated state with similarity_score and identified_gaps
        """
        try:
            # Update workflow stage
            state["current_agent"] = "gap_analyzer"
            state["workflow_stage"] = "analyzing"

            # Get parsed data
            resume_sections = state.get("resume_sections", [])
            resume_keywords = state.get("parsed_resume", {}).get("all_keywords", [])
            job_requirements = state.get("job_requirements", [])
            job_keywords = state.get("job_keywords", [])

            # Prepare data for prompt
            resume_sections_str = json.dumps([
                {"section": s["section_name"], "keywords": s["keywords"]}
                for s in resume_sections
            ], indent=2)

            job_requirements_str = json.dumps([
                {
                    "category": r["category"],
                    "requirement": r["requirement"],
                    "priority": r["priority"]
                }
                for r in job_requirements
            ], indent=2)

            # Create prompt
            prompt = get_agent_prompt(
                "gap_analyzer",
                resume_keywords=", ".join(resume_keywords[:50]),  # First 50 keywords
                job_keywords=", ".join(job_keywords[:50]),
                resume_sections=resume_sections_str,
                job_requirements=job_requirements_str
            )

            # Get system prompt
            system_prompt = get_system_prompt("gap_analyzer")

            # Call Claude to analyze gaps
            response = self.client.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )

            # Extract analysis results
            similarity_score = float(response.get("similarity_score", 0))
            keyword_overlap = float(response.get("keyword_overlap", 0))
            gaps_data = response.get("gaps", [])

            # Convert to Gap objects
            gaps: List[Gap] = []
            for gap in gaps_data:
                gaps.append(Gap(
                    gap_type=gap.get("gap_type", "other"),
                    description=gap.get("description", ""),
                    severity=gap.get("severity", "low"),
                    related_requirement=gap.get("related_requirement")
                ))

            # Update state
            state["similarity_score"] = similarity_score
            state["keyword_overlap"] = keyword_overlap
            state["identified_gaps"] = gaps  # This will append due to operator.add

            # Count gaps by severity
            high = sum(1 for g in gaps if g["severity"] == "high")
            medium = sum(1 for g in gaps if g["severity"] == "medium")
            low = sum(1 for g in gaps if g["severity"] == "low")

            print(f"[OK] Similarity Score: {similarity_score:.1f}/100")
            print(f"[OK] Keyword Overlap: {keyword_overlap:.1f}%")
            print(f"[OK] Identified {len(gaps)} gaps (High: {high}, Medium: {medium}, Low: {low})")

            return state

        except Exception as e:
            error_msg = f"Gap Analyzer error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"[X] {error_msg}")
            return state


def analyze_gaps_node(state: AgentState) -> AgentState:
    """
    LangGraph node function for gap analysis.

    Args:
        state: Current agent state

    Returns:
        Updated state
    """
    agent = GapAnalyzerAgent()
    return agent.analyze_gaps(state)
