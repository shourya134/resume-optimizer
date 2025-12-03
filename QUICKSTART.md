# Quick Start Guide

## Setup (5 minutes)

### 1. Create Virtual Environment

```bash
cd C:\Users\shour\resume-optimizer
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (Git Bash):**
```bash
source venv/Scripts/activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

Copy the example environment file:
```bash
copy .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 5. Verify Installation

```bash
python -m src.main version
```

## Basic Usage

### Optimize Your Resume

```bash
python -m src.main optimize --resume path/to/your_resume.tex --job path/to/job_description.txt
```

This will:
1. Analyze your resume against the job description
2. Calculate a similarity score
3. Identify gaps and missing keywords
4. Generate prioritized recommendations
5. Let you interactively select which recommendations to apply
6. Create an optimized resume file (`your_resume_optimized.tex`)

### Analysis Only (No Changes)

```bash
python -m src.main analyze --resume your_resume.tex --job job_description.txt
```

This shows recommendations without modifying your resume.

### Auto-Apply High Priority Recommendations

```bash
python -m src.main optimize --resume your_resume.tex --job job_description.txt --auto-priority 2
```

This automatically applies all Priority 1 and 2 recommendations without prompting.

### Skip Interactive Mode

```bash
python -m src.main optimize --resume your_resume.tex --job job_description.txt --auto
```

## Input File Requirements

### Resume File
- Must be a `.tex` (LaTeX) file
- Should contain standard resume sections (experience, education, skills, etc.)

### Job Description File
- Can be a `.txt` file
- Paste the complete job description from the job posting

## Output

The tool generates:
- **Optimized Resume**: `your_resume_optimized.tex` (or custom path with `--output`)
- **Terminal Output**:
  - Similarity score (0-100)
  - Identified gaps
  - Recommendations with priorities
  - Side-by-side diff view
  - Summary of applied changes

## Tips

1. **Keep originals**: The tool never modifies your original resume file
2. **Review changes**: Use interactive mode to review each recommendation
3. **Multiple iterations**: Run the tool multiple times for different jobs
4. **Check compilation**: Always compile the optimized LaTeX file to verify it works

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure you created the `.env` file
- Verify your API key is correct

**"File not found"**
- Use absolute paths or ensure you're in the correct directory
- Check file extensions (.tex for resume, .txt for job description)

**LaTeX compilation errors**
- The tool preserves LaTeX structure, but always verify output compiles
- If errors occur, review the changes in the diff view
