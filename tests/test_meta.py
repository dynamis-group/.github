"""Invariants: pins agree, the profile stays a short signpost, public text stays public."""

from __future__ import annotations

import json
import re
import tomllib

from conftest import ROOT

PUBLIC_DOCS = ("profile/README.md", "README.md", "CONTRIBUTING.md", "SECURITY.md")
SITE_ROUTES = {"/", "/digital/", "/advisory/", "/labs/", "/contact/"}


def inline_dependencies(script: str) -> list[str]:
    text = (ROOT / "scripts" / script).read_text(encoding="utf-8")
    block = re.search(r"^# /// script\n(.*?)^# ///$", text, flags=re.MULTILINE | re.DOTALL)
    assert block, script
    lines = block.group(1).splitlines()
    body = "\n".join(line.removeprefix("# ").removeprefix("#") for line in lines)
    return sorted(tomllib.loads(body)["dependencies"])


def test_pep723_block_matches_pyproject() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert inline_dependencies("build_assets.py") == sorted(project["project"]["dependencies"])


def test_tokens_define_both_themes_and_three_divisions() -> None:
    tokens = json.loads((ROOT / "design" / "tokens.json").read_text(encoding="utf-8"))
    assert set(tokens["themes"]["dark"]) == set(tokens["themes"]["light"])
    assert [d["slug"] for d in tokens["divisions"]] == ["digital", "advisory", "labs"]


def test_every_font_ships_with_its_licence() -> None:
    for font in sorted((ROOT / "design" / "fonts").glob("*.ttf")):
        assert (font.parent / f"OFL-{font.stem.split('-')[0]}.txt").exists(), font.name


def test_profile_is_a_short_signpost() -> None:
    text = (ROOT / "profile" / "README.md").read_text(encoding="utf-8")
    assert len(text.strip().splitlines()) <= 30
    assert "DYNAMIS GROUP PTY LTD · ACN 697 317 605 · Melbourne, Australia" in text
    for rel in re.findall(r'(?:srcset|src)="(assets/[^"]+)"', text):
        assert (ROOT / "profile" / rel).exists(), rel
        twin = rel.replace("-dark", "-light") if "-dark" in rel else rel.replace("-light", "-dark")
        assert (ROOT / "profile" / twin).exists(), twin
    routes = {
        re.sub(r"^https://dynamisgroup\.com\.au", "", url) or "/"
        for url in re.findall(r'href="(https://dynamisgroup\.com\.au[^"]*)"', text)
    }
    assert routes and routes <= SITE_ROUTES


def test_public_text_names_no_private_repository() -> None:
    allowed = {".github", ".github-private"}
    for rel in PUBLIC_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        repos = set(re.findall(r"github\.com/dynamis-group/([\w.-]+)", text))
        assert repos <= allowed, (rel, repos - allowed)
        hosts = set(re.findall(r"https?://([\w.-]+)", text))
        assert all(
            h.endswith(
                ("dynamisgroup.com.au", "github.com", "conventionalcommits.org", "astral.sh")
            )
            for h in hosts
        ), (rel, hosts)
