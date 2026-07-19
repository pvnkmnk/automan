# src/automan/parser.py
"""Heuristic parser: converts raw help text into structured CliDoc."""
from __future__ import annotations

import re
from typing import Optional

from automan.models import Argument, CliDoc, Flag, RawProbe, Subcommand

# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------

# Matches: -f, --flag  or  --flag=VALUE  or  -f, --flag VALUE  [description]
_FLAG_RE = re.compile(
    r"^\s*"
    r"(?P<short>-[a-zA-Z0-9])?"          # optional short flag
    r"(?:[,\s]+)?"                        # optional separator
    r"(?P<long>--[a-zA-Z0-9][a-zA-Z0-9_-]*)"  # long flag (required)
    r"(?:[=\s]+(?P<metavar>[A-Z_][A-Z_0-9]*))?"  # optional metavar
    r"\s{2,}(?P<desc>.+)$",              # 2+ spaces then description
    re.MULTILINE,
)

# Matches short-only flags like: -v  Verbose output
_SHORT_FLAG_RE = re.compile(
    r"^\s+(?P<short>-[a-zA-Z])\s{2,}(?P<desc>.+)$",
    re.MULTILINE,
)

# Subcommand lines: "  subcommand   Description text"
_SUBCMD_RE = re.compile(
    r"^\s{2,4}(?P<name>[a-z][a-z0-9_-]*)\s{2,}(?P<desc>.+)$",
    re.MULTILINE,
)

# Usage line
_USAGE_RE = re.compile(r"^[Uu]sage:\s*(.+)$", re.MULTILINE)

# Version strings like "tool 1.2.3" or "tool version 1.2.3"
_VERSION_RE = re.compile(
    r"\bv?(?P<ver>\d+\.\d+(?:\.\d+)?(?:[.-][a-zA-Z0-9]+)?)\b"
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(probe: RawProbe) -> CliDoc:
    """Parse a :class:`RawProbe` into a :class:`CliDoc`."""
    text = (probe.stdout or probe.stderr).strip()
    lines = text.splitlines()

    short_desc = _extract_short_description(lines)
    usage = _extract_usage(text)
    version = _extract_version(lines[:5])  # version usually near top
    flags = _extract_flags(text)
    subcommands = _extract_subcommands(text, flags)

    return CliDoc(
        name=probe.command,
        version=version,
        short_description=short_desc,
        long_description="",
        usage=usage,
        flags=flags,
        subcommands=subcommands,
        probe_strategy=probe.strategy,
        source_command=probe.command,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_short_description(lines: list[str]) -> str:
    """Return the first non-empty, non-usage line as the short description."""
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.lower().startswith(("usage:", "options",
                                                         "commands", "flags")):
            return stripped
    return ""


def _extract_usage(text: str) -> str:
    m = _USAGE_RE.search(text)
    return m.group(1).strip() if m else ""


def _extract_version(lines: list[str]) -> Optional[str]:
    for line in lines:
        m = _VERSION_RE.search(line)
        if m:
            return m.group("ver")
    return None


def _extract_flags(text: str) -> list[Flag]:
    flags: list[Flag] = []
    seen: set[str] = set()

    for m in _FLAG_RE.finditer(text):
        long = m.group("long")
        if long in seen:
            continue
        seen.add(long)
        flags.append(Flag(
            short=m.group("short"),
            long=long,
            metavar=m.group("metavar"),
            description=m.group("desc").strip(),
        ))

    for m in _SHORT_FLAG_RE.finditer(text):
        short = m.group("short")
        if short in seen:
            continue
        seen.add(short)
        flags.append(Flag(
            short=short,
            long=None,
            metavar=None,
            description=m.group("desc").strip(),
        ))

    return flags


def _extract_subcommands(text: str, existing_flags: list[Flag]) -> list[Subcommand]:
    """Extract subcommand names heuristically, skipping flag names."""
    flag_longs = {f.long for f in existing_flags if f.long}
    subcommands: list[Subcommand] = []
    seen: set[str] = set()

    for m in _SUBCMD_RE.finditer(text):
        name = m.group("name")
        # Skip if it looks like a flag argument or already seen
        if name in seen or f"--{name}" in flag_longs:
            continue
        seen.add(name)
        subcommands.append(Subcommand(
            name=name,
            description=m.group("desc").strip(),
        ))

    return subcommands
