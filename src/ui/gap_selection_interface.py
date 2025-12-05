"""
Gap Selection Interface

Interactive interface for users to review and select gaps to address.
"""

from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.markdown import Markdown
from ..graph.state import Gap


class GapSelectionInterface:
    """Interactive interface for gap selection"""

    def __init__(self):
        self.console = Console()

    def display_gaps(self, gaps: List[Gap]):
        """
        Display all gaps in a formatted table.

        Args:
            gaps: List of Gap objects
        """
        if not gaps:
            self.console.print("\n[yellow]No gaps identified.[/yellow]\n")
            return

        self.console.print(f"\n[bold cyan]Identified {len(gaps)} Gaps:[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=8)
        table.add_column("Severity", style="cyan", width=10)
        table.add_column("Type", style="yellow", width=20)
        table.add_column("Description", style="white")

        for i, gap in enumerate(gaps):
            gap_id = f"gap_{i}"
            severity_icon = self._get_severity_icon(gap['severity'])
            severity_style = self._get_severity_style(gap['severity'])

            table.add_row(
                gap_id,
                f"[{severity_style}]{severity_icon} {gap['severity'].upper()}[/{severity_style}]",
                gap['gap_type'],
                gap['description'][:50] + "..." if len(gap['description']) > 50 else gap['description']
            )

        self.console.print(table)
        self.console.print()

    def display_gap_details(self, gap: Gap, index: int):
        """
        Display detailed information about a single gap.

        Args:
            gap: Gap object
            index: Gap index
        """
        severity_icon = self._get_severity_icon(gap['severity'])

        details = f"""
**ID:** gap_{index}
**Severity:** {severity_icon} {gap['severity'].upper()}
**Type:** {gap['gap_type']}

**Description:**
{gap['description']}
"""
        if gap.get('related_requirement'):
            details += f"\n**Related Requirement:**\n{gap['related_requirement']}"

        panel = Panel(
            Markdown(details),
            title=f"Gap Details",
            border_style=self._get_severity_style(gap['severity'])
        )

        self.console.print("\n")
        self.console.print(panel)
        self.console.print("\n")

    def select_gaps(self, gaps: List[Gap],
                   auto_severity: str = None) -> List[str]:
        """
        Interactive selection of gaps.

        Args:
            gaps: List of Gap objects
            auto_severity: Automatically select gaps with this severity or higher

        Returns:
            List of selected gap IDs ("gap_0", "gap_1", etc.)
        """
        if not gaps:
            return []

        selected_ids = []

        # Display all gaps
        self.display_gaps(gaps)

        # Count by severity
        high_count = sum(1 for g in gaps if g['severity'].lower() == 'high')
        medium_count = sum(1 for g in gaps if g['severity'].lower() == 'medium')
        low_count = sum(1 for g in gaps if g['severity'].lower() == 'low')

        self.console.print(f"[bold]Gap Summary:[/bold] {high_count} HIGH, {medium_count} MEDIUM, {low_count} LOW\n")

        # Ask user what they want to do
        self.console.print("[bold]Selection Options:[/bold]")
        self.console.print("  1. Address all gaps")
        self.console.print("  2. Review and select individually")
        self.console.print("  3. Auto-select by severity")
        self.console.print("  4. Skip all (generate no recommendations)")

        choice = Prompt.ask("\nChoose an option", choices=["1", "2", "3", "4"], default="2")

        if choice == "1":
            # Accept all
            selected_ids = [f"gap_{i}" for i in range(len(gaps))]
            self.console.print(f"\n[green]✓ Selected all {len(selected_ids)} gaps[/green]\n")

        elif choice == "2":
            # Review individually
            selected_ids = self._review_individually(gaps)

        elif choice == "3":
            # Auto-select by severity
            self.console.print("\n[bold]Select gaps to address:[/bold]")
            self.console.print("  1. HIGH severity only")
            self.console.print("  2. HIGH + MEDIUM severity")
            self.console.print("  3. All severities (HIGH + MEDIUM + LOW)")

            severity_choice = Prompt.ask("Choose severity threshold", choices=["1", "2", "3"], default="2")

            if severity_choice == "1":
                selected_severities = ['high']
            elif severity_choice == "2":
                selected_severities = ['high', 'medium']
            else:
                selected_severities = ['high', 'medium', 'low']

            selected_ids = [
                f"gap_{i}"
                for i, gap in enumerate(gaps)
                if gap['severity'].lower() in selected_severities
            ]
            self.console.print(f"\n[green]✓ Selected {len(selected_ids)} gaps ({', '.join(s.upper() for s in selected_severities)} severity)[/green]\n")

        elif choice == "4":
            # Skip all
            self.console.print("\n[yellow]✗ Skipped all gaps (no recommendations will be generated)[/yellow]\n")
            selected_ids = []

        return selected_ids

    def _review_individually(self, gaps: List[Gap]) -> List[str]:
        """
        Review each gap individually.

        Args:
            gaps: List of Gap objects

        Returns:
            List of selected gap IDs
        """
        selected_ids = []

        for i, gap in enumerate(gaps):
            self.console.print(f"\n[bold cyan]--- Gap {i+1}/{len(gaps)} ---[/bold cyan]")
            self.display_gap_details(gap, i)

            if Confirm.ask("Address this gap?", default=True):
                selected_ids.append(f"gap_{i}")
                self.console.print("[green]✓ Will address[/green]")
            else:
                self.console.print("[yellow]✗ Skipped[/yellow]")

        self.console.print(f"\n[bold green]Selected {len(selected_ids)}/{len(gaps)} gaps[/bold green]\n")
        return selected_ids

    def _get_severity_style(self, severity: str) -> str:
        """Get color style for severity level."""
        severity_lower = severity.lower()
        if severity_lower == "high":
            return "bold red"
        elif severity_lower == "medium":
            return "bold yellow"
        elif severity_lower == "low":
            return "cyan"
        else:
            return "dim"

    def _get_severity_icon(self, severity: str) -> str:
        """Get icon for severity level."""
        severity_lower = severity.lower()
        if severity_lower == "high":
            return "🔴"
        elif severity_lower == "medium":
            return "🟡"
        elif severity_lower == "low":
            return "🔵"
        else:
            return "⚪"


def interactive_gap_selection(gaps: List[Gap],
                              auto_severity: str = None) -> List[str]:
    """
    Main function for interactive gap selection.

    Args:
        gaps: List of Gap objects
        auto_severity: Auto-select gaps with this severity or higher

    Returns:
        List of selected gap IDs
    """
    interface = GapSelectionInterface()
    return interface.select_gaps(gaps, auto_severity)
