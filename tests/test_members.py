"""The members-only profile, checked when dynamis-group/.github-private sits next to this one.

Its CI checks this repository out beside it and runs these tests there.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest
from dynamis import assets
from dynamis.theme import load_repositories

CHECKOUT = assets.PRIVATE_DEFAULT
pytestmark = pytest.mark.skipif(
    not (CHECKOUT / ".git").exists(), reason="dynamis-group/.github-private is not checked out"
)
FOOTER = "DYNAMIS GROUP PTY LTD · ACN 697 317 605 · Members only"


def readme() -> str:
    return (CHECKOUT / "profile" / "README.md").read_text(encoding="utf-8")


def test_committed_member_images_match_a_fresh_build() -> None:
    built, ledger = assets.build_private(CHECKOUT)
    assert assets.stale(built, assets.private_assets(CHECKOUT)) == []
    assert ledger.failures(assets.TOKENS.min_text_px) == []


def test_every_member_svg_is_clean() -> None:
    for path in sorted(assets.private_assets(CHECKOUT).glob("*.svg")):
        text = path.read_text(encoding="utf-8")
        root = ET.fromstring(text)
        assert root.attrib.get("role") == "img", path.name
        assert not re.search(r"""(?:href|src)\s*=\s*["'](?!#|data:)""", text), path.name


def test_members_readme_opens_with_a_full_width_banner() -> None:
    text = readme()
    assert text.startswith("<picture>")
    banner = next(line for line in text.splitlines() if 'src="assets/banner-light.svg"' in line)
    assert 'width="100%"' in banner
    assert FOOTER in text


def test_members_readme_links_every_repository_card_in_order() -> None:
    text = readme()
    repos = load_repositories(assets.private_data(CHECKOUT))
    row = next(line for line in text.splitlines() if 'width="33.33%"' in line)
    assert row.count('width="33.33%"') == len(repos) == 3
    assert "</a><a " in row and "</a> <a" not in row
    assert re.findall(r'<a href="([^"]+)">', row) == [r.href for r in repos]
    for rel in re.findall(r'(?:srcset|src)="(assets/[^"]+)"', text):
        assert (CHECKOUT / "profile" / rel).exists(), rel
        twin = rel.replace("-dark", "-light") if "-dark" in rel else rel.replace("-light", "-dark")
        assert (CHECKOUT / "profile" / twin).exists(), twin
