package com.example.orders.api;

import com.example.orders.domain.OrderLine;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record OrderLineDto(
        @NotBlank String sku,
        @Min(1) int quantity,
        @NotNull @Valid MoneyDto unitPrice) {

    static OrderLineDto from(OrderLine line) {
        return new OrderLineDto(line.sku(), line.quantity(), MoneyDto.from(line.unitPrice()));
    }

    OrderLine toDomain() {
        return new OrderLine(sku, quantity, unitPrice.toDomain());
    }
}
