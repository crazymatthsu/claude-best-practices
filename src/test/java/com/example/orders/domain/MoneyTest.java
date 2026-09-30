package com.example.orders.domain;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class MoneyTest {

    @Test
    void constructor_normalisesScaleToTwoDecimals() {
        assertThat(new Money(new BigDecimal("1.5"), "EUR").amount()).isEqualByComparingTo("1.50");
        assertThat(new Money(new BigDecimal("1.5"), "EUR").amount().scale()).isEqualTo(2);
    }

    @Test
    void constructor_rejectsNegativeAmount() {
        assertThatThrownBy(() -> new Money(new BigDecimal("-0.01"), "EUR"))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void constructor_rejectsNonIsoCurrency() {
        assertThatThrownBy(() -> new Money(BigDecimal.ONE, "euro"))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void plus_addsAmountsInSameCurrency() {
        Money sum = new Money(new BigDecimal("1.20"), "EUR").plus(new Money(new BigDecimal("2.30"), "EUR"));
        assertThat(sum).isEqualTo(new Money(new BigDecimal("3.50"), "EUR"));
    }

    @Test
    void plus_rejectsDifferentCurrencies() {
        Money eur = new Money(BigDecimal.ONE, "EUR");
        Money usd = new Money(BigDecimal.ONE, "USD");
        assertThatThrownBy(() -> eur.plus(usd)).isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void times_multipliesByQuantity() {
        assertThat(new Money(new BigDecimal("2.50"), "EUR").times(3))
                .isEqualTo(new Money(new BigDecimal("7.50"), "EUR"));
    }
}
