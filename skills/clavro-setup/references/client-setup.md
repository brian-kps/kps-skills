# Client SDK Setup

## URL Configuration

### Resource Strings (`composeApp/src/commonMain/composeResources/values/strings.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="vault_key_host">your-instance-url.clavro.org</string>
</resources>
```

Replace `your-instance-url.clavro.org` with actual Clavro instance host (without `https://`).

## Android Setup

### MainActivity (`composeApp/src/androidMain/kotlin/.../MainActivity.kt`)

```kotlin
import org.clavro.sdk.compose.ClavroProvider
import <package>.composeapp.generated.resources.Res
import <package>.composeapp.generated.resources.vault_key_host
import org.jetbrains.compose.resources.stringResource

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ClavroProvider(
                instanceUrl = "https://${stringResource(Res.string.vault_key_host)}",
                redirectUriScheme = "example://",
                context = applicationContext
            ) {
                App()
            }
        }
    }
}
```

### Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `instanceUrl` | Full Clavro URL with `https://` prefix | Yes |
| `redirectUriScheme` | OAuth redirect scheme (e.g., `myapp://`) | Yes |
| `context` | Android application context | Android only |

## iOS Setup

### MainViewController (`composeApp/src/iosMain/kotlin/.../MainViewController.kt`)

```kotlin
import org.clavro.sdk.compose.ClavroProvider
import <package>.composeapp.generated.resources.Res
import <package>.composeapp.generated.resources.vault_key_host
import org.jetbrains.compose.resources.stringResource

fun MainViewController() = ComposeUIViewController {
    ClavroProvider(
        instanceUrl = "https://${stringResource(Res.string.vault_key_host)}",
        redirectUriScheme = "example://"
    ) {
        App()
    }
}
```

**Note:** iOS does not require the `context` parameter.
