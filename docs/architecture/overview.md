# Architecture overview: orders-service

Enforced by [`ArchitectureTest`](../../src/test/java/com/example/orders/architecture/ArchitectureTest.java).
If this doc and that test disagree, the test wins. Fix the doc.

## Context

```mermaid
flowchart LR
    Client[Client apps<br/>web shop, back office] -->|HTTPS JSON<br/>orders-api v1| OS[orders-service]
    OS -.future.-> DB[(Orders DB)]
    Contract[[contracts/openapi/<br/>orders-api.v1.yaml]] -.defines.-> OS
```

## Layers

```mermaid
flowchart TB
    subgraph api["api: HTTP adapter"]
        OC[OrderController] --> DTO[DTOs: CreateOrderRequest,<br/>OrderResponse, …]
        EH[ApiExceptionHandler<br/>→ problem+json]
    end
    subgraph application["application: use cases"]
        OSV[OrderService]
        REPO[[OrderRepository port]]
    end
    subgraph domain["domain: plain Java"]
        O[Order aggregate]
        M[Money / OrderLine]
    end
    subgraph infrastructure["infrastructure: adapters"]
        IMR[InMemoryOrderRepository]
        CLK[ClockConfig]
    end
    OC --> OSV
    OSV --> O
    OSV --> REPO
    IMR -.implements.-> REPO
    O --> M
```

| Rule | Why |
|---|---|
| `domain` depends on nothing (no Spring, no Jakarta) | trivially unit-testable, portable |
| Business rules live in `Order` | one place to read, test and change them |
| `application` owns the `OrderRepository` port, `infrastructure` implements it | swap in-memory for JPA without touching the core |
| `api` DTOs mirror the OpenAPI contract | `OrdersApiContractIT` checks every response |
| Only `api` and `infrastructure` know about the outside world | adapters at the edges |

## Domain model

```mermaid
classDiagram
    class Order {
        UUID id
        String customerId
        List~OrderLine~ lines
        Instant createdAt
        OrderStatus status
        String cancellationReason
        +place(customerId, lines, clock)$ Order
        +cancel(reason)
        +markShipped()
        +total() Money
    }
    class OrderLine {
        String sku
        int quantity
        Money unitPrice
        +subtotal() Money
    }
    class Money {
        BigDecimal amount
        String currency
        +plus(Money) Money
        +times(int) Money
    }
    class OrderStatus {
        <<enumeration>>
        PLACED
        SHIPPED
        CANCELLED
    }
    Order "1" *-- "1..*" OrderLine
    OrderLine --> Money
    Order --> OrderStatus
```

## Order lifecycle

Matches the transitions in `Order` and the tests in `OrderTest`.

```mermaid
stateDiagram-v2
    [*] --> PLACED: place()
    PLACED --> SHIPPED: markShipped()
    PLACED --> CANCELLED: cancel(reason)
    SHIPPED --> [*]
    CANCELLED --> [*]
    note right of SHIPPED: cancel() → 409 InvalidOrderStateException
```

## Cancel order flow (ORD-002)

```mermaid
sequenceDiagram
    actor C as Client
    participant OC as OrderController
    participant S as OrderService
    participant R as OrderRepository
    participant O as Order
    C->>OC: POST /api/v1/orders/{id}/cancel {reason}
    OC->>OC: @Valid CancelOrderRequest (400 if blank)
    OC->>S: cancelOrder(id, reason)
    S->>R: findById(id)
    alt not found
        R-->>S: empty
        S-->>OC: OrderNotFoundException
        OC-->>C: 404 problem+json
    else found
        S->>O: cancel(reason)
        alt status != PLACED
            O-->>S: InvalidOrderStateException
            OC-->>C: 409 problem+json
        else PLACED
            S->>R: save(order)
            OC-->>C: 200 Order{status: CANCELLED, cancellationReason}
        end
    end
```
