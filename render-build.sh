#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🎭 Installing Playwright browsers..."
python -m playwright install chromium

echo "🔧 Installing system dependencies for Chromium..."
python -m playwright install-deps chromium

echo "✅ Build completed successfully!"
