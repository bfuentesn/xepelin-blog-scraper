# Xepelin Blog Scraper API

API REST para scrapear posts del blog de Xepelin (https://xepelin.com/blog) y almacenar los resultados en Google Sheets.

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
5. **BONUS**: Scrapear todas las categorías del blog automáticamente

## 🚀 Instalación

### Prerrequisitos

- Python 3.8+
- Cuenta de Google Cloud con Google Sheets API habilitada
- Credenciales de servicio de Google Cloud

### Paso 1: Clonar el repositorio

```bash
cd /home/bfuentesn/xepelin/parte2
```

### Paso 2: Crear entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows

pip install -r requirements.txt
```

### Paso 3: Configurar Google Sheets API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita **Google Sheets API** y **Google Drive API**
4. Crea credenciales de **Service Account**
5. Descarga el archivo JSON de credenciales
6. Guarda el archivo como `credentials.json` en el directorio del proyecto

### Paso 4: Configurar variables de entorno

Copia el archivo `.env.example` a `.env`:

```bash
cp .env.example .env
```

Edita `.env` y configura:

```env
# Ruta al archivo de credenciales de Google o el JSON completo
GOOGLE_CREDENTIALS_JSON=./credentials.json

# Tu email para las respuestas del webhook
YOUR_EMAIL=benjamin.fuentes@uc.cl

# Configuración del servidor
PORT=5000
HOST=0.0.0.0
```

## 🏃 Ejecución

### Modo desarrollo

```bash
python app.py
```

### Modo producción con Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app:app
```

El API estará disponible en `http://localhost:5000`

## 📡 Endpoints

### 1. GET `/` - Información de la API

Devuelve información sobre la API y sus endpoints.

```bash
curl http://localhost:5000/
```

### 2. GET `/health` - Health Check

Verifica que la API esté funcionando.

```bash
curl http://localhost:5000/health
```

### 3. GET `/categories` - Categorías disponibles

Lista todas las categorías disponibles del blog.

```bash
curl http://localhost:5000/categories
```

**Respuesta:**
```json
{
  "categories": [
    "Pymes y Negocios",
    "Pymes",
    "Fintech",
    "Corporativos",
    "Educación Financiera",
    "Emprendedores",
    "Xepelin",
    "Casos de éxito"
  ],
  "count": 8
}
```

### 4. POST `/scrape` - Scrapear categoría

Endpoint principal para scrapear posts del blog.

**Parámetros del body (JSON):**
- `categoria` (requerido*): Nombre de la categoría a scrapear
- `webhook` (requerido): URL del webhook para recibir resultados
- `email` (opcional): Email para la respuesta (por defecto usa el del .env)
- `scrape_all` (opcional): `true` para scrapear todas las categorías (BONUS)

*No requerido si `scrape_all` es `true`

## 📝 Ejemplos de uso

### Ejemplo 1: Scrapear categoría "Pymes"

```bash
curl -X POST 'http://localhost:5000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Pymes",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/"
  }'
```

### Ejemplo 2: Scrapear categoría "Fintech" con email personalizado

```bash
curl -X POST 'http://localhost:5000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "categoria": "Fintech",
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
    "email": "benjamin.fuentes@uc.cl"
  }'
```

### Ejemplo 3: Scrapear todas las categorías (BONUS)

```bash
curl -X POST 'http://localhost:5000/scrape' \
  -H 'Content-Type: application/json' \
  -d '{
    "scrape_all": true,
    "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
    "email": "benjamin.fuentes@uc.cl"
  }'
```

### Respuesta inmediata (202 Accepted)

```json
{
  "status": "accepted",
  "message": "Scraping job started. Results will be sent to webhook when complete.",
  "categoria": "Pymes",
  "webhook": "https://hooks.zapier.com/hooks/catch/11217441/bfemddr/",
  "email": "benjamin.fuentes@uc.cl"
}
```

### Respuesta al webhook (cuando termina el scraping)

```json
{
  "email": "benjamin.fuentes@uc.cl",
  "link": "https://docs.google.com/spreadsheets/d/1ABC123...",
  "status": "success"
}
```

## 🌐 Deployment

### Opción 1: Railway

1. Crear cuenta en [Railway.app](https://railway.app)
2. Conectar tu repositorio de GitHub
3. Agregar las variables de entorno en Railway:
   - `GOOGLE_CREDENTIALS_JSON` (pegar el contenido del JSON)
   - `YOUR_EMAIL`
   - `PORT=5000`

Railway detectará automáticamente el archivo `requirements.txt` y desplegará la aplicación.

### Opción 2: Render

1. Crear cuenta en [Render.com](https://render.com)
2. Crear nuevo Web Service
3. Conectar repositorio
4. Configurar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 app:app`
5. Agregar variables de entorno

### Opción 3: Heroku

```bash
# Instalar Heroku CLI y login
heroku login

# Crear app
heroku create xepelin-blog-scraper

# Configurar variables de entorno
heroku config:set GOOGLE_CREDENTIALS_JSON="$(cat credentials.json)"
heroku config:set YOUR_EMAIL="benjamin.fuentes@uc.cl"

# Crear Procfile
echo "web: gunicorn --bind 0.0.0.0:\$PORT --workers 2 --timeout 300 app:app" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Opción 4: VPS (DigitalOcean, AWS, etc.)

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Clonar repositorio
git clone <tu-repo>
cd parte2

# Crear entorno virtual e instalar
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar systemd service
sudo nano /etc/systemd/system/xepelin-scraper.service
```

Contenido del service:
```ini
[Unit]
Description=Xepelin Blog Scraper API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/parte2
Environment="PATH=/path/to/parte2/venv/bin"
ExecStart=/path/to/parte2/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar servicio
sudo systemctl start xepelin-scraper
sudo systemctl enable xepelin-scraper
```

## 📊 Estructura del Google Sheet

El Google Sheet generado tendrá las siguientes columnas:

| Titular | Categoría | Autor | Tiempo de lectura | Fecha de publicación | URL |
|---------|-----------|-------|-------------------|---------------------|-----|
| Título del post | Categoría | Nombre del autor | 5 min | 2024-01-15 | https://... |

Para el modo BONUS (todas las categorías), se crean múltiples hojas (worksheets), una por cada categoría.

## 🔧 Troubleshooting

### Error: "No Google credentials provided"

- Asegúrate de que el archivo `credentials.json` existe
- O que la variable `GOOGLE_CREDENTIALS_JSON` está configurada en `.env`

### Error: "Error authorizing with Google Sheets"

- Verifica que Google Sheets API y Google Drive API estén habilitadas
- Verifica que el JSON de credenciales sea válido
- Asegúrate de usar credenciales de Service Account

### El webhook no recibe respuesta

- Verifica que la URL del webhook sea correcta
- Verifica que el webhook acepte requests POST con JSON
- Revisa los logs del servidor para ver errores

### No se encuentran posts en una categoría

- Verifica que el nombre de la categoría sea correcto
- Usa el endpoint `/categories` para ver las categorías disponibles
- El blog de Xepelin puede cambiar su estructura

## 🎯 Categorías soportadas

- **Pymes y Negocios** / **Pymes**: Consejos para pequeñas y medianas empresas
- **Fintech**: Tecnología financiera
- **Corporativos**: Contenido para grandes empresas
- **Educación Financiera**: Educación sobre finanzas
- **Emprendedores**: Consejos para emprendedores
- **Xepelin**: Noticias oficiales de Xepelin
- **Casos de éxito**: Historias de clientes

## 📦 Archivos del proyecto

```
parte2/
├── app.py                  # API Flask principal
├── scraper.py              # Scraper del blog de Xepelin
├── sheets_manager.py       # Gestión de Google Sheets
├── requirements.txt        # Dependencias de Python
├── .env.example           # Ejemplo de variables de entorno
├── .gitignore             # Archivos a ignorar en Git
├── README.md              # Esta documentación
└── credentials.json       # Credenciales de Google (no incluir en Git)
```

## 🤝 Contribuir

Si encuentras algún bug o quieres mejorar el proyecto:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto fue creado como parte de un desafío técnico para Xepelin.

## 📞 Contacto

Benjamin Fuentes - benjamin.fuentes@uc.cl

---

**Nota**: Este scraper está diseñado para uso educativo y de evaluación. Respeta los términos de servicio del sitio web de Xepelin y usa el scraper de manera responsable con delays apropiados entre requests.
