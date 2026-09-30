# Contract changelog

Every change under `contracts/` gets an entry here, newest first.
Classify each change as **additive** (minor bump) or **breaking** (major bump + ADR + new file).
See [docs/07-contracts.md](../docs/07-contracts.md).

## orders-api 1.1.0 — additive

- Added `POST /api/v1/orders/{orderId}/cancel` (spec: [ORD-002](../docs/specs/ORD-002-cancel-order.md)).
- Added optional `Order.cancellationReason`.
- Decision: [ADR-0003](../docs/adr/0003-order-cancellation.md).

## orders-api 1.0.0 — initial

- `POST /api/v1/orders`, `GET /api/v1/orders/{orderId}`.
- Decision: [ADR-0002](../docs/adr/0002-contract-first-api.md).
