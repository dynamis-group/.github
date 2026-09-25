"""The Dynamis images: the profile banner, the division cards and tiles, and the call to action.

Precision first. The only motion is a single hairline that scans the grid and rests; the
official logos are placed untouched and never move, as the brand requires.
"""

from __future__ import annotations

from dataclasses import dataclass

from svgkit.canvas import Canvas
from svgkit.color import Ledger
from svgkit.svg import el, fmt

from . import logos
from .theme import Division, Repository, Theme, Tokens


def _defs(*items: str) -> str:
    return el("defs", None, "".join(items))


def _radial(gid: str, colour: str, opacity: float, cx: float, cy: float, r: float) -> str:
    return el(
        "radialGradient",
        {"id": gid, "gradientUnits": "userSpaceOnUse", "cx": cx, "cy": cy, "r": r},
        el("stop", {"offset": "0", "stop-color": colour, "stop-opacity": fmt(opacity)})
        + el("stop", {"offset": "1", "stop-color": colour, "stop-opacity": "0"}),
    )


def _panel(width: float, height: float, fill: str, stroke: str, radius: float = 16) -> str:
    return el("rect", {"width": width, "height": height, "rx": radius, "fill": fill}) + el(
        "rect",
        {
            "x": 0.5,
            "y": 0.5,
            "width": width - 1,
            "height": height - 1,
            "rx": radius - 0.5,
            "fill": "none",
            "stroke": stroke,
        },
    )


def _grid(
    width: float, height: float, theme: Theme, cx: float, cy: float, rx: float, ry: float
) -> str:
    """The site's 64 px hairline grid, faded out by an elliptical mask like its hero."""
    pattern = el(
        "pattern",
        {"id": "gp", "width": 64, "height": 64, "patternUnits": "userSpaceOnUse", "x": 0, "y": 0},
        el("path", {"d": "M64 0V64M0 64H64", "fill": "none", "stroke": theme.line}),
    )
    fade = el(
        "radialGradient",
        {
            "id": "gf",
            "gradientUnits": "userSpaceOnUse",
            "cx": cx,
            "cy": cy,
            "r": rx,
            "gradientTransform": (
                f"translate({fmt(cx)} {fmt(cy)}) scale(1 {fmt(ry / rx, 4)}) "
                f"translate({fmt(-cx)} {fmt(-cy)})"
            ),
        },
        el("stop", {"offset": "0.4", "stop-color": "#fff"})
        + el("stop", {"offset": "1", "stop-color": "#000"}),
    )
    mask = el(
        "mask", {"id": "gm"}, el("rect", {"width": width, "height": height, "fill": "url(#gf)"})
    )
    return _defs(pattern, fade, mask) + el(
        "rect", {"width": width, "height": height, "fill": "url(#gp)", "mask": "url(#gm)"}
    )


def _scan_css(travel: float, loop: float) -> str:
    return (
        ".sc{opacity:0;animation:sc "
        f"{fmt(loop)}s ease-in-out infinite}}"
        "@keyframes sc{0%,55%{transform:none;opacity:0}58%{opacity:.55}"
        f"76%{{opacity:.55}}80%,100%{{transform:translateY({fmt(travel)}px);opacity:0}}}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    )


def lockup(
    brand: str, theme: Theme, *, x: float, y: float, mark_h: float, prefix: str
) -> tuple[str, float]:
    """D-graphic plus wordmark, side by side, as core-web's Logo component lays them out."""
    mark, mark_w = logos.place(logos.mark_name(brand), x=x, y=y, height=mark_h, prefix=f"{prefix}m")
    cap = mark_h * 0.4
    word, word_w = logos.place(
        logos.lockup_name(brand, theme),
        x=x + mark_w + mark_h * 0.36,
        y=y + (mark_h - cap) / 2,
        height=cap,
        prefix=f"{prefix}w",
    )
    return mark + word, mark_w + mark_h * 0.36 + word_w


@dataclass(frozen=True)
class BannerLayout:
    width: float
    height: float
    pad: float
    mark_h: float
    headline_size: float
    headline_y: float
    body_size: float
    body_y: float
    body_width: float
    leading: float
    mobile: bool


BANNER_WIDE = BannerLayout(880, 320, 48, 40, 44, 164, 17, 222, 560, 26, False)
BANNER_COMPACT = BannerLayout(400, 320, 24, 32, 34, 124, 16, 200, 352, 24, True)


def banner(tokens: Tokens, theme: Theme, layout: BannerLayout, ledger: Ledger, asset: str) -> str:
    site = tokens.site
    f = tokens.fonts
    scale = (
        tokens.min_scale(layout.width)
        if layout.mobile
        else min(1.0, tokens.desktop_px / layout.width)
    )
    c = Canvas(asset, layout.width, layout.height, ledger=ledger, bg=theme.bg, min_scale=scale)
    c.style("h", f.sans_medium, layout.headline_size, theme.fg)
    c.style("hm", f.sans_medium, layout.headline_size, theme.muted)
    c.style("b", f.sans, layout.body_size, theme.fg_dim)
    w, h, pad = layout.width, layout.height, layout.pad
    glow_x = w * 0.78
    parts = [
        _defs(_radial("gl", theme.brand, 0.16, glow_x, -40, w * 0.5)),
        _panel(w, h, theme.bg, theme.line),
        el("rect", {"width": w, "height": h, "rx": 16, "fill": "url(#gl)"}),
        _grid(w, h, theme, glow_x, 0, w * 0.46, h * 0.9),
        el(
            "g",
            {"class": "sc"},
            el("path", {"d": f"M{fmt(w * 0.42)} 0.5H{fmt(w - 1)}", "stroke": theme.brand}),
        ),
    ]
    mark, _ = lockup("group", theme, x=pad, y=pad, mark_h=layout.mark_h, prefix="g")
    parts.append(mark)
    first, second = site.headline
    y = layout.headline_y
    if layout.mobile:
        parts.append(c.tracked(first, pad, y, "h", -0.03))
        parts.append(c.tracked(second, pad, y + layout.headline_size * 1.05, "hm", -0.03))
        body_top = y + layout.headline_size * 1.05 + 44
    else:
        parts.append(c.tracked(first, pad, y, "h", -0.03))
        first_w = c.measure(first, "h", -0.03)
        parts.append(c.tracked(second, pad + first_w + layout.headline_size * 0.26, y, "hm", -0.03))
        body_top = layout.body_y
    for i, line in enumerate(c.wrap(site.description, "b", layout.body_width)):
        parts.append(c.text(line, pad, body_top + i * layout.leading, "b"))
    desc = f"{site.name}. {first} {second} {site.description}"
    return c.render(
        title=site.name, desc=desc, body="".join(parts), extra_css=_scan_css(h - 1, tokens.loop_s)
    )


# The three division images sit side by side at a third of the row each, with no space between
# them, so the row lines up with the banner at any width. Each image carries its share of the
# gutters: the outer cards sit flush with the banner's edges.
ROW_W = BANNER_WIDE.width
CARD_GAP, CARD_H = 16, 248
# The banner's line box already leaves about 9 px below it; this tops the vertical gap up to the
# gutter between the cards.
CARD_TOP = 7
CARD_W = ROW_W / 3
CARD_VISIBLE = (ROW_W - 2 * CARD_GAP) / 3
# On a phone (the README's max-width: 600px sources) the same third of the row is too narrow
# for a card, so each division becomes a tile: its mark, its name and what it does.
TILE_GAP, TILE_H = 8, 116


def _slot(position: int, gap: float) -> float:
    """Left edge of the visible card in its image, for the 0th, 1st or 2nd image of the row."""
    return position * gap / 3


def _arrow(cx: float, cy: float, colour: str) -> str:
    return el(
        "path",
        {
            "d": (
                f"M{fmt(cx - 5)} {fmt(cy)}H{fmt(cx + 5)}"
                f"M{fmt(cx + 1)} {fmt(cy - 4)}L{fmt(cx + 5)} {fmt(cy)}"
                f"L{fmt(cx + 1)} {fmt(cy + 4)}"
            ),
            "fill": "none",
            "stroke": colour,
            "stroke-width": "1.5",
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
        },
    )


def _card_panel(x: float, width: float, height: float, radius: float, theme: Theme) -> str:
    return el(
        "rect", {"x": x, "width": width, "height": height, "rx": radius, "fill": theme.surface}
    ) + el(
        "rect",
        {
            "x": x + 0.5,
            "y": 0.5,
            "width": width - 1,
            "height": height - 1,
            "rx": radius - 0.5,
            "fill": "none",
            "stroke": theme.line,
        },
    )


def division_card(
    tokens: Tokens, theme: Theme, index: int, division: Division, ledger: Ledger, asset: str
) -> str:
    f = tokens.fonts
    x0, w = _slot(index - 1, CARD_GAP), CARD_VISIBLE
    c = Canvas(
        asset,
        CARD_W,
        CARD_TOP + CARD_H,
        ledger=ledger,
        bg=theme.surface,
        min_scale=min(1.0, tokens.desktop_px / ROW_W),
    )
    c.style("e", f.sans_medium, 13, theme.muted)
    c.style("p", f.sans, 15, theme.fg_dim)
    c.style("l", f.sans_medium, 14, theme.fg_dim)
    parts = [
        _defs(_radial("dg", division.glow, 0.14, x0 + w - 24, -8, 150)),
        _card_panel(x0, w, CARD_H, 16, theme),
        el("rect", {"x": x0, "width": w, "height": CARD_H, "rx": 16, "fill": "url(#dg)"}),
        c.tracked(f"{index:02d} / {division.tag.upper()}", x0 + 24, 44, "e", 0.14),
    ]
    mark, _ = lockup(division.slug, theme, x=x0 + 24, y=68, mark_h=28, prefix="d")
    parts.append(mark)
    for i, line in enumerate(c.wrap(division.positioning, "p", w - 48)):
        parts.append(c.text(line, x0 + 24, 136 + i * 22, "p"))
    # "Learn more" with the site's round arrow button, bottom right.
    cx, cy = x0 + w - 24 - 16, 208
    parts.append(c.text("Learn more", cx - 16 - 10, 213, "l", anchor="end"))
    parts.append(
        el("circle", {"cx": cx, "cy": cy, "r": 16, "fill": theme.fg, "fill-opacity": "0.06"})
    )
    parts.append(_arrow(cx, cy, theme.fg_dim))
    desc = f"{division.name} ({division.tag}): {division.positioning} Learn more at {division.href}"
    body = el("g", {"transform": f"translate(0 {CARD_TOP})"}, "".join(parts))
    return c.render(title=division.name, desc=desc, body=body)


def division_tile(
    tokens: Tokens, theme: Theme, index: int, division: Division, ledger: Ledger, asset: str
) -> str:
    """The phone version of a division card: a third of a 324 px row, drawn at 1:1."""
    f = tokens.fonts
    width = tokens.mobile_px / 3
    visible = (tokens.mobile_px - 2 * TILE_GAP) / 3
    x0 = _slot(index - 1, TILE_GAP)
    c = Canvas(asset, width, TILE_H, ledger=ledger, bg=theme.surface, min_scale=1)
    c.style("n", f.sans_medium, 15, theme.fg)
    c.style("t", f.sans, 12, theme.muted)
    parts = [
        _defs(_radial("dg", division.glow, 0.16, x0 + visible - 8, -8, 90)),
        _card_panel(x0, visible, TILE_H, 12, theme),
        el("rect", {"x": x0, "width": visible, "height": TILE_H, "rx": 12, "fill": "url(#dg)"}),
    ]
    mark, _ = logos.place(logos.mark_name(division.slug), x=x0 + 12, y=14, height=22, prefix="t")
    parts.append(mark)
    parts.append(_arrow(x0 + visible - 18, 25, theme.fg_dim))
    parts.append(c.text(division.name.removeprefix("Dynamis "), x0 + 12, 66, "n"))
    for i, line in enumerate(c.wrap(division.tag, "t", visible - 24)):
        parts.append(c.text(line, x0 + 12, 86 + i * 15, "t"))
    desc = f"{division.name} ({division.tag}): {division.positioning} Learn more at {division.href}"
    return c.render(title=division.name, desc=desc, body="".join(parts))


def _fits(c: Canvas, content: str, style: str, width: float) -> None:
    """Refuse data-driven text that would overflow its card rather than clip it."""
    if c.measure(content, style) > width:
        raise ValueError(f"{c.asset}: {content!r} is wider than {fmt(width)} px")


def repository_card(
    tokens: Tokens, theme: Theme, index: int, repo: Repository, ledger: Ledger, asset: str
) -> str:
    """A members-only card for one repository, on the same grid as the division cards."""
    f = tokens.fonts
    x0, w = _slot(index - 1, CARD_GAP), CARD_VISIBLE
    c = Canvas(
        asset,
        CARD_W,
        CARD_TOP + CARD_H,
        ledger=ledger,
        bg=theme.surface,
        min_scale=min(1.0, tokens.desktop_px / ROW_W),
    )
    c.style("e", f.sans_medium, 13, theme.muted)
    c.style("n", f.mono, 24, theme.fg)
    c.style("p", f.sans, 15, theme.fg_dim)
    c.style("s", f.mono, 13, theme.muted)
    parts = [
        _defs(_radial("dg", theme.brand, 0.12, x0 + w - 24, -8, 150)),
        _card_panel(x0, w, CARD_H, 16, theme),
        el("rect", {"x": x0, "width": w, "height": CARD_H, "rx": 16, "fill": "url(#dg)"}),
        c.tracked(f"{index:02d} / {repo.tag.upper()}", x0 + 24, 44, "e", 0.14),
        c.text(repo.name, x0 + 24, 92, "n"),
    ]
    _fits(c, repo.name, "n", w - 48)
    _fits(c, repo.stack, "s", w - 48 - 32 - 16)
    summary = c.wrap(repo.summary, "p", w - 48)
    if len(summary) > 3:
        raise ValueError(f"{asset}: the summary runs to {len(summary)} lines; keep it to three")
    for i, line in enumerate(summary):
        parts.append(c.text(line, x0 + 24, 132 + i * 22, "p"))
    cx, cy = x0 + w - 24 - 16, 208
    parts.append(c.text(repo.stack, x0 + 24, 212, "s"))
    parts.append(
        el("circle", {"cx": cx, "cy": cy, "r": 16, "fill": theme.fg, "fill-opacity": "0.06"})
    )
    parts.append(_arrow(cx, cy, theme.fg_dim))
    desc = f"{repo.name} ({repo.tag}): {repo.summary} Built with {repo.stack}. Open {repo.href}"
    body = el("g", {"transform": f"translate(0 {CARD_TOP})"}, "".join(parts))
    return c.render(title=repo.name, desc=desc, body=body)


def repository_tile(
    tokens: Tokens, theme: Theme, index: int, repo: Repository, ledger: Ledger, asset: str
) -> str:
    """The phone version of a repository card, drawn like the division tiles."""
    f = tokens.fonts
    width = tokens.mobile_px / 3
    visible = (tokens.mobile_px - 2 * TILE_GAP) / 3
    x0 = _slot(index - 1, TILE_GAP)
    c = Canvas(asset, width, TILE_H, ledger=ledger, bg=theme.surface, min_scale=1)
    c.style("i", f.mono, 12, theme.muted)
    c.style("n", f.mono, 13, theme.fg)
    c.style("t", f.sans, 12, theme.muted)
    parts = [
        _defs(_radial("dg", theme.brand, 0.14, x0 + visible - 8, -8, 90)),
        _card_panel(x0, visible, TILE_H, 12, theme),
        el("rect", {"x": x0, "width": visible, "height": TILE_H, "rx": 12, "fill": "url(#dg)"}),
        c.text(f"{index:02d}", x0 + 12, 29, "i"),
        _arrow(x0 + visible - 18, 25, theme.fg_dim),
        c.text(repo.name, x0 + 12, 66, "n"),
    ]
    _fits(c, repo.name, "n", visible - 24)
    for i, line in enumerate(c.wrap(repo.tag, "t", visible - 24)):
        parts.append(c.text(line, x0 + 12, 86 + i * 15, "t"))
    desc = f"{repo.name} ({repo.tag}): {repo.summary} Open {repo.href}"
    return c.render(title=repo.name, desc=desc, body="".join(parts))


CTA_W, CTA_H = 176, 48


def cta(tokens: Tokens, theme: Theme, ledger: Ledger, asset: str) -> str:
    c = Canvas(asset, CTA_W, CTA_H, ledger=ledger, bg=theme.fg, min_scale=1)
    c.style("c", tokens.fonts.sans_medium, 16, theme.bg)
    label = "Get in touch"
    label_w = c.measure(label, "c")
    x = (CTA_W - label_w - 20) / 2
    parts = [
        el("rect", {"width": CTA_W, "height": CTA_H, "rx": CTA_H / 2, "fill": theme.fg}),
        c.text(label, x, 29.5, "c"),
        el(
            "path",
            {
                "d": (
                    f"M{fmt(x + label_w + 8)} 24H{fmt(x + label_w + 20)}"
                    f"M{fmt(x + label_w + 15)} 19L{fmt(x + label_w + 20)} 24"
                    f"L{fmt(x + label_w + 15)} 29"
                ),
                "fill": "none",
                "stroke": theme.bg,
                "stroke-width": "1.6",
                "stroke-linecap": "round",
                "stroke-linejoin": "round",
            },
        ),
    ]
    return c.render(title=label, desc="Get in touch with Dynamis Group.", body="".join(parts))
