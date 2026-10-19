package com.example.orders.application;

import com.example.orders.domain.Order;
import java.time.Clock;
import java.util.UUID;
import org.springframework.stereotype.Service;

/**
 * Use cases for orders. Thin: rules live in {@link Order}, persistence behind {@link OrderRepository}.
 */
@Service
public class OrderService {

    private final OrderRepository repository;
    private final Clock clock;

    public OrderService(OrderRepository repository, Clock clock) {
        this.repository = repository;
        this.clock = clock;
    }

    public Order placeOrder(PlaceOrderCommand command) {
        Order order = Order.place(command.customerId(), command.lines(), clock);
        return repository.save(order);
    }

    public Order getOrder(UUID id) {
        return repository.findById(id).orElseThrow(() -> new OrderNotFoundException(id));
    }

    public Order cancelOrder(UUID id, String reason) {
        Order order = getOrder(id);
        order.cancel(reason);
        return repository.save(order);
    }
}
