# Android Testing Commands Reference

**Project Details:**
- Root: `/Users/briankennedy/projects/hopinsports`
- Package: `com.hopinsports`
- Main Activity: `com.hopinsports/.MainActivity`
- Platform: macOS ARM

---

## 1. List Available Emulators

```bash
emulator -list-avds
```

**Example output:**
```
Pixel_9_API_36
Pixel_7_API_33
```

---

## 2. Start Emulator

```bash
emulator -avd Pixel_9_API_36
```

**Example output (first lines):**
```
INFO    | Android emulator version 36.0.0.0
INFO    | Boot completed in 15234 ms
```

**Note:** User typically has emulator already running

---

## 3. Check Device Connection

```bash
adb devices
```

**Example output:**
```
List of devices attached
emulator-5554    device
```

**Usage:** Always verify emulator is running before install/test operations

---

## 4. Build and Install Debug APK

```bash
cd /Users/briankennedy/projects/hopinsports
./gradlew :composeApp:installDebug
```

**Example output (tail):**
```
> Task :composeApp:installDebug
Installed on 1 device.
```

**Error handling:** If fails, report error and stop. Do not guess fixes.

---

## 5. Launch the App

```bash
adb shell am start -n com.hopinsports/.MainActivity
```

**Example output:**
```
Starting: Intent { cmp=com.hopinsports/.MainActivity }
```

---

## 6. View UI Hierarchy

**Dump UI hierarchy to device:**
```bash
adb shell uiautomator dump /sdcard/ui.xml
```

**Example output:**
```
UI hierchary dumped to: /sdcard/ui.xml
```

**Pull to local machine:**
```bash
adb pull /sdcard/ui.xml /tmp/ui.xml
```

**Example output:**
```
/sdcard/ui.xml: 1 file pulled. 0.3 MB/s (18920 bytes in 0.061s)
```

**Usage:** Use this to find tap targets before tapping. Parse with the skill's parse script:

```bash
python3 /Users/briankennedy/.claude/skills/android-compose-testing/scripts/parse_ui_hierarchy.py /tmp/ui.xml text "Login"
```

**Handling duplicate matches:** When multiple elements have the same text (e.g., "Sign in" header and button):
- Filter by `clickable: true` for interactive elements
- Use Y coordinate: lower Y = higher on screen (headers), higher Y = lower (form buttons)
- Filter by class: `android.widget.Button` vs `android.widget.TextView`

---

## 7. Tap on Screen Coordinates

```bash
adb shell input tap 540 1200
```

**Example output:** (no output on success)

**Usage:** Get coordinates from UI hierarchy or user confirmation

---

## 8. Enter Text

```bash
# Simple text
adb shell input text "testuser"

# Text with spaces - use %s
adb shell input text "test%swriter"

# Text with special characters (@, #, $, !, etc.)
adb shell "input text '@Example_123'"
adb shell "input text 'user@email.com'"
```

**Special character escaping:**
- Spaces: Use `%s`
- `@`, `#`, `$`, `!`, etc.: Wrap command in double quotes, text in single quotes

**Example output:** (no output on success)

---

## 8b. Clear Text Field

```bash
# Select all and delete
adb shell input keyevent KEYCODE_CTRL_A && adb shell input keyevent KEYCODE_DEL
```

**Example output:** (no output on success)

**Usage:** Clear a text field before entering new text (e.g., correcting a typo)

---

## 9. Take Screenshot

```bash
adb exec-out screencap -p > /tmp/hopinsports.png
```

**Example output:** (no output; file written)

**Usage:** Take screenshot for visual verification or before ambiguous taps

---

## 10. Capture App Logs

**Get app PID:**
```bash
adb shell pidof -s com.hopinsports
```

**Example output:**
```
12345
```

**Capture logs for PID:**
```bash
adb logcat --pid=12345
```

**Example output (sample):**
```
10-20 12:44:01.123 12345 12345 I hopinsports: App started
10-20 12:44:02.456 12345 12345 D hopinsports: Loaded schedule list
```

**For crashes:** Use `scripts/capture_crash_logs.sh` to automatically capture relevant logs

---

## 11. Stop App

```bash
adb shell am force-stop com.hopinsports
```

**Example output:** (no output on success)

**Usage:** Optional cleanup or to restart the app fresh

---

## Testing Workflow Rules

1. **Always verify emulator is running** via `adb devices` before install
2. **If installDebug fails**, report error; do not guess fixes
3. **Take screenshots** for visual verification or before ambiguous element interactions
4. **Capture logs automatically** when crashes occur
5. **Report results** including: installed (yes/no), launched (yes/no), taps performed (count), screenshot path, and log highlights
