# DcoY Enterprise Security Platform - Deployment & Release Manual (v1.0.0)

**Document Version:** 1.0.0  
**Target Release:** v1.0.0 General Availability (GA)  
**Author:** Senior DevOps & Release Engineering  
**Classification:** Internal Operational Guide  

---

## 1. Deployment Readiness Audit Summary

The DcoY Enterprise Threat Defense and Deception Platform has completed architectural modularization, authentication persistence, and operational observability hardening.

| Audit Dimension | Status | Verification & Readiness Notes |
| :--- | :---: | :--- |
| **Backend API Modularization** | **PASSED** | Aggregated entry point [`backend/app/main.py`](file:///c:/Users/Anup%20Kumar/Desktop/projects/dcoy/backend/app/main.py) refactored to 85 lines across 10 APIRouter modules. |
| **Auth Persistence** | **PASSED** | Persistent `DBUser` and `DBApiKey` tables with SHA-256 key hashing and constant-time validation (`hmac.compare_digest`). |
| **Operational Observability** | **PASSED** | `X-Request-ID` correlation middleware, JSON structured logger, `/health/live`, `/health/ready`, and `/metrics` telemetry endpoints. |
| **Test Suite Pass Rate** | **PASSED** | **101 / 101 backend unit & integration tests passing** with 0 Pyright errors (`0 errors, 0 warnings`). |
| **OpenAPI Schema Stability** | **PASSED** | OpenAPI v3 spec generates 72.4 KB schema with domain tags and summaries. |
| **Containerization** | **PASSED** | Multi-stage [`backend/Dockerfile`](file:///c:/Users/Anup%20Kumar/Desktop/projects/dcoy/backend/Dockerfile) and [`frontend/Dockerfile`](file:///c:/Users/Anup%20Kumar/Desktop/projects/dcoy/frontend/Dockerfile) with Nginx reverse proxy. |

---

## 2. Docker & Containerization Infrastructure

### Backend Container (`dcoy_backend`)
- **Base Image:** `python:3.11-slim` multi-stage build.
- **Security:** Non-root runtime user (`dcoy:dcoy`).
- **Healthcheck:** Probes `http://localhost:8001/health/ready` every 15s.

### Frontend Container (`dcoy_frontend`)
- **Base Image:** `node:20-alpine` (builder) $\rightarrow$ `nginx:1.25-alpine` (runner).
- **Reverse Proxy:** Pre-configured Nginx routing `/api/`, `/register`, `/login`, `/health`, and `/ws/` WebSocket upgrade streams.

```bash
# Build production images locally
docker-compose build --no-cache
```

---

## 3. Environment & Secret Management

### Production Environment Variables (`production.env.example`)
Copy [`production.env.example`](file:///c:/Users/Anup%20Kumar/Desktop/projects/dcoy/production.env.example) to `.env` on your target server:

```ini
ENV=production
DEBUG=false
PORT=8001
SECRET_KEY=SECURE_RANDOM_64_CHARACTER_KEY_GENERATE_WITH_OPENSSL
CORS_ORIGINS=https://dcoy.yourdomain.com
DATABASE_URL=sqlite:///./dcoy.db
LOG_LEVEL=INFO
LOG_FORMAT_JSON=true
```

### Secret Generation Commands
```bash
# Generate 64-character hex secret key for JWT signing
openssl rand -hex 32
```

---

## 4. HTTPS & TLS 1.3 Configuration

In production, terminate TLS 1.3 at your edge load balancer (Nginx / Cloudflare / AWS ALB / Traefik):

```nginx
# Sample HTTPS Nginx Edge Termination Configuration
server {
    listen 443 ssl http2;
    server_name dcoy.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/dcoy.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dcoy.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

---

## 5. v1.0.0 Release Checklist

- [x] All 101 pytest backend unit & integration tests pass cleanly.
- [x] Pyright type diagnostics return `0 errors, 0 warnings`.
- [x] Database migrations verified with Alembic (`001_create_auth_tables.py`).
- [x] FastAPI lifespan startup logic consolidated and idempotent.
- [x] In-memory authentication dicts replaced with database persistence.
- [x] Plaintext API keys replaced with SHA-256 hashed storage.
- [x] Production environment template generated (`production.env.example`).
- [x] Multi-stage Frontend Nginx Dockerfile created.
- [x] Docker Compose multi-service orchestrator configured.
- [x] Readiness `/health/ready` probe verifies DB and security engine availability.

---

## 6. Deployment Commands

### Option A: Docker Compose Deployment (Recommended)

```bash
# 1. Clone repository on target production host
git clone https://github.com/AKJenaX/DcoY.git /opt/dcoy
cd /opt/dcoy

# 2. Configure production environment file
cp production.env.example .env
nano .env  # Update SECRET_KEY and CORS_ORIGINS

# 3. Pull and build containers
docker-compose build --no-cache

# 4. Launch services in detached background mode
docker-compose up -d

# 5. Inspect service status & health
docker-compose ps
docker-compose logs -f --tail=50
```

### Option B: Kubernetes Deployment (K8s Manifest Summary)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dcoy-backend
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: backend
        image: dcoy/backend:v1.0.0
        ports:
        - containerPort: 8001
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 15
```

---

## 7. Zero-Downtime Rollback Plan

If a critical issue is discovered post-release:

### Step 1: Immediate Container Image Rollback
```bash
# Revert to previous release image tag in docker-compose
docker-compose down
docker-compose up -d --build --pull
```

### Step 2: Database Migration Downgrade (If Schema Changed)
```bash
cd backend
.\.venv\Scripts\python.exe -m alembic downgrade -1
```

### Step 3: Cache & Connection Purge
```bash
docker-compose restart backend
```

---

## 8. Post-Deployment Verification Checklist (Smoketests)

Execute these operational verification steps immediately after deployment:

```bash
# 1. Verify Liveness Probe
curl -f -s http://localhost:8001/health/live

# 2. Verify Readiness Probe (Checks DB + Service Container)
curl -f -s http://localhost:8001/health/ready

# 3. Verify Operational Telemetry Metrics
curl -f -s http://localhost:8001/metrics

# 4. Test User Authentication Endpoint
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{"username":"operator","password":"secure_password"}'

# 5. Verify Frontend SPA Index Load
curl -I http://localhost:80
```
