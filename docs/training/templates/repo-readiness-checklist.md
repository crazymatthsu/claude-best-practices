# Repository readiness checklist

*Complete before Claude Code is used for real work on a repository. Commit the filled checklist with the
configuration pull request. Owner: the repository's tech lead. Reference implementation: this repository.*

| Repository | Tech lead | Date | Plugin version |
|---|---|---|---|
| [name] | [name] | [YYYY-MM-DD] | [x.y.z or "copied"] |

## A. Build and verification

- [ ] A single verification command exists (`scripts/verify.sh` or equivalent) that runs the build, unit tests,
      integration tests and any architecture or coverage gates.
- [ ] It is quiet on success (one line) and prints only failures on error.
- [ ] It runs in under [5] minutes locally; a faster per-module loop exists for day-to-day work.
- [ ] CI runs the same scripts, so local and CI cannot disagree.

## B. Context

- [ ] Root `CLAUDE.md` is under about 50 lines and has the five parts: identity, commands, architecture in three
      lines, five to seven non-negotiables each backed by a mechanism, a map.
- [ ] Area-specific rules live in `.claude/rules/*.md` with `paths:`.
- [ ] Directories with different rules (contracts, generated code, legacy) have a nested `CLAUDE.md`.
- [ ] No secrets, customer data or generic style guides are in any instruction file.
- [ ] `/memory` and `/context` were checked: always-loaded context is small.

## C. Permissions and hooks

- [ ] `.claude/settings.json` has `allow` for the build, tests and read-only git; `ask` for push, PR creation,
      build and CI configuration, hooks and settings; `deny` for secret paths and destructive commands.
- [ ] The three standard hooks are configured and their scripts are executable: human confirmation on protected
      files, pre-push gate, tests required before stopping.
- [ ] Each hook was triggered once on purpose and blocked or asked as expected.
- [ ] Organisation managed settings are present on developer machines (ask platform), so bypass mode is disabled
      and the deny list cannot be removed locally.

## D. Ownership and CI

- [ ] CODEOWNERS covers `contracts/`, `.claude/settings.json`, `.claude/hooks/`, `scripts/`, `docs/adr/`,
      `docs/specs/`.
- [ ] Branch protection on the default branch: PR required, at least one human approval, status checks required.
- [ ] The PR template with the acceptance-criteria-to-tests table is in place.
- [ ] If Claude runs in CI, it is read-only or comment-only, uses a dedicated identity, and the action version is pinned.

## E. Contracts (if other teams depend on this repository)

- [ ] Contracts live in a dedicated top-level folder with a nested `CLAUDE.md` and a CHANGELOG.
- [ ] A contract test fails when code and contract disagree.
- [ ] A compatibility check (oasdiff, `buf breaking`, schema registry, `japicmp`, …) runs in CI.
- [ ] The `contract-change` procedure (skill) is installed and understood by the team.

## F. Workflows

- [ ] Skills installed: `tdd-feature`, `pr-ready`, `write-spec`, `write-adr` (plus `contract-change` where relevant).
- [ ] Subagents installed: `code-reviewer` (read-only), `test-writer` (tests only).
- [ ] Spec template available to product; at least one spec is `Ready`.

## G. Integrations

- [ ] Any `.mcp.json` lists only servers from the approved catalogue, with credentials via environment variables.
- [ ] Tokens are read-only and scoped (one project, one space, non-production data).

## H. People and measurement

- [ ] The team completed the developer lab (WF-01, WF-02); the tech lead completed the tech-lead workshop.
- [ ] A champion is named and attends office hours.
- [ ] Four weeks of baseline KPIs are recorded in the [scorecard](kpi-scorecard.md).

## Sign-off

| Role | Name | Date |
|---|---|---|
| Tech lead | | |
| Platform | | |
| Security (if contracts or integrations) | | |
