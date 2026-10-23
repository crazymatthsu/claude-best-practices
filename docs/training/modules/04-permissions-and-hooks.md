# Module 04: Permissions and hooks. Deterministic guardrails

| | |
|---|---|
| **Audience** | platform engineers, tech leads, developers |
| **Duration** | 90 min (45 min teaching, 45 min lab) |
| **Prerequisites** | modules 01 and 02 |
| **Materials** | [`docs/05-hooks-and-permissions.md`](../../05-hooks-and-permissions.md), [`.claude/settings.json`](../../../.claude/settings.json), [`.claude/hooks/`](../../../.claude/hooks/) |

> **Version note.** Mode names, rule syntax and hook events were checked against the official documentation in
> October 2026. Check the permissions and hooks pages for your installed version before teaching.

## Learning objectives

1. Choose a default permission mode for the organisation and explain each mode's risk.
2. Write allow, ask and deny rules and predict how they are evaluated.
3. Explain hook events, exit codes and JSON output, and read the three hooks in this repository.
4. Lock down hooks and permissions at the organisation level without breaking repository guardrails.

## Topics

### 1. Permission modes

| Mode | Behaviour | Governance stance |
|---|---|---|
| `default` (shown as Manual) | asks before file changes and commands not on the allow list | the baseline for interactive work |
| `acceptEdits` | file edits run without prompts; commands still ask | fine inside a repository with a gate |
| `plan` | read-only; the agent proposes a plan | required for non-trivial work before code |
| `auto` | a classifier reviews actions and prompts only for risky ones | convenient; pin or disable by policy |
| `dontAsk` | denies anything that would prompt | right for unattended runs |
| `bypassPermissions` | no prompts at all | disable centrally |

Terminal and VS Code sessions start in `auto` by default from v2.1.283. Organisations that require a human on
every prompt set `permissions.defaultMode: "default"` in managed settings. Kill switches:
`permissions.disableBypassPermissionsMode: "disable"` and `permissions.disableAutoMode: "disable"`.
Headless (`claude -p`) and the Agent SDK start in `default`.

### 2. Rules and how they are evaluated

- Evaluation order: **deny, then ask, then allow**. First match wins; an allow cannot carve an exception out of a
  deny. Deny rules apply in every mode, including bypass.
- Syntax: `Bash(./gradlew:*)` or `Bash(npm run *)`, `Read(./.env)`, `Edit(/src/**)` (anchored to the settings
  file's root), `WebFetch(domain:*.example.com)`, `mcp__<server>__*`. Path rules work with `Edit` and `Read`;
  `Write`, `Glob` and `NotebookEdit` path rules never match.
- `permissions.additionalDirectories` grants file access only; it loads no configuration from those directories.
- Limit: Bash rules match command text. `Bash(curl *)` does not match `/usr/bin/curl` or `sh -c 'curl …'`. For
  network enforcement use the sandbox's domain allowlist (module 08), not Bash patterns.

### 3. The three lists in this repository

| List | Content | Why |
|---|---|---|
| `allow` | `./gradlew`, `scripts/verify.sh`, the check scripts, read-only git, `git add`, `git commit` | safe and frequent; fewer prompts mean fewer rubber-stamp approvals |
| `ask` | `git push`, edits to `build.gradle.kts`, `settings.gradle.kts`, `gradle/**`, `.github/**`, `.claude/settings.json`, `.claude/hooks/**` | anything that changes shared state or the guardrails themselves |
| `deny` | `.env` files, `secrets/**`, `*.pem`, force push, hard reset, `rm -rf`, `./gradlew publish` | secrets and destructive actions |

Central denial: put `permissions.deny` in managed settings. Setting `allowManagedPermissionRulesOnly: true`
makes managed rules the only ones that apply, dropping user and project allow rules as well.

### 4. Hooks

Hooks are shell commands (or HTTP calls) the harness runs at fixed events. They run every time, whatever the
model decides.

- **Events**: 33, including `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`,
  `PostToolUse`, `PostToolUseFailure`, `Notification`, `PreCompact`, `SubagentStop`, `Stop`, `ConfigChange`,
  `SessionEnd`.
- **Exit codes**: 0 continues (stdout JSON is applied); 2 blocks on events that support blocking (`PreToolUse`,
  `UserPromptSubmit`, `Stop`, `SubagentStop`, `ConfigChange`), with stderr fed back to the agent as the reason.
  `PostToolUse` cannot block because the tool already ran. Other non-zero codes are non-blocking unless the hook
  sets `"onFailure": "block"` (v2.1.295+).
- **JSON output**: `continue`, `stopReason`, `systemMessage`, `decision: "block"`. On `PreToolUse`,
  `hookSpecificOutput.permissionDecision` (`allow`, `deny`, `ask`, `defer`) with `permissionDecisionReason`,
  `updatedInput` and `additionalContext`.
- **Locations**: user, project, local, managed policy, plugin `hooks/hooks.json`, and skill or subagent frontmatter.

The three hooks here, all calling the same scripts CI runs:

| Hook | Event and matcher | Guarantee |
|---|---|---|
| [`protect-contracts.sh`](../../../.claude/hooks/protect-contracts.sh) | `PreToolUse` on `Edit`, `Write`, `MultiEdit` | returns `ask` with a reason for any file under `contracts/openapi/` |
| [`pre-pr-gate.sh`](../../../.claude/hooks/pre-pr-gate.sh) | `PreToolUse` on `Bash` and `mcp__github__create_pull_request` | `git push`, `gh pr create` and MCP PR creation run only if `scripts/verify.sh` is green; exit 2 otherwise |
| [`require-tests-on-stop.sh`](../../../.claude/hooks/require-tests-on-stop.sh) | `Stop` | production changes without test changes cannot end the turn; loop-safe via `stop_hook_active` |

Design rules: fast on the hot path, quiet on success, actionable on failure, loop-safe, one source of truth with
CI, and the guardrail files themselves protected (`ask` plus CODEOWNERS).

### 5. Organisation-level hooks and lock-down

Managed hooks merge with lower levels and cannot be removed by them. `allowManagedHooksOnly: true` disables
user, project, local and plugin hooks, which also disables the repository hooks this curriculum relies on, so use
it only where the managed layer carries every hook teams need. Only a managed-level `disableAllHooks` can disable
managed hooks.

### 6. Auditing configuration changes

A `ConfigChange` hook can log edits to local settings for audit. It does not fire for server-managed or MDM
changes and cannot block `policy_settings`. Settings-change audit events are also available through the
Compliance API or audit log export (module 08).

## Key messages

- Permissions decide *what may run*. Hooks decide *what must happen first*. Tests and CI decide *what counts as done*.
- Make the right path the easy path: allow the safe and frequent, ask for shared state, deny the destructive.
- A hook's failure message is the best training material you have: it teaches at the moment of the mistake.

## Lab (45 min)

1. **Trigger every hook.** Edit a contract file (ask), end a turn with a `src/main` change and no test (blocked),
   push with a failing assertion (blocked). Read each message as the agent sees it.
2. **Turn module 01's risk inventory into rules.** Write the allow, ask and deny entries for your repository.
3. **Write a `PostToolUse` hook** that runs your formatter after each edit and stays quiet on success.
4. **Design a `ConfigChange` audit hook** that appends the change to a log file.

## Governance controls introduced

| Control | Layer | Owner | Where |
|---|---|---|---|
| Default mode pinned, bypass and auto disabled as policy requires | guarantee | security | managed settings |
| Central deny list | guarantee | security | managed settings |
| Repository allow and ask lists | guarantee | tech leads | `.claude/settings.json` |
| Three standard hooks | guarantee | tech leads | `.claude/hooks/`, distributed by plugin |
| Configuration change audit | oversight | platform | `ConfigChange` hook, Compliance API |

## Common questions

- *"Will prompts annoy developers into bypass?"* That is what the allow list is for. Measure prompt volume in
  telemetry (`claude_code.tool_decision`) and extend the allow list where prompts are routine.
- *"Can the agent edit the hook that blocks it?"* Edits to `.claude/hooks/**` and `.claude/settings.json` are
  under `ask` and owned in CODEOWNERS; managed hooks cannot be edited from a session at all.
- *"Why not just deny everything risky?"* Deny what is never legitimate. Ask for what is sometimes legitimate.
  Over-denying pushes work outside the tool.

## Further reading

- https://code.claude.com/docs/en/permissions, https://code.claude.com/docs/en/permission-modes
- https://code.claude.com/docs/en/hooks
- [`docs/05-hooks-and-permissions.md`](../../05-hooks-and-permissions.md)
