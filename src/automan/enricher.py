# src/automan/enricher.py
"""Enricher: post-processing pass to fill in gaps left by the parser."""
from __future__ import annotations

import re
import subprocess
from typing import Optional

from automan.models import CliDoc

_VERSION_FLAGS = ("--version", "-V", "-v", "version")
_TIMEOUT = 5


def enrich(doc: CliDoc) -> CliDoc:
    """
    Attempt to fill in missing fields on *doc* without re-parsing.

    Currently enriches:
    * ``version``   — if missing, tries ``--version`` / ``-V``
    * ``see_also``  — adds related man-page names heuristically
    """
    version = doc.version or _probe_version(doc.source_command)
    see_also = doc.see_also or _infer_see_also(doc)

    return CliDoc(
        name=doc.name,
        version=version,
        short_description=doc.short_description,
        long_description=doc.long_description,
        usage=doc.usage,
        flags=doc.flags,
        arguments=doc.arguments,
        subcommands=doc.subcommands,
        examples=doc.examples,
        authors=doc.authors,
        see_also=see_also,
        probe_strategy=doc.probe_strategy,
        source_command=doc.source_command,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VER_RE = re.compile(
    r"\bv?(?P<ver>\d+\.\d+(?:\.\d+)?(?:[.-][a-zA-Z0-9]+)?)\b"
)


def _probe_version(command: str) -> Optional[str]:
    """Try common version flags and extract a semver-ish string."""
    for flag in _VERSION_FLAGS:
        try:
            r = subprocess.run(
                [command, flag],
                capture_output=True,
                text=True,
                timeout=_TIMEOUT,
            )
            combined = (r.stdout + r.stderr).strip()
            m = _VER_RE.search(combined)
            if m:
                return m.group("ver")
        except Exception:  # noqa: BLE001
            continue
    return None


def _infer_see_also(doc: CliDoc) -> list[str]:
    """
    Heuristically build a ``SEE ALSO`` list.

    Strategy: if the tool has subcommands, suggest ``<tool>-<subcommand>(1)``
    man-page names (common convention in git-style tools).
    """
    if not doc.subcommands:
        return []
    return [
        f"{doc.name}-{sub.name}(1)"
        for sub in doc.subcommands[:5]  # cap at 5 to avoid noise
    ]
