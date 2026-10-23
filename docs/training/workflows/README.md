# Workflow catalogue

Each card describes a repeatable way of working with Claude Code: the steps, the feature used at each step, the
guardrail active at that moment, and the evidence the workflow leaves behind. Use the cards as lab exercises, as
the "approved ways of working" referenced by your usage policy, and as the shape for your own cards
([template](../templates/workflow-card-template.md)).

| ID | Workflow | Primary roles | Key features | Lab in this repository |
|---|---|---|---|---|
| [WF-01](WF-01-spec-to-pull-request.md) | Spec to pull request | developer, tech lead, product | plan mode, `tdd-feature` and `pr-ready` skills, Stop and pre-push hooks, `code-reviewer` subagent, PR template | yes |
| [WF-02](WF-02-safe-api-contract-change.md) | Safe API contract change | developer, API owner | nested `CLAUDE.md`, `contract-change` skill, `protect-contracts` hook, `contract-guardian` subagent, oasdiff in CI, `write-adr` | yes |
| [WF-03](WF-03-bug-fix-reproduce-first.md) | Bug fix, reproduce first | developer | failing test first, testing rules, Stop hook, gate | yes |
| [WF-04](WF-04-understanding-a-large-codebase.md) | Understanding a large or legacy codebase | developer, architect | Explore subagent, plan mode, `/context`, `/compact`, nested `CLAUDE.md`, `/add-dir` | partly |
| [WF-05](WF-05-ai-assisted-code-review.md) | AI-assisted code review, locally and in CI | tech lead, platform | `code-reviewer` and `contract-guardian` subagents, GitHub Action, headless mode, read-only permissions | partly |
| [WF-06](WF-06-architecture-docs-adrs-perf-reports.md) | Architecture documents, ADRs and performance reports | architect, tech lead | `tech-doc`, `write-adr`, `update-diagrams`, `perf-report`, `confluence-publish` skills, Atlassian MCP | yes |
| [WF-07](WF-07-from-idea-to-testable-spec.md) | From idea to testable spec | product, business analysts | `write-spec` skill, issue-tracker MCP, reading a PR without code | yes |
| [WF-08](WF-08-onboarding-a-repository.md) | Onboarding a repository to governed Claude Code | tech lead, platform | `/init`, rules, settings, hooks, `verify.sh`, CI, CODEOWNERS, readiness checklist | yes |
| [WF-09](WF-09-enterprise-policy-rollout.md) | Enterprise policy rollout | platform, security | managed settings, deny lists, MCP and plugin allowlists, telemetry, staged rollout | organisation level |
| [WF-10](WF-10-headless-and-scheduled-automation.md) | Headless and scheduled automation | platform, tech lead | `claude -p`, tool allowlists, JSON output, CI schedules, read-only credentials | partly |

## Feature × workflow matrix

| Feature | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| `CLAUDE.md`, rules, nested memory | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Plan mode | ✓ | ✓ | | ✓ | | ✓ | | ✓ | | |
| Skills | ✓ | ✓ | ✓ | | | ✓ | ✓ | ✓ | | ✓ |
| Subagents | ✓ | ✓ | | ✓ | ✓ | | | | | ✓ |
| Hooks | ✓ | ✓ | ✓ | | ✓ | | | ✓ | ✓ | ✓ |
| Permissions (allow / ask / deny) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| MCP servers | | | | | ✓ | ✓ | ✓ | | ✓ | ✓ |
| Headless mode and CI | | ✓ | | | ✓ | | | ✓ | | ✓ |
| Plugins and managed settings | | | | | | | | ✓ | ✓ | |
| PR template and CODEOWNERS | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | | |

## How to read a card

1. **Header**: who, when, which features, which guides.
2. **Flow**: one diagram, twelve nodes or fewer.
3. **Steps**: a table with the prompt or action, the feature, and the guardrail active at that step.
4. **Guardrails that fire**: what the developer sees when a control triggers.
5. **Evidence**: what the workflow leaves behind for reviewers and auditors.
6. **Prompts, variations, anti-patterns**: what to type, how to adapt, what to avoid.

## Which human decisions remain

Across all cards, the agent stops for a human at exactly these points: approving a plan, confirming an edit to
a protected file, confirming a push or a PR, and the PR review itself. Everything else is automatic and leaves
a trace. Keep that list short and visible; it is the heart of the governance story.
