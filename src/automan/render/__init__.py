# src/automan/render/__init__.py
"""Render sub-package: output formatters for CliDoc."""
from __future__ import annotations

from automan.render.manpage import render as render_manpage
from automan.render.markdown import render as render_markdown

__all__ = ["render_manpage", "render_markdown"]
