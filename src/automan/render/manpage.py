# src/automan/render/manpage.py
"""Render a CliDoc as a groff/troff man-page (mdoc-lite style)."""
from __future__ import annotations

import datetime
from typing import Optional

from automan.models import CliDoc, Flag, Subcommand

_SECTION = "1"  # user commands


def render(doc: CliDoc, section: str = _SECTION) -> str:
    """
    Render *doc* as a groff man-page string.

    The output can be piped directly to ``groff -man -Tutf8`` or written
    to a ``.<section>`` file in a man-page directory.
    """
    date_str = datetime.date.today().strftime("%B %Y")
    version_str = doc.version or ""
    lines: list[str] = []

    # TH macro: title, section, date, source, manual
    lines.append(
        f'.TH "{doc.name.upper()}" "{section}" "{date_str}" "{version_str}" "User Commands"'
    )

    # NAME
    lines.append(".SH NAME")
    name_line = doc.name
    if doc.short_description:
        name_line += f" \\- {doc.short_description}"
    lines.append(name_line)

    # SYNOPSIS
    if doc.usage:
        lines.append(".SH SYNOPSIS")
        lines.append(f".B {doc.name}")
        lines.append(f".RI {_escape(doc.usage)}")

    # DESCRIPTION
    if doc.long_description:
        lines.append(".SH DESCRIPTION")
        lines.append(_escape(doc.long_description))

    # OPTIONS
    if doc.flags:
        lines.append(".SH OPTIONS")
        for flag in doc.flags:
            lines.append(".TP")
            flag_str = _flag_synopsis(flag)
            lines.append(f".B {flag_str}")
            if flag.description:
                lines.append(_escape(flag.description))

    # COMMANDS / SUBCOMMANDS
    if doc.subcommands:
        lines.append(".SH COMMANDS")
        for sub in doc.subcommands:
            lines.append(".TP")
            lines.append(f".B {sub.name}")
            if sub.description:
                lines.append(_escape(sub.description))

    # EXAMPLES
    if doc.examples:
        lines.append(".SH EXAMPLES")
        for ex in doc.examples:
            lines.append(".PP")
            lines.append(f".EX")
            lines.append(_escape(ex))
            lines.append(".EE")

    # AUTHORS
    if doc.authors:
        lines.append(".SH AUTHORS")
        lines.append(", ".join(doc.authors))

    # SEE ALSO
    if doc.see_also:
        lines.append(".SH SEE ALSO")
        lines.append(", ".join(doc.see_also))

    return "\n".join(lines) + "\n"


def _escape(text: str) -> str:
    """Escape groff special characters."""
    return text.replace("\\", "\\\\").replace("'", "\\&'").replace(".", "\\&.")


def _flag_synopsis(flag: Flag) -> str:
    parts: list[str] = []
    if flag.short:
        parts.append(flag.short)
    if flag.long:
        parts.append(flag.long)
    synopsis = ", ".join(parts)
    if flag.metavar:
        synopsis += f" <{flag.metavar}>"
    return synopsis
