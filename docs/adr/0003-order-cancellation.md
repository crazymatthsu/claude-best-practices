# 0003: Order cancellation as an explicit command endpoint

- **Status:** Accepted
- **Date:** 2026-09-30
- **Deciders:** tech lead, API owners, PM
- **Related:** [ORD-002](../specs/ORD-002-cancel-order.md), orders-api 1.1.0

## Context
Customers need to cancel orders that haven't shipped yet. We have to decide how to model this in the API
and whether the change is backward compatible.

## Options considered
1. **`PATCH /orders/{id}` with `{status: CANCELLED}`**: generic, but lets clients attempt any status transition, and
   the reason field only makes sense for one of them.
2. **`DELETE /orders/{id}`**: suggests the order disappears, but we must keep it for audit.
3. **`POST /orders/{id}/cancel` with `{reason}`**: an explicit command that maps 1:1 to `Order.cancel()`, with
   a clear 409 for invalid transitions.

## Decision
Option 3. Add optional response field `cancellationReason`. Both changes are **additive**, so orders-api 1.0.0 → 1.1.0 with no new major version.

## Consequences
- Easier: clear semantics, straightforward tests per acceptance criterion, no v2 needed.
- Harder: each future transition (e.g. "return") needs its own endpoint.
