---
name: write-adr
description: Record an architecture or contract decision as an ADR in docs/adr/. Use when choosing between technical options, changing a layer boundary, adding a dependency, or making a breaking contract change.
---

# Write an ADR

1. Next number: `ls docs/adr | sort | tail -1` → increment. File: `docs/adr/NNNN-kebab-title.md`.
2. Copy `docs/adr/template.md`. Fill every section. Keep it to one page.
3. Status starts as `Proposed`. Only a human changes it to `Accepted`.
4. Options: list at least two real alternatives with honest trade-offs.
5. Consequences: include what becomes *harder*, not just what becomes easier.
6. Link it from where it matters (CHANGELOG entry, spec, PR description).
7. Never rewrite an accepted ADR. Supersede it with a new one and mark the old one `Superseded by NNNN`.
