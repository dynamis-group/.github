"""Golden files for every renderer.

The public images are their own goldens (the build test compares them). The members banner
ships in the private repository, so its goldens live here, where public CI can check them.
"""

from __future__ import annotations

from conftest import assert_golden
from dynamis import art, assets
from svgkit.color import Ledger


def committed(name: str) -> str:
    return (assets.PUBLIC / name).read_text(encoding="utf-8")


def test_public_renderers_match_the_committed_images() -> None:
    for name, theme in assets.TOKENS.themes.items():
        assert art.banner(assets.TOKENS, theme, art.BANNER_WIDE, Ledger(), "b") == committed(
            f"banner-{name}.svg"
        )
        compact = art.banner(assets.TOKENS, theme, art.BANNER_COMPACT, Ledger(), "b")
        assert compact == committed(f"banner-{name}-compact.svg")
        for index, division in enumerate(assets.TOKENS.divisions, start=1):
            card = art.division_card(assets.TOKENS, theme, index, division, Ledger(), "c")
            assert card == committed(f"{division.slug}-{name}.svg")
        assert art.cta(assets.TOKENS, theme, Ledger(), "c") == committed(f"contact-{name}.svg")


def test_members_banner() -> None:
    for name, theme in sorted(assets.TOKENS.themes.items()):
        for compact in (False, True):
            suffix = "-compact" if compact else ""
            rendered = art.members_banner(assets.TOKENS, theme, compact, Ledger(), "m")
            assert_golden(f"members-{name}{suffix}.svg", rendered)


def test_cards_never_end_on_an_orphaned_word() -> None:
    from svgkit.canvas import Canvas

    theme = assets.TOKENS.themes["dark"]
    canvas = Canvas("t", art.CARD_W, art.CARD_H, ledger=Ledger(), bg=theme.surface, min_scale=1)
    canvas.style("p", assets.TOKENS.fonts.sans, 15, theme.fg_dim)
    for division in assets.TOKENS.divisions:
        lines = canvas.wrap(division.positioning, "p", art.CARD_W - 48)
        assert len(lines[-1].split()) > 1, division.slug
