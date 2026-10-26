#!/usr/bin/env python3
"""Render a clean SVG (optionally PNG) line or bar chart from a CSV, for Confluence, slides or Word.

Standard library only. The first CSV column is x (a category, elapsed seconds, or an ISO timestamp); every other
numeric column is a series (at most as many as the theme has colours, in the order given). Non-numeric columns are
ignored. Colours come from a theme in scripts/docs/themes (--theme, --list-themes, env DOC_THEME).

Examples:
  python3 scripts/docs/chart.py build/docs/p95.csv --out build/docs/p95.svg --title "p95 latency, Orders API" \
      --y-label "ms" --threshold 300 --threshold-label "SLO 300 ms" --png
  python3 scripts/docs/chart.py by-scenario.csv --type bar --columns p95,p99 --out latency.svg --y-label "ms"
  python3 scripts/docs/chart.py build/docs/p95.csv --table      # the same data as a Markdown table (accessible twin)

PNG needs one of: the cairosvg package, rsvg-convert (librsvg), Inkscape, ImageMagick with an SVG delegate, or a
Chrome/Chromium binary on PATH or in CHROME_PATH (headless screenshot).
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import zlib
from datetime import datetime
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doc_themes import list_themes, load_theme  # noqa: E402  (shared with confluence_publish.py)

FONT = "system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def load(path, x_column, columns, max_series):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = [c for c in (reader.fieldnames or []) if c]
        rows = list(reader)
    if not fields or not rows:
        sys.exit(f"{path}: no data")
    xcol = x_column or fields[0]
    if xcol not in fields:
        sys.exit(f"x column {xcol!r} not in {fields}")
    wanted = [c.strip() for c in columns.split(",")] if columns else [c for c in fields if c != xcol]
    series = {}
    for col in wanted:
        if col not in fields:
            sys.exit(f"column {col!r} not in {fields}")
        values, numeric = [], True
        for row in rows:
            raw = (row.get(col) or "").strip()
            if raw == "":
                values.append(None)
                continue
            try:
                values.append(float(raw))
            except ValueError:
                numeric = False
                break
        if numeric and any(v is not None for v in values):
            series[col] = values
    if not series:
        sys.exit("no numeric series found")
    if len(series) > max_series:
        sys.exit(f"{len(series)} series is too many to read; this theme has {max_series} colours (fold the rest into 'Other')")
    return [row.get(xcol, "") for row in rows], series


def nice_ticks(top_value, target=5):
    if top_value <= 0:
        return [0.0, 1.0], 1.0
    rough = top_value / target
    magnitude = 10 ** math.floor(math.log10(rough))
    step = next((f * magnitude for f in (1, 2, 2.5, 5, 10) if top_value / (f * magnitude) <= target), 10 * magnitude)
    top = math.ceil(top_value / step) * step
    return [i * step for i in range(int(round(top / step)) + 1)], top


def compact(v):
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:g}M"
    if abs(v) >= 1_000:
        return f"{v / 1_000:g}K"
    return f"{v:g}"


def x_label(raw, fmt):
    raw = raw.strip()
    if fmt == "raw":
        return raw
    if fmt in ("auto", "mmss") and re.fullmatch(r"-?\d+(\.\d+)?", raw):
        s = int(round(float(raw)))
        return f"{s // 60}:{s % 60:02d}"
    if fmt in ("auto", "time"):
        try:
            dt = datetime.fromisoformat(raw)
            return dt.strftime("%H:%M:%S" if dt.second else "%H:%M")
        except ValueError:
            pass
    return raw


def text(x, y, s, size, fill, anchor="start", weight="normal", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" {extra}>{escape(s)}</text>')


def rounded_top_bar(x, y, w, h, r=4):
    r = min(r, h / 2, w / 2)
    return (f'M{x:.1f},{y + h:.1f} V{y + r:.1f} Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f} H{x + w - r:.1f} '
            f'Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f} V{y + h:.1f} Z')


def render(xs, series, args, theme):
    names = list(series)
    colors, c, threshold_color = theme["series"], theme["chrome"], theme["threshold"]
    SURFACE, INK, INK_2, MUTED, GRID, AXIS = c["surface"], c["ink"], c["ink2"], c["muted"], c["grid"], c["axis"]
    width, height = args.width, args.height
    legend = len(names) >= 2
    top_margin = 48 + (24 if legend else 0) + (16 if args.subtitle else 0)
    left, right, bottom = 64, 24, 60
    plot_w, plot_h = width - left - right, height - top_margin - bottom
    highest = max([v for vals in series.values() for v in vals if v is not None] + ([args.threshold] if args.threshold else []))
    ticks, top = nice_ticks(highest * 1.05)

    def y_of(v):
        return top_margin + plot_h - (v / top) * plot_h

    n = len(xs)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
           f'role="img" aria-label="{escape(args.title or "chart")}">',
           f'<rect width="{width}" height="{height}" fill="{SURFACE}"/>']
    if args.title:
        svg.append(text(left, 26, args.title, 15, INK, weight="600"))
    if args.subtitle:
        svg.append(text(left, 44, args.subtitle, 12, MUTED))
    if legend:
        lx, ly = left, top_margin - 14
        for i, name in enumerate(names):
            color = colors[i]
            if args.type == "line":
                svg.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 18}" y2="{ly}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')
                svg.append(f'<circle cx="{lx + 9}" cy="{ly}" r="3.5" fill="{color}" stroke="{SURFACE}" stroke-width="2"/>')
            else:
                svg.append(f'<rect x="{lx}" y="{ly - 6}" width="12" height="12" rx="2" fill="{color}"/>')
            svg.append(text(lx + 24, ly + 4, name, 12, INK_2))
            lx += 24 + len(name) * 6.8 + 20
    for t in ticks:
        y = y_of(t)
        if t > 0:
            svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        svg.append(text(left - 8, y + 4, compact(t), 11, MUTED, anchor="end", extra='font-variant-numeric="tabular-nums"'))
    svg.append(f'<line x1="{left}" y1="{y_of(0):.1f}" x2="{left + plot_w}" y2="{y_of(0):.1f}" stroke="{AXIS}" stroke-width="1"/>')
    if args.y_label:
        svg.append(text(16, top_margin + plot_h / 2, args.y_label, 12, INK_2, anchor="middle",
                        extra=f'transform="rotate(-90 16 {top_margin + plot_h / 2:.1f})"'))
    if args.x_label_title:
        svg.append(text(left + plot_w / 2, height - 12, args.x_label_title, 12, INK_2, anchor="middle"))

    step = max(1, math.ceil(n / max(1, args.max_x_labels)))
    if args.type == "line":
        def x_of(i):
            return left + (plot_w * i / (n - 1) if n > 1 else plot_w / 2)
        for i in range(0, n, step):
            svg.append(text(x_of(i), top_margin + plot_h + 18, x_label(xs[i], args.x_format), 11, MUTED, anchor="middle"))
        show_markers = args.markers == "always" or (args.markers == "auto" and n <= 60)
        for si, name in enumerate(names):
            color, vals = colors[si], series[name]
            segment = []
            for i, v in enumerate(vals + [None]):
                if v is None:
                    if len(segment) > 1:
                        svg.append(f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in segment)}" fill="none" '
                                   f'stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
                    segment = []
                else:
                    segment.append((x_of(i), y_of(v)))
            if show_markers:
                for i, v in enumerate(vals):
                    if v is not None:
                        svg.append(f'<circle cx="{x_of(i):.1f}" cy="{y_of(v):.1f}" r="4" fill="{color}" stroke="{SURFACE}" stroke-width="2"/>')
            if args.end_labels and len(names) <= 4:
                last = next(((i, v) for i, v in reversed(list(enumerate(vals))) if v is not None), None)
                if last:
                    svg.append(text(x_of(last[0]) + 8, y_of(last[1]) + 4, compact(last[1]), 11, INK_2))
    else:
        band = plot_w / n
        k = len(names)
        group_w = min(band * 0.8, k * 24 + (k - 1) * 2)
        bar_w = (group_w - (k - 1) * 2) / k
        for i in range(n):
            cx = left + band * (i + 0.5)
            if i % step == 0:
                svg.append(text(cx, top_margin + plot_h + 18, x_label(xs[i], args.x_format if args.x_format != "auto" else "raw"),
                                11, MUTED, anchor="middle"))
            for si, name in enumerate(names):
                v = series[name][i]
                if v is None:
                    continue
                x = cx - group_w / 2 + si * (bar_w + 2)
                svg.append(f'<path d="{rounded_top_bar(x, y_of(v), bar_w, y_of(0) - y_of(v))}" fill="{colors[si]}"/>')
                if args.end_labels and k <= 2:
                    svg.append(text(x + bar_w / 2, y_of(v) - 6, compact(v), 11, INK_2, anchor="middle"))
    if args.threshold is not None:
        y = y_of(args.threshold)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="{threshold_color}" stroke-width="1.5" stroke-dasharray="6 4"/>')
        svg.append(text(left + plot_w, y - 6, args.threshold_label or f"threshold {compact(args.threshold)}", 11, INK_2, anchor="end"))
    svg.append("</svg>")
    return "\n".join(svg)


def find_chrome():
    if os.environ.get("CHROME_PATH"):
        return os.environ["CHROME_PATH"]
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge"):
        if shutil.which(name):
            return shutil.which(name)
    return None


def crop_png(path, max_width, max_height):
    """Crop a non-interlaced 8-bit RGB/RGBA PNG to the top-left max_width x max_height, standard library only.
    Dropping trailing pixels and rows keeps every PNG row filter valid, so no pixel decoding is needed."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return
    pos, chunks, idat = 8, [], b""
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + length]
        chunks.append((kind, body))
        if kind == b"IDAT":
            idat += body
        pos += 12 + length
    ihdr = next((b for k, b in chunks if k == b"IHDR"), None)
    if ihdr is None:
        return
    width, height, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", ihdr)
    bpp = {2: 3, 6: 4}.get(color)
    if depth != 8 or bpp is None or interlace != 0 or (width <= max_width and height <= max_height):
        return
    new_w, new_h = min(width, max_width), min(height, max_height)
    raw, stride = zlib.decompress(idat), 1 + width * bpp
    rows = b"".join(raw[y * stride:y * stride + 1 + new_w * bpp] for y in range(new_h))

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)

    new_ihdr = struct.pack(">IIBBBBB", new_w, new_h, depth, color, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", new_ihdr) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


def to_png(svg_path, png_path, width, height, scale=2):
    """Try the converters people typically have: cairosvg, librsvg, Inkscape, ImageMagick, then headless Chrome."""
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(url=svg_path, write_to=png_path, scale=scale)
        return "cairosvg"
    except ImportError:
        pass
    attempts = []
    if shutil.which("rsvg-convert"):
        attempts.append(("rsvg-convert", ["rsvg-convert", "-z", str(scale), "-o", png_path, svg_path]))
    if shutil.which("inkscape"):
        attempts.append(("inkscape", ["inkscape", svg_path, "--export-type=png", f"--export-filename={png_path}",
                                      f"--export-dpi={96 * scale}"]))
    for tool in ("magick", "convert"):
        if shutil.which(tool):
            attempts.append((tool, [tool, "-density", str(96 * scale), "-background", "white", svg_path, png_path]))
    chrome = find_chrome()
    if chrome:
        # New-style headless Chrome counts its own UI (about 110px) inside --window-size, so ask for a taller window
        # and crop the screenshot back to the chart's size afterwards.
        attempts.append(("chrome", [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                                    f"--force-device-scale-factor={scale}", f"--window-size={width},{height + 160}",
                                    f"--screenshot={png_path}", "file://" + os.path.abspath(svg_path)]))
    for name, cmd in attempts:
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
        if os.path.exists(png_path) and os.path.getsize(png_path) > 0:
            if name == "chrome":
                crop_png(png_path, width * scale, height * scale)
            return name
    sys.exit("PNG conversion failed: install the cairosvg package, librsvg (rsvg-convert), Inkscape, ImageMagick with an SVG "
             "delegate, or set CHROME_PATH to a Chrome/Chromium binary. The SVG was written and can be attached as is.")


def markdown_table(xs, series):
    names = list(series)
    out = ["| x | " + " | ".join(names) + " |", "|---|" + "|".join(["---"] * len(names)) + "|"]
    for i, x in enumerate(xs):
        out.append("| " + x + " | " + " | ".join("" if series[n][i] is None else f"{series[n][i]:g}" for n in names) + " |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--out", help="output .svg path (default: next to the CSV)")
    ap.add_argument("--type", choices=["line", "bar"], default="line")
    ap.add_argument("--columns", help="comma-separated series columns, in legend order (default: all numeric columns)")
    ap.add_argument("--x-column", help="x column (default: first column)")
    ap.add_argument("--x-format", choices=["auto", "raw", "mmss", "time"], default="auto",
                    help="x labels: elapsed seconds as m:ss, ISO timestamps as HH:MM, or raw text")
    ap.add_argument("--title")
    ap.add_argument("--subtitle", help="one line of context: environment, date, load model")
    ap.add_argument("--x-label", dest="x_label_title")
    ap.add_argument("--y-label", help="unit, e.g. ms or req/s")
    ap.add_argument("--threshold", type=float, help="horizontal reference line, e.g. the SLO")
    ap.add_argument("--threshold-label")
    ap.add_argument("--markers", choices=["auto", "always", "never"], default="auto")
    ap.add_argument("--end-labels", action="store_true", help="label the last value of each series (lines) or each bar")
    ap.add_argument("--max-x-labels", type=int, default=12)
    ap.add_argument("--width", type=int, default=960)
    ap.add_argument("--height", type=int, default=420)
    ap.add_argument("--theme", default=os.environ.get("DOC_THEME", "default"),
                    help="colour theme from scripts/docs/themes (or a path to a theme JSON); env DOC_THEME")
    ap.add_argument("--colors", help="comma-separated hex colours overriding the theme's series order")
    ap.add_argument("--list-themes", action="store_true")
    ap.add_argument("--png", action="store_true", help="also write a PNG next to the SVG (2x scale)")
    ap.add_argument("--table", action="store_true", help="print the data as a Markdown table instead of drawing")
    args = ap.parse_args()
    if args.list_themes:
        for name in list_themes():
            print(f"{name:12s} {load_theme(name).get('description', '')}")
        return
    if not args.csv:
        ap.error("a CSV file is required")
    try:
        theme = load_theme(args.theme)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(str(e))
    if args.colors:
        theme["series"] = [col.strip() for col in args.colors.split(",") if col.strip()]

    xs, series = load(args.csv, args.x_column, args.columns, len(theme["series"]))
    if args.table:
        print(markdown_table(xs, series))
        return
    out = args.out or re.sub(r"\.csv$", "", args.csv, flags=re.I) + ".svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(xs, series, args, theme))
    print(f"wrote {out} ({len(series)} series, {len(xs)} points)", file=sys.stderr)
    if args.png:
        png = re.sub(r"\.svg$", "", out, flags=re.I) + ".png"
        tool = to_png(out, png, args.width, args.height)
        print(f"wrote {png} via {tool}", file=sys.stderr)


if __name__ == "__main__":
    main()
