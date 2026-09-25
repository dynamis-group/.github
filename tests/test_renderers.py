"""Golden files for every renderer.

The public images are their own goldens (the build test compares them). The members-only
profile reuses the public banner, so its copy must match the public images exactly.
"""

from __future__ import annotations

import dataclasses

import pytest
from conftest import MEMBERS_FIXTURE
from dynamis import art, assets
from dynamis.theme import load_repositories
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


def test_members_profile_opens_with_the_public_banner() -> None:
    built, _ = assets.build_private(MEMBERS_FIXTURE)
    banners = {path.name: content for path, content in built.items() if "banner" in path.name}
    expected = {f"banner-{t}{s}.svg" for t in ("dark", "light") for s in ("", "-compact")}
    assert set(banners) == expected
    for name, content in banners.items():
        assert content == committed(name), name


def test_members_profile_has_a_card_and_a_tile_per_repository() -> None:
    built, _ = assets.build_private(MEMBERS_FIXTURE)
    names = {path.name for path in built if "banner" not in path.name}
    repos = load_repositories(assets.private_data(MEMBERS_FIXTURE))
    assert names == {
        f"{r.name}-{t}{s}.svg" for r in repos for t in ("dark", "light") for s in ("", "-compact")
    }
    assert all(path.parent == assets.private_assets(MEMBERS_FIXTURE) for path in built)


def test_repository_text_that_would_overflow_is_refused() -> None:
    theme = assets.TOKENS.themes["dark"]
    repo = load_repositories(assets.private_data(MEMBERS_FIXTURE))[0]
    long_name = dataclasses.replace(repo, name="a-repository-name-far-too-long")
    with pytest.raises(ValueError, match="wider than"):
        art.repository_card(assets.TOKENS, theme, 1, long_name, Ledger(), "c")
    with pytest.raises(ValueError, match="wider than"):
        art.repository_tile(assets.TOKENS, theme, 1, long_name, Ledger(), "t")
    long_stack = dataclasses.replace(repo, stack="Astro · D1 · Workers · KV · R2 · Queues")
    with pytest.raises(ValueError, match="wider than"):
        art.repository_card(assets.TOKENS, theme, 1, long_stack, Ledger(), "c")
    long_summary = dataclasses.replace(repo, summary=" ".join([repo.summary] * 3))
    with pytest.raises(ValueError, match="keep it to three"):
        art.repository_card(assets.TOKENS, theme, 1, long_summary, Ledger(), "c")


def test_the_banner_spans_the_readme_column() -> None:
    """Without a width the banner stops at 880 px while the 33.33% cards below it stretch."""
    text = (assets.PUBLIC.parent / "README.md").read_text(encoding="utf-8")
    assert '<img alt="Dynamis Group.' in text
    banner = next(line for line in text.splitlines() if 'src="assets/banner-light.svg"' in line)
    assert 'width="100%"' in banner


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
