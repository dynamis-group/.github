"""Shared helpers for the tests."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Stand-in for the dynamis-group/.github-private checkout, with neutral repository data.
MEMBERS_FIXTURE = ROOT / "tests" / "fixtures" / "members"
