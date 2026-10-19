#!/usr/bin/env python3
"""Turn load-test results into report-ready Markdown: a per-scenario results table, SLO verdicts and a
time series (a Mermaid xychart for Git/GitHub, plus a CSV for scripts/docs/chart.py to render for Confluence).

Standard library only. Input formats (auto-detected unless --format is given):
  jtl         JMeter CSV results (timeStamp, elapsed, label, success, ...)
  k6-csv      k6 --out csv=results.csv (http_req_duration rows)
  k6-summary  k6 --summary-export=summary.json (one row, no time series)
  csv         any CSV, with --columns ts=<col>,value=<col>[,label=<col>][,success=<col>]

Examples:
  python3 scripts/docs/perf_report.py results.jtl --slo "p95<=300,p99<=800,error_rate<=1" --title "Orders API, 50 rps"
  python3 scripts/docs/perf_report.py results.jtl --bucket 30 --series-csv build/docs/p95.csv --out build/docs/perf.md
  python3 scripts/docs/perf_report.py summary.json --format k6-summary --slo "p95<=300"

Method (stated in the output so reviewers can check it):
  percentiles  nearest-rank over every sample of the scenario
  throughput   requests / (last sample - first sample) of the scenario, in req/s
  error        JTL success=false, k6 expected_response=false (or HTTP status >= 400)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

METRICS = ("avg", "min", "p50", "p90", "p95", "p99", "max", "error_rate", "throughput", "count")
SLO_ALIASES = {"errors": "error_rate", "error": "error_rate", "error_pct": "error_rate", "rps": "throughput",
               "tps": "throughput", "mean": "avg", "median": "p50"}
TRUE_VALUES = {"true", "1", "yes", "y", "ok", "pass", "passed"}
SLO_RE = re.compile(r"^\s*([A-Za-z_0-9]+)\s*(<=|>=|<|>|=)\s*([0-9]+(?:\.[0-9]+)?)\s*(ms|s|%|rps|req/s)?\s*$")
ALL = "All"


@dataclass
class Sample:
    ts: float      # seconds since the epoch
    label: str     # scenario / request name
    value: float   # duration in milliseconds
    ok: bool


# ---------------------------------------------------------------- parsing

def parse_timestamp(raw, unit="auto"):
    s = str(raw).strip()
    if unit != "iso" and re.fullmatch(r"-?\d+(\.\d+)?", s):
        v = float(s)
        return v / 1000.0 if unit == "ms" or (unit == "auto" and v > 1e11) else v
    for fmt in (None, "%Y/%m/%d %H:%M:%S.%f", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.fromisoformat(s) if fmt is None else datetime.strptime(s, fmt)
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    raise ValueError(f"unrecognised timestamp {raw!r}")


def parse_bool(raw):
    return str(raw).strip().lower() in TRUE_VALUES


def sniff_format(path):
    if path.lower().endswith(".json"):
        return "k6-summary"
    with open(path, newline="", encoding="utf-8-sig") as f:
        header = {c.strip().lower() for c in f.readline().split(",")}
    if {"metric_name", "timestamp", "metric_value"} <= header:
        return "k6-csv"
    if {"timestamp", "elapsed"} <= header:
        return "jtl"
    return "csv"


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            yield {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}


def parse_jtl(path, ts_unit):
    samples, skipped = [], 0
    for row in read_rows(path):
        try:
            samples.append(Sample(parse_timestamp(row["timestamp"], ts_unit), row.get("label") or "request",
                                  float(row["elapsed"]), parse_bool(row.get("success", "true"))))
        except (KeyError, ValueError):
            skipped += 1
    return samples, skipped


def parse_k6_csv(path, ts_unit, label_col):
    samples, skipped = [], 0
    for row in read_rows(path):
        if row.get("metric_name") != "http_req_duration":
            continue
        try:
            label = (label_col and row.get(label_col)) or row.get("scenario") or row.get("name") or row.get("url") or "request"
            if row.get("expected_response", "") != "":
                ok = parse_bool(row["expected_response"])
            else:
                ok = int(row.get("status") or 0) < 400
            samples.append(Sample(parse_timestamp(row["timestamp"], ts_unit), label, float(row["metric_value"]), ok))
        except (KeyError, ValueError):
            skipped += 1
    return samples, skipped


def parse_generic(path, columns, ts_unit):
    if not columns:
        sys.exit("generic CSV needs --columns ts=<col>,value=<col>[,label=<col>][,success=<col>]")
    spec = dict(part.split("=", 1) for part in columns.split(",") if "=" in part)
    spec = {k.strip().lower(): v.strip().lower() for k, v in spec.items()}
    if "ts" not in spec or "value" not in spec:
        sys.exit("--columns must name at least ts=<col> and value=<col>")
    samples, skipped = [], 0
    for row in read_rows(path):
        try:
            label = row.get(spec["label"], "") if "label" in spec else ""
            ok = parse_bool(row.get(spec["success"], "true")) if "success" in spec else True
            samples.append(Sample(parse_timestamp(row[spec["ts"]], ts_unit), label or "request", float(row[spec["value"]]), ok))
        except (KeyError, ValueError):
            skipped += 1
    return samples, skipped


def parse_k6_summary(path, label):
    """k6 --summary-export JSON (also accepts the handleSummary() data shape with nested 'values')."""
    with open(path, encoding="utf-8") as f:
        metrics = json.load(f).get("metrics", {})

    def values(name):
        m = metrics.get(name, {})
        return m.get("values", m)

    duration, reqs, failed = values("http_req_duration"), values("http_reqs"), values("http_req_failed")
    count = int(reqs.get("count", 0))
    errors = int(failed.get("passes", 0))  # for the http_req_failed Rate metric, "passes" counts failed requests
    row = {"label": label or ALL, "count": count, "errors": errors,
           "error_rate": 100.0 * errors / count if count else 0.0, "throughput": float(reqs.get("rate", 0.0))}
    for key, src in (("avg", "avg"), ("min", "min"), ("p50", "med"), ("p90", "p(90)"), ("p95", "p(95)"),
                     ("p99", "p(99)"), ("max", "max")):
        row[key] = duration.get(src)
    return row


# ---------------------------------------------------------------- statistics

def percentile(sorted_values, p):
    k = max(1, math.ceil(p / 100.0 * len(sorted_values)))
    return sorted_values[k - 1]


def summarize(label, samples, span=None):
    values = sorted(s.value for s in samples)
    n = len(values)
    errors = sum(1 for s in samples if not s.ok)
    start, end = min(s.ts for s in samples), max(s.ts for s in samples)
    span = span if span is not None else max(end - start, 1.0)
    return {"label": label, "count": n, "errors": errors, "error_rate": 100.0 * errors / n, "throughput": n / span,
            "avg": sum(values) / n, "min": values[0], "p50": percentile(values, 50), "p90": percentile(values, 90),
            "p95": percentile(values, 95), "p99": percentile(values, 99), "max": values[-1], "start": start, "end": end}


def parse_slos(text):
    slos = []
    for part in filter(None, (p.strip() for p in (text or "").split(","))):
        m = SLO_RE.match(part)
        if not m:
            sys.exit(f"bad --slo entry {part!r}; expected e.g. p95<=300, error_rate<=1, throughput>=50")
        metric = SLO_ALIASES.get(m.group(1).lower(), m.group(1).lower())
        if metric not in METRICS:
            sys.exit(f"unknown SLO metric {metric!r}; use one of {', '.join(METRICS)}")
        target = float(m.group(3)) * (1000.0 if m.group(4) == "s" else 1.0)
        slos.append({"metric": metric, "op": m.group(2), "target": target, "text": part})
    return slos


def meets(value, op, target):
    if value is None:
        return False
    return {"<=": value <= target, "<": value < target, ">=": value >= target, ">": value > target, "=": value == target}[op]


def failing_slos(row, slos):
    return [slo["text"] for slo in slos if not meets(row.get(slo["metric"]), slo["op"], slo["target"])]


# ---------------------------------------------------------------- time series

def bucket_metric(samples, metric, bucket):
    if not samples:
        return None
    if metric == "count":
        return len(samples)
    if metric == "throughput":
        return len(samples) / bucket
    return summarize("", samples, span=bucket)[metric]


def build_series(samples, bucket, metric, max_points):
    start = min(s.ts for s in samples)
    end = max(s.ts for s in samples)
    while int((end - start) // bucket) + 1 > max_points:
        bucket *= 2
    buckets = int((end - start) // bucket) + 1
    groups = defaultdict(lambda: defaultdict(list))
    for s in samples:
        index = int((s.ts - start) // bucket)
        groups[s.label][index].append(s)
        groups[ALL][index].append(s)
    series = {label: [bucket_metric(by_index.get(i, []), metric, bucket) for i in range(buckets)]
              for label, by_index in groups.items()}
    return {"bucket": bucket, "start": start, "metric": metric,
            "elapsed": [i * bucket for i in range(buckets)], "series": series}


def mmss(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"


def mermaid_xychart(title, elapsed, values, y_label, slo_target=None):
    plotted = [0 if v is None else round(v, 1) for v in values]
    top = max(plotted + ([slo_target] if slo_target else [1]))
    y_max = nice_ceiling(top * 1.15)
    lines = ["```mermaid", "xychart-beta", f"    title {json.dumps(title)}",
             f"    x-axis \"elapsed (m:ss)\" [{', '.join(json.dumps(mmss(e)) for e in elapsed)}]",
             f"    y-axis {json.dumps(y_label)} 0 --> {y_max:g}",
             f"    line [{', '.join(f'{v:g}' for v in plotted)}]"]
    if slo_target:
        lines.append(f"    line [{', '.join([f'{slo_target:g}'] * len(plotted))}]")
    lines.append("```")
    return "\n".join(lines)


def nice_ceiling(value):
    if value <= 0:
        return 1
    magnitude = 10 ** math.floor(math.log10(value))
    for factor in (1, 2, 2.5, 5, 10):
        if value <= factor * magnitude:
            return factor * magnitude
    return 10 * magnitude


# ---------------------------------------------------------------- output

def fmt_ms(v):
    if v is None:
        return "–"
    return f"{v:,.0f}" if v >= 10 else f"{v:.1f}"


def fmt_time(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def results_table(rows, slos):
    header = ["Scenario", "Requests", "Errors", "Error %", "Throughput (req/s)", "Avg (ms)", "p50 (ms)", "p90 (ms)",
              "p95 (ms)", "p99 (ms)", "Max (ms)"] + (["SLO"] if slos else [])
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for row in rows:
        label = f"**{row['label']}**" if row["label"] == ALL else row["label"]
        cells = [label, f"{row['count']:,}", f"{row['errors']:,}", f"{row['error_rate']:.2f}", f"{row['throughput']:.1f}",
                 fmt_ms(row.get("avg")), fmt_ms(row.get("p50")), fmt_ms(row.get("p90")), fmt_ms(row.get("p95")),
                 fmt_ms(row.get("p99")), fmt_ms(row.get("max"))]
        if slos:
            failed = failing_slos(row, slos)
            cells.append("✅ PASS" if not failed else "❌ FAIL (" + "; ".join(failed) + ")")
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def write_series_csv(path, series):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        labels = [ALL] + sorted(l for l in series["series"] if l != ALL)
        writer.writerow(["elapsed_s", "time", *labels])
        for i, elapsed in enumerate(series["elapsed"]):
            when = datetime.fromtimestamp(series["start"] + elapsed, tz=timezone.utc).isoformat()
            writer.writerow([elapsed, when] + ["" if series["series"][l][i] is None else f"{series['series'][l][i]:.2f}"
                                               for l in labels])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="result files (same format)")
    ap.add_argument("--format", choices=["auto", "jtl", "k6-csv", "k6-summary", "csv"], default="auto")
    ap.add_argument("--columns", help="generic CSV mapping: ts=<col>,value=<col>[,label=<col>][,success=<col>]")
    ap.add_argument("--ts-unit", choices=["auto", "ms", "s", "iso"], default="auto", help="timestamp unit (auto: >1e11 means ms)")
    ap.add_argument("--label", help="scenario label for k6-summary input, or the k6 CSV column to label by")
    ap.add_argument("--title", default="Load test", help="used in headings and chart titles")
    ap.add_argument("--slo", default="", help='comma-separated, e.g. "p95<=300,p99<=800,error_rate<=1,throughput>=50"')
    ap.add_argument("--bucket", type=int, default=60, help="time-series bucket in seconds (default 60)")
    ap.add_argument("--series-metric", choices=["p50", "p90", "p95", "p99", "avg", "max", "throughput", "error_rate", "count"],
                    default="p95")
    ap.add_argument("--max-points", type=int, default=40, help="coarsen the bucket until the series has at most this many points")
    ap.add_argument("--mermaid-per-label", action="store_true", help="one Mermaid chart per scenario instead of the total only")
    ap.add_argument("--heading-level", type=int, default=3)
    ap.add_argument("--out", help="write the Markdown here instead of stdout")
    ap.add_argument("--series-csv", help="write the bucketed time series (for scripts/docs/chart.py)")
    ap.add_argument("--json", help="write all computed numbers as JSON")
    args = ap.parse_args()

    fmt = sniff_format(args.files[0]) if args.format == "auto" else args.format
    slos = parse_slos(args.slo)
    samples, skipped, rows, notes = [], 0, [], []

    if fmt == "k6-summary":
        rows = [parse_k6_summary(path, args.label) for path in args.files]
        notes.append("k6 summary export has no per-sample data, so there is no time series; use `k6 --out csv` for one.")
    else:
        parser = {"jtl": lambda p: parse_jtl(p, args.ts_unit), "k6-csv": lambda p: parse_k6_csv(p, args.ts_unit, args.label),
                  "csv": lambda p: parse_generic(p, args.columns, args.ts_unit)}[fmt]
        for path in args.files:
            got, bad = parser(path)
            samples.extend(got)
            skipped += bad
        if not samples:
            sys.exit(f"no samples parsed from {', '.join(args.files)} (format {fmt}); check --format/--columns")
        by_label = defaultdict(list)
        for s in samples:
            by_label[s.label].append(s)
        rows = [summarize(label, group) for label, group in sorted(by_label.items())]
        if len(rows) > 1:
            rows.append(summarize(ALL, samples))
    if skipped:
        notes.append(f"{skipped} malformed rows skipped.")

    verdict = None
    if slos:
        failed = {row["label"]: failing_slos(row, slos) for row in rows}
        verdict = "PASS" if not any(failed.values()) else "FAIL"

    series = build_series(samples, args.bucket, args.series_metric, args.max_points) if samples else None
    if series and series["bucket"] != args.bucket:
        notes.append(f"Bucket widened from {args.bucket}s to {series['bucket']}s to keep the chart at {args.max_points} points or fewer.")

    h = "#" * max(1, min(6, args.heading_level))
    md = [f"{h} Results: {args.title}", ""]
    if samples:
        md.append(f"Source: {', '.join(args.files)} ({fmt}), {len(samples):,} samples, "
                  f"{fmt_time(min(s.ts for s in samples))} to {fmt_time(max(s.ts for s in samples))} "
                  f"({mmss(max(s.ts for s in samples) - min(s.ts for s in samples))} min:sec).")
    else:
        md.append(f"Source: {', '.join(args.files)} ({fmt}).")
    md += ["", results_table(rows, slos), ""]
    if slos:
        md.append(f"**SLO verdict: {verdict}** against `{', '.join(s['text'] for s in slos)}`" +
                  ("" if verdict == "PASS" else " (failing scenarios marked in the table)") + ".")
        md.append("")
    if series:
        metric_label = {"throughput": "req/s", "error_rate": "%", "count": "requests"}.get(args.series_metric, "ms")
        slo_for_metric = next((s["target"] for s in slos if s["metric"] == args.series_metric), None)
        labels = [ALL] if not args.mermaid_per_label else sorted(l for l in series["series"] if l != ALL)
        for label in labels:
            title = f"{args.series_metric} ({metric_label}) per {series['bucket']} s" + ("" if label == ALL else f": {label}")
            md.append(mermaid_xychart(title, series["elapsed"], series["series"][label], metric_label, slo_for_metric))
            caption = f"*Figure: {args.series_metric} over elapsed time, {label}."
            if slo_for_metric:
                caption += f" The flat line is the SLO ({slo_for_metric:g} {metric_label})."
            if any(v is None for v in series["series"][label]):
                caption += " Buckets without samples plot as 0."
            md += [caption + "*", ""]
    md += ["Method: percentiles are nearest-rank over all samples of a scenario; throughput is requests divided by the "
           "scenario's first-to-last sample span; errors are samples flagged unsuccessful by the tool."]
    for note in notes:
        md.append(f"Note: {note}")
    text = "\n".join(md) + "\n"

    if args.series_csv and series:
        write_series_csv(args.series_csv, series)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"title": args.title, "format": fmt, "files": args.files, "rows": rows, "slos": slos, "verdict": verdict,
                       "series": series, "notes": notes}, f, indent=2, default=str)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {args.out}: {len(rows)} rows" + (f", verdict {verdict}" if verdict else ""), file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
