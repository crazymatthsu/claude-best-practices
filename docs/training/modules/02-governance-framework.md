# Module 02: The governance framework. Policy stack, roles and the minimum standard

| | |
|---|---|
| **Audience** | executives (sections 1 to 3), platform and security, tech leads |
| **Duration** | 60 min |
| **Prerequisites** | module 01 or the executive briefing |
| **Materials** | [`docs/05-hooks-and-permissions.md`](../../05-hooks-and-permissions.md), [`templates/managed-settings.example.json`](../templates/managed-settings.example.json), [`templates/governance-policy-template.md`](../templates/governance-policy-template.md) |

> **Version note.** Setting names below were checked against the official documentation
> (https://code.claude.com/docs) in October 2026. Several keys are version-gated and are marked as such.
> Re-check the settings reference before each delivery.

## Learning objectives

1. Distinguish guidance, guarantees and oversight, and place any control in the right category.
2. Describe the settings precedence and the four delivery channels for organisation policy.
3. Name the locks that stop lower layers from loosening organisation policy, and their limits.
4. Assign ownership of each layer and define the minimum repository standard.

## Topics

### 1. Three kinds of control

| Kind | Examples | Property |
|---|---|---|
| Guidance | `CLAUDE.md`, rules, skills, specs | tells the agent what we want; can be forgotten or pushed out of context |
| Guarantees | permission rules, hooks, tests, CI, CODEOWNERS, sandbox | run every time regardless of what the model decides |
| Oversight | telemetry, cost dashboards, PR evidence, KPI reviews | show what happened; feed corrections back into the first two |

Rule of thumb: if breaking a rule would hurt, it needs a guarantee and at most one line of guidance.

### 2. The settings precedence

Highest first: **managed (organisation) settings** → command-line `--settings` → `.claude/settings.local.json`
(personal, gitignored) → `.claude/settings.json` (project, committed) → `~/.claude/settings.json` (user).

Managed values cannot be overridden by lower scopes. Array keys such as `permissions.allow` and
`permissions.deny` merge across scopes, so users and projects can **add** entries but never remove managed ones.

### 3. Delivering organisation policy

| Channel | Where | Notes |
|---|---|---|
| Device file | macOS `/Library/Application Support/ClaudeCode/managed-settings.json`; Linux and WSL `/etc/claude-code/managed-settings.json`; Windows `C:\Program Files\ClaudeCode\managed-settings.json`; drop-ins in `managed-settings.d/` | deployed by MDM or configuration management |
| MDM profile or registry | macOS plist domain `com.anthropic.claudecode`; Windows `HKLM\SOFTWARE\Policies\ClaudeCode`, value `Settings` (JSON string) | stronger than a plain file; the HKCU twin is user-writable and only a fallback |
| Server-managed settings | claude.ai Admin settings → Claude Code → Managed settings | Teams or Enterprise, Owner or Primary Owner role; reaches claude.ai sign-ins only |
| Companion files | managed `CLAUDE.md` (same directories), `managed-mcp.json`, managed `.claude/agents/` | guidance, exclusive MCP control, organisation subagents |

Two behaviours to plan for:

- **One source applies by default.** The first managed source that delivers a key wins unless
  `managedSourcesBehavior: "merge"` is set. Mixing device and server-managed settings without it can silently
  drop policy.
- **Sessions on third-party providers** (`CLAUDE_CODE_USE_*`, a custom `ANTHROPIC_BASE_URL`), gateway sign-ins
  and Cowork do not receive claude.ai server-managed settings. Use device delivery for them.

Limit to state plainly to leadership: the documentation calls managed settings a client-side control, not a
security boundary. A user with local administrator rights can edit the files. Pair them with controls the client
cannot bypass: branch protection, CI gates, network policy, server-side credentials.

### 4. What belongs at each layer

| Layer | Owner | Content | Examples of keys |
|---|---|---|---|
| Organisation | security, platform | deny lists, mode restrictions, login and provider enforcement, telemetry destination, approved MCP servers and plugin sources, version floors, model restrictions | `permissions.deny`, `permissions.defaultMode`, `permissions.disableBypassPermissionsMode`, `forceLoginMethod`, `forceLoginOrgUUID`, `env` (OTel), `allowedMcpServers`, `extraKnownMarketplaces`, `enabledPlugins`, `availableModels` |
| Project | tech leads | commands and non-negotiables, allow and ask lists, hooks, skills, subagents, CODEOWNERS | [`.claude/settings.json`](../../../.claude/settings.json) in this repository |
| User | developer | personal preferences; extra restrictions | `~/.claude/settings.json`, `~/.claude/CLAUDE.md` |

### 5. The locks

| Lock (managed only) | Effect | When to turn it on |
|---|---|---|
| `permissions.disableBypassPermissionsMode: "disable"` | bypass mode cannot be selected | day one |
| `permissions.disableAutoMode: "disable"` | the classifier-driven `auto` mode cannot be selected | if policy requires a human on every prompt |
| `allowManagedPermissionRulesOnly: true` | only managed rules apply; user and project allow rules are dropped | after the plugin or managed file carries the allow lists teams need |
| `allowManagedHooksOnly: true` | user, project, local and plugin hooks are disabled | rarely; it also disables the repository hooks this curriculum relies on |
| `allowManagedMcpServersOnly: true` | the managed MCP allowlist is authoritative, including for plugin and claude.ai servers | once the catalogue exists |
| `strictKnownMarketplaces`, `blockedMarketplaces`, `disableSideloadFlags` | restrict where plugins come from | once the internal marketplace exists; an empty strict list blocks everything, including the official marketplace |
| `strictPluginOnlyCustomization` | skills, agents, hooks and MCP come only from plugins and managed settings | high-assurance environments |
| `allowedProviders` (v2.1.285+) | limits which model providers a machine may use | with the deployment decision |

Known gaps the documentation lists: plugin keys cannot target individual users or groups, and the `/plugin`
command cannot be hidden.

### 6. Roles

| Role | Owns |
|---|---|
| Security | sections 3 to 5 above: deny lists, login enforcement, MCP catalogue, plugin sources, incident process |
| Platform and enablement | authoring and deploying managed settings, the reference configuration and internal plugin, telemetry, training |
| Tech leads | the project layer, CODEOWNERS on guardrail files, contract ownership, monthly pruning |
| Developers | the user layer; reporting friction and corrections |
| Product | specs; acceptance criteria; out-of-scope |
| Compliance and legal | commercial terms, retention, residency; the policy document |

### 7. The minimum repository standard

Before an agent does real work in a repository: a lean `CLAUDE.md`, path rules, allow/ask/deny settings, the
three standard hooks, a gate that CI also runs, CODEOWNERS on contracts and guardrail files, the PR template.
Checklist: [`templates/repo-readiness-checklist.md`](../templates/repo-readiness-checklist.md).

### 8. Exceptions and review

Exceptions are time-boxed, approved by security, recorded, and reviewed when the policy is reviewed. The policy
is reviewed every six months and after any major Claude Code release.

## Key messages

- Decide what each layer may do; then lock only what the layers below would otherwise loosen.
- Managed settings are necessary and not sufficient. Branch protection, CI and server-side credentials are the
  controls a client cannot switch off.
- Turn locks on progressively. A lock that removes what teams need gets worked around.

## Demo

1. Open [`.claude/settings.json`](../../../.claude/settings.json) and walk through the three lists and the hooks.
2. Open [`templates/managed-settings.example.json`](../templates/managed-settings.example.json) and show how the
   organisation layer repeats the deny list, pins the default mode, disables bypass, enforces login and switches
   telemetry on. The key-by-key explanation is in [WF-09](../workflows/WF-09-enterprise-policy-rollout.md).
3. Run `/permissions` and point out that rules show their source scope.

## Governance controls introduced

| Control | Layer | Owner | Where |
|---|---|---|---|
| Managed settings with deny lists, mode pin, bypass disabled | guarantee | security, platform | device file, MDM or registry, server-managed settings |
| Login and provider enforcement | guarantee | security | `forceLoginMethod`, `forceLoginOrgUUID`, `allowedProviders` |
| Project settings reviewed like code | guarantee | tech leads | `.claude/settings.json`, CODEOWNERS |
| Policy document | oversight | compliance | [`templates/governance-policy-template.md`](../templates/governance-policy-template.md) |

## Exercises

1. **Draft managed settings v0.1** from the example: keep only what every team can live with on day one.
2. **Choose the delivery channel** for your fleet and decide `managedSourcesBehavior`.
3. **Fill the RACI** in the policy template with names.

## Common questions

- *"Can a developer turn the hooks off?"* Project hooks are under `ask` for edits and owned in CODEOWNERS;
  managed hooks cannot be removed by lower scopes; `allowManagedHooksOnly` removes all others. A local admin can
  still edit managed files, which is why CI and branch protection remain the backstop.
- *"Do we need server-managed and device settings?"* Device delivery covers every sign-in method; server-managed
  settings are convenient for claude.ai sign-ins. If you use both, set the merge behaviour explicitly.
- *"Where does the organisation `CLAUDE.md` go?"* The managed settings directory, or the managed-only `claudeMd`
  key. Developers cannot exclude it. Keep it under ten lines.

## Further reading

- https://code.claude.com/docs/en/managed-settings, https://code.claude.com/docs/en/server-managed-settings
- https://code.claude.com/docs/en/settings, https://code.claude.com/docs/en/admin-setup
- [`docs/05-hooks-and-permissions.md`](../../05-hooks-and-permissions.md)
