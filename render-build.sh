#!/usr/bin/env bash
# Exit on error
set -e

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "� Creating Playwright cache directory..."
mkdir -p /opt/render/.cache/ms-playwright

echo "�🗑️  Cleaning old Playwright cache..."
rm -rf /opt/render/.cache/ms-playwright/* 2>/dev/null || true

echo "🎭 Installing Playwright with Chromium..."
echo "📍 Browser path: ${PLAYWRIGHT_BROWSERS_PATH:-/opt/render/.cache/ms-playwright}"

# Install chromium browser - usa la variable de entorno de Render
echo "Downloading Chromium browser..."
python -m playwright install chromium --with-deps

echo "📋 Verifying Chromium installation..."
echo "Checking cache directory..."
ls -la /opt/render/.cache/ 2>/dev/null || echo "⚠️  Cache directory doesn't exist"
ls -la /opt/render/.cache/ms-playwright/ 2>/dev/null || echo "⚠️  Playwright cache doesn't exist"

# Buscar chromium en cualquier ubicación
CHROMIUM_DIR=$(find /opt/render/.cache/ms-playwright -type d -name "chromium-*" 2>/dev/null | head -n 1)

if [ -n "$CHROMIUM_DIR" ]; then
    echo "✅ Chromium found at: $CHROMIUM_DIR"
    ls -la "$CHROMIUM_DIR/"
    echo "✅ Build completed successfully!"
else
    echo "❌ ERROR: Chromium NOT installed!"
    echo "Contents of /opt/render/.cache/:"
    ls -laR /opt/render/.cache/ 2>/dev/null || echo "Directory not accessible"
    exit 1
fi
