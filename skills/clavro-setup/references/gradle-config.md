# Gradle Configuration

## Version Catalog (`gradle/libs.versions.toml`)

### Versions Section

```toml
[versions]
clavro = "development-SNAPSHOT"
```

### Libraries Section

```toml
[libraries]
clavro-client-compose-navigation = { module = "org.clavro:sdk-client-compose-navigation", version.ref = "clavro" }
clavro-resource-server-ktor = { module = "org.clavro:sdk-resource-server-ktor", version.ref = "clavro" }
```

## Maven Repository (`settings.gradle.kts`)

Add to `dependencyResolutionManagement.repositories`:

```kotlin
mavenLocal()
maven {
    url = uri("https://maven.pkg.github.com/bkenn/Clavro")
    credentials {
        username = "bkenn"
        password = System.getenv("GITHUB_TOKEN")
    }
}
```

**Note:** Ensure `GITHUB_TOKEN` environment variable is set with appropriate access.

## Compose App Dependencies (`composeApp/build.gradle.kts`)

### Plugins

```kotlin
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidApplication)
    alias(libs.plugins.composeMultiplatform)
    alias(libs.plugins.composeCompiler)
    alias(libs.plugins.kotlinxSerialization)
}
```

### Dependencies

In `commonMain.dependencies`:

```kotlin
implementation(libs.clavro.client.compose.navigation)
```

## Server Dependencies (`server/build.gradle.kts`)

### Plugins

```kotlin
plugins {
    alias(libs.plugins.kotlinJvm)
    alias(libs.plugins.ktor)
    application
    alias(libs.plugins.kotlinxSerialization)
}
```

### Dependencies

```kotlin
dependencies {
    implementation(libs.clavro.resource.server.ktor)
    implementation(libs.ktor.serverContentNegotiation)
}
```
