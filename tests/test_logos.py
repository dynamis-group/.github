"""The official logos: svgo may only strip metadata, and the images must nest them unchanged."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from dynamis import assets, logos
from dynamis.theme import ROOT

LOGOS = ROOT / "design" / "logos"
# Everything that decides what a logo looks like. Ids and editor metadata are not on the list.
GEOMETRY = (
    "d",
    "transform",
    "x",
    "y",
    "width",
    "height",
    "x1",
    "y1",
    "x2",
    "y2",
    "fill",
    "stroke",
    "opacity",
    "stop-color",
    "stop-opacity",
    "offset",
    "gradientUnits",
    "viewBox",
    "fill-rule",
    "clip-rule",
    "shape-rendering",
)


def geometry(path: Path) -> list[tuple[str, str, str]]:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    found = []
    for element in root.iter():
        tag = element.tag.split("}")[-1]
        for name in GEOMETRY:
            if name in element.attrib:
                value = re.sub(r"url\(#[^)]+\)", "url(#ref)", element.attrib[name])
                found.append((tag, name, value))
    return sorted(found)


def test_optimised_logos_keep_every_path_shape_and_gradient() -> None:
    sources = sorted((LOGOS / "source").glob("*.svg"))
    assert len(sources) == 12
    for source in sources:
        optimised = LOGOS / "optimised" / source.name
        assert geometry(source) == geometry(optimised), source.name


def test_images_nest_the_logos_unchanged() -> None:
    built, _ = assets.build_public()
    banner = built[assets.PUBLIC / "banner-dark.svg"]
    for name in ("DYNAMIS_GROUP_D_GRAPHIC", "DYNAMIS_GROUP_UNBOLDED_LIGHT"):
        for d in re.findall(r' d="([^"]+)"', logos.load(name).body):
            assert f' d="{d}"' in banner, name
    card = built[assets.PUBLIC / "labs-light.svg"]
    for d in re.findall(r' d="([^"]+)"', logos.load("DYNAMIS_LABS_UNBOLDED_DARK_ACCENT").body):
        assert f' d="{d}"' in card


def test_lockups_follow_the_site_defaults() -> None:
    dark, light = assets.TOKENS.themes["dark"], assets.TOKENS.themes["light"]
    assert logos.lockup_name("group", dark) == "DYNAMIS_GROUP_UNBOLDED_LIGHT"
    assert logos.lockup_name("group", light) == "DYNAMIS_GROUP_UNBOLDED_DARK"
    assert logos.lockup_name("labs", dark) == "DYNAMIS_LABS_UNBOLDED_LIGHT_ACCENT"
