"""Place the website's pillar glyphs inside generated images without redrawing them.

design/icons holds the glyphs from core-web's PillarIcon component, each wrapped in the same
<svg> attributes the component renders (24 px grid, 1.5 stroke, round caps and joins). An icon
is nested unchanged; only its colour is set, through the ``color`` its ``currentColor`` reads.
"""

from __future__ import annotations

import re
from functools import lru_cache

from svgkit.svg import fmt

from .theme import ROOT

ICON_DIR = ROOT / "design" / "icons"
_ROOT_TAG = re.compile(r"<svg\b([^>]*)>")
# The component's wrapper, minus xmlns and the 24 px default size, which a placement replaces.
_KEPT = ("viewBox", "fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin")


def names() -> list[str]:
    return sorted(path.stem for path in ICON_DIR.glob("*.svg"))


@lru_cache(maxsize=16)
def load(name: str) -> tuple[str, str]:
    """The icon's kept root attributes and its body, exactly as stored."""
    path = ICON_DIR / f"{name}.svg"
    if not path.exists():
        raise ValueError(f"unknown icon {name!r}; the icons are {', '.join(names())}")
    text = path.read_text(encoding="utf-8").strip()
    root = _ROOT_TAG.match(text)
    assert root, f"unexpected icon file {name}"
    values = dict(re.findall(r'([\w-]+)="([^"]*)"', root.group(1)))
    kept = "".join(f' {key}="{values[key]}"' for key in _KEPT)
    return kept, text[root.end() : text.rfind("</svg>")]


def place(name: str, *, x: float, y: float, size: float, colour: str) -> str:
    """Nest an icon as a ``size`` px square at (x, y), drawn in ``colour``."""
    kept, body = load(name)
    return (
        f'<svg x="{fmt(x)}" y="{fmt(y)}" width="{fmt(size)}" height="{fmt(size)}"'
        f'{kept} color="{colour}">{body}</svg>'
    )
