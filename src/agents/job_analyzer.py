"""
Job Analyzer Agent

Responsible for analyzing job descriptions and extracting requirements.
"""

from typing import List
from ..graph.state import AgentState, JobRequirement
from ..llm.claude_client import get_claude_client
from ..llm.prompts import get_agent_prompt, get_system_prompt


class JobAnalyzerAgent:
    """Agent for analyzing job descriptions"""

    def __init__(self):
        self.client = get_claude_client()

    def analyze_job(self, state: AgentState) -> AgentState:
        """
        Analyze the job description and extract requirements.

        Args:
            state: Current agent state with job_description

        Returns:
            Updated state with job_requirements and job_keywords
        """
        try:
            # Update workflow stage
            state["current_agent"] = "job_analyzer"

            # Get the job description
            job_description = state["job_description"]

            # Create prompt
            prompt = get_agent_prompt(
                "job_analyzer",
                job_description=job_description
            )

            # Get system prompt
            system_prompt = get_system_prompt("job_analyzer")

            # Call Claude to analyze the job
            response = self.client.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )

            # Extract job data
            job_title = response.get("job_title", "Unknown")
            company_name = response.get("company_name", "Unknown")
            requirements_data = response.get("requirements", [])
            all_keywords = response.get("all_keywords", [])

            # Convert to JobRequirement objects
            job_requirements: List[JobRequirement] = []
            for req in requirements_data:
                job_requirements.append(JobRequirement(
                    category=req.get("category", "other"),
                    requirement=req.get("requirement", ""),
                    priority=req.get("priority", "preferred"),
                    keywords=req.get("keywords", [])
                ))

            # Update state
            state["job_title"] = job_title
            state["company_name"] = company_name
            state["job_requirements"] = job_requirements
            state["job_keywords"] = all_keywords

            print(f"[OK] Analyzed job: {job_title} at {company_name}")
            print(f"[OK] Extracted {len(job_requirements)} requirements")
            print(f"[OK] Identified {len(all_keywords)} keywords")

            return state

        except Exception as e:
            error_msg = f"Job Analyzer error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"[X] {error_msg}")
            return state


def analyze_job_node(state: AgentState) -> AgentState:
    """
    LangGraph node function for analyzing jobs.

    Args:
        state: Current agent state

    Returns:
        Updated state
    """
    agent = JobAnalyzerAgent()
    return agent.analyze_job(state)
