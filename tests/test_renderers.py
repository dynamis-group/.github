"""Golden files for every renderer.

The public images are their own goldens (the build test compares them). The members-only
profile reuses the public banner, so its copy must match the public images exactly.
"""

from __future__ import annotations

from pathlib import Path

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
            tile = art.division_tile(assets.TOKENS, theme, index, division, Ledger(), "t")
            assert tile == committed(f"{division.slug}-{name}-compact.svg")
        assert art.cta(assets.TOKENS, theme, Ledger(), "c") == committed(f"contact-{name}.svg")


def test_members_profile_opens_with_the_public_banner(tmp_path: Path) -> None:
    built, _ = assets.build_private(tmp_path)
    names = {path.name for path in built}
    assert names == {f"banner-{t}{s}.svg" for t in ("dark", "light") for s in ("", "-compact")}
    for path, content in built.items():
        assert content == committed(path.name), path.name


def test_the_division_row_spans_the_banner() -> None:
    """Three images of a third each, flush with the banner's edges, with equal gaps."""
    assert art.CARD_W * 3 == art.ROW_W == art.BANNER_WIDE.width
    edges = []
    for position in range(3):
        left = position * art.CARD_W + art._slot(position, art.CARD_GAP)
        edges.append((left, left + art.CARD_VISIBLE))
    assert edges[0][0] == 0 and abs(edges[-1][1] - art.ROW_W) < 1e-9
    gaps = [edges[i + 1][0] - edges[i][1] for i in range(2)]
    assert all(abs(g - art.CARD_GAP) < 1e-9 for g in gaps)


def test_readme_rows_have_no_space_between_the_divisions() -> None:
    text = (assets.PUBLIC.parent / "README.md").read_text(encoding="utf-8")
    row = next(line for line in text.splitlines() if "/digital/" in line)
    assert row.count('width="33.33%"') == 3 and "</a><a " in row and "</a> <a" not in row


def test_cards_never_end_on_an_orphaned_word() -> None:
    from svgkit.canvas import Canvas

    theme = assets.TOKENS.themes["dark"]
    canvas = Canvas("t", art.CARD_W, art.CARD_H, ledger=Ledger(), bg=theme.surface, min_scale=1)
    canvas.style("p", assets.TOKENS.fonts.sans, 15, theme.fg_dim)
    for division in assets.TOKENS.divisions:
        lines = canvas.wrap(division.positioning, "p", art.CARD_VISIBLE - 48)
        assert len(lines[-1].split()) > 1, division.slug
