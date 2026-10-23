# KPI scorecard (template)

*One scorecard per pilot team or business unit. Fill the baseline over four weeks before training. Review
monthly. Sources are automated wherever possible; the two survey-based rows are marked.*

| Team | Period | Owner | Claude Code version |
|---|---|---|---|
| [name] | [YYYY-MM to YYYY-MM] | [name] | [N] |

## Scorecard

| Area | KPI | Definition | Source | Baseline | Target (day 90) | Current | Trend |
|---|---|---|---|---|---|---|---|
| Adoption | Active users | distinct users with at least one session per week | telemetry | | | | |
| Adoption | Sessions per developer per week | sessions / active users | telemetry | | | | |
| Quality | First-pass CI green rate | PRs whose first CI run passed / all PRs | CI | | | | |
| Quality | Review rounds per PR | review submissions with changes requested per PR | Git hosting | | | | |
| Quality | PRs with production changes and no test changes | from the tests-present check in CI | CI | | 0 | | |
| Quality | Escaped defects | bugs found after merge, attributed to the period's PRs | issue tracker label | | | | |
| Quality | Coverage at the gate | line / branch coverage reported by the build | build report | | stable or up | | |
| Safety | Unplanned contract changes | contract diffs without CHANGELOG or version bump | CI contract check | | 0 | | |
| Safety | Pushes blocked by the gate | hook blocks per week | hook logs or telemetry | | visible | | |
| Safety | Permission denials | denied tool calls per week, by rule | telemetry (tool decision events) | | trending down | | |
| Safety | Attempted reads of secret paths | denials on secret-path rules | telemetry | | 0 | | |
| Velocity | Lead time spec Ready → merged | median days | spec status + merge date | | down | | |
| Cost | Spend per active developer per month | cost / active users | telemetry, usage analytics | | within budget | | |
| Cost | Tokens per merged PR | tokens / merged PRs | telemetry + Git hosting | | trending down | | |
| Experience | Human corrections per task (survey) | developer self-report, weekly | short survey | | down | | |
| Experience | Developer satisfaction (survey) | 1 to 5, monthly | short survey | | up | | |

## Designing a fair comparison

1. Pick six to ten representative tasks of similar size: a feature, a bug fix, a refactor, a contract change.
2. Run half on a branch *without* the guardrails (only a `/init`-generated `CLAUDE.md`) and half *with* the full
   setup. Swap which half next round.
3. For each task record: CI green on first push? A test for every acceptance criterion? Contract untouched unless
   intended? Review comments? Time to merge?
4. Compare `/context` at the end of a typical task in both setups. The guarded setup should use *less*
   always-on context, not more.

## Metrics to avoid as targets

Lines of code written, number of sessions, number of prompts, and "acceptance rate" of suggestions. They measure
activity, not outcomes, and are easy to move in the wrong direction.

## Review notes

| Date | What changed | Decision |
|---|---|---|
| | | |
