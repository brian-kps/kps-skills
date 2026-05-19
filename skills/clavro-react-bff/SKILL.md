---
name: clavro-react-bff
description: |
  Set up a React SPA with Clavro BFF (Backend for Frontend) authentication for the data plane.
  Use when: (1) Building a React app that authenticates users via Clavro, (2) Setting up BFF cookie-based auth
  for a web app, (3) Configuring Vite proxy for local dev with Clavro, (4) Adding auth context, protected routes,
  or token refresh to a React app using Clavro, (5) User asks to "set up a React app with Clavro" or
  "add Clavro auth to my web app".
user_invocable: true
---

# Clavro React BFF Setup — Data Plane

Build a React SPA that authenticates end users via Clavro using the BFF (Backend for Frontend) pattern.
Tokens live in httpOnly cookies — JavaScript never touches JWTs.

## Quick Start with `@clavro/react`

The `@clavro/react` SDK package provides everything needed for BFF auth and data API access out of the box.

### Install

```bash
pnpm add @clavro/react
```

### Provider Setup

Use Vite environment variables to configure `baseUrl` per environment:

```tsx
// src/main.tsx
import { ClavroProvider } from "@clavro/react";

createRoot(document.getElementById("root")!).render(
  <ClavroProvider
    baseUrl={import.meta.env.VITE_CLAVRO_BASE_URL}
    onSessionExpired={() => {
      // Fires when a previously authenticated session is lost
      // (refresh failure, token expiry). Does NOT fire on initial
      // load or intentional signOut().
      toast.error("Session expired. Please sign in again.");
    }}
  >
    <App />
  </ClavroProvider>
);
```

```bash
# .env.development — empty = same-origin (Vite proxy handles routing)
VITE_CLAVRO_BASE_URL=

# .env.production — custom domain pointing to Clavro instance
VITE_CLAVRO_BASE_URL=https://clavro.example.com
```

Add the TypeScript declaration for the env var:

```ts
// src/vite-env.d.ts
/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly VITE_CLAVRO_BASE_URL: string
}
interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

### Authentication

```tsx
import { useAuth, ClavroApiError } from "@clavro/react";

function SignInPage() {
  const { signIn } = useAuth();

  async function handleSubmit(email: string, password: string) {
    try {
      await signIn({ email, password });
    } catch (err) {
      if (err instanceof ClavroApiError) {
        console.error(err.code, err.message); // e.g., "INVALID_CREDENTIALS"
      }
    }
  }
  // ...
}
```

### Route Protection & Conditional Rendering

```tsx
import { AuthGuard, SignedIn, SignedOut } from "@clavro/react";
import { useNavigate } from "react-router-dom";

// Route guard — redirects unauthenticated users
function ProtectedLayout() {
  const navigate = useNavigate();
  return (
    <AuthGuard onUnauthenticated={() => navigate("/sign-in")}>
      <Outlet />
    </AuthGuard>
  );
}

// Declarative — show different content based on auth state
// Both accept an optional `fallback` rendered during loading
function Header() {
  return (
    <>
      <SignedIn fallback={<Skeleton />}>
        <UserMenu />
      </SignedIn>
      <SignedOut>
        <SignInButton />
      </SignedOut>
    </>
  );
}
```

### Data API Access

```tsx
import { useClavro } from "@clavro/react";

function ProfilePage() {
  const { users, sessions, organizations } = useClavro();

  useEffect(() => {
    users.getMe().then(setProfile);
    sessions.list().then(setSessions);
  }, []);
  // ...
}
```

### Password Reset Flow

```tsx
const { forgotPassword, resetPassword } = useAuth();

// Step 1: Request reset email (always returns success to prevent user enumeration)
await forgotPassword("user@example.com");

// Step 2: User clicks email link, lands on reset page with token in URL
const token = new URLSearchParams(window.location.search).get("token");
await resetPassword(token, "newSecurePassword123");
```

### Email Verification

```tsx
const { sendVerificationEmail, verifyEmail } = useAuth();

// Resend verification email
await sendVerificationEmail("user@example.com");

// Verify with token from email link
const token = new URLSearchParams(window.location.search).get("token");
await verifyEmail(token);
```

### Account Unlock

```tsx
const { unlockAccount } = useAuth();

// Unlock with token from email link
const token = new URLSearchParams(window.location.search).get("token");
await unlockAccount("user@example.com", token);
```

### OAuth Consent Management

```tsx
import { useClavro } from "@clavro/react";

function ConnectedApps() {
  const { consents } = useClavro();

  useEffect(() => {
    consents.list().then(setApps);
  }, []);

  async function revokeAccess(clientId: string) {
    await consents.revoke(clientId);
  }
}
```

### Accessing User (Non-Null)

```tsx
import { useUser, SignedIn } from "@clavro/react";

// useUser() returns ClavroUser (never null) — throws if not signed in
function UserGreeting() {
  const user = useUser();
  return <p>Hello, {user.firstName ?? user.email}</p>;
}

// Safe usage — wrap in SignedIn or AuthGuard
<SignedIn>
  <UserGreeting />
</SignedIn>
```

### Social Sign-In

```tsx
const { signInWithProvider } = useAuth();

// Unified method — works with any configured provider
signInWithProvider("google");
signInWithProvider("apple", "/dashboard");
signInWithProvider("github");

// Convenience aliases also available:
// signInWithApple(), signInWithGoogle(), signInWithGithub()
```

Social sign-in uses the BFF social login endpoint (`/api/bff/v1/auth/social/{provider}`). The server handles the full OAuth flow — initiates the redirect to the provider, receives the callback, creates the session, sets httpOnly cookies, and redirects the user back to your app at the specified `redirectPath` (defaults to current page). No tokens or OAuth parameters are ever exposed to JavaScript.

## Prerequisites

Before starting, the developer needs:

1. **A Clavro instance** — created in the Clavro dashboard. Your instance URL is `{slug}.clavro.org` where `{slug}` is the slug assigned to your application instance (e.g., `acme.clavro.org`)
2. **BFF enabled** — toggle "Enable BFF Authentication" in instance settings
3. **A custom domain (production)** — e.g., `auth.example.com` pointing to your Clavro instance via CNAME

## Architecture Overview

```
Browser (React SPA)
  │
  ├── /api/bff/v1/auth/*     → Clavro BFF auth (cookie-based, hosted by Clavro)
  ├── /api/data/v1/*          → Clavro data API (user profile, sessions, orgs)
  └── /api/*                  → Your backend (validates JWT from cookie or Bearer header)
```

- **Auth cookies** (`vaultkey_access`, `vaultkey_refresh`) are httpOnly — invisible to JS
- **Same-origin required for cookies** — use Vite proxy (dev) or shared domain (prod)
- **Your backend reads the same cookie** — `vaultkey_access` contains the JWT; validate it identically to Bearer tokens

## Setup Steps

### Step 1: Create Your React App

See [react-app-setup.md](references/react-app-setup.md) for:
- Vite project scaffolding
- Required dependencies
- Vite proxy configuration for local development

### Step 2: Install `@clavro/react`

```bash
pnpm add @clavro/react
```

The SDK provides: `ClavroProvider`, `useAuth`, `AuthGuard`, `useClavro`, `ClavroApiError`, and all TypeScript types.

### Step 3: Wrap Your App with `ClavroProvider`

```tsx
<ClavroProvider
  baseUrl=""
  onSessionExpired={() => {
    // Optional — fires when an active session is lost (not on initial load or sign-out)
    toast.error("Session expired");
    navigate("/sign-in");
  }}
>
  <App />
</ClavroProvider>
```

The provider handles session restore on mount, silent token refresh every 13 minutes, and automatic 401 retry with refresh for all data API calls.

### Step 4: Add Route Protection with `AuthGuard`

The SDK's `AuthGuard` does NOT depend on react-router-dom. It uses an `onUnauthenticated` callback:

```tsx
<AuthGuard onUnauthenticated={() => navigate("/sign-in")}>
  <ProtectedContent />
</AuthGuard>
```

See [protected-routes.md](references/protected-routes.md) for full router setup patterns.

### Step 5: Call Clavro Data APIs with `useClavro()`

```tsx
const { users, sessions, organizations, consents, environment } = useClavro();
```

See [data-api-client.md](references/data-api-client.md) for all available endpoints and response types.

### Step 6: Connect Your Backend

Your backend can read the JWT from the `vaultkey_access` cookie — same token it would get from a `Bearer` header. Add cookie-based auth as a fallback:

```kotlin
// Ktor: extract token from Bearer header OR vaultkey_access cookie
val token = extractBearerToken(call) ?: call.request.cookies["vaultkey_access"]
```

The web app makes API calls with `credentials: "include"` so cookies are sent automatically:

```ts
const res = await fetch("/api/users/me", { credentials: "include" })
```

The Vite proxy routes `/api/bff/v1` and `/api/data/v1` to Clavro, and all other `/api/*` to your backend server. In production, the cookie domain (e.g., `.example.com`) covers both `clavro.example.com` and `example.com`.

See [backend-integration.md](references/backend-integration.md) for full patterns (Node.js, Ktor, Go).

## SDK Exports

| Export | Type | Description |
|--------|------|-------------|
| `ClavroProvider` | Component | Auth context provider with session management. Props: `baseUrl`, `refreshInterval`, `onSessionExpired` |
| `useAuth()` | Hook | `{ user, session, isLoading, signIn, signUp, signOut, forgotPassword, resetPassword, sendVerificationEmail, verifyEmail, unlockAccount, signInWithProvider }` |
| `useUser()` | Hook | Returns non-null `ClavroUser`. Throws if not signed in — use inside `<SignedIn>` or `<AuthGuard>` |
| `SignedIn` | Component | Renders children when authenticated. Accepts optional `fallback` for loading state |
| `SignedOut` | Component | Renders children when NOT authenticated. Accepts optional `fallback` for loading state |
| `AuthGuard` | Component | Route guard with loading fallback and redirect callback |
| `useClavro()` | Hook | Data API client with automatic 401 retry `{ users, sessions, organizations, consents, environment }` |
| `ClavroApiError` | Class | Typed errors with `status`, `code`, `message` |
| `createAuthApi()` | Factory | Standalone BFF auth client (for non-React use). Exposes `fetchWithRetry` |
| `createDataApi()` | Factory | Standalone data API client. Accepts optional `authedFetch` for 401 retry |
| `FetchWithRetry` | Type | Fetch wrapper type `<T>(input, init?) => Promise<T>` for 401 retry |

## BFF API Reference

| Method | Endpoint | Auth | Response |
|--------|----------|------|----------|
| `POST` | `/api/bff/v1/auth/sign-in` | Public | Sets cookies, returns `{ session, user }` |
| `POST` | `/api/bff/v1/auth/sign-up` | Public | Sets cookies, returns `{ session, user, message }` |
| `POST` | `/api/bff/v1/auth/refresh` | Cookie | Rotates cookies, returns `{ session }` |
| `POST` | `/api/bff/v1/auth/sign-out` | Cookie | Clears cookies, returns 204 |
| `GET`  | `/api/bff/v1/auth/session` | Cookie | Returns `{ authenticated, session?, user? }` |
| `GET`  | `/api/bff/v1/auth/social/{provider}` | Public | Initiates OAuth flow, redirects to provider. Query: `redirect_path` |

## Auth API Reference (Public)

| Method | Endpoint | SDK Method | Description |
|--------|----------|------------|-------------|
| `POST` | `/api/data/v1/auth/forgot-password` | `forgotPassword(email)` | Sends password reset email (always returns success) |
| `POST` | `/api/data/v1/auth/reset-password` | `resetPassword(token, newPassword)` | Resets password with token from email |
| `POST` | `/api/data/v1/auth/send-verification` | `sendVerificationEmail(email)` | Resends email verification link |
| `POST` | `/api/data/v1/auth/verify-email` | `verifyEmail(token)` | Verifies email with token from link |
| `POST` | `/api/data/v1/auth/unlock-account` | `unlockAccount(email, token)` | Unlocks account with token from email |
| `GET`  | `/api/bff/v1/auth/social/{provider}` | `signInWithProvider(provider)` | Initiates BFF social OAuth flow (server-side redirect) |

## Data API Reference (Authenticated)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`    | `/api/data/v1/users/me` | Current user profile |
| `PATCH`  | `/api/data/v1/users/me` | Update profile |
| `DELETE` | `/api/data/v1/users/me` | Delete account |
| `POST`   | `/api/data/v1/users/me/change-email` | Change email |
| `POST`   | `/api/data/v1/users/me/change-password` | Change password |
| `GET`    | `/api/data/v1/sessions` | List active sessions |
| `DELETE` | `/api/data/v1/sessions/{id}` | Revoke a session |
| `GET`    | `/api/data/v1/organizations` | List organizations |
| `POST`   | `/api/data/v1/organizations` | Create organization |
| `GET`    | `/api/data/v1/oauth/consents` | List OAuth consents (connected apps) |
| `DELETE` | `/api/data/v1/oauth/consents/{clientId}` | Revoke OAuth consent |
| `GET`    | `/api/data/v1/environment` | SDK/config discovery |

All data API routes accept **either** `Authorization: Bearer <token>` **or** the `vaultkey_access` httpOnly cookie (via `AuthenticationStrategy.FirstSuccessful`).

## Key Design Decisions

1. **No JWT in JavaScript** — tokens live only in httpOnly cookies, immune to XSS
2. **Three-layer token refresh** — (a) proactive 13-min interval, (b) reactive 401 retry with single-promise dedup via `fetchWithRetry`, (c) `visibilitychange` handler for background tabs
3. **`onSessionExpired` callback** — fires only on authenticated→unauthenticated transition, not on initial load or intentional sign-out
4. **`isLoading` guard** — prevents redirect flicker on app mount during session check. `SignedIn`/`SignedOut` accept `fallback` for loading UI
5. **Tenant resolution via Host header** — Clavro determines the instance from the request hostname
6. **Same-origin preferred** — use custom domains so SPA and API share origin (no CORS)
7. **No react-router-dom dependency** — `AuthGuard` uses `onUnauthenticated` callback, works with any router
8. **BFF social login** — social sign-in uses a dedicated BFF endpoint (`/api/bff/v1/auth/social/{provider}`) that handles the full OAuth flow server-side and sets cookies on callback. Does NOT use the OAuth 2.1 authorize endpoint (which requires PKCE params for third-party clients)

## Third-Party Cookie Gotcha (CRITICAL)

**Problem**: When `baseUrl` points to a different origin (e.g., `localhost:5173` → `dev-slug.clavro.org`), sign-in **appears to work** because the SDK sets auth state from the JSON response body. But the `Set-Cookie` header is **silently blocked** by the browser as a third-party cookie. On page refresh, `getSession()` sends no cookie and the user is logged out.

**Symptoms**:
- Sign-in succeeds, user sees authenticated content
- Page refresh immediately redirects to sign-in
- No errors in the console (cookie blocking is silent)
- `Application > Cookies` in DevTools shows no `vaultkey_access` cookie

**Root cause**: Browsers block `Set-Cookie` from a different registrable domain (third-party). `localhost` and `clavro.org` are different sites. CORS headers don't help — this is a cookie storage policy, not a CORS issue.

**Fix**: Use a Vite proxy with `cookieDomainRewrite` so all requests are same-origin AND cookies are accepted. Set `baseUrl=""` in development:

```ts
// vite.config.ts
server: {
  proxy: {
    "/api/bff/v1": {
      target: "https://dev-slug.clavro.org",
      changeOrigin: true,
      secure: true,
      cookieDomainRewrite: "",  // Strips Domain attr from Set-Cookie → browser scopes to localhost
    },
    "/api/data/v1": {
      target: "https://dev-slug.clavro.org",
      changeOrigin: true,
      secure: true,
      cookieDomainRewrite: "",
    },
    "/api": { target: "http://localhost:8080", changeOrigin: true }, // your backend
  }
}
```

```bash
# .env.development
VITE_CLAVRO_BASE_URL=
```

All requests now go to `localhost:5173/api/...` → Vite proxies to the correct server. Same-origin, no CORS, no third-party cookie issues.

**Why `cookieDomainRewrite` is required**: The Vite proxy makes requests same-origin from the browser's perspective, but `changeOrigin: true` sends `Host: dev-slug.clavro.org` to the upstream. The Clavro server sees that hostname and sets `Domain=.clavro.org` (or a custom domain) on the cookie. The browser then rejects that cookie because `localhost` doesn't match. `cookieDomainRewrite: ""` strips the `Domain` attribute, so the browser scopes the cookie to `localhost` — which is what we want.

**webpack-dev-server equivalent**:
```js
// webpack.config.js
devServer: {
  proxy: [{
    context: ["/api/bff/v1", "/api/data/v1"],
    target: "https://dev-slug.clavro.org",
    changeOrigin: true,
    secure: true,
    cookieDomainRewrite: "",
  }]
}
```

## Domain Configuration

All customer instances use `{slug}.clavro.org` — there is no separate dev domain.

| Scenario | baseUrl | Cookie | CORS |
|----------|---------|--------|------|
| **Local dev**: `localhost:5173` → Vite proxy | `""` (empty) | First-party (localhost) via `cookieDomainRewrite: ""` | Vite proxy handles it |
| **Production**: shared domain via CNAME (`clavro.example.com`) | `"https://clavro.example.com"` | `.example.com` (first-party) | Not needed (same registrable domain) |
| **Production**: cross-origin (`{slug}.clavro.org`) | `"https://{slug}.clavro.org"` | Third-party — **will NOT work in most browsers** | CORS required but cookies still blocked |

**NEVER use a cross-origin `baseUrl` for production.** Always use a custom CNAME domain on the same registrable domain as your SPA so cookies are first-party.

## Error Codes

| Code | Meaning |
|------|---------|
| `BFF_NOT_ENABLED` | BFF auth not enabled for this instance |
| `INVALID_CREDENTIALS` | Wrong email or password |
| `ACCOUNT_LOCKED` | Account is locked |
| `ACCOUNT_BANNED` | Account is banned |
| `REFRESH_TOKEN_MISSING` | No refresh cookie found |
| `PASSWORD_AUTH_DISABLED` | Password auth disabled for this instance |
| `INVALID_TOKEN` | Invalid or expired reset/verification token |
| `WEAK_PASSWORD` | New password doesn't meet requirements |
| `RATE_LIMIT_EXCEEDED` | Too many requests (e.g., forgot-password) |
| `INVALID_REQUEST` | Malformed request body |

## Checklist

- [ ] Clavro instance created and BFF enabled in dashboard
- [ ] React app created with Vite
- [ ] `pnpm add @clavro/react`
- [ ] `.env.development` with `VITE_CLAVRO_BASE_URL=` (empty = same-origin)
- [ ] `.env.production` with `VITE_CLAVRO_BASE_URL=https://clavro.example.com`
- [ ] `vite-env.d.ts` with `ImportMetaEnv` type declaration
- [ ] Vite proxy: `/api/bff/v1` and `/api/data/v1` → Clavro (with `cookieDomainRewrite: ""`), `/api` → your backend
- [ ] `<ClavroProvider baseUrl={import.meta.env.VITE_CLAVRO_BASE_URL}>` wrapping app root
- [ ] `<AuthGuard>` protecting authenticated routes
- [ ] Sign-in and sign-up pages wired to `useAuth()`
- [ ] Data API calls via `useClavro()` for user/session/org operations
- [ ] Backend reads `vaultkey_access` cookie as Bearer token fallback
- [ ] Custom CNAME domain configured for production (same registrable domain as SPA)
