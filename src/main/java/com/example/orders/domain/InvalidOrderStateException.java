package com.example.orders.domain;

/**
 * Thrown when a state transition is not allowed, e.g. cancelling a shipped order.
 */
public class InvalidOrderStateException extends RuntimeException {

    public InvalidOrderStateException(String message) {
        super(message);
    }
}
