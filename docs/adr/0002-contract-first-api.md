# 0002: Contract-first HTTP API

- **Status:** Accepted
- **Date:** 2026-09-30
- **Deciders:** tech lead, API owners
- **Related:** contracts/openapi/orders-api.v1.yaml 1.0.0

## Context
Several clients consume the Orders API. With AI-assisted development, the fastest way to make a failing test pass
is sometimes to change the API shape, which silently breaks consumers.

## Options considered
1. **Code-first** (generate OpenAPI from annotations): low effort, but the contract becomes a by-product of the code
   and changes whenever the code does.
2. **Contract-first** (hand-owned OpenAPI in `contracts/`, code validated against it): the contract is an explicit,
   reviewed artefact. It needs a validation test.

## Decision
Contract-first. `contracts/openapi/*.yaml` is the source of truth. `OrdersApiContractIT` validates every response.
Changes follow `docs/07-contracts.md` (hook, CHANGELOG, version bump, oasdiff, CODEOWNERS).

## Consequences
- Easier: consumer trust, safe AI-assisted changes, reviewable API evolution.
- Harder: every API change touches two places (contract + DTO). This is intended friction.
