package com.example.orders.domain;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class OrderLineTest {

    private static final Money PRICE = new Money(new BigDecimal("3.00"), "EUR");

    @Test
    void subtotal_isUnitPriceTimesQuantity() {
        assertThat(new OrderLine("SKU-1", 4, PRICE).subtotal())
                .isEqualTo(new Money(new BigDecimal("12.00"), "EUR"));
    }

    @ParameterizedTest
    @ValueSource(ints = {0, -1})
    void rejectsQuantityBelowOne(int quantity) {
        assertThatThrownBy(() -> new OrderLine("SKU-1", quantity, PRICE))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void rejectsBlankSku() {
        assertThatThrownBy(() -> new OrderLine("", 1, PRICE)).isInstanceOf(IllegalArgumentException.class);
    }
}
