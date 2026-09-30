---
name: tdd-feature
description: Implement a feature or bug fix test-first from a spec in docs/specs/ or an issue. Use whenever you are asked to add or change behaviour in src/main (new endpoint, business rule, validation, bug fix).
---

# Test-first feature workflow

Work through these steps in order. Don't write production code before step 3 has a failing test.

## 1. Understand
- Read the spec (`docs/specs/<ID>-*.md`) or issue. Only implement specs with status `Ready` (or a bug with a clear
  reproduction). Pull out the acceptance criteria as a numbered list.
- If a criterion is ambiguous or missing (error cases, limits, who is allowed), **stop and ask**.
- Check whether the HTTP contract must change. If yes, run the `contract-change` skill first, then come back.

## 2. Plan (show this to the user before coding anything non-trivial)
- The files you'll touch, by layer (domain / application / api / infrastructure).
- A test matrix: one row per acceptance criterion → unit test name + IT test name.

  | AC | Unit test (`*Test`) | Integration test (`*IT`) |
  |----|---------------------|--------------------------|
  | AC1 | `OrderTest.Cancel.ac1_…` | `OrdersApiContractIT.cancelOrder_…_returns200…` |

## 3. Red
- Write the unit tests for domain rules first. Run `./gradlew test --tests <Class>` and confirm they **fail for the
  right reason** (an assertion, not a compile error in unrelated code).
- Write the integration test(s) for HTTP behaviour in `src/integrationTest`, including `.andExpect(matchesContract())`.

## 4. Green
- Implement the smallest change that makes the tests pass. Put rules in the domain aggregate.
- Run `./gradlew test` often. Run `./gradlew check` once the unit tests pass.

## 5. Refactor and document
- Remove duplication and keep names aligned with the spec's vocabulary.
- If a flow in `docs/architecture/` changed, run the `update-diagrams` skill.

## 6. Hand off
- Run `scripts/verify.sh` and get it green.
- Summarise for the user: ACs → tests mapping, files changed, anything deliberately left out.

## Don'ts
- Don't write tests that assert the implementation (mock call counts, private state) instead of behaviour.
- Don't weaken, skip or delete existing tests to get green.
- Don't add behaviour the spec doesn't ask for. Note it as a follow-up instead.
