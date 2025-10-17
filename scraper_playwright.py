#!/usr/bin/env python3
"""
Scraper con Playwright para obtener TODOS los posts del blog de Xepelin.
Requiere dependencias del sistema instaladas: sudo playwright install-deps
"""
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout


class XepelinPlaywrightScraper:
    """
    Scraper que usa Playwright para manejar carga dinámica del blog.
    Capaz de obtener TODOS los posts, incluyendo los cargados con el botón "Cargar más".
    """
    
    BASE_URL = "https://xepelin.com/blog"
    
    CATEGORIES = {
        "Pymes": "pymes",
        "Corporativos": "corporativos",
        "Educación Financiera": "educacion-financiera",
        "Emprendedores": "emprendedores",
        "Noticias": "noticias",
        "Casos de éxito": "empresarios-exitosos"
    }
    
    def __init__(self, headless: bool = True, timeout: int = 60000):
        """
        Inicializa el scraper con Playwright.
        
        Args:
            headless: Si True, ejecuta el navegador sin GUI
            timeout: Timeout en milisegundos para operaciones de página
        """
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    def __enter__(self):
        """Context manager para manejar el navegador."""
        import os
        
        # Verificar que Playwright puede encontrar los browsers
        browsers_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '/opt/render/.cache/ms-playwright')
        if os.path.exists(browsers_path):
            print(f"✅ Playwright browsers path exists: {browsers_path}")
            # Listar contenido para debug
            try:
                import subprocess
                result = subprocess.run(['ls', '-la', browsers_path], capture_output=True, text=True)
                print(f"Contents:\n{result.stdout}")
            except Exception as e:
                print(f"Could not list directory: {e}")
        else:
            print(f"⚠️  WARNING: Playwright browsers path does not exist: {browsers_path}")
        
        self.playwright = sync_playwright().start()
        print("🎭 Launching Chromium browser...")
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        print("✅ Chromium browser launched successfully")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra el navegador al salir."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def _load_all_posts(self, page: Page) -> None:
        """
        Hace scroll y carga todos los posts clickeando "Cargar más" hasta que no haya más.
        
        Args:
            page: Página de Playwright
        """
        max_clicks = 100  # Límite de seguridad
        clicks = 0
        no_change_count = 0
        
        print("🔄 Cargando posts dinámicamente...")
        
        while clicks < max_clicks:
            try:
                # Contar posts antes del scroll
                posts_before = page.locator('a[href*="/blog/"][href*="-"]').count()
                
                # Hacer scroll hasta el final
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(5)
                
                # Contar posts después del scroll
                posts_after_scroll = page.locator('a[href*="/blog/"][href*="-"]').count()
                
                # Si el scroll cargó más posts, continuar
                if posts_after_scroll > posts_before:
                    print(f"   ✅ +{posts_after_scroll - posts_before} posts cargados (total: {posts_after_scroll})")
                    no_change_count = 0
                    clicks += 1
                    continue
                
                # Buscar el botón "Cargar más"
                load_more_button = page.locator('button:has-text("Cargar más")').first
                
                if load_more_button.count() > 0:
                    try:
                        if load_more_button.is_visible(timeout=2000):
                            load_more_button.scroll_into_view_if_needed()
                            time.sleep(1)
                            load_more_button.click()
                            time.sleep(5)
                            
                            # Verificar si se cargaron posts nuevos
                            posts_after_click = page.locator('a[href*="/blog/"][href*="-"]').count()
                            new_posts = posts_after_click - posts_after_scroll
                            
                            if new_posts > 0:
                                print(f"   ✅ Botón clickeado: +{new_posts} posts (total: {posts_after_click})")
                                no_change_count = 0
                                clicks += 1
                            else:
                                no_change_count += 1
                        else:
                            no_change_count += 1
                    except Exception:
                        no_change_count += 1
                else:
                    no_change_count += 1
                
                # Si no hubo cambios en 3 iteraciones, terminar
                if no_change_count >= 3:
                    print(f"   ✅ Carga completa - Total: {posts_after_scroll} posts encontrados")
                    break
                    
            except PlaywrightTimeout:
                # No se encontró el botón o no es visible
                print("✅ No hay más posts para cargar (timeout)")
                break
            except Exception as e:
                print(f"⚠️ Error al cargar más posts: {e}")
                break
        
        if clicks >= max_clicks:
            print(f"⚠️ Se alcanzó el límite de {max_clicks} clics (puedes aumentarlo en el código si necesitas más)")
        
        # Hacer un último scroll para asegurar que todo esté cargado
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
    
    def _extract_post_details(self, page: Page, url: str) -> Dict[str, str]:
        """
        Navega a un post individual para extraer sus detalles completos.
        
        Args:
            page: Página de Playwright
            url: URL del post
            
        Returns:
            Diccionario con los datos del post
        """
        try:
            # Navegar al post
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(1000)  # Reducido de 2000 a 1000ms para mayor velocidad
            
            html = page.content()
            soup = BeautifulSoup(html, 'lxml')
            
            # Extraer título
            titulo = "Sin título"
            for tag in ['h1', 'h2']:
                title_tag = soup.find(tag)
                if title_tag:
                    titulo = title_tag.get_text(strip=True)
                    break
            
            # Extraer tiempo de lectura (debajo del título)
            # Buscar texto que contenga "min de lectura" o "min lectura"
            tiempo_lectura = "N/A"
            try:
                # Buscar en todos los divs que contengan texto de lectura
                all_text_divs = soup.find_all('div')
                for div in all_text_divs:
                    text = div.get_text(strip=True)
                    # Buscar patrones como "7min de lectura", "7 min de lectura", etc.
                    if 'min' in text.lower() and 'lectura' in text.lower():
                        # Extraer solo el texto relevante
                        if len(text) < 30:  # Filtrar para evitar párrafos largos
                            tiempo_lectura = text.replace('min de lectura', ' min de lectura').replace('min lectura', ' min de lectura').strip()
                            break
            except Exception as e:
                print(f"      ⚠️ Error extrayendo tiempo de lectura: {e}")
                pass
            
            # Extraer autor (debajo de la imagen principal)
            # Buscar el contenedor con clase 'flex gap-2' que contiene los divs del autor
            autor = "N/A"
            try:
                author_container = soup.find('div', class_='flex gap-2')
                if author_container:
                    # Encontrar todos los divs con el texto del autor
                    all_divs = author_container.find_all('div', class_='text-sm dark:text-text-disabled')
                    autor_parts = [div.get_text(strip=True) for div in all_divs if div.get_text(strip=True)]
                    if autor_parts:
                        autor = ' '.join(autor_parts)  # "Lilia Valenzuela | SaaS Specialist"
            except Exception:
                pass
            
            # Extraer fecha de publicación desde metadata
            # NOTA: El sitio web no expone fechas de publicación en metadata estándar
            # ni en JSON-LD. Las fechas están embebidas en el contenido Next.js
            # pero no son accesibles mediante scraping estándar.
            fecha = "N/A"
            try:
                # Intentar obtener desde meta tag primero
                meta_date = soup.find('meta', property='article:published_time')
                if meta_date:
                    fecha = meta_date.get('content', 'N/A')
                else:
                    # Intentar desde JSON-LD
                    json_ld = soup.find('script', type='application/ld+json')
                    if json_ld and json_ld.string:
                        import json
                        data = json.loads(json_ld.string)
                        if isinstance(data, dict) and 'datePublished' in data:
                            fecha = data['datePublished']
            except Exception:
                pass
            
            return {
                "Titular": titulo,
                "Autor": autor,
                "Tiempo de lectura": tiempo_lectura,
                "Fecha": fecha,
                "URL": url
            }
            
        except Exception as e:
            print(f"⚠️ Error extrayendo detalles de {url}: {str(e)}")
            # Retornar datos básicos en caso de error
            return {
                "Titular": url.split('/')[-1].replace('-', ' ').title(),
                "Autor": "N/A",
                "Tiempo de lectura": "N/A",
                "Fecha": "N/A",
                "URL": url
            }
    
    def _extract_posts_from_page(self, initial_page: Page) -> List[Dict[str, str]]:
        """
        Extrae todos los posts de la página actual usando BeautifulSoup después de la carga dinámica.
        
        Args:
            initial_page: Página de Playwright con los posts cargados
            
        Returns:
            Lista de diccionarios con la información de cada post
        """
        page = initial_page
        # Obtener el HTML completo después de la carga dinámica
        html_content = page.content()
        
        # Parsear con BeautifulSoup
        soup = BeautifulSoup(html_content, 'lxml')
        
        posts = []
        seen_urls = set()
        
        # Buscar todos los enlaces a posts
        post_links = soup.find_all('a', href=lambda x: x and '/blog/' in x and '-' in x)
        
        # Primero recolectar todas las URLs
        urls_to_process = []
        for link in post_links:
            try:
                url = link.get('href', '')
                
                # Validar URL
                if not url or not url.startswith('http'):
                    if url.startswith('/'):
                        url = f"https://xepelin.com{url}"
                    else:
                        continue
                
                # Evitar páginas de categorías (exactas, sin posts después)
                # Agregar trailing slash para comparación exacta
                url_clean = url.rstrip('/')
                category_pages = [
                    'https://xepelin.com/blog/pymes',
                    'https://xepelin.com/blog/corporativos',
                    'https://xepelin.com/blog/educacion-financiera',
                    'https://xepelin.com/blog/emprendedores',
                    'https://xepelin.com/blog/noticias',
                    'https://xepelin.com/blog/empresarios-exitosos',
                    'https://xepelin.com/blog'
                ]
                if url_clean in category_pages:
                    continue
                
                # Evitar duplicados
                if url in seen_urls:
                    continue
                
                seen_urls.add(url)
                urls_to_process.append(url)
                
            except Exception as e:
                continue
        
        print(f"📋 Procesando {len(urls_to_process)} posts individuales...")
        
        # Ahora navegar a cada post para obtener detalles
        # IMPORTANTE: Reiniciar página cada 100 posts para liberar memoria
        for i, url in enumerate(urls_to_process, 1):
            if i % 10 == 0:
                print(f"   Procesados {i}/{len(urls_to_process)} posts...")
            
            # Reiniciar página cada 100 posts para prevenir "object has been collected"
            if i > 1 and i % 100 == 0 and i < len(urls_to_process):
                print(f"   🔄 Reiniciando página para liberar memoria (post {i}/{len(urls_to_process)})...")
                try:
                    # Cerrar página actual
                    page.close()
                    # Crear nueva página limpia
                    page = self.browser.new_page()
                    page.set_default_timeout(self.timeout)
                    print(f"   ✅ Página reiniciada, continuando...")
                except Exception as e:
                    print(f"   ⚠️ Error reiniciando página: {e}")
            
            try:
                post_details = self._extract_post_details(page, url)
                if post_details:
                    posts.append(post_details)
            except Exception as e:
                print(f"   ⚠️ Error procesando post {i}: {str(e)}")
                continue
        
        print(f"✅ {len(posts)} posts únicos extraídos con detalles completos")
        return posts
    
    def scrape_category(self, category_name: str) -> List[Dict[str, str]]:
        """
        Scrapea TODOS los posts de una categoría específica.
        
        Args:
            category_name: Nombre de la categoría (ej: "Pymes")
            
        Returns:
            Lista de diccionarios con los posts de la categoría
        """
        if category_name not in self.CATEGORIES:
            raise ValueError(f"Categoría '{category_name}' no válida. "
                           f"Categorías disponibles: {list(self.CATEGORIES.keys())}")
        
        category_slug = self.CATEGORIES[category_name]
        url = f"{self.BASE_URL}/{category_slug}"
        
        print(f"\n🎯 Scrapeando categoría: {category_name}")
        print(f"📍 URL: {url}")
        
        if not self.browser:
            raise RuntimeError("Browser no inicializado. Usa 'with XepelinPlaywrightScraper():'")
        
        # Crear una nueva página
        page = self.browser.new_page()
        page.set_default_timeout(self.timeout)
        
        try:
            # Navegar a la página de la categoría
            print(f"🌐 Navegando a {url}...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            print("✅ Página cargada")
            
            # Hacer un scroll inicial para activar el lazy loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Esperar a que aparezcan los enlaces de posts (con hyphens en la URL)
            print("⏳ Esperando a que se carguen los posts...")
            try:
                # Esperar hasta 15 segundos a que aparezca al menos un enlace de post
                page.wait_for_selector('a[href*="/blog/"][href*="-"]', timeout=15000)
                print("✅ Posts encontrados en la página")
            except PlaywrightTimeout:
                print("⚠️  Timeout esperando posts - intentando continuar de todos modos")
            
            # Esperar más tiempo para que el contenido se renderice completamente
            page.wait_for_timeout(5000)
            
            # Cargar todos los posts
            self._load_all_posts(page)
            
            # Extraer posts
            posts = self._extract_posts_from_page(page)
            
            # Asignar categoría correcta a todos los posts
            for post in posts:
                post["Categoría"] = category_name
            
            print(f"✅ {len(posts)} posts extraídos de {category_name}")
            return posts
            
        finally:
            page.close()
    
    def scrape_all_categories(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Scrapea TODOS los posts de TODAS las categorías.
        
        Returns:
            Diccionario con categorías como keys y listas de posts como values
        """
        results = {}
        
        print("\n" + "="*70)
        print("🚀 INICIANDO SCRAPING COMPLETO DE TODAS LAS CATEGORÍAS")
        print("="*70)
        
        for category_name in self.CATEGORIES.keys():
            try:
                posts = self.scrape_category(category_name)
                results[category_name] = posts
            except Exception as e:
                print(f"❌ Error scrapeando {category_name}: {e}")
                results[category_name] = []
        
        # Resumen
        total_posts = sum(len(posts) for posts in results.values())
        print("\n" + "="*70)
        print(f"✨ SCRAPING COMPLETO - Total: {total_posts} posts")
        print("="*70)
        for cat, posts in results.items():
            print(f"  • {cat}: {len(posts)} posts")
        print("="*70 + "\n")
        
        return results


def test_scraper():
    """Función de prueba para el scraper."""
    print("🧪 Probando Playwright Scraper...\n")
    
    try:
        with XepelinPlaywrightScraper(headless=True) as scraper:
            # Probar con una categoría
            posts = scraper.scrape_category("Pymes")
            
            if posts:
                print(f"\n✅ {len(posts)} posts encontrados en Pymes")
                print("\nPrimeros 3 posts:")
                for i, post in enumerate(posts[:3], 1):
                    print(f"\n{i}. {post['Titular']}")
                    print(f"   Autor: {post['Autor']}")
                    print(f"   Fecha: {post['Fecha']}")
                    print(f"   URL: {post['URL']}")
            else:
                print("❌ No se encontraron posts")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Si ves 'Host system is missing dependencies', ejecuta:")
        print("   sudo playwright install-deps")


if __name__ == "__main__":
    test_scraper()
