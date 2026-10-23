# Knowledge checks

Short checks per module. Use them at the end of a session or as a self-test. Answers follow each block.

## Module 01: Foundations

1. Name the four kinds of action Claude Code can take, and one risk attached to each.
2. Why is "please always write tests" in `CLAUDE.md` guidance rather than a control?
3. Which session mode lets the agent plan without being able to edit files?
4. With whose access does the agent operate by default?

*Answers: (1) read: secrets or sensitive data in context; edit: unreviewed or scope-creeping changes; run:
destructive commands; call: data leaving through integrations. (2) Instructions can be forgotten, misread or
pushed out of context; a hook or test runs every time. (3) Plan mode. (4) The developer's own.*

## Module 02: Governance framework

1. Order the settings layers by precedence, highest first.
2. Where should a rule go if breaking it would hurt?
3. Who owns the organisation layer, the project layer and the user layer?
4. Why is the project settings file committed to Git?

*Answers: (1) managed (organisation) settings, then command-line flags, then local project settings, then shared
project settings, then user settings. (2) In a permission rule, hook, test or CI check, with at most one line
of guidance. (3) Security and platform; tech leads; each developer. (4) So the team shares it, it is reviewed in
pull requests and protected by CODEOWNERS.*

## Module 03: Context and memory

1. What are the five parts of a good root `CLAUDE.md`?
2. When does a `.claude/rules/` file with a `paths:` block load?
3. Why prefer a link over an `@import` for an architecture document?
4. Name two commands that show what is loaded and how full the context is.

*Answers: (1) one-line identity; commands; architecture in three lines; five to seven non-negotiables each backed
by a mechanism; a map. (2) Only when the agent works on files matching the paths. (3) An import inlines the file
every session; a link loads it only when needed. (4) `/memory` and `/context`.*

## Module 04: Permissions and hooks

1. What is the difference between `ask` and `deny`?
2. What does a hook's exit code 2 mean, and where does its stderr go?
3. Why do the hooks call the same scripts as CI?
4. Which permission mode should managed settings disable, and why?

*Answers: (1) `ask` requires a human confirmation each time; `deny` never runs. (2) Block the action; stderr is
fed back to the agent as an instruction. (3) So local and CI cannot disagree, and a CI failure means something
environmental rather than a skipped check. (4) Bypass permissions mode, because it removes every confirmation
including those that protect against prompt injection and destructive commands.*

## Module 05: Skills, subagents and plugins

1. Skill, `CLAUDE.md` or subagent: where does "the contract is changed before the code" belong?
2. How does a subagent enforce separation of duties?
3. What is the always-on cost of having twenty skills?
4. What does a plugin distribute, and why does that matter at enterprise scale?

*Answers: (1) A skill: it is an ordered procedure. (2) Its tool list is fixed; a reviewer without Edit or Write
cannot change what it reviews. (3) Twenty names and descriptions; bodies load on demand. (4) Skills, subagents,
hooks, slash commands and MCP configuration, versioned; one reviewed standard reaches every repository.*

## Module 06: MCP and integrations

1. What should you check before adding an MCP server?
2. Where do credentials for a project-scoped server belong?
3. Name two ways to limit what an MCP server can do.
4. Why must hooks cover MCP tools as well as the shell?

*Answers: (1) Whether a CLI already does the job, and whether most of the team needs it. (2) In environment
variables referenced from the configuration, never literal tokens in Git. (3) Read-only tokens; scope to one
project, space or non-production database; an organisation allowlist. (4) Guardrails must cover every path to the
outside world, such as PR creation through an MCP tool.*

## Module 07: Quality gates and the SDLC

1. List the five mechanisms that make "tests before the PR" a fact.
2. What happens if a field is added in code but not in the OpenAPI contract?
3. When a contract test fails, what is the correct fix?
4. What do humans review that machines and AI reviewers do not?

*Answers: (1) The `tdd-feature` skill, the Stop hook, the pre-push gate, CI running the same scripts, the PR
template's AC table. (2) The contract test fails because the schema forbids additional properties. (3) Fix the code
to match the contract; change the contract only on purpose through the contract-change procedure. (4) Intent,
design, risk and business correctness.*

## Module 08: Security, privacy and compliance

1. Name three deployment options for an enterprise.
2. Give two examples of prompt injection sources and one mitigation.
3. What is the first control against secrets reaching the agent's context?
4. Why should Claude in CI be read-only?

*Answers: (1) Anthropic API through Claude for Enterprise, AWS Bedrock, Google Vertex AI, Microsoft Foundry, or an
LLM gateway. (2) A fetched web page, a dependency's README, an issue comment; mitigations: permission prompts for
new actions, read-only agents, human review. (3) `deny` rules on secret paths in managed settings. (4) Content it
reads is untrusted; a read-only agent cannot be turned into an author.*

## Module 09: Observability, cost and ROI

1. Which standard does Claude Code use to export telemetry?
2. Name three KPIs that measure outcomes rather than activity.
3. What is wrong with "lines of code written" as a target?
4. What is a fair comparison design for a pilot?

*Answers: (1) OpenTelemetry. (2) First-pass CI green rate, review rounds per PR, lead time from spec Ready to
merge, escaped defects. (3) It measures activity and is easy to inflate. (4) Similar tasks split between a guarded
and an unguarded setup, swapped next round, with outcomes recorded per task.*

## Module 10: Adoption and change management

1. What should a repository set up first?
2. In what order of preference does a repeated correction become permanent?
3. Name the five maturity levels.
4. Why review the material after each Claude Code release?

*Answers: (1) A reliable verification script and the commands in `CLAUDE.md`. (2) A test, then a hook, then a
rule. (3) Ad hoc, managed, guarded, standardised, optimised. (4) Setting and feature names change; the material
must match the version in use.*
