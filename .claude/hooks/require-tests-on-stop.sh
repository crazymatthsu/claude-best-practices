#!/usr/bin/env bash
# Stop: when Claude thinks it's done, make sure production changes came with tests.
# Cheap (git only, no build). The full build runs in the pre-PR gate.
set -uo pipefail

input="$(cat)"
# Avoid loops: if we already blocked once this turn, let Claude stop.
[[ "$(jq -r '.stop_hook_active // false' <<<"$input")" == "true" ]] && exit 0

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
if ! out="$(scripts/check-tests-present.sh 2>&1)"; then
  echo "$out" >&2
  echo "Write the missing tests before finishing (tdd-feature skill), or explain to the user why none are needed." >&2
  exit 2
fi
exit 0
