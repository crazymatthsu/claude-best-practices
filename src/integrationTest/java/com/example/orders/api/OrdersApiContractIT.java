package com.example.orders.api;

import static com.atlassian.oai.validator.mockmvc.OpenApiValidationMatchers.openApi;
import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.orders.application.OrderRepository;
import com.jayway.jsonpath.JsonPath;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultMatcher;

/**
 * Integration + contract test. Boots the full app and checks every request/response
 * against contracts/openapi/orders-api.v1.yaml. If the code drifts from the contract,
 * this fails — the fix is almost always in the code, not the contract.
 */
@SpringBootTest
@AutoConfigureMockMvc
class OrdersApiContractIT {

    private static final String CONTRACT = "contracts/openapi/orders-api.v1.yaml";

    private static final String VALID_ORDER = """
            {"customerId":"cust-42","lines":[
              {"sku":"SKU-1","quantity":2,"unitPrice":{"amount":10.00,"currency":"EUR"}},
              {"sku":"SKU-2","quantity":1,"unitPrice":{"amount":5.50,"currency":"EUR"}}]}
            """;

    @Autowired
    MockMvc mvc;

    @Autowired
    OrderRepository repository;

    private static ResultMatcher matchesContract() {
        return openApi().isValid(CONTRACT);
    }

    private String createOrder() throws Exception {
        String body = mvc.perform(post("/api/v1/orders").contentType(MediaType.APPLICATION_JSON).content(VALID_ORDER))
                .andExpect(status().isCreated())
                .andReturn().getResponse().getContentAsString();
        return JsonPath.read(body, "$.id");
    }

    @Test
    void createOrder_returns201WithLocationAndTotal() throws Exception {
        mvc.perform(post("/api/v1/orders").contentType(MediaType.APPLICATION_JSON).content(VALID_ORDER))
                .andExpect(status().isCreated())
                .andExpect(header().string("Location", containsString("/api/v1/orders/")))
                .andExpect(jsonPath("$.status").value("PLACED"))
                .andExpect(jsonPath("$.total.amount").value(25.50))
                .andExpect(matchesContract());
    }

    @Test
    void createOrder_withoutLines_returns400Problem() throws Exception {
        mvc.perform(post("/api/v1/orders").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"customerId\":\"cust-42\",\"lines\":[]}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400));
    }

    @Test
    void createOrder_withMixedCurrencies_returns400Problem() throws Exception {
        String mixed = """
                {"customerId":"cust-42","lines":[
                  {"sku":"SKU-1","quantity":1,"unitPrice":{"amount":1.00,"currency":"EUR"}},
                  {"sku":"SKU-2","quantity":1,"unitPrice":{"amount":1.00,"currency":"USD"}}]}
                """;
        mvc.perform(post("/api/v1/orders").contentType(MediaType.APPLICATION_JSON).content(mixed))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.title").value("Invalid request"))
                .andExpect(matchesContract());
    }

    @Test
    void getOrder_returnsCreatedOrder() throws Exception {
        String id = createOrder();

        mvc.perform(get("/api/v1/orders/{id}", id))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(id))
                .andExpect(matchesContract());
    }

    @Test
    void getOrder_unknownId_returns404Problem() throws Exception {
        mvc.perform(get("/api/v1/orders/{id}", UUID.randomUUID()))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.title").value("Order not found"))
                .andExpect(matchesContract());
    }

    // --- ORD-002 cancel order: acceptance criteria end-to-end ---

    @Test
    void cancelOrder_placedOrder_returns200Cancelled() throws Exception {
        String id = createOrder();

        mvc.perform(post("/api/v1/orders/{id}/cancel", id).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"reason\":\"customer request\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("CANCELLED"))
                .andExpect(jsonPath("$.cancellationReason").value("customer request"))
                .andExpect(matchesContract());
    }

    @Test
    void cancelOrder_shippedOrder_returns409Problem() throws Exception {
        String id = createOrder();
        repository.findById(UUID.fromString(id)).orElseThrow().markShipped();

        mvc.perform(post("/api/v1/orders/{id}/cancel", id).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"reason\":\"too late\"}"))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.title").value("Invalid order state"))
                .andExpect(matchesContract());
    }

    @Test
    void cancelOrder_alreadyCancelled_returns409AndKeepsOriginalReason() throws Exception {
        String id = createOrder();
        mvc.perform(post("/api/v1/orders/{id}/cancel", id).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"reason\":\"first\"}"))
                .andExpect(status().isOk());

        mvc.perform(post("/api/v1/orders/{id}/cancel", id).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"reason\":\"second\"}"))
                .andExpect(status().isConflict())
                .andExpect(matchesContract());
        mvc.perform(get("/api/v1/orders/{id}", id))
                .andExpect(jsonPath("$.cancellationReason").value("first"));
    }

    @Test
    void cancelOrder_missingReason_returns400Problem() throws Exception {
        String id = createOrder();

        mvc.perform(post("/api/v1/orders/{id}/cancel", id).contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void cancelOrder_unknownId_returns404Problem() throws Exception {
        mvc.perform(post("/api/v1/orders/{id}/cancel", UUID.randomUUID()).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"reason\":\"x\"}"))
                .andExpect(status().isNotFound())
                .andExpect(matchesContract());
    }
}
