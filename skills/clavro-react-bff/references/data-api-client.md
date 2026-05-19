# Step 5: Data API Client

The `@clavro/react` SDK provides the `useClavro()` hook for authenticated data API access. The `vaultkey_access` httpOnly cookie is sent automatically by the browser — no token management needed.

## Using `useClavro()`

```tsx
import { useClavro } from "@clavro/react";

function MyComponent() {
  const { users, sessions, organizations, environment } = useClavro();

  // Each namespace has typed methods for the corresponding API endpoints
}
```

The hook reads `baseUrl` from the nearest `<ClavroProvider>` and returns a memoized data API client. It subscribes only to `baseUrl` changes — not auth state — so components using `useClavro()` don't re-render on sign-in/sign-out.

## Standalone Usage (Advanced)

For use outside of React:

```typescript
import { createDataApi } from "@clavro/react";

const dataApi = createDataApi("https://acme.clavro.org");
const profile = await dataApi.users.getMe();
```

## API Namespaces

### `users`

| Method | Description |
|--------|-------------|
| `getMe()` | Get current user's profile → `ClavroUser` |
| `updateMe(data)` | Update profile (firstName, lastName, avatarUrl, metadata) → `ClavroUser` |
| `deleteMe()` | Delete current user's account → `void` |
| `changeEmail(newEmail, currentPassword)` | Change email → `void` |
| `changePassword(currentPassword, newPassword)` | Change password → `void` |

### `sessions`

| Method | Description |
|--------|-------------|
| `list()` | List all active sessions → `ClavroSession[]` |
| `revoke(sessionId)` | Revoke a specific session → `void` |

### `organizations`

| Method | Description |
|--------|-------------|
| `list()` | List orgs the user belongs to → `ClavroOrganization[]` |
| `get(id)` | Get org by ID → `ClavroOrganization` |
| `create(data)` | Create org (name, slug, logoUrl?, metadata?) → `ClavroOrganization` |
| `update(id, data)` | Update org → `ClavroOrganization` |
| `delete(id)` | Delete org → `void` |
| `transferOwnership(id, newOwnerId)` | Transfer org ownership → `void` |

### `environment`

| Method | Description |
|--------|-------------|
| `getConfig()` | Get instance config (public, no auth) → `ClavroEnvironmentConfig` |

## SDK Types

```typescript
import type {
  ClavroUser,              // User profile
  ClavroSession,           // Full session (for data API /sessions)
  ClavroOrganization,      // Org with memberCount and role
  ClavroEnvironmentConfig, // Instance config (auth, display, user settings)
} from "@clavro/react";
```

## Usage Examples

### Profile Page

```tsx
import { useEffect, useState } from "react";
import { useClavro, type ClavroUser } from "@clavro/react";

export function ProfilePage() {
  const { users } = useClavro();
  const [profile, setProfile] = useState<ClavroUser | null>(null);

  useEffect(() => {
    users.getMe().then(setProfile);
  }, [users]);

  if (!profile) return <p>Loading...</p>;

  return (
    <div>
      <h1>Profile</h1>
      <p>Email: {profile.email}</p>
      <p>Name: {profile.fullName}</p>
      <p>Verified: {profile.emailVerified ? "Yes" : "No"}</p>
    </div>
  );
}
```

### Active Sessions Page

```tsx
import { useEffect, useState } from "react";
import { useClavro, type ClavroSession } from "@clavro/react";

export function SessionsPage() {
  const { sessions: sessionsApi } = useClavro();
  const [sessions, setSessions] = useState<ClavroSession[]>([]);

  useEffect(() => {
    sessionsApi.list().then(setSessions);
  }, [sessionsApi]);

  async function handleRevoke(sessionId: string) {
    await sessionsApi.revoke(sessionId);
    setSessions((s) => s.filter((sess) => sess.id !== sessionId));
  }

  return (
    <div>
      <h1>Active Sessions</h1>
      {sessions.map((session) => (
        <div key={session.id}>
          <p>
            {session.userAgent} — Last active: {session.lastActiveAt}
            {session.current && " (current)"}
          </p>
          {!session.current && (
            <button onClick={() => handleRevoke(session.id)}>Revoke</button>
          )}
        </div>
      ))}
    </div>
  );
}
```

### Using with React Query

```tsx
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useClavro } from "@clavro/react";

function ProfilePage() {
  const { users } = useClavro();
  const queryClient = useQueryClient();

  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => users.getMe(),
  });

  const updateProfile = useMutation({
    mutationFn: (data: { firstName?: string; lastName?: string }) =>
      users.updateMe(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] }),
  });

  // ...
}
```
