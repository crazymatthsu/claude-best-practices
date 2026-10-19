#!/usr/bin/env bash
# Enforces the contract change process (docs/07-contracts.md):
#   1. any change to contracts/openapi/* must be recorded in contracts/CHANGELOG.md
#   2. a modified spec must bump info.version
#   3. a new major-version spec file (…v2.yaml) must come with a new/changed ADR
# Breaking-change *detection* is done by oasdiff in CI (.github/workflows/ci.yml).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

changed="$(scripts/changed-files.sh "$@")"
specs="$(grep -E '^contracts/openapi/.*\.ya?ml$' <<<"$changed" || true)"
[[ -z "$specs" ]] && { echo "✓ no contract changes"; exit 0; }

fail=0
if ! grep -qx 'contracts/CHANGELOG.md' <<<"$changed"; then
  echo "✗ contracts changed but contracts/CHANGELOG.md was not updated" >&2
  fail=1
fi

base_ref="${1:-${BASE_REF:-origin/main}}"
git rev-parse --verify --quiet "$base_ref" >/dev/null || base_ref=HEAD
merge_base="$(git merge-base HEAD "$base_ref" 2>/dev/null || git rev-parse HEAD)"

version_of() { grep -m1 -E '^\s+version:' | awk '{print $2}'; }

while IFS= read -r spec; do
  [[ -f "$spec" ]] || continue
  if git cat-file -e "$merge_base:$spec" 2>/dev/null; then
    old="$(git show "$merge_base:$spec" | version_of)"
    new="$(version_of < "$spec")"
    if [[ "$old" == "$new" ]]; then
      echo "✗ $spec changed but info.version is still $old" >&2
      fail=1
    fi
  else
    if ! grep -qE '^docs/adr/[0-9]{4}-.*\.md$' <<<"$changed"; then
      echo "✗ new contract file $spec needs an ADR in docs/adr/" >&2
      fail=1
    fi
  fi
done <<<"$specs"

if [[ $fail -ne 0 ]]; then
  echo "  Follow the contract-change skill / docs/07-contracts.md." >&2
  exit 1
fi
echo "✓ contract change is versioned and recorded"
