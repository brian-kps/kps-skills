---
name: gradle-kmp-build
description: |
  Gradle build patterns for Kotlin Multiplatform projects including bundling frontend apps,
  environment variable handling, Exec task pitfalls, and CI/CD integration. Use when:
  (1) Integrating React/Vite builds into Gradle, (2) Debugging Gradle Exec tasks (pnpm/npm not found),
  (3) Loading .env files for local development, (4) Configuring processResources for generated assets,
  (5) Setting up build chains with proper task dependencies.
---

# Gradle KMP Build Patterns

## Bundling a Frontend App into a Server JAR

### Architecture

```
React app (Vite) → dist/ → processResources → classpath → Ktor serves SPA
```

**Never copy generated assets into source directories** (`src/main/resources/`). Instead, inject them into the build output via `processResources`:

```kotlin
val controlPlaneSpaDir = rootProject.file("control-plane-web-app")
val controlPlaneSpaOutput = controlPlaneSpaDir.resolve("dist")

val buildControlPlaneSpa by tasks.registering(Exec::class) {
    group = "build"
    workingDir = controlPlaneSpaDir
    commandLine(pnpmPath, "run", "build")
    inputs.dir(controlPlaneSpaDir.resolve("src"))
    inputs.file(controlPlaneSpaDir.resolve("package.json"))
    inputs.file(controlPlaneSpaDir.resolve("vite.config.ts"))
    inputs.file(controlPlaneSpaDir.resolve("index.html"))
    outputs.dir(controlPlaneSpaOutput)
}

tasks.named<ProcessResources>("processResources") {
    dependsOn(buildControlPlaneSpa)
    from(controlPlaneSpaOutput) {
        into("control-plane-spa")  // classpath folder name
    }
}
```

### Build chain with TypeScript generation

```
:control-plane-types:compileKotlinJs
  → :control-plane-types:copyTypeScriptDefinitions  (copies .d.ts to React src/generated/)
    → :server:buildControlPlaneSpa                    (pnpm build)
      → :server:processResources                      (copies dist/ into build output)
        → :server:jar / :server:shadowJar
```

Wire with `dependsOn`:
```kotlin
val buildControlPlaneSpa by tasks.registering(Exec::class) {
    dependsOn(":control-plane-types:copyTypeScriptDefinitions")
    // ...
}
```

## Exec Tasks: pnpm/npm Not Found

Gradle `Exec` tasks fork a new process **without your shell's PATH**. The error:
```
A problem occurred starting process 'command 'pnpm''
```

**Fix:** Resolve the full path:
```kotlin
val pnpmPath = listOf(
    System.getenv("PNPM_HOME")?.let { "$it/pnpm" },
    "/usr/local/bin/pnpm",
    "${System.getProperty("user.home")}/Library/pnpm/pnpm",
    "${System.getProperty("user.home")}/.local/share/pnpm/pnpm",
).firstOrNull { it != null && file(it).exists() } ?: "pnpm"
commandLine(pnpmPath, "run", "build")
```

For CI, install pnpm via `pnpm/action-setup@v4` and `actions/setup-node@v4` before Gradle runs.

## Loading .env Files

Gradle does not read `.env` files. Parse and forward manually:

```kotlin
val dotEnvFile = rootProject.file(".env")
if (dotEnvFile.exists()) {
    val envVars = dotEnvFile.readLines()
        .filter { it.isNotBlank() && !it.startsWith("#") }
        .associate {
            val (key, value) = it.split("=", limit = 2)
            key.trim() to value.trim()
        }

    tasks.withType<JavaExec>().configureEach {
        envVars.forEach { (key, value) ->
            environment(key, value)
        }
    }
}
```

### .env file format (no `export` needed)

```
DATABASE_URL=jdbc:postgresql://localhost:5432/mydb
DATABASE_USER=myuser
DATABASE_PASSWORD=secret
```

## Vite Configuration for Ktor SPA Serving

### `base` must match the server mount point

```typescript
// vite.config.ts
export default defineConfig({
  base: "/dashboard/",  // matches Ktor route("/dashboard")
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api/control/bff/v1": { target: "http://localhost:8080", changeOrigin: true },
      "/api/control/v1":     { target: "http://localhost:8080", changeOrigin: true },
    },
  },
})
```

- **Dev:** Vite proxy forwards API calls to Ktor — no CORS needed.
- **Prod:** Same origin (Ktor serves both SPA and API) — no CORS needed.

## TypeScript 5.9+ `erasableSyntaxOnly`

Parameter properties (`public` in constructor) are not allowed:

```typescript
// BAD
class MyError extends Error {
  constructor(public status: number) { super(); }
}

// GOOD
class MyError extends Error {
  status: number;
  constructor(status: number) { super(); this.status = status; }
}
```

## CI/CD: Adding Node/pnpm to GitHub Actions

If the workflow builds the server JAR (which triggers the React build), add before Gradle:

```yaml
- uses: pnpm/action-setup@v4
  with:
    version: 9

- uses: actions/setup-node@v4
  with:
    node-version: "22"
    cache: "pnpm"
    cache-dependency-path: control-plane-web-app/pnpm-lock.yaml

- name: Install React app dependencies
  run: pnpm install --frozen-lockfile
  working-directory: control-plane-web-app
```

## Gitignore Rules for Generated Artifacts

```gitignore
# In control-plane-web-app/.gitignore
src/generated/*.d.ts    # TypeScript definitions from Kotlin/JS

# In root .gitignore (if applicable)
server/src/main/resources/control-plane-spa/  # should never exist — assets go in build output
```
