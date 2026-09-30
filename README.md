# claude-best-practices

A reference Java project showing how to guide **Claude Code** on large codebases. It keeps context lean, keeps
API contracts intact but changeable, and makes unit and integration tests mandatory before a PR.

**Start here → [docs/README.md](docs/README.md)**

## What's inside

```
CLAUDE.md                     # lean, always-loaded project memory
.claude/
  settings.json               # permissions + hooks (team-shared)
  rules/                      # path-scoped rules: java.md, testing.md, docs.md
  skills/                     # tdd-feature, contract-change, pr-ready, write-adr, write-spec, update-diagrams
  agents/                     # code-reviewer, test-writer, contract-guardian
  hooks/                      # protect-contracts, pre-pr-gate, require-tests-on-stop
contracts/
  CLAUDE.md                   # nested memory: loaded only when working on contracts
  openapi/orders-api.v1.yaml  # source of truth for the HTTP API
  CHANGELOG.md
scripts/verify.sh             # the pre-PR gate: same checks locally, in hooks, and in CI
build.gradle.kts              # Gradle 9 build: test + integrationTest suites, JaCoCo gate, Java 25 toolchain
src/main, src/test, src/integrationTest  # demo Spring Boot 4.1 orders-service + unit and integration tests
docs/                         # the guide (13 topics), architecture, ADRs, specs, templates
.github/                      # CI, PR template, CODEOWNERS
```

## Try it

```bash
scripts/verify.sh           # build + unit + integration/contract + architecture + coverage
./gradlew bootRun           # then:
curl -s -XPOST localhost:8080/api/v1/orders -H 'content-type: application/json' \
  -d '{"customerId":"c1","lines":[{"sku":"A","quantity":2,"unitPrice":{"amount":10,"currency":"EUR"}}]}'
```

Then open Claude Code in this folder and try:

- `Implement a "mark order as shipped" endpoint using the tdd-feature skill. Stop after the plan.`
  Watch it pick up the contract-change skill, ask before touching the contract, and write tests first.
- `Change the OrderResponse total field name to grandTotal.` The contract-change skill should classify this as
  **breaking** and route it to a v2 plus an ADR, not an in-place edit.

Requirements: JDK 25 (or let the Gradle toolchain resolver download it), `jq` (used by the hooks).
Gradle itself comes from the wrapper (`./gradlew`, Gradle 9.8).
