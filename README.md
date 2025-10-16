# Xepelin Blog Scraper API

API REST para scrapear posts del blog de Xepelin (https://xepelin.com/blog) y almacenar los resultados en Google Sheets.

**🚀 API en producción:** https://web-production-00c53.up.railway.app

---

## 📦 ENTREGABLES

### 1️⃣ Comando cURL para hacer POST a la API

Comandos listos para ejecutar que incluyen los **2 parámetros requeridos**: `categoria` y `webhook`.

#### **Categoría: Noticias**
```bash
curl -X POST 'https://web-production-00c53.up.railway.app/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Noticias",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

#### **Categoría: Casos de éxito**
```bash
curl -X POST 'https://web-production-00c53.up.railway.app/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Casos de éxito",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

#### **Categoría: Pymes**
```bash
curl -X POST 'https://web-production-00c53.up.railway.app/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Pymes",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

#### **Categoría: Emprendedores**
```bash
curl -X POST 'https://web-production-00c53.up.railway.app/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Emprendedores",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

#### **Categoría: Corporativos**
```bash
curl -X POST 'https://web-production-00c53.up.railway.app/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Corporativos",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

#### **Categoría: Educación Financiera**
```bash
curl -X POST 'https://web-production-00c53.up.railway.app/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Educación Financiera",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

#### **Todas las categorías (BONUS)**
```bash
curl -X POST 'https://web-production-00c53.up.railway.app/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "scrape_all": true,
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

**Respuesta esperada (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Scraping job started. Results will be sent to webhook when complete.",
  "categoria": "Noticias",
  "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
}
```

---

### 2️⃣ Google Sheet con los datos

**URL del Google Sheet:**
```
https://docs.google.com/spreadsheets/d/17JhWF2_3DMt_jRllzKQp7DuKNcHGfYDJ6u5DeBsYHR8/
```

El Google Sheet se actualiza automáticamente cada vez que ejecutas el scraper y contiene las siguientes columnas:

| Columna | Descripción |
|---------|-------------|
| **Titular** | Título del post del blog |
| **Categoría** | Categoría del post (Pymes, Noticias, etc.) |
| **Autor** | Autor del post |
| **Tiempo de lectura** | Tiempo estimado de lectura |
| **Fecha de publicación** | Fecha de publicación del post |
| **URL** | Link al post original |

**Código que ejecuta el scraper:** Ver `scraper_playwright.py` y `sheets_manager.py` en este repositorio.

---

### 3️⃣ Código de la API

El proyecto consta de los siguientes archivos principales:

#### **📄 Archivos del proyecto**

| Archivo | Descripción |
|---------|-------------|
| `app.py` | API REST con Flask - Endpoints principales |
| `scraper_playwright.py` | Scraper con Playwright para carga dinámica |
| `sheets_manager.py` | Integración con Google Sheets API |
| `requirements.txt` | Dependencias del proyecto |
| `Dockerfile` | Configuración para deployment |

#### **🔧 Tecnologías utilizadas**

- **Flask**: Framework web para la API REST
- **Playwright**: Automatización de navegador para scraping dinámico
- **BeautifulSoup4**: Parsing de HTML
- **Google Sheets API**: Almacenamiento de datos
- **Railway**: Hosting y deployment

---

## � Resultados esperados

| Categoría | Posts | Tiempo estimado |
|-----------|-------|-----------------|
| Noticias | ~28 | 2-3 min |
| Casos de éxito | ~50 | 3-5 min |
| Pymes | ~150 | 8-12 min |
| Emprendedores | ~120 | 7-10 min |
| Corporativos | ~100 | 6-9 min |
| Educación Financiera | ~200 | 12-15 min |
| **TODAS** | ~654 | 25-30 min |

---

## 📡 Endpoints disponibles

### GET `/health` - Health Check
```bash
curl https://web-production-00c53.up.railway.app/health
```

### GET `/categories` - Lista de categorías
```bash
curl https://web-production-00c53.up.railway.app/categories
```

**Respuesta:**
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

### GET `/test-playwright` - Test de Playwright
```bash
curl https://web-production-00c53.up.railway.app/test-playwright
```

### POST `/scrape` - Endpoint principal
Scrapea posts del blog y envía resultados al webhook.

**Parámetros requeridos:**
- `categoria`: Nombre de la categoría (o usa `scrape_all: true`)
- `webhook`: URL del webhook para recibir el link del Google Sheet

---

## 🚀 Quick Start

```bash
# 1. Verificar que la API está funcionando
curl https://web-production-00c53.up.railway.app/health

# 2. Ver categorías disponibles
curl https://web-production-00c53.up.railway.app/categories

# 3. Scrapear categoría Noticias (recomendado para prueba rápida)
curl -X POST 'https://web-production-00c53.up.railway.app/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Noticias",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'

# 4. Esperar ~2 minutos y revisar el webhook para obtener el link del Google Sheet
```

---

## 📝 Cómo funciona

1. **Recibes el POST** → La API recibe la categoría y webhook
2. **Job en background** → Se inicia un proceso de scraping asíncrono
3. **Playwright scrapea** → Navega al blog, carga todos los posts dinámicamente
4. **Extrae datos** → Visita cada post para obtener detalles completos
5. **Guarda en Google Sheets** → Crea/actualiza el spreadsheet
6. **Webhook notifica** → Envía el link del Google Sheet al webhook

---

## 🔒 Configuración

El proyecto requiere credenciales de Google Sheets API configuradas como variable de entorno:

```bash
GOOGLE_CREDENTIALS_JSON='{...}'  # Credenciales del service account
```



