"""Benchmark runner — compares all 3 levels on an eval dataset.

Usage:
    python -m src.evaluation.benchmark --dataset examples/eval_dataset.jsonl
"""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from src.evaluation.metrics import estimate_cost, simple_correctness_check
from src.levels.level_1_prompt import run_level_1
from src.levels.level_2_rag import run_level_2
from src.levels.level_3_agents import run_level_3
from src.utils.config import config

app = typer.Typer()
console = Console()


@app.command()
def benchmark(
    dataset: Path = typer.Option(
        Path("examples/eval_dataset.jsonl"),
        "--dataset",
        "-d",
        help="JSONL file with {query, expected_keywords} entries",
    ),
    output: Path = typer.Option(
        Path("benchmark_results/results.json"),
        "--output",
        "-o",
    ),
):
    """Run all 3 levels against a dataset and compare."""
    console.print("[bold cyan]🏁 Running benchmark across all 3 levels[/bold cyan]\n")

    model = (
        config.bedrock_model_id
        if config.execution_mode == "bedrock"
        else config.anthropic_model
    )

    items = [json.loads(line) for line in dataset.read_text().splitlines() if line.strip()]
    results = {"level_1": [], "level_2": [], "level_3": []}

    for i, item in enumerate(items, 1):
        query = item["query"]
        expected = item.get("expected_keywords", [])
        console.print(f"[dim]({i}/{len(items)})[/dim] {query[:80]}")

        for level_num, runner, key in [
            (1, run_level_1, "level_1"),
            (2, run_level_2, "level_2"),
            (3, run_level_3, "level_3"),
        ]:
            try:
                out = runner(query)
                cost = estimate_cost(
                    model,
                    out.get("input_tokens", 0),
                    out.get("output_tokens", 0),
                )
                correct = (
                    simple_correctness_check(out["answer"], expected)
                    if expected
                    else None
                )
                results[key].append(
                    {
                        "query": query,
                        "latency_ms": out["latency_ms"],
                        "cost_usd": cost,
                        "correct": correct,
                    }
                )
            except Exception as e:
                console.print(f"[red]Level {level_num} failed: {e}[/red]")
                results[key].append({"query": query, "error": str(e)})

    # Summary
    console.print("\n[bold]Summary[/bold]")
    table = Table()
    table.add_column("Level")
    table.add_column("Accuracy", justify="right")
    table.add_column("Avg Latency", justify="right")
    table.add_column("Avg Cost/Query", justify="right")

    for key, label in [
        ("level_1", "Level 1 (Prompt)"),
        ("level_2", "Level 2 (RAG)"),
        ("level_3", "Level 3 (Agents)"),
    ]:
        runs = [r for r in results[key] if "error" not in r]
        if not runs:
            continue
        correct_count = sum(1 for r in runs if r.get("correct") is True)
        total_checked = sum(1 for r in runs if r.get("correct") is not None)
        acc = f"{100 * correct_count / total_checked:.0f}%" if total_checked else "N/A"
        avg_latency = sum(r["latency_ms"] for r in runs) / len(runs)
        avg_cost = sum(r["cost_usd"] for r in runs) / len(runs)
        table.add_row(label, acc, f"{avg_latency:.0f} ms", f"${avg_cost:.4f}")

    console.print(table)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2))
    console.print(f"\n[green]💾 Full results saved to {output}[/green]")


if __name__ == "__main__":
    app()
