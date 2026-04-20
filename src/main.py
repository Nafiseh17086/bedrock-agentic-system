"""CLI entry point.

Usage:
    python -m src.main --level 1 --query "Your question"
    python -m src.main --level 2 --query "..."
    python -m src.main --level 3 --query "..."
"""

import json

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src.levels.level_1_prompt import run_level_1
from src.levels.level_2_rag import run_level_2
from src.levels.level_3_agents import run_level_3
from src.utils.config import config

app = typer.Typer(help="Bedrock Agentic AI System")
console = Console()


@app.command()
def run(
    query: str = typer.Option(..., "--query", "-q"),
    level: int = typer.Option(3, "--level", "-l", help="1=prompt, 2=RAG, 3=agents"),
):
    """Run a query at the specified evolution level."""
    config.validate()

    console.print(
        Panel.fit(
            f"[bold cyan]🛡️ Bedrock Agentic System[/bold cyan]\n"
            f"[dim]Mode: {config.execution_mode} | Level: {level}[/dim]\n\n"
            f"[white]{query}[/white]",
            border_style="cyan",
        )
    )

    runners = {1: run_level_1, 2: run_level_2, 3: run_level_3}
    if level not in runners:
        console.print(f"[red]Invalid level: {level}. Use 1, 2, or 3.[/red]")
        raise typer.Exit(1)

    result = runners[level](query)

    console.print("\n")
    console.print(Panel(Markdown(result["answer"]), title="📋 Response"))
    console.print(
        f"\n[dim]Latency: {result['latency_ms']} ms | "
        f"Approach: {result['approach']}[/dim]\n"
    )

    if level == 3 and "routing" in result:
        console.print(f"[dim]Routing: {json.dumps(result['routing'], indent=2)}[/dim]")


if __name__ == "__main__":
    app()
