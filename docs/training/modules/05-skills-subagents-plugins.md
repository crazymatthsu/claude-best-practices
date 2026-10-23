# Module 05: Skills, subagents and plugins. Standardising how work is done

| | |
|---|---|
| **Audience** | tech leads, developers, platform engineers who build the enterprise plugin |
| **Duration** | 60 min |
| **Prerequisites** | modules 01 and 03 |
| **Materials** | [`docs/03-skills.md`](../../03-skills.md), [`docs/04-subagents.md`](../../04-subagents.md), `.claude/skills/`, `.claude/agents/` |

## Learning objectives

1. Choose between `CLAUDE.md`, a skill and a subagent for a given need.
2. Write a skill with a trigger description, ordered steps, explicit stop-and-ask points and a verification step.
3. Design a least-privilege subagent with a fixed output format.
4. Explain how plugins and an internal marketplace distribute one reviewed standard to every repository.

## Topics

1. **Skills.** A folder with `SKILL.md` (frontmatter plus steps) and optional reference files. Only name and
   description are always in context; the body loads on match or on `/name`. Frontmatter options worth knowing:
   `allowed-tools` restricts tools while the skill runs; `disable-model-invocation: true` makes a skill manual
   only, which is right for releases and other risky procedures.
2. **Skills in this repository.** `tdd-feature` (spec → test matrix → red → green → gate), `contract-change`
   (classify, version, changelog, ADR), `pr-ready` (gate, reviewer, PR template), `write-adr`, `write-spec`,
   `update-diagrams`, `tech-doc`, `perf-report`, `confluence-publish`.
3. **When to write a skill.** The same multi-step instruction typed more than twice. A procedure with a correct
   order. A process shared by several roles. Never for something one command does.
4. **Subagents.** A separate agent with its own context, tool list and prompt (`.claude/agents/<name>.md`).
   Design rules: least privilege (reviewers cannot edit), fixed output format, a clear "never" list,
   description says when to use it, independent jobs run in parallel. The built-in Explore agent for read-only
   searches.
5. **Separation of duties as code.** `code-reviewer` and `contract-guardian` have no Edit or Write tool.
   `test-writer` may edit tests and never production code or contracts. A test that exposes a bug is reported,
   not "fixed".
6. **Plugins and marketplaces.** A plugin bundles skills, subagents, hooks, slash commands and MCP configuration.
   Marketplaces are catalogues of plugins; an organisation can host one in an internal Git repository and
   developers install from it with `/plugin`. The plugin is how the reference configuration reaches two hundred
   repositories without two hundred copies. Managed settings register the internal marketplace
   (`extraKnownMarketplaces`), force-enable or block plugins (`enabledPlugins`), and restrict sources
   (`strictKnownMarketplaces`, `blockedMarketplaces`, `disableSideloadFlags`); `strictPluginOnlyCustomization`
   limits skills, agents, hooks and MCP to plugins and managed settings. Organisation-wide subagents can also
   ship in the managed settings directory. See module 02 for the locks.
7. **Governance of the extension surface.** Who may publish enterprise-wide skills and agents. Review before
   publishing, like any dependency. Version the plugin; repositories pin a version. Risky skills manual-only.
   Agent prompts stay factual and short.

## Key messages

- Skills encode **order**: contract before code, test before implementation, gate before push.
- Subagents encode **separation of duties**: the reviewer cannot change what it reviews.
- Plugins encode **distribution**: one reviewed standard, many repositories, one upgrade path.

## Demo in this repository

1. Open [`.claude/skills/contract-change/SKILL.md`](../../../.claude/skills/contract-change/SKILL.md) and its
   reference file `compatibility-rules.md`. Show the description, the stop-and-ask points and the verification
   step.
2. Ask: *"Add an optional `cancellationNote` field to `Order`."* Watch the skill trigger from the description
   alone, classify the change as additive and ask before touching the contract.
3. Run `/agents`. Open [`.claude/agents/code-reviewer.md`](../../../.claude/agents/code-reviewer.md) and point
   at the `tools:` line and the output format. Run it on a branch and read the verdict.

## Governance controls introduced

| Control | Layer | Owner | Enforcement |
|---|---|---|---|
| Standard workflows as skills | guidance | tech leads, platform | reviewed in PRs; distributed by plugin |
| Read-only reviewer and guardian subagents | guarantee (tool list) | tech leads | `tools:` frontmatter |
| Manual-only skills for risky procedures | guarantee | tech leads | `disable-model-invocation: true` |
| Internal plugin marketplace | guarantee (distribution) | platform | pre-registered in managed settings; versioned |

## Exercises

1. **Write a skill** for a procedure your team repeats (a release checklist, a migration, an incident
   post-mortem). Include at least one stop-and-ask point and a final verification command.
2. **Define a read-only `security-reviewer` subagent**: tools, the checks it runs, its output format.
3. **Design the enterprise plugin.** List what goes in (skills, agents, hooks, MCP config) and what stays
   repository-specific. Decide who reviews a change to it.

## Common questions

- *"Skill or CLAUDE.md?"* Facts and rules in `CLAUDE.md`; procedures in skills; big reading jobs in subagents.
- *"Can a subagent escalate its own permissions?"* No. Its tool list is fixed in its definition and permission
  rules still apply to the tools it has.
- *"Do plugins replace repository configuration?"* They carry the shared part. Commands, non-negotiables and
  path rules stay in the repository.

## Further reading

- [`docs/03-skills.md`](../../03-skills.md), [`docs/04-subagents.md`](../../04-subagents.md)
- [`docs/13-adopting-and-measuring.md`](../../13-adopting-and-measuring.md), the copy list
