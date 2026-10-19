# ORD-001: Place an order

| Field | Value |
|---|---|
| Status | Done |
| Owner (PM) | @pm |
| Contract impact | additive (initial: orders-api 1.0.0) |
| Related | ADR-0002 |

## Problem
Clients need to place an order with one or more lines and get back the order with its total.

## Acceptance criteria
- **AC1**: Given valid lines in one currency, when the client POSTs `/api/v1/orders`, then it gets 201, a `Location` header, status `PLACED`, and a total equal to the sum of the line subtotals.
- **AC2**: Given no lines, when the client places an order, then it gets 400 problem+json.
- **AC3**: Given lines in different currencies, when the client places an order, then it gets 400 problem+json.
- **AC4**: Given an existing order id, when the client GETs it, then it gets 200 with the order. An unknown id gives 404.

## Out of scope
Payment, stock reservation, persistence beyond memory.

## Traceability
| AC | Unit test | Integration test |
|----|-----------|------------------|
| AC1 | `OrderTest.Place.totalSumsAllLineSubtotals` | `OrdersApiContractIT.createOrder_returns201WithLocationAndTotal` |
| AC2 | `OrderTest.Place.rejectsEmptyLines` | `OrdersApiContractIT.createOrder_withoutLines_returns400Problem` |
| AC3 | `OrderTest.Place.rejectsMixedCurrencies` | `OrdersApiContractIT.createOrder_withMixedCurrencies_returns400Problem` |
| AC4 | `OrderServiceTest.getOrder_unknownId_throwsNotFound` | `OrdersApiContractIT.getOrder_returnsCreatedOrder`, `getOrder_unknownId_returns404Problem` |
