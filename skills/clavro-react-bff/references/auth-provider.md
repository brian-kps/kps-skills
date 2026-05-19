# Step 3: Auth Provider

The `@clavro/react` SDK provides `ClavroProvider` — a React context provider that manages auth state, session restore on mount, and silent token refresh.

## Setup

```tsx
// src/main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ClavroProvider } from "@clavro/react";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ClavroProvider>
      <App />
    </ClavroProvider>
  </StrictMode>
);
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `baseUrl` | `string` | `""` | API base URL. Empty = same-origin (works with Vite proxy). Set to `https://{slug}.clavro.org` for cross-origin. |
| `refreshInterval` | `number` | `780000` (13 min) | Silent refresh interval in ms. Access tokens expire at 15 min. |
| `children` | `ReactNode` | — | App content |

### Cross-Origin Example

```tsx
<ClavroProvider baseUrl="https://acme.clavro.org">
  <App />
</ClavroProvider>
```

## The `useAuth()` Hook

```tsx
import { useAuth } from "@clavro/react";

function MyComponent() {
  const { user, session, isLoading, signIn, signUp, signOut } = useAuth();

  if (isLoading) return <p>Loading...</p>;
  if (!user) return <p>Not signed in</p>;

  return <p>Hello, {user.fullName ?? user.email}</p>;
}
```

### Return Value

| Field | Type | Description |
|-------|------|-------------|
| `user` | `ClavroUser \| null` | Current user profile |
| `session` | `ClavroSessionInfo \| null` | Current session metadata |
| `isLoading` | `boolean` | `true` until initial session check completes |
| `signIn` | `(data: SignInRequest) => Promise<void>` | Sign in with email/password |
| `signUp` | `(data: SignUpRequest) => Promise<void>` | Create account and sign in |
| `signOut` | `() => Promise<void>` | Sign out and clear state |

## How It Works

### 1. Session Restore (on mount)

When the app loads, `ClavroProvider` calls `GET /api/bff/v1/auth/session`. The browser sends the `vaultkey_access` httpOnly cookie automatically. If the cookie is valid, the server returns user info and `authenticated: true`.

```
App loads → ClavroProvider mounts → GET /session
  ├── Cookie valid     → user state populated, isLoading = false
  └── Cookie missing   → user = null, isLoading = false
      or expired           └── AuthGuard fires onUnauthenticated
```

### 2. Silent Refresh (proactive)

A `setInterval` runs every 13 minutes while the user is logged in. The access token expires at 15 minutes, so this gives a 2-minute buffer. The browser sends the `vaultkey_refresh` cookie, and the server rotates both cookies.

If the refresh fails (e.g., refresh token expired after 7 days of inactivity), the user is automatically signed out.

### 3. Context Optimization

The provider follows React's recommended context optimization patterns:
- **`useMemo` on context value** — prevents unnecessary re-renders of consumers
- **`useCallback` on all action functions** — stable references across renders
- **Separate `BaseUrlContext`** — `useClavro()` subscribes only to `baseUrl`, not auth state, so data API components don't re-render on auth changes
