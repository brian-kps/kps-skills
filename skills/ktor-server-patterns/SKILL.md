---
name: ktor-server-patterns
description: |
  Best practices and gotchas for Ktor server development including routing, middleware interceptors,
  authentication providers, SPA serving, and CORS. Use when: (1) Adding new routes or middleware to Ktor,
  (2) Configuring authentication (JWT, cookies, multi-provider), (3) Serving SPAs from Ktor,
  (4) Debugging request pipeline issues (403/404/400 from interceptors), (5) Setting up CORS.
---

# Ktor Server Patterns

## Routing

### `route("/path")` does NOT match `/path` (no trailing slash)

Ktor's `route("/dashboard")` matches `/dashboard/` and `/dashboard/anything`, but **not** bare `/dashboard`.

**Fix:** Add an explicit redirect:
```kotlin
get("/dashboard") {
    call.respondRedirect("/dashboard/")
}
route("/dashboard") {
    singlePageApplication { ... }
}
```

### SPA serving with `singlePageApplication`

```kotlin
route("/dashboard") {
    singlePageApplication {
        useResources = true
        filesPath = "control-plane-spa"   // classpath folder
        defaultPage = "index.html"        // fallback for client-side routing
    }
}
```
- Place SPA routes **last** in the routing block to avoid catching API routes.
- The Vite `base` config must match the mount path (e.g., `base: "/dashboard/"`).

## Middleware Interceptors

### Every interceptor needs an updated skip list

When adding new route prefixes (e.g., `/api/control/bff/v1/`, `/dashboard`), **audit ALL interceptors** — not just the obvious ones. Common interceptors that need updating:
- `TenantResolution`
- `KeyValidation`
- `SessionActivityTracking`
- `RouteAccessLogging`

Symptoms of a missing skip: unexpected 400/403/404 with `"Tenant context not resolved"` or similar.

### Interceptor ordering in `Application.module()`

```
CORS → ExceptionHandling → TenantResolution → KeyValidation → JwtAuth → SessionTracking → Logging → Routing
```

CORS must be first (preflight). Exception handling wraps everything. Tenant resolution and key validation happen before auth.

## Authentication

### Multi-provider with FirstSuccessful

Use when the same routes need to accept both Bearer tokens (SDK/desktop) and cookies (web dashboard):

```kotlin
// In JwtAuth.kt — register providers
bearer("jwt") { ... }
bearer("control-plane-bff") {
    authHeader { call ->
        val token = call.request.cookies["clavro_cp_access"]
        token?.let { HttpAuthHeader.Single("Bearer", it) }
    }
    authenticate { tokenCredential -> ... }
}

// In route files — accept either
authenticate("jwt", "control-plane-bff", strategy = AuthenticationStrategy.FirstSuccessful) {
    // routes here
}
```

**Import:** `import io.ktor.server.auth.AuthenticationStrategy`

### Cookie-based auth provider

Read a cookie and synthesize a Bearer header so the standard `authenticate { }` block works unchanged:

```kotlin
bearer("my-cookie-auth") {
    authHeader { call ->
        val token = call.request.cookies["my_access_cookie"]
        token?.let { HttpAuthHeader.Single("Bearer", it) }
    }
    authenticate { tokenCredential ->
        // Same verification logic as Bearer token
    }
}
```

## CORS

In production with BFF pattern (SPA served from same origin), CORS is **not needed**. Only configure for development:

```kotlin
fun Application.configureCors() {
    val allowedOrigins = System.getenv("CORS_ALLOWED_ORIGINS")
        ?.split(",")?.map { it.trim() }?.filter { it.isNotEmpty() }
        ?: return  // No-op if env var not set

    install(CORS) {
        for (origin in allowedOrigins) {
            allowHost(origin.removePrefix("https://").removePrefix("http://"),
                schemes = if (origin.startsWith("https://")) listOf("https") else listOf("http"))
        }
        allowCredentials = true
        allowHeader(HttpHeaders.ContentType)
        allowHeader(HttpHeaders.Authorization)
        // ... methods
    }
}
```

## Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| 400 "Tenant context not resolved" on new routes | Middleware interceptor missing skip for new path prefix | Add path to skip list in ALL interceptors |
| 404 on `/path` but 200 on `/path/` | `route("/path")` doesn't match without trailing slash | Add `get("/path")` redirect |
| Smart cast error across modules | `if (obj.field != null) { use(obj.field) }` fails when `field` is in different module | Extract to local val: `val f = obj.field; if (f != null) { use(f) }` |
| `Principal` deprecation warning | Ktor deprecated the `Principal` interface | Can be safely ignored; will be removed in future Ktor versions |
