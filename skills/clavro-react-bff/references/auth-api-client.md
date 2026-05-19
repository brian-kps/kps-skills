# Step 2: Auth API Client

The `@clavro/react` SDK provides the auth API client built in. All requests use `credentials: "include"` so the browser automatically sends and receives httpOnly cookies.

## Using via the Provider (Recommended)

When using `<ClavroProvider>`, you don't create the auth client directly — the `useAuth()` hook handles everything:

```tsx
import { useAuth } from "@clavro/react";

function MyComponent() {
  const { signIn, signUp, signOut, user, session, isLoading } = useAuth();

  // signIn, signUp, signOut are pre-wired to the provider's baseUrl
}
```

## Standalone Usage (Advanced)

For use outside of React (tests, scripts, SSR), use the factory function directly:

```typescript
import { createAuthApi, ClavroApiError } from "@clavro/react";

const authApi = createAuthApi("https://acme.clavro.org");

try {
  const res = await authApi.signIn({ email: "user@example.com", password: "..." });
  console.log(res.user, res.session);
} catch (err) {
  if (err instanceof ClavroApiError) {
    console.error(err.status, err.code, err.message);
  }
}
```

## SDK Types

```typescript
import type {
  ClavroUser,          // User profile (id, email, firstName, lastName, avatarUrl, etc.)
  ClavroSessionInfo,   // Session metadata (userId, sessionId, email, expiresAt)
  SignInRequest,        // { email, password, rememberMe? }
  SignUpRequest,        // { email, password, firstName?, lastName?, metadata? }
  BffSignInResponse,    // { session: ClavroSession, user: ClavroUser }
  BffSignUpResponse,    // { session: ClavroSession, user: ClavroUser, message? }
  BffSessionResponse,   // { authenticated, session?, user? }
  BffRefreshResponse,   // { session: ClavroSession }
} from "@clavro/react";
```

## Auth API Methods

| Method | Description | Auth |
|--------|-------------|------|
| `signIn(data)` | Email + password sign-in. Sets cookies. | Public |
| `signUp(data)` | Create account + auto sign-in. Sets cookies. | Public |
| `signOut()` | Revokes session, clears cookies. | Cookie |
| `refresh()` | Rotates access + refresh cookies. | Cookie |
| `getSession()` | Check current session status. | Cookie |

## Error Handling

```typescript
import { ClavroApiError } from "@clavro/react";

try {
  await signIn({ email, password });
} catch (err) {
  if (err instanceof ClavroApiError) {
    // err.status  — HTTP status code (401, 403, etc.)
    // err.code    — Error code ("INVALID_CREDENTIALS", "ACCOUNT_LOCKED", etc.)
    // err.message — Human-readable message
    setError(err.message);
  }
}
```

## Key Points

1. **`credentials: "include"`** — handled internally by the SDK. The browser sends/receives httpOnly cookies automatically.

2. **No tokens in responses** — the sign-in/sign-up responses contain user and session metadata, but the actual JWT is only in the `Set-Cookie` header (httpOnly, invisible to JS).

3. **Error typing** — `ClavroApiError` carries `status`, `code`, and `message` so your UI can show specific error messages (e.g., "Invalid credentials" vs "Account locked").
