package com.example.orders.api;

import com.example.orders.application.OrderNotFoundException;
import com.example.orders.domain.InvalidOrderStateException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * Maps domain/application errors to RFC 9457 problem details, as declared in the contract.
 */
@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(OrderNotFoundException.class)
    ProblemDetail notFound(OrderNotFoundException e) {
        return problem(HttpStatus.NOT_FOUND, "Order not found", e.getMessage());
    }

    @ExceptionHandler(InvalidOrderStateException.class)
    ProblemDetail conflict(InvalidOrderStateException e) {
        return problem(HttpStatus.CONFLICT, "Invalid order state", e.getMessage());
    }

    @ExceptionHandler(IllegalArgumentException.class)
    ProblemDetail badRequest(IllegalArgumentException e) {
        return problem(HttpStatus.BAD_REQUEST, "Invalid request", e.getMessage());
    }

    private static ProblemDetail problem(HttpStatus status, String title, String detail) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(status, detail);
        problem.setTitle(title);
        return problem;
    }
}
