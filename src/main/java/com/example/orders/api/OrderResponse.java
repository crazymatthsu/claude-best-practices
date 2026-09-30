package com.example.orders.api;

import com.example.orders.domain.Order;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

/**
 * Wire representation of an order. Must match the Order schema in
 * contracts/openapi/orders-api.v1.yaml; OrdersApiContractIT enforces it.
 */
public record OrderResponse(
        UUID id,
        String customerId,
        String status,
        List<OrderLineDto> lines,
        MoneyDto total,
        Instant createdAt,
        String cancellationReason) {

    static OrderResponse from(Order order) {
        return new OrderResponse(
                order.id(),
                order.customerId(),
                order.status().name(),
                order.lines().stream().map(OrderLineDto::from).toList(),
                MoneyDto.from(order.total()),
                order.createdAt(),
                order.cancellationReason());
    }
}
