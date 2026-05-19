# HopInSports Screen Patterns

## Table of Contents
- [File Structure](#file-structure)
- [Route Pattern](#route-pattern)
- [Screen Pattern](#screen-pattern)
- [ViewModel Pattern](#viewmodel-pattern)
- [Navigation Route](#navigation-route)
- [Koin Registration](#koin-registration)
- [Common Imports](#common-imports)

## File Structure

Each feature creates a package under `composeApp/src/commonMain/kotlin/com/hopinsports/`:

```
featurename/
├── FeatureNameRoute.kt      # Navigation wrapper, ViewModel wiring
├── FeatureNameScreen.kt     # Pure UI composable
├── FeatureNameViewModel.kt  # State management + business logic
└── components/              # Optional: sub-components
    └── FeatureNameTopBar.kt
```

## Route Pattern

Route composables wire up the ViewModel, collect state, and handle navigation:

```kotlin
package com.hopinsports.{featurename}

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.navigation.NavHostController
import com.hopinsports.ui.ReAuthEffect
import org.koin.compose.viewmodel.koinViewModel

@Composable
fun {FeatureName}Route(
    navController: NavHostController,
    viewModel: {FeatureName}ViewModel = koinViewModel()
) {
    val state by viewModel.state.collectAsState()

    // Optional: Load data on mount
    LaunchedEffect(Unit) {
        viewModel.load()
    }

    // Optional: Handle re-authentication
    ReAuthEffect(
        requiresReAuth = state.requiresReAuth,
        navController = navController,
        onDismiss = { viewModel.clearError() }
    )

    {FeatureName}Screen(
        state = state,
        onNavigateBack = { navController.popBackStack() },
        // ... other callbacks
    )
}
```

### Route with Entity ID Parameter

```kotlin
@Composable
fun {FeatureName}Route(
    entityId: String,
    navController: NavHostController,
    viewModel: {FeatureName}ViewModel = koinViewModel()
) {
    val state by viewModel.state.collectAsState()

    LaunchedEffect(entityId) {
        viewModel.load(entityId)
    }

    // ... rest of implementation
}
```

### Route with Lifecycle Refresh

```kotlin[animated-paywall-compose.skill](../../../../Downloads/animated-paywall-compose.skill)
@Composable
fun {FeatureName}Route(
    navController: NavHostController,
    viewModel: {FeatureName}ViewModel = koinViewModel()
) {
    val state by viewModel.state.collectAsState()
    val lifecycleOwner = LocalLifecycleOwner.current

    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) {
                viewModel.refresh(silent = true)
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    // ... rest of implementation
}
```

## Screen Pattern

Screen composables are pure UI, receiving state and callbacks:

```kotlin
package com.hopinsports.{featurename}

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.composeunstyled.theme.Theme
import com.hopinsports.theme.surface

@Composable
fun {FeatureName}Screen(
    state: {FeatureName}State,
    onNavigateBack: () -> Unit,
    // ... other callbacks
) {
    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Theme.surface())
            .windowInsetsPadding(WindowInsets.safeDrawing)
    ) {
        // Top Bar
        {FeatureName}TopBar(onNavigateBack = onNavigateBack)

        // Content
        when {
            state.isLoading -> LoadingContent()
            state.errorMessage != null -> ErrorContent(
                message = state.errorMessage,
                onRetry = { /* retry action */ }
            )
            else -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(scrollState)
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // Main content here
                }
            }
        }
    }
}
```

### TopBar Component

```kotlin
@Composable
private fun {FeatureName}TopBar(onNavigateBack: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(Theme.primary())
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clickable(onClick = onNavigateBack),
                contentAlignment = Alignment.Center
            ) {
                Image(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back",
                    colorFilter = ColorFilter.tint(Theme.primaryForeground()),
                    modifier = Modifier.size(24.dp)
                )
            }
            BasicText(
                text = "{Feature Title}",
                style = TextStyle(
                    fontSize = 18.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = Theme.primaryForeground()
                )
            )
        }
    }
}
```

## ViewModel Pattern

ViewModels manage state and business logic:

```kotlin
package com.hopinsports.{featurename}

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class {FeatureName}State(
    val isLoading: Boolean = true,
    val errorMessage: String? = null,
    val requiresReAuth: Boolean = false,
    // ... feature-specific fields
)

class {FeatureName}ViewModel(
    private val repository: SomeRepository
) : ViewModel() {

    private val _state = MutableStateFlow({FeatureName}State())
    val state: StateFlow<{FeatureName}State> = _state.asStateFlow()

    fun load() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, errorMessage = null) }
            when (val result = repository.getData()) {
                is ApiResult.Success -> {
                    _state.update { it.copy(isLoading = false, data = result.data) }
                }
                is ApiResult.Error -> {
                    _state.update {
                        it.copy(
                            isLoading = false,
                            errorMessage = result.displayMessage,
                            requiresReAuth = result.isUnauthorized
                        )
                    }
                }
            }
        }
    }

    fun clearError() {
        _state.update { it.copy(errorMessage = null, requiresReAuth = false) }
    }
}
```

### ViewModel without Repository (local state only)

```kotlin
class {FeatureName}ViewModel : ViewModel() {
    private val _state = MutableStateFlow({FeatureName}State())
    val state: StateFlow<{FeatureName}State> = _state.asStateFlow()

    fun onSomeValueChanged(value: String) {
        _state.update { it.copy(someValue = value) }
    }
}
```

## Navigation Route

Add route to `composeApp/src/commonMain/kotlin/com/hopinsports/navigation/Routes.kt`:

```kotlin
// For screens without parameters
@Serializable
object {FeatureName}Route

// For screens with parameters
@Serializable
data class {FeatureName}Route(val entityId: String)
```

If this route should show the bottom bar, add it to `BOTTOM_BAR_ROUTE_PATTERNS` in the same file.
If this route is a tab root, also add it to `TAB_ROUTE_NAMES`.

Register the composable in `composeApp/src/commonMain/kotlin/com/hopinsports/navigation/AppNavGraph.kt` inside `appNavGraph()`:

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

When navigating to tab destinations from a screen, use `navigateToTab()`:
```kotlin
import com.hopinsports.navigation.navigateToTab
navController.navigateToTab(ExploreTabRoute)
```

## Koin Registration

Add ViewModel to `composeApp/src/commonMain/kotlin/com/hopinsports/di/AppModule.kt`:

```kotlin
// ViewModel without dependencies
viewModel { {FeatureName}ViewModel() }

// ViewModel with repository dependencies
viewModel { {FeatureName}ViewModel(get()) }

// ViewModel with multiple dependencies
viewModel { {FeatureName}ViewModel(get(), get(), get()) }
```

## Common Imports

### Route file imports
```kotlin
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.navigation.NavHostController
import com.hopinsports.navigation.*
import com.hopinsports.ui.ReAuthEffect
import org.koin.compose.viewmodel.koinViewModel
```

### Screen file imports
```kotlin
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.BasicText
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.composeunstyled.theme.Theme
import com.hopinsports.theme.*
import com.hopinsports.theme.components.*
```

### ViewModel file imports
```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
```
