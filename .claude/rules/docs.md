---
paths:
  - "docs/**"
  - "**/*.md"
---
# Documentation rules

- Diagrams are Mermaid in fenced code blocks. They render on GitHub and diff cleanly. No binary images for
  architecture.
- Charts come from `scripts/docs/chart.py` (or the Mermaid chart `scripts/docs/perf_report.py` emits), generated from
  a CSV committed next to the document; commit the SVG and the CSV, never a hand-drawn image.
- Architecture documents and performance reports follow `docs/templates/tech-doc/` (`tech-doc` and `perf-report`
  skills). Numbers are generated, never typed.
- When code changes a flow shown in `docs/architecture/`, update the diagram in the same PR (`update-diagrams` skill).
- Keep docs task-oriented. Link to code with repo-relative paths; don't paste large code blocks that will rot.
- Specs (`docs/specs/`) are owned by product. Don't change acceptance criteria without a human asking.
