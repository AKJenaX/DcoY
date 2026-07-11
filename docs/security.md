# DcoY Security Framework

This document outlines the security architecture, data validation checks, and cryptography configurations embedded within DcoY.

---

## 🔒 1. Authentication & Session Management

DcoY implements a secure multi-layered authentication system to protect telemetry data and agent coordination pipelines:

* **Bearer Token Authentication (JWT)**:
  * Session endpoints (`/detect`, `/agents`, `/explain`, `/ask`, `/report`) require a JSON Web Token (JWT) transmitted via the HTTP `Authorization: Bearer <TOKEN>` header.
  * Tokens are cryptographically signed using the **HS256** algorithm.
  * Default fallback sessions (e.g. `"default_user"`) have been removed. Any unauthenticated or invalid token query returns a strict `401 Unauthorized` response.
* **API Key Ingestion Authentication**:
  * Machine-to-machine integrations (`/api/ingest` and `/api/capture`) are protected via high-entropy API keys passed in the `X-API-Key` HTTP header.
  * API keys are dynamically generated on-demand for registered operator profiles via the `/generate-api-key` endpoint.

---

## 🔑 2. Cryptographic Hardening

* **Bcrypt Password Hashing**:
  * Passwords are never stored in plaintext. They are hashed using a secure work factor salt via the native Python `bcrypt` library before being stored in the database.
  * Password verification uses timing-attack resistant comparisons.
* **Dynamic Secret Key Verification & Validation**:
  * The signing secret key `SECRET_KEY` is loaded from environment variables (or `.env` file).
  * **Startup Safety Constraints**:
    * **Development Mode (`DEBUG=True`)**: If `SECRET_KEY` is missing or insecure (less than 32 characters, or a common default name), a warning log is generated, and a secure temporary random 32-byte hex key is dynamically auto-generated for development friction reduction.
    * **Production Mode (`DEBUG=False`)**: The application strictly refuses to boot and raises a `ValueError` if the `SECRET_KEY` is missing or insecure (<32 characters, or default text).
  * **Session Lifetime**: JWT session tokens expire automatically after a configurable lifetime (`ACCESS_TOKEN_EXPIRE_MINUTES`, defaulting to 60 minutes).

---

## 🛠️ 3. Input Data Sanitization

* **Pydantic Validation**: All POST payloads (`/api/ingest`, `/register`, `/ask`) pass through unified Pydantic data schemas.
* **Type Enforcement**: Payload types are strictly checked (e.g. IP formats, numerical ranges for login failures). Input errors generate standard FastAPI `422 Unprocessable Entity` responses rather than causing server exceptions.

---

## ⚙️ 4. Required Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

```bash
# Debug Mode (set to False in production)
DEBUG=False

# JWT Secret Configuration
SECRET_KEY=at_least_32_characters_random_hex_string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 🕵️ 5. Vulnerability Reporting

Please review our [SECURITY.md](file:///c:/Users/Anup%20Kumar/Desktop/projects/dcoy/SECURITY.md) guidelines at the repository root before submitting vulnerability disclosures.
