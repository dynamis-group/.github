"""Place the official Dynamis logos inside generated images without redrawing them.

Each logo is the svgo-cleaned copy of core-web's public/logos file (design/logos/optimised),
nested as an inner <svg> that keeps its original viewBox, so every path renders exactly as
published. Ids are prefixed per placement so several logos can share one image.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from svgkit.svg import fmt

from .theme import ROOT, Theme

LOGO_DIR = ROOT / "design" / "logos" / "optimised"
_ROOT_TAG = re.compile(r"<svg\b[^>]*>")
_VIEWBOX = re.compile(r'viewBox="0 0 ([\d.]+) ([\d.]+)"')
_NUMBER = re.compile(r"-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?")
_COMMAND = re.compile(r"[A-Za-z]")


@dataclass(frozen=True)
class Logo:
    name: str
    body: str
    view_w: float
    view_h: float
    bbox: tuple[float, float, float, float]  # visible artwork in viewBox units


def _path_points(d: str) -> list[tuple[float, float]]:
    """Coordinates of an absolute-command path (Figma exports only absolute commands)."""
    points: list[tuple[float, float]] = []
    tokens = re.findall(r"[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?", d)
    command = ""
    numbers: list[float] = []
    x = y = 0.0

    def flush() -> None:
        nonlocal x, y
        if command in "HV":
            for value in numbers:
                x, y = (value, y) if command == "H" else (x, value)
                points.append((x, y))
        else:
            for i in range(0, len(numbers) - 1, 2):
                x, y = numbers[i], numbers[i + 1]
                points.append((x, y))

    for item in tokens:
        if _COMMAND.fullmatch(item):
            if item.islower() and item != "z":
                raise ValueError(f"relative path command {item!r} is not supported")
            flush()
            command, numbers = item.upper(), []
        else:
            numbers.append(float(item))
    flush()
    return points


def _bbox(body: str) -> tuple[float, float, float, float]:
    # Artwork only: skip clip-path definitions and the transformed gradient fills they clip.
    visible = re.sub(r"<defs>.*?</defs>", "", body, flags=re.DOTALL)
    visible = re.sub(r'<g clip-path="[^"]*">.*?</g></g>', "", visible, flags=re.DOTALL)
    points: list[tuple[float, float]] = []
    for d in re.findall(r'<path[^>]*\bd="([^"]+)"', visible):
        points.extend(_path_points(d))
    for rect in re.findall(r"<rect\b([^>]*)>", visible):
        if "transform=" in rect:
            continue
        values = dict(re.findall(r'(x|y|width|height)="([^"]+)"', rect))
        if {"x", "y", "width", "height"} <= set(values):
            rx, ry = float(values["x"]), float(values["y"])
            points += [(rx, ry), (rx + float(values["width"]), ry + float(values["height"]))]
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


@lru_cache(maxsize=32)
def load(name: str) -> Logo:
    text = (LOGO_DIR / f"{name}.svg").read_text(encoding="utf-8").strip()
    root = _ROOT_TAG.match(text)
    view = _VIEWBOX.search(text)
    assert root and view, f"unexpected logo file {name}"
    body = text[root.end() : text.rfind("</svg>")]
    return Logo(name, body, float(view.group(1)), float(view.group(2)), _bbox(body))


def mark_name(brand: str) -> str:
    return f"DYNAMIS_{brand.upper()}_D_GRAPHIC"


def lockup_name(brand: str, theme: Theme) -> str:
    """The site's default lockup (LOGO.style 'unbolded', LOGO.accent true) for this ground."""
    text = "LIGHT" if theme.logo_text == "light" else "DARK"
    accent = "" if brand == "group" else "_ACCENT"
    return f"DYNAMIS_{brand.upper()}_UNBOLDED_{text}{accent}"


def _prefix_ids(body: str, prefix: str) -> str:
    body = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}{m.group(1)}"', body)
    return re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{prefix}{m.group(1)})", body)


def place(name: str, *, x: float, y: float, height: float, prefix: str) -> tuple[str, float]:
    """Nest a logo so its visible artwork starts at (x, y) and is ``height`` tall.

    Returns the markup and the artwork's rendered width.
    """
    logo = load(name)
    minx, miny, maxx, maxy = logo.bbox
    scale = height / (maxy - miny)
    markup = (
        f'<svg x="{fmt(x - minx * scale, 3)}" y="{fmt(y - miny * scale, 3)}" '
        f'width="{fmt(logo.view_w * scale, 3)}" height="{fmt(logo.view_h * scale, 3)}" '
        f'viewBox="0 0 {fmt(logo.view_w, 3)} {fmt(logo.view_h, 3)}" fill="none">'
        f"{_prefix_ids(logo.body, prefix)}</svg>"
    )
    return markup, (maxx - minx) * scale


def source_files() -> list[Path]:
    return sorted((ROOT / "design" / "logos" / "source").glob("*.svg"))
