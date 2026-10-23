# Module 01: Foundations. What Claude Code is and where risk comes from

| | |
|---|---|
| **Audience** | everyone: executives, platform, security, tech leads, developers, product |
| **Duration** | 45 min (25 min talk, 15 min live demo, 5 min questions) |
| **Prerequisites** | none |
| **Materials** | this repository open in Claude Code; [`docs/01-context-engineering.md`](../../01-context-engineering.md) |

## Learning objectives

After this module, participants can:

1. Describe what Claude Code does during a session (the agentic loop) and on which surfaces it runs.
2. Name the four kinds of action it takes (read, edit, run, call) and the risk attached to each.
3. Explain why written instructions alone are guidance, not control.
4. Use the vocabulary of the rest of the curriculum: context, tool, permission, hook, skill, subagent, MCP.

## Topics

1. **What it is.** A coding agent that runs in the terminal and IDE, in CI (GitHub Actions), in the browser
   (Claude Code on the web) and as a library for custom agents (Agent SDK). Same configuration files everywhere.
2. **The loop.** Read the task → gather context (files, command output, docs) → plan → act with tools → verify
   → iterate. It stops when done, when blocked, or when a human must confirm.
3. **The tools.** File read, edit and write. Shell commands. Web fetch and search. MCP tools for external
   systems. Delegation to subagents. Each tool is a place where a permission rule or hook can attach.
4. **Context as working memory.** Everything loaded competes for attention. The three failure modes on large
   projects are *too much*, *stale* and *unenforced* context, not "it didn't know".
5. **Where risk comes from.** It acts with the developer's own access. It follows the path of least resistance
   when a test and a spec disagree. It is fast, so habits scale. It reads untrusted content (web pages,
   dependencies, issues), which can carry hidden instructions. It can reach other systems through integrations.
6. **Session modes.** Default (asks before changes), plan (read-only planning), accept-edits (file edits run
   without prompts), auto (a classifier decides what to ask about; the starting mode in recent versions unless
   policy pins another), don't-ask (denies anything that would prompt; for unattended runs), bypass (no prompts
   at all, to be disabled centrally), and headless (scripted, non-interactive).
7. **Where governance attaches.** A preview of the control families in modules 02 to 09, each mapped to one
   of the risks above.

## Key messages

- Claude Code operates with the developer's own access unless we constrain it. Constraining it is configuration,
  not persuasion.
- Guidance (markdown) tells the agent what we want. Guarantees (permissions, hooks, tests, CI) make sure it
  happens. Oversight (telemetry, PR evidence) shows that it did.
- The most valuable thing you can give the agent is a fast, reliable way to check its own work. A test suite
  and a verification script beat a longer instruction every time.

## Demo in this repository (15 min)

1. Open Claude Code in the repository root. Run `/memory` and `/context`. Point out how little is loaded:
   a `CLAUDE.md` under 50 lines, skill names and descriptions, nothing else.
2. Ask: *"Read `docs/specs/ORD-002-cancel-order.md` and the `Order` aggregate. Summarise the acceptance
   criteria. Do not write code."* Watch it open files on demand. The Java rules in `.claude/rules/java.md`
   load only when it touches a `src/main` file.
3. Ask it to add a field to `contracts/openapi/orders-api.v1.yaml`. The `protect-contracts` hook turns the edit
   into a question for the human. Decline. Explain that the model did not decide to ask: the harness did.
4. Run `/hooks`, `/permissions` and `/agents` to show the configured controls, then `/clear`.

## Governance controls introduced

| Control | Layer | Where in this repository | Owner |
|---|---|---|---|
| Lean, always-loaded instructions | guidance | [`CLAUDE.md`](../../../CLAUDE.md) | tech lead |
| Permission rules allow / ask / deny | guarantee | [`.claude/settings.json`](../../../.claude/settings.json) | tech lead, platform |
| Human-confirm hook on contract files | guarantee | [`.claude/hooks/protect-contracts.sh`](../../../.claude/hooks/protect-contracts.sh) | API owners |

## Exercises

1. **Risk inventory (10 min, pairs).** List five things the agent could do in *your* repository that would hurt.
   Classify each: would you address it with guidance, a guarantee, or oversight? Keep the list; module 04 turns it
   into rules and hooks.
2. **Vocabulary check.** Questions 1 to 4 in [`knowledge-checks.md`](../knowledge-checks.md).

## Common questions

- *"Does it learn from our code?"* Under commercial terms, prompts and outputs are not used for model training
  by default, and retention is a contractual choice. Module 08 covers deployment options and data handling.
- *"Can it push to main?"* Only if permissions, hooks and branch protection allow it. In this repository a push
  needs a green gate and a human confirmation, and `main` should be protected on the Git host.
- *"A human reviews everything anyway, so why bother?"* Controls make human review tractable: consistent PR
  descriptions, acceptance criteria mapped to tests, and evidence of what was checked before the PR was opened.

## Further reading

- [`docs/01-context-engineering.md`](../../01-context-engineering.md): the four questions and the noise-reduction techniques
- [`docs/README.md`](../../README.md): the mental model diagram
- Official documentation: https://code.claude.com/docs
