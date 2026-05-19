# Step 4: Protected Routes

## `<SignedIn>` and `<SignedOut>` Components

For inline conditional rendering based on auth state — no callbacks, no redirects:

```tsx
import { SignedIn, SignedOut } from "@clavro/react";

function Header() {
  return (
    <header>
      <SignedOut>
        <a href="/sign-in">Sign In</a>
        <a href="/sign-up">Sign Up</a>
      </SignedOut>
      <SignedIn>
        <UserMenu />
      </SignedIn>
    </header>
  );
}
```

Both components render nothing while `isLoading` is true (no flash of wrong content).

## `<AuthGuard>` Component

For route-level protection with loading states and redirect callbacks:

```tsx
import { AuthGuard } from "@clavro/react";
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `ReactNode` | — | Protected content |
| `fallback` | `ReactNode` | Centered "Loading..." | Shown while `isLoading` is true |
| `onUnauthenticated` | `() => void` | — | Called when user is not authenticated (e.g., redirect) |

## Router Setup (React Router)

```tsx
// src/router.tsx
import { createBrowserRouter, Outlet, useNavigate } from "react-router-dom";
import { AuthGuard } from "@clavro/react";
import { SignInPage } from "@/pages/sign-in";
import { SignUpPage } from "@/pages/sign-up";
import { DashboardPage } from "@/pages/dashboard";
import { ProfilePage } from "@/pages/profile";

function ProtectedLayout() {
  const navigate = useNavigate();
  return (
    <AuthGuard onUnauthenticated={() => navigate("/sign-in", { replace: true })}>
      <main>
        <Outlet />
      </main>
    </AuthGuard>
  );
}

export const router = createBrowserRouter([
  // Public routes
  { path: "/sign-in", element: <SignInPage /> },
  { path: "/sign-up", element: <SignUpPage /> },

  // Protected routes (all children require auth)
  {
    element: <ProtectedLayout />,
    children: [
      { path: "/", element: <DashboardPage /> },
      { path: "/profile", element: <ProfilePage /> },
    ],
  },
]);
```

### Per-Route Guard (Alternative)

```tsx
export const router = createBrowserRouter([
  { path: "/sign-in", element: <SignInPage /> },
  {
    path: "/",
    element: (
      <AuthGuard onUnauthenticated={() => window.location.href = "/sign-in"}>
        <DashboardPage />
      </AuthGuard>
    ),
  },
]);
```

### Custom Loading Fallback

```tsx
<AuthGuard
  fallback={<div className="flex items-center justify-center h-screen"><Spinner /></div>}
  onUnauthenticated={() => navigate("/sign-in")}
>
  <Outlet />
</AuthGuard>
```

## App Entry Point

```tsx
// src/App.tsx
import { ClavroProvider } from "@clavro/react";
import { RouterProvider } from "react-router-dom";
import { router } from "./router";

export default function App() {
  return (
    <ClavroProvider>
      <RouterProvider router={router} />
    </ClavroProvider>
  );
}
```

## Sign-In Page

```tsx
// src/pages/sign-in.tsx
import { useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { useAuth, ClavroApiError } from "@clavro/react";

export function SignInPage() {
  const { isLoading, user, signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Already authenticated — redirect to dashboard
  if (!isLoading && user) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await signIn({ email, password });
      // Provider updates state → AuthGuard renders dashboard
    } catch (err) {
      if (err instanceof ClavroApiError) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1>Sign In</h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={submitting}>
          {submitting ? "Signing in..." : "Sign In"}
        </button>
      </form>

      <p>
        Don't have an account? <Link to="/sign-up">Sign up</Link>
      </p>
    </div>
  );
}
```

## Sign-Up Page

```tsx
// src/pages/sign-up.tsx
import { useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { useAuth, ClavroApiError } from "@clavro/react";

export function SignUpPage() {
  const { isLoading, user, signUp } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!isLoading && user) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await signUp({
        email,
        password,
        firstName: firstName || undefined,
        lastName: lastName || undefined,
      });
    } catch (err) {
      if (err instanceof ClavroApiError) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1>Create Account</h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="firstName">First Name</label>
          <input
            id="firstName"
            type="text"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="lastName">Last Name</label>
          <input
            id="lastName"
            type="text"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
        </div>
        <button type="submit" disabled={submitting}>
          {submitting ? "Creating account..." : "Sign Up"}
        </button>
      </form>

      <p>
        Already have an account? <Link to="/sign-in">Sign in</Link>
      </p>
    </div>
  );
}
```

## Sign-Out Button

```tsx
import { useAuth } from "@clavro/react";

function SignOutButton() {
  const { signOut } = useAuth();
  return <button onClick={() => signOut()}>Sign Out</button>;
}
```

## Displaying User Info

```tsx
import { useAuth } from "@clavro/react";

function UserGreeting() {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <div>
      <p>Welcome, {user.fullName || user.email}</p>
      {!user.emailVerified && <p>Please verify your email address.</p>}
    </div>
  );
}
```
