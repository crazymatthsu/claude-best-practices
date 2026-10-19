---
name: write-spec
description: Turn a feature idea, ticket or conversation into a feature spec with testable acceptance criteria in docs/specs/. Use when a PM or developer describes new functionality that is not yet specified.
---

# Write a feature spec

1. Copy [template.md](template.md) to `docs/specs/<ID>-<kebab-title>.md` (ID from the ticket, e.g. ORD-003).
2. Interview the requester about gaps. Don't invent business rules. Typical gaps: error cases, permissions,
   limits, idempotency, what happens to existing data.
3. Write acceptance criteria as **Given / When / Then**, numbered AC1…ACn. Each must be verifiable by
   a test. "Fast" or "user friendly" are not criteria. "p95 < 200 ms at 50 rps" is.
4. Fill "Contract impact" with the endpoints and fields that change. Mark it additive or breaking if known.
5. Fill "Out of scope" explicitly. It's the main defence against scope creep.
6. Add a Mermaid sequence or state diagram if the flow has more than two actors or states.
7. Status: `Draft`. The PM sets `Ready` once questions are answered. Developers (and Claude) only implement `Ready` specs.
