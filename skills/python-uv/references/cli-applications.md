---
title: CLI Applications
description: Building CLI applications with typer, commands, arguments, options, and rich output
tags: [typer, click, cli, commands, arguments, options, rich]
---

# CLI Applications

## Setup

```bash
uv add typer
uv add --dev pytest
```

## Basic CLI

```python
import typer

app = typer.Typer()


@app.command()
def hello(name: str) -> None:
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
```

```bash
uv run python cli.py Alice
```

## Commands and Subcommands

```python
import typer

app = typer.Typer(help="User management CLI")
users_app = typer.Typer(help="User operations")
app.add_typer(users_app, name="users")


@users_app.command("list")
def list_users(
    limit: int = typer.Option(10, help="Max users to display"),
    active: bool = typer.Option(True, help="Only show active users"),
) -> None:
    typer.echo(f"Listing {limit} users (active={active})")


@users_app.command("create")
def create_user(
    name: str = typer.Argument(help="User's full name"),
    email: str = typer.Option(..., help="User's email"),
    admin: bool = typer.Option(False, "--admin", help="Grant admin role"),
) -> None:
    typer.echo(f"Created user: {name} ({email}) admin={admin}")


@app.command()
def version() -> None:
    typer.echo("v1.0.0")
```

```bash
uv run python cli.py users list --limit 5
uv run python cli.py users create "Alice" --email alice@example.com --admin
uv run python cli.py version
```

## Arguments and Options

```python
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer


class OutputFormat(str, Enum):
    json = "json"
    table = "table"
    csv = "csv"


@app.command()
def export(
    path: Annotated[Path, typer.Argument(help="Output file path")],
    format: Annotated[OutputFormat, typer.Option(help="Output format")] = OutputFormat.json,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
    tags: Annotated[Optional[list[str]], typer.Option("--tag", "-t")] = None,
) -> None:
    if verbose:
        typer.echo(f"Exporting to {path} as {format.value}")
    if tags:
        typer.echo(f"Tags: {', '.join(tags)}")
```

## Rich Output

```python
import typer
from rich.console import Console
from rich.table import Table

console = Console()


@app.command()
def status() -> None:
    table = Table(title="Service Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Uptime")

    table.add_row("API", "Running", "3d 14h")
    table.add_row("Worker", "Running", "3d 14h")
    table.add_row("Database", "Running", "30d 2h")

    console.print(table)
```

## Progress Bars

```python
import time

import typer


@app.command()
def process(items: int = 100) -> None:
    with typer.progressbar(range(items), label="Processing") as progress:
        for _item in progress:
            time.sleep(0.01)
    typer.echo("Done!")
```

## Error Handling

```python
@app.command()
def deploy(environment: str) -> None:
    if environment not in ("staging", "production"):
        typer.echo(f"Unknown environment: {environment}", err=True)
        raise typer.Exit(code=1)

    if environment == "production":
        confirmed = typer.confirm("Deploy to production?")
        if not confirmed:
            raise typer.Abort()

    typer.echo(f"Deploying to {environment}")
```

## Entry Point Configuration

```toml
[project.scripts]
my-cli = "my_app.cli:app"
```

```bash
uv run my-cli users list
uv run my-cli --help
```

## Testing CLI

```python
from typer.testing import CliRunner

from my_app.cli import app

runner = CliRunner()


def test_hello():
    result = runner.invoke(app, ["hello", "Alice"])
    assert result.exit_code == 0
    assert "Hello Alice" in result.output


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "v1.0.0" in result.output
```

## Click Alternative

```python
import click


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("name")
@click.option("--count", default=1, help="Number of greetings")
def hello(name: str, count: int) -> None:
    for _ in range(count):
        click.echo(f"Hello, {name}!")


if __name__ == "__main__":
    cli()
```
