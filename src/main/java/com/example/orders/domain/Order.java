package com.example.orders.domain;

import java.time.Clock;
import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * Order aggregate. All state transitions go through methods on this class so
 * the rules in docs/specs live in exactly one place.
 */
public final class Order {

    private final UUID id;
    private final String customerId;
    private final List<OrderLine> lines;
    private final Instant createdAt;
    private OrderStatus status;
    private String cancellationReason;

    private Order(UUID id, String customerId, List<OrderLine> lines, Instant createdAt) {
        this.id = id;
        this.customerId = customerId;
        this.lines = List.copyOf(lines);
        this.createdAt = createdAt;
        this.status = OrderStatus.PLACED;
    }

    public static Order place(String customerId, List<OrderLine> lines, Clock clock) {
        if (customerId == null || customerId.isBlank()) {
            throw new IllegalArgumentException("customerId must not be blank");
        }
        Objects.requireNonNull(lines, "lines");
        if (lines.isEmpty()) {
            throw new IllegalArgumentException("an order needs at least one line");
        }
        long currencies = lines.stream().map(l -> l.unitPrice().currency()).distinct().count();
        if (currencies > 1) {
            throw new IllegalArgumentException("all lines must use the same currency");
        }
        return new Order(UUID.randomUUID(), customerId, lines, clock.instant());
    }

    /** ORD-002: only a PLACED order can be cancelled. */
    public void cancel(String reason) {
        if (reason == null || reason.isBlank()) {
            throw new IllegalArgumentException("a cancellation reason is required");
        }
        if (status != OrderStatus.PLACED) {
            throw new InvalidOrderStateException("order " + id + " cannot be cancelled in status " + status);
        }
        status = OrderStatus.CANCELLED;
        cancellationReason = reason;
    }

    public void markShipped() {
        if (status != OrderStatus.PLACED) {
            throw new InvalidOrderStateException("order " + id + " cannot be shipped in status " + status);
        }
        status = OrderStatus.SHIPPED;
    }

    public Money total() {
        String currency = lines.getFirst().unitPrice().currency();
        return lines.stream().map(OrderLine::subtotal).reduce(Money.zero(currency), Money::plus);
    }

    public UUID id() {
        return id;
    }

    public String customerId() {
        return customerId;
    }

    public List<OrderLine> lines() {
        return lines;
    }

    public Instant createdAt() {
        return createdAt;
    }

    public OrderStatus status() {
        return status;
    }

    public String cancellationReason() {
        return cancellationReason;
    }
}
