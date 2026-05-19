# HopInSports Screen Types

## Table of Contents
- [Detail Screen](#detail-screen)
- [List Screen](#list-screen)
- [Form/Edit Screen](#formedit-screen)
- [Settings Screen](#settings-screen)
- [Create Screen](#create-screen)

## Detail Screen

Displays a single entity with full details. Loads data by ID.

### State
```kotlin
data class EventDetailState(
    val isLoading: Boolean = true,
    val errorMessage: String? = null,
    val requiresReAuth: Boolean = false,
    val event: EventDetail? = null,
    val userRegistration: Registration? = null,
    val cancelSuccess: Boolean = false
)
```

### Route
```kotlin
@Composable
fun EventDetailRoute(
    eventId: String,
    navController: NavHostController,
    viewModel: EventDetailViewModel = koinViewModel()
) {
    val state by viewModel.state.collectAsState()

    LaunchedEffect(eventId) {
        viewModel.load(eventId)
    }

    LaunchedEffect(state.cancelSuccess) {
        if (state.cancelSuccess) {
            viewModel.clearCancelSuccess()
            navController.popBackStack()
        }
    }

    ReAuthEffect(
        requiresReAuth = state.requiresReAuth,
        navController = navController,
        onDismiss = { viewModel.clearError() }
    )

    EventDetailScreen(
        state = state,
        viewModel = viewModel,
        onNavigateBack = { navController.popBackStack() },
        onNavigateToUserProfile = { userId ->
            navController.navigate(UserProfileRoute(userId = userId))
        },
        // ... other navigation callbacks
    )
}
```

### Screen Structure
```kotlin
@Composable
fun EventDetailScreen(
    state: EventDetailState,
    viewModel: EventDetailViewModel,
    onNavigateBack: () -> Unit,
    onNavigateToUserProfile: (String) -> Unit,
    // ... other callbacks
) {
    Box(modifier = Modifier.fillMaxSize().background(Theme.surface())) {
        when {
            state.isLoading -> LoadingState()
            state.errorMessage != null -> ErrorState(state.errorMessage, onRetry)
            state.event == null -> ErrorState("Event not found")
            else -> {
                // Detail content with scrollable sections
                Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
                    // Header image/info
                    // Detail sections
                    // Action buttons
                }
            }
        }
    }
}
```

## List Screen

Displays a scrollable list of entities with optional filtering.

### State
```kotlin
data class OrganizationListState(
    val isLoading: Boolean = true,
    val isRefreshing: Boolean = false,
    val errorMessage: String? = null,
    val requiresReAuth: Boolean = false,
    val organizations: List<OrganizationSummary> = emptyList(),
    val searchQuery: String = ""
)
```

### Screen Structure
```kotlin
@Composable
fun OrganizationListScreen(
    state: OrganizationListState,
    onSearch: (String) -> Unit,
    onRefresh: () -> Unit,
    onOrganizationClick: (String) -> Unit,
    onNavigateBack: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Theme.surface())
            .windowInsetsPadding(WindowInsets.safeDrawing)
    ) {
        // Top Bar with optional search
        ListTopBar(
            title = "Organizations",
            searchQuery = state.searchQuery,
            onSearchChange = onSearch,
            onNavigateBack = onNavigateBack
        )

        when {
            state.isLoading -> LoadingState()
            state.errorMessage != null -> ErrorState(state.errorMessage)
            state.organizations.isEmpty() -> EmptyState("No organizations found")
            else -> {
                LazyColumn(
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(state.organizations) { org ->
                        OrganizationCard(
                            organization = org,
                            onClick = { onOrganizationClick(org.id) }
                        )
                    }
                }
            }
        }
    }
}
```

## Form/Edit Screen

Edits an existing entity. Loads current data, allows modification, saves changes.

### State
```kotlin
data class ProfileEditState(
    val isLoading: Boolean = true,
    val isSaving: Boolean = false,
    val errorMessage: String? = null,
    val requiresReAuth: Boolean = false,
    val saveSuccess: Boolean = false,
    // Form fields
    val firstName: String = "",
    val lastName: String = "",
    val alias: String = "",
    val bio: String = "",
    // Validation
    val hasChanges: Boolean = false
)
```

### Route with Save Success Navigation
```kotlin
@Composable
fun ProfileEditScreenRoute(
    navController: NavHostController,
    viewModel: ProfileEditViewModel = koinViewModel()
) {
    val state by viewModel.state.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.load()
    }

    // Navigate back on successful save
    LaunchedEffect(state.saveSuccess) {
        if (state.saveSuccess) {
            viewModel.clearSaveSuccess()
            navController.popBackStack()
        }
    }

    ReAuthEffect(
        requiresReAuth = state.requiresReAuth,
        navController = navController,
        onDismiss = { viewModel.clearError() }
    )

    ProfileEditScreen(
        state = state,
        onFirstNameChange = viewModel::onFirstNameChanged,
        onLastNameChange = viewModel::onLastNameChanged,
        onSave = viewModel::save,
        onNavigateBack = { navController.popBackStack() }
    )
}
```

### Screen Structure
```kotlin
@Composable
fun ProfileEditScreen(
    state: ProfileEditState,
    onFirstNameChange: (String) -> Unit,
    onLastNameChange: (String) -> Unit,
    onSave: () -> Unit,
    onNavigateBack: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Theme.surface())
            .windowInsetsPadding(WindowInsets.safeDrawing)
    ) {
        // Top Bar with Save action
        EditTopBar(
            title = "Edit Profile",
            onNavigateBack = onNavigateBack,
            onSave = onSave,
            isSaving = state.isSaving,
            canSave = state.hasChanges && !state.isSaving
        )

        if (state.isLoading) {
            LoadingState()
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Form fields
                HopInOutlinedTextField(
                    value = state.firstName,
                    onValueChange = onFirstNameChange,
                    label = "First Name"
                )
                HopInOutlinedTextField(
                    value = state.lastName,
                    onValueChange = onLastNameChange,
                    label = "Last Name"
                )
                // ... more fields
            }
        }
    }
}
```

## Settings Screen

Displays grouped settings with toggles and navigation items.

### State
```kotlin
data class SettingsState(
    val isLoading: Boolean = false,
    val darkModeEnabled: Boolean = false,
    val notificationsEnabled: Boolean = true,
    val appVersion: String = "1.0.0",
    val buildNumber: String = "1",
    val errorMessage: String? = null
)
```

### Screen Structure
```kotlin
@Composable
fun SettingsScreen(
    state: SettingsState,
    onNavigateBack: () -> Unit,
    onDarkModeChanged: (Boolean) -> Unit,
    onNotificationsEnabledChanged: (Boolean) -> Unit,
    onPrivacyPolicyClick: () -> Unit,
    onTermsOfServiceClick: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Theme.surface())
            .windowInsetsPadding(WindowInsets.safeDrawing)
    ) {
        SettingsTopBar(onNavigateBack = onNavigateBack)

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Grouped settings sections
            SettingsSection(title = "Appearance") {
                ToggleSetting(
                    icon = Icons.Default.DarkMode,
                    title = "Dark Mode",
                    subtitle = "Use dark theme",
                    isEnabled = state.darkModeEnabled,
                    onToggle = onDarkModeChanged
                )
            }

            SettingsSection(title = "Legal") {
                NavigationSetting(
                    icon = Icons.Default.Policy,
                    title = "Privacy Policy",
                    onClick = onPrivacyPolicyClick
                )
            }

            SettingsSection(title = "About") {
                AboutItem(
                    icon = Icons.Default.Info,
                    title = "Version",
                    value = "${state.appVersion} (${state.buildNumber})"
                )
            }
        }
    }
}

@Composable
private fun SettingsSection(
    title: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        BasicText(
            text = title,
            style = TextStyle(
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                color = Theme.foregroundMuted()
            ),
            modifier = Modifier.padding(start = 4.dp)
        )
        HopInOutlinedCard {
            Column(
                modifier = Modifier.fillMaxWidth(),
                content = content
            )
        }
    }
}
```

## Create Screen

Creates a new entity. Similar to Edit but starts with empty state.

### State
```kotlin
data class OrganizationCreateState(
    val isLoading: Boolean = false,
    val isSaving: Boolean = false,
    val errorMessage: String? = null,
    val requiresReAuth: Boolean = false,
    val createSuccess: Boolean = false,
    val createdId: String? = null,
    // Form fields
    val name: String = "",
    val description: String = "",
    // Validation
    val isValid: Boolean = false
)
```

### Route with Create Success Navigation
```kotlin
@Composable
fun OrganizationCreateRoute(
    navController: NavHostController,
    viewModel: OrganizationCreateViewModel = koinViewModel()
) {
    val state by viewModel.state.collectAsState()

    // Navigate to detail on successful creation
    LaunchedEffect(state.createSuccess, state.createdId) {
        if (state.createSuccess && state.createdId != null) {
            viewModel.clearCreateSuccess()
            navController.popBackStack()
            navController.navigate(OrganizationDetailRoute(state.createdId))
        }
    }

    ReAuthEffect(
        requiresReAuth = state.requiresReAuth,
        navController = navController,
        onDismiss = { viewModel.clearError() }
    )

    OrganizationCreateScreen(
        state = state,
        onNameChange = viewModel::onNameChanged,
        onDescriptionChange = viewModel::onDescriptionChanged,
        onCreate = viewModel::create,
        onNavigateBack = { navController.popBackStack() }
    )
}
```

### ViewModel
```kotlin
class OrganizationCreateViewModel(
    private val repository: OrganizationsRepository
) : ViewModel() {

    private val _state = MutableStateFlow(OrganizationCreateState())
    val state: StateFlow<OrganizationCreateState> = _state.asStateFlow()

    fun onNameChanged(name: String) {
        _state.update {
            it.copy(
                name = name,
                isValid = name.isNotBlank()
            )
        }
    }

    fun onDescriptionChanged(description: String) {
        _state.update { it.copy(description = description) }
    }

    fun create() {
        val current = _state.value
        if (!current.isValid) return

        viewModelScope.launch {
            _state.update { it.copy(isSaving = true, errorMessage = null) }
            when (val result = repository.create(current.name, current.description)) {
                is ApiResult.Success -> {
                    _state.update {
                        it.copy(
                            isSaving = false,
                            createSuccess = true,
                            createdId = result.data.id
                        )
                    }
                }
                is ApiResult.Error -> {
                    _state.update {
                        it.copy(
                            isSaving = false,
                            errorMessage = result.displayMessage,
                            requiresReAuth = result.isUnauthorized
                        )
                    }
                }
            }
        }
    }

    fun clearCreateSuccess() {
        _state.update { it.copy(createSuccess = false, createdId = null) }
    }

    fun clearError() {
        _state.update { it.copy(errorMessage = null, requiresReAuth = false) }
    }
}
```
