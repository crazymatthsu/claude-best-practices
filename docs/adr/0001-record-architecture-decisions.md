# 0001: Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-09-30
- **Deciders:** tech lead

## Context
Humans and Claude both change this codebase. Without a written record, Claude can't know why something is the way
it is, and it may "fix" a deliberate decision. New team members have the same problem.

## Options considered
1. **Wiki pages**: easy to write, but they live outside the repo, drift from the code, and Claude can't see them.
2. **ADRs in `docs/adr/`**: versioned with the code, reviewed in PRs, and readable by Claude on demand.

## Decision
Use lightweight ADRs in `docs/adr/` (template: `docs/adr/template.md`, skill: `write-adr`).
Accepted ADRs are immutable. Change a decision by superseding it.

## Consequences
- Easier: onboarding, reviews, Claude understanding intent ("see ADR-0002").
- Harder: a small amount of writing for each significant decision.
