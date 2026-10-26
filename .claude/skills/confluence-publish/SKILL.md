---
name: confluence-publish
description: Publish a Markdown document from this repo (with Mermaid diagrams, tables, code blocks and images) as a Confluence page, through the Atlassian MCP server, the REST script scripts/docs/confluence_publish.py, or a manual paste. Use when asked to put a document, design, report or runbook on Confluence, or to update an existing Confluence page from Markdown.
---

# Publish to Confluence

1. **Confirm the target with the user:** space key, parent page (id or URL), page title, and whether an existing page
   should be updated. Never create pages in a space the user did not name. Titles are unique per space, so publishing
   to an existing title updates that page.
2. **Dry run and inspect:**
   ```bash
   python3 scripts/docs/confluence_publish.py <doc.md> --dry-run --strict --toc --page-properties --theme <theme>
   ```
   `--theme` (`--list-themes`; `atlassian` looks native in Confluence) colours the rendered diagrams; use the same theme
   as the document's charts.
   Read `build/docs/<name>/page.storage.xml` and look at the rendered diagrams in the same folder. Fix Mermaid errors in
   the Markdown. Unsupported Markdown comes through as plain text: simplify the source rather than editing the XML.
   Relative links need `--link-base <repo blob URL>` to stay clickable.
3. **Pick the route:**

   | Route | When | How |
   |---|---|---|
   | Atlassian MCP server | Confluence tools are available in this session | create or update the page with the Markdown body, then attach the diagram images from `build/docs/<name>/` with the script (`--page-id <id>`) or by hand, because the Atlassian MCP tools do not upload attachments at the time of writing |
   | REST script | credentials are in the environment | `CONFLUENCE_BASE_URL`, `CONFLUENCE_EMAIL` + `CONFLUENCE_API_TOKEN` (Cloud) or `CONFLUENCE_TOKEN` (Data Center, add `--api v1`); run the step 2 command without `--dry-run`, plus `--space KEY --parent-id ID [--labels a,b]` |
   | Manual paste | no credentials and no MCP | create the page, paste the Markdown (the Cloud editor converts headings, lists, tables and code), insert the images from `build/docs/<name>/` |

4. **Secrets:** tokens come from environment variables or a secret manager. Never write them into files, commands in
   documents, or the chat, and never echo them.
5. **Verify in the browser:** table of contents, page properties, diagrams, tables, panels, code blocks. Record the page
   URL in the document's metadata table and in the PR description.
6. **Updates are re-runs** of the same command: the script bumps the page version with a message and replaces
   attachments by file name. Markdown stays the source of truth; if someone edits the page in Confluence, copy the change
   back to Markdown before the next publish.
