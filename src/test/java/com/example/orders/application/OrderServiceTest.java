package com.example.orders.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.example.orders.domain.Money;
import com.example.orders.domain.Order;
import com.example.orders.domain.OrderLine;
import com.example.orders.domain.OrderStatus;
import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * Unit test with a hand-written fake instead of mocks: asserts behaviour, not call sequences.
 */
class OrderServiceTest {

    private final FakeOrderRepository repository = new FakeOrderRepository();
    private final OrderService service = new OrderService(
            repository, Clock.fixed(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC));

    private Order placeOne() {
        return service.placeOrder(new PlaceOrderCommand("cust-1",
                List.of(new OrderLine("SKU-1", 1, new Money(new BigDecimal("9.99"), "EUR")))));
    }

    @Test
    void placeOrder_persistsTheOrder() {
        Order order = placeOne();

        assertThat(repository.findById(order.id())).contains(order);
    }

    @Test
    void getOrder_unknownId_throwsNotFound() {
        UUID unknown = UUID.randomUUID();

        assertThatThrownBy(() -> service.getOrder(unknown)).isInstanceOf(OrderNotFoundException.class);
    }

    @Test
    void cancelOrder_cancelsAndPersists() {
        Order order = placeOne();

        service.cancelOrder(order.id(), "duplicate");

        assertThat(repository.findById(order.id()).orElseThrow().status()).isEqualTo(OrderStatus.CANCELLED);
    }

    @Test
    void cancelOrder_unknownId_throwsNotFound() {
        UUID unknown = UUID.randomUUID();

        assertThatThrownBy(() -> service.cancelOrder(unknown, "x")).isInstanceOf(OrderNotFoundException.class);
    }

    private static final class FakeOrderRepository implements OrderRepository {

        private final Map<UUID, Order> store = new HashMap<>();

        @Override
        public Order save(Order order) {
            store.put(order.id(), order);
            return order;
        }

        @Override
        public Optional<Order> findById(UUID id) {
            return Optional.ofNullable(store.get(id));
        }
    }
}
