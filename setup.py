"""
Setup script for Resume Optimizer
"""

from setuptools import setup, find_packages

setup(
    name="resume-optimizer",
    version="0.1.0",
    description="AI-powered resume optimization for ATS compatibility",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "langgraph>=0.2.0",
        "anthropic>=0.18.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pylatexenc>=2.10",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "resume-optimizer=src.main:main",
        ],
    },
    python_requires=">=3.9",
)
