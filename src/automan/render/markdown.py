# src/automan/render/markdown.py
"""Render a CliDoc as GitHub-Flavoured Markdown."""
from __future__ import annotations

from automan.models import CliDoc, Flag


def render(doc: CliDoc) -> str:
    """
    Render *doc* as a Markdown string.

    Suitable for saving as ``<tool>.md``, embedding in a docs site,
    or rendering in a terminal with a Markdown pager (e.g. glow).
    """
    parts: list[str] = []

    # Title
    title = f"# {doc.name}"
    if doc.version:
        title += f" ({doc.version})"
    parts.append(title)

    if doc.short_description:
        parts.append(f"\n{doc.short_description}\n")

    # Synopsis
    if doc.usage:
        parts.append("## Synopsis\n")
        parts.append(f"```\n{doc.usage}\n```\n")

    # Description
    if doc.long_description:
        parts.append("## Description\n")
        parts.append(doc.long_description + "\n")

    # Options
    if doc.flags:
        parts.append("## Options\n")
        parts.append(_render_flags(doc.flags))

    # Subcommands
    if doc.subcommands:
        parts.append("## Commands\n")
        parts.append("| Command | Description |")
        parts.append("|---------|-------------|")
        for sub in doc.subcommands:
            parts.append(f"| `{sub.name}` | {sub.description} |")
        parts.append("")

    # Examples
    if doc.examples:
        parts.append("## Examples\n")
        for ex in doc.examples:
            parts.append(f"```sh\n{ex}\n```\n")

    # Authors
    if doc.authors:
        parts.append("## Authors\n")
        parts.append(", ".join(doc.authors) + "\n")

    # See also
    if doc.see_also:
        parts.append("## See Also\n")
        parts.append(", ".join(f"`{s}`" for s in doc.see_also) + "\n")

    return "\n".join(parts)


def _render_flags(flags: list[Flag]) -> str:
    rows = ["| Flag | Metavar | Description |", "|------|---------|-------------|"]
    for f in flags:
        flag_str = ", ".join(p for p in [f.short, f.long] if p)
        metavar = f"`{f.metavar}`" if f.metavar else ""
        rows.append(f"| `{flag_str}` | {metavar} | {f.description} |")
    return "\n".join(rows) + "\n"
