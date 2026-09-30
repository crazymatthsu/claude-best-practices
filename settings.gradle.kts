plugins {
    // Downloads a matching JDK when the toolchain in build.gradle.kts isn't installed locally.
    id("org.gradle.toolchains.foojay-resolver-convention") version "1.0.0"
}

rootProject.name = "orders-service"
