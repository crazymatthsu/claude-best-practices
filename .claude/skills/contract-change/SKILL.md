---
name: contract-change
description: Change an API contract in contracts/ (OpenAPI) safely. Classify it as additive or breaking, bump the version, update the changelog and ADR, and assess consumer impact. Use before editing any file under contracts/, or when a feature needs a new/changed endpoint or field.
---

# Contract change procedure

The contract is a promise to other teams. It **can** change, but always deliberately, visibly and in versioned form.

## 1. Confirm the change is wanted
- State in one sentence what changes and why (link the spec/issue).
- If the only reason is "the code/test disagrees with the contract", **stop**. Fix the code instead.

## 2. Classify (see [compatibility-rules.md](compatibility-rules.md))
- **Additive**: new endpoint, new optional request field, new response field, new enum value *only if* consumers
  are known to tolerate unknown values → **minor** bump.
- **Breaking**: anything else that can break an existing client → **major** version, which means a new file.
- When unsure, treat it as breaking and ask the user.

## 3. Apply
Additive:
1. Edit `contracts/openapi/orders-api.v1.yaml` (a hook will ask the human to confirm).
2. Bump `info.version` minor (1.1.0 → 1.2.0).
3. Add an entry at the top of `contracts/CHANGELOG.md`: version, "additive", bullets, spec/ADR links.

Breaking:
1. Write an ADR first (`write-adr` skill) covering why, alternatives, migration and sunset date for v1.
2. Copy to `orders-api.v2.yaml`, set `info.version: 2.0.0`, and apply the change there. Leave v1 untouched.
3. CHANGELOG entry marked **breaking** with a migration note.
4. Plan the parallel `/api/v2` implementation. v1 tests must keep passing.

## 4. Make code follow the contract
- Update the DTOs in `api/` to match field for field.
- Add or extend `*IT` tests (`src/integrationTest`) with `.andExpect(matchesContract())` for every new response code.

## 5. Verify
- `scripts/check-contract-change.sh` (CHANGELOG + version bump + ADR checks)
- `scripts/verify.sh`
- In the PR description, fill the "Contract impact" section: classification, consumers affected, rollout.
