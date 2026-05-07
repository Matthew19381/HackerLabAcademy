# 🐳 HackerLabAcademy — Docker Deployment Guide

**Data:** 2026-04-02

---

## 📋 Requirements

- Docker Desktop (or Docker Engine + Docker Compose)
- GEMINI_API_KEY from https://aistudio.google.com/app/apikey

---

## 🚀 Quick Start (3 Steps)

### 1. Prepare Environment File

```bash
cd "G:\Mój dysk\NowaNadzieja\Praca\ClaudeCode\03_Projects\HackerLabAcademy"

# Copy example env
cp .env.example .env

# Edit .env and add your GEMINI_API_KEY
# Use any text editor (Notepad, VS Code, etc.)
```

**`.env` file content:**
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
CVE_SCHEDULED_FETCH=false  # optional: true to auto-fetch CVEs daily
```

### 2. Build & Start

```bash
# Build images and start containers
docker-compose up --build
```

**First build will take 2-5 minutes** (downloads base images, installs dependencies).

### 3. Access Application

- **Frontend (app):** http://localhost
- **Backend API docs:** http://localhost:8001/docs
- **Health check:** http://localhost:8001/api/health

---

## 🎯 First Time Setup

1. Open http://localhost in browser
2. You'll see `/setup` page — create your user (name + user_id)
3. Click "Create User"
4. You're redirected to Dashboard
5. Start learning!

---

## 🐛 Troubleshooting

### "GEMINI_API_KEY not set" or AI errors

**Check:** Backend container has the env var.

```bash
# View backend logs
docker-compose logs backend

# Should show: "GEMINI_API_KEY is set" or similar
```

**Fix:** Stop containers, edit `.env`, restart:

```bash
docker-compose down
# Edit .env, save
docker-compose up --build
```

### Port 80 already in use

**Error:** "Bind for 0.0.0.0:80 failed: port is already allocated"

**Fix:** Change frontend port in `docker-compose.yml`:

```yaml
frontend:
  ports:
    - "8080:80"  # instead of "80:80"
```

Then access http://localhost:8080

### Database not initialized / tables missing

**Symptom:** 404 errors on endpoints, empty topics.

**Fix:** Recreate database (volume must be cleared):

```bash
docker-compose down -v  # ⚠️ removes all data!
docker-compose up --build
```

### Files (PDF/audio) not persisting

Docker uses named volume `backend_data`. Files are stored in:
- Database: `backend_data/HackerLabAcademy.db`
- Audio: `backend_data/audio/`
- Exports: `backend_data/exports/`

To backup/restore, see "Data Management" below.

---

## 🔄 Common Commands

| Action | Command |
|--------|---------|
| Start (detached) | `docker-compose up -d` |
| Stop | `docker-compose stop` |
| Stop & remove containers | `docker-compose down` |
| Stop, remove containers + volumes (⚠️ delete data) | `docker-compose down -v` |
| View logs (all services) | `docker-compose logs -f` |
| View logs (backend only) | `docker-compose logs -f backend` |
| View logs (frontend only) | `docker-compose logs -f frontend` |
| Rebuild & restart | `docker-compose up --build` |
| Execute command in backend container | `docker-compose exec backend bash` |
| Check container status | `docker-compose ps` |

---

## 💾 Data Management

### Backup Database

```bash
# Create backup of SQLite DB
docker-compose exec backend cp /app/HackerLabAcademy.db /tmp/backup.db

# Copy from container to host
docker cp $(docker-compose ps -q backend):/tmp/backup.db ./HackerLabAcademy_backup.db
```

### Restore Database

```bash
# Copy backup into container
docker cp ./HackerLabAcademy_backup.db $(docker-compose ps -q backend):/tmp/restore.db

# Stop services, replace DB, start
docker-compose down
docker-compose exec backend cp /tmp/restore.db /app/HackerLabAcademy.db
docker-compose up -d
```

### Volume Location (Docker Desktop)

On Windows with Docker Desktop, volume data stored in:
```
%USERPROFILE%\AppData\Local\Docker\volumes\hackerlabacademy_backend_data\
```

You can backup entire folder while containers are stopped.

---

## ⚙️ Configuration

### Enable CVE Auto-Fetch

Edit `.env`:

```env
CVE_SCHEDULED_FETCH=true
```

Restart:

```bash
docker-compose down
docker-compose up -d
```

Backend will fetch CVEs every 24 hours starting at container launch.

---

## 🏗️ Build Customization

### Change Backend Port

Edit `docker-compose.yml`:

```yaml
backend:
  ports:
    - "8081:8001"  # host:container
```

Then http://localhost:8081 (but frontend proxy expects backend:8001 internally — keep as is unless you know what you're doing).

---

## 🧪 Testing the Deployment

```bash
# 1. Health check
curl http://localhost:8001/api/health
# Expected: {"status":"ok","app":"HackerLabAcademy"}

# 2. Topics list (after creating user)
# First get your user_id from localStorage in browser DevTools
# Then:
curl "http://localhost:8001/api/topics/?user_id=1"

# 3. Generate lesson (triggers AI)
curl -X POST "http://localhost:8001/api/topics/http-basics/theory?user_id=1"
```

---

## 📁 Project Structure (Docker)

```
HackerLabAcademy/
├── docker-compose.yml
├── .env                    ← your secrets (NOT in git)
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── main.py
│   └── ... (all backend code)
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── nginx.conf
│   ├── dist/               ← built by Docker, served by nginx
│   └── ... (all frontend code)
└── volumes/
    └── backend_data/       ← created by Docker (DB, audio, exports)
```

---

## 🔓 Security Notes

- **Development only:** This setup is for personal/local use.
- **No auth:** System uses simple user_id localStorage (no passwords).
- **API exposed:** Backend Swagger UI available at http://localhost:8001/docs.
- **No HTTPS:** For production, add SSL/TLS (certbot + nginx).

---

## 🚢 Production Deployment (VPS)

1. Push code to GitHub
2. On VPS:
   ```bash
   git clone <your-repo>
   cd HackerLabAcademy
   cp .env.example .env
   # Edit .env with production GEMINI_API_KEY
   docker-compose up -d
   ```
3. Configure firewall: allow ports 80 (HTTP) and 8001 (optional API)
4. (Optional) Add nginx reverse proxy with SSL in front

---

## 🐛 Known Issues

| Issue | Workaround |
|-------|------------|
| First lesson generation slow | Wait 5-10 seconds, Gemini API cold start |
| Mindmap D3 errors if built without d3 | `npm install` runs in Docker build, should be fine |
| Audio generation fails | Check GEMINI_API_KEY, edge-tts requires voice pack (usually preinstalled) |
| PDF blank pages | fpdf2 font issue — usually fine with default |

---

## 📞 Support

Check logs:
```bash
docker-compose logs -f backend  # for API errors
docker-compose logs -f frontend # for build/serve errors
```

---

**Enjoy your HackerLabAcademy! 🎓**
