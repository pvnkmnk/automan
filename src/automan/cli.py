# src/automan/cli.py
"""Command-line interface for automan."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

from automan import __version__
from automan.enricher import enrich
from automan.normalizer import normalize
from automan.parser import parse
from automan.probe import probe
from automan.render import render_manpage, render_markdown


@click.group()
@click.version_option(__version__, prog_name="automan")
def cli() -> None:
    """automan — auto-generate manpages and docs from CLI help output."""


@cli.command("gen")
@click.argument("command")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["man", "md", "markdown"], case_sensitive=False),
    default="man",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Write output to FILE instead of stdout.",
)
@click.option(
    "--section",
    "-s",
    default="1",
    show_default=True,
    help="Man-page section number (only used with --format man).",
)
@click.option(
    "--no-enrich",
    is_flag=True,
    default=False,
    help="Skip the enrichment pass (faster, but may miss version/see-also).",
)
def gen(
    command: str,
    fmt: str,
    output: Optional[str],
    section: str,
    no_enrich: bool,
) -> None:
    """Generate documentation for COMMAND."""
    try:
        raw = probe(command)
    except RuntimeError as exc:
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)

    doc = parse(raw)
    doc = normalize(doc)
    if not no_enrich:
        doc = enrich(doc)

    if fmt == "man":
        result = render_manpage(doc, section=section)
    else:
        result = render_markdown(doc)

    if output:
        Path(output).write_text(result, encoding="utf-8")
        click.echo(f"Written to {output}")
    else:
        click.echo(result, nl=False)


def main() -> None:  # pragma: no cover
    cli()


if __name__ == "__main__":  # pragma: no cover
    main()
