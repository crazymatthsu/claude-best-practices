---
name: tech-doc
description: Write professional technical documentation for a system or feature (architecture or solution design document, technical design, integration overview) with Mermaid diagrams (context, containers, data flow, sequence, state, deployment), tables and charts, as Markdown that renders on GitHub and publishes to Confluence. Use when asked to document an architecture, design, data flow, integration or technical approach, or to produce a Confluence page from the code.
---

# Technical documentation

1. **Pick the document and name the audience.**

   | Need | Use |
   |---|---|
   | architecture or solution design, integration overview, technical design | `docs/templates/tech-doc/architecture.md` (this skill) |
   | load, stress or soak test results | `perf-report` skill |
   | one decision with alternatives | `write-adr` skill |
   | requirements with acceptance criteria | `write-spec` skill |

   Write for the least informed reader named in the metadata table (usually a new engineer or on-call).
2. **Gather facts before writing.** Read, in this order: entry points (controllers, listeners, schedulers), application
   services, the domain model, repositories and migrations, contracts (`contracts/`), configuration (`application*.yml`),
   build and deployment files, CI, dashboards and existing ADRs. Keep the list of sources; it becomes the References section.
3. **Never invent.** Numbers, SLAs, owners and versions come from a source you can link. Anything unverified is written as
   `TBD (owner)` and listed under Open questions. Don't guess business rules; ask.
4. **Copy the template** to `docs/architecture/<system>.md` (or `docs/design/<TICKET>-<topic>.md`). Fill every section or
   delete it: no placeholder text, no empty headings, no "lorem". Keep the HTML guidance comments while drafting; the
   publisher drops them.
5. **Diagrams:** one question per diagram, using the patterns in [diagram-cookbook.md](diagram-cookbook.md). Derive them
   from the code and use its names (same rules as `update-diagrams`): 12 nodes or fewer, labelled edges, a one-line
   caption that states the takeaway. A data-flow diagram always comes with its flow table (volume, format, classification).
6. **Tables and charts:** every table has units in the header and a stated source and date. Numbers are generated, never
   typed: `perf-report` skill, `scripts/docs/perf_report.py`, `scripts/docs/chart.py`. Charts have one measure and one
   y-axis, a labelled SLO line, a legend for two or more series, and the same data as a table.
7. **Quality pass** against [quality-checklist.md](quality-checklist.md). Then re-read as the audience: can an on-call
   engineer find the failure modes in a minute? Can a new engineer find where a request enters the code?
8. **Deliver.** Commit the Markdown; diagrams stay Mermaid source, chart SVGs and their CSVs may sit in `images/` next to
   the doc, rendered diagram PNGs are build output. Publish with the `confluence-publish` skill when asked and record the
   page URL in the metadata table. Mention the document in the PR description.
