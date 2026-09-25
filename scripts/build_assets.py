# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "brotli==1.2.0",
#   "fonttools[woff]==4.66.0",
#   "uharfbuzz==0.56.2",
# ]
# ///
"""Build the organisation profile images from design/tokens.json and the official logos.

    uv run scripts/build_assets.py                 # write profile/assets/
    uv run scripts/build_assets.py --check         # fail if profile/assets/ is stale
    uv run scripts/build_assets.py --private DIR   # also build the members-only profile

The members-only profile (dynamis-group/.github-private) opens with the public banner, followed
by a card for each core repository, drawn from that checkout's design/repositories.json. It is
built into ../.github-private/profile/assets whenever that checkout exists.
The build refuses text that fails WCAG AA or renders below the minimum size.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dynamis import assets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--check", action="store_true", help="verify instead of writing")
    parser.add_argument("--private", type=Path, help="checkout of the members-only profile")
    args = parser.parse_args(argv)

    built, ledger = assets.build_public()
    targets = [(built, assets.PUBLIC)]
    default = assets.PRIVATE_DEFAULT
    private = args.private or (default if (default / ".git").exists() else None)
    if private is not None:
        members, members_ledger = assets.build_private(private)
        ledger.entries.extend(members_ledger.entries)
        targets.append((members, assets.private_assets(private)))

    problems = ledger.failures(assets.TOKENS.min_text_px)
    for problem in problems:
        print(f"illegible: {problem}", file=sys.stderr)
    if problems:
        return 1
    if args.check:
        stale = [p for files, folder in targets for p in assets.stale(files, folder)]
        for path in stale:
            print(f"out of date: {path}", file=sys.stderr)
        return 1 if stale else 0
    changed = [p for files, _ in targets for p in assets.write(files)]
    for path in changed:
        print(f"wrote {path}")
    print(f"{sum(len(f) for f, _ in targets)} assets, {len(changed)} changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
