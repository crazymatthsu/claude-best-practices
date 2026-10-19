#!/usr/bin/env python3
"""Publish a Markdown document (Mermaid diagrams, tables, code, images) as a Confluence page.

Pipeline: Markdown -> render ```mermaid blocks to PNG/SVG with mermaid-cli (mmdc) -> Confluence storage format
-> create or update the page -> upload attachments (diagrams and local images). Standard library only.

Always dry-run first (no network; writes build/docs/<name>/page.storage.xml and the rendered diagrams):
  python3 scripts/docs/confluence_publish.py docs/architecture/overview.md --dry-run

Confluence Cloud (API token from https://id.atlassian.com/manage-profile/security/api-tokens):
  export CONFLUENCE_BASE_URL=https://acme.atlassian.net/wiki CONFLUENCE_EMAIL=you@acme.com CONFLUENCE_API_TOKEN=...
  python3 scripts/docs/confluence_publish.py docs/architecture/overview.md --space ARCH --parent-id 123456 \
      --title "Orders service: architecture" --labels architecture,orders --toc --page-properties

Confluence Data Center / Server (personal access token):
  export CONFLUENCE_BASE_URL=https://confluence.acme.com CONFLUENCE_TOKEN=...
  python3 scripts/docs/confluence_publish.py doc.md --api v1 --space ARCH --parent-id 123456

Supported Markdown: headings, paragraphs, bold/italic/strikethrough/inline code, links, images, bullet/numbered/task
lists (nested), tables, fenced code (code macro), ```mermaid (rendered image), blockquotes and GitHub alerts
(> [!NOTE] / [!TIP] / [!IMPORTANT] / [!WARNING] / [!CAUTION] become panels), horizontal rules, [[TOC]], and HTML
comments (dropped, so template guidance never reaches the page). Anything else is passed through as text.

Mermaid rendering uses `mmdc` from PATH, or MERMAID_CMD / --mermaid-cmd (e.g. "npx -y -p @mermaid-js/mermaid-cli mmdc").
Set PUPPETEER_CONFIG to a puppeteer config JSON if Chromium needs flags (e.g. --no-sandbox in containers).
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*([\w+#.-]*)\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
HR_RE = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
TASK_RE = re.compile(r"^\[([ xX])\]\s+(.*)$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
ALERT_RE = re.compile(r"^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", re.I)
BOLD_PREFIX_RE = re.compile(r"^\*\*(Note|Tip|Info|Important|Warning|Caution)[:!]?\*\*:?\s*(.*)$", re.I)
PANEL = {"note": "info", "info": "info", "tip": "tip", "important": "note", "warning": "warning", "caution": "warning"}
LANG = {"sh": "bash", "shell": "bash", "zsh": "bash", "console": "bash", "yml": "yaml", "js": "javascript", "ts": "typescript",
        "kt": "kotlin", "kts": "kotlin", "py": "python", "jsonc": "json", "text": "none", "txt": "none", "": "none",
        "plaintext": "none", "c#": "csharp", "c++": "cpp"}
TOC_MACRO = '<ac:structured-macro ac:name="toc"><ac:parameter ac:name="maxLevel">3</ac:parameter></ac:structured-macro>'


def cdata(s):
    return s.replace("]]>", "]]]]><![CDATA[>")


def macro(name, body, title=None):
    param = f'<ac:parameter ac:name="title">{escape(title)}</ac:parameter>' if title else ""
    return f'<ac:structured-macro ac:name="{name}">{param}<ac:rich-text-body>{body}</ac:rich-text-body></ac:structured-macro>'


class Converter:
    def __init__(self, doc_path, out_dir, image_format="png", mermaid_cmd=None, link_base=None, page_properties=False):
        self.doc_dir = os.path.dirname(os.path.abspath(doc_path))
        self.stem = re.sub(r"[^A-Za-z0-9_-]+", "-", os.path.splitext(os.path.basename(doc_path))[0]).strip("-") or "doc"
        self.out_dir = out_dir
        self.image_format = image_format
        self.mermaid_cmd = mermaid_cmd
        self.link_base = link_base.rstrip("/") if link_base else None
        self.page_properties = page_properties
        self.attachments = []      # local file paths to upload
        self.diagrams = 0
        self.unrendered = []
        self.warnings = []
        self.title = None
        self._first_table_done = False

    # ---------------------------------------------------------------- document

    def convert(self, text):
        lines = text.replace("\r\n", "\n").split("\n")
        lines = self.strip_front_matter(lines)
        # The first H1 becomes the page title; Confluence shows it above the body.
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            m = HEADING_RE.match(line)
            if m and len(m.group(1)) == 1:
                self.title = m.group(2).strip()
                lines = lines[:i] + lines[i + 1:]
            break
        return "".join(self.blocks(lines))

    def strip_front_matter(self, lines):
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    for raw in lines[1:i]:
                        if raw.lower().startswith("title:"):
                            self.title = raw.split(":", 1)[1].strip().strip("\"'")
                    return lines[i + 1:]
        return lines

    # ---------------------------------------------------------------- blocks

    def blocks(self, lines):
        out, i, n = [], 0, len(lines)
        while i < n:
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                i += 1
                continue
            if stripped.startswith("<!--"):
                if stripped.lower() == "<!-- toc -->":
                    out.append(TOC_MACRO)
                while i < n and "-->" not in lines[i]:
                    i += 1
                i += 1
                continue
            if stripped in ("[[TOC]]", "[TOC]"):
                out.append(TOC_MACRO)
                i += 1
                continue
            fence = FENCE_RE.match(line)
            if fence:
                marker, lang = fence.group(1), fence.group(2).lower()
                close = re.compile(rf"^\s{{0,3}}{re.escape(marker[0])}{{{len(marker)},}}\s*$")
                i += 1
                code = []
                while i < n and not close.match(lines[i]):
                    code.append(lines[i])
                    i += 1
                i += 1
                out.append(self.code_block(lang, "\n".join(code)))
                continue
            heading = HEADING_RE.match(line)
            if heading:
                level = len(heading.group(1))
                out.append(f"<h{level}>{self.inline(heading.group(2))}</h{level}>")
                i += 1
                continue
            if HR_RE.match(line):
                out.append("<hr/>")
                i += 1
                continue
            if stripped.startswith(">"):
                quote = []
                while i < n and lines[i].strip() and (lines[i].lstrip().startswith(">") or quote):
                    if not lines[i].lstrip().startswith(">"):
                        break
                    quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                    i += 1
                out.append(self.quote(quote))
                continue
            if LIST_RE.match(line):
                items = []
                while i < n and (LIST_RE.match(lines[i]) or (items and lines[i].strip() and lines[i][:1].isspace())):
                    items.append(lines[i])
                    i += 1
                out.append(self.list_block(items))
                continue
            if "|" in line and i + 1 < n and TABLE_SEP_RE.match(lines[i + 1]):
                rows = [line]
                i += 2
                while i < n and lines[i].strip() and "|" in lines[i]:
                    rows.append(lines[i])
                    i += 1
                out.append(self.table(rows))
                continue
            para = []
            while i < n and lines[i].strip() and not self.starts_block(lines[i]):
                para.append(lines[i])
                i += 1
            if not para:  # a block start we don't otherwise handle; treat the single line as text
                para.append(lines[i])
                i += 1
            out.append(self.paragraph(para))
        return out

    def starts_block(self, line):
        s = line.strip()
        return bool(FENCE_RE.match(line) or HEADING_RE.match(line) or HR_RE.match(line) or LIST_RE.match(line)
                    or s.startswith(">") or s.startswith("<!--"))

    def paragraph(self, lines):
        parts = []
        for raw in lines:
            parts.append(self.inline(raw.strip()) + ("<br/>" if raw.endswith("  ") else " "))
        return f"<p>{''.join(parts).strip()}</p>"

    def quote(self, lines):
        kind, first = None, lines[0].strip() if lines else ""
        alert = ALERT_RE.match(first)
        bold = BOLD_PREFIX_RE.match(first)
        if alert:
            kind, lines = PANEL[alert.group(1).lower()], lines[1:]
            title = alert.group(1).capitalize()
        elif bold:
            kind, title = PANEL[bold.group(1).lower()], bold.group(1).capitalize()
            lines = [bold.group(2)] + lines[1:]
        body = "".join(self.blocks(lines))
        if kind:
            return macro(kind, body, title)
        return f"<blockquote>{body}</blockquote>"

    def list_block(self, raw_lines):
        items = []  # [indent, ordered, text]
        for raw in raw_lines:
            m = LIST_RE.match(raw)
            if m:
                items.append([len(m.group(1).expandtabs(4)), m.group(2)[0].isdigit(), m.group(3).strip()])
            elif items:
                items[-1][2] += " " + raw.strip()
        if items and all(TASK_RE.match(t) for _, _, t in items) and len({ind for ind, _, _ in items}) == 1:
            tasks = []
            for _, _, t in items:
                m = TASK_RE.match(t)
                status = "complete" if m.group(1).lower() == "x" else "incomplete"
                tasks.append(f"<ac:task><ac:task-status>{status}</ac:task-status><ac:task-body><span>{self.inline(m.group(2))}</span></ac:task-body></ac:task>")
            return f"<ac:task-list>{''.join(tasks)}</ac:task-list>"

        def item_html(t):
            m = TASK_RE.match(t)
            if m:
                return ("&#9745; " if m.group(1).lower() == "x" else "&#9744; ") + self.inline(m.group(2))
            return self.inline(t)

        def build(start, indent):
            html, i = [], start
            tag = "ol" if items[start][1] else "ul"
            while i < len(items) and items[i][0] >= indent:
                if items[i][0] > indent:
                    sub, i = build(i, items[i][0])
                    if html:
                        html[-1] = html[-1][:-5] + sub + "</li>"
                    else:
                        html.append(f"<li>{sub}</li>")
                    continue
                html.append(f"<li>{item_html(items[i][2])}</li>")
                i += 1
            return f"<{tag}>{''.join(html)}</{tag}>", i

        html, _ = build(0, items[0][0])
        return html

    def table(self, rows):
        def cells(line):
            line = line.strip()
            if line.startswith("|"):
                line = line[1:]
            if line.endswith("|") and not line.endswith("\\|"):
                line = line[:-1]
            return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]

        header = cells(rows[0])
        html = ["<table><tbody><tr>" + "".join(f"<th>{self.inline(c)}</th>" for c in header) + "</tr>"]
        for row in rows[1:]:
            cs = cells(row)
            cs += [""] * (len(header) - len(cs))
            html.append("<tr>" + "".join(f"<td>{self.inline(c)}</td>" for c in cs[:len(header)]) + "</tr>")
        html.append("</tbody></table>")
        table = "".join(html)
        if self.page_properties and not self._first_table_done:
            self._first_table_done = True
            return macro("details", table)
        return table

    def code_block(self, lang, code):
        if lang == "mermaid":
            return self.mermaid(code)
        language = LANG.get(lang, lang) or "none"
        return (f'<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">{escape(language)}</ac:parameter>'
                f'<ac:plain-text-body><![CDATA[{cdata(code)}]]></ac:plain-text-body></ac:structured-macro>')

    def mermaid(self, code):
        self.diagrams += 1
        filename = f"{self.stem}-diagram-{self.diagrams:02d}.{self.image_format}"
        path = os.path.join(self.out_dir, filename)
        if self.render_mermaid(code, path):
            self.attachments.append(path)
            return (f'<p><ac:image ac:align="center" ac:alt="Diagram {self.diagrams}">'
                    f'<ri:attachment ri:filename="{escape(filename)}"/></ac:image></p>')
        self.unrendered.append(self.diagrams)
        note = macro("warning", f"<p>Diagram {self.diagrams} is Mermaid source. Render it with mermaid-cli, a Mermaid macro, "
                                f"or draw.io (Insert &gt; Advanced &gt; Mermaid) and replace this block.</p>")
        return note + self.code_block("text", code)

    def render_mermaid(self, code, out_path):
        if not self.mermaid_cmd:
            return False
        os.makedirs(self.out_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False, encoding="utf-8") as f:
            f.write(code)
            src = f.name
        cmd = shlex.split(self.mermaid_cmd) + ["-i", src, "-o", out_path, "-b", "white", "-q"]
        if self.image_format == "png":
            cmd += ["-s", "2"]
        if os.environ.get("PUPPETEER_CONFIG"):
            cmd += ["-p", os.environ["PUPPETEER_CONFIG"]]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as e:
            self.warnings.append(f"diagram {self.diagrams}: {e}")
            return False
        finally:
            os.unlink(src)
        if result.returncode != 0 or not os.path.exists(out_path):
            self.warnings.append(f"diagram {self.diagrams}: mermaid-cli failed: {(result.stderr or result.stdout).strip()[-400:]}")
            return False
        return True

    # ---------------------------------------------------------------- inline

    def inline(self, text):
        codes = []

        def stash(m):
            codes.append(f"<code>{escape(m.group(2))}</code>")
            return f"\x00{len(codes) - 1}\x00"

        text = re.sub(r"(`+)(.+?)\1", stash, text)
        text = escape(text, {'"': "&quot;"})
        text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+&quot;[^&]*&quot;)?\)", self.image, text)
        text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+&quot;[^&]*&quot;)?\)", self.link, text)
        text = re.sub(r"&lt;(https?://.+?)&gt;", r'<a href="\1">\1</a>', text)
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"(?<!\w)__(.+?)__(?!\w)", r"<strong>\1</strong>", text)
        text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
        text = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", r"<em>\1</em>", text)
        text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
        return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)

    def image(self, m):
        alt, src = m.group(1), m.group(2)
        if re.match(r"https?://", src):
            return f'<ac:image ac:alt="{alt}"><ri:url ri:value="{src}"/></ac:image>'
        path = os.path.normpath(os.path.join(self.doc_dir, urllib.parse.unquote(src)))
        if os.path.isfile(path):
            if path.lower().endswith(".svg"):
                self.warnings.append(f"{os.path.basename(path)}: SVG attachments may not display on Confluence Data Center; "
                                     "prefer PNG (scripts/docs/chart.py --png)")
            if path not in self.attachments:
                self.attachments.append(path)
            return f'<ac:image ac:alt="{alt}"><ri:attachment ri:filename="{escape(os.path.basename(path))}"/></ac:image>'
        self.warnings.append(f"image not found: {src}")
        return f"[missing image: {alt or src}]"

    def link(self, m):
        label, href = m.group(1), m.group(2)
        if re.match(r"(https?://|mailto:)", href):
            return f'<a href="{href}">{label}</a>'
        if href.startswith("#"):
            return label
        if self.link_base:
            target = urllib.parse.urljoin(self.link_base + "/", href.split("#", 1)[0])
            return f'<a href="{escape(target)}">{label}</a>'
        return f"{label} (<code>{href}</code>)"


# ---------------------------------------------------------------- Confluence REST

class Confluence:
    def __init__(self, base_url, auth, api="v2"):
        self.base = base_url.rstrip("/")
        self.auth = auth
        self.api = api

    def request(self, method, path, body=None, raw=None, headers=None):
        url = path if path.startswith("http") else self.base + path
        data = raw if raw is not None else (json.dumps(body).encode("utf-8") if body is not None else None)
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", self.auth)
        req.add_header("Accept", "application/json")
        if body is not None:
            req.add_header("Content-Type", "application/json")
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = resp.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:800]
            sys.exit(f"HTTP {e.code} for {method} {url}\n{detail}")
        except urllib.error.URLError as e:
            sys.exit(f"cannot reach {url}: {e.reason}")
        return json.loads(payload) if payload.strip() else {}

    def space_id(self, key):
        if self.api == "v1":
            return key
        res = self.request("GET", f"/api/v2/spaces?keys={urllib.parse.quote(key)}&limit=1")
        if not res.get("results"):
            sys.exit(f"space {key!r} not found (or no permission)")
        return res["results"][0]["id"]

    def find_page(self, space, title):
        q = urllib.parse.quote(title)
        if self.api == "v1":
            res = self.request("GET", f"/rest/api/content?spaceKey={urllib.parse.quote(space)}&title={q}&expand=version&limit=1")
        else:
            res = self.request("GET", f"/api/v2/pages?space-id={space}&title={q}&status=current&limit=1")
        results = res.get("results") or []
        return results[0] if results else None

    def get_page(self, page_id):
        if self.api == "v1":
            return self.request("GET", f"/rest/api/content/{page_id}?expand=version")
        return self.request("GET", f"/api/v2/pages/{page_id}")

    def create_page(self, space, title, parent_id, xhtml):
        if self.api == "v1":
            body = {"type": "page", "title": title, "space": {"key": space},
                    "body": {"storage": {"value": xhtml, "representation": "storage"}}}
            if parent_id:
                body["ancestors"] = [{"id": str(parent_id)}]
            return self.request("POST", "/rest/api/content", body)
        body = {"spaceId": str(space), "status": "current", "title": title,
                "body": {"representation": "storage", "value": xhtml}}
        if parent_id:
            body["parentId"] = str(parent_id)
        return self.request("POST", "/api/v2/pages", body)

    def update_page(self, page, title, xhtml, message):
        page_id = page["id"]
        current = (page.get("version") or {}).get("number") or self.get_page(page_id)["version"]["number"]
        if self.api == "v1":
            body = {"id": page_id, "type": "page", "title": title,
                    "body": {"storage": {"value": xhtml, "representation": "storage"}},
                    "version": {"number": current + 1, "message": message}}
            return self.request("PUT", f"/rest/api/content/{page_id}", body)
        body = {"id": page_id, "status": "current", "title": title, "body": {"representation": "storage", "value": xhtml},
                "version": {"number": current + 1, "message": message}}
        return self.request("PUT", f"/api/v2/pages/{page_id}", body)

    def upload_attachment(self, page_id, path):
        boundary = "----confluence-publish-" + uuid.uuid4().hex
        name = os.path.basename(path)
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            content = f.read()
        raw = b"".join([
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\nContent-Type: {ctype}\r\n\r\n'.encode(),
            content, b"\r\n",
            f'--{boundary}\r\nContent-Disposition: form-data; name="minorEdit"\r\n\r\ntrue\r\n--{boundary}--\r\n'.encode()])
        return self.request("PUT", f"/rest/api/content/{page_id}/child/attachment", raw=raw,
                            headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "X-Atlassian-Token": "nocheck"})

    def add_labels(self, page_id, labels):
        self.request("POST", f"/rest/api/content/{page_id}/label", [{"prefix": "global", "name": l} for l in labels])

    def page_url(self, page):
        links = page.get("_links") or {}
        if links.get("webui"):
            return (links.get("base") or self.base) + links["webui"]
        return f"{self.base}/pages/viewpage.action?pageId={page['id']}"


def auth_header():
    email, token, pat = os.environ.get("CONFLUENCE_EMAIL"), os.environ.get("CONFLUENCE_API_TOKEN"), os.environ.get("CONFLUENCE_TOKEN")
    if email and token:
        return "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()
    if pat:
        return "Bearer " + pat
    return None


def validate_storage(xhtml):
    wrapped = ('<root xmlns:ac="http://atlassian.com/content" xmlns:ri="http://atlassian.com/resource/identifier">'
               + xhtml + "</root>")
    try:
        ET.fromstring(wrapped)
        return None
    except ET.ParseError as e:
        return str(e)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown")
    ap.add_argument("--title", help="page title (default: the document's first H1, then the file name)")
    ap.add_argument("--space", help="space key (required to create a page)")
    ap.add_argument("--parent-id", help="parent page id for a new page")
    ap.add_argument("--page-id", help="update exactly this page instead of matching by title")
    ap.add_argument("--base-url", default=os.environ.get("CONFLUENCE_BASE_URL"), help="e.g. https://acme.atlassian.net/wiki")
    ap.add_argument("--api", choices=["v2", "v1"], default="v2", help="v2 = Cloud (default), v1 = Data Center/Server")
    ap.add_argument("--out-dir", help="working directory for the storage XML and diagrams (default build/docs/<name>)")
    ap.add_argument("--image-format", choices=["png", "svg"], default="png")
    ap.add_argument("--mermaid-cmd", default=os.environ.get("MERMAID_CMD") or (shutil.which("mmdc") and "mmdc"),
                    help="command that renders Mermaid (default: mmdc on PATH)")
    ap.add_argument("--link-base", help="URL prefix that makes relative Markdown links absolute, e.g. the repo's blob URL")
    ap.add_argument("--labels", help="comma-separated page labels")
    ap.add_argument("--toc", action="store_true", help="prepend a table-of-contents macro")
    ap.add_argument("--page-properties", action="store_true", help="wrap the first table in a Page Properties macro")
    ap.add_argument("--version-message", default="Published from Markdown")
    ap.add_argument("--dry-run", action="store_true", help="convert and render only; no network")
    ap.add_argument("--strict", action="store_true", help="fail if a diagram could not be rendered")
    args = ap.parse_args()

    with open(args.markdown, encoding="utf-8") as f:
        text = f.read()
    stem = os.path.splitext(os.path.basename(args.markdown))[0]
    out_dir = args.out_dir or os.path.join("build", "docs", stem)
    os.makedirs(out_dir, exist_ok=True)
    conv = Converter(args.markdown, out_dir, args.image_format, args.mermaid_cmd, args.link_base, args.page_properties)
    xhtml = conv.convert(text)
    if args.toc:
        xhtml = TOC_MACRO + xhtml
    title = args.title or conv.title or stem

    storage_path = os.path.join(out_dir, "page.storage.xml")
    with open(storage_path, "w", encoding="utf-8") as f:
        f.write(xhtml)
    with open(os.path.join(out_dir, "attachments.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(conv.attachments) + ("\n" if conv.attachments else ""))
    error = validate_storage(xhtml)
    rendered = conv.diagrams - len(conv.unrendered)
    print(f"title: {title}\nstorage format: {storage_path} ({len(xhtml):,} chars)\n"
          f"diagrams: {rendered}/{conv.diagrams} rendered, attachments: {len(conv.attachments)}")
    for w in conv.warnings:
        print(f"warning: {w}")
    if conv.unrendered and not args.mermaid_cmd:
        print("warning: mermaid-cli not found; diagrams were left as source (install @mermaid-js/mermaid-cli or set --mermaid-cmd)")
    if error:
        sys.exit(f"storage format is not well-formed XML: {error}")
    if args.strict and conv.unrendered:
        sys.exit(f"unrendered diagrams: {conv.unrendered}")
    if args.dry_run:
        print("dry run: nothing published")
        return

    if not args.base_url:
        sys.exit("set CONFLUENCE_BASE_URL or pass --base-url (or use --dry-run)")
    auth = auth_header()
    if not auth:
        sys.exit("set CONFLUENCE_EMAIL + CONFLUENCE_API_TOKEN (Cloud) or CONFLUENCE_TOKEN (Data Center PAT), or use --dry-run")
    client = Confluence(args.base_url, auth, args.api)

    if args.page_id:
        page = client.update_page(client.get_page(args.page_id), title, xhtml, args.version_message)
        action = "updated"
    else:
        if not args.space:
            sys.exit("--space is required to find or create the page")
        space = client.space_id(args.space)
        existing = client.find_page(space, title)
        if existing:
            page = client.update_page(existing, title, xhtml, args.version_message)
            action = "updated"
        else:
            page = client.create_page(space, title, args.parent_id, xhtml)
            action = "created"
    for path in conv.attachments:
        client.upload_attachment(page["id"], path)
    if args.labels:
        client.add_labels(page["id"], [l.strip() for l in args.labels.split(",") if l.strip()])
    print(f"{action} page {page['id']}: {client.page_url(page)}")
    if conv.attachments:
        print(f"uploaded {len(conv.attachments)} attachment(s)")


if __name__ == "__main__":
    main()
