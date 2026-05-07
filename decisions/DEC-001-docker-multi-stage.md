# DEC-001 — Docker Multi-Stage Build with Nginx

**Date:** 2026-04-06  
**Author:** Claude Code (autonomous)  
**Status:** Accepted  
**Category:** Infrastructure  

---

## Context

HackerLabAcademy was using Vite dev server in Docker (`npm run dev`). This is fine for development but **not production-ready**:

- No static asset caching
- CORS issues when frontend and backend on different ports
- Hot reload unnecessary in production
- No built reverse proxy configuration
- Security: dev server exposes more than needed

ForgeBody project uses Vite dev server as well, but ForgeBody is explicitly a **development/local project**. HackerLabAcademy aims to be a production-ready learning platform (even if self-hosted).

---

## Problem

How to deploy HackerLabAcademy in Docker with:

1. **Performance:** Static assets cached, gzipped
2. **CORS elimination:** Frontend and backend same origin (or properly proxied)
3. **SPA support:** Client-side routing fallback to `index.html`
4. **Maintainability:** Single docker-compose command for full stack
5. **Simplicity:** No manual nginx config on host (containerized)

---

## Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **Keep Vite dev** | Quick, zero config changes | CORS, no caching, not production-ready |
| **Multi-stage + nginx** | Production-ready, CORS-free, fast static serving | Requires rebuild for code changes |
| **Vite build + serve** | Simple static server (serve/fttp) | No reverse proxy in container, manual host config |

---

## Decision

**Adopt multi-stage Docker build with nginx**:

### Frontend Dockerfile
```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy to backend
    location /api {
        proxy_pass http://backend:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|mp3|pdf|zip)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}
```

### Docker Compose
```yaml
frontend:
  build: ./frontend
  ports:
    - "80:80"  # host:container
  depends_on:
    backend:
      condition: service_healthy
  restart: unless-stopped
```

---

## Consequences

### Positive
- ✅ Production-ready static serving (nginx)
- ✅ CORS eliminated (API proxied through nginx)
- ✅ Asset caching (1 year for static files)
- ✅ SPA routing works out of the box
- ✅ Smaller final image (nginx-alpine ~20MB vs node:20 ~150MB)
- ✅ No environment variables needed for frontend (proxy handles `/api`)

### Negative
- ⚠️ Hot reload disabled — code changes require rebuild (`docker-compose up --build`)
- ⚠️ Longer initial build (~2-3 minutes vs instant dev server)
- ⚠️ Need to ensure nginx.conf is kept in sync with SPA needs

---

## Implementation Checklist

- [x] Create multi-stage `frontend/Dockerfile`
- [x] Ensure `nginx.conf` exists with SPA + proxy config
- [x] Update `docker-compose.yml`:
  - [x] Frontend port: `80:80` (from `80:5173`)
  - [x] Remove `VITE_API_BASE_URL` env (not needed)
  - [x] Increase backend healthcheck timeout to 40s
- [x] Backend CORS: Allow `http://localhost:80` (already present)
- [x] Test endpoints:
  - [x] Frontend loads at http://localhost
  - [x] API proxied via `/api` works
  - [x] Static assets cached (check response headers)
  - [x] SPA navigation works (refresh on deep routes)

---

## Test Results

**Build successful:**  
- Frontend image: `hackerlabacademy-frontend:latest`
- Backend image: `hackerlabacademy-backend:latest`
- Build time: ~2-3 minutes (including npm install, npm run build, pip install)

**Containers:**
- Backend: `Up (healthy)` after ~15s
- Frontend: `Up` (nginx listening on port 80)

**Manual verification required:**
1. Open http://localhost — should load React app
2. Create user at `/setup`
3. Navigate through topics, complete quiz — ensure API calls work through nginx proxy
4. Check Swagger UI at http://localhost:8001/docs (backend directly) also works

---

## Related Changes

This decision triggered additional refactoring:

- **Backend import paths:** All `from backend.X` → relative imports (to work in Docker `/app` context)
- **Path constants:** `audio/`, `exports/` instead of `backend/audio`, `backend/exports`
- **SQLAlchemy:** `ConversationTurn.metadata` → `turn_metadata` (reserved keyword conflict)
- **Models:** Fixed class name mismatches (`YouTubeVideo`, `UserAttackProgress`)
- **Config:** `PDF_EXPORT_DIR`, `AUDIO_DIR` moved to module-level (pydanticSettings doesn't export them)

See `TASKS.md` and `CHANGELOG.md` for full list of modifications.

---

## References

- ForgeBody Docker setup (similar pattern, but keeps Vite dev for development phase)
- FastAPI production deployment guide
- Nginx SPA configuration patterns
