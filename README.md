# dynamis-group/.github

The organisation's public profile, and the defaults every Dynamis repository inherits when it
doesn't have its own.

| Path | What it holds |
|---|---|
| `profile/README.md` | The organisation profile: the banner, the three divisions, and a way to get in touch. |
| `profile/assets/` | The profile's images. They're generated, so don't edit them by hand. |
| `CONTRIBUTING.md`, `SECURITY.md` | The default contributing guide and security policy. |
| `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` | Default issue forms and pull request template. |
| `design/` | Brand tokens, fonts and the official logos the images are built from. |
| `scripts/`, `tests/` | The image build and the checks that keep it honest. |

## Rebuilding the images

You need [uv](https://docs.astral.sh/uv/). From the repository root:

```bash
uv sync                                  # dev environment from uv.lock
uv run scripts/build_assets.py           # regenerate profile/assets/
uv run scripts/build_assets.py --check   # what CI runs: fail if anything is stale
uv run pytest && uv run ruff check && uv run mypy
```

When `dynamis-group/.github-private` is checked out next to this repository, the same build
writes the members-only banner into it (`--private DIR` points it somewhere else).

The build refuses text that fails WCAG AA contrast, or that would render smaller than 12 px on
a phone. Every image is checked for a `viewBox`, a title and description, no external
references, and motion limited to `transform` and `opacity` with a reduced-motion fallback.

## Where the brand comes from

- Colour and type come from the Dynamis website's stylesheet, and the copy and divisions from
  its site configuration. When those change, update `design/tokens.json` and rebuild.
- Fonts are Geist and JetBrains Mono, unmodified from `google/fonts`, each with its SIL OFL
  licence. The images embed renamed subsets. The website's licensed display faces are never
  embedded here, because these files are public.
- The logos in `design/logos/source/` are the official files. `design/logos/svgo.config.mjs`
  strips editor metadata and unused ids without touching geometry (a test compares every path,
  shape and gradient), and the images nest them unchanged. Never redraw a logo.
