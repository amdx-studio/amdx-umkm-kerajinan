"""
services/auth_service.py
VERSI TANPA JWT
Registrasi & Login sederhana
"""

import bcrypt
from db import get_db


# =========================================================
# HASH PASSWORD
# =========================================================
def hash_password(plain: str) -> str:
    """
    Hash password menggunakan bcrypt.
    """

    return bcrypt.hashpw(
        plain.encode(),
        bcrypt.gensalt(rounds=12)
    ).decode()


# =========================================================
# CHECK PASSWORD
# =========================================================
def check_password(plain: str, hashed: str) -> bool:
    """
    Verifikasi password plain vs hash.
    """

    return bcrypt.checkpw(
        plain.encode(),
        hashed.encode()
    )


# =========================================================
# REGISTER USER
# =========================================================
def register_user(nama: str, email: str, password: str) -> dict:

    db = get_db()

    # ── Cek email sudah ada ────────────────────────────
    existing = (
        db.table("users")
        .select("id")
        .eq("email", email)
        .execute()
    )

    if existing.data:

        return {
            "success": False,
            "message": "Email sudah terdaftar."
        }

    # ── Hash password ──────────────────────────────────
    pw_hash = hash_password(password)

    # ── Simpan user ────────────────────────────────────
    result = (
        db.table("users")
        .insert({
            "nama": nama,
            "email": email,
            "password": pw_hash
        })
        .execute()
    )

    if not result.data:

        return {
            "success": False,
            "message": "Gagal menyimpan user."
        }

    user = result.data[0]

    return {
        "success": True,
        "message": "Registrasi berhasil.",
        "user": {
            "id": user["id"],
            "nama": user["nama"],
            "email": user["email"]
        }
    }


# =========================================================
# LOGIN USER
# =========================================================
def login_user(email: str, password: str) -> dict:

    db = get_db()

    # ── Cari user ──────────────────────────────────────
    result = (
        db.table("users")
        .select("id, nama, email, password")
        .eq("email", email)
        .execute()
    )

    if not result.data:

        return {
            "success": False,
            "message": "Email atau password salah."
        }

    user = result.data[0]

    # ── Verifikasi password ────────────────────────────
    if not check_password(password, user["password"]):

        return {
            "success": False,
            "message": "Email atau password salah."
        }

    return {
        "success": True,
        "message": "Login berhasil.",
        "user": {
            "id": user["id"],
            "nama": user["nama"],
            "email": user["email"]
        }
    }