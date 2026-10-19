#!/usr/bin/env bash
# PreToolUse(Edit|Write|MultiEdit): contract files are never edited silently.
# Returns "ask" so a human confirms every contract edit. The contract can still change,
# but only on purpose. Reason text is shown to both the user and Claude.
set -euo pipefail

file="$(jq -r '.tool_input.file_path // empty')"
[[ -z "$file" ]] && exit 0

case "$file" in
  */contracts/openapi/*|contracts/openapi/*)
    jq -n --arg f "$file" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "ask",
        permissionDecisionReason: ("CONTRACT CHANGE: " + $f + " is a public API contract. Approve only if this change is intended and the contract-change skill was followed (classification, version bump, CHANGELOG, ADR if breaking). Never change a contract to make a test pass.")
      }
    }'
    ;;
esac
exit 0
