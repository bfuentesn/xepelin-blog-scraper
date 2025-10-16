# 🚀 Xepelin Blog Scraper - Comandos de Uso

## 📍 Base URL
```
http://localhost:5000
```

## 1️⃣ Obtener Categorías Disponibles

```bash
curl http://localhost:5000/categories
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

---

## 2️⃣ Scrapear UNA Categoría (Requerimiento Principal)

### Ejemplo 1: Noticias
```bash
curl -X POST 'http://localhost:5000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Noticias",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

### Ejemplo 2: Pymes
```bash
curl -X POST 'http://localhost:5000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Pymes",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

### Ejemplo 3: Con email personalizado
```bash
curl -X POST 'http://localhost:5000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Corporativos",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
    "email": "benjamin.fuentes@uc.cl"
  }'
```

### Ejemplo 4: Con Google Sheet existente
```bash
curl -X POST 'http://localhost:5000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Educación Financiera",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
    "email": "benjamin.fuentes@uc.cl",
    "sheet_url": "https://docs.google.com/spreadsheets/d/17JhWF2_3DMt_jRllzKQp7DuKNcHGfYDJ6u5DeBsYHR8/"
  }'
```

**Respuesta inmediata (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Scraping job started. Results will be sent to webhook when complete.",
  "categoria": "Noticias",
  "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
  "email": "benjamin.fuentes@uc.cl"
}
```

**Webhook recibe (al completar):**
```json
{
  "email": "benjamin.fuentes@uc.cl",
  "link": "https://docs.google.com/spreadsheets/d/17JhWF2_3DMt_jRllzKQp7DuKNcHGfYDJ6u5DeBsYHR8",
  "status": "success"
}
```

---

## 3️⃣ Scrapear TODAS las Categorías (BONUS TRACK)

```bash
curl -X POST 'http://localhost:5000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "scrape_all": true,
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
    "email": "benjamin.fuentes@uc.cl"
  }'
```

**Nota:** Esto toma ~25 minutos y scrapea 654 posts de 6 categorías.

**Respuesta inmediata:**
```json
{
  "status": "accepted",
  "message": "Scraping job started. Results will be sent to webhook when complete.",
  "mode": "all_categories",
  "info": "Scraping all blog categories (bonus feature)",
  "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
  "email": "benjamin.fuentes@uc.cl"
}
```

---

## 4️⃣ Health Check

```bash
curl http://localhost:5000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

---

## 5️⃣ Información de la API

```bash
curl http://localhost:5000/
```

**Respuesta:** Documentación completa de todos los endpoints.

---

## 📊 Tiempos Estimados de Scraping

| Categoría | Posts | Tiempo Aprox |
|-----------|-------|--------------|
| Casos de éxito | 17 | 1 min |
| Noticias | 28 | 2 min |
| Emprendedores | 61 | 5 min |
| Corporativos | 147 | 7 min |
| Educación Financiera | 150 | 7 min |
| Pymes | 251 | 10 min |
| **TODAS** | **654** | **~25 min** |

---

## ⚠️ Notas Importantes

1. **El API responde inmediatamente** (202 Accepted) y ejecuta el scraping en background
2. **Los resultados se envían al webhook** cuando termina el scraping
3. **El email recibe confirmación** si el webhook está configurado con Zapier
4. **La URL del Google Sheet** viene limpia (sin /edit#gid=...)
5. **Solo se crean hojas para las categorías solicitadas**:
   - 1 categoría → 1 hoja en el Sheet
   - Todas las categorías → 6 hojas en el Sheet

---

## 🔗 Google Sheet de Resultados

**URL:** https://docs.google.com/spreadsheets/d/17JhWF2_3DMt_jRllzKQp7DuKNcHGfYDJ6u5DeBsYHR8

**Columnas:**
- Titular
- Categoría
- Autor
- Tiempo de lectura
- Fecha de publicación
- URL

---

## 🐛 Manejo de Errores

### Error: Categoría inválida
```bash
curl -X POST 'http://localhost:5000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Categoría Inexistente",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

**Respuesta (400):**
```json
{
  "error": "Invalid category: 'Categoría Inexistente'",
  "available_categories": [
    "Pymes",
    "Corporativos",
    "Educación Financiera",
    "Emprendedores",
    "Noticias",
    "Casos de éxito"
  ]
}
```

### Error: Parámetros faltantes
```bash
curl -X POST 'http://localhost:5000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Noticias"
  }'
```

**Respuesta (400):**
```json
{
  "error": "Missing required parameter: 'webhook'"
}
```

---

## 🎯 Comando Curl Completo (Copy-Paste Ready)

### Para evaluación/prueba:
```bash
curl -X POST 'http://localhost:5000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Noticias",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
    "email": "benjamin.fuentes@uc.cl"
  }'
```

**Este comando cumple EXACTAMENTE con el requerimiento:**
- ✅ POST al endpoint /scrape
- ✅ Parámetro 1: categoria = "Noticias"
- ✅ Parámetro 2: webhook = "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
- ✅ Email incluido para notificación

---

## 📧 Webhook Response Format

El webhook recibirá (formato exacto requerido):

```bash
curl -X POST 'https://hooks.zapier.com/hooks/catch/11217441/bfemddr/' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "benjamin.fuentes@uc.cl",
    "link": "https://docs.google.com/spreadsheets/d/17JhWF2_3DMt_jRllzKQp7DuKNcHGfYDJ6u5DeBsYHR8"
  }'
```

**Campos adicionales incluidos:**
- `status`: "success" o "failed"
- `error`: Mensaje de error (si aplica)
