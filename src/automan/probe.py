# src/automan/probe.py
"""Probe layer: runs a CLI tool and captures its help output."""
from __future__ import annotations

import shutil
import subprocess
from typing import Optional

from automan.models import ProbeStrategy, RawProbe

# Ordered list of strategies to try
_STRATEGIES: list[tuple[ProbeStrategy, list[str]]] = [
    (ProbeStrategy.HELP_FLAG, ["--help"]),
    (ProbeStrategy.HELP_FLAG, ["-h"]),
    (ProbeStrategy.HELP_SUBCOMMAND, ["help"]),
    (ProbeStrategy.FALLBACK, []),
]

_TIMEOUT = 10  # seconds


def _run(command: str, args: list[str]) -> tuple[str, str, int]:
    """Run *command* with *args* and return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            [command, *args],
            capture_output=True,
            text=True,
            timeout=_TIMEOUT,
        )
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        raise RuntimeError(f"Command not found: {command!r}")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Command timed out after {_TIMEOUT}s: {command!r}")


def probe(command: str, *, strategy: Optional[ProbeStrategy] = None) -> RawProbe:
    """
    Probe *command* and return the best :class:`RawProbe` we can get.

    If *strategy* is given, only that strategy is attempted.
    Otherwise strategies are tried in order until one yields non-empty output.
    """
    if not shutil.which(command):
        raise RuntimeError(f"Command not found on PATH: {command!r}")

    candidates = (
        [(strategy, _strategy_args(strategy))]
        if strategy
        else _STRATEGIES
    )

    last: Optional[RawProbe] = None
    for strat, args in candidates:
        stdout, stderr, rc = _run(command, args)
        probe_result = RawProbe(
            command=command,
            args=args,
            stdout=stdout,
            stderr=stderr,
            returncode=rc,
            strategy=strat,
        )
        last = probe_result
        combined = (stdout + stderr).strip()
        if combined:
            return probe_result

    # All strategies returned empty output — return the last attempt
    assert last is not None
    return last


def _strategy_args(strategy: ProbeStrategy) -> list[str]:
    """Return the CLI arguments that correspond to *strategy*."""
    mapping = {
        ProbeStrategy.HELP_FLAG: ["--help"],
        ProbeStrategy.HELP_SUBCOMMAND: ["help"],
        ProbeStrategy.MAN_PAGE: [],  # handled separately via man(1)
        ProbeStrategy.FALLBACK: [],
    }
    return mapping.get(strategy, [])
