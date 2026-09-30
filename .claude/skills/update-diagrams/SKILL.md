---
name: update-diagrams
description: Update the Mermaid architecture, sequence and state diagrams in docs/ to match the code. Use after changing a flow, adding an endpoint, changing layers, or when asked to document or visualise the system.
---

# Keep diagrams true

1. Find the affected diagrams: `grep -rl '```mermaid' docs/`.
2. Derive the diagram from the **code**, not from memory: read the controller → service → domain path.
3. Diagram types:
   - Component and layer view → `flowchart` in `docs/architecture/overview.md`
   - Request flow → `sequenceDiagram` (one per non-trivial use case)
   - Lifecycle → `stateDiagram-v2` (must match the transitions in the aggregate, e.g. `Order`)
4. Keep diagrams small (≤ 12 nodes). Split them rather than cram.
5. Use the names from the code (class/endpoint names) so readers can grep them.
6. Check the Mermaid syntax. Every block must open with a valid diagram type, with balanced brackets and quotes.
7. Mention the diagram update in the PR description.
