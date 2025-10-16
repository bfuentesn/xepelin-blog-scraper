"""
Flask API for Xepelin Blog Scraper
Provides endpoint to scrape blog posts and send results to webhook
"""

from flask import Flask, request, jsonify
import requests
import threading
import os
from dotenv import load_dotenv
from scraper_playwright import XepelinPlaywrightScraper
from sheets_manager import GoogleSheetsManager

# Load environment variables
load_dotenv()

# Set Playwright browser path for Render deployment
if os.path.exists('/opt/render'):
    # Running on Render - set browser path
    browser_cache_path = '/opt/render/.cache/ms-playwright'
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browser_cache_path
    
    # Check if Chromium is installed, if not install it at runtime
    chromium_path = os.path.join(browser_cache_path, 'chromium-1091', 'chrome-linux', 'chrome')
    
    if not os.path.exists(chromium_path):
        print("\n" + "="*60)
        print("⚠️  Chromium not found - Installing at runtime...")
        print(f"Expected path: {chromium_path}")
        print("="*60 + "\n")
        
        try:
            import subprocess
            
            # Create cache directory
            os.makedirs(browser_cache_path, exist_ok=True)
            print(f"📁 Created cache directory: {browser_cache_path}")
            
            # Install Chromium (this will take ~2 minutes on first startup)
            print("⬇️  Downloading Chromium (153 MB)...")
            print("⏳ This will take about 2 minutes on first startup...")
            
            result = subprocess.run(
                ['python', '-m', 'playwright', 'install', 'chromium'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                print("✅ Chromium installed successfully at runtime!")
                print(f"📍 Browser path: {browser_cache_path}")
            else:
                print(f"❌ Failed to install Chromium:")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
        
        except Exception as e:
            print(f"❌ Error installing Chromium at runtime: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"✅ Chromium already installed at: {chromium_path}")

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Support Spanish characters


def process_scraping_job(category: str, webhook_url: str, email: str, 
                         scrape_all: bool = False, sheet_url: str = None):
    """
    Background job to scrape blog and send results to webhook
    
    Args:
        category: Category to scrape
        webhook_url: URL to send results
        email: Email for webhook response
        scrape_all: Whether to scrape all categories
        sheet_url: Optional Google Sheet URL to use (instead of creating new one)
    """
    try:
        print(f"\n{'='*60}")
        print(f"Starting scraping job")
        print(f"Category: {category if not scrape_all else 'ALL CATEGORIES'}")
        print(f"Webhook: {webhook_url}")
        print(f"Email: {email}")
        print(f"{'='*60}\n")
        
        # Initialize sheets manager
        print("📊 Initializing Google Sheets manager...")
        sheets_manager = GoogleSheetsManager()
        print("✅ Google Sheets manager initialized")
        
        # Scrape blog posts with Playwright
        print("🎭 Initializing Playwright scraper...")
        with XepelinPlaywrightScraper() as scraper:
            print("✅ Playwright scraper initialized")
            if scrape_all:
                print("Scraping all categories...")
                categories_data = scraper.scrape_all_categories()
                
                if not categories_data:
                    print("No data scraped!")
                    send_webhook_response(webhook_url, email, None, 
                                        error="No se pudieron extraer datos del blog")
                    return
                
                # Write to Google Sheets
                result_sheet_url = sheets_manager.write_multiple_categories(categories_data, sheet_url)
            else:
                print(f"Scraping category: {category}")
                posts = scraper.scrape_category(category)
                
                if not posts:
                    print(f"No posts found for category: {category}")
                    send_webhook_response(webhook_url, email, None, 
                                        error=f"No se encontraron posts en la categoría '{category}'")
                    return
                
                # Write to Google Sheets - single category as dict
                result_sheet_url = sheets_manager.write_multiple_categories({category: posts}, sheet_url)
        
        # Send success response to webhook
        print(f"\n{'='*60}")
        print(f"✅ SCRAPING COMPLETED SUCCESSFULLY!")
        print(f"📊 Google Sheet URL: {result_sheet_url}")
        print(f"📧 Sending webhook response...")
        print(f"{'='*60}\n")
        send_webhook_response(webhook_url, email, result_sheet_url)
    
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ ERROR IN SCRAPING JOB")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()
        send_webhook_response(webhook_url, email, None, error=str(e))


def send_webhook_response(webhook_url: str, email: str, sheet_url: str = None, 
                         error: str = None):
    """
    Send response to webhook with results
    
    Args:
        webhook_url: Webhook URL to send response
        email: Email address
        sheet_url: Google Sheets URL with results
        error: Error message if any
    """
    try:
        payload = {
            "email": email,
            "link": sheet_url if sheet_url else "Error - No data available"
        }
        
        if error:
            payload["error"] = error
            payload["status"] = "failed"
        else:
            payload["status"] = "success"
        
        print(f"\nSending response to webhook: {webhook_url}")
        print(f"Payload: {payload}")
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        response.raise_for_status()
        print(f"Webhook response sent successfully! Status: {response.status_code}")
    
    except requests.RequestException as e:
        print(f"Error sending webhook response: {e}")


@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "Xepelin Blog Scraper API",
        "version": "1.0",
        "endpoints": {
            "/scrape": {
                "method": "POST",
                "description": "Scrape blog posts from a category",
                "required_parameters": {
                    "categoria": "Category name (e.g., 'Pymes', 'Noticias', 'Corporativos')",
                    "webhook": "Webhook URL to receive results"
                }
            },
            "/categories": {
                "method": "GET",
                "description": "Get list of available categories"
            },
            "/test-playwright": {
                "method": "GET",
                "description": "Test if Playwright is working correctly"
            },
            "/health": {
                "method": "GET",
                "description": "Health check endpoint"
            }
        },
        "example": {
            "curl": """curl -X POST 'https://xepelin-blog-scraper-0af5.onrender.com/scrape' \\
  -H 'Content-Type: application/json' \\
  -d '{"categoria":"Noticias","webhook":"https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"}'"""
        }
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "API is running"
    }), 200


@app.route('/test-playwright', methods=['GET'])
def test_playwright():
    """Test if Playwright is working"""
    try:
        from playwright.sync_api import sync_playwright
        
        print("Testing Playwright installation...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://example.com", timeout=30000)
            title = page.title()
            browser.close()
        
        return jsonify({
            "status": "success",
            "message": "Playwright is working correctly",
            "test_page_title": title
        }), 200
    
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": "Playwright test failed",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/categories', methods=['GET'])
def get_categories():
    """Get available blog categories"""
    categories = list(XepelinPlaywrightScraper.CATEGORIES.keys())
    
    return jsonify({
        "categories": categories,
        "count": len(categories)
    }), 200


@app.route('/scrape', methods=['POST'])
def scrape_blog():
    """
    Main endpoint to scrape blog posts
    
    Expected JSON body:
    {
        "categoria": "Category name" (required if not scrape_all),
        "webhook": "Webhook URL" (required),
        "scrape_all": true/false (optional, default: false)
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Check for required parameters
        webhook_url = data.get('webhook')
        scrape_all = data.get('scrape_all', False)
        
        if not webhook_url:
            return jsonify({
                "error": "Missing required parameter: 'webhook'"
            }), 400
        
        # Category is required unless scrape_all is true
        if scrape_all:
            categoria = "all"
        else:
            categoria = data.get('categoria')
            if not categoria:
                return jsonify({
                    "error": "Missing required parameter: 'categoria' (or set 'scrape_all': true)"
                }), 400
            
            # Validate category
            available_categories = list(XepelinPlaywrightScraper.CATEGORIES.keys())
            
            if categoria not in available_categories:
                return jsonify({
                    "error": f"Invalid category: '{categoria}'",
                    "available_categories": available_categories
                }), 400
        
        # Use default email from environment
        email = os.getenv('YOUR_EMAIL', 'benjamin.fuentes@uc.cl')
        
        # Use default sheet URL (will be overwritten each time)
        sheet_url = "https://docs.google.com/spreadsheets/d/17JhWF2_3DMt_jRllzKQp7DuKNcHGfYDJ6u5DeBsYHR8/"
        
        # Start background job
        thread = threading.Thread(
            target=process_scraping_job,
            args=(categoria, webhook_url, email, scrape_all, sheet_url)
        )
        thread.daemon = True
        thread.start()
        
        # Return immediate response
        response = {
            "status": "accepted",
            "message": "Scraping job started. Results will be sent to webhook when complete.",
            "webhook": webhook_url
        }
        
        if scrape_all:
            response["mode"] = "all_categories"
            response["info"] = "Scraping all 6 categories (654 posts total, ~25 min)"
        else:
            response["categoria"] = categoria
        
        return jsonify(response), 202
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": "Use GET / to see available endpoints"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500


if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print("\n" + "="*60)
    print("Xepelin Blog Scraper API")
    print("="*60)
    print(f"Starting server on {host}:{port}")
    print(f"Debug mode: {debug}")
    print("="*60 + "\n")
    
    app.run(host=host, port=port, debug=debug)
