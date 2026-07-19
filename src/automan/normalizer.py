# src/automan/normalizer.py
"""Normalizer: cleans and canonicalises a CliDoc after parsing."""
from __future__ import annotations

import re
import textwrap

from automan.models import CliDoc, Flag, Subcommand

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_MULTI_SPACE_RE = re.compile(r" {2,}")
_BLANK_LINE_RE = re.compile(r"\n{3,}")


def normalize(doc: CliDoc) -> CliDoc:
    """
    Return a new :class:`CliDoc` with cleaned text fields.

    Operations applied
    ------------------
    * Strip ANSI escape codes from all text fields.
    * Collapse excessive whitespace in descriptions.
    * Deduplicate flags (by long name, then short name).
    * Deduplicate subcommands by name.
    * Capitalise first letter of every description.
    * Trim leading/trailing blank lines from long_description.
    """
    return CliDoc(
        name=doc.name.strip(),
        version=doc.version,
        short_description=_clean(doc.short_description),
        long_description=_clean_block(doc.long_description),
        usage=_clean(doc.usage),
        flags=_dedup_flags([_normalize_flag(f) for f in doc.flags]),
        arguments=doc.arguments,
        subcommands=_dedup_subcommands(
            [_normalize_subcommand(s) for s in doc.subcommands]
        ),
        examples=doc.examples,
        authors=doc.authors,
        see_also=doc.see_also,
        probe_strategy=doc.probe_strategy,
        source_command=doc.source_command,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def _clean(text: str) -> str:
    """Strip ANSI, collapse inner spaces, strip edges."""
    text = _strip_ansi(text)
    text = _MULTI_SPACE_RE.sub(" ", text)
    text = text.strip()
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    return text


def _clean_block(text: str) -> str:
    """Clean a multi-line text block."""
    text = _strip_ansi(text)
    text = _BLANK_LINE_RE.sub("\n\n", text)  # max one blank line
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def _normalize_flag(flag: Flag) -> Flag:
    return Flag(
        short=flag.short,
        long=flag.long,
        metavar=flag.metavar,
        description=_clean(flag.description),
        required=flag.required,
        repeatable=flag.repeatable,
    )


def _normalize_subcommand(sub: Subcommand) -> Subcommand:
    return Subcommand(
        name=sub.name.strip(),
        description=_clean(sub.description),
        flags=[_normalize_flag(f) for f in sub.flags],
        arguments=sub.arguments,
        subcommands=[_normalize_subcommand(s) for s in sub.subcommands],
        examples=sub.examples,
    )


def _dedup_flags(flags: list[Flag]) -> list[Flag]:
    seen_long: set[str] = set()
    seen_short: set[str] = set()
    result: list[Flag] = []
    for f in flags:
        key_long = f.long or ""
        key_short = f.short or ""
        if key_long and key_long in seen_long:
            continue
        if not key_long and key_short and key_short in seen_short:
            continue
        if key_long:
            seen_long.add(key_long)
        if key_short:
            seen_short.add(key_short)
        result.append(f)
    return result


def _dedup_subcommands(subs: list[Subcommand]) -> list[Subcommand]:
    seen: set[str] = set()
    result: list[Subcommand] = []
    for s in subs:
        if s.name in seen:
            continue
        seen.add(s.name)
        result.append(s)
    return result
