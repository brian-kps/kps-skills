---
name: kotlin-js-typescript
description: |
  Kotlin/JS and TypeScript definition generation from Kotlin Multiplatform. Use when:
  (1) Adding a JS target to a KMP module, (2) Exporting Kotlin types to TypeScript with @JsExport,
  (3) Debugging Kotlin/JS compilation errors, (4) Sharing types between Kotlin backend and React/TypeScript frontend,
  (5) Setting up generateTypeScriptDefinitions().
---

# Kotlin/JS TypeScript Generation

## Setup

### Adding JS target to a KMP module

```kotlin
kotlin {
    jvm()
    js {
        browser()
        binaries.library()
        generateTypeScriptDefinitions()
    }
}
```

### Output location

TypeScript `.d.ts` files are generated at:
```
build/compileSync/js/main/productionLibrary/kotlin/<module-name>.d.ts
```

Trigger with: `./gradlew :module:jsProductionLibraryCompileSync`

## @JsExport Limitations

### Unsupported types

| Kotlin Type | Problem | Workaround |
|-------------|---------|------------|
| `Long` | Not representable in JS | Use `Double` or `Int` |
| `Instant` / `Duration` | Not exportable | Use `String` (ISO format) |
| `UInt`, `ULong` | Unsigned not supported | Use signed equivalents |
| `internal` visibility | Not exported | Use `public` |
| Inline classes | Not supported | Use regular classes |

### Example: JS-safe model

```kotlin
@JsExport
@Serializable
data class BffUser(
    val id: String,
    val email: String,
    val fullName: String? = null,
    val createdAt: String,      // String, not Instant
    val updatedAt: String
)

@JsExport
@Serializable
data class BffSessionInfo(
    val userId: String,
    val expiresAt: Double,      // Double, not Long
    val role: String? = null
)
```

## Transitive Dependency Problem

**If module A has `js()` target and depends on module B, then B must also have a `js()` target.**

If B cannot support JS (e.g., depends on a JVM-only library like `ulid-kotlin`), you have two options:

### Option 1: Separate module for JS-exportable types (recommended)

Create a standalone module with no problematic dependencies:
```
control-plane-types/
  src/commonMain/kotlin/.../BffTypes.kt   # @JsExport types
  build.gradle.kts                         # js() + jvm() only
```

The server uses its own copies of the types (same JSON shape), and the standalone module generates `.d.ts`.

### Option 2: Platform-scoped dependencies

Move problematic dependencies out of `commonMain` into platform-specific source sets:
```kotlin
sourceSets {
    commonMain.dependencies {
        implementation(libs.kotlinx.serializationJson)  // JS-safe
    }
    jvmMain.dependencies {
        implementation(projects.coreIdentity)  // JVM-only dep
    }
}
```

**Caveat:** Any `commonMain` code that imports from the JVM-only dep will fail JS compilation.

## Copying Definitions to React App

```kotlin
val copyTypeScriptDefinitions by tasks.registering(Copy::class) {
    dependsOn("jsProductionLibraryCompileSync")
    from(layout.buildDirectory.dir("compileSync/js/main/productionLibrary/kotlin")) {
        include("*.d.ts")
    }
    into(rootProject.file("control-plane-web-app/src/generated"))
}
```

- The `src/generated/` directory should be **gitignored** (generated artifact).
- Wire this into the build chain so it runs before the React build.

## Generated TypeScript Shape

Kotlin nullable types become `Nullable<T>` (which is `T | null | undefined`). Example output:

```typescript
type Nullable<T> = T | null | undefined
export declare namespace org.clavro.controlplane.types {
    class BffUser {
        constructor(id: string, email: string, fullName: Nullable<string> | undefined, ...);
        get id(): string;
        get email(): string;
        get fullName(): Nullable<string>;
        // ...
    }
}
```
