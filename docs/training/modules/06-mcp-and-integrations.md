# Module 06: MCP and integrations. Connecting to enterprise systems safely

| | |
|---|---|
| **Audience** | platform engineers, security, tech leads |
| **Duration** | 60 min |
| **Prerequisites** | modules 02 and 04 |
| **Materials** | [`docs/06-mcp-and-tools.md`](../../06-mcp-and-tools.md), [`docs/templates/mcp.json`](../../templates/mcp.json) |

> **Version note.** `managedMcpServers` requires v2.1.259 or later. Other names were checked against the
> official documentation in October 2026.

## Learning objectives

1. Decide whether a need is best served by a CLI, a project MCP server or a user-scoped one.
2. Explain MCP scopes, precedence and the approval flow for project servers.
3. Configure organisation-level allowlists and denylists and know what they match on.
4. Run a catalogue process for approving servers with scoped, read-only credentials.

## Topics

### 1. What MCP adds, and what it costs

MCP (Model Context Protocol) servers give the agent tools for external systems: Git hosting, issue trackers,
documentation, databases, observability. Every server adds tool definitions to the context and one more wrong
choice the agent can make. Fewer, focused servers produce better tool choices. Decide in this order: can a CLI
already do it? Does most of the team need it for this repository? Can it be limited?

### 2. Scopes and precedence

| Scope | Stored in | Shared | Use for |
|---|---|---|---|
| local (default) | `~/.claude.json`, per project | no | personal experiments |
| project | `.mcp.json` in the repository | yes, reviewed in PRs | servers most of the team needs |
| user | `~/.claude.json` | no | personal tools across repositories |
| plugin | the plugin's `.mcp.json` | yes, versioned | the enterprise standard |
| claude.ai connectors | account level | per user | connectors admitted by the organisation |

Precedence: local, project, user, plugin, claude.ai connectors. `managedMcpServers` in managed settings outranks
all of them.

### 3. Approving project servers

Interactive sessions prompt for approval the first time a project server is used. Settings:
`enableAllProjectMcpServers`, `enabledMcpjsonServers`, `disabledMcpjsonServers` (blocks in every mode).
**Headless (`claude -p`) and the Agent SDK load project servers without asking**, so review `.mcp.json` before
enabling any automation on a repository ([WF-10](../workflows/WF-10-headless-and-scheduled-automation.md)).

### 4. Organisation controls

| Control | Effect |
|---|---|
| `managed-mcp.json` in the managed settings directory | exclusive control: users cannot add other servers; an empty `mcpServers` map disables MCP. Not deliverable through server-managed settings |
| `allowedMcpServers`, `deniedMcpServers` | match on `serverUrl` (wildcards), `serverCommand` (exact array) or `serverName` (a label, not a security control). The denylist always wins. An empty allowlist allows nothing |
| `allowManagedMcpServersOnly: true` | the managed allowlist is authoritative, including for servers added by users, plugins and claude.ai |
| `managedMcpServers` (v2.1.259+) | provides remote HTTPS servers to every user |
| `allowAllClaudeAiMcps` | re-admits claude.ai connectors alongside `managed-mcp.json` |

### 5. Credentials and transports

- Secrets through `${ENV_VAR}` expansion in configuration, a secret manager, or `headersHelper` for dynamic
  headers. Never literal tokens in Git.
- OAuth where the server supports it, with scopes pinned (`oauth.scopes`); `--client-id` and `--client-secret`
  for pre-registered clients.
- Tokens read-only and scoped: one Jira project, one Confluence space, a non-production database role.
- Transports: HTTP for remote servers (recommended), SSE (deprecated), stdio for local processes. Prefer remote
  servers run by a team over stdio binaries on every laptop.

### 6. Guardrails must cover MCP too

Hooks and permission rules apply to MCP tools (`mcp__<server>__<tool>`). The pre-PR gate in this repository
matches `mcp__github__create_pull_request` so that a PR created through MCP is gated exactly like `git push`.
Telemetry records `claude_code.mcp_server_connection` events for inventory.

### 7. The catalogue process

1. A team requests a server with purpose, scope, data touched and token type.
2. Security reviews data flow and token scope; platform tests it.
3. The server is added to the catalogue (a page or a repository), to `allowedMcpServers`, and, if universal, to
   `managedMcpServers` or the enterprise plugin.
4. Project `.mcp.json` entries are reviewed in PRs like any configuration.

## Key messages

- A CLI already allowed in permissions costs no context. Reach for MCP when there is no shell equivalent.
- `serverName` is a label. Allowlist by URL or command.
- Review `.mcp.json` before any headless use: automation does not get an approval prompt.

## Demo

1. `/mcp` in this repository: nothing is configured, on purpose.
2. Open [`docs/templates/mcp.json`](../../templates/mcp.json): the GitHub and Atlassian entries with
   `${GITHUB_PAT}` expansion.
3. Open [`.claude/settings.json`](../../../.claude/settings.json) and point at the `mcp__github__create_pull_request`
   matcher in the pre-PR gate hook.

## Governance controls introduced

| Control | Layer | Owner | Where |
|---|---|---|---|
| Approved catalogue enforced | guarantee | security, platform | `allowedMcpServers`, `allowManagedMcpServersOnly`, `managed-mcp.json` |
| Project servers reviewed | guarantee | tech leads | `.mcp.json` in PRs; CODEOWNERS |
| Scoped, read-only credentials | guarantee | security | token policy; `${ENV_VAR}`; OAuth scopes |
| Gate covers MCP publishing paths | guarantee | tech leads | hook matcher |
| Server inventory | oversight | platform | telemetry events, catalogue |

## Exercises

1. **Build the catalogue table** for your organisation: server, purpose, scope, token type, owner, status.
2. **Write `allowedMcpServers` entries** for three approved servers, matching on URL or command.
3. **Classify three requested servers** (a production database, a Jira read-only server, a browser automation
   server) as approve, approve with conditions, or decline.

## Common questions

- *"Can we block all MCP?"* Yes: an empty `mcpServers` map in `managed-mcp.json`. Prefer a small catalogue over a
  blanket block; teams will otherwise paste data by hand.
- *"What about personal servers?"* With `allowManagedMcpServersOnly`, they must match the allowlist too.
- *"Is the GitHub CLI enough?"* Often. The MCP server helps where there is no shell, such as the web surface.

## Further reading

- https://code.claude.com/docs/en/mcp, https://code.claude.com/docs/en/managed-mcp
- [`docs/06-mcp-and-tools.md`](../../06-mcp-and-tools.md)
