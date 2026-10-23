# Module 10: Adoption and change management

| | |
|---|---|
| **Audience** | executives, platform and enablement, tech leads |
| **Duration** | 45 min |
| **Prerequisites** | the executive briefing or module 02 |
| **Materials** | [`docs/13-adopting-and-measuring.md`](../../13-adopting-and-measuring.md), [`templates/repo-readiness-checklist.md`](../templates/repo-readiness-checklist.md), [`templates/kpi-scorecard.md`](../templates/kpi-scorecard.md) |

## Learning objectives

1. Sequence a rollout: foundation → guardrails → workflows → measure and prune.
2. Place a team on the maturity model and name its next step.
3. Run the feedback loop that turns corrections into rules, hooks and tests.
4. Plan role-based training and a champions network.

## Topics

1. **Sequence per repository (four weeks).** Week 1: lean `CLAUDE.md`, rules, a reliable `verify.sh` and CI
   running the same scripts. Week 2: hooks and permissions, the contract folder and contract tests. Week 3:
   skills (`tdd-feature`, `pr-ready`), subagents, the spec template for product. Week 4 and after: baseline
   versus guarded comparison, monthly pruning. Start with commands and the gate.
2. **Sequence for the organisation (90 days).** Decisions and managed settings first, pilot repositories with the
   reference configuration, role-based training, pilot delivery with office hours, then the internal plugin,
   the MCP catalogue, policy v1.0 and a KPI review before wave two. See the executive briefing, slide 11.
3. **What to copy, adapt or write.** Hooks and scripts copy as is. Settings, agents, CI and CODEOWNERS adapt.
   `CLAUDE.md`, rules, contracts and specs are written per repository.
4. **The maturity model.** Level 0 ad hoc, 1 managed, 2 guarded, 3 standardised, 4 optimised. Assessment
   questions per level (below). Teams move one level at a time.
5. **The feedback loop.** Every repeated correction becomes, in this order of preference: a test, a hook, a rule.
   Weekly office hours collect them. The platform team ships them in the plugin. Nobody fixes the same thing twice.
6. **Champions and communication.** One champion per team, trained first, present at office hours. Release
   notes for the plugin. A visible scorecard.
7. **A fair pilot.** Six to ten representative tasks; half with the full setup, half with only a `/init`
   `CLAUDE.md`; swap next round; record CI green on first push, tests per AC, contract untouched, review
   comments, time to merge. Avoid vanity metrics (lines of code, number of sessions).
8. **Keeping it healthy.** Monthly pruning of rules. Watch the gate's runtime. Track the Claude Code version and
   re-check setting names after upgrades. Retire controls that no longer fire.

## Maturity assessment questions

| Level | Ask | Evidence |
|---|---|---|
| 1 Managed | Is there one approved endpoint, central identity, a managed settings file with deny lists, telemetry on? | managed settings deployed; dashboard shows sessions |
| 2 Guarded | Does every active repository have a lean `CLAUDE.md`, allow/ask/deny, the three hooks, a gate equal to CI, CODEOWNERS on the guardrails? | readiness checklist complete per repository |
| 3 Standardised | Are skills, agents and hooks installed from a versioned internal plugin? Is there an approved MCP catalogue? Is Claude in CI read-only? | plugin version pinned in repositories; catalogue published |
| 4 Optimised | Are KPIs reviewed monthly? Were rules deleted last month? Do automated audits run? | KPI review minutes; pruning commits; scheduled jobs |

## Common objections and responses

| Objection | Response |
|---|---|
| "This slows developers down." | The allow list removes prompts for safe, frequent commands. The gate catches failures before CI, which is faster than a CI round trip. Measure review rounds and lead time, not feelings. |
| "We have too many repositories." | The plugin carries the shared part. Each repository writes under 50 lines plus its commands. Start with the active ones. |
| "Developers will just disable the hooks." | The hook and settings files are owned in CODEOWNERS and edits to them are under `ask`. Managed settings cannot be overridden locally. Also measure bypass attempts. |
| "Our stack is not Java." | Everything except the Gradle commands is stack-agnostic: swap the build command in `verify.sh`, `CLAUDE.md` and the allow list. |
| "Show me the ROI first." | Run the fair pilot with the scorecard. Decide at day 90 on your own numbers. |

## Exercises

1. **Assess your team** against the questions above. Name the single next step.
2. **Write a 30-day plan for one repository** using the readiness checklist. Identify who owns each item.
3. **Plan the first office hour.** What will you ask teams to bring?

## Further reading

- [`docs/13-adopting-and-measuring.md`](../../13-adopting-and-measuring.md)
- [`00-executive-briefing.md`](../00-executive-briefing.md), slides 10 to 14
- [`workflows/WF-08-onboarding-a-repository.md`](../workflows/WF-08-onboarding-a-repository.md)
