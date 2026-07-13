# Multi-stage builder for DcoY security hardening
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

# Compile requirements to local packages
RUN pip install --no-cache-dir --user -r requirements.txt

# Runner stage
FROM python:3.11-slim AS runner

WORKDIR /app

# Create a non-privileged user and group
RUN groupadd -r dcoy && useradd -r -g dcoy -d /home/dcoy -m dcoy

# Copy built python packages
COPY --from=builder /root/.local /home/dcoy/.local
COPY --chown=dcoy:dcoy . .

# Update path to resolve locally installed binaries
ENV PATH=/home/dcoy/.local/bin:$PATH

USER dcoy

EXPOSE 8000

# Run FastAPI service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
