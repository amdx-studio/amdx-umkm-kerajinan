"""
routes/keranjang_routes.py
VERSI TANPA JWT
"""

from flask import Blueprint, request, jsonify
from db import get_db

keranjang_bp = Blueprint("keranjang", __name__)


# =========================================================
# GET KERANJANG
# GET /api/keranjang/?user_id=1
# =========================================================
@keranjang_bp.get("/")
def get_keranjang():

    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id wajib dikirim."
        }), 400

    user_id = int(user_id)

    db = get_db()

    resp = (
        db.table("keranjang")
        .select("produk_id, jumlah, created_at")
        .eq("user_id", user_id)
        .execute()
    )

    items = resp.data or []

    if not items:
        return jsonify({
            "success": True,
            "data": [],
            "total_harga": 0
        })

    produk_ids = [i["produk_id"] for i in items]

    p_resp = (
        db.table("produk")
        .select("id, nama, harga, gambar_url, stok")
        .in_("id", produk_ids)
        .execute()
    )

    produk_map = {
        p["id"]: p for p in (p_resp.data or [])
    }

    result = []
    total_harga = 0

    for item in items:

        pid = item["produk_id"]

        p = produk_map.get(pid, {})

        subtotal = float(p.get("harga", 0)) * item["jumlah"]

        total_harga += subtotal

        result.append({
            "produk_id": pid,
            "nama": p.get("nama", "-"),
            "harga": float(p.get("harga", 0)),
            "gambar_url": p.get("gambar_url", ""),
            "stok": p.get("stok", 0),
            "jumlah": item["jumlah"],
            "subtotal": subtotal,
        })

    return jsonify({
        "success": True,
        "data": result,
        "total_harga": total_harga
    })


# =========================================================
# TAMBAH KERANJANG
# POST /api/keranjang/
# =========================================================
@keranjang_bp.post("/")
def tambah_keranjang():

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    produk_id = data.get("produk_id")
    jumlah = int(data.get("jumlah", 1))

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id wajib diisi."
        }), 400

    if not produk_id or jumlah < 1:
        return jsonify({
            "success": False,
            "message": "produk_id dan jumlah wajib diisi."
        }), 400

    user_id = int(user_id)

    db = get_db()

    existing = (
        db.table("keranjang")
        .select("id, jumlah")
        .eq("user_id", user_id)
        .eq("produk_id", produk_id)
        .execute()
    )

    # kalau produk sudah ada
    if existing.data:

        new_jumlah = existing.data[0]["jumlah"] + jumlah

        (
            db.table("keranjang")
            .update({"jumlah": new_jumlah})
            .eq("user_id", user_id)
            .eq("produk_id", produk_id)
            .execute()
        )

        return jsonify({
            "success": True,
            "message": "Jumlah diperbarui."
        })

    # insert baru
    (
        db.table("keranjang")
        .insert({
            "user_id": user_id,
            "produk_id": produk_id,
            "jumlah": jumlah
        })
        .execute()
    )

    return jsonify({
        "success": True,
        "message": "Produk ditambahkan ke keranjang."
    }), 201


# =========================================================
# UPDATE JUMLAH
# PATCH /api/keranjang/<produk_id>
# =========================================================
@keranjang_bp.patch("/<int:produk_id>")
def update_jumlah(produk_id):

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    jumlah = data.get("jumlah")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id wajib diisi."
        }), 400

    if jumlah is None or int(jumlah) < 1:
        return jsonify({
            "success": False,
            "message": "Jumlah tidak valid."
        }), 400

    user_id = int(user_id)

    db = get_db()

    (
        db.table("keranjang")
        .update({"jumlah": int(jumlah)})
        .eq("user_id", user_id)
        .eq("produk_id", produk_id)
        .execute()
    )

    return jsonify({
        "success": True,
        "message": "Jumlah diperbarui."
    })


# =========================================================
# HAPUS ITEM
# DELETE /api/keranjang/<produk_id>?user_id=1
# =========================================================
@keranjang_bp.delete("/<int:produk_id>")
def hapus_item(produk_id):

    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id wajib dikirim."
        }), 400

    user_id = int(user_id)

    db = get_db()

    (
        db.table("keranjang")
        .delete()
        .eq("user_id", user_id)
        .eq("produk_id", produk_id)
        .execute()
    )

    return jsonify({
        "success": True,
        "message": "Item dihapus dari keranjang."
    })


# =========================================================
# KOSONGKAN KERANJANG
# DELETE /api/keranjang/?user_id=1
# =========================================================
@keranjang_bp.delete("/")
def kosongkan():

    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id wajib dikirim."
        }), 400

    user_id = int(user_id)

    db = get_db()

    (
        db.table("keranjang")
        .delete()
        .eq("user_id", user_id)
        .execute()
    )

    return jsonify({
        "success": True,
        "message": "Keranjang dikosongkan."
    })