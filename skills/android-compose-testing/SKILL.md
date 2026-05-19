---
name: android-compose-testing
description: Automate testing and UI verification for Kotlin Compose Multiplatform Android apps using ADB and Android emulator. Use when the user wants to test Android UI, verify that UI changes look good, validate screen workflows, interact with the hopinsports app, or check Compose screens. Triggers include phrases like "test my Android app", "verify the UI", "check if the compose screen", "validate that UI changes look good", or anything related to testing UI on Android emulator.
---

# Android Compose Multiplatform Testing

Automate testing and UI verification for the hopinsports Kotlin Compose Multiplatform app via ADB commands.

## Overview

This skill enables you to:
- Build and install the Android app
- Launch and navigate through screens
- Take screenshots for visual verification
- Find and tap UI elements intelligently
- Capture and analyze crash logs
- Verify UI changes after code modifications

## Core Testing Workflow

The typical workflow is: **Make code change → Reinstall → Verify the change looks correct on screen**

### Pre-flight Check

Always start by verifying the emulator is connected:

```bash
adb devices
```

Expected output should show a device in "device" state (not "offline" or "unauthorized").

### Build and Install

Navigate to project root and install:

```bash
cd /Users/briankennedy/projects/hopinsports
./gradlew :composeApp:installDebug
```

**If build fails:** Report the error and stop. Do not guess at fixes.

### Launch App

```bash
adb shell am start -n com.hopinsports/.MainActivity
```

### Navigate and Verify UI

Follow this interaction pattern:

#### 1. Take Screenshot First

Before any tap or verification:

```bash
adb exec-out screencap -p > /tmp/hopinsports.png
```

Then view the screenshot to understand the current screen state.

#### 2. Analyze the Screenshot

- **Main agent analysis:** Describe what you see on screen, verify expected elements are present
- **Sub-agent analysis:** If detailed verification needed, spawn a sub-agent with context about what's expected and have it analyze the screenshot

#### 3. Find UI Elements (when tapping)

If you need to tap an element:

**a) Dump UI hierarchy:**
```bash
adb shell uiautomator dump /sdcard/ui.xml
adb pull /sdcard/ui.xml /tmp/ui.xml
```

**b) Parse to find element:**
```bash
python3 /Users/briankennedy/.claude/skills/android-compose-testing/scripts/parse_ui_hierarchy.py /tmp/ui.xml text "Login"
```

The script outputs JSON with tap coordinates.

**c) If multiple elements match:** Filter by additional attributes:
```bash
# Find only clickable buttons (not headers/labels)
python3 /Users/briankennedy/.claude/skills/android-compose-testing/scripts/parse_ui_hierarchy.py /tmp/ui.xml text "Sign in" | jq '.[] | select(.clickable == true)'

# Find by class type
python3 /Users/briankennedy/.claude/skills/android-compose-testing/scripts/parse_ui_hierarchy.py /tmp/ui.xml class "android.widget.Button"

# When multiple results, prefer:
# - Lower Y coordinate = higher on screen (headers)
# - Higher Y coordinate = lower on screen (buttons in forms)
# - clickable: true = interactive elements
```

**d) If still ambiguous:** Ask the user which element to tap, or take a screenshot and mark options

**e) Tap the element:**
```bash
adb shell input tap <x> <y>
```

#### 4. Enter Text (if needed)

```bash
# Simple text (no special chars)
adb shell input text "username"

# Text with spaces - use %s
adb shell input text "hello%sworld"

# Text with special characters (@, #, $, etc.) - wrap in double quotes with single quotes inside
adb shell "input text '@Example_123'"
adb shell "input text 'user@email.com'"
```

**Special character escaping:**
- Spaces: Use `%s`
- `@`, `#`, `$`, `!`, etc.: Wrap entire command in double quotes, text in single quotes

#### 5. Clear Text Field (before re-entering)

```bash
# Select all and delete (Ctrl+A then Delete)
adb shell input keyevent KEYCODE_CTRL_A && adb shell input keyevent KEYCODE_DEL

# Or long-press delete to clear (slower but reliable)
adb shell input keyevent --longpress KEYCODE_DEL KEYCODE_DEL KEYCODE_DEL KEYCODE_DEL KEYCODE_DEL
```

### Crash Handling

If the app crashes or hangs:

**1. Capture logs automatically:**
```bash
scripts/capture_crash_logs.sh /tmp/crash_$(date +%s).log
```

**2. Analyze the logs:**
- Look for `FATAL`, `Exception`, or `AndroidRuntime` errors
- Identify the stack trace and exception type
- Note the file and line number where crash occurred

**3. Report findings:**
- Summarize the exception type and message
- Show the relevant stack trace
- Guess why the exception occurred based on the code path

**4. If you cannot solve:** Stop and report the issue with your analysis

### Typical Test Scenarios

#### Scenario 1: Verify Screen Appears After Action

```bash
# 1. Take screenshot before
adb exec-out screencap -p > /tmp/before.png

# 2. Perform action (e.g., tap button)
adb shell uiautomator dump /sdcard/ui.xml
adb pull /sdcard/ui.xml /tmp/ui.xml
python3 scripts/parse_ui_hierarchy.py /tmp/ui.xml text "Continue"
adb shell input tap <x> <y>

# 3. Wait a moment
sleep 2

# 4. Take screenshot after
adb exec-out screencap -p > /tmp/after.png

# 5. Analyze the after screenshot
```

#### Scenario 2: Verify Code Change

```bash
# 1. Build and install
cd /Users/briankennedy/projects/hopinsports
./gradlew :composeApp:installDebug

# 2. Launch app
adb shell am start -n com.hopinsports/.MainActivity

# 3. Navigate to the changed screen
# (tap sequence based on UI hierarchy)

# 4. Take screenshot
adb exec-out screencap -p > /tmp/verification.png

# 5. Analyze screenshot to verify change
```

#### Scenario 3: Multi-step Flow Verification

```bash
# For each step in the flow:
# 1. Take screenshot
# 2. Verify expected state
# 3. Find and tap next action
# 4. Repeat

# Example: Login flow
# Step 1: Verify login screen
adb exec-out screencap -p > /tmp/login_screen.png

# Step 2: Enter credentials
adb shell uiautomator dump /sdcard/ui.xml
adb pull /sdcard/ui.xml /tmp/ui.xml
python3 scripts/parse_ui_hierarchy.py /tmp/ui.xml resource_id "username"
adb shell input tap <x> <y>
adb shell input text "testuser"

# Step 3: Tap login button
python3 scripts/parse_ui_hierarchy.py /tmp/ui.xml text "Login"
adb shell input tap <x> <y>

# Step 4: Verify next screen
sleep 2
adb exec-out screencap -p > /tmp/after_login.png
```

## Screenshot Analysis Guidelines

When analyzing screenshots:

1. **Describe what you see:** Layout, colors, text, buttons, images
2. **Verify expected elements:** Are the components you expect visible?
3. **Check for errors:** Error messages, missing content, broken layouts
4. **Assess visual quality:** Does it look polished and correct?
5. **Compare to expectations:** Does it match what the code change should produce?

Use sub-agents when:
- Detailed comparison needed (before/after screenshots)
- Multiple verification points
- Complex screen with many elements to check

## Reporting Results

Always include:
- **Installed:** yes/no (with any error messages)
- **Launched:** yes/no
- **Taps performed:** count and what was tapped
- **Screenshot paths:** where screenshots were saved
- **Verification result:** what you observed vs what was expected
- **Log highlights:** any warnings/errors from logcat (if captured)

## Reference Files

- **commands.md:** Detailed command reference with examples
- **parse_ui_hierarchy.py:** Find UI elements in hierarchy XML
- **capture_crash_logs.sh:** Capture and filter logcat for crashes

## Platform Notes

- **macOS ARM:** All commands compatible
- **Emulator:** Typically already running (user manages it)
- **Package:** `com.hopinsports`
- **Project root:** `/Users/briankennedy/projects/hopinsports`

## Error Handling Philosophy

1. **Build failures:** Report and stop
2. **App crashes:** Capture logs, analyze, report, guess cause
3. **UI element not found:** Ask user or show screenshot with options
4. **Ambiguous interactions:** Screenshot first, ask for clarification
