#!/usr/bin/env bash
# Exit on error
set -e

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗑️  Cleaning old Playwright cache..."
rm -rf /opt/render/.cache/ms-playwright 2>/dev/null || true

echo "🎭 Installing Playwright with Chromium..."
# Set browser path BEFORE installing
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright

# Install chromium browser
echo "Downloading Chromium browser..."
python -m playwright install chromium

# Try to install system dependencies (may fail on Render, that's ok)
echo "🔧 Attempting to install system dependencies..."
python -m playwright install-deps chromium 2>/dev/null || echo "⚠️  Skipping system deps (may not have sudo)"

echo "📋 Verifying Chromium installation..."
if [ -d "/opt/render/.cache/ms-playwright/chromium-1091" ]; then
    echo "✅ Chromium found at: /opt/render/.cache/ms-playwright/chromium-1091"
    ls -la /opt/render/.cache/ms-playwright/chromium-1091/
else
    echo "❌ ERROR: Chromium NOT installed!"
    ls -la /opt/render/.cache/ms-playwright/ || echo "Cache directory not found"
    exit 1
fi

echo "✅ Build completed successfully!"
