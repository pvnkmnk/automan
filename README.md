# automan

> Auto-generate structured man-pages and Markdown docs from any CLI tool's `--help` output.

[![CI](https://github.com/pvnkmnk/automan/actions/workflows/ci.yml/badge.svg)](https://github.com/pvnkmnk/automan/actions/workflows/ci.yml)

## What it does

`automan` probes an installed CLI tool (via `--help`, `-h`, `help`, or fallback),
parses the help text heuristically into a structured data model, normalises
the output, optionally enriches it (version, see-also), and renders it as
either a groff/troff **man-page** or **GitHub-Flavoured Markdown**.

```
curl --help   -->  automan gen curl          -->  curl.1  (man-page)
git --help    -->  automan gen git --format md  -->  git.md  (Markdown)
```

## Architecture

```
CLI tool
   |
   v
[probe]  -- runs --help / -h / help / fallback
   |
   v
[parser]  -- regex heuristics: flags, subcommands, usage, version
   |
   v
[normalizer]  -- ANSI strip, whitespace collapse, dedup, capitalise
   |
   v
[enricher]  -- fills in missing version, infers see-also
   |
   v
[render]  -- manpage.py (groff) | markdown.py (GFM)
```

## Install

```sh
# From source (editable)
git clone https://github.com/pvnkmnk/automan
cd automan
pip install -e .[dev]
```

## Usage

```sh
# Generate a man-page for curl and install it
automan gen curl -o /usr/local/share/man/man1/curl.1
man curl

# Generate Markdown docs for git
automan gen git --format md -o git.md

# Print to stdout (for piping into groff)
automan gen ls | groff -man -Tutf8 | less
```

## Development

This project uses [mise](https://mise.jdx.dev/) for toolchain management.

```sh
# Install tools (Python, etc.)
mise install

# Run tests
mise run test

# Run linters
mise run lint

# Format code
mise run fmt
```

## Project layout

```
src/automan/
  __init__.py       version
  models.py         domain dataclasses (CliDoc, Flag, Argument, Subcommand)
  probe.py          runs CLI tools and captures help output
  parser.py         heuristic regex parser
  normalizer.py     ANSI stripping, whitespace, dedup
  enricher.py       version probing, see-also inference
  cli.py            Click entry-point (automan gen)
  render/
    manpage.py      groff/troff renderer
    markdown.py     GitHub-Flavoured Markdown renderer

tests/
  unit/             pure Python unit tests (no subprocess)
  integration/      tests that run real system commands
  fixtures/         captured --help outputs for golden testing
```

## License

MIT
