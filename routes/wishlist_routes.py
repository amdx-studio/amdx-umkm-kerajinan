"""
routes/wishlist_routes.py
VERSI TANPA JWT
"""

from flask import Blueprint, request, jsonify
from db import get_db

wishlist_bp = Blueprint("wishlist", __name__)


# =========================================================
# GET WISHLIST
# GET /api/wishlist/?user_id=1
# =========================================================
@wishlist_bp.get("/")
def get_wishlist():

    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id wajib dikirim."
        }), 400

    try:
        user_id = int(user_id)

    except ValueError:
        return jsonify({
            "success": False,
            "message": "user_id harus angka."
        }), 400

    db = get_db()

    resp = (
        db.table("wishlist")
        .select("produk_id, created_at")
        .eq("user_id", user_id)
        .execute()
    )

    produk_ids = [
        r["produk_id"]
        for r in (resp.data or [])
    ]

    if not produk_ids:
        return jsonify({
            "success": True,
            "data": []
        })

    # ── Ambil detail produk ───────────────────────────
    p_resp = (
        db.table("produk")
        .select("id, nama, harga, gambar_url, rating_avg")
        .in_("id", produk_ids)
        .execute()
    )

    return jsonify({
        "success": True,
        "total": len(p_resp.data or []),
        "data": p_resp.data or []
    })


# =========================================================
# TAMBAH WISHLIST
# POST /api/wishlist/
# =========================================================
@wishlist_bp.post("/")
def tambah_wishlist():

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    produk_id = data.get("produk_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id wajib diisi."
        }), 400

    if not produk_id:
        return jsonify({
            "success": False,
            "message": "produk_id wajib diisi."
        }), 400

    try:
        user_id = int(user_id)
        produk_id = int(produk_id)

    except ValueError:
        return jsonify({
            "success": False,
            "message": "Format data tidak valid."
        }), 400

    db = get_db()

    # ── Cek duplikat ───────────────────────────────────
    existing = (
        db.table("wishlist")
        .select("id")
        .eq("user_id", user_id)
        .eq("produk_id", produk_id)
        .execute()
    )

    if existing.data:
        return jsonify({
            "success": False,
            "message": "Produk sudah ada di wishlist."
        }), 409

    # ── Insert ─────────────────────────────────────────
    (
        db.table("wishlist")
        .insert({
            "user_id": user_id,
            "produk_id": produk_id
        })
        .execute()
    )

    return jsonify({
        "success": True,
        "message": "Ditambahkan ke wishlist."
    }), 201


# =========================================================
# HAPUS WISHLIST
# DELETE /api/wishlist/<produk_id>?user_id=1
# =========================================================
@wishlist_bp.delete("/<int:produk_id>")
def hapus_wishlist(produk_id):

    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id wajib dikirim."
        }), 400

    try:
        user_id = int(user_id)

    except ValueError:
        return jsonify({
            "success": False,
            "message": "user_id harus angka."
        }), 400

    db = get_db()

    (
        db.table("wishlist")
        .delete()
        .eq("user_id", user_id)
        .eq("produk_id", produk_id)
        .execute()
    )

    return jsonify({
        "success": True,
        "message": "Dihapus dari wishlist."
    })