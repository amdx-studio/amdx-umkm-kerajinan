"""
routes/rating_routes.py
VERSI TANPA JWT
"""

from flask import Blueprint, request, jsonify
from db import get_db

rating_bp = Blueprint("rating", __name__)


# =========================================================
# POST RATING
# POST /api/rating/
# =========================================================
@rating_bp.post("/")
def beri_rating():

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    produk_id = data.get("produk_id")
    nilai = data.get("nilai")

    # ── Validasi ─────────────────────────────────────────
    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id wajib diisi."
        }), 400

    if produk_id is None or nilai is None:
        return jsonify({
            "success": False,
            "message": "produk_id dan nilai wajib diisi."
        }), 400

    try:
        user_id = int(user_id)
        produk_id = int(produk_id)
        nilai = int(nilai)

        assert 1 <= nilai <= 5

    except (ValueError, AssertionError):

        return jsonify({
            "success": False,
            "message": "Nilai rating harus antara 1–5."
        }), 400

    db = get_db()

    # ── Cek rating sebelumnya ───────────────────────────
    existing = (
        db.table("rating")
        .select("id")
        .eq("user_id", user_id)
        .eq("produk_id", produk_id)
        .execute()
    )

    # ── UPDATE ──────────────────────────────────────────
    if existing.data:

        resp = (
            db.table("rating")
            .update({
                "nilai": nilai
            })
            .eq("user_id", user_id)
            .eq("produk_id", produk_id)
            .execute()
        )

        aksi = "diperbarui"

    # ── INSERT ──────────────────────────────────────────
    else:

        resp = (
            db.table("rating")
            .insert({
                "user_id": user_id,
                "produk_id": produk_id,
                "nilai": nilai
            })
            .execute()
        )

        aksi = "ditambahkan"

    # ── Update rating average produk ───────────────────
    _update_rating_avg(db, produk_id)

    return jsonify({
        "success": True,
        "message": f"Rating {aksi}.",
        "data": resp.data[0] if resp.data else {}
    }), 201


# =========================================================
# UPDATE RATING AVG PRODUK
# =========================================================
def _update_rating_avg(db, produk_id):

    resp = (
        db.table("rating")
        .select("nilai")
        .eq("produk_id", produk_id)
        .execute()
    )

    values = [r["nilai"] for r in (resp.data or [])]

    if values:

        avg = round(sum(values) / len(values), 2)

        (
            db.table("produk")
            .update({
                "rating_avg": avg
            })
            .eq("id", produk_id)
            .execute()
        )


# =========================================================
# GET RATING USER
# GET /api/rating/user?user_id=1
# =========================================================
@rating_bp.get("/user")
def rating_by_user():

    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id wajib dikirim."
        }), 400

    user_id = int(user_id)

    db = get_db()

    resp = (
        db.table("rating")
        .select("produk_id, nilai, created_at")
        .eq("user_id", user_id)
        .execute()
    )

    return jsonify({
        "success": True,
        "data": resp.data or []
    })


# =========================================================
# GET RATING PRODUK
# GET /api/rating/produk/<id>
# =========================================================
@rating_bp.get("/produk/<int:produk_id>")
def rating_by_produk(produk_id):

    db = get_db()

    resp = (
        db.table("rating")
        .select("user_id, nilai, created_at")
        .eq("produk_id", produk_id)
        .execute()
    )

    values = [r["nilai"] for r in (resp.data or [])]

    avg = round(sum(values) / len(values), 2) if values else 0

    return jsonify({
        "success": True,
        "produk_id": produk_id,
        "total": len(values),
        "rata_rata": avg,
        "data": resp.data or [],
    })