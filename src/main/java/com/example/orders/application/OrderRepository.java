package com.example.orders.application;

import com.example.orders.domain.Order;
import java.util.Optional;
import java.util.UUID;

/**
 * Port owned by the application layer; infrastructure provides the adapter.
 */
public interface OrderRepository {

    Order save(Order order);

    Optional<Order> findById(UUID id);
}
