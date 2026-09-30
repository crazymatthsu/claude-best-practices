package com.example.orders.api;

import com.example.orders.application.OrderService;
import com.example.orders.application.PlaceOrderCommand;
import com.example.orders.domain.Order;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Implements contracts/openapi/orders-api.v1.yaml. Do not add endpoints here
 * without changing the contract first (see docs/07-contracts.md).
 */
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping
    public ResponseEntity<OrderResponse> create(@Valid @RequestBody CreateOrderRequest request) {
        var command = new PlaceOrderCommand(
                request.customerId(),
                request.lines().stream().map(OrderLineDto::toDomain).toList());
        Order order = orderService.placeOrder(command);
        return ResponseEntity.created(URI.create("/api/v1/orders/" + order.id()))
                .body(OrderResponse.from(order));
    }

    @GetMapping("/{orderId}")
    public OrderResponse get(@PathVariable UUID orderId) {
        return OrderResponse.from(orderService.getOrder(orderId));
    }

    @PostMapping("/{orderId}/cancel")
    public OrderResponse cancel(@PathVariable UUID orderId, @Valid @RequestBody CancelOrderRequest request) {
        return OrderResponse.from(orderService.cancelOrder(orderId, request.reason()));
    }
}
