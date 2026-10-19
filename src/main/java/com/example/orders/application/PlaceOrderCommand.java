package com.example.orders.application;

import com.example.orders.domain.OrderLine;
import java.util.List;

public record PlaceOrderCommand(String customerId, List<OrderLine> lines) {
}
