package com.example.orders.api;

import com.example.orders.domain.Money;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import java.math.BigDecimal;

public record MoneyDto(
        @NotNull @DecimalMin("0.00") BigDecimal amount,
        @NotNull @Pattern(regexp = "[A-Z]{3}") String currency) {

    static MoneyDto from(Money money) {
        return new MoneyDto(money.amount(), money.currency());
    }

    Money toDomain() {
        return new Money(amount, currency);
    }
}
