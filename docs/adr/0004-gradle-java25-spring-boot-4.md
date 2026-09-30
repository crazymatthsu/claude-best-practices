# 0004: Gradle 9, Java 25 and Spring Boot 4.1

- **Status:** Accepted
- **Date:** 2026-09-30
- **Deciders:** tech lead

## Context
This repo is a template that new projects copy. Its build must be current and fast, and it must make the
unit/integration split impossible to blur, because the guardrails (hooks, CI) depend on that split.

## Options considered
1. **Maven 3.9 + Java 21 + Spring Boot 3.5**: familiar, but Boot 3.5's open-source support has ended, and surefire/failsafe
   separate tests by naming convention only.
2. **Gradle 9 (Kotlin DSL, wrapper) + Java 25 (LTS) + Spring Boot 4.1**: current LTS JDK and supported Boot line. JVM test
   suites give unit and integration tests separate source sets *and* classpaths. The build cache and configuration cache
   keep Claude's frequent feedback loop fast.

## Decision
Option 2. The wrapper pins Gradle 9.8. `java.toolchain` pins Java 25, and the foojay resolver downloads it where it's missing.
Unit tests live in `src/test` (`test` suite, no Spring on the classpath). Integration and contract tests live in
`src/integrationTest` (`integrationTest` suite). `./gradlew check` runs both plus the JaCoCo gate.

## Consequences
- Easier: one command (`./gradlew check`) for local, hooks and CI. Unit tests can't boot Spring by accident.
- Harder: Gradle caching must know every file a test reads. `contracts/` is declared as an input of `integrationTest`,
  otherwise a contract-only change would be served from cache.
- Spring Boot 4 moved MockMvc test auto-configuration to `spring-boot-starter-webmvc-test`
  (`org.springframework.boot.webmvc.test.autoconfigure`). The contract validator is now
  `com.atlassian.oai:openapi-request-validator-mockmvc` (renamed from `swagger-request-validator-mockmvc`).
