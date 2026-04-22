# Docker Quick Reference - Insurance Chatbot

## Quick Start

```bash
# 1. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 2. Start application
docker compose up -d

# 3. Access application
# Frontend: http://localhost:8080
# Backend API: http://localhost:5000
```

## Service Entry Points

### Backend (insurance-chatbot-backend)
- **Container Path:** `/app/src/main.py`
- **Command:** `python main.py`
- **Working Dir:** `/app/src`
- **Port:** 5000
- **Health:** http://localhost:5000/api/v1/health

### Frontend (insurance-chatbot-frontend)
- **Container Path:** `/usr/share/nginx/html/index.html`
- **Command:** `nginx -g "daemon off;"`
- **Working Dir:** `/usr/share/nginx/html/`
- **Port:** 80 → 8080 (host)
- **Health:** http://localhost:8080/health

## Useful Commands

```bash
# View logs
docker compose logs -f

# Check status
docker compose ps

# Restart services
docker compose restart

# Stop services
docker compose down

# Rebuild after changes
docker compose build
docker compose up -d --force-recreate

# Debug inside containers
docker exec -it insurance-chatbot-backend bash
docker exec -it insurance-chatbot-frontend sh
```

## Modified Files

All changes were to Docker configuration only:

1. ✅ `docker-compose.yml` - Removed obsolete version, added env_file
2. ✅ `backend/Dockerfile` - Removed chroma_db copy, added mkdir
3. ✅ `.dockerignore` - Created (root level)
4. ✅ `backend/.dockerignore` - Created
5. ✅ `frontend/.dockerignore` - Created
6. ✅ `.gitignore` - Updated to allow .dockerignore files
7. ✅ `DOCKER_GUIDE.md` - Comprehensive documentation (NEW)
8. ✅ `DOCKER_QUICK_REFERENCE.md` - This file (NEW)

No application code was modified. ✨

## Complete Documentation

For full details, see [DOCKER_GUIDE.md](./DOCKER_GUIDE.md) which includes:
- All Docker configuration files (complete listings)
- Detailed service verification guide
- Architecture diagrams
- Troubleshooting guide
- Security and optimization notes
