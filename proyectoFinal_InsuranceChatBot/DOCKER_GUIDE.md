# Docker Configuration Guide - Insurance Chatbot

## SALIDA 3.1: Archivos de Configuración Final y Corregidos

Este documento presenta la configuración completa de Docker para el proyecto Insurance Chatbot, incluyendo todos los archivos necesarios para ejecutar la aplicación completa usando `docker-compose up`.

---

## 1. docker-compose.yml

**Ubicación:** `/docker-compose.yml`

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: insurance-chatbot-backend
    ports:
      - "5000:5000"
    env_file:
      - ./backend/.env
    environment:
      - FLASK_ENV=production
      - CHROMA_DB_PATH=/app/chroma_db
      - UPLOAD_FOLDER=/app/uploads
    volumes:
      - ./backend/chroma_db:/app/chroma_db
      - ./backend/uploads:/app/uploads
      - ./data:/app/data:ro  # Mount data directory as read-only
    networks:
      - chatbot-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: insurance-chatbot-frontend
    ports:
      - "8080:80"
    depends_on:
      - backend
    networks:
      - chatbot-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3

networks:
  chatbot-network:
    driver: bridge

volumes:
  chroma_data:
  uploads_data:
```

**Configuración:**
- **Servicios:** backend (Flask API), frontend (Nginx)
- **Red:** chatbot-network (bridge) para comunicación entre servicios
- **Volúmenes:** Persistencia de datos para ChromaDB y archivos subidos
- **Puertos expuestos:** 
  - Backend: 5000 (API REST)
  - Frontend: 8080 (interfaz web)

---

## 2. Backend Dockerfile

**Ubicación:** `/backend/Dockerfile`

```dockerfile
# Backend Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs /app/chroma_db

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

# Run the application
WORKDIR /app/src
CMD ["python", "main.py"]
```

**Optimizaciones:**
- Uso de imagen base slim para menor tamaño
- Layer caching optimizado (requirements.txt primero)
- Variables de entorno para Python configuradas
- Health check integrado
- Directorio de trabajo en `/app/src` para ejecución correcta

---

## 3. Frontend Dockerfile

**Ubicación:** `/frontend/Dockerfile`

```dockerfile
# Frontend Dockerfile
FROM nginx:alpine

# Copy frontend files
COPY . /usr/share/nginx/html/

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

**Características:**
- Imagen Alpine para tamaño mínimo
- Nginx como servidor web estático
- Configuración personalizada para proxying API
- Health check para monitoreo

---

## 4. Archivo .dockerignore (Raíz)

**Ubicación:** `/.dockerignore`

```
# Git
.git
.gitignore
.gitattributes

# Documentation
*.md
docs/
WBS.md
CLEANUP_SUMMARY.md
DEVELOPMENT_NOTES.md
FRONTEND_MIGRATION.md
QUICKSTART.md
readme.md
refactor backend.md

# IDE and Editor files
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Virtual environments
.venv/
env/
venv/
.conda/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Test and coverage
.pytest_cache/
.coverage
htmlcov/
.tox/

# Build artifacts
build/
dist/
*.egg-info/

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
*.tmp
*.bak
*.backup

# OS files
Thumbs.db
desktop.ini

# Setup scripts (not needed in container)
setup.bat
setup.sh
```

---

## 5. Backend .dockerignore

**Ubicación:** `/backend/.dockerignore`

```
# Git
.git
.gitignore

# Documentation
*.md
backend-refactoring-plan.md

# Environment files (use docker-compose env instead)
.env
.env.local
.env.production

# Virtual environments
.venv/
env/
venv/
.conda/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Build artifacts
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.hypothesis/

# Logs
*.log
logs/

# IDE and Editor files
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# ChromaDB data (mounted as volume)
chroma_db/

# Upload directories (mounted as volume)
uploads/
temp/
tmp/

# Jupyter Notebook
.ipynb_checkpoints

# OS files
Thumbs.db
desktop.ini

# Backup files
*.bak
*.backup
*.old

# Data files (should be mounted as volumes)
data/
local_data/

# Old/backup scripts
S3_connection/
data_ingestion/
chatbot_logic.py
```

---

## 6. Frontend .dockerignore

**Ubicación:** `/frontend/.dockerignore`

```
# Git
.git
.gitignore

# Documentation
*.md
refactor frontend.md

# IDE and Editor files
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Old/backup files
.old/
*.bak
*.backup
*.old

# Logs
*.log
logs/

# OS files
Thumbs.db
desktop.ini

# Temporary files
tmp/
temp/
*.tmp

# Keep only necessary files for static frontend:
# - index.html
# - styles.css
# - js/
# - assets/
# - nginx.conf
```

---

## 7. Nginx Configuration

**Ubicación:** `/frontend/nginx.conf`

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Main location
    location / {
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API proxy to backend (for development)
    location /api/ {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

---

## SALIDA 3.2: Guía de Verificación de Ejecución

Esta sección documenta los puntos clave de cada servicio configurado para verificar que los archivos correctos se están ejecutando.

---

### Servicio 1: Backend (insurance-chatbot-backend)

#### **Información General**
- **Nombre del Servicio:** `backend`
- **Nombre del Contenedor:** `insurance-chatbot-backend`
- **Imagen Base:** `python:3.12-slim`
- **Puerto Expuesto:** `5000` (host) → `5000` (contenedor)

#### **Punto de Entrada (CMD/ENTRYPOINT)**
```python
CMD ["python", "main.py"]
```

#### **Directorio de Trabajo**
- **WORKDIR Final:** `/app/src`
- El contenedor cambia al directorio `/app/src` antes de ejecutar el comando principal

#### **Ruta del Archivo Principal**
- **Entry Point Absoluto:** `/app/src/main.py`
- **Archivo Ejecutado:** `main.py`

#### **Contenido del Entry Point (main.py)**
El archivo `main.py` contiene:
- Importación del factory pattern de Flask: `from api.app import create_app`
- Función `main()` que:
  1. Lee configuración de `FLASK_ENV` (por defecto: `development`)
  2. Crea la aplicación Flask con `create_app(config_name)`
  3. Ejecuta el servidor en `0.0.0.0:5000`
- Estructura del API REST en `/api/v1/*` endpoints

#### **Estructura de Archivos Dentro del Contenedor**
```
/app/
├── src/                          # Código fuente copiado
│   ├── main.py                   # ← ARCHIVO EJECUTADO
│   ├── api/                      # Módulos de la API
│   │   ├── app.py               # Application factory
│   │   ├── config.py            # Configuración
│   │   ├── extensions.py        # Extensiones Flask
│   │   └── routes/              # Rutas de la API
│   ├── services/                 # Servicios del chatbot
│   ├── models/                   # Modelos de datos
│   └── utils/                    # Utilidades
├── chroma_db/                    # Base de datos vectorial (montado)
├── uploads/                      # Archivos subidos (montado)
├── data/                         # Datos de entrada (montado RO)
└── logs/                         # Logs de aplicación

```

#### **Variables de Entorno Clave**
- `FLASK_ENV=production` (sobrescrito desde docker-compose)
- `CHROMA_DB_PATH=/app/chroma_db`
- `UPLOAD_FOLDER=/app/uploads`
- `GOOGLE_API_KEY` (desde .env)
- `BRAVE_API_KEY` (desde .env)

#### **Health Check**
- **URL:** `http://localhost:5000/api/v1/health`
- **Intervalo:** 30s
- **Timeout:** 10s
- **Start Period:** 40s (tiempo de inicialización)

#### **Verificación Manual**
```bash
# Verificar que el contenedor está corriendo
docker ps | grep insurance-chatbot-backend

# Ver logs del contenedor
docker logs insurance-chatbot-backend

# Verificar health check
docker inspect insurance-chatbot-backend | grep -A 10 "Health"

# Probar el endpoint desde el host
curl http://localhost:5000/api/v1/health

# Entrar al contenedor para debugging
docker exec -it insurance-chatbot-backend bash
cd /app/src
ls -la
cat main.py
```

---

### Servicio 2: Frontend (insurance-chatbot-frontend)

#### **Información General**
- **Nombre del Servicio:** `frontend`
- **Nombre del Contenedor:** `insurance-chatbot-frontend`
- **Imagen Base:** `nginx:alpine`
- **Puerto Expuesto:** `8080` (host) → `80` (contenedor)

#### **Punto de Entrada (CMD/ENTRYPOINT)**
```bash
CMD ["nginx", "-g", "daemon off;"]
```

#### **Directorio de Trabajo**
- **WORKDIR:** `/usr/share/nginx/html/` (por defecto de nginx)
- **Configuración:** `/etc/nginx/conf.d/default.conf`

#### **Ruta del Archivo Principal**
- **Entry Point del Servidor:** `/usr/sbin/nginx` (binario de nginx)
- **Archivo HTML Principal:** `/usr/share/nginx/html/index.html`
- **Configuración:** `/etc/nginx/conf.d/default.conf`

#### **Estructura de Archivos Dentro del Contenedor**
```
/usr/share/nginx/html/
├── index.html                    # ← PÁGINA PRINCIPAL
├── styles.css                    # Estilos CSS
├── js/                          # JavaScript modular
│   ├── main.js                  # Entry point JS
│   ├── config/
│   │   └── api-config.js        # Configuración de API
│   ├── services/
│   │   └── api-service.js       # Cliente API
│   ├── components/
│   │   └── chat-component.js    # Componente de chat
│   ├── state/                   # Gestión de estado
│   └── utils/                   # Utilidades
└── assets/
    └── anioneai.png             # Logo e imágenes

/etc/nginx/conf.d/
└── default.conf                  # ← CONFIGURACIÓN NGINX
```

#### **Configuración de Nginx**
- **Puerto de escucha:** `80`
- **Documento raíz:** `/usr/share/nginx/html`
- **Índice:** `index.html`

**Rutas configuradas:**
1. **`/`** - Sirve archivos estáticos (HTML, CSS, JS, imágenes)
2. **`/api/`** - Proxy reverso a `http://backend:5000` (opcional, para comunicación interna)
3. **`/health`** - Endpoint de health check

#### **Health Check**
- **URL:** `http://localhost/health`
- **Intervalo:** 30s
- **Timeout:** 5s
- **Respuesta esperada:** `"healthy\n"` (HTTP 200)

#### **Arquitectura de Frontend**
El frontend es una **Single Page Application (SPA)** que:
1. Carga `index.html` desde nginx
2. Carga módulos JS desde `/js/`
3. Se conecta al backend en `http://localhost:5000/api/v1/*` (desde el navegador del usuario)
4. Usa arquitectura modular con ES6 modules

#### **Verificación Manual**
```bash
# Verificar que el contenedor está corriendo
docker ps | grep insurance-chatbot-frontend

# Ver logs de nginx
docker logs insurance-chatbot-frontend

# Verificar health check
curl http://localhost:8080/health

# Verificar que la página carga
curl -I http://localhost:8080/

# Entrar al contenedor para debugging
docker exec -it insurance-chatbot-frontend sh
cd /usr/share/nginx/html
ls -la
cat index.html | head -20

# Ver configuración de nginx
cat /etc/nginx/conf.d/default.conf

# Ver logs en tiempo real
docker exec -it insurance-chatbot-frontend tail -f /var/log/nginx/access.log
```

---

## Instrucciones de Ejecución

### Prerrequisitos
1. Docker Engine instalado (versión 20.10+)
2. Docker Compose instalado (versión 2.0+)
3. Puertos 5000 y 8080 disponibles

### Configuración Inicial

1. **Clonar el repositorio:**
```bash
git clone https://github.com/MichaelYnoa/proyectoFinal_InsuranceChatBot.git
cd proyectoFinal_InsuranceChatBot
```

2. **Configurar variables de entorno:**
```bash
# Copiar el archivo de ejemplo
cp backend/.env.example backend/.env

# Editar el archivo .env y agregar las API keys
nano backend/.env
```

Contenido mínimo requerido en `backend/.env`:
```env
GOOGLE_API_KEY=your_google_api_key_here
BRAVE_API_KEY=your_brave_api_key_here
FLASK_ENV=production
CHROMA_DB_PATH=/app/chroma_db
UPLOAD_FOLDER=/app/uploads
```

3. **Verificar que ChromaDB está inicializado:**
```bash
# Verificar que existe el directorio
ls -la backend/chroma_db/

# Si está vacío, construir la base de datos primero (opcional)
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cd src
python chroma_db_builder.py
cd ../..
```

### Ejecución con Docker Compose

```bash
# Construir y levantar todos los servicios
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f backend
docker compose logs -f frontend

# Verificar el estado de los servicios
docker compose ps

# Verificar health checks
docker inspect insurance-chatbot-backend --format='{{json .State.Health}}'
docker inspect insurance-chatbot-frontend --format='{{json .State.Health}}'
```

### Acceso a la Aplicación

- **Frontend (Interfaz Web):** http://localhost:8080
- **Backend API:** http://localhost:5000
- **Health Check Backend:** http://localhost:5000/api/v1/health
- **Health Check Frontend:** http://localhost:8080/health

### Detener la Aplicación

```bash
# Detener sin eliminar contenedores
docker compose stop

# Detener y eliminar contenedores
docker compose down

# Detener y eliminar contenedores + volúmenes
docker compose down -v

# Detener y eliminar todo (incluyendo imágenes)
docker compose down -v --rmi all
```

---

## Resolución de Problemas

### El backend no inicia
```bash
# Verificar logs
docker logs insurance-chatbot-backend

# Problemas comunes:
# 1. Falta .env → Copiar de .env.example y configurar API keys
# 2. ChromaDB no inicializado → Ver sección "Configuración Inicial"
# 3. Puerto 5000 ocupado → Cambiar en docker-compose.yml
```

### El frontend no se conecta al backend
```bash
# Verificar que ambos servicios están corriendo
docker compose ps

# Verificar que el backend responde
curl http://localhost:5000/api/v1/health

# Verificar logs del navegador (F12 → Console)
# Problema común: CORS → Flask-CORS ya está configurado
```

### Rebuild después de cambios
```bash
# Rebuild de un servicio específico
docker compose build backend
docker compose build frontend

# Rebuild completo sin cache
docker compose build --no-cache

# Recrear contenedores con nuevas imágenes
docker compose up -d --force-recreate
```

---

## Arquitectura de Comunicación

```
┌─────────────────────────────────────────────────────────────┐
│                        HOST MACHINE                         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │               Web Browser (Usuario)                  │  │
│  │                                                      │  │
│  │  http://localhost:8080 (Frontend HTML/JS/CSS)      │  │
│  │           │                                          │  │
│  │           └──────────────────────────┐              │  │
│  └──────────────────────────────────────┼──────────────┘  │
│                                         │                   │
│  ┌──────────────────────────────────────┼──────────────┐  │
│  │ Docker Host Network                  │              │  │
│  │                                      │              │  │
│  │  Port 5000 → Backend Container      │              │  │
│  │  Port 8080 → Frontend Container     │              │  │
│  └──────────────────────────────────────┼──────────────┘  │
└─────────────────────────────────────────┼──────────────────┘
                                          │
        ┌─────────────────────────────────┴──────────────────┐
        │           Docker Network: chatbot-network          │
        │                                                     │
        │  ┌─────────────────────┐    ┌──────────────────┐ │
        │  │  Backend Container  │    │ Frontend Container│ │
        │  │  (Flask API)        │◄───┤ (Nginx)          │ │
        │  │  Port 5000          │    │ Port 80          │ │
        │  │                     │    │                   │ │
        │  │  /app/src/main.py   │    │ /usr/share/nginx/│ │
        │  │                     │    │      html/       │ │
        │  └─────────┬───────────┘    └──────────────────┘ │
        │            │                                       │
        │  ┌─────────▼───────────┐                         │
        │  │  Volumes (Persist)  │                         │
        │  │  - chroma_db/       │                         │
        │  │  - uploads/         │                         │
        │  │  - data/ (RO)       │                         │
        │  └─────────────────────┘                         │
        └───────────────────────────────────────────────────┘
```

**Flujo de Comunicación:**
1. Usuario abre navegador en `http://localhost:8080`
2. Nginx sirve `index.html` y archivos estáticos
3. JavaScript en el navegador hace peticiones a `http://localhost:5000/api/v1/*`
4. Las peticiones van directamente al backend expuesto en el puerto 5000 del host
5. Backend procesa y responde (ChromaDB, LLM, etc.)
6. Alternativamente, nginx puede hacer proxy de `/api/` a `http://backend:5000` internamente

---

## Características de Seguridad

### Backend
- Variables de entorno para API keys (no hardcoded)
- Flask-CORS configurado para CORS apropiado
- Health checks para monitoreo
- Montaje de datos como read-only cuando es apropiado

### Frontend
- Headers de seguridad HTTP (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
- Compresión gzip habilitada
- Cache de assets estáticos
- Proxy reverso para APIs

---

## Optimizaciones Implementadas

1. **Build Caching:**
   - `requirements.txt` se copia antes del código para aprovechar cache de layers
   - `.dockerignore` excluye archivos innecesarios

2. **Tamaño de Imagen:**
   - Backend: `python:3.12-slim` (~180MB menos que full)
   - Frontend: `nginx:alpine` (~25MB vs ~140MB standard)

3. **Persistencia de Datos:**
   - Volúmenes para ChromaDB y uploads
   - Data directory montado como read-only

4. **Resiliencia:**
   - Health checks configurados
   - Restart policy: `unless-stopped`
   - Depends_on para orden de inicio

---

## Notas Adicionales

### Volúmenes Declarados pero No Utilizados
En `docker-compose.yml` se declaran los volúmenes `chroma_data` y `uploads_data` pero no se usan. En su lugar, se usan bind mounts (montajes de directorios del host). Esto es intencional para:
- Facilitar el acceso a los datos desde el host
- Permitir backup y restauración sencilla
- Facilitar debugging y desarrollo

Si se prefiere usar volúmenes de Docker gestionados:
```yaml
volumes:
  - chroma_data:/app/chroma_db
  - uploads_data:/app/uploads
```

### Inicialización de ChromaDB
La base de datos vectorial debe estar inicializada antes del primer uso. Si está vacía:
1. Ejecutar `python chroma_db_builder.py` localmente
2. O montar datos pre-procesados
3. O implementar inicialización en el startup del contenedor

### Escalabilidad
Para producción, considerar:
- Usar un load balancer (nginx como reverse proxy externo)
- Separar ChromaDB a un servicio dedicado
- Implementar cache (Redis)
- Usar orquestación con Kubernetes

---

**Fecha de última actualización:** 2024
**Versión de Docker Compose:** 2.x
**Versión de configuración:** 1.0
