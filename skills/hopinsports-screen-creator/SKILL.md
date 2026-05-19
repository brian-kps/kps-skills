---
name: hopinsports-screen-creator
description: Creates new Compose Multiplatform screens for HopInSports with full navigation and Koin integration. Use when creating new screens, adding new features that need UI, or scaffolding screen templates. Generates Route, Screen, and ViewModel files following project patterns. Handles navigation route registration in Routes.kt, App.kt wiring, and Koin ViewModel registration.
---

# HopInSports Screen Creator

Creates new screens for the HopInSports Kotlin Multiplatform app with proper structure, navigation integration, and dependency injection.

## Workflow

### Step 1: Gather Requirements

Determine screen type and details:
- **Screen name**: PascalCase (e.g., `EventAttendees`, `MemberList`)
- **Screen type**: Detail, List, Form/Edit, Settings, or Create
- **Parameters**: Entity ID if detail/edit screen
- **Data source**: Which repository/API to use
- **Navigation targets**: Other screens this navigates to

### Step 2: Create Feature Package

Create directory: `composeApp/src/commonMain/kotlin/com/hopinsports/{featurename}/`

### Step 3: Generate Files

Create files in order (read `references/patterns.md` for templates):

1. **ViewModel** (`{FeatureName}ViewModel.kt`)
   - Define State data class with `isLoading`, `errorMessage`, `requiresReAuth`
   - Add feature-specific state fields
   - Implement load/refresh/action methods

2. **Screen** (`{FeatureName}Screen.kt`)
   - Pure UI composable receiving state and callbacks
   - Handle loading/error/content states
   - Use Theme.* for colors, HopInOutlinedCard for containers
   - Add testTag modifiers for Maestro testing

3. **Route** (`{FeatureName}Route.kt`)
   - Wire ViewModel with koinViewModel()
   - Collect state with collectAsState()
   - Handle LaunchedEffect for data loading
   - Include ReAuthEffect for auth handling
   - Connect navigation callbacks

Read `references/screen-types.md` for screen-type-specific patterns.

### Step 4: Register Navigation Route

Add to `composeApp/src/commonMain/kotlin/com/hopinsports/navigation/Routes.kt`:

```kotlin
// No parameters
@Serializable
object {FeatureName}Route

// With parameters
@Serializable
data class {FeatureName}Route(val entityId: String)
```

**If this is a tab-level route** (shown with bottom bar), also add it to the route classification maps in `Routes.kt`:
- `TAB_ROUTE_NAMES` — if it should highlight a tab
- `BOTTOM_BAR_ROUTE_PATTERNS` — if it should show the bottom bar

### Step 5: Wire in AppNavGraph.kt

Add composable entry in `composeApp/src/commonMain/kotlin/com/hopinsports/navigation/AppNavGraph.kt` inside `appNavGraph()`:

```kotlin
// No parameters
composable<{FeatureName}Route> {
    {FeatureName}Route(navController = navController)
}

// With parameters
composable<{FeatureName}Route> { entry ->
    val route = entry.toRoute<{FeatureName}Route>()
    {FeatureName}Route(
        entityId = route.entityId,
        navController = navController
    )
}
```

**Important:** Route registrations go in `AppNavGraph.kt`, NOT in `App.kt`. App.kt calls `appNavGraph(navController)` inside the NavHost.

### Step 5b: Navigation to Tab Destinations

When navigating TO a tab destination from within a screen, always use `navigateToTab()`:

```kotlin
import com.hopinsports.navigation.navigateToTab

// ✅ Correct — uses consistent tab-style navigation
navController.navigateToTab(ExploreTabRoute)

// ❌ Wrong — breaks back stack and tab highlighting
navController.navigate(ExploreTabRoute)
```

`navigateToTab()` handles `popUpTo(HomeTabRoute)`, `saveState`, `launchSingleTop`, and `restoreState` consistently.

### Step 6: Register ViewModel in Koin

Add to `composeApp/src/commonMain/kotlin/com/hopinsports/di/AppModule.kt`:

```kotlin
viewModel { {FeatureName}ViewModel(get()) }
```

Match constructor parameters to injected dependencies.

## Screen Type Quick Reference

| Type | Key State Fields | Key Callbacks |
|------|------------------|---------------|
| Detail | `entity: T?`, `isLoading` | `onRefresh`, `onNavigateBack`, navigation to related |
| List | `items: List<T>`, `searchQuery` | `onSearch`, `onItemClick`, `onRefresh` |
| Form/Edit | form fields, `hasChanges`, `saveSuccess` | `on{Field}Change`, `onSave` |
| Settings | toggle states | `on{Setting}Changed` |
| Create | form fields, `isValid`, `createSuccess`, `createdId` | `on{Field}Change`, `onCreate` |

## File Locations

- Feature code: `composeApp/src/commonMain/kotlin/com/hopinsports/{feature}/`
- Routes & classification: `composeApp/src/commonMain/kotlin/com/hopinsports/navigation/Routes.kt`
- Nav graph (route registration): `composeApp/src/commonMain/kotlin/com/hopinsports/navigation/AppNavGraph.kt`
- App scaffold: `composeApp/src/commonMain/kotlin/com/hopinsports/App.kt`
- Bottom bar (tabs/search): `composeApp/src/commonMain/kotlin/com/hopinsports/ui/AppBottomBar.kt`
- Koin module: `composeApp/src/commonMain/kotlin/com/hopinsports/di/AppModule.kt`
- Theme components: `composeApp/src/commonMain/kotlin/com/hopinsports/theme/components/`

## Key Imports

Always use:
- `com.composeunstyled.theme.Theme` for theme access
- `com.hopinsports.theme.*` for theme extensions (surface, primary, etc.)
- `com.hopinsports.theme.components.*` for shared components
- `org.koin.compose.viewmodel.koinViewModel` for ViewModel injection
