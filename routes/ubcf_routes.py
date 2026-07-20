"""
routes/ubcf_routes.py
VERSI TANPA JWT
"""

from flask import Blueprint, jsonify, request

from services.ubcf_service import (
    get_recommendations,
    get_similarity_matrix,
    _fetch_rating_matrix
)

ubcf_bp = Blueprint("ubcf", __name__)


# =========================================================
# GET REKOMENDASI
# GET /api/rekomendasi/?user_id=1
# =========================================================
@ubcf_bp.get("/")
def rekomendasi():

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

    try:

        result = get_recommendations(user_id)

        return jsonify({
            "success": True,
            "user_id": user_id,
            "recommendations": result.get("recommendations", []),
            "neighbors": result.get("neighbors", []),
            "debug": result.get("debug", {}),
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================================================
# GET SIMILARITY MATRIX
# GET /api/rekomendasi/matrix
# =========================================================
@ubcf_bp.get("/matrix")
def similarity_matrix():

    try:

        matrix = get_similarity_matrix()

        return jsonify({
            "success": True,
            "matrix": matrix,
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================================================
# DEBUG RATING MATRIX
# GET /api/rekomendasi/debug
# =========================================================
@ubcf_bp.get("/debug")
def debug_matrix():

    try:

        import pandas as pd

        matrix = _fetch_rating_matrix()

        if matrix.empty:
            return jsonify({
                "success": False,
                "message": "Belum ada data rating."
            })

        # ── Konversi matrix ke JSON ─────────────────────
        matrix_json = {}

        for uid in matrix.index:

            matrix_json[int(uid)] = {}

            for pid in matrix.columns:

                val = matrix.loc[uid, pid]

                matrix_json[int(uid)][int(pid)] = (
                    None if pd.isna(val) else float(val)
                )

        return jsonify({
            "success": True,
            "users": [int(u) for u in matrix.index],
            "produk_ids": [int(p) for p in matrix.columns],
            "matrix": matrix_json,
            "shape": list(matrix.shape),
            "sparsity_pct": round(
                100 * matrix.isna().sum().sum()
                / (matrix.shape[0] * matrix.shape[1]),
                2
            ),
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500