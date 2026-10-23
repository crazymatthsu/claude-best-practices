# Module 09: Observability, cost and ROI

| | |
|---|---|
| **Audience** | executives, platform engineers, tech leads, finance partners |
| **Duration** | 45 min |
| **Prerequisites** | module 02 |
| **Materials** | [`templates/kpi-scorecard.md`](../templates/kpi-scorecard.md), [`docs/13-adopting-and-measuring.md`](../../13-adopting-and-measuring.md) |

> **Version note.** Variable, metric and dashboard names were checked against the official documentation in
> October 2026. The research did not confirm current `/cost` behaviour; the costs page documents `/usage`.

## Learning objectives

1. Switch on telemetry for the fleet from managed settings and name what it emits.
2. Map every KPI in the scorecard to a telemetry metric, an event, or Git and CI data.
3. Use the spend and model controls that exist at each billing model.
4. Run a fair pilot and avoid vanity metrics.

## Topics

### 1. Telemetry setup

OpenTelemetry export is enabled with `CLAUDE_CODE_ENABLE_TELEMETRY=1` plus exporter settings:
`OTEL_METRICS_EXPORTER`, `OTEL_LOGS_EXPORTER`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS`,
`OTEL_EXPORTER_OTLP_PROTOCOL`. Set them in the managed `env` block so every machine reports to the same
collector; project files cannot set them, and managed endpoint settings override developer values.

### 2. What is emitted

| Kind | Names |
|---|---|
| Metrics | `claude_code.session.count`, `claude_code.cost.usage`, `claude_code.token.usage`, `claude_code.lines_of_code.count`, `claude_code.code_edit_tool.decision`, `claude_code.active_time.total`, and others |
| Events | `claude_code.tool_decision` (decision and source), `claude_code.tool_result`, `claude_code.api_request`, `claude_code.mcp_server_connection`, `claude_code.plugin_installed`, and others |
| Content | off by default: `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_TOOL_DETAILS`, `OTEL_LOG_TOOL_CONTENT`, `OTEL_LOG_RAW_API_BODIES` |

### 3. Dashboards and APIs

- Teams and Enterprise: claude.ai/analytics/claude-code (Owners and Admins; contribution metrics are beta and
  unavailable under Zero Data Retention), plus the Enterprise Analytics API.
- Console: platform.claude.com/claude-code and the Claude Code Analytics API.
- Cloud providers: their own billing consoles. The self-hosted gateway adds a per-request log with identity.

### 4. Spend and model controls

| Billing model | Controls |
|---|---|
| Teams and Enterprise | seat allowance as the default ceiling; usage credits; spend limits at organisation, group or member level |
| Console | workspace spend and rate limits |
| Cloud providers | provider budgets and quotas |
| Any | `--max-budget-usd` per run; managed `modelPricing` so displayed costs match contract rates (display only); `/usage` in a session |
| Model restriction (managed) | `availableModels` (picker), `enforceAvailableModels` (default model), `deniedModels` (lock), `maxEffortLevel` (effort cap); `model` alone is a default, not a lock |

### 5. From telemetry to the scorecard

| KPI | Source |
|---|---|
| Active users, sessions per developer | `claude_code.session.count` by user and team |
| Spend per developer, tokens per merged PR | `claude_code.cost.usage`, `claude_code.token.usage`, joined with merged PRs from Git hosting |
| Permission denials, attempted secret reads, prompt volume | `claude_code.tool_decision` by rule and source |
| Pushes blocked by the gate | hook logs (write a line per block) or a custom event |
| First-pass CI green rate, review rounds, PRs without tests, unplanned contract changes | CI and Git hosting data; the check scripts in CI |
| Lead time spec Ready to merge | spec status history plus merge date |
| Escaped defects | issue tracker label |

### 6. A fair pilot

Six to ten representative tasks, half with the full setup and half with only a `/init` `CLAUDE.md`; swap next
round; record outcomes per task; compare `/context` at the end. Baseline for four weeks before training.

### 7. Vanity metrics

Lines of code, number of prompts, number of sessions and "acceptance rate" measure activity, not outcomes, and are
easy to move the wrong way. Report them for capacity planning, never as targets.

### 8. Closing the loop

Monthly: read the scorecard, delete rules the agent follows unprompted, turn the top correction into a hook or
test, extend allow lists where prompt volume is routine, and record the decisions in the scorecard's review notes.

## Key messages

- Switch telemetry on before the pilot, or there is no baseline.
- Measure outcomes (green on first push, review rounds, lead time, escaped defects) and watch costs per merged PR.
- The scorecard is a management tool: it decides what to prune, what to lock and when to scale.

## Demo

1. Show the managed settings example's `env` block.
2. Run `/usage` and `/context` in a session.
3. Walk through the scorecard template with one real baseline row.

## Governance controls introduced

| Control | Layer | Owner | Where |
|---|---|---|---|
| Fleet telemetry to one collector | oversight | platform | managed `env` |
| Spend limits and budgets | guarantee | platform, finance | billing console; `--max-budget-usd` |
| Model restrictions | guarantee | platform | `availableModels`, `deniedModels`, `maxEffortLevel` |
| KPI scorecard and monthly review | oversight | enablement, tech leads | [`templates/kpi-scorecard.md`](../templates/kpi-scorecard.md) |

## Exercises

1. **Map your KPIs** to sources using the table above; mark gaps that need a hook log line or a CI step.
2. **Sketch the dashboard**: four panels for leadership, eight for platform.
3. **Set the budget** for the pilot and the alert threshold.

## Common questions

- *"Can we see individual prompts?"* Only if content capture is switched on, which is a policy decision with privacy
  consequences. Default is off.
- *"Our Zero Data Retention blocks contribution metrics."* Yes for the hosted dashboard; OpenTelemetry to your own
  collector still works.
- *"What does a good first result look like?"* PRs without tests at zero, first-pass green rate up, review rounds
  down, with cost per merged PR flat or down.

## Further reading

- https://code.claude.com/docs/en/monitoring-usage, https://code.claude.com/docs/en/analytics,
  https://code.claude.com/docs/en/costs
- [`docs/13-adopting-and-measuring.md`](../../13-adopting-and-measuring.md)
