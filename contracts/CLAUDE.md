# contracts/ — read before editing anything here

Files here are **public promises** to other teams. Code follows the contract, not the other way round.

- Never edit a contract to make a failing test pass. Fix the code instead.
- To change a contract, use the `contract-change` skill. It walks through classification, version bump,
  CHANGELOG, ADR and consumer impact.
- Additive (new optional field, new endpoint) → minor bump in `info.version` + CHANGELOG entry.
- Breaking (remove/rename field, new required request field, type change, status code change) →
  new file `orders-api.v2.yaml` + ADR + migration note. Keep v1 working until its sunset date.
- `scripts/check-contract-change.sh` enforces this in CI and in the pre-PR gate.
