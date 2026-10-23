# Module 03: Context and memory. CLAUDE.md, rules and nested memory

| | |
|---|---|
| **Audience** | tech leads, developers, platform engineers who maintain the reference configuration |
| **Duration** | 60 min (30 min teaching, 30 min workshop) |
| **Prerequisites** | module 01 |
| **Materials** | [`docs/02-claude-md-and-rules.md`](../../02-claude-md-and-rules.md), this repository's `CLAUDE.md`, `.claude/rules/`, `contracts/CLAUDE.md` |

## Learning objectives

1. Explain the memory hierarchy (organisation → user → project → local → nested → path rules) and what loads when.
2. Write a root `CLAUDE.md` under about 50 lines with the five standard parts.
3. Decide, for any piece of information, where it belongs, using the four questions.
4. Recognise the anti-patterns and run a pruning session.

## Topics

1. **The hierarchy.** Organisation-managed `CLAUDE.md` (deployed by IT), `~/.claude/CLAUDE.md` (personal),
   `./CLAUDE.md` (project, committed), `CLAUDE.local.md` (personal, gitignored), `dir/CLAUDE.md` (nested, loads
   when working in that directory), `.claude/rules/*.md` (always, or only for matching `paths:`). `/memory`
   shows what is loaded now.
2. **The five parts of a root `CLAUDE.md`.** One-line identity; the commands (build, fast test loop, single test,
   the gate); the architecture in three lines pointing at the test that enforces it; five to seven
   non-negotiables, each backed by a mechanism; a map of where things are. Nothing the model already knows.
3. **The four questions.** Needed in most sessions? True now and staying true? Could a tool enforce it instead?
   Specific to this repository? Each "no" sends the content somewhere else or deletes it.
4. **Path-scoped rules and nested memory.** `paths:` frontmatter so test rules cost nothing when fixing a
   controller. Nested files for directories with different physics: contracts, generated code, legacy modules,
   shared libraries.
5. **Progressive disclosure.** Link, do not import. Skill descriptions as the only always-on cost. Reference files
   inside skills. Subagents for large reading jobs.
6. **Session hygiene.** One task per session and `/clear`. Plan mode for anything non-trivial. `/context` when
   quality drops. `/compact <focus>` in long tasks. Point at files instead of pasting them.
7. **Standardising across the enterprise.** An organisation-level `CLAUDE.md` of at most ten lines (security
   contact, approved tooling, "never paste secrets or customer data"). A template repository `CLAUDE.md` with
   the five parts. Changes to any `CLAUDE.md` reviewed like code and owned in CODEOWNERS.
8. **Pruning.** Monthly: delete rules the agent follows without being told, merge duplicates, turn repeated
   corrections into a hook or test first and a rule second.

## Key messages

- Every line in always-loaded context costs attention in every session, forever. Make it earn its place.
- A rule that matters gets a mechanism, not capital letters.
- Generate or test what must stay true. Link what is background. Delete what is generic.

## Demo in this repository

1. `/memory` and open [`CLAUDE.md`](../../../CLAUDE.md). Walk through the five parts.
2. Ask the agent to describe `contracts/openapi/orders-api.v1.yaml`. Show that
   [`contracts/CLAUDE.md`](../../../contracts/CLAUDE.md) is now loaded and was not before.
3. Open [`.claude/rules/testing.md`](../../../.claude/rules/testing.md). Point at the `paths:` block.
4. On a scratch copy of a participant's repository, run `/init`, then cut the output by half live, moving
   area-specific content into `.claude/rules/`.

## Governance controls introduced

| Control | Layer | Owner | Enforcement |
|---|---|---|---|
| Organisation `CLAUDE.md` (managed location) | guidance | platform, security | deployed with managed settings; see module 02 for file locations |
| Project `CLAUDE.md` and `.claude/rules/` | guidance | tech leads | reviewed in PRs; path owned in CODEOWNERS |
| Nested `CLAUDE.md` on sensitive directories | guidance | directory owners | reviewed in PRs |
| Template repository `CLAUDE.md` | guidance | platform | the starting point for WF-08 |

## Exercises (30 min)

1. **Cut it in half.** Take a long `CLAUDE.md` (the trainer provides a 300-line example, or use fresh `/init`
   output). Reduce it to under 50 lines plus rule files. Justify every surviving line with the four questions.
2. **Write one rule file** for an area of your codebase (persistence, messaging, UI) with a `paths:` block.
3. **Draft the organisation `CLAUDE.md`** in at most ten lines. Compare drafts; keep only lines every team
   would agree with.

## Common questions

- *"Should we `@import` our style guide?"* No. Point the agent at the formatter and linter instead. Imports
  inline the file every session.
- *"Can developers override project rules?"* They can add personal preferences. Anything that must hold is a
  permission or hook (module 04), and managed settings can lock those.
- *"How do I know what is loaded right now?"* `/memory` for files, `/context` for the budget.

## Further reading

- [`docs/01-context-engineering.md`](../../01-context-engineering.md)
- [`docs/02-claude-md-and-rules.md`](../../02-claude-md-and-rules.md)
- [`docs/11-playbook-java-developers.md`](../../11-playbook-java-developers.md), large-codebase tips
