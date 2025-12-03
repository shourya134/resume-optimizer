"""
Selection Interface

Interactive interface for users to review and select recommendations.
"""

from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.markdown import Markdown
from ..graph.state import Recommendation


class SelectionInterface:
    """Interactive interface for recommendation selection"""

    def __init__(self):
        self.console = Console()

    def display_recommendations(self, recommendations: List[Recommendation]):
        """
        Display all recommendations in a formatted table.

        Args:
            recommendations: List of Recommendation objects
        """
        if not recommendations:
            self.console.print("\n[yellow]No recommendations generated.[/yellow]\n")
            return

        self.console.print(f"\n[bold cyan]Generated {len(recommendations)} Recommendations:[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=8)
        table.add_column("Priority", style="cyan", width=8)
        table.add_column("Category", style="yellow", width=15)
        table.add_column("Description", style="white")

        for rec in recommendations:
            priority_str = f"P{rec['priority']}"
            priority_style = self._get_priority_style(rec['priority'])

            table.add_row(
                rec['recommendation_id'],
                f"[{priority_style}]{priority_str}[/{priority_style}]",
                rec['category'],
                rec['description'][:60] + "..." if len(rec['description']) > 60 else rec['description']
            )

        self.console.print(table)
        self.console.print()

    def display_recommendation_details(self, recommendation: Recommendation):
        """
        Display detailed information about a single recommendation.

        Args:
            recommendation: Recommendation object
        """
        details = f"""
**ID:** {recommendation['recommendation_id']}
**Priority:** {recommendation['priority']} ({self._get_priority_label(recommendation['priority'])})
**Category:** {recommendation['category']}

**Description:**
{recommendation['description']}

**Specific Action:**
{recommendation['specific_action']}

**Rationale:**
{recommendation['rationale']}
"""
        if recommendation.get('latex_modification'):
            details += f"\n**LaTeX Modification:**\n```latex\n{recommendation['latex_modification']}\n```"

        panel = Panel(
            Markdown(details),
            title=f"Recommendation Details",
            border_style=self._get_priority_style(recommendation['priority'])
        )

        self.console.print("\n")
        self.console.print(panel)
        self.console.print("\n")

    def select_recommendations(self, recommendations: List[Recommendation],
                              auto_select_priority: int = None) -> List[str]:
        """
        Interactive selection of recommendations.

        Args:
            recommendations: List of Recommendation objects
            auto_select_priority: Automatically select recommendations with this priority or higher

        Returns:
            List of selected recommendation IDs
        """
        if not recommendations:
            return []

        selected_ids = []

        # Auto-select high priority if specified
        if auto_select_priority:
            selected_ids = [
                r['recommendation_id']
                for r in recommendations
                if r['priority'] <= auto_select_priority
            ]
            self.console.print(f"\n[green]Auto-selected {len(selected_ids)} high-priority recommendations (P{auto_select_priority} and above)[/green]\n")

        # Display all recommendations
        self.display_recommendations(recommendations)

        # Ask user what they want to do
        self.console.print("[bold]Selection Options:[/bold]")
        self.console.print("  1. Accept all recommendations")
        self.console.print("  2. Review and select individually")
        self.console.print("  3. Auto-select by priority")
        self.console.print("  4. Skip all (no changes)")

        choice = Prompt.ask("\nChoose an option", choices=["1", "2", "3", "4"], default="2")

        if choice == "1":
            # Accept all
            selected_ids = [r['recommendation_id'] for r in recommendations]
            self.console.print(f"\n[green]✓ Selected all {len(selected_ids)} recommendations[/green]\n")

        elif choice == "2":
            # Review individually
            selected_ids = self._review_individually(recommendations)

        elif choice == "3":
            # Auto-select by priority
            max_priority = Prompt.ask(
                "Select recommendations with priority",
                choices=["1", "2", "3"],
                default="2"
            )
            selected_ids = [
                r['recommendation_id']
                for r in recommendations
                if r['priority'] <= int(max_priority)
            ]
            self.console.print(f"\n[green]✓ Selected {len(selected_ids)} recommendations[/green]\n")

        elif choice == "4":
            # Skip all
            self.console.print("\n[yellow]✗ Skipped all recommendations[/yellow]\n")
            selected_ids = []

        return selected_ids

    def _review_individually(self, recommendations: List[Recommendation]) -> List[str]:
        """
        Review each recommendation individually.

        Args:
            recommendations: List of Recommendation objects

        Returns:
            List of selected recommendation IDs
        """
        selected_ids = []

        for i, rec in enumerate(recommendations, 1):
            self.console.print(f"\n[bold cyan]--- Recommendation {i}/{len(recommendations)} ---[/bold cyan]")
            self.display_recommendation_details(rec)

            if Confirm.ask("Apply this recommendation?", default=True):
                selected_ids.append(rec['recommendation_id'])
                self.console.print("[green]✓ Accepted[/green]")
            else:
                self.console.print("[yellow]✗ Skipped[/yellow]")

        self.console.print(f"\n[bold green]Selected {len(selected_ids)}/{len(recommendations)} recommendations[/bold green]\n")
        return selected_ids

    def _get_priority_style(self, priority: int) -> str:
        """Get color style for priority level."""
        if priority == 1:
            return "bold red"
        elif priority == 2:
            return "bold yellow"
        elif priority == 3:
            return "cyan"
        else:
            return "dim"

    def _get_priority_label(self, priority: int) -> str:
        """Get label for priority level."""
        labels = {
            1: "Critical",
            2: "Important",
            3: "Suggested",
            4: "Optional",
            5: "Minor"
        }
        return labels.get(priority, "Unknown")


def interactive_selection(recommendations: List[Recommendation],
                         auto_priority: int = None) -> List[str]:
    """
    Main function for interactive recommendation selection.

    Args:
        recommendations: List of Recommendation objects
        auto_priority: Auto-select recommendations with this priority or higher

    Returns:
        List of selected recommendation IDs
    """
    interface = SelectionInterface()
    return interface.select_recommendations(recommendations, auto_priority)
