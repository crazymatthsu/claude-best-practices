# Module 08: Security, privacy and compliance

| | |
|---|---|
| **Audience** | security, platform, compliance and legal, executives (sections 1 and 3) |
| **Duration** | 60 min |
| **Prerequisites** | module 02 |
| **Materials** | official pages listed under further reading; [`templates/governance-policy-template.md`](../templates/governance-policy-template.md) |

> **Version note.** Facts below were checked against the official documentation in October 2026. The research
> did not open the Zero Data Retention, legal and compliance, HIPAA, dev container and cloud environment pages;
> confirm those details with your account team and the live pages before publishing figures in a policy.

## Learning objectives

1. Compare the deployment options and name what each decides: identity, billing, residency, retention.
2. State how prompts and code are handled: training, retention, local transcripts, telemetry content.
3. Explain what the sandbox does and does not cover, and where the remaining controls come from.
4. Describe the prompt-injection threat model and the layered mitigation.
5. Name the audit sources for an individual change and for the fleet.

## Topics

### 1. Deployment options

| Option | Enabled by | Identity | Notes |
|---|---|---|---|
| Claude for Teams or Enterprise | claude.ai sign-in | SSO at the Claude account level | required for cloud sessions, routines, Code Review, Remote Control and the Chrome extension |
| Claude Console (API) | `ANTHROPIC_API_KEY` or `apiKeyHelper` | Console roles: "Claude Code" (creates only Claude Code keys) and "Developer" | workspace spend and rate limits |
| Amazon Bedrock | `CLAUDE_CODE_USE_BEDROCK` | AWS IAM | provider billing and regions |
| Claude Platform on AWS | `CLAUDE_CODE_USE_ANTHROPIC_AWS` | AWS IAM | provider billing and regions |
| Google Cloud Agent Platform (formerly Vertex AI) | `CLAUDE_CODE_USE_VERTEX` | Google Cloud IAM | provider billing and regions |
| Microsoft Foundry | `CLAUDE_CODE_USE_FOUNDRY` | Entra ID | provider billing and regions |
| LLM gateway | `ANTHROPIC_BASE_URL` | gateway's | your logging and routing |
| Claude apps gateway (self-hosted) | fronts Bedrock, AWS, Google Cloud, Foundry or the Anthropic API | OIDC SSO only | per-request audit log with IdP identity, per-user and per-group spend limits, managed-policy delivery; positioned for data residency needs |

Related controls: `allowedProviders` (v2.1.285+) limits which providers a machine may use; `forceLoginMethod`
(`claudeai`, `console`, `gateway`) and `forceLoginOrgUUID` enforce the sign-in for terminal, VS Code and SDK
sessions. Set them in both device and server-managed sources, because managed sources do not merge by default.
Version floors: `minimumVersion`, `requiredMinimumVersion`, `requiredMaximumVersion`.

Credential order: cloud provider variables, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_API_KEY`, `apiKeyHelper`,
`CLAUDE_CODE_OAUTH_TOKEN`, profiles, then `/login`. Storage: macOS Keychain; Linux `~/.claude/.credentials.json`
(mode 0600); Windows under the user profile.

### 2. Network

`HTTPS_PROXY`, `HTTP_PROXY`, `NO_PROXY` (no SOCKS); corporate CAs with `NODE_EXTRA_CA_CERTS` or
`CLAUDE_CODE_CERT_STORE`; mutual TLS with `CLAUDE_CODE_CLIENT_CERT` and `CLAUDE_CODE_CLIENT_KEY`.

### 3. Data handling

| Question | Answer from the documentation |
|---|---|
| Is our code used for training? | Under commercial terms (Team, Enterprise, API, third-party platforms): no, unless the customer opts in. Consumer plans are opt-in |
| How long are prompts retained? | 30 days standard for commercial accounts. Zero Data Retention is available to qualified Claude for Enterprise accounts and enabled per organisation by the account team |
| Exceptions? | Transcripts sent with `/feedback`, `/bug` or `/share` are kept five years. Local transcripts under `~/.claude/projects/` are kept 30 days by default (`cleanupPeriodDays`) |
| Does telemetry contain code? | Not by default. Content capture gates (`OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_TOOL_DETAILS`, `OTEL_LOG_TOOL_CONTENT`, `OTEL_LOG_RAW_API_BODIES`) are off |
| Data residency? | Through provider regions and the self-hosted gateway. No Claude Code-specific control beyond those |
| Regulated workloads? | A HIPAA setup page exists; confirm scope with your account team |

### 4. Sandboxing

Off by default; enable with `/sandbox` or `sandbox.enabled`. Uses Seatbelt on macOS and bubblewrap plus socat on
Linux and WSL2; native Windows runs unsandboxed. It isolates Bash, PowerShell and Monitor commands and their
children, with network traffic passing a proxy that checks `sandbox.network.allowedDomains` (empty by default).

It does **not** cover file tools, MCP servers or hooks. Managed enforcement keys: `sandbox.failIfUnavailable`,
`allowUnsandboxedCommands: false`, `sandbox.network.allowManagedDomainsOnly`,
`sandbox.filesystem.allowManagedReadPathsOnly`. Project files cannot disable filesystem isolation. The security
page recommends the sandbox runtime or a dev container for stronger isolation.

### 5. Prompt injection

Threat: instructions hidden in content the agent reads (a web page, a dependency's README, an issue comment, CI
logs) that try to redirect it, exfiltrate data or escalate access. Product protections: manual and auto modes,
command-injection detection, fail-closed permission matching, workspace trust, `.mcp.json` approval. The
documentation does not claim immunity. Our layers: permission prompts for new actions, deny lists, read-only
agents in CI, the sandbox's network allowlist, human review of every PR, and treating anything a bot reads as
untrusted data.

### 6. Cloud sessions and GitHub Actions

- Anthropic-hosted cloud sessions run in an isolated VM per session; network access is limited by default and set
  per environment; GitHub credentials stay server-side behind a proxy that rejects branch deletions and
  non-branch pushes; branch protection still applies; audit logging is available.
- `anthropics/claude-code-action@v1`: triggering requires write access; bots are blocked unless listed in
  `allowed_bots`; restrict tools with `--allowedTools` in `claude_args` and turns with `--max-turns`. The GitHub
  App's permission set is broad and cannot be accepted in part; a custom app with Contents, Issues and Pull
  requests is the narrower option.

### 7. Audit trail

| Scope | Source |
|---|---|
| One change | the PR (description, review, verdicts), CI logs, hook decisions, commits |
| Configuration | settings-change audit events through the Compliance API or audit log export; `ConfigChange` hooks for local edits |
| Fleet | OpenTelemetry events (`tool_decision`, `api_request`, `mcp_server_connection`, `plugin_installed`); the gateway's per-request log |

### 8. Incident process

Secret exposure, unexpected destructive actions and suspected injection are reported to [security contact],
the session transcript is preserved, the credential is rotated, and the lesson becomes a deny rule, a hook or a
test. The policy template has the clause.

## Key messages

- The deployment decision settles identity, billing, residency and retention at once. Make it first.
- Nothing here claims zero risk. The design makes risk small, visible and attributable.
- The controls a client cannot switch off (branch protection, CI, server-side credentials, network policy) are the
  ones to rely on when a laptop is compromised.

## Demo

1. Ask the agent to read `.env` in this repository: the deny rule refuses.
2. Show `/sandbox` and the `sandbox` block in the managed settings example.
3. Walk through the data-handling table with the compliance representative in the room.

## Governance controls introduced

| Control | Layer | Owner | Where |
|---|---|---|---|
| One approved endpoint and sign-in | guarantee | security | `allowedProviders`, `forceLoginMethod`, `forceLoginOrgUUID` |
| Secrets never in context | guarantee | security | managed `permissions.deny` |
| Sandbox with network allowlist | guarantee | platform | `sandbox.*` managed keys |
| Read-only agents in CI, narrow GitHub App | guarantee | platform | workflow permissions, `allowed_bots`, `--allowedTools` |
| Retention and training terms | oversight | legal | contract, ZDR |
| Audit sources | oversight | security | Compliance API, telemetry, gateway log |

## Exercises

1. **Pick the deployment option** for your organisation and list what it decides.
2. **Classify your data** into the four rows of the policy template's data-handling table.
3. **Draft the incident runbook** in ten lines.

## Common questions

- *"Can we prove nothing left the building?"* Telemetry and the gateway log show which endpoints were called; the
  sandbox allowlist and network policy bound where commands can connect; MCP allowlists bound integrations.
- *"Is the sandbox enough?"* It covers commands, not file tools, MCP or hooks. Combine with permissions and the
  network policy.
- *"What about developers' local transcripts?"* Kept 30 days by default; adjust `cleanupPeriodDays` by policy.

## Further reading

- https://code.claude.com/docs/en/security, https://code.claude.com/docs/en/sandboxing
- https://code.claude.com/docs/en/data-usage, https://code.claude.com/docs/en/third-party-integrations
- https://code.claude.com/docs/en/claude-apps-gateway, https://code.claude.com/docs/en/authentication
- https://code.claude.com/docs/en/network-config, https://code.claude.com/docs/en/github-actions,
  https://code.claude.com/docs/en/claude-code-on-the-web
