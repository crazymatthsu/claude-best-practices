#!/usr/bin/env bash
# Lists files changed on this branch relative to the base branch, including
# uncommitted and untracked files. Shared by hooks, verify.sh and CI.
# Usage: scripts/changed-files.sh [base-ref]   (default: origin/main, falling back to main, then HEAD)
set -euo pipefail

base_ref="${1:-${BASE_REF:-}}"
if [[ -z "$base_ref" ]]; then
  for candidate in origin/main main; do
    if git rev-parse --verify --quiet "$candidate" >/dev/null; then base_ref="$candidate"; break; fi
  done
fi
base_ref="${base_ref:-HEAD}"
merge_base="$(git merge-base HEAD "$base_ref" 2>/dev/null || git rev-parse HEAD)"

{
  git diff --name-only "$merge_base" HEAD
  git diff --name-only HEAD
  git ls-files --others --exclude-standard
} | sort -u
