# Resume Optimizer

An AI-powered resume optimization agent that analyzes your LaTeX resume against job descriptions and provides tailored recommendations.

## Features

- **ATS-Style Scanning**: Analyzes your resume like an Applicant Tracking System
- **Semantic Similarity Analysis**: Matches your resume content with job requirements
- **Gap Identification**: Identifies missing keywords, skills, and experiences
- **Intelligent Recommendations**: Provides prioritized, actionable suggestions
- **LaTeX Support**: Direct manipulation of .tex files with side-by-side diff view
- **Multi-Agent Architecture**: Modular LangGraph-based system with specialized agents

## Architecture

The system uses a LangGraph multi-agent architecture with 6 specialized agents:

1. **Supervisor Agent**: Orchestrates workflow and manages state
2. **LaTeX Parser Agent**: Extracts structured data from .tex files
3. **Job Analyzer Agent**: Extracts requirements and keywords from job descriptions
4. **Gap Analyzer Agent**: Calculates similarity scores and identifies gaps
5. **Recommendation Generator Agent**: Creates prioritized improvement suggestions
6. **LaTeX Editor Agent**: Applies recommendations to generate optimized resume

## Installation

1. Navigate to the project:
```bash
cd C:\Users\shour\resume-optimizer
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# OR: venv\Scripts\activate   # Windows CMD
# OR: source venv/bin/activate # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

5. Ensure pdflatex is installed (for local compilation):
```bash
pdflatex --version
```

## Usage

```bash
python src/main.py optimize --resume path/to/resume.tex --job path/to/job_description.txt
```

## Project Structure

```
resume-optimizer/
├── src/
│   ├── main.py                    # CLI entry point
│   ├── agents/                    # Agent implementations
│   ├── graph/                     # LangGraph workflow
│   ├── llm/                       # Claude API client and prompts
│   ├── latex/                     # LaTeX parsing and compilation
│   ├── ui/                        # CLI and diff viewer
│   └── utils/                     # Utilities
├── tests/                         # Test suite
└── config/                        # Configuration files
```

## Future Enhancements

- Overleaf API integration for cloud compilation
- Web-based interface
- Support for multiple resume formats
- Industry-specific optimization profiles
