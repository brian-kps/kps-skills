---
name: clavro-setup
description: |
  Set up Clavro authentication SDK in Kotlin Multiplatform applications with Compose Multiplatform UI and Ktor server backend. Use when: (1) Integrating Clavro auth into a new KMP project, (2) Adding authentication to Compose Multiplatform apps, (3) Configuring Ktor resource server with JWT validation, (4) Setting up OAuth navigation flows, (5) User asks to "set up Clavro" or "add Clavro authentication".
user_invocable: true
---

# Clavro Setup for Kotlin Multiplatform

Integrate Clavro authentication SDK into KMP applications with Compose Multiplatform and Ktor.

## Setup Workflow

### 1. Gather Requirements

Before starting, determine:
- **Clavro instance URL** (e.g., `your-app.clavro.org`)
- **Redirect URI scheme** for OAuth (e.g., `myapp://`)
- **JWT audience** for server validation (e.g., `app.clavro.dev`)

### 2. Configure Gradle Dependencies

Add Clavro SDK dependencies to the project. See [gradle-config.md](references/gradle-config.md) for:
- Version catalog entries
- Maven repository setup
- Client and server dependencies

### 3. Set Up Client SDK

Configure `ClavroProvider` wrapper for Android and iOS. See [client-setup.md](references/client-setup.md) for:
- Android `MainActivity` setup
- iOS `MainViewController` setup
- URL resource configuration

### 4. Configure Navigation

Set up auth-aware navigation with proper loading states. See [navigation-setup.md](references/navigation-setup.md) for:
- Auth state handling (prevents sign-in screen flicker)
- Splash screen as `startDestination`
- `ClavroAuthNavigationHandler` configuration
- Alternative `AuthStateGate` approach

### 5. Configure Server (if applicable)

Set up Ktor resource server with JWT validation. See [server-setup.md](references/server-setup.md) for:
- `JwtValidator` configuration
- Ktor authentication plugin setup
- Protected route configuration

## Auth States Reference

| State | Description | Action |
|-------|-------------|--------|
| `Initializing` | Checking stored tokens at startup | Show splash, no navigation |
| `Refreshing` | Startup token refresh only | Show splash, no navigation |
| `Authenticated` | Valid session — has `userId` property | Navigate to authenticated route |
| `Unauthenticated` | No session | Navigate to sign-in |
| `Error` | Auth error | Navigate to sign-in |

**Key behaviors:**
- `Authenticated.userId` — extracted from JWT `sub` claim at construction time. No separate API call needed.
- `Authenticated.equals()` compares `userId` only — `MutableStateFlow` won't emit on token refresh (same user, new tokens), preventing unnecessary recomposition.
- `Refreshing` is only emitted during initial startup. During an active session, token refreshes happen silently while state stays `Authenticated`.

## BFF (Backend for Frontend) Pattern

For web dashboards served from the same origin (e.g., control plane at `/dashboard`), use the BFF pattern instead of exposing tokens to the browser.

See [bff-pattern.md](references/bff-pattern.md) for:
- Cookie-based auth with httpOnly cookies (no tokens in JS)
- BFF auth routes (`/api/control/bff/v1/auth/*`)
- Dual auth providers (Bearer + cookie) via `AuthenticationStrategy.FirstSuccessful`
- Same-origin SPA serving (Ktor `singlePageApplication`)
- React auth context with silent refresh
- Vite dev proxy configuration

### When to use BFF vs SDK

| Scenario | Approach |
|----------|----------|
| Native mobile app (Android/iOS) | Clavro SDK with `ClavroProvider` |
| Desktop app (KMP) | Clavro SDK with `ClavroProvider` |
| Web dashboard served from same server | BFF pattern with httpOnly cookies |
| Third-party web app (separate origin) | Clavro SDK (JS) or standard OAuth |

## Quick Reference

```kotlin
// Access userId directly from auth state (no API call)
val authState = rememberAuthState()
if (authState is AuthState.Authenticated) {
    val userId = authState.userId  // from JWT, no network call
}

// Access full user profile (fetches from API, cached)
val user = rememberUserProfile()

// Sign out (mobile/desktop)
scope.launch { ClavroSDK.auth.signOut() }
```

```typescript
// BFF auth (web dashboard)
const res = await fetch("/api/control/bff/v1/auth/session", {
  credentials: "include",  // sends httpOnly cookies
});
```

## Checklist

### Gradle
- [ ] Add `clavro` version to `libs.versions.toml`
- [ ] Add Clavro libraries to version catalog
- [ ] Configure Maven repository in `settings.gradle.kts`

### Client (Mobile/Desktop)
- [ ] Add `vault_key_host` to `strings.xml`
- [ ] Wrap app with `ClavroProvider` (Android + iOS)
- [ ] Create splash screen for loading state
- [ ] Configure `ClavroAuthNavigationHandler`

### Server (Resource Server)
- [ ] Add resource server dependency
- [ ] Configure `JwtValidator`
- [ ] Protect routes with `authenticate("clavro")`

### BFF (Web Dashboard)
- [ ] Create BFF auth routes (sign-in, sign-up, sign-out, session, refresh)
- [ ] Set httpOnly, Secure, SameSite=Lax cookies
- [ ] Register cookie-based auth provider (`control-plane-bff`)
- [ ] Update existing routes to accept both Bearer + cookie auth
- [ ] Add BFF paths to middleware skip lists (TenantResolution, KeyValidation)
- [ ] Configure SPA serving under `/dashboard` with redirect from bare path
- [ ] Set Vite `base` to match server mount point
- [ ] Bundle React build into server JAR via `processResources`
