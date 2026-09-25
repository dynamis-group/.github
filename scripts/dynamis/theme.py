"""Load design/tokens.json into typed objects shared by every Dynamis renderer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from svgkit import fonts

ROOT = Path(__file__).resolve().parents[2]
TOKENS = ROOT / "design" / "tokens.json"
FONT_DIR = ROOT / "design" / "fonts"


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str
    surface: str
    surface_2: str
    line: str
    line_strong: str
    fg: str
    fg_dim: str
    muted: str
    brand: str
    brand_2: str
    logo_text: str  # "light" (white wordmark, for dark grounds) or "dark"


@dataclass(frozen=True)
class Division:
    slug: str
    name: str
    tag: str
    accent: str
    glow: str
    positioning: str
    href: str


@dataclass(frozen=True)
class Site:
    name: str
    legal_name: str
    acn: str
    locality: str
    url: str
    contact: str
    headline: tuple[str, str]
    description: str


@dataclass(frozen=True)
class Fonts:
    sans: fonts.FontFace
    sans_medium: fonts.FontFace
    mono: fonts.FontFace


@dataclass(frozen=True)
class Tokens:
    themes: dict[str, Theme]
    site: Site
    divisions: tuple[Division, ...]
    fonts: Fonts
    desktop_px: float
    mobile_px: float
    min_text_px: float
    loop_s: float

    def min_scale(self, width: float) -> float:
        return min(1.0, self.mobile_px / width)


_ALIASES = {"sans": "s", "sans_medium": "t", "mono": "m"}


def _face(role: str, spec: dict[str, Any]) -> fonts.FontFace:
    return fonts.FontFace(
        alias=_ALIASES[role],
        path=FONT_DIR / str(spec["file"]),
        weight=int(spec["weight"]),
        axes=tuple(sorted((str(k), float(v)) for k, v in spec.get("axes", {}).items())),
    )


def load(path: Path = TOKENS) -> Tokens:
    data = json.loads(path.read_text(encoding="utf-8"))
    themes = {name: Theme(name=name, **values) for name, values in data["themes"].items()}
    site = data["site"]
    types = data["type"]
    return Tokens(
        themes=themes,
        site=Site(**{**site, "headline": tuple(site["headline"])}),
        divisions=tuple(Division(**d) for d in data["divisions"]),
        fonts=Fonts(**{role: _face(role, spec) for role, spec in types.items()}),
        desktop_px=float(data["layout"]["desktop_content_px"]),
        mobile_px=float(data["layout"]["mobile_content_px"]),
        min_text_px=float(data["layout"]["min_text_px"]),
        loop_s=float(data["motion"]["loop_s"]),
    )
