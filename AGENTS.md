# AGENTS.md

This project uses docs-driven development. Sources of truth live in `docs/`.
Read `docs/SPEC.md` first, then `docs/ROADMAP.md` for current progress.
Update `docs/DECISIONS.md` with a D-XXX entry whenever you make a non-trivial
trade-off, and never silently change behaviour declared in SPEC.

Generated reports belong under `docs/_generated/docdev/`, not in the four
source-of-truth documents.

Deterministic work belongs in the `docdev` CLI. The skill should stay the
decision layer: workflow, judgment, prompts, and boundaries.
