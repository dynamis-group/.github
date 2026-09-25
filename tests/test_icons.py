"""The website's pillar glyphs: stored as the site renders them, and nested unchanged."""

from __future__ import annotations

import dataclasses
import re
import xml.etree.ElementTree as ET

import pytest
from conftest import MEMBERS_FIXTURE
from dynamis import art, assets, icons
from dynamis.theme import load_repositories
from svgkit.color import Ledger, contrast

SVG = "{http://www.w3.org/2000/svg}"
# PillarIcon.astro's wrapper, which every stored glyph carries unchanged.
WRAPPER = {
    "width": "24",
    "height": "24",
    "viewBox": "0 0 24 24",
    "fill": "none",
    "stroke": "currentColor",
    "stroke-width": "1.5",
    "stroke-linecap": "round",
    "stroke-linejoin": "round",
}
SHAPES = {"path", "rect", "circle", "line", "polyline", "polygon"}


def test_every_icon_is_a_stroked_glyph_on_the_sites_grid() -> None:
    names = icons.names()
    assert len(names) == 10
    for name in names:
        root = ET.fromstring((icons.ICON_DIR / f"{name}.svg").read_text(encoding="utf-8"))
        assert root.attrib == WRAPPER, name
        children = list(root)
        assert children and {child.tag.removeprefix(SVG) for child in children} <= SHAPES, name
        for child in children:
            assert child.attrib.get("fill", "currentColor") == "currentColor", name
            assert "stroke" not in child.attrib or child.attrib["stroke"] == "none", name


def test_cards_and_tiles_nest_each_icon_unchanged() -> None:
    built, _ = assets.build_private(MEMBERS_FIXTURE)
    target = assets.private_assets(MEMBERS_FIXTURE)
    for repo in load_repositories(assets.private_data(MEMBERS_FIXTURE)):
        _, body = icons.load(repo.icon)
        for suffix in ("", "-compact"):
            image = built[target / f"{repo.name}-dark{suffix}.svg"]
            assert body in image, (repo.name, suffix)
            assert re.search(r'<svg x="[\d.]+" y="[\d.]+" width="(20|16)"', image), repo.name


def test_an_unknown_icon_is_refused() -> None:
    theme = assets.TOKENS.themes["dark"]
    repo = load_repositories(assets.private_data(MEMBERS_FIXTURE))[0]
    with pytest.raises(ValueError, match="unknown icon"):
        art.repository_card(
            assets.TOKENS, theme, 1, dataclasses.replace(repo, icon="nope"), Ledger(), "c"
        )


def test_the_glyph_stands_out_from_its_tile() -> None:
    """WCAG 1.4.11: a meaningful graphic needs 3:1 against what's behind it."""
    for theme in assets.TOKENS.themes.values():
        assert contrast(theme.fg_dim, theme.surface_2) >= 3, theme.name
