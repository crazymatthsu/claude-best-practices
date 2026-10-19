---
name: perf-report
description: Turn load or performance test results (JMeter JTL, k6 summary JSON or CSV, Gatling or any CSV export) into a professional performance report with a results table, SLO verdicts, time-series charts and analysis, ready for Confluence. Use when asked to report, compare, chart or document load test, stress test, soak test or benchmark results.
---

# Performance report

1. **Collect the facts of the run before touching the numbers:** system version or commit, environment and how it
   differs from production, tool and version, workload model (scenarios, rates or users, ramp, think time, test data),
   duration and warm-up, what else was running. Ask for what is missing; a result without its environment cannot be
   reported.
2. **Get the SLO targets from the spec, the architecture document (section 9) or the ticket.** Never derive targets from
   the results.
3. **Generate the numbers, never type them:**
   ```bash
   python3 scripts/docs/perf_report.py <results> --title "<system>, <load>" \
       --slo "p95<=300,p99<=800,error_rate<=1" --bucket 60 \
       --series-csv docs/performance/images/p95.csv --out build/docs/results.md
   ```
   Formats are auto-detected (JMeter JTL, k6 `--summary-export`, k6 `--out csv`); other CSVs take `--columns`.
   Exclude warm-up by trimming the input and say so in the report. `--series-metric throughput` or `error_rate` gives
   the other time series.
4. **Charts for Confluence** (the Mermaid chart in `results.md` already renders on GitHub):
   ```bash
   python3 scripts/docs/chart.py docs/performance/images/p95.csv --out docs/performance/images/p95.svg \
       --title "p95 latency, <system>" --subtitle "<environment, date, load>" --y-label ms \
       --threshold 300 --threshold-label "SLO 300 ms" --png
   ```
   One measure per chart, one y-axis, a legend for two or more series, the SLO as a labelled line. Commit the CSV and
   the SVG next to the document; PNGs are for Confluence Data Center.
5. **Write the report** from `docs/templates/tech-doc/performance-report.md` into `docs/performance/<system>-<date>.md`:
   verdict first, evidence second. Analysis is evidence, then hypothesis, then confidence. Compare with the previous run
   when one exists (same table shape). List excluded data and the reason.
6. **Don't cherry-pick.** Every scenario stays in the table; the verdict comes from the script; one failing scenario is a
   failing report. Keep the method section (percentile definition, throughput formula) so reviewers can check the numbers.
7. **Quality pass** with the [tech-doc checklist](../tech-doc/quality-checklist.md), then deliver: link the report from
   the architecture document (section 13) and the PR description; publish with the `confluence-publish` skill when asked.
