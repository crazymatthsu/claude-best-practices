---
paths:
  - "docs/**"
  - "**/*.md"
---
# Documentation rules

- Diagrams are Mermaid in fenced code blocks. They render on GitHub and diff cleanly. No binary images for
  architecture.
- When code changes a flow shown in `docs/architecture/`, update the diagram in the same PR (`update-diagrams` skill).
- Keep docs task-oriented. Link to code with repo-relative paths; don't paste large code blocks that will rot.
- Specs (`docs/specs/`) are owned by product. Don't change acceptance criteria without a human asking.
