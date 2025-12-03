"""
Diff Viewer

Displays side-by-side comparison of original and modified LaTeX resumes.
"""

import difflib
from typing import List, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.layout import Layout
from rich.text import Text


class DiffViewer:
    """Displays diff between original and modified LaTeX"""

    def __init__(self):
        self.console = Console()

    def show_diff(self, original: str, modified: str, context_lines: int = 3):
        """
        Show side-by-side diff of LaTeX files.

        Args:
            original: Original LaTeX content
            modified: Modified LaTeX content
            context_lines: Number of context lines to show around changes
        """
        # Split into lines
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)

        # Generate unified diff
        diff = list(difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile='Original Resume',
            tofile='Optimized Resume',
            lineterm='',
            n=context_lines
        ))

        if not diff or len(diff) <= 2:  # No changes
            self.console.print("\n[yellow]No changes detected between original and modified resume.[/yellow]\n")
            return

        # Display diff
        self.console.print("\n[bold cyan]LaTeX Resume Diff[/bold cyan]")
        self.console.print("=" * 80)

        for line in diff:
            if line.startswith('---') or line.startswith('+++'):
                self.console.print(f"[bold]{line}[/bold]")
            elif line.startswith('@@'):
                self.console.print(f"[blue]{line}[/blue]")
            elif line.startswith('-'):
                self.console.print(f"[red]{line}[/red]")
            elif line.startswith('+'):
                self.console.print(f"[green]{line}[/green]")
            else:
                self.console.print(line)

        self.console.print("=" * 80 + "\n")

    def show_side_by_side(self, original: str, modified: str, max_width: int = 80):
        """
        Show side-by-side comparison of original and modified LaTeX.

        Args:
            original: Original LaTeX content
            modified: Modified LaTeX content
            max_width: Maximum width for each panel
        """
        layout = Layout()
        layout.split_row(
            Layout(name="original"),
            Layout(name="modified")
        )

        # Create syntax-highlighted panels
        original_syntax = Syntax(original, "latex", theme="monokai", line_numbers=True)
        modified_syntax = Syntax(modified, "latex", theme="monokai", line_numbers=True)

        layout["original"].update(Panel(original_syntax, title="Original Resume", border_style="red"))
        layout["modified"].update(Panel(modified_syntax, title="Optimized Resume", border_style="green"))

        self.console.print("\n")
        self.console.print(layout)
        self.console.print("\n")

    def show_changes_summary(self, applied_changes: List[dict]):
        """
        Show summary of applied changes.

        Args:
            applied_changes: List of change dictionaries
        """
        if not applied_changes:
            self.console.print("\n[yellow]No changes were applied.[/yellow]\n")
            return

        self.console.print(f"\n[bold green]Applied {len(applied_changes)} Changes:[/bold green]\n")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Section", style="magenta")
        table.add_column("Change Description", style="white")

        for i, change in enumerate(applied_changes, 1):
            section = change.get("section_modified", "Unknown")
            description = change.get("change_description", "No description")
            table.add_row(str(i), section, description)

        self.console.print(table)
        self.console.print()

    def show_stats(self, similarity_score: float, gaps_count: int,
                   recommendations_count: int, changes_count: int):
        """
        Show optimization statistics.

        Args:
            similarity_score: Similarity score (0-100)
            gaps_count: Number of gaps identified
            recommendations_count: Number of recommendations generated
            changes_count: Number of changes applied
        """
        # Create stats panel
        stats_text = Text()
        stats_text.append("Similarity Score: ", style="bold")

        # Color code the score
        if similarity_score >= 80:
            score_style = "bold green"
        elif similarity_score >= 60:
            score_style = "bold yellow"
        else:
            score_style = "bold red"

        stats_text.append(f"{similarity_score:.1f}/100\n", style=score_style)
        stats_text.append(f"Gaps Identified: ", style="bold")
        stats_text.append(f"{gaps_count}\n", style="cyan")
        stats_text.append(f"Recommendations: ", style="bold")
        stats_text.append(f"{recommendations_count}\n", style="cyan")
        stats_text.append(f"Changes Applied: ", style="bold")
        stats_text.append(f"{changes_count}\n", style="green")

        panel = Panel(stats_text, title="Optimization Statistics", border_style="blue")
        self.console.print("\n")
        self.console.print(panel)
        self.console.print("\n")


def display_diff(original: str, modified: str, applied_changes: List[dict] = None,
                 similarity_score: float = None, gaps_count: int = None,
                 recommendations_count: int = None):
    """
    Main function to display all diff information.

    Args:
        original: Original LaTeX content
        modified: Modified LaTeX content
        applied_changes: List of applied changes
        similarity_score: Similarity score
        gaps_count: Number of gaps
        recommendations_count: Number of recommendations
    """
    viewer = DiffViewer()

    # Show stats if provided
    if similarity_score is not None:
        changes_count = len(applied_changes) if applied_changes else 0
        viewer.show_stats(
            similarity_score=similarity_score,
            gaps_count=gaps_count or 0,
            recommendations_count=recommendations_count or 0,
            changes_count=changes_count
        )

    # Show changes summary
    if applied_changes:
        viewer.show_changes_summary(applied_changes)

    # Show diff
    viewer.show_diff(original, modified)
