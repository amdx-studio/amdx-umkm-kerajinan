"""
routes/auth_routes.py
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
"""

from flask import Blueprint, request, jsonify
from services.auth_service import register_user, login_user
from db import get_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    nama = (data.get("nama", "") or "").strip()
    email = (data.get("email", "") or "").strip().lower()
    password = data.get("password", "") or ""

    if not all([nama, email, password]):
        return jsonify({
            "success": False,
            "message": "Nama, email, dan password wajib diisi."
        }), 400

    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password minimal 8 karakter."
        }), 400

    result = register_user(nama, email, password)

    status = 201 if result["success"] else 400

    return jsonify(result), status


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    email = (data.get("email", "") or "").strip().lower()
    password = data.get("password", "") or ""

    if not all([email, password]):
        return jsonify({
            "success": False,
            "message": "Email dan password wajib diisi."
        }), 400

    result = login_user(email, password)

    status = 200 if result["success"] else 401

    return jsonify(result), status


# SEMENTARA TANPA JWT
@auth_bp.get("/me")
def me():

    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id wajib dikirim."
        }), 400

    db = get_db()

    result = (
        db.table("users")
        .select("id, nama, email, created_at")
        .eq("id", int(user_id))
        .execute()
    )

    if not result.data:
        return jsonify({
            "success": False,
            "message": "User tidak ditemukan."
        }), 404

    return jsonify({
        "success": True,
        "user": result.data[0]
    })