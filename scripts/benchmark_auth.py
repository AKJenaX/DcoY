import time
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

if sys.platform == "win32":
    try:
        getattr(sys.stdout, "reconfigure")(encoding="utf-8")
    except Exception:
        pass

import bcrypt
from app.utils.auth_utils import hash_password, verify_password, create_access_token, decode_access_token
from app.config import settings

print("🛡️ DcoY Security Hardening Latency Benchmarks\n")

# 1. Hashing Latency
start = time.perf_counter()
h = hash_password("operator_password")
hash_latency = (time.perf_counter() - start) * 1000
print(f"🔑 Password Hashing (Bcrypt gensalt): {hash_latency:.2f} ms")

# 2. Verification Latency
start = time.perf_counter()
match = verify_password("operator_password", h)
verify_latency = (time.perf_counter() - start) * 1000
print(f"✅ Password Verification (Match): {verify_latency:.2f} ms (Result: {match})")

# 3. Failed Verification Latency
start = time.perf_counter()
mismatch = verify_password("wrong_password", h)
failed_verify_latency = (time.perf_counter() - start) * 1000
print(f"❌ Password Verification (Mismatch): {failed_verify_latency:.2f} ms (Result: {mismatch})")

# 4. Token Creation Latency
start = time.perf_counter()
token = create_access_token({"user": "operator"})
token_create_latency = (time.perf_counter() - start) * 1000
print(f"🎫 JWT Signature Token Creation: {token_create_latency:.2f} ms")

# 5. Token Decoding Latency
start = time.perf_counter()
decoded = decode_access_token(token)
token_decode_latency = (time.perf_counter() - start) * 1000
print(f"🔍 JWT Signature Token Verification: {token_decode_latency:.2f} ms (Result user: {decoded.get('user') if decoded else None})")
