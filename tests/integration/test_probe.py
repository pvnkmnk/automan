# tests/integration/test_probe.py
"""Integration tests for automan.probe — requires real system commands."""
from __future__ import annotations

import shutil

import pytest

from automan.models import ProbeStrategy, RawProbe
from automan.probe import probe


# ---------------------------------------------------------------------------
# Helpers / marks
# ---------------------------------------------------------------------------

def _skip_if_missing(command: str):
    """Skip the test if *command* is not available on PATH."""
    return pytest.mark.skipif(
        shutil.which(command) is None,
        reason=f"{command!r} not found on PATH",
    )


# ---------------------------------------------------------------------------
# Tests against universally available POSIX commands
# ---------------------------------------------------------------------------

@_skip_if_missing("ls")
class TestProbeLs:
    def test_returns_raw_probe(self):
        result = probe("ls")
        assert isinstance(result, RawProbe)

    def test_command_field(self):
        result = probe("ls")
        assert result.command == "ls"

    def test_combined_output_nonempty(self):
        result = probe("ls")
        combined = result.stdout + result.stderr
        assert combined.strip()

    def test_strategy_recorded(self):
        result = probe("ls")
        assert result.strategy in ProbeStrategy


@_skip_if_missing("python3")
class TestProbePython3:
    def test_returns_probe(self):
        result = probe("python3")
        assert isinstance(result, RawProbe)

    def test_nonempty_output(self):
        result = probe("python3")
        assert (result.stdout + result.stderr).strip()


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestProbeErrors:
    def test_raises_on_missing_command(self):
        with pytest.raises(RuntimeError, match="not found"):
            probe("__nonexistent_command_automan_test__")

    def test_strategy_override(self):
        """Passing an explicit strategy should not crash."""
        if shutil.which("ls") is None:
            pytest.skip("ls not available")
        result = probe("ls", strategy=ProbeStrategy.HELP_FLAG)
        assert isinstance(result, RawProbe)
