# BFF (Backend for Frontend) Pattern

## Architecture

```
Browser → Ktor server (same origin)
  ├── /dashboard/*           → SPA (React) served from classpath
  ├── /api/control/bff/v1/*  → BFF auth routes (cookie-based)
  └── /api/control/v1/*      → Control plane API (Bearer OR cookie)
```

No CORS needed in production — everything is same-origin.

## Cookie-Based Auth Routes

Create BFF auth routes at `/api/control/bff/v1/auth/`:

```kotlin
route("/api/control/bff/v1") {
    route("/auth") {
        post("/sign-in")  { /* validate credentials, set cookies */ }
        post("/sign-up")  { /* create account, set cookies */ }
        post("/sign-out") { /* clear cookies */ }
        get("/session")   { /* return current user from cookie */ }
        post("/refresh")  { /* refresh token, update cookies */ }
    }
}
```

### Setting httpOnly Cookies

```kotlin
private fun ApplicationCall.setAuthCookies(accessToken: String, refreshToken: String) {
    response.cookies.append(
        Cookie(
            name = "clavro_cp_access",
            value = accessToken,
            httpOnly = true,
            secure = true,          // HTTPS only
            path = "/",
            extensions = mapOf("SameSite" to "Lax")
        )
    )
    response.cookies.append(
        Cookie(
            name = "clavro_cp_refresh",
            value = refreshToken,
            httpOnly = true,
            secure = true,
            path = "/api/control/bff/v1/auth/refresh",  // narrow path
            extensions = mapOf("SameSite" to "Lax")
        )
    )
}

private fun ApplicationCall.clearAuthCookies() {
    response.cookies.append(Cookie("clavro_cp_access", "", maxAge = 0, path = "/"))
    response.cookies.append(Cookie("clavro_cp_refresh", "", maxAge = 0,
        path = "/api/control/bff/v1/auth/refresh"))
}
```

## Dual Auth Provider (Bearer + Cookie)

Register a cookie-reading auth provider that synthesizes a Bearer header:

```kotlin
// In JwtAuth.kt
bearer("control-plane-bff") {
    authHeader { call ->
        val token = call.request.cookies["clavro_cp_access"]
        token?.let { HttpAuthHeader.Single("Bearer", it) }
    }
    authenticate { tokenCredential ->
        // Same JWT verification as the "jwt" provider
    }
}
```

Then update all control plane routes to accept either:

```kotlin
import io.ktor.server.auth.AuthenticationStrategy

authenticate("jwt", "control-plane-bff", strategy = AuthenticationStrategy.FirstSuccessful) {
    // routes accept Bearer token OR httpOnly cookie
}
```

## Middleware Skip Lists

When adding BFF routes, update ALL interceptors to skip them:

```kotlin
// In KeyValidation.kt, TenantResolution.kt, etc.
val path = call.request.path()
if (path.startsWith("/api/control/v1") ||
    path.startsWith("/api/control/bff/v1") ||
    path.startsWith("/dashboard") ||
    path.startsWith("/health") ||
    path == "/" ||
    path == "/favicon.ico") {
    proceed()
    return@intercept
}
```

Missing a skip causes `400 "Tenant context not resolved"` or similar on the new routes.

## React Auth Context

```typescript
// auth/api.ts - All BFF calls use credentials: "include"
export async function bffFetch(path: string, options: RequestInit = {}) {
  const res = await fetch(`/api/control/bff/v1${path}`, {
    ...options,
    credentials: "include",  // sends httpOnly cookies
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!res.ok) throw new BffApiError(res.status, await res.json());
  return res.json();
}

// auth/auth-context.tsx
// - Check session on mount: GET /auth/session
// - Silent refresh every 13 minutes: POST /auth/refresh
// - signIn/signUp/signOut actions
```

## SPA Serving from Ktor

See the `ktor-server-patterns` skill for:
- `singlePageApplication` configuration
- `/dashboard` → `/dashboard/` redirect (required)
- Build integration via `processResources`

## Vite Dev Configuration

```typescript
// vite.config.ts
export default defineConfig({
  base: "/dashboard/",  // must match Ktor mount point
  server: {
    proxy: {
      "/api/control/bff/v1": { target: "http://localhost:8080", changeOrigin: true },
      "/api/control/v1":     { target: "http://localhost:8080", changeOrigin: true },
    },
  },
})
```

- **Dev:** Vite proxy forwards API calls to Ktor — no CORS needed
- **Prod:** Same origin (Ktor serves both SPA and API) — no CORS needed
