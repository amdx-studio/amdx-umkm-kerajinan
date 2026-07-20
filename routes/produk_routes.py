"""
routes/produk_routes.py
GET  /api/produk/                 → semua produk (+ filter, sort, search)
GET  /api/produk/<id>             → detail satu produk
GET  /api/produk/kategori/list    → daftar kategori
"""

from flask import Blueprint, request, jsonify
from db import get_db

produk_bp = Blueprint("produk", __name__)


def _build_produk_response(
    produk: dict,
    kategori_map: dict
) -> dict:

    gambar = produk.get("gambar_url", "")

    gambar_url = (
        request.host_url +
        "static/uploads/" +
        gambar
    ) if gambar else ""

    return {
        "id": produk["id"],
        "nama": produk["nama"],
        "deskripsi": produk.get("deskripsi", ""),
        "harga": float(produk["harga"]),
        "stok": produk.get("stok", 0),

        "gambar_url": gambar_url,

        "kategori":
            kategori_map.get(
                produk.get("kategori_id"),
                "-"
            ),

        "kategori_id":
            produk.get("kategori_id"),

        "rating_avg":
            float(
                produk.get("rating_avg") or 0
            ),
    }


@produk_bp.get("/")
def get_produk():
    db = get_db()

    # ── Ambil semua produk ────────────────────────────────────
    query = db.table("produk").select(
        "id, nama, deskripsi, harga, stok, gambar_url, kategori_id, rating_avg"
    )
    resp = query.execute()
    produk_list = resp.data or []

    # ── Ambil map kategori ────────────────────────────────────
    kat_resp = db.table("kategori").select("id, nama").execute()
    kat_map  = {k["id"]: k["nama"] for k in (kat_resp.data or [])}

    # ── Filter & Search (di Python, lebih fleksibel) ──────────
    params   = request.args
    kategori = params.get("kategori", "").strip()
    search   = params.get("q", "").strip().lower()
    sort     = params.get("sort", "").strip()          # harga_asc, harga_desc, rating

    if kategori:
        produk_list = [
            p for p in produk_list
            if kat_map.get(p.get("kategori_id"), "").lower() == kategori.lower()
        ]

    if search:
        produk_list = [
            p for p in produk_list
            if search in p["nama"].lower() or search in (p.get("deskripsi") or "").lower()
        ]

    if sort == "harga_asc":
        produk_list.sort(key=lambda p: float(p["harga"]))
    elif sort == "harga_desc":
        produk_list.sort(key=lambda p: float(p["harga"]), reverse=True)
    elif sort == "rating":
        produk_list.sort(key=lambda p: float(p.get("rating_avg") or 0), reverse=True)

    result = [_build_produk_response(p, kat_map) for p in produk_list]
    return jsonify({"success": True, "total": len(result), "data": result})


@produk_bp.get("/<int:produk_id>")
def get_produk_detail(produk_id: int):
    db = get_db()

    resp = (
        db.table("produk")
        .select("id, nama, deskripsi, harga, stok, gambar_url, kategori_id, rating_avg")
        .eq("id", produk_id)
        .execute()
    )
    if not resp.data:
        return jsonify({"success": False, "message": "Produk tidak ditemukan."}), 404

    kat_resp = db.table("kategori").select("id, nama").execute()
    kat_map  = {k["id"]: k["nama"] for k in (kat_resp.data or [])}

    # Ambil juga semua rating untuk produk ini
    rating_resp = (
        db.table("rating")
        .select("nilai")
        .eq("produk_id", produk_id)
        .execute()
    )
    ratings = [r["nilai"] for r in (rating_resp.data or [])]

    produk = _build_produk_response(resp.data[0], kat_map)
    produk["jumlah_rating"] = len(ratings)

    return jsonify({"success": True, "data": produk})


@produk_bp.get("/kategori/list")
def get_kategori():
    db = get_db()
    resp = db.table("kategori").select("id, nama").order("nama").execute()
    return jsonify({"success": True, "data": resp.data or []})
