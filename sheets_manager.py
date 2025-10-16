"""
Google Sheets integration for storing scraped blog data
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict
import json
import os
from datetime import datetime


class GoogleSheetsManager:
    """Manages Google Sheets operations for blog data"""
    
    SCOPES = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    HEADERS = [
        'Titular',
        'Categoría',
        'Autor',
        'Tiempo de lectura',
        'Fecha de publicación',
        'URL'
    ]
    
    def __init__(self, credentials_json: str = None):
        """
        Initialize Google Sheets manager
        
        Args:
            credentials_json: JSON string with Google API credentials
                            or path to credentials file
        """
        self.credentials_json = credentials_json or os.getenv('GOOGLE_CREDENTIALS_JSON')
        self.client = None
        self._authorize()
    
    def _authorize(self):
        """Authorize with Google Sheets API"""
        try:
            if not self.credentials_json:
                raise ValueError("No Google credentials provided")
            
            # Check if it's a file path or JSON string
            if os.path.isfile(self.credentials_json):
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    self.credentials_json,
                    self.SCOPES
                )
            else:
                # Parse as JSON string
                creds_dict = json.loads(self.credentials_json)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(
                    creds_dict,
                    self.SCOPES
                )
            
            self.client = gspread.authorize(creds)
            print("Successfully authorized with Google Sheets API")
        
        except Exception as e:
            print(f"Error authorizing with Google Sheets: {e}")
            raise
    
    def create_spreadsheet(self, title: str = None) -> str:
        """
        Create a new Google Spreadsheet
        
        Args:
            title: Spreadsheet title
        
        Returns:
            Spreadsheet URL
        """
        if not title:
            title = f"Xepelin Blog Data - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            spreadsheet = self.client.create(title)
            
            # Make it publicly readable
            spreadsheet.share('', perm_type='anyone', role='reader')
            
            url = spreadsheet.url
            print(f"Created spreadsheet: {url}")
            
            return url
        
        except Exception as e:
            print(f"Error creating spreadsheet: {e}")
            raise
    
    def write_data(self, posts: List[Dict[str, str]], spreadsheet_url: str = None, 
                   sheet_title: str = "Blog Posts") -> str:
        """
        Write blog post data to Google Sheet
        
        Args:
            posts: List of blog post dictionaries
            spreadsheet_url: URL of existing spreadsheet (creates new if None)
            sheet_title: Name of the worksheet
        
        Returns:
            Spreadsheet URL (cleaned)
        """
        try:
            # Create or open spreadsheet
            if spreadsheet_url:
                spreadsheet = self.client.open_by_url(spreadsheet_url)
                
                # Delete ALL existing worksheets except the first one
                # This ensures only the new category data is present
                existing_worksheets = spreadsheet.worksheets()
                if len(existing_worksheets) > 1:
                    for ws in existing_worksheets[1:]:
                        try:
                            spreadsheet.del_worksheet(ws)
                            print(f"Deleted old worksheet: {ws.title}")
                        except:
                            pass
            else:
                spreadsheet_url = self.create_spreadsheet()
                spreadsheet = self.client.open_by_url(spreadsheet_url)
            
            # Get or create worksheet
            try:
                worksheet = spreadsheet.worksheet(sheet_title)
                worksheet.clear()  # Clear existing data
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=sheet_title, rows=1000, cols=10)
            
            # Prepare data
            data = [self.HEADERS]
            
            for post in posts:
                row = [
                    post.get('Titular', 'N/A'),
                    post.get('Categoría', 'N/A'),
                    post.get('Autor', 'N/A'),
                    post.get('Tiempo de lectura', 'N/A'),
                    post.get('Fecha de publicación', 'N/A'),
                    post.get('URL', 'N/A')
                ]
                data.append(row)
            
            # Write to sheet
            worksheet.update('A1', data)
            
            # Format header row
            worksheet.format('A1:F1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.86}
            })
            
            # Auto-resize columns
            worksheet.columns_auto_resize(0, 5)
            
            # Clean URL (remove /edit#gid=... part)
            clean_url = self._clean_sheet_url(spreadsheet.url)
            
            print(f"Successfully wrote {len(posts)} posts to Google Sheet")
            print(f"Sheet URL: {clean_url}")
            
            return clean_url
        
        except Exception as e:
            print(f"Error writing to Google Sheet: {e}")
            raise
    
    def write_multiple_categories(self, categories_data: Dict[str, List[Dict[str, str]]],
                                  spreadsheet_url: str = None) -> str:
        """
        Write multiple categories to different worksheets
        
        Args:
            categories_data: Dictionary mapping category names to lists of posts
            spreadsheet_url: URL of existing spreadsheet (creates new if None)
        
        Returns:
            Spreadsheet URL (cleaned)
        """
        try:
            # Create or open spreadsheet
            if spreadsheet_url:
                spreadsheet = self.client.open_by_url(spreadsheet_url)
            else:
                title = f"Xepelin Blog - All Categories - {datetime.now().strftime('%Y-%m-%d')}"
                spreadsheet_url = self.create_spreadsheet(title)
                spreadsheet = self.client.open_by_url(spreadsheet_url)
            
            # Primero: Obtener lista de hojas existentes ANTES de escribir
            existing_sheets_before = {ws.title for ws in spreadsheet.worksheets()}
            categories_to_write = set(categories_data.keys())
            
            # Write each category to its own sheet
            for category_name, posts in categories_data.items():
                if not posts:
                    continue
                
                sheet_title = category_name[:30]  # Google Sheets has 31 char limit
                
                print(f"Writing {len(posts)} posts for category: {category_name}")
                
                try:
                    worksheet = spreadsheet.worksheet(sheet_title)
                    worksheet.clear()
                except gspread.exceptions.WorksheetNotFound:
                    worksheet = spreadsheet.add_worksheet(
                        title=sheet_title,
                        rows=len(posts) + 10,
                        cols=10
                    )
                
                # Prepare data
                data = [self.HEADERS]
                for post in posts:
                    row = [
                        post.get('Titular', 'N/A'),
                        post.get('Categoría', 'N/A'),
                        post.get('Autor', 'N/A'),
                        post.get('Tiempo de lectura', 'N/A'),
                        post.get('Fecha de publicación', 'N/A'),
                        post.get('URL', 'N/A')
                    ]
                    data.append(row)
                
                # Write to sheet
                worksheet.update('A1', data)
                
                # Format header
                worksheet.format('A1:F1', {
                    'textFormat': {'bold': True},
                    'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.86}
                })
                
                worksheet.columns_auto_resize(0, 5)
            
            # Borrar hojas que NO están en las categorías escritas
            # Esto asegura que solo queden las hojas solicitadas
            try:
                all_worksheets = spreadsheet.worksheets()
                sheets_to_keep = {cat[:30] for cat in categories_to_write}  # Truncar a 30 chars
                
                for ws in all_worksheets:
                    # Borrar si NO está en las categorías a mantener
                    if ws.title not in sheets_to_keep:
                        try:
                            spreadsheet.del_worksheet(ws)
                            print(f"Deleted old worksheet: {ws.title}")
                        except Exception as e:
                            # Ignorar error si es la última hoja (Google no permite borrar todas)
                            if "can't remove all the sheets" not in str(e).lower():
                                print(f"Warning: Could not delete {ws.title}: {e}")
            except Exception as e:
                print(f"Warning: Could not clean up worksheets: {e}")
            
            clean_url = self._clean_sheet_url(spreadsheet.url)
            print(f"Successfully wrote all categories to Google Sheet: {clean_url}")
            
            return clean_url
        
        except Exception as e:
            print(f"Error writing multiple categories: {e}")
            raise
    
    def _clean_sheet_url(self, url: str) -> str:
        """
        Clean Google Sheets URL by removing edit parameters
        
        Args:
            url: Full Google Sheets URL
        
        Returns:
            Cleaned URL
        """
        # Remove /edit#gid=... part
        if '/edit' in url:
            url = url.split('/edit')[0]
        
        return url


if __name__ == "__main__":
    # Test the Google Sheets manager
    print("Testing Google Sheets Manager...")
    
    # Sample data
    test_data = [
        {
            'Titular': 'Test Blog Post 1',
            'Categoría': 'Pymes',
            'Autor': 'John Doe',
            'Tiempo de lectura': '5 min',
            'Fecha de publicación': '2024-01-15',
            'URL': 'https://xepelin.com/blog/test-1'
        },
        {
            'Titular': 'Test Blog Post 2',
            'Categoría': 'Fintech',
            'Autor': 'Jane Smith',
            'Tiempo de lectura': '8 min',
            'Fecha de publicación': '2024-01-16',
            'URL': 'https://xepelin.com/blog/test-2'
        }
    ]
    
    try:
        manager = GoogleSheetsManager()
        url = manager.write_data(test_data)
        print(f"Test successful! Sheet URL: {url}")
    except Exception as e:
        print(f"Test failed: {e}")
        print("\nMake sure to:")
        print("1. Create a Google Cloud Project")
        print("2. Enable Google Sheets API and Google Drive API")
        print("3. Create a service account and download credentials JSON")
        print("4. Set GOOGLE_CREDENTIALS_JSON in .env file")
