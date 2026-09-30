# 10: Documentation and diagrams

Docs serve two readers: **people** (onboarding, decisions, reviews) and **Claude** (on-demand context).
Both suffer from stale docs. The approach here: few docs, close to the code, diagrams as text, and updates as part of the PR.

## What docs exist, and who owns them

| Doc | Purpose | Owner | Changes when |
|---|---|---|---|
| `CLAUDE.md` + `.claude/rules/` | instructions for Claude | tech lead | conventions change |
| `docs/architecture/overview.md` | C4-style context/containers/components + key flows | tech lead | boundaries/flows change |
| `docs/adr/NNNN-*.md` | decisions + rationale, immutable once accepted | author + tech lead | a decision is made |
| `docs/specs/<ID>-*.md` | what to build: ACs, out of scope | PM | requirements change |
| `contracts/CHANGELOG.md` | contract history | API owners | any contract change |
| `docs/NN-*.md` | this guide | platform/enablement | practices change |

## Diagrams as code (Mermaid)

Mermaid renders on GitHub/GitLab, diffs in PRs, and **Claude can read and write it**. It's the best format when an AI co-maintains docs.

| Question | Diagram | Example |
|---|---|---|
| What are the parts and who talks to whom? | `flowchart` (C4-ish) | [architecture/overview.md](architecture/overview.md) |
| What happens on a request? | `sequenceDiagram` | cancel flow in [overview.md](architecture/overview.md#cancel-order-flow-ord-002) |
| What states can X be in? | `stateDiagram-v2` | order lifecycle in [overview.md](architecture/overview.md#order-lifecycle) |
| How is the data shaped? | `classDiagram` / `erDiagram` | domain model in [overview.md](architecture/overview.md#domain-model) |
| What is the process? | `flowchart` | [07 contract change](07-contracts.md) |

Rules (from [`.claude/rules/docs.md`](../.claude/rules/docs.md) and the [`update-diagrams`](../.claude/skills/update-diagrams/SKILL.md) skill):

- Derive diagrams **from code**, and use the code's names.
- Keep each diagram to 12 nodes or fewer. Split rather than cram.
- Update them in the **same PR** as the code (the PR template has a checkbox).

## Keeping docs true

- **Executable docs beat prose:** the layer diagram is backed by `ArchitectureTest`, the state diagram by `OrderTest`, the API docs by the OpenAPI contract and `OrdersApiContractIT`.
- **ADRs are append-only**, so they never go stale. They're history.
- **Ask Claude to audit:** "Compare docs/architecture/overview.md to the code and list discrepancies" is a great periodic task (or a scheduled headless job).

## Useful prompts

- "Use the update-diagrams skill: the cancel flow changed, update the sequence diagram."
- "Generate a state diagram for `Order` from the code and check it against overview.md."
- "Write an ADR for moving from the in-memory repository to Postgres. Give two alternatives."
