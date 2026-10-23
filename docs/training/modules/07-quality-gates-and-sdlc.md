# Module 07: Quality gates and the SDLC. Tests, contracts, pull requests and CI

| | |
|---|---|
| **Audience** | tech leads, developers; product for sections 1, 2 and 6 |
| **Duration** | 90 min |
| **Prerequisites** | modules 01 and 04 (for the hook mechanics) |
| **Materials** | [`docs/07-contracts.md`](../../07-contracts.md), [`docs/08-testing-strategy.md`](../../08-testing-strategy.md), [`docs/09-pr-workflow-and-ci.md`](../../09-pr-workflow-and-ci.md) |

## Learning objectives

1. Explain how "tests before the PR" becomes a mechanical fact: skill → Stop hook → pre-push gate → CI → PR template.
2. Describe the layers that keep a contract intact but changeable, and apply the pattern to other contract types.
3. Describe the layered review model: machine, AI self-review, AI contract review, human.
4. Read a pull request as a non-developer using the acceptance-criteria-to-tests table.

## Topics

1. **The feedback loop is the control.** A fast, reliable test command and a verification script that is quiet
   on success and specific on failure. The agent runs it far more often than a human would, so its speed matters.
2. **Tests before the PR.** The pyramid in this repository: unit tests (`*Test`, plain Java, milliseconds),
   integration and contract tests (`*IT`, Spring context, every response validated against the OpenAPI file),
   architecture rules (ArchUnit), a coverage gate (JaCoCo). Tests named after acceptance criteria (`ac2_…`).
   AI-specific smells: tests written after the code that mirror it, happy paths only, over-mocking, weakened
   assertions, coverage gaming. The countermeasure for each.
3. **Contracts: intact but changeable.** A dedicated top-level folder; nested `CLAUDE.md`; a human-confirm hook
   on every edit; contract tests that fail when code and spec disagree in either direction; a process check
   (version, changelog, ADR); a breaking-change diff in CI; CODEOWNERS. The same pattern for events, schemas,
   protobuf, library APIs and consumer-driven contracts.
4. **The PR workflow.** Spec → plan → branch → TDD → `pr-ready` → reviewer subagent → gate → PR from template →
   CI runs the same scripts → human review by code owners → merge. The local gate and the CI gate are the same
   script, so they cannot disagree.
5. **Review in layers.** Machines check build, tests, coverage, architecture and compatibility. The reviewer
   subagent checks spec conformance, test quality, scope and docs. Humans review intent, design, risk and business
   correctness. Branch protection makes human approval mandatory and self-merge impossible.
6. **For product.** You own acceptance criteria, out-of-scope and spec status. Review a PR by reading the
   AC-to-tests table and the test names, then the contract-impact section, then the follow-ups.

## Key messages

- Make "tested" a fact the system checks, not a promise the agent makes.
- Never let the agent edit a contract to make a test pass. Fix the code.
- Small commits, one task per branch, a PR description the reviewer can scan in a minute.

## Demo in this repository

1. **Break the contract test.** Remove `CANCELLED` from the `status` enum in
   `contracts/openapi/orders-api.v1.yaml` and run `./gradlew integrationTest`. `OrdersApiContractIT` fails with
   a schema enum violation. Restore the file.
2. **Push with a red build.** Introduce a failing assertion and ask the agent to push. The pre-PR gate blocks
   with the filtered failure. Show that CI would have failed on the same script.
3. **`/pr-ready`** on a finished branch. The gate runs, `code-reviewer` returns MUST FIX / SHOULD FIX, and the
   PR description comes out of the template with the AC table filled.

## Governance controls introduced

| Control | Layer | Where | Owner |
|---|---|---|---|
| Tests accompany production changes | guarantee | `scripts/check-tests-present.sh` in the Stop hook, the gate and CI | tech leads |
| Pre-push gate equals CI gate | guarantee | `scripts/verify.sh`, `.claude/hooks/pre-pr-gate.sh`, `.github/workflows/ci.yml` | tech leads, platform |
| Contract protection | guarantee | `contracts/`, `protect-contracts.sh`, `OrdersApiContractIT`, `check-contract-change.sh`, oasdiff job, CODEOWNERS | API owners |
| Architecture and coverage rules | guarantee | `ArchitectureTest`, JaCoCo thresholds in `build.gradle.kts` | tech leads |
| PR evidence | oversight | `.github/pull_request_template.md`, `pr-ready` skill | tech leads |
| Human approval and ownership | guarantee | branch protection, `.github/CODEOWNERS` | tech leads, API owners |

## Exercises

1. **Map your gate.** For your repository, write the equivalent of `verify.sh`: the commands, the expected
   runtime, and how to filter output to failures only.
2. **Classify three contract changes** from your own API history as additive or breaking, using
   `.claude/skills/contract-change/compatibility-rules.md`.
3. **Product exercise.** Read the PR description produced in the demo without opening a Java file. Is every AC
   covered? What is in follow-ups?

## Common questions

- *"Our test suite takes 40 minutes."* Split the fast loop (per module unit tests) from the full gate (pre-push
  and CI). A slow gate gets bypassed by humans and agents alike.
- *"What if the contract is actually wrong?"* Then change it on purpose with the `contract-change` skill: classify,
  version, record, review. The hook asks, it does not forbid.
- *"Can the reviewer subagent approve the PR?"* No, and it should not. It produces a verdict a human reads.

## Further reading

- [`docs/07-contracts.md`](../../07-contracts.md), [`docs/08-testing-strategy.md`](../../08-testing-strategy.md),
  [`docs/09-pr-workflow-and-ci.md`](../../09-pr-workflow-and-ci.md)
- Worked example ORD-002: [`docs/11-playbook-java-developers.md`](../../11-playbook-java-developers.md)
- Product view: [`docs/12-playbook-project-managers.md`](../../12-playbook-project-managers.md)
