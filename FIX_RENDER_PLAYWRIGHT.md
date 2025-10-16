# 🔧 Fix: Playwright en Render

## Problema Identificado

```
Error: Executable doesn't exist at /opt/render/.cache/ms-playwright/chromium-1091/chrome-linux/chrome
```

**Causa:** Playwright no se instaló correctamente durante el build en Render.

---

## ✅ Solución Aplicada

He actualizado `render-build.sh` para usar el método correcto de instalación:

```bash
# ❌ ANTES (no funcionaba)
playwright install --with-deps chromium

# ✅ AHORA (correcto)
python -m playwright install chromium
python -m playwright install-deps chromium
```

---

## 🚀 Pasos para Re-Deploy en Render

### Opción 1: Re-Deploy Manual (Recomendado)

1. **Sube los cambios a GitHub:**
   ```bash
   cd /home/bfuentesn/xepelin/parte2
   git add render-build.sh app.py
   git commit -m "Fix: Playwright installation in Render"
   git push origin main
   ```

2. **Forzar re-deploy en Render:**
   - Ve a https://dashboard.render.com
   - Click en tu servicio: `xepelin-blog-scraper`
   - Click en **"Manual Deploy"** → **"Clear build cache & deploy"**
   - Espera ~10-15 minutos (el build tardará más por instalar Chromium)

3. **Verificar instalación:**
   ```bash
   curl https://xepelin-blog-scraper-0af5.onrender.com/test-playwright
   ```
   
   Debe retornar:
   ```json
   {
     "status": "success",
     "message": "Playwright is working correctly",
     "test_page_title": "Example Domain"
   }
   ```

4. **Probar scraping:**
   ```bash
   curl -X POST 'https://xepelin-blog-scraper-0af5.onrender.com/scrape' \
     -H 'Content-Type: application/json' \
     -d '{
       "categoria": "Noticias",
       "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
       "email": "benjamin.fuentes@uc.cl"
     }'
   ```

---

### Opción 2: Re-Deploy Automático

Si tienes **Auto-Deploy habilitado** en Render:

1. **Solo sube los cambios:**
   ```bash
   cd /home/bfuentesn/xepelin/parte2
   git add render-build.sh app.py
   git commit -m "Fix: Playwright installation in Render"
   git push origin main
   ```

2. **Render detectará el push** y hará re-deploy automáticamente

---

## 📊 Monitorear el Build

Durante el re-deploy, en los **Logs de Render** deberías ver:

```
🔧 Installing Python dependencies...
✅ Successfully installed packages

🎭 Installing Playwright browsers...
Downloading Chromium 119.0.6045.9 (playwright build v1091)...
✅ Chromium installed successfully

🔧 Installing system dependencies for Chromium...
Installing dependencies for Chromium...
✅ Dependencies installed

✅ Build completed successfully!
```

---

## ⚠️ Consideraciones Importantes

### 1. Tiempo de Build
- **Primer build con Chromium:** ~10-15 minutos
- **Builds siguientes (con cache):** ~3-5 minutos

### 2. Tamaño del Deploy
- Chromium agrega ~200 MB al deploy
- Render Free tier tiene suficiente espacio

### 3. Memoria en Runtime
- El plan Free de Render tiene **512 MB RAM**
- Playwright + Chromium consumen ~300-400 MB
- **Para scraping pesado (ej: todas las categorías), puede fallar por memoria**

### 4. Recomendaciones
- ✅ **Noticias** (28 posts, ~2 min) - Funciona perfectamente
- ✅ **Casos de éxito** (17 posts, ~1 min) - Funciona perfectamente
- ✅ **Emprendedores** (61 posts, ~5 min) - Debería funcionar
- ⚠️ **Corporativos** (147 posts, ~7 min) - Puede agotar memoria
- ⚠️ **Pymes** (251 posts, ~10 min) - Puede agotar memoria
- ❌ **Todas las categorías** (654 posts, ~25 min) - Muy probable que falle por memoria

---

## 🔍 Troubleshooting

### Si sigue fallando después del re-deploy:

1. **Verifica el build log completo:**
   - Dashboard → Tu servicio → "Logs" tab
   - Busca errores durante `playwright install`

2. **Verifica las variables de entorno:**
   ```
   ✅ GOOGLE_CREDENTIALS_JSON - JSON completo de credentials
   ✅ YOUR_EMAIL - benjamin.fuentes@uc.cl
   ✅ PORT - 10000
   ✅ PYTHON_VERSION - 3.11.0
   ✅ HOST - 0.0.0.0
   ✅ DEBUG - False
   ```

3. **Prueba el endpoint de diagnóstico:**
   ```bash
   curl https://xepelin-blog-scraper-0af5.onrender.com/test-playwright
   ```

4. **Si test-playwright funciona pero scrape falla:**
   - Problema: Memoria insuficiente
   - Solución: Usar categorías pequeñas (Noticias, Casos de éxito)
   - O: Upgrade a plan Starter ($7/mes) con 512 MB → 2 GB RAM

---

## 📝 Cambios Realizados en el Código

### 1. `render-build.sh`
- Cambié `playwright install --with-deps chromium`
- Por: `python -m playwright install chromium` + `python -m playwright install-deps chromium`

### 2. `app.py`
- ✅ Agregado endpoint `/test-playwright` para diagnóstico
- ✅ Mejorado logging en `process_scraping_job()`
- ✅ Agregado traceback completo en errores

---

## ✅ Confirmación de Éxito

Cuando el re-deploy funcione, deberías ver:

1. **Health check OK:**
   ```bash
   curl https://xepelin-blog-scraper-0af5.onrender.com/health
   # {"status": "healthy", "message": "API is running"}
   ```

2. **Playwright test OK:**
   ```bash
   curl https://xepelin-blog-scraper-0af5.onrender.com/test-playwright
   # {"status": "success", ...}
   ```

3. **Scraping OK:**
   - Webhook recibe email con link válido de Google Sheet
   - Sheet contiene los posts scrapeados

---

## 🎯 Comando Final para Probar

```bash
# Test completo
curl https://xepelin-blog-scraper-0af5.onrender.com/test-playwright && \
curl -X POST 'https://xepelin-blog-scraper-0af5.onrender.com/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Noticias",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
    "email": "benjamin.fuentes@uc.cl"
  }'
```

Deberías recibir:
1. ✅ Test de Playwright exitoso
2. ✅ Respuesta 202 Accepted del scraping
3. ✅ Email con link de Google Sheet en ~2 minutos

---

¡El fix está listo! Solo necesitas hacer el re-deploy en Render. 🚀
