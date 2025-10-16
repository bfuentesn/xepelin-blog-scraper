#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🎭 Installing Playwright and Chromium..."
playwright install --with-deps chromium

echo "✅ Build completed successfully!"
