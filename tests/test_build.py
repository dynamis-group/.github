"""The committed images must equal a fresh build, stay deterministic, and pass hygiene."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from dynamis import assets

SVG = "{http://www.w3.org/2000/svg}"
EXTERNAL = re.compile(r"""(?:href|src)\s*=\s*["'](?!#|data:)|url\(\s*["']?(?!#|data:)|@import""")
KEYFRAMES = re.compile(r"@keyframes\s+[\w-]+\s*\{((?:[^{}]*\{[^{}]*\})*)\s*\}")


def test_committed_images_match_a_fresh_build() -> None:
    built, _ = assets.build_public()
    assert assets.stale(built, assets.PUBLIC) == []


def test_build_is_deterministic() -> None:
    assert assets.build_public()[0] == assets.build_public()[0]


def test_every_string_is_legible() -> None:
    for build in (assets.build_public, lambda: assets.build_private(assets.PUBLIC)):
        _, ledger = build()
        assert ledger.entries
        assert ledger.failures(assets.TOKENS.min_text_px) == []


def test_every_svg_is_clean() -> None:
    files = sorted(assets.PUBLIC.glob("*.svg"))
    assert len(files) == 12
    for path in files:
        text = path.read_text(encoding="utf-8")
        root = ET.fromstring(text)
        assert root.tag == f"{SVG}svg" and "viewBox" in root.attrib, path.name
        assert root.attrib.get("role") == "img", path.name
        assert root.find(f"{SVG}title") is not None and root.find(f"{SVG}desc") is not None
        body = re.sub(r'xmlns(:\w+)?="[^"]*"', "", text)
        assert not EXTERNAL.search(body), f"{path.name} references something outside the file"
        budget = 250_000 if path.name.startswith("banner") else 80_000
        assert len(text.encode()) <= budget, path.name
        for block in KEYFRAMES.findall(text):
            assert set(re.findall(r"([a-z-]+)\s*:", block)) <= {"transform", "opacity"}
        if "@keyframes" in text:
            assert "prefers-reduced-motion:reduce" in text.replace(" ", "")
