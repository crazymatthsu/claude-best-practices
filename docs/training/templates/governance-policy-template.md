# AI coding agent usage policy (template)

*Replace the bracketed text. Keep the policy short enough to be read; put detail in the linked standards.
Each requirement names the control that enforces it, so the policy can be audited rather than trusted.*

| Field | Value |
|---|---|
| Policy owner | [CISO or head of platform] |
| Approved by | [CIO] |
| Version, date | [1.0, YYYY-MM-DD] |
| Review cadence | [every 6 months, and after any major Claude Code release] |
| Applies to | [all employees and contractors using Claude Code or other AI coding agents on company code] |

## 1. Purpose and scope

This policy sets the conditions under which AI coding agents may read, modify, run and integrate with company
code and systems. It covers Claude Code in all surfaces: terminal and IDE, CI pipelines, the web, and
SDK-based agents. [Add other tools in scope.]

## 2. Definitions

See the [glossary](../glossary.md). Terms used here: agent, permission rule, hook, managed settings, MCP server,
plugin, headless mode.

## 3. Approved tooling and deployment

| Item | Decision | Enforced by |
|---|---|---|
| Approved agent | Claude Code, version [N] or later | managed settings; software catalogue |
| Deployment endpoint | [Anthropic API via Claude for Enterprise / AWS Bedrock / Google Vertex AI / Microsoft Foundry / LLM gateway at URL] | managed settings; network policy |
| Identity | [SSO; no personal API keys on company devices] | identity provider; managed settings |
| Data retention | [commercial terms; Zero Data Retention where contracted] | contract; endpoint choice |
| Models permitted | [list] | managed settings |

## 4. Data handling

| Data class | May enter the agent's context? | Control |
|---|---|---|
| Source code and internal documentation | yes | default |
| Secrets, keys, tokens, certificates | never | `deny` rules on secret paths and file patterns; secret scanning in CI |
| Customer or personal data | [only synthetic or masked data] | data classification; test fixtures policy |
| Production databases | never with write access; [read-only replicas only, with approval] | MCP allowlist; credential policy |
| Third-party code under restrictive licences | [per legal guidance] | dependency policy |

## 5. Permitted, confirmed and prohibited actions

These map directly to the `allow`, `ask` and `deny` lists in settings.

| Category | Examples | Rule |
|---|---|---|
| Permitted without confirmation | build, test, lint, read-only git, verification scripts | `allow` |
| Requires human confirmation | push, PR creation, edits to build or CI configuration, edits to hooks and settings, edits to API contracts | `ask`, hooks |
| Prohibited | reading secret paths, force push, hard reset, recursive delete, publishing artefacts, bypassing permission prompts | `deny` in managed settings; bypass mode disabled |

## 6. Minimum repository standard

Before an agent is used for real work on a repository, the repository must satisfy the
[readiness checklist](repo-readiness-checklist.md): a lean `CLAUDE.md`, path-scoped rules, allow/ask/deny
settings, the standard hooks, a verification gate that CI also runs, CODEOWNERS on contracts and guardrail
files, and the PR template. [Reference your internal plugin and its minimum version.]

## 7. Integrations (MCP servers)

- Only MCP servers from the approved catalogue may be configured. [Link.] The catalogue is enforced by managed
  settings.
- Project-scoped servers are committed in the repository and reviewed in a pull request.
- Credentials are supplied through environment variables or secret managers, never in files. Tokens are
  read-only and scoped to one project, space or non-production database wherever the provider allows.
- New servers are requested through [process]; security reviews data flow and token scope.

## 8. Human oversight

- Every change reaches the main branch through a pull request reviewed and approved by a human code owner.
  Agents never approve or merge.
- Agents running in CI are read-only or comment-only unless an exception is approved. [Exceptions process.]
- Developers own the code the agent writes. The gate proves it works; the review proves it is right.
- Plans for non-trivial work are reviewed before code is written (plan mode).

## 9. Logging, telemetry and retention

- Telemetry is enabled by managed settings and exported to [monitoring stack]. It records sessions, tokens, cost,
  tool-permission decisions and code-change events per user and team. It does not record prompt or file content
  unless [decision].
- Retention: [period]. Access: [roles].
- Pull requests, CI logs and hook decisions form the audit trail for individual changes.

## 10. Incident reporting

Report suspected secret exposure, unexpected destructive actions, or suspected prompt injection to [contact]
within [time]. Preserve the session transcript. [Link to the incident process.]

## 11. Exceptions

Exceptions to sections 3 to 8 are requested through [process], approved by [role], time-boxed, and recorded.
A standing exception becomes a policy change at the next review.

## 12. Roles

| Role | Responsibility |
|---|---|
| Security | sections 3, 4, 5 (deny lists), 7 (catalogue), 10 |
| Platform and enablement | managed settings deployment, the reference configuration and plugin, telemetry, training |
| Tech leads | repository standard (section 6), CODEOWNERS, contract ownership, monthly pruning |
| Developers | sections 5 and 8 in daily work; report every repeated correction |
| Product | specs with testable acceptance criteria and an explicit out-of-scope list |

## Appendix A: mapping to controls

| Policy clause | Control | Where |
|---|---|---|
| 4 secrets never in context | `deny` rules: `Read(./.env)`, `Read(**/*.pem)`, secret directories | managed settings; `.claude/settings.json` |
| 5 confirmation on push and PR | `ask` rule on `git push`; pre-push gate hook | `.claude/settings.json`, `.claude/hooks/pre-pr-gate.sh` |
| 5 contracts need confirmation | human-confirm hook on `contracts/` | `.claude/hooks/protect-contracts.sh` |
| 6 tests before the PR | Stop hook, gate script, CI, PR template | `.claude/hooks/require-tests-on-stop.sh`, `scripts/verify.sh`, `.github/` |
| 7 approved servers only | MCP allowlist | managed settings |
| 8 human approval | branch protection, CODEOWNERS | Git hosting |
| 9 telemetry | OpenTelemetry settings | managed settings |
