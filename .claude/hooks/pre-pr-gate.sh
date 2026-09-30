#!/usr/bin/env bash
# PreToolUse(Bash | mcp__github__create_pull_request): before code leaves the machine
# (git push / gh pr create / GitHub MCP PR creation), run the same gate as CI.
# Exit 2 blocks the tool call and feeds stderr back to Claude so it can fix and retry.
set -uo pipefail

input="$(cat)"
tool="$(jq -r '.tool_name // empty' <<<"$input")"
cmd="$(jq -r '.tool_input.command // empty' <<<"$input")"

if [[ "$tool" == "Bash" ]]; then
  # Only gate commands that publish code; everything else passes straight through.
  grep -qE '(^|[;&|[:space:]])(git[[:space:]]+push|gh[[:space:]]+pr[[:space:]]+create)' <<<"$cmd" || exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
if ! out="$(scripts/verify.sh 2>&1)"; then
  {
    echo "Blocked: pre-PR gate failed. Fix the problems below, then try again."
    echo "Don't skip, disable or weaken tests to get past this gate."
    echo "$out"
  } >&2
  exit 2
fi
exit 0
