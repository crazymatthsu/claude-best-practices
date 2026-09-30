import org.gradle.api.tasks.testing.logging.TestExceptionFormat
import org.gradle.api.tasks.testing.logging.TestLogEvent

plugins {
    java
    jacoco
    id("org.springframework.boot") version "4.1.1"
    id("io.spring.dependency-management") version "1.1.7"
}

group = "com.example"
version = "0.1.0-SNAPSHOT"
description = "Demo service showing how to guardrail Claude Code on a Java project"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(25)
    }
}

repositories {
    mavenCentral()
}

// Coverage gate enforced by `./gradlew check` (see docs/08-testing-strategy.md)
val coverageLineMinimum = "0.80".toBigDecimal()
val coverageBranchMinimum = "0.70".toBigDecimal()

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-webmvc")
    implementation("org.springframework.boot:spring-boot-starter-validation")
}

testing {
    suites {
        // Unit tests: src/test, *Test.java, fast, no Spring context
        named<JvmTestSuite>("test") {
            useJUnitJupiter()
            dependencies {
                implementation("org.springframework.boot:spring-boot-starter-test")
                // Architecture rules as tests: layering can't silently erode
                implementation("com.tngtech.archunit:archunit-junit5:1.5.1")
            }
        }

        // Integration + contract tests: src/integrationTest, *IT.java, full Spring context
        register<JvmTestSuite>("integrationTest") {
            useJUnitJupiter()
            dependencies {
                implementation(project())
                implementation("org.springframework.boot:spring-boot-starter-webmvc-test")
                // Validates real HTTP responses against contracts/openapi/orders-api.v1.yaml
                implementation("com.atlassian.oai:openapi-request-validator-mockmvc:3.0.0")
            }
            targets.all {
                testTask.configure {
                    shouldRunAfter(tasks.test)
                    // The contract path in the tests is relative to the project root
                    workingDir = rootDir
                    // Without this, a contract-only change would be served from the build cache
                    inputs.dir("contracts").withPathSensitivity(PathSensitivity.RELATIVE)
                }
            }
        }
    }
}

// Failing tests print their name and assertion message, not a full stack trace:
// short, actionable output for humans and for Claude (see scripts/verify.sh).
tasks.withType<Test>().configureEach {
    testLogging {
        events(TestLogEvent.FAILED)
        exceptionFormat = TestExceptionFormat.FULL
        showStackTraces = false
        showCauses = false
    }
}

tasks.check {
    dependsOn(testing.suites.named("integrationTest"))
    dependsOn(tasks.jacocoTestCoverageVerification)
}

jacoco {
    toolVersion = "0.8.15"
}

// Coverage is measured over unit + integration tests combined
val coverageData = files(
    layout.buildDirectory.file("jacoco/test.exec"),
    layout.buildDirectory.file("jacoco/integrationTest.exec"),
)

tasks.jacocoTestReport {
    dependsOn(tasks.test, tasks.named("integrationTest"))
    executionData.setFrom(coverageData)
}

tasks.jacocoTestCoverageVerification {
    dependsOn(tasks.test, tasks.named("integrationTest"))
    executionData.setFrom(coverageData)
    classDirectories.setFrom(sourceSets.main.get().output.asFileTree.matching {
        exclude("com/example/orders/OrdersApplication.class")
    })
    violationRules {
        rule {
            limit {
                counter = "LINE"
                minimum = coverageLineMinimum
            }
            limit {
                counter = "BRANCH"
                minimum = coverageBranchMinimum
            }
        }
    }
    finalizedBy(tasks.jacocoTestReport)
}
