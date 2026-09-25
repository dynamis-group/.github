# Contributing to Dynamis Group repositories

This is the default guide for every repository in the organisation, for staff and contractors
alike. Each repository's own README (and CLAUDE.md, where there is one) has the commands and
conventions specific to it, and wins wherever the two differ. Internal detail, like how client
work is set up, is on the [members-only profile](https://github.com/dynamis-group/.github-private/blob/main/profile/README.md).

## Branches and commits

- Branch off the default branch, and keep one piece of work per branch.
- Write commit messages as [Conventional Commits](https://www.conventionalcommits.org/):
  `feat: …`, `fix: …`, `docs: …`, `test: …`.
- Never amend or force-push a shared branch. A fix is a new commit, and history stays linear.
- Commit messages carry no AI attribution: no `Co-Authored-By:` or "Generated with" trailers.

## Tests first

Write the failing test before the code that makes it pass, then run the repository's own
checks (lint, types, tests, build) before you push. Behaviour you can't test with a unit test
still gets a test: an end-to-end spec written alongside the change, not after it.

## Review

Every change goes through three stages, in order:

1. The implementer builds it, test-first.
2. A spec-compliance review checks it does what was asked, no more and no less.
3. A code-quality review checks it's something we're happy to maintain.

## Secrets and client work

- Secrets never go in a repository, not even a private one. Use the password manager and each
  repository's documented secret store. `.env` files stay local; commit a `.env.example`.
- Client website repositories are named `client-<shortname>-website`.
- Clients are never named in public: not in public repositories, issues, commit messages or
  pull request titles.

## Security

Report vulnerabilities privately, as [SECURITY.md](SECURITY.md) describes. Never in an issue.
