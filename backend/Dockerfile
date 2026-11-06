# Backend - build context is the project root (docker-compose.yml), so the code keeps its
# package layout and `backend.main:app` imports work as in local runs (plan B2, 2026-11-03).
FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/

# Database, generated audio and exports live in volumes (docker-compose.yml)
RUN mkdir -p data audio exports

EXPOSE 8003

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8003"]
