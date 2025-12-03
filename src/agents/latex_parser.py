"""
LaTeX Parser Agent

Responsible for parsing LaTeX resume files and extracting structured information.
"""

from typing import Dict, Any, List
import json
import re
from ..graph.state import AgentState, ResumeSection
from ..llm.claude_client import get_claude_client
from ..llm.prompts import get_agent_prompt, get_system_prompt


class LaTeXParserAgent:
    """Agent for parsing LaTeX resumes"""

    def __init__(self):
        self.client = get_claude_client()

    def parse_resume(self, state: AgentState) -> AgentState:
        """
        Parse the LaTeX resume and extract structured information.

        Args:
            state: Current agent state with resume_tex

        Returns:
            Updated state with parsed_resume and resume_sections
        """
        try:
            # Update workflow stage
            state["current_agent"] = "latex_parser"
            state["workflow_stage"] = "parsing"

            # Get the resume content
            resume_tex = state["resume_tex"]

            # Create prompt
            prompt = get_agent_prompt(
                "latex_parser",
                resume_tex=resume_tex
            )

            # Get system prompt
            system_prompt = get_system_prompt("latex_parser")

            # Call Claude to parse the resume
            response = self.client.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )

            # Extract parsed data
            contact_info = response.get("contact_info", {})
            sections_data = response.get("sections", [])
            all_keywords = response.get("all_keywords", [])

            # Convert to ResumeSection objects
            resume_sections: List[ResumeSection] = []
            for section in sections_data:
                resume_sections.append(ResumeSection(
                    section_name=section.get("section_name", "Unknown"),
                    content=section.get("content", ""),
                    keywords=section.get("keywords", [])
                ))

            # Update state
            state["parsed_resume"] = {
                "contact_info": contact_info,
                "all_keywords": all_keywords,
                "section_count": len(resume_sections)
            }
            state["resume_sections"] = resume_sections

            print(f"[OK] Parsed {len(resume_sections)} sections from resume")
            print(f"[OK] Extracted {len(all_keywords)} keywords")

            return state

        except Exception as e:
            error_msg = f"LaTeX Parser error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"[X] {error_msg}")
            return state


def parse_resume_node(state: AgentState) -> AgentState:
    """
    LangGraph node function for parsing resumes.

    Args:
        state: Current agent state

    Returns:
        Updated state
    """
    agent = LaTeXParserAgent()
    return agent.parse_resume(state)
