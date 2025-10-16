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
        sheets_manager = GoogleSheetsManager()
        
        # Scrape blog posts with Playwright
        with XepelinPlaywrightScraper() as scraper:
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
        print(f"\nScraping completed successfully!")
        print(f"Google Sheet URL: {result_sheet_url}")
        send_webhook_response(webhook_url, email, result_sheet_url)
    
    except Exception as e:
        print(f"Error in scraping job: {e}")
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
                "parameters": {
                    "categoria": "Category name (e.g., 'Pymes y Negocios', 'Fintech')",
                    "webhook": "Webhook URL to receive results"
                },
                "optional_parameters": {
                    "email": "Email for webhook response (default from env)",
                    "sheet_url": "Existing Google Sheet URL to write data (creates new if not provided)",
                    "scrape_all": "Set to true to scrape all categories (bonus feature)"
                }
            },
            "/categories": {
                "method": "GET",
                "description": "Get list of available categories"
            },
            "/health": {
                "method": "GET",
                "description": "Health check endpoint"
            }
        },
        "example": {
            "curl": """curl -X POST 'http://YOUR_SERVER:5000/scrape' \\
  -H 'Content-Type: application/json' \\
  -d '{"categoria":"Pymes","webhook":"https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"}'"""
        }
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "API is running"
    }), 200


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
        "categoria": "Category name",
        "webhook": "Webhook URL",
        "email": "your@email.com" (optional),
        "sheet_url": "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/" (optional),
        "scrape_all": false (optional, bonus feature)
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
        if not scrape_all:
            category = data.get('categoria')
            if not category:
                return jsonify({
                    "error": "Missing required parameter: 'categoria' (or set 'scrape_all': true)"
                }), 400
        else:
            category = "all"
        
        # Get email (from request or environment)
        email = data.get('email', os.getenv('YOUR_EMAIL', 'benjamin.fuentes@uc.cl'))
        
        # Get optional sheet_url
        sheet_url = data.get('sheet_url')
        
        # Validate category if not scraping all
        if not scrape_all:
            available_categories = list(XepelinPlaywrightScraper.CATEGORIES.keys())
            
            # Check if category is valid (case insensitive)
            if category not in available_categories:
                return jsonify({
                    "error": f"Invalid category: '{category}'",
                    "available_categories": available_categories
                }), 400
        
        # Start background job
        thread = threading.Thread(
            target=process_scraping_job,
            args=(category, webhook_url, email, scrape_all, sheet_url)
        )
        thread.daemon = True
        thread.start()
        
        # Return immediate response
        response_data = {
            "status": "accepted",
            "message": "Scraping job started. Results will be sent to webhook when complete.",
            "webhook": webhook_url,
            "email": email
        }
        
        if scrape_all:
            response_data["mode"] = "all_categories"
            response_data["info"] = "Scraping all blog categories (bonus feature)"
        else:
            response_data["categoria"] = category
        
        if sheet_url:
            response_data["sheet_url"] = sheet_url
            response_data["note"] = "Using existing Google Sheet"
        
        return jsonify(response_data), 202
    
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
