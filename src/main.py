"""
Resume Optimizer CLI

Main entry point for the resume optimization tool.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console

from .graph.workflow import run_workflow, run_workflow_with_user_selection
from .ui.diff_viewer import display_diff
from .ui.selection_interface import interactive_selection

app = typer.Typer(help="AI-powered resume optimizer for ATS compatibility")
console = Console()


@app.command()
def optimize(
    resume: Path = typer.Option(
        ...,
        "--resume", "-r",
        help="Path to LaTeX resume file (.tex)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    job: Path = typer.Option(
        ...,
        "--job", "-j",
        help="Path to job description file (.txt)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Path for optimized resume output (default: resume_optimized.tex)",
        file_okay=True,
        dir_okay=False,
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--auto",
        help="Interactive mode for selecting recommendations",
    ),
    auto_priority: Optional[int] = typer.Option(
        None,
        "--auto-priority",
        help="Auto-apply recommendations up to this priority (1-5, 1=highest)",
        min=1,
        max=5,
    ),
    gap_selection: bool = typer.Option(
        True,
        "--gap-selection/--no-gap-selection",
        help="Interactive gap selection before generating recommendations",
    ),
    auto_gap_severity: Optional[str] = typer.Option(
        None,
        "--auto-gap-severity",
        help="Auto-select gaps by severity (high, medium, low)",
    ),
    show_diff: bool = typer.Option(
        True,
        "--show-diff/--no-diff",
        help="Show diff between original and optimized resume",
    ),
):
    """
    Optimize a LaTeX resume for a specific job description.

    This command analyzes your resume against a job description, identifies gaps,
    and provides recommendations to improve ATS compatibility and match rate.
    """
    try:
        # Read input files with encoding fallback
        console.print(f"\n[cyan]Reading resume from:[/cyan] {resume}")
        try:
            resume_tex = resume.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            resume_tex = resume.read_text(encoding='cp1252')

        console.print(f"[cyan]Reading job description from:[/cyan] {job}")
        try:
            job_description = job.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            job_description = job.read_text(encoding='cp1252')

        # Run workflow
        console.print("\n[cyan]Running optimization workflow...[/cyan]\n")

        # Phase 1: Run analysis and generate recommendations
        state = run_workflow(
            resume_tex=resume_tex,
            job_description=job_description,
            resume_path=str(resume),
            job_path=str(job),
            interactive_gap_selection=gap_selection and interactive,
            auto_select_gap_severity=auto_gap_severity or ""
        )

        # Check for errors
        if state.get("errors"):
            console.print("\n[red]Workflow completed with errors:[/red]")
            for error in state["errors"]:
                console.print(f"  - {error}")

        # Get results
        recommendations = state.get("recommendations", [])
        similarity_score = state.get("similarity_score", 0)
        gaps = state.get("identified_gaps", [])
        selected_gaps = state.get("user_selected_gaps")

        # Phase 2: Interactive selection (if enabled)
        if interactive and recommendations:
            selected_ids = interactive_selection(recommendations, auto_priority)

            if selected_ids:
                # Apply selected recommendations using minimal workflow
                console.print("\n[cyan]Applying selected recommendations...[/cyan]\n")

                state = run_workflow_with_user_selection(
                    resume_tex=resume_tex,
                    job_description=job_description,
                    accepted_recommendation_ids=selected_ids,
                    resume_path=str(resume),
                    job_path=str(job),
                    previous_state=state  # Pass state from phase 1 to avoid re-analysis
                )
        elif auto_priority and recommendations:
            # Auto-select by priority
            selected_ids = [
                r['recommendation_id']
                for r in recommendations
                if r['priority'] <= auto_priority
            ]
            console.print(f"\n[cyan]Auto-applying {len(selected_ids)} recommendations (priority ≤ {auto_priority})...[/cyan]\n")

        # Get modified resume
        modified_resume = state.get("modified_resume_tex")
        applied_changes = state.get("applied_changes", [])

        # Display results
        if show_diff and modified_resume:
            display_diff(
                original=resume_tex,
                modified=modified_resume,
                applied_changes=applied_changes or [],
                similarity_score=similarity_score or 0.0,
                gaps_count=len(gaps) if gaps else 0,
                recommendations_count=len(recommendations) if recommendations else 0
            )

        # Save output
        if modified_resume:
            if output is None:
                output = resume.parent / f"{resume.stem}_optimized.tex"

            output.write_text(modified_resume, encoding='utf-8')
            console.print(f"\n[green]✓ Optimized resume saved to:[/green] {output}")
        else:
            console.print("\n[yellow][WARNING] No modifications were made to the resume.[/yellow]")

        # Print summary
        console.print(f"\n[bold]Final Results:[/bold]")
        console.print(f"  Similarity Score: {similarity_score:.1f}/100")
        console.print(f"  Gaps Identified: {len(gaps) if gaps else 0}")
        if selected_gaps is not None:
            console.print(f"  Gaps Selected: {len(selected_gaps) if selected_gaps else 0}")
        console.print(f"  Recommendations Generated: {len(recommendations) if recommendations else 0}")
        console.print(f"  Changes Applied: {len(applied_changes) if applied_changes else 0}\n")

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}\n")
        raise typer.Exit(code=1)


@app.command()
def analyze(
    resume: Path = typer.Option(
        ...,
        "--resume", "-r",
        help="Path to LaTeX resume file (.tex)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    job: Path = typer.Option(
        ...,
        "--job", "-j",
        help="Path to job description file (.txt)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
):
    """
    Analyze resume against job description without making modifications.

    This command only performs analysis and shows recommendations,
    without applying any changes to the resume.
    """
    try:
        # Read input files with encoding fallback
        console.print(f"\n[cyan]Reading resume from:[/cyan] {resume}")
        try:
            resume_tex = resume.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            resume_tex = resume.read_text(encoding='cp1252')

        console.print(f"[cyan]Reading job description from:[/cyan] {job}")
        try:
            job_description = job.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            job_description = job.read_text(encoding='cp1252')

        # Run workflow without applying edits
        console.print("\n[cyan]Running analysis...[/cyan]\n")

        state = run_workflow(
            resume_tex=resume_tex,
            job_description=job_description,
            resume_path=str(resume),
            job_path=str(job)
        )

        # Display results (analysis only, no modifications)
        recommendations = state.get("recommendations", [])
        similarity_score = state.get("similarity_score", 0)
        gaps = state.get("identified_gaps", [])

        # Display recommendations
        from .ui.selection_interface import SelectionInterface
        interface = SelectionInterface()
        interface.display_recommendations(recommendations)

        # Print summary
        console.print(f"\n[bold]Analysis Results:[/bold]")
        console.print(f"  Similarity Score: {similarity_score:.1f}/100")
        console.print(f"  Gaps Identified: {len(gaps) if gaps else 0}")
        console.print(f"  Recommendations: {len(recommendations) if recommendations else 0}\n")

        console.print("[dim]Use 'optimize' command to apply recommendations.[/dim]\n")

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}\n")
        raise typer.Exit(code=1)


@app.command()
def version():
    """Show version information."""
    console.print("\n[bold]Resume Optimizer[/bold] v0.1.0")
    console.print("AI-powered resume optimization for ATS compatibility\n")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
