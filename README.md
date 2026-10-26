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
  skills/                     # tdd-feature, contract-change, pr-ready, write-adr, write-spec, update-diagrams,
                              # tech-doc, perf-report, confluence-publish (architecture docs, perf reports, Confluence)
  agents/                     # code-reviewer, test-writer, contract-guardian
  hooks/                      # protect-contracts, pre-pr-gate, require-tests-on-stop
contracts/
  CLAUDE.md                   # nested memory: loaded only when working on contracts
  openapi/orders-api.v1.yaml  # source of truth for the HTTP API
  CHANGELOG.md
scripts/verify.sh             # the pre-PR gate: same checks locally, in hooks, and in CI
scripts/docs/                 # perf_report.py, chart.py, confluence_publish.py, palette_check.py, themes/: tables, charts, Confluence
build.gradle.kts              # Gradle 9 build: test + integrationTest suites, JaCoCo gate, Java 25 toolchain
src/main, src/test, src/integrationTest  # demo Spring Boot 4.1 orders-service + unit and integration tests
docs/                         # the guide (14 topics), architecture, ADRs, specs, templates (incl. templates/tech-doc), examples
.github/                      # CI, PR template, CODEOWNERS
```

## Try it

```bash
scripts/verify.sh           # build + unit + integration/contract + architecture + coverage
./gradlew bootRun           # then:
curl -s -XPOST localhost:8080/api/v1/orders -H 'content-type: application/json' \
  -d '{"customerId":"c1","lines":[{"sku":"A","quantity":2,"unitPrice":{"amount":10,"currency":"EUR"}}]}'
```

Technical documentation (architecture docs, performance reports, Confluence pages), see [docs/14](docs/14-technical-documentation.md):

```bash
python3 scripts/docs/perf_report.py docs/examples/perf/orders-api-sample.jtl --slo "p95<=300,error_rate<=1"
python3 scripts/docs/confluence_publish.py docs/templates/tech-doc/architecture.md --dry-run   # renders the diagrams
```

Then open Claude Code in this folder and try:

- `Implement a "mark order as shipped" endpoint using the tdd-feature skill. Stop after the plan.`
  Watch it pick up the contract-change skill, ask before touching the contract, and write tests first.
- `Change the OrderResponse total field name to grandTotal.` The contract-change skill should classify this as
  **breaking** and route it to a v2 plus an ADR, not an in-place edit.
- `Use the tech-doc skill to write the architecture document for this service from the code.` Watch it fill
  `docs/templates/tech-doc/architecture.md` with context, data-flow and sequence diagrams derived from the code.

Requirements: JDK 25 (or let the Gradle toolchain resolver download it), `jq` (used by the hooks), Python 3.9+ for
`scripts/docs/` (optional: mermaid-cli to render diagrams, see docs/14).
Gradle itself comes from the wrapper (`./gradlew`, Gradle 9.8).
