---
name: pr-ready
description: Prepare the current branch for a pull request. Run the gate, check test coverage of acceptance criteria, check docs/contract impact, and draft the PR description from the template. Use when the user says the work is done, asks to open a PR, or asks "is this ready?".
---

# PR readiness

1. `scripts/changed-files.sh`: list what changed. Group by layer.
2. **Tests**: for each production change, name the test that covers it. For each acceptance criterion in the
   linked spec, name the unit test and the IT test. Missing ones → write them now (`tdd-feature` skill).
3. **Contract**: if `contracts/` changed, confirm `contract-change` was followed and fill in "Contract impact".
4. **Docs**: if a flow or boundary changed, check that `docs/architecture/` diagrams are updated. New decisions
   need an ADR.
5. **Gate**: run `scripts/verify.sh` and get it green. Paste only the summary line, not the log.
6. **Self-review**: run the `code-reviewer` subagent on the diff and address every "must fix".
7. **Describe**: fill `.github/pull_request_template.md` completely. Leave no placeholder text. Keep it short
   and factual: what, why, how it was tested, contract impact, follow-ups.
8. Ask the user before pushing or opening the PR.
