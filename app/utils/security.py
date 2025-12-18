# app/utils/security.py

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# 🔐 Argon2 configuration (safe defaults)
pwd_hasher = PasswordHasher(
    time_cost=3,        # iterations
    memory_cost=65536,  # 64 MB
    parallelism=4,
    hash_len=32,
    salt_len=16
)

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using Argon2.
    """
    return pwd_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against the stored Argon2 hash.
    """
    try:
        return pwd_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
