# orders-service

Spring Boot 4.1 / Java 25 service, built with Gradle 9 (Kotlin DSL, wrapper). Demo project for guardrailing Claude Code. The guides are in `docs/` (start at `docs/README.md`).

## Commands
- Build + all tests + coverage gate: `./gradlew check` (~1 min; always use the wrapper, never a system `gradle`)
- Unit tests only (fast loop): `./gradlew test`
- One test: `./gradlew test --tests OrderTest` or `./gradlew integrationTest --tests OrdersApiContractIT`
- Pre-PR gate (same checks as CI): `scripts/verify.sh`

## Architecture (enforced by `ArchitectureTest`)
`api` → `application` → `domain` ← `infrastructure`. `domain` is plain Java: no Spring, no Jakarta.
Business rules live in the domain aggregate (`Order`), not in services or controllers.
Details and diagrams: `docs/architecture/overview.md`. Read it only when you change a layer boundary.

## Non-negotiables
1. **Contract first.** `contracts/openapi/*.yaml` is the source of truth for the HTTP API. Never edit a
   contract to make code or tests pass. To change one, use the `contract-change` skill.
2. **Tests before the PR.** Every change under `src/main` comes with tests: unit tests
   (`src/test`, `*Test`, no Spring) for logic, and integration tests (`src/integrationTest`, `*IT`) for HTTP behaviour, validated
   against the contract. Write the failing test first (`tdd-feature` skill).
3. **Green before push.** Run `scripts/verify.sh` and get it passing before `git push` or opening a PR. A hook
   enforces this. Do not bypass it.
4. **No silent scope creep.** Only change what the task or spec asks for. List any follow-ups in the PR
   description; don't implement them.
5. **Decisions are recorded.** Architecture or contract decisions go in `docs/adr/` (`write-adr` skill).

## Where things are
- Feature specs with acceptance criteria: `docs/specs/` (e.g. `ORD-002-cancel-order.md`)
- ADRs: `docs/adr/`. Contract history: `contracts/CHANGELOG.md`
- Path-scoped coding rules are loaded automatically from `.claude/rules/`

## Working style
- For anything bigger than a small fix, plan first. Read the spec, list the files you'll touch and the tests
  you'll add, then implement.
- Prefer small, reviewable commits. Commit messages: `ORD-123: imperative summary`.
- If a requirement is ambiguous, ask. Don't guess at business rules.
