# Navigation Setup

## Auth States

| State | Description | Navigation |
|-------|-------------|------------|
| `Initializing` | SDK starting, checking tokens | **No navigation** - wait |
| `Refreshing` | Startup token refresh only | **No navigation** - wait |
| `Authenticated` | Valid session (has `userId`) | Navigate to authenticated route |
| `Unauthenticated` | No valid session | Navigate to sign-in |
| `Authorizing` | OAuth flow in progress | No navigation |
| `Error` | Auth error occurred | Navigate to sign-in |

**Key behaviors:**
- `Refreshing` is only emitted during initial startup (checking stored tokens). During an active session, token refreshes happen silently — the state stays `Authenticated`.
- `Authenticated.userId` is extracted from the JWT `sub` claim at construction time. Access it directly: `state.userId`.
- `Authenticated.equals()` compares `userId` only — `MutableStateFlow` won't emit on token refresh (same user, new tokens), so no unnecessary recomposition or navigation.

## Recommended Setup with Splash Screen

### Route Definitions

```kotlin
import kotlinx.serialization.Serializable

@Serializable
object SplashRoute  // Shown during SDK initialization

@Serializable
object AuthenticatedRoute
```

### App Composable (`composeApp/src/commonMain/kotlin/.../App.kt`)

```kotlin
import org.clavro.sdk.compose.navigation.*
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController

@Composable
fun App() {
    val navController = rememberNavController()

    // Handle auth state-based navigation
    ClavroAuthNavigationHandler(
        navController = navController,
        config = AuthNavigationConfig(
            authenticatedRoute = AuthenticatedRoute,
            unauthenticatedRoute = ClavroSignInRoute
        )
    )

    NavHost(
        navController = navController,
        startDestination = SplashRoute,  // Start with splash, NOT sign-in
    ) {
        // Splash screen - shown during Initializing/Refreshing states
        composable<SplashRoute> {
            SplashScreen()
        }

        // Register all Clavro auth screens
        clavroAuthRoutes(navController = navController)

        // Add your authenticated routes
        composable<AuthenticatedRoute> {
            AuthenticatedScreen()
        }
    }
}

@Composable
fun SplashScreen() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        CircularProgressIndicator()
    }
}
```

## App Launch Behavior

| Scenario | User Experience |
|----------|-----------------|
| Valid tokens stored | Splash -> Home (instant) |
| Expired tokens, refresh succeeds | Splash -> Home (1-2s) |
| Expired tokens, refresh fails | Splash -> Sign-In |
| No tokens stored | Splash -> Sign-In (instant) |

## Alternative: AuthStateGate (No NavHost)

For simpler apps without complex navigation:

```kotlin
import org.clavro.sdk.compose.AuthStateGate

@Composable
fun App() {
    AuthStateGate(
        loading = { SplashScreen() },
        authenticated = { HomeScreen() },
        unauthenticated = { SignInFlow() }
    )
}
```

## Advanced: Custom Loading State Callbacks

```kotlin
ClavroAuthNavigationHandler(
    navController = navController,
    config = AuthNavigationConfig(
        authenticatedRoute = AuthenticatedRoute,
        unauthenticatedRoute = ClavroSignInRoute,
        onInitializing = { navController ->
            navController.navigate(SplashRoute) {
                launchSingleTop = true
            }
        },
        // onRefreshing only fires at startup (expired stored tokens being refreshed)
        // During active sessions, token refresh is silent — state stays Authenticated
        onRefreshing = { navController, refreshingState ->
            // refreshingState.previousTokens for optimistic UI at startup
        }
    )
)
```

## Accessing userId

`AuthState.Authenticated` exposes `userId` directly from the JWT — no API call needed:

```kotlin
when (val state = authState) {
    is AuthState.Authenticated -> {
        // userId available immediately, no network call
        val userId = state.userId
        initSentry(userId)
        initRevenueCat(userId)
    }
}
```

Token refreshes (same user, new tokens) do NOT trigger recomposition because
`Authenticated.equals()` compares `userId` only.

## Common Pitfalls

- **Don't** use sign-in as `startDestination` - causes flicker
- **Don't** navigate during `Initializing` or `Refreshing`
- **Don't** access `state.tokens` for the user ID — use `state.userId` instead
- **Do** use splash/loading screen as `startDestination`
- **Do** let `ClavroAuthNavigationHandler` manage navigation
