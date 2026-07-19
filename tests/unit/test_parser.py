# tests/unit/test_parser.py
"""Unit tests for automan.parser."""
from __future__ import annotations

import pytest

from automan.models import ProbeStrategy, RawProbe
from automan.parser import (
    _extract_flags,
    _extract_short_description,
    _extract_usage,
    _extract_version,
    parse,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

SAMPLE_HELP = """\
curl - transfer a URL

Usage: curl [options...] <url>

Options:
  -h, --help              Show this help message
  -V, --version           Show version and exit
  -v, --verbose           Make the operation more talkative
  -o, --output FILE       Write output to FILE instead of stdout
  -s, --silent            Silent mode; don't show progress meter or errors

Commands:
  fetch   Download a remote resource
  upload  Upload a file to a remote server
"""


def _make_probe(text: str, command: str = "curl") -> RawProbe:
    return RawProbe(
        command=command,
        args=["--help"],
        stdout=text,
        stderr="",
        returncode=0,
        strategy=ProbeStrategy.HELP_FLAG,
    )


# ---------------------------------------------------------------------------
# _extract_short_description
# ---------------------------------------------------------------------------

class TestExtractShortDescription:
    def test_returns_first_meaningful_line(self):
        lines = ["curl - transfer a URL", "Usage: curl [options]", "More stuff"]
        assert _extract_short_description(lines) == "curl - transfer a URL"

    def test_skips_empty_lines(self):
        lines = ["", "  ", "My tool does things"]
        assert _extract_short_description(lines) == "My tool does things"

    def test_skips_usage_line(self):
        lines = ["Usage: foo [options]", "A great tool"]
        assert _extract_short_description(lines) == "A great tool"

    def test_returns_empty_on_all_usage(self):
        lines = ["Usage: foo", "Options:", "Commands:"]
        assert _extract_short_description(lines) == ""


# ---------------------------------------------------------------------------
# _extract_usage
# ---------------------------------------------------------------------------

class TestExtractUsage:
    def test_extracts_usage_line(self):
        text = "Usage: curl [options...] <url>"
        assert _extract_usage(text) == "curl [options...] <url>"

    def test_case_insensitive(self):
        text = "usage: mytool [flags]"
        assert _extract_usage(text) == "mytool [flags]"

    def test_returns_empty_when_no_usage(self):
        text = "No usage here"
        assert _extract_usage(text) == ""


# ---------------------------------------------------------------------------
# _extract_version
# ---------------------------------------------------------------------------

class TestExtractVersion:
    def test_extracts_semver(self):
        lines = ["curl 7.88.1"]
        assert _extract_version(lines) == "7.88.1"

    def test_extracts_with_v_prefix(self):
        lines = ["mytool v2.0.0 (build 123)"]
        assert _extract_version(lines) == "2.0.0"

    def test_returns_none_when_no_version(self):
        lines = ["No version info here"]
        assert _extract_version(lines) is None

    def test_prefers_first_match(self):
        lines = ["tool 1.0.0", "other 2.0.0"]
        assert _extract_version(lines) == "1.0.0"


# ---------------------------------------------------------------------------
# _extract_flags
# ---------------------------------------------------------------------------

class TestExtractFlags:
    def test_extracts_long_flags(self):
        flags = _extract_flags(SAMPLE_HELP)
        longs = [f.long for f in flags if f.long]
        assert "--help" in longs
        assert "--verbose" in longs

    def test_extracts_short_flags(self):
        flags = _extract_flags(SAMPLE_HELP)
        shorts = [f.short for f in flags if f.short]
        assert "-h" in shorts
        assert "-v" in shorts

    def test_extracts_metavar(self):
        flags = _extract_flags(SAMPLE_HELP)
        output_flag = next((f for f in flags if f.long == "--output"), None)
        assert output_flag is not None
        assert output_flag.metavar == "FILE"

    def test_no_duplicates(self):
        flags = _extract_flags(SAMPLE_HELP)
        longs = [f.long for f in flags if f.long]
        assert len(longs) == len(set(longs))


# ---------------------------------------------------------------------------
# parse (integration of all helpers)
# ---------------------------------------------------------------------------

class TestParse:
    def test_returns_clidoc(self):
        from automan.models import CliDoc
        doc = parse(_make_probe(SAMPLE_HELP))
        assert isinstance(doc, CliDoc)

    def test_command_name(self):
        doc = parse(_make_probe(SAMPLE_HELP, command="curl"))
        assert doc.name == "curl"

    def test_short_description_populated(self):
        doc = parse(_make_probe(SAMPLE_HELP))
        assert doc.short_description  # non-empty

    def test_usage_populated(self):
        doc = parse(_make_probe(SAMPLE_HELP))
        assert "curl" in doc.usage

    def test_flags_populated(self):
        doc = parse(_make_probe(SAMPLE_HELP))
        assert len(doc.flags) > 0

    def test_subcommands_extracted(self):
        doc = parse(_make_probe(SAMPLE_HELP))
        names = [s.name for s in doc.subcommands]
        assert "fetch" in names or "upload" in names

    def test_empty_help_gives_empty_doc(self):
        doc = parse(_make_probe(""))
        assert doc.short_description == ""
        assert doc.flags == []
