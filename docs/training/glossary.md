# Glossary

Written for readers who do not use Claude Code daily. Terms link to the module that explains them.

| Term | Meaning | Module |
|---|---|---|
| **Agent** | Software that pursues a goal by repeatedly choosing an action (read a file, run a command), observing the result and deciding the next step. Claude Code is an agent for software work | [01](modules/01-foundations.md) |
| **Agentic loop** | The cycle gather context → plan → act with a tool → verify → iterate until done or blocked | 01 |
| **Context window** | The agent's working memory for one session. Everything in it competes for attention: instructions, files read, command output, conversation | [03](modules/03-context-and-memory.md) |
| **Tool** | A capability the agent can invoke: read, edit or write files, run shell commands (Bash), fetch web pages, call MCP servers, delegate to a subagent | 01 |
| **CLAUDE.md** | A markdown file of instructions loaded automatically. Exists at organisation, user, project and directory level. The project one is committed and reviewed like code | 03 |
| **Rules (`.claude/rules/`)** | Instruction files that load only when the agent works on matching file paths, so test rules appear only when touching tests | 03 |
| **Nested memory** | A `CLAUDE.md` inside a directory, loaded only when the agent works there. Used for areas with different rules, such as API contracts or generated code | 03 |
| **Progressive disclosure** | Keeping always-loaded context tiny and loading detail on demand (rules, skills, linked documents) | 03 |
| **Permission rule** | A setting that marks a tool or command pattern as `allow` (runs freely), `ask` (human confirms) or `deny` (never) | [04](modules/04-permissions-and-hooks.md) |
| **Permission mode** | The session's overall stance: default (ask before changes), plan (read-only planning), accept edits, auto (a classifier decides what to ask about; the starting mode in recent versions unless policy pins another), don't-ask (for unattended runs) and bypass (no prompts; disabled centrally in managed environments) | 04 |
| **Plan mode** | A read-only mode in which the agent proposes a plan for approval before any file changes. The cheapest moment to correct course | 04 |
| **Hook** | A shell command the Claude Code harness runs at fixed events (before a tool runs, after it, when the agent wants to stop). Runs every time, regardless of what the model decides. The main deterministic control | 04 |
| **Gate** | A script that must pass before code leaves the machine (here `scripts/verify.sh`), run by a hook before push and by CI on the server | [07](modules/07-quality-gates-and-sdlc.md) |
| **Managed settings** | An organisation-level settings file deployed by IT that takes precedence over project and user settings and cannot be overridden | [02](modules/02-governance-framework.md) |
| **Skill** | A reusable, named procedure (`.claude/skills/<name>/SKILL.md`) that the agent loads when a task matches its description or when invoked with `/name`. Encodes the correct order of steps | [05](modules/05-skills-subagents-plugins.md) |
| **Subagent** | A separately configured agent with its own context window, tool list and instructions, used for a delegated job such as review. Returns only a result. Enables least privilege (a reviewer that cannot edit) | 05 |
| **Plugin** | A package of skills, subagents, hooks, slash commands and MCP configuration that can be installed from a marketplace. The distribution unit for an enterprise standard | 05 |
| **Marketplace** | A catalogue of plugins, which an organisation can host internally in a Git repository | 05 |
| **MCP (Model Context Protocol)** | An open standard for connecting the agent to external systems (issue trackers, Git hosting, databases, documentation). Each MCP server adds tools | [06](modules/06-mcp-and-integrations.md) |
| **Headless mode** | Running Claude Code non-interactively (`claude -p "…"`) in scripts, CI jobs or scheduled tasks | [WF-10](workflows/WF-10-headless-and-scheduled-automation.md) |
| **Contract** | Anything other teams depend on: an HTTP API (OpenAPI), events, database schemas, a library's public API. Protected so it cannot drift by accident but can evolve on purpose | 07 |
| **CODEOWNERS** | A Git hosting feature that requires review from named owners when specific paths change. Used here to protect contracts and the guardrail configuration | 07 |
| **ADR (Architecture Decision Record)** | A short, append-only document recording a decision, its alternatives and consequences | [WF-06](workflows/WF-06-architecture-docs-adrs-perf-reports.md) |
| **Spec** | A feature description with numbered, testable acceptance criteria and an explicit out-of-scope list. Owned by product. The agent only implements specs marked Ready | [WF-07](workflows/WF-07-from-idea-to-testable-spec.md) |
| **Acceptance criterion (AC)** | A Given / When / Then statement that a test can verify. Each becomes a named test | 07 |
| **Prompt injection** | Instructions hidden in content the agent reads (a web page, a dependency, an issue comment) that try to redirect it. Mitigated by permissions, read-only agents and human review | [08](modules/08-security-privacy-compliance.md) |
| **Sandbox** | Operating-system level isolation of the commands the agent runs, restricting file system and network access | 08 |
| **Zero Data Retention (ZDR)** | A contractual and technical arrangement under which the provider does not retain prompts or outputs after the request is served | 08 |
| **OpenTelemetry (OTel)** | An open standard for exporting metrics, logs and traces. Claude Code can export usage, cost and tool-decision telemetry to your monitoring stack | [09](modules/09-observability-cost-roi.md) |
| **Token** | The unit in which model usage is metered and billed. Context size and cost are measured in tokens | 09 |
