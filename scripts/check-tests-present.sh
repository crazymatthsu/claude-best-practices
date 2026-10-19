#!/usr/bin/env bash
# Fails if production Java code changed but no test code changed.
# Cheap heuristic that catches "forgot the tests"; coverage and review catch the rest.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

changed="$(scripts/changed-files.sh "$@")"
main_changes="$(grep -E '^src/main/java/.*\.java$' <<<"$changed" || true)"
test_changes="$(grep -E '^src/(test|integrationTest)/java/.*\.java$' <<<"$changed" || true)"

if [[ -n "$main_changes" && -z "$test_changes" ]]; then
  echo "✗ Production code changed without any test changes:" >&2
  sed 's/^/    /' <<<"$main_changes" >&2
  echo "  Add or update unit tests (src/test, *Test) and, for HTTP behaviour, integration tests (src/integrationTest, *IT)." >&2
  echo "  See docs/08-testing-strategy.md." >&2
  exit 1
fi
echo "✓ tests present for production changes"
