# Step 1: React App Setup

## Create the Project

```bash
pnpm create vite@latest my-app -- --template react-ts
cd my-app
pnpm install
```

## Install the Clavro SDK

```bash
pnpm add @clavro/react
```

Optional but recommended:
```bash
pnpm add react-router-dom
pnpm add @tanstack/react-query    # data fetching / caching
```

## Configure Vite Proxy (REQUIRED for local dev)

The Vite proxy is **required** for local development. Without it, Clavro's `Set-Cookie` headers are silently blocked by the browser as third-party cookies (`localhost` ≠ `clavro.org`). The sign-in will appear to work but the session is lost on page refresh.

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Clavro BFF auth routes — MUST come before the catch-all /api
      "/api/bff/v1": {
        target: "https://dev-slug.clavro.org",
        changeOrigin: true,
        secure: true,
      },
      // Clavro data API routes — MUST come before the catch-all /api
      "/api/data/v1": {
        target: "https://dev-slug.clavro.org",
        changeOrigin: true,
        secure: true,
      },
      // All other /api/* routes → your backend server
      "/api": {
        target: "http://localhost:8080",
        changeOrigin: true,
      },
    },
  },
});
```

> **Important:** Replace `dev-slug.clavro.org` with your actual Clavro dev instance URL. The Vite proxy matches routes in order — more specific paths (`/api/bff/v1`, `/api/data/v1`) must come before the catch-all `/api`.

## Environment Variables

Use Vite env files to configure `ClavroProvider` baseUrl per environment:

```bash
# .env.development — empty = same-origin (uses Vite proxy)
VITE_CLAVRO_BASE_URL=

# .env.production — custom domain pointing to Clavro instance via CNAME
VITE_CLAVRO_BASE_URL=https://clavro.example.com
```

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

```tsx
// src/main.tsx
<ClavroProvider baseUrl={import.meta.env.VITE_CLAVRO_BASE_URL}>
```

### How the Proxy Works

```
Browser (localhost:5173)
  └── fetch("/api/bff/v1/auth/sign-in", { credentials: "include" })
        │
        ▼
Vite Dev Server (localhost:5173)
  └── Proxies to: https://dev-slug.clavro.org/api/bff/v1/auth/sign-in
        │
        ▼
Clavro Server
  └── Sets httpOnly cookies on the response
        │
        ▼
Browser receives cookies as FIRST-PARTY (domain: localhost)

  └── fetch("/api/users/me", { credentials: "include" })
        │
        ▼
Vite Dev Server (localhost:5173)
  └── Proxies to: http://localhost:8080/api/users/me (with cookies forwarded)
        │
        ▼
Your Backend
  └── Reads JWT from vaultkey_access cookie, validates via JWKS
```

### Why Not Cross-Origin baseUrl?

Setting `baseUrl="https://dev-slug.clavro.org"` **does not work** for local development:

- CORS headers are set correctly by Clavro
- `signIn()` succeeds and returns user data (SDK sets state from response body)
- But `Set-Cookie` is **silently blocked** — the browser treats it as a third-party cookie
- On refresh, `getSession()` sends no cookie → user appears logged out
- No errors in the console (cookie blocking is silent)

This is not a Clavro bug — it's how modern browsers handle cookies from different registrable domains. The Vite proxy makes everything same-origin, solving the problem entirely.

## Project Structure

With `@clavro/react`, the project structure is simpler — no need for local auth/api boilerplate:

```
src/
├── components/
│   └── ...
├── pages/
│   ├── sign-in.tsx
│   ├── sign-up.tsx
│   ├── dashboard.tsx
│   ├── profile.tsx
│   ├── sessions.tsx
│   └── ...
├── App.tsx
├── router.tsx
└── main.tsx
```
