"""
LangGraph State Schema for Resume Optimizer

This module defines the state structure that flows through the multi-agent workflow.
Each agent reads from and writes to this shared state.
"""

from typing import TypedDict, Optional, List, Dict, Any
from typing_extensions import Annotated
import operator


class ResumeSection(TypedDict):
    """Structured representation of a resume section"""
    section_name: str
    content: str
    keywords: List[str]


class JobRequirement(TypedDict):
    """Structured representation of a job requirement"""
    category: str  # e.g., "technical_skills", "experience", "education", "soft_skills"
    requirement: str
    priority: str  # "required" or "preferred"
    keywords: List[str]


class Gap(TypedDict):
    """Identified gap between resume and job requirements"""
    gap_type: str  # "missing_keyword", "missing_skill", "missing_experience", "formatting"
    description: str
    severity: str  # "high", "medium", "low"
    related_requirement: Optional[str]


class Recommendation(TypedDict):
    """Actionable recommendation for resume improvement"""
    recommendation_id: str
    priority: int  # 1 (highest) to 5 (lowest)
    category: str
    description: str
    specific_action: str
    rationale: str
    latex_modification: Optional[str]  # Specific LaTeX change to make


class AgentState(TypedDict):
    """
    Complete state for the resume optimization workflow.

    This state is shared across all agents and modified as it flows through the graph.
    """

    # Input data
    resume_tex: str  # Original LaTeX resume content
    job_description: str  # Job description text
    resume_file_path: Optional[str]  # Path to the resume file
    job_file_path: Optional[str]  # Path to the job description file

    # Parsed data from LaTeX Parser Agent
    parsed_resume: Optional[Dict[str, Any]]  # Structured resume data
    resume_sections: Optional[List[ResumeSection]]  # Individual sections

    # Analysis from Job Analyzer Agent
    job_requirements: Optional[List[JobRequirement]]  # Extracted requirements
    job_keywords: Optional[List[str]]  # Key terms from job description
    job_title: Optional[str]
    company_name: Optional[str]

    # Analysis from Gap Analyzer Agent
    similarity_score: Optional[float]  # Overall match score (0-100)
    keyword_overlap: Optional[float]  # Keyword match percentage
    identified_gaps: Annotated[List[Gap], operator.add]  # Gaps found (appendable)

    # Output from Recommendation Generator Agent
    recommendations: Annotated[List[Recommendation], operator.add]  # Generated recommendations

    # Output from LaTeX Editor Agent
    modified_resume_tex: Optional[str]  # Optimized LaTeX content
    applied_changes: Optional[List[str]]  # List of changes that were applied

    # Workflow control
    current_agent: Optional[str]  # Name of the currently executing agent
    workflow_stage: str  # "parsing", "analyzing", "generating", "editing", "complete"
    errors: Annotated[List[str], operator.add]  # Any errors encountered (appendable)

    # User selections (for interactive mode)
    user_accepted_recommendations: Optional[List[str]]  # IDs of accepted recommendations
    user_rejected_recommendations: Optional[List[str]]  # IDs of rejected recommendations


def create_initial_state(resume_tex: str, job_description: str,
                         resume_path: Optional[str] = None,
                         job_path: Optional[str] = None) -> AgentState:
    """
    Create the initial state for the workflow.

    Args:
        resume_tex: The LaTeX resume content
        job_description: The job description text
        resume_path: Optional path to the resume file
        job_path: Optional path to the job description file

    Returns:
        Initial AgentState with inputs populated
    """
    return AgentState(
        resume_tex=resume_tex,
        job_description=job_description,
        resume_file_path=resume_path,
        job_file_path=job_path,
        parsed_resume=None,
        resume_sections=None,
        job_requirements=None,
        job_keywords=None,
        job_title=None,
        company_name=None,
        similarity_score=None,
        keyword_overlap=None,
        identified_gaps=[],
        recommendations=[],
        modified_resume_tex=None,
        applied_changes=None,
        current_agent=None,
        workflow_stage="parsing",
        errors=[],
        user_accepted_recommendations=None,
        user_rejected_recommendations=None,
    )
