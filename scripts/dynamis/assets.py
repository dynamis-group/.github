"""Every image the organisation profiles use, and how to build, write and verify them."""

from __future__ import annotations

from pathlib import Path

from svgkit.color import Ledger
from svgkit.svg import write_if_changed

from . import art
from .theme import ROOT, load

TOKENS = load()
PUBLIC = ROOT / "profile" / "assets"
# The members-only profile lives in dynamis-group/.github-private; build it there when that
# repository is checked out next to this one.
PRIVATE_DEFAULT = ROOT.parent / ".github-private" / "profile" / "assets"


def build_public() -> tuple[dict[Path, str], Ledger]:
    ledger = Ledger()
    out: dict[Path, str] = {}
    for name, theme in sorted(TOKENS.themes.items()):
        out[PUBLIC / f"banner-{name}.svg"] = art.banner(
            TOKENS, theme, art.BANNER_WIDE, ledger, f"banner-{name}.svg"
        )
        out[PUBLIC / f"banner-{name}-compact.svg"] = art.banner(
            TOKENS, theme, art.BANNER_COMPACT, ledger, f"banner-{name}-compact.svg"
        )
        for index, division in enumerate(TOKENS.divisions, start=1):
            rel = f"{division.slug}-{name}.svg"
            out[PUBLIC / rel] = art.division_card(TOKENS, theme, index, division, ledger, rel)
        out[PUBLIC / f"contact-{name}.svg"] = art.cta(TOKENS, theme, ledger, f"contact-{name}.svg")
    return out, ledger


def build_private(target: Path) -> tuple[dict[Path, str], Ledger]:
    ledger = Ledger()
    out: dict[Path, str] = {}
    for name, theme in sorted(TOKENS.themes.items()):
        out[target / f"members-{name}.svg"] = art.members_banner(
            TOKENS, theme, False, ledger, f"members-{name}.svg"
        )
        out[target / f"members-{name}-compact.svg"] = art.members_banner(
            TOKENS, theme, True, ledger, f"members-{name}-compact.svg"
        )
    return out, ledger


def write(built: dict[Path, str]) -> list[Path]:
    return [path for path, content in sorted(built.items()) if write_if_changed(path, content)]


def stale(built: dict[Path, str], folder: Path) -> list[Path]:
    present = set(folder.glob("*.svg"))
    changed = [
        path
        for path, content in sorted(built.items())
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]
    return changed + sorted(present - set(built))
