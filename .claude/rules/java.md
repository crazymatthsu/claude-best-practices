---
paths:
  - "src/main/**/*.java"
---
# Java production code rules

- Constructor injection only. No `@Autowired` fields (ArchitectureTest fails otherwise).
- Use records for DTOs, commands and value objects. Aggregates (`Order`) are final classes with behaviour.
- Validate invariants in the domain constructor/factory. Bean Validation annotations belong on `api` DTOs only.
- Never pass time implicitly: inject `java.time.Clock`. Never call `Instant.now()` or `LocalDateTime.now()` directly.
- Money is `Money` (BigDecimal, scale 2). Never `double` for amounts.
- Errors: domain throws `IllegalArgumentException` / `InvalidOrderStateException`, application throws
  `OrderNotFoundException`. `ApiExceptionHandler` maps them to problem+json. Don't catch and swallow.
- API DTOs mirror `contracts/openapi/orders-api.v1.yaml` field for field. Adding a field to a DTO is a contract change.
- No new dependencies in `build.gradle.kts` without asking first. Never change the Java toolchain version.
