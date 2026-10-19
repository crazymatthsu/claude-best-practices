package com.example.orders.domain;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class OrderTest {

    private static final Clock CLOCK = Clock.fixed(Instant.parse("2026-01-01T10:00:00Z"), ZoneOffset.UTC);

    private static OrderLine line(String sku, int qty, String price, String currency) {
        return new OrderLine(sku, qty, new Money(new BigDecimal(price), currency));
    }

    private static Order placedOrder() {
        return Order.place("cust-1", List.of(line("SKU-1", 2, "10.00", "EUR")), CLOCK);
    }

    @Nested
    class Place {

        @Test
        void createsPlacedOrderWithTimestampFromClock() {
            Order order = placedOrder();

            assertThat(order.status()).isEqualTo(OrderStatus.PLACED);
            assertThat(order.createdAt()).isEqualTo(Instant.parse("2026-01-01T10:00:00Z"));
            assertThat(order.id()).isNotNull();
            assertThat(order.customerId()).isEqualTo("cust-1");
        }

        @Test
        void rejectsEmptyLines() {
            assertThatThrownBy(() -> Order.place("cust-1", List.of(), CLOCK))
                    .isInstanceOf(IllegalArgumentException.class);
        }

        @Test
        void rejectsBlankCustomer() {
            List<OrderLine> lines = List.of(line("SKU-1", 1, "1.00", "EUR"));
            assertThatThrownBy(() -> Order.place(" ", lines, CLOCK))
                    .isInstanceOf(IllegalArgumentException.class);
        }

        @Test
        void rejectsMixedCurrencies() {
            List<OrderLine> lines = List.of(line("SKU-1", 1, "1.00", "EUR"), line("SKU-2", 1, "1.00", "USD"));
            assertThatThrownBy(() -> Order.place("cust-1", lines, CLOCK))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("currency");
        }

        @Test
        void totalSumsAllLineSubtotals() {
            Order order = Order.place("cust-1",
                    List.of(line("SKU-1", 2, "10.00", "EUR"), line("SKU-2", 1, "5.50", "EUR")), CLOCK);

            assertThat(order.total()).isEqualTo(new Money(new BigDecimal("25.50"), "EUR"));
        }
    }

    /** Acceptance criteria from docs/specs/ORD-002-cancel-order.md. */
    @Nested
    class Cancel {

        @Test
        void ac1_placedOrderBecomesCancelledAndKeepsReason() {
            Order order = placedOrder();

            order.cancel("customer changed their mind");

            assertThat(order.status()).isEqualTo(OrderStatus.CANCELLED);
            assertThat(order.cancellationReason()).isEqualTo("customer changed their mind");
        }

        @Test
        void ac2_shippedOrderCannotBeCancelled() {
            Order order = placedOrder();
            order.markShipped();

            assertThatThrownBy(() -> order.cancel("too late"))
                    .isInstanceOf(InvalidOrderStateException.class);
            assertThat(order.status()).isEqualTo(OrderStatus.SHIPPED);
        }

        @Test
        void ac3_cancelledOrderCannotBeCancelledAgain() {
            Order order = placedOrder();
            order.cancel("first");

            assertThatThrownBy(() -> order.cancel("second"))
                    .isInstanceOf(InvalidOrderStateException.class);
            assertThat(order.cancellationReason()).isEqualTo("first");
        }

        @Test
        void ac4_reasonIsRequired() {
            Order order = placedOrder();

            assertThatThrownBy(() -> order.cancel(" ")).isInstanceOf(IllegalArgumentException.class);
            assertThat(order.status()).isEqualTo(OrderStatus.PLACED);
        }
    }

    @Nested
    class Ship {

        @Test
        void cancelledOrderCannotBeShipped() {
            Order order = placedOrder();
            order.cancel("no longer needed");

            assertThatThrownBy(order::markShipped).isInstanceOf(InvalidOrderStateException.class);
        }
    }
}
