#!/bin/bash
# Capture recent logcat logs for hopinsports app, especially around crashes
# Usage: capture_crash_logs.sh [output_file] [lines_before_crash]

OUTPUT_FILE="${1:-/tmp/hopinsports_crash.log}"
LINES="${2:-200}"
PACKAGE="com.hopinsports"

echo "Capturing logs for $PACKAGE..."

# Get the PID if app is still running
PID=$(adb shell pidof -s "$PACKAGE" 2>/dev/null)

if [ -n "$PID" ]; then
    echo "App is running with PID: $PID"
    # Capture logs for this specific PID
    adb logcat --pid="$PID" -d -t "$LINES" > "$OUTPUT_FILE"
else
    echo "App not running. Capturing all recent logs containing package name..."
    # App crashed/stopped, get recent logs mentioning the package
    adb logcat -d -t "$LINES" | grep -i "$PACKAGE" > "$OUTPUT_FILE"
    
    # If no grep results, get all recent logs
    if [ ! -s "$OUTPUT_FILE" ]; then
        echo "No package-specific logs found. Capturing all recent logs..."
        adb logcat -d -t "$LINES" > "$OUTPUT_FILE"
    fi
fi

# Also capture any fatal exceptions
FATAL_LOGS=$(mktemp)
adb logcat -d -t 500 | grep -E "(FATAL|AndroidRuntime|Exception|Error)" > "$FATAL_LOGS"

if [ -s "$FATAL_LOGS" ]; then
    echo -e "\n========== FATAL ERRORS/EXCEPTIONS ==========\n" >> "$OUTPUT_FILE"
    cat "$FATAL_LOGS" >> "$OUTPUT_FILE"
fi

rm -f "$FATAL_LOGS"

echo "Logs saved to: $OUTPUT_FILE"
echo "Total lines: $(wc -l < "$OUTPUT_FILE")"

# Print summary
if grep -q "FATAL" "$OUTPUT_FILE"; then
    echo "⚠️  FATAL errors detected in logs"
fi

if grep -q "Exception" "$OUTPUT_FILE"; then
    echo "⚠️  Exceptions detected in logs"
fi
