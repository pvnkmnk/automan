# src/automan/models.py
"""Domain models for automan — pure dataclasses, no I/O."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class ProbeStrategy(Enum):
    """How the help text was obtained."""
    HELP_FLAG = auto()       # cmd --help
    HELP_SUBCOMMAND = auto() # cmd help
    MAN_PAGE = auto()        # man cmd
    FALLBACK = auto()        # no-args / stderr


@dataclass
class RawProbe:
    """Raw output captured from a CLI probe attempt."""
    command: str
    args: list[str]
    stdout: str
    stderr: str
    returncode: int
    strategy: ProbeStrategy


@dataclass
class Flag:
    """A single CLI flag / option."""
    short: Optional[str]          # e.g. "-v"
    long: Optional[str]           # e.g. "--verbose"
    metavar: Optional[str]        # e.g. "FILE"
    description: str = ""
    required: bool = False
    repeatable: bool = False


@dataclass
class Argument:
    """A positional argument."""
    name: str
    description: str = ""
    optional: bool = False
    variadic: bool = False        # e.g. FILE...


@dataclass
class Subcommand:
    """A subcommand entry (may be recursive)."""
    name: str
    description: str = ""
    flags: list[Flag] = field(default_factory=list)
    arguments: list[Argument] = field(default_factory=list)
    subcommands: list["Subcommand"] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


@dataclass
class CliDoc:
    """Fully-parsed, normalised representation of a CLI tool's documentation."""
    name: str
    version: Optional[str]
    short_description: str
    long_description: str = ""
    usage: str = ""
    flags: list[Flag] = field(default_factory=list)
    arguments: list[Argument] = field(default_factory=list)
    subcommands: list[Subcommand] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    authors: list[str] = field(default_factory=list)
    see_also: list[str] = field(default_factory=list)
    # Metadata
    probe_strategy: Optional[ProbeStrategy] = None
    source_command: str = ""
