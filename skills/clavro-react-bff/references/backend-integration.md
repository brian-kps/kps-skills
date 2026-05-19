# Step 6: Backend Integration (Optional)

If your app has its own backend API, you need to validate Clavro JWTs on incoming requests. The JWT in the `vaultkey_access` cookie (or `Authorization: Bearer` header) is a standard RS256 token that can be verified using the JWKS endpoint.

## How It Works

```
Browser → Your Backend → Clavro JWKS
  │           │               │
  │  Cookie or Bearer token   │
  │           │               │
  │     1. Extract JWT        │
  │     2. Fetch JWKS ────────┤
  │     3. Verify signature   │
  │     4. Extract claims     │
  │           │               │
  │     200 { data }          │
```

The JWKS endpoint is at:
```
https://{slug}.clavro.org/.well-known/jwks.json
```

Or if using a custom domain:
```
https://auth.example.com/.well-known/jwks.json
```

## JWT Claims

The access token contains these claims:

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | string | User ID |
| `iss` | string | Issuer URL (your instance URL) |
| `aud` | string | Audience |
| `exp` | number | Expiration timestamp |
| `iat` | number | Issued at timestamp |
| `jti` | string | Unique token ID |
| `session_id` | string | Session ID |
| `email` | string | User email |
| `email_verified` | boolean | Whether email is verified |
| `org_id` | string? | Organization ID (if applicable) |
| `role` | string? | User role |
| `permissions` | string[]? | User permissions |

## Node.js / Express

```typescript
// middleware/auth.ts
import jwt from "jsonwebtoken";
import jwksClient from "jwks-rsa";

const CLAVRO_INSTANCE_URL = process.env.CLAVRO_INSTANCE_URL!;
// e.g., "https://acme.clavro.org"

const client = jwksClient({
  jwksUri: `${CLAVRO_INSTANCE_URL}/.well-known/jwks.json`,
  cache: true,
  cacheMaxAge: 600000, // 10 minutes
});

function getSigningKey(header: jwt.JwtHeader): Promise<string> {
  return new Promise((resolve, reject) => {
    client.getSigningKey(header.kid, (err, key) => {
      if (err) return reject(err);
      resolve(key!.getPublicKey());
    });
  });
}

export interface ClavroClaims {
  sub: string;          // userId
  email: string;
  emailVerified: boolean;
  sessionId: string;
  orgId?: string;
  role?: string;
  permissions?: string[];
}

export async function verifyClavroToken(token: string): Promise<ClavroClaims> {
  const decoded = jwt.decode(token, { complete: true });
  if (!decoded) throw new Error("Invalid token");

  const publicKey = await getSigningKey(decoded.header);

  const payload = jwt.verify(token, publicKey, {
    algorithms: ["RS256"],
    issuer: CLAVRO_INSTANCE_URL,
  }) as jwt.JwtPayload;

  return {
    sub: payload.sub!,
    email: payload.email,
    emailVerified: payload.email_verified,
    sessionId: payload.session_id,
    orgId: payload.org_id,
    role: payload.role,
    permissions: payload.permissions,
  };
}

// Express middleware
export function requireAuth(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  const token = authHeader?.startsWith("Bearer ")
    ? authHeader.slice(7)
    : req.cookies?.vaultkey_access; // If proxying cookies

  if (!token) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  verifyClavroToken(token)
    .then((claims) => {
      (req as any).user = claims;
      next();
    })
    .catch(() => {
      res.status(401).json({ error: "Invalid token" });
    });
}
```

### Usage

```typescript
import express from "express";
import { requireAuth } from "./middleware/auth";

const app = express();

app.get("/api/dashboard", requireAuth, (req, res) => {
  const user = (req as any).user;
  res.json({ message: `Hello ${user.email}` });
});
```

## Ktor (Kotlin) — Using Clavro Resource Server SDK

If your backend is Ktor, use the official Clavro resource server SDK with a custom auth provider that supports both Bearer tokens AND the BFF cookie:

### Gradle

```kotlin
// build.gradle.kts
dependencies {
    implementation("org.clavro:sdk-resource-server-ktor:$clavroVersion")
}
```

### Custom Auth Provider with Cookie Fallback

```kotlin
// auth/ClavroAuth.kt
import io.ktor.http.auth.HttpAuthHeader
import io.ktor.server.auth.*
import io.ktor.server.response.respond
import org.clavro.ktor.ClavroPrincipal
import org.clavro.sdk.resourceserver.JwtValidator
import org.clavro.sdk.resourceserver.models.ValidationResult

fun AuthenticationConfig.clavroWithCookie(validator: JwtValidator, realm: String = "Clavro") {
    val provider = object : AuthenticationProvider(Config("clavro")) {
        override suspend fun onAuthenticate(context: AuthenticationContext) {
            val call = context.call

            // Try Bearer token first, then fall back to BFF cookie
            val token = extractBearerToken(call) ?: extractCookieToken(call)

            if (token == null) {
                context.challenge("ClavroAuth", AuthenticationFailedCause.NoCredentials) { ch, _ ->
                    call.respond(UnauthorizedResponse(bearerChallenge(realm)))
                    ch.complete()
                }
                return
            }

            when (val result = validator.validate(token)) {
                is ValidationResult.Success -> context.principal(ClavroPrincipal(result.value))
                is ValidationResult.Failure -> context.challenge(
                    "ClavroAuth", AuthenticationFailedCause.InvalidCredentials
                ) { ch, _ ->
                    call.respond(UnauthorizedResponse(bearerChallenge(realm)))
                    ch.complete()
                }
            }
        }
    }
    register(provider)
}

private fun extractBearerToken(call: ApplicationCall): String? {
    val authHeader = call.request.parseAuthorizationHeader() as? HttpAuthHeader.Single
    if (authHeader == null || !authHeader.authScheme.equals("Bearer", ignoreCase = true)) return null
    return authHeader.blob
}

// The vaultkey_access cookie contains the same JWT as the Bearer token
private fun extractCookieToken(call: ApplicationCall): String? =
    call.request.cookies["vaultkey_access"]?.takeIf { it.isNotBlank() }
```

### Usage

```kotlin
fun Application.configureAuth() {
    val validator = JwtValidator.Builder()
        .jwksUrl("https://acme.clavro.org/.well-known/jwks.json")
        .build()

    install(Authentication) {
        clavroWithCookie(validator)
    }
}

fun Application.configureRoutes() {
    routing {
        authenticate("clavro") {
            get("/api/dashboard") {
                val principal = call.principal<ClavroPrincipal>()!!
                call.respond(mapOf("userId" to principal.userId))
            }
        }
    }
}
```

This pattern supports:
- **Mobile apps** → send `Authorization: Bearer <token>` (existing behavior)
- **Web app (BFF)** → browser sends `vaultkey_access` cookie automatically with `credentials: "include"`
- **Both use the same JWT validation** — no separate auth flows needed

## Go

```go
package main

import (
    "context"
    "net/http"
    "github.com/lestrrat-go/jwx/v2/jwk"
    "github.com/lestrrat-go/jwx/v2/jwt"
)

var jwksURL = "https://acme.clavro.org/.well-known/jwks.json"
var issuer  = "https://acme.clavro.org"

var keySet *jwk.Cache

func init() {
    ctx := context.Background()
    keySet = jwk.NewCache(ctx)
    keySet.Register(jwksURL)
}

func requireAuth(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := extractToken(r) // from Authorization header or cookie
        if token == "" {
            http.Error(w, "Unauthorized", 401)
            return
        }

        set, _ := keySet.Get(r.Context(), jwksURL)

        tok, err := jwt.Parse([]byte(token),
            jwt.WithKeySet(set),
            jwt.WithIssuer(issuer),
        )
        if err != nil {
            http.Error(w, "Invalid token", 401)
            return
        }

        // tok.Subject() = userId, tok.PrivateClaims()["email"], etc.
        ctx := context.WithValue(r.Context(), "user", tok)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

## OIDC Discovery

Clavro also exposes an OpenID Connect discovery document at:

```
https://{instance}/.well-known/openid-configuration
```

This returns standard OIDC metadata including `jwks_uri`, `issuer`, `authorization_endpoint`, `token_endpoint`, etc. Any OIDC-compliant library can use this for auto-configuration.

## Architecture: Cookie Proxying vs. Token Forwarding

### Option A: Same-domain proxy (recommended for BFF)

Your backend and Clavro share the cookie domain. The browser sends `vaultkey_access` to your backend too.

```
Browser → Your Backend (app.example.com)
            Cookie: vaultkey_access=<JWT>
            → Extract JWT from cookie, verify via JWKS
```

### Option B: Token forwarding

Your React app calls Clavro BFF for auth, and your own backend uses `Authorization: Bearer`. The React app never sees the JWT (it's httpOnly), so this only works if your backend is a downstream service that receives the token from another server — not from the browser directly.

### Option C: Separate auth flow

Your backend independently validates JWTs using JWKS. Tokens can come from:
- Mobile/native clients using the Clavro SDK (sends `Authorization: Bearer`)
- Server-to-server calls
- Any OAuth 2.1 compliant client
