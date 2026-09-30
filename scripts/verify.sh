#!/usr/bin/env bash
# Pre-PR gate. Runs the same checks as CI. Quiet on success, detailed on failure,
# so it costs Claude almost no context when things are green.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"

log="$(mktemp)"
trap 'rm -f "$log"' EXIT

scripts/check-tests-present.sh "$@" || exit 1
scripts/check-contract-change.sh "$@" || exit 1

if ./gradlew check --console=plain >"$log" 2>&1; then
  echo "✓ gradle check: build, unit tests, integration/contract tests, architecture rules, coverage gate"
  exit 0
fi

echo "✗ gradle check failed. Relevant output:" >&2
# Keep failing test names, assertion messages, compiler errors and rule violations; drop stack frames and noise.
grep -E -A3 'FAILED$|error:|What went wrong|violated|tests completed' "$log" \
  | grep -v -E '^\s+at |^--$|^\s*$|^> Task|Try:|Run with --|Get more help|Build Scan|JAVA_TOOL_OPTIONS|Sharing is only supported|Incubating' \
  | head -40 >&2
echo "  Full log: re-run './gradlew check'. HTML reports: build/reports/tests/." >&2
exit 1
