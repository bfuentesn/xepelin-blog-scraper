# 🚀 Guía de Deploy en Render.com

## 📋 Prerequisitos

- [ ] Cuenta en GitHub
- [ ] Cuenta en Render.com (gratis)
- [ ] Proyecto subido a GitHub

---

## 🔧 PASO 1: Preparar el Proyecto

### 1.1 Verificar archivos necesarios

Asegúrate de tener estos archivos en tu repositorio:

```bash
cd /home/bfuentesn/xepelin/parte2
ls -1
```

Debes tener:
- ✅ `requirements.txt`
- ✅ `Procfile` (opcional pero recomendado)
- ✅ `runtime.txt`
- ✅ `app.py`
- ✅ `scraper_playwright.py`
- ✅ `sheets_manager.py`
- ✅ `.gitignore`
- ✅ `README.md`

### 1.2 Actualizar requirements.txt

Verificar que `requirements.txt` tenga todas las dependencias:

```txt
Flask==3.0.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
gspread==5.12.0
oauth2client==4.1.3
python-dotenv==1.0.0
playwright==1.40.0
gunicorn==21.2.0
```

### 1.3 Crear archivo de build para Render

Crear `render-build.sh`:

```bash
#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers and dependencies
playwright install --with-deps chromium
```

Dar permisos de ejecución:

```bash
chmod +x render-build.sh
```

### 1.4 Actualizar .gitignore

Asegurarse que `.gitignore` tenga:

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.log
.env
credentials.json
*.json
!requirements.json
.DS_Store
render-build.sh
```

**IMPORTANTE:** Quitar `render-build.sh` del gitignore si lo agregaste.

---

## 📦 PASO 2: Subir a GitHub

### 2.1 Inicializar Git (si no lo has hecho)

```bash
cd /home/bfuentesn/xepelin/parte2
git init
git add .
git commit -m "Initial commit - Xepelin Blog Scraper"
```

### 2.2 Crear repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre: `xepelin-blog-scraper`
3. Descripción: "API para scrapear blog de Xepelin"
4. Privado o Público (tu elección)
5. Click "Create repository"

### 2.3 Push al repositorio

```bash
git remote add origin https://github.com/TU_USUARIO/xepelin-blog-scraper.git
git branch -M main
git push -u origin main
```

---

## 🌐 PASO 3: Configurar Render.com

### 3.1 Crear cuenta en Render

1. Ve a https://render.com
2. Click "Get Started for Free"
3. Regístrate con GitHub (recomendado)

### 3.2 Crear nuevo Web Service

1. En el dashboard, click "New +" → "Web Service"
2. Conecta tu repositorio de GitHub
3. Selecciona `xepelin-blog-scraper`
4. Click "Connect"

### 3.3 Configurar el servicio

**Name:** `xepelin-blog-scraper`

**Region:** Oregon (US West) - recomendado

**Branch:** `main`

**Root Directory:** (dejar vacío)

**Runtime:** `Python 3`

**Build Command:**
```bash
./render-build.sh
```

**Start Command:**
```bash
gunicorn app:app
```

**Instance Type:** `Free`

---

## 🔑 PASO 4: Configurar Variables de Entorno

En la sección "Environment Variables", agregar:

### 4.1 PORT
```
Key: PORT
Value: 10000
```

### 4.2 PYTHON_VERSION
```
Key: PYTHON_VERSION
Value: 3.11.0
```

### 4.3 GOOGLE_CREDENTIALS_JSON

**IMPORTANTE:** Aquí necesitas el contenido de `credentials.json` en una sola línea.

En tu terminal local:

```bash
cd /home/bfuentesn/xepelin/parte2
cat credentials.json | tr -d '\n' | pbcopy
# O si no tienes pbcopy:
cat credentials.json | tr -d '\n'
```

Copia el resultado completo, luego en Render:

```
Key: GOOGLE_CREDENTIALS_JSON
Value: (pegar el JSON completo en una línea)
```

### 4.4 YOUR_EMAIL
```
Key: YOUR_EMAIL
Value: benjamin.fuentes@uc.cl
```

### 4.5 HOST
```
Key: HOST
Value: 0.0.0.0
```

### 4.6 DEBUG
```
Key: DEBUG
Value: False
```

---

## 🚀 PASO 5: Deploy

1. Click "Create Web Service"
2. Render comenzará a construir tu aplicación
3. Espera 5-10 minutos (Playwright tarda en instalarse)
4. Cuando veas "Live ✓" significa que está funcionando

---

## ✅ PASO 6: Verificar que funciona

### 6.1 Obtener la URL

Tu URL será algo como:
```
https://xepelin-blog-scraper.onrender.com
```

### 6.2 Probar el endpoint /health

```bash
curl https://xepelin-blog-scraper.onrender.com/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### 6.3 Probar /categories

```bash
curl https://xepelin-blog-scraper.onrender.com/categories
```

### 6.4 Probar scraping (IMPORTANTE: Usar tu URL)

```bash
curl -X POST 'https://xepelin-blog-scraper.onrender.com/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Noticias",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
    "email": "benjamin.fuentes@uc.cl"
  }'
```

Respuesta esperada:
```json
{
  "status": "accepted",
  "message": "Scraping job started...",
  ...
}
```

---

## 🔧 PASO 7: Solución de Problemas

### Si el build falla:

#### Error: "playwright not found"

**Solución:** Verificar que `render-build.sh` existe y tiene permisos de ejecución.

#### Error: "Module not found"

**Solución:** Verificar que `requirements.txt` está completo.

#### Error: "Port already in use"

**Solución:** Verificar que `PORT=10000` está en variables de entorno.

### Si la app arranca pero falla al scrapear:

#### Error: "Browser not found"

**Solución:** Asegurarse que el build command incluye:
```bash
playwright install --with-deps chromium
```

#### Error: "Google credentials not provided"

**Solución:** Verificar que `GOOGLE_CREDENTIALS_JSON` está correctamente configurada en variables de entorno.

---

## 📊 PASO 8: Monitoreo

### Ver logs en tiempo real

1. En Render dashboard, ve a tu servicio
2. Click en "Logs"
3. Verás todos los logs en tiempo real

### Activar auto-deploy

En la configuración del servicio:
- ✅ "Auto-Deploy" debe estar activado
- Cada push a `main` hará redeploy automático

---

## ⚡ Optimizaciones Opcionales

### 8.1 Usar Disk para caché de Playwright

En Render, puedes crear un disco persistente para cachear los browsers:

1. Ve a tu servicio
2. Click "Storage" → "Add Disk"
3. Mount Path: `/opt/render/project/.cache`
4. Size: 1GB

Esto hará que los builds sean más rápidos después del primero.

### 8.2 Configurar Custom Domain (opcional)

1. En Render dashboard, ve a tu servicio
2. Click "Settings"
3. Sección "Custom Domain"
4. Agrega tu dominio

---

## 🎯 PASO 9: Actualizar el proyecto

Cada vez que hagas cambios:

```bash
# En tu máquina local
git add .
git commit -m "Descripción de cambios"
git push origin main
```

Render detectará el push y hará redeploy automáticamente.

---

## 📝 Notas Importantes

### Limitaciones del plan Free de Render:

1. **Sleep después de 15 minutos de inactividad**
   - Primera request después de sleep tarda ~30 segundos
   - Solución: Usar un cron job para hacer ping cada 10 minutos

2. **750 horas/mes gratis**
   - Suficiente para uso de desarrollo/demo
   - Para producción, considerar plan Starter ($7/mes)

3. **Builds lentos en plan Free**
   - Primer build: ~10 minutos
   - Builds subsecuentes: ~5 minutos (con caché)

### Alternativa: Mantener activo con cron

Crear un servicio externo que haga ping:

```bash
# En cron.io o similar
*/10 * * * * curl https://xepelin-blog-scraper.onrender.com/health
```

---

## ✅ Checklist Final

Antes de considerar el deploy completo:

- [ ] Build exitoso en Render
- [ ] `/health` responde correctamente
- [ ] `/categories` retorna las 6 categorías
- [ ] POST `/scrape` acepta requests (202)
- [ ] Webhook recibe respuesta al terminar scraping
- [ ] Google Sheet se actualiza correctamente
- [ ] Logs muestran scraping exitoso
- [ ] Email de confirmación llega (si Zapier configurado)

---

## 🆘 Soporte

Si algo falla, revisar:

1. **Logs en Render**: Mostrarán errores específicos
2. **GitHub Actions**: Si configuraste CI/CD
3. **Variables de entorno**: Verificar que estén todas configuradas

---

## 🎉 Deploy Completado

Una vez que todo funcione, tu API estará disponible en:

```
https://xepelin-blog-scraper.onrender.com
```

Puedes compartir esta URL para que otros usen tu API.

---

## 📚 Recursos Adicionales

- Documentación Render: https://render.com/docs
- Playwright en Render: https://render.com/docs/deploy-playwright
- Render Free Tier: https://render.com/docs/free
