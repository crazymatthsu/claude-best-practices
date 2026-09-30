# ORD-002: Cancel an order

| Field | Value |
|---|---|
| Status | Done |
| Owner (PM) | @pm |
| Tech lead | @lead |
| Contract impact | **additive**: new endpoint + optional field (orders-api 1.0.0 → 1.1.0) |
| Related | [ADR-0003](../adr/0003-order-cancellation.md) |

## Problem
Customers who order by mistake contact support, who can't cancel orders in the system. We need a way to cancel
orders that haven't shipped, and to keep the reason for reporting.

## Acceptance criteria
- **AC1**: Given a `PLACED` order, when the client cancels it with a reason, then it gets 200 and the order has status `CANCELLED` with `cancellationReason` set.
- **AC2**: Given a `SHIPPED` order, when the client cancels it, then it gets 409 problem+json and the order is unchanged.
- **AC3**: Given an already `CANCELLED` order, when the client cancels it again, then it gets 409 and the original reason is kept.
- **AC4**: Given no or a blank reason, when the client cancels, then it gets 400 and the order is unchanged.
- **AC5**: Given an unknown order id, when the client cancels, then it gets 404 problem+json.

## Contract impact
- `POST /api/v1/orders/{orderId}/cancel` with body `{reason: string(1..500)}` → 200 `Order` | 400 | 404 | 409
- `Order.cancellationReason` (optional string)

## Flow
See [architecture/overview.md, cancel flow](../architecture/overview.md#cancel-order-flow-ord-002).

## Out of scope
- Refunds (ORD-010), partial cancellation of lines, customer notification e-mails.
- Authorisation (who may cancel). Handled by the gateway for now.

## Open questions
- [x] Should cancellation of `SHIPPED` orders be a return instead? → Yes, separate feature (ORD-011).

## Traceability
| AC | Unit test | Integration test |
|----|-----------|------------------|
| AC1 | `OrderTest.Cancel.ac1_placedOrderBecomesCancelledAndKeepsReason` | `OrdersApiContractIT.cancelOrder_placedOrder_returns200Cancelled` |
| AC2 | `OrderTest.Cancel.ac2_shippedOrderCannotBeCancelled` | `OrdersApiContractIT.cancelOrder_shippedOrder_returns409Problem` |
| AC3 | `OrderTest.Cancel.ac3_cancelledOrderCannotBeCancelledAgain` | `OrdersApiContractIT.cancelOrder_alreadyCancelled_returns409AndKeepsOriginalReason` |
| AC4 | `OrderTest.Cancel.ac4_reasonIsRequired` | `OrdersApiContractIT.cancelOrder_missingReason_returns400Problem` |
| AC5 | `OrderServiceTest.cancelOrder_unknownId_throwsNotFound` | `OrdersApiContractIT.cancelOrder_unknownId_returns404Problem` |
