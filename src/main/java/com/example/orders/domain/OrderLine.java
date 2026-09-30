package com.example.orders.domain;

import java.util.Objects;

public record OrderLine(String sku, int quantity, Money unitPrice) {

    public OrderLine {
        Objects.requireNonNull(unitPrice, "unitPrice");
        if (sku == null || sku.isBlank()) {
            throw new IllegalArgumentException("sku must not be blank");
        }
        if (quantity < 1) {
            throw new IllegalArgumentException("quantity must be at least 1");
        }
    }

    public Money subtotal() {
        return unitPrice.times(quantity);
    }
}
