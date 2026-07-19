# tests/unit/test_normalizer.py
"""Unit tests for automan.normalizer."""
from __future__ import annotations

from automan.models import CliDoc, Flag, Subcommand
from automan.normalizer import _clean, _dedup_flags, _dedup_subcommands, normalize


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _basic_doc(**kwargs) -> CliDoc:
    defaults = dict(
        name="mytool",
        version=None,
        short_description="a tool",
        long_description="",
        usage="mytool [options]",
        flags=[],
        arguments=[],
        subcommands=[],
        examples=[],
        authors=[],
        see_also=[],
    )
    defaults.update(kwargs)
    return CliDoc(**defaults)


# ---------------------------------------------------------------------------
# _clean
# ---------------------------------------------------------------------------

class TestClean:
    def test_strips_ansi(self):
        text = "\x1b[32mGreen text\x1b[0m"
        assert _clean(text) == "Green text"

    def test_collapses_spaces(self):
        assert _clean("foo   bar") == "foo bar"

    def test_capitalises_first_letter(self):
        assert _clean("lowercase first") == "Lowercase first"

    def test_does_not_double_capitalise(self):
        assert _clean("Already capitalised") == "Already capitalised"

    def test_strips_leading_trailing_whitespace(self):
        assert _clean("  trimmed  ") == "Trimmed"

    def test_empty_string(self):
        assert _clean("") == ""


# ---------------------------------------------------------------------------
# _dedup_flags
# ---------------------------------------------------------------------------

class TestDedupFlags:
    def _make_flag(self, short=None, long=None):
        return Flag(short=short, long=long, metavar=None, description="")

    def test_removes_duplicate_long_flags(self):
        flags = [
            self._make_flag(long="--verbose"),
            self._make_flag(long="--verbose"),
        ]
        assert len(_dedup_flags(flags)) == 1

    def test_removes_duplicate_short_flags(self):
        flags = [
            self._make_flag(short="-v"),
            self._make_flag(short="-v"),
        ]
        assert len(_dedup_flags(flags)) == 1

    def test_keeps_distinct_flags(self):
        flags = [
            self._make_flag(long="--verbose"),
            self._make_flag(long="--quiet"),
        ]
        assert len(_dedup_flags(flags)) == 2


# ---------------------------------------------------------------------------
# _dedup_subcommands
# ---------------------------------------------------------------------------

class TestDedupSubcommands:
    def _make_sub(self, name):
        return Subcommand(name=name, description="")

    def test_removes_duplicates(self):
        subs = [self._make_sub("init"), self._make_sub("init")]
        assert len(_dedup_subcommands(subs)) == 1

    def test_keeps_distinct(self):
        subs = [self._make_sub("init"), self._make_sub("clone")]
        assert len(_dedup_subcommands(subs)) == 2


# ---------------------------------------------------------------------------
# normalize (full pass)
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_returns_clidoc(self):
        doc = _basic_doc()
        result = normalize(doc)
        assert isinstance(result, CliDoc)

    def test_strips_ansi_from_short_description(self):
        doc = _basic_doc(short_description="\x1b[31mRed description\x1b[0m")
        result = normalize(doc)
        assert result.short_description == "Red description"

    def test_deduplicates_flags(self):
        dup_flag = Flag(short="-v", long="--verbose", metavar=None, description="Verbose")
        doc = _basic_doc(flags=[dup_flag, dup_flag])
        result = normalize(doc)
        assert len(result.flags) == 1

    def test_deduplicates_subcommands(self):
        sub = Subcommand(name="run", description="Run it")
        doc = _basic_doc(subcommands=[sub, sub])
        result = normalize(doc)
        assert len(result.subcommands) == 1

    def test_name_stripped(self):
        doc = _basic_doc(name="  mytool  ")
        result = normalize(doc)
        assert result.name == "mytool"

    def test_preserves_version(self):
        doc = _basic_doc(version="1.2.3")
        result = normalize(doc)
        assert result.version == "1.2.3"
