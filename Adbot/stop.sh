#!/bin/bash
# Stop the running bot

echo "Stopping bot instances..."
ps aux | grep -i "python.*main.py" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null

# Also check for session locks and clear them
cd "$(dirname "$0")"
rm -f assets/sessions/*.session-journal 2>/dev/null

echo "✓ Bot stopped (if it was running)"

