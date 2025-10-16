# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by Playwright/Chromium
RUN apt-get update && apt-get install -y \
    # Core libraries
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    # X11 libraries
    libx11-6 \
    libxcb1 \
    libxext6 \
    # GLib and GObject
    libglib2.0-0 \
    libgobject-2.0-0 \
    libgio-2.0-0 \
    # Additional
    libexpat1 \
    # Fonts
    fonts-liberation \
    fonts-noto-color-emoji \
    # Utilities
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and Chromium (skip install-deps since we already installed system deps)
RUN python -m playwright install chromium

# Copy application code
COPY . .

# Set environment variable for Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

# Set PORT for Railway
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "600", "app:app"]
