# Xepelin Blog Scraper API

API REST para scrapear posts del blog de Xepelin (https://xepelin.com/blog) y almacenar los resultados en Google Sheets.

**🚀 API en producción:** https://xepelin-blog-scraper-0af5.onrender.com

## 📋 Descripción

Esta API permite:
1. Recibir una categoría del blog de Xepelin y un webhook
2. Scrapear todos los posts de esa categoría
3. Guardar los datos en Google Sheets con las columnas:
   - Titular
   - Categoría
   - Autor
   - Tiempo de lectura
   - Fecha de publicación
   - URL
4. Enviar el link del Google Sheet al webhook proporcionado
5. Scrapear todas las categorías del blog automáticamente

## 📡 Endpoints

### 1. GET `/` - Información de la API

Devuelve información sobre la API y sus endpoints.

```bash
curl https://xepelin-blog-scraper-0af5.onrender.com/
```

### 2. GET `/health` - Health Check

Verifica que la API esté funcionando.

```bash
curl https://xepelin-blog-scraper-0af5.onrender.com/health
```

### 3. GET `/categories` - Categorías disponibles

Lista todas las categorías disponibles del blog.

```bash
curl https://xepelin-blog-scraper-0af5.onrender.com/categories
```

**Respuesta esperada:**
```json
{
  "categories": [
    "Pymes",
    "Corporativos",
    "Educación Financiera",
    "Emprendedores",
    "Noticias",
    "Casos de éxito"
  ],
  "count": 6
}
```

### 4. GET `/test-playwright` - Test de Playwright

Verifica que Playwright esté instalado y funcionando correctamente.

```bash
curl https://xepelin-blog-scraper-0af5.onrender.com/test-playwright
```

**Respuesta esperada:**
```json
{
  "status": "success",
  "message": "Playwright is working correctly",
  "test_page_title": "Example Domain"
}
```

### 5. POST `/scrape` - Scrapear categoría(s)

Endpoint principal para scrapear posts del blog.

**Parámetros del body (JSON):**
- `categoria` (requerido*): Nombre de la categoría a scrapear
- `webhook` (requerido): URL del webhook para recibir resultados
- `scrape_all` (opcional): `true` para scrapear todas las categorías

*No requerido si `scrape_all` es `true`

## 📝 Ejemplos de uso

### Ejemplo 1: Scrapear categoría "Noticias"

```bash
curl -X POST 'https://xepelin-blog-scraper-0af5.onrender.com/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Noticias",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

### Ejemplo 2: Scrapear categoría "Casos de éxito"

```bash
curl -X POST 'https://xepelin-blog-scraper-0af5.onrender.com/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Casos de éxito",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

### Ejemplo 3: Scrapear categoría "Emprendedores"

```bash
curl -X POST 'https://xepelin-blog-scraper-0af5.onrender.com/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Emprendedores",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

### Ejemplo 4: Scrapear TODAS las categorías (BONUS)

```bash
curl -X POST 'https://xepelin-blog-scraper-0af5.onrender.com/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "scrape_all": true,
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

### Respuesta inmediata (202 Accepted)

**Para una categoría:**
```json
{
  "status": "accepted",
  "message": "Scraping job started. Results will be sent to webhook when complete.",
  "categoria": "Noticias",
  "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
}
```

**Para todas las categorías:**
```json
{
  "status": "accepted",
  "message": "Scraping job started. Results will be sent to webhook when complete.",
  "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
  "mode": "all_categories",
  "info": "Scraping all 6 categories"
}
```
---

## 🚀 Quick Start

### Test rápido de la API

```bash
# 1. Verificar que la API está funcionando
curl https://xepelin-blog-scraper-0af5.onrender.com/health

# 2. Ver categorías disponibles
curl https://xepelin-blog-scraper-0af5.onrender.com/categories

# 3. Verificar que Playwright está funcionando
curl https://xepelin-blog-scraper-0af5.onrender.com/test-playwright

# 4. Scrapear categoría Noticias (28 posts, ~2 minutos)
curl -X POST 'https://xepelin-blog-scraper-0af5.onrender.com/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Noticias",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

