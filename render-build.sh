#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗑️  Cleaning old Playwright cache..."
rm -rf /opt/render/.cache/ms-playwright || true

echo "🎭 Installing Playwright browsers..."
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright
python -m playwright install chromium

echo "🔧 Installing system dependencies for Chromium..."
python -m playwright install-deps chromium

echo "📋 Verifying Chromium installation..."
ls -la /opt/render/.cache/ms-playwright/ || echo "Cache directory not found"

echo "✅ Build completed successfully!"
