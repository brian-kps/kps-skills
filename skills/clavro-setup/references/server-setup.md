# Ktor Server Configuration

## JWT Validator Setup

```kotlin
import org.clavro.sdk.resourceserver.JwtValidator
import org.clavro.sdk.resourceserver.ResourceServerConfig

val jwtValidator = JwtValidator(ResourceServerConfig.default("app.clavro.dev"))
```

**Configuration:**
- `audience`: Must match JWT access token audience claim
- `default()` provides sensible defaults for cache, timeouts, retries

## Application Module (`server/src/main/kotlin/.../Application.kt`)

```kotlin
import org.clavro.ktor.clavro
import org.clavro.ktor.ClavroPrincipal
import io.ktor.server.application.*
import io.ktor.server.auth.*
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import io.ktor.serialization.kotlinx.json.json
import io.ktor.http.ContentType
import io.ktor.server.response.respond
import io.ktor.server.response.respondText
import io.ktor.server.routing.*
import kotlinx.serialization.json.Json

fun Application.module() {
    // Configure JSON serialization
    install(ContentNegotiation) {
        json(Json {
            ignoreUnknownKeys = true
            explicitNulls = false
        })
    }

    // Install Clavro authentication
    install(Authentication) {
        clavro(validator = jwtValidator)
    }

    routing {
        // Public endpoint
        get("/health") {
            call.respondText("OK", ContentType.Text.Plain)
        }

        // Protected endpoint
        authenticate("clavro") {
            get("/protected") {
                val principal = call.principal<ClavroPrincipal>()
                val userId = principal?.userId
                call.respond(mapOf("message" to "Hello, user $userId!"))
            }
        }
    }
}
```

## Key Points

- Install `ContentNegotiation` with JSON for API responses
- Install `Authentication` with `clavro` provider using JWT validator
- Use `authenticate("clavro")` block to protect routes
- Access user info via `call.principal<ClavroPrincipal>()`

## Available Principal Properties

```kotlin
val principal = call.principal<ClavroPrincipal>()
principal?.userId      // User ID from token
principal?.email       // User email (if available)
principal?.claims      // All JWT claims
```
