---
paths:
  - "src/test/**"
  - "src/integrationTest/**"
---
# Test rules

- `src/test/java/**/*Test.java`: unit tests. No Spring context, run by `./gradlew test`, must stay under 100 ms each.
- `src/integrationTest/java/**/*IT.java`: integration tests (Gradle `integrationTest` suite). `@SpringBootTest` +
  MockMvc, run by `./gradlew integrationTest` (part of `check`). Every HTTP response assertion also asserts
  `matchesContract()` against the OpenAPI file.
- Name tests `method_condition_expectation` or, for spec criteria, `acN_description` so they map 1:1 to
  acceptance criteria in `docs/specs/`.
- Structure each test as arrange / act / assert, separated by blank lines. One behaviour per test.
- Prefer hand-written fakes (see `OrderServiceTest.FakeOrderRepository`) over Mockito for ports.
  Use Mockito only for things you can't fake cheaply.
- Use AssertJ (`assertThat`), not JUnit `assertEquals`.
- Use a fixed `Clock`. Tests must not depend on wall time, ordering, or network.
- Never delete, `@Disabled`, or weaken an existing assertion to make a build pass. If a test is wrong,
  say why in the PR.
- Coverage gate: 80% line / 70% branch (unit + integration combined), enforced by JaCoCo in `./gradlew check`.
- Test dependencies go in the suite's `dependencies {}` block in `build.gradle.kts`. Ask before adding any.
