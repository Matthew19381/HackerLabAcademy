# 🐳 Docker Deployment — Test & Fix Guide

**Data:** 2026-04-02

---

## 📋 Pre-Flight Checklist

### ✅ Required Files (All Present)

| File | Purpose | Status |
|------|---------|--------|
| `backend/Dockerfile` | Python + FastAPI image | ✅ |
| `frontend/Dockerfile` | Node → nginx multi-stage | ✅ |
| `docker-compose.yml` | Orchestration | ✅ |
| `frontend/nginx.conf` | Proxy config | ✅ |
| `backend/.dockerignore` | Exclude noise | ✅ |
| `frontend/.dockerignore` | Exclude noise | ✅ |
| `backend/requirements.txt` | Python deps | ✅ (httpx added) |
| `frontend/package.json` | Node deps | ✅ (react-markdown added) |
| `.env.example` | Config template | ✅ (AI provider options) |
| `backend/main.py` | App entry with CORS | ✅ (localhost:80 added) |

---

## 🚀 Step-by-Step Test

### **Step 1: Prepare .env**

```bash
cd "G:\Mój dysk\NowaNadzieja\Praca\ClaudeCode\03_Projects\HackerLabAcademy"

# Copy template
copy .env.example .env   # CMD
# or: cp .env.example .env   # bash
```

**Edit `.env`** — Choose your AI provider:

**Option A: Gemini (cloud)**
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_actual_key_here
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
CVE_SCHEDULED_FETCH=false
```

**Option B: Ollama (local)**
```env
AI_PROVIDER=ollama
GEMINI_API_KEY=  # leave empty
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
CVE_SCHEDULED_FETCH=false
```

**Option C: Auto (fallback)**
```env
AI_PROVIDER=auto
GEMINI_API_KEY=your_key_here  # optional but recommended
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

---

### **Step 2: Ensure External Services Running**

#### If using Ollama (AI_PROVIDER=ollama or auto):

```bash
# In a separate terminal (outside Docker)
ollama serve

# In another terminal, pull model:
ollama pull llama3
# or: ollama pull deepseek-coder-v2:16b
# or: ollama pull qwen2.5:7b
```

**Verify Ollama is running:**
```bash
curl http://localhost:11434/api/tags
# Should return JSON with models list
```

---

### **Step 3: Build Docker Images**

```bash
docker-compose down -v  # Cleanup any previous

docker-compose up --build
```

**Watch the output carefully.** You should see:

```
backend_1   | INFO:     Application startup complete.
frontend_1  | ...
```

**If build fails**, note the error message.

---

### **Step 4: Check Container Status**

```bash
docker-compose ps
```

Expected:
```
NAME                IMAGE               STATUS          PORTS
backend     ...backend   Up (healthy)   0.0.0.0:8001->8001/tcp
frontend    ...frontend  Up             0.0.0.0:80->80/tcp
```

**Healthcheck** shows `(healthy)` after a few seconds.

---

### **Step 5: Test Endpoints**

#### Backend Health
```bash
curl http://localhost:8001/api/health
```
Expected: `{"status":"ok","app":"HackerLabAcademy"}`

#### Backend API Docs
Open: http://localhost:8001/docs  
Should show Swagger UI with all endpoints.

#### Frontend
Open: http://localhost  
Should load React app (green "HackerLabAcademy" header).

---

## 🐛 Troubleshooting Table

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| **Backend fails to start: `No module named 'httpx'`** | Dependencies not updated | Ensure `httpx` in `requirements.txt`. Rebuild: `docker-compose down && docker-compose up --build` |
| **Frontend shows blank page / build error** | `react-markdown` missing | Ensure `react-markdown` in `package.json`. Rebuild frontend: `docker-compose build --no-cache frontend` |
| **CORS error in browser console** | Frontend origin not in CORS list | Check `backend/main.py` CORS includes `http://localhost` and `http://localhost:80`. Rebuild backend. |
| **`/api/health` returns 500** | DB init failed | Check backend logs: `docker-compose logs backend`. May need to clear volume: `docker-compose down -v` and rebuild. |
| **AI calls fail (Gemini)** | `GEMINI_API_KEY` not set or invalid | Verify `.env` has correct key. Check backend logs for "Invalid API key". |
| **AI calls fail (Ollama)** | Ollama not running or wrong URL | 1. Run `ollama serve` on host. 2. Verify `OLLAMA_BASE_URL` is `http://host.docker.internal:11434` for Docker Desktop. Test: `curl http://localhost:11434/api/tags` from host. |
| **Port 80 already in use** | Another service (IIS, Apache, nginx) | Change frontend port in `docker-compose.yml`: `ports: - "8080:80"`. Then access http://localhost:8080 |
| **PDF/audio generation fails** | Missing fonts or edge-tts issues | Check backend logs. Ensure `edge-tts` package installed (in requirements.txt). Edge TTS requires voice data — usually bundled. |
| **Cannot connect to backend from frontend** | Nginx proxy misconfigured | Verify `frontend/nginx.conf` has `proxy_pass http://backend:8001;`. Check Docker network: `docker network ls` should show `default` network. |
| **Mindmap D3 errors** | D3 not installed | `d3` is in `package.json`. Rebuild frontend. |
| **Container keeps restarting** | Healthcheck failing | Increase healthcheck timeout: in `docker-compose.yml`, change `timeout: 10s` → `timeout: 30s`. |
| **Database tables not created** | Seed functions failing | Check logs for seed errors. Manually create: `docker-compose exec backend python -c "from backend.main import lifespan; import asyncio; asyncio.run(lifespan(None))"` |

---

## 🔍 Deep Diagnostics

### **Check Backend Logs**
```bash
docker-compose logs -f backend
```

Look for:
- `Application startup complete.` → OK
- `Seeded X topics` → DB seeded
- `Added X new CVEs` → CVE seed OK
- `Gemini AI service loaded` or `Ollama AI service loaded` → AI provider loaded
- Errors in red: `ImportError`, `ModuleNotFoundError` → missing Python package
- `ConnectionError` to Ollama → Ollama not running or wrong URL

### **Check Frontend Logs**
```bash
docker-compose logs -f frontend
```

Look for:
- `listening on port 80` → Nginx started
- Build errors during image build (run `docker-compose build frontend` to see full build output)
- 404 errors for `/api/...` → Nginx proxy misconfigured

### **Execute Commands in Container**

```bash
# Backend shell
docker-compose exec backend bash

# Inside container, test:
python -c "import httpx; print('httpx OK')"
python -c "import fpdf; print('fpdf OK')"
python -c "import edge_tts; print('edge-tts OK')"
python -c "import genanki; print('genanki OK')"

# Check if AI provider loads:
python -c "from backend.services.ai_service import generate_text; print('ai_service OK')"

# Exit
exit
```

---

## 🎯 Common Fixes

### **Fix 1: Rebuild with No Cache**
If Docker uses cached layers and misses new packages:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### **Fix 2: Clear Volume (Reset Database)**
If DB is corrupted or migrations failed:

```bash
docker-compose down -v   # ⚠️ deletes all data
docker-compose up --build
```

### **Fix 3: Add Missing Python Package**
If logs show `ModuleNotFoundError: No module named 'xyz'`:

1. Add to `backend/requirements.txt`
2. Rebuild:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### **Fix 4: Fix CORS**
If frontend gets CORS errors:

In `backend/main.py`, ensure:
```python
allow_origins=[
    "http://localhost",
    "http://localhost:80",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
    # ... other origins
]
```

Rebuild backend.

### **Fix 5: Ollama Connection (Docker Desktop)**
On Windows/Mac, Docker containers cannot reach `localhost:11434` directly. Use `host.docker.internal`:

In `.env`:
```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Rebuild and restart.

On Linux (Docker native), use:
```env
OLLAMA_BASE_URL=http://172.17.0.1:11434
```

---

## 📊 Expected Behavior

### **First Load (Slow)**
- First lesson generation: 5-10 seconds (Gemini API call)
- PDF generation: 2-3 seconds
- Audio generation: 3-5 seconds
- Mindmap D3: instant after npm install

### **Performance**
- Backend API: < 100ms for simple queries
- Frontend: instant routing (SPA)
- Static assets cached 1 year (nginx)

---

## ✅ Success Criteria

- [ ] `docker-compose ps` shows both containers `Up (healthy)`
- [ ] http://localhost loads React app
- [ ] Can create user at `/setup`
- [ ] Can generate lesson for a topic (AI responds)
- [ ] Can complete quiz and earn XP
- [ ] Can review flashcards (audio plays)
- [ ] Can view `/articles` and complete article quiz
- [ ] `/api/health` returns `{"status":"ok"}`
- [ ] No CORS errors in browser console
- [ ] AI provider logs: "Gemini AI service loaded" or "Ollama AI service loaded"

---

## 🆘 Emergency Reset

If everything is broken:

```bash
# Stop and remove everything
docker-compose down -v

# Rebuild from scratch
docker-compose up --build

# If still failing, check logs
docker-compose logs -f
```

---

**If issues persist, capture:**
1. `docker-compose logs -f` output (last 50 lines)
2. `docker-compose ps` output
3. Browser console errors (F12 → Console)
4. Network tab failures (F12 → Network)
