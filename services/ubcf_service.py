"""
services/ubcf_service.py
═══════════════════════════════════════════════════════════════
User-Based Collaborative Filtering (UBCF)
─────────────────────────────────────────
Algoritma:
  1. Bangun user-item rating matrix dari tabel `rating`
  2. Hitung Pearson Correlation Similarity antar semua user
  3. Pilih K neighbor terdekat untuk active user
  4. Prediksi rating produk yang BELUM dinilai active user
     menggunakan weighted average dari rating neighbor
  5. Kembalikan Top-N produk dengan prediksi rating tertinggi

Referensi:
  Resnick et al. (1994) — GroupLens: An Open Architecture for
  Collaborative Filtering of Netnews
═══════════════════════════════════════════════════════════════
"""

import os
import numpy as np
import pandas as pd
from db import get_db

# ── Konfigurasi dari .env ────────────────────────────────────
K_NEIGHBORS = int(os.getenv("UBCF_K_NEIGHBORS", 3))
TOP_N       = int(os.getenv("UBCF_TOP_N", 4))


# ────────────────────────────────────────────────────────────
#  STEP 1: Ambil data rating dari Supabase
# ────────────────────────────────────────────────────────────
def _fetch_rating_matrix() -> pd.DataFrame:
    """
    Mengambil semua data rating dari DB dan membentuk
    user-item matrix (baris = user, kolom = produk).
    Nilai NaN artinya user belum menilai produk tersebut.
    """
    db = get_db()
    resp = db.table("rating").select("user_id, produk_id, nilai").execute()
    rows = resp.data

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    # Pivot: baris = user_id, kolom = produk_id, nilai = rating
    matrix = df.pivot_table(
        index="user_id",
        columns="produk_id",
        values="nilai",
        aggfunc="mean"   # kalau ada duplikat, rata-ratakan
    )
    return matrix


# ────────────────────────────────────────────────────────────
#  STEP 2: Pearson Correlation Similarity
# ────────────────────────────────────────────────────────────
def _pearson_similarity(matrix: pd.DataFrame, user_a: int, user_b: int) -> float:
    """
    Hitung Pearson Correlation antara dua user.
    Hanya menggunakan produk yang KEDUANYA sudah menilai (co-rated).
    Mengembalikan nilai antara -1.0 s/d 1.0.
    """
    if user_a not in matrix.index or user_b not in matrix.index:
        return 0.0

    # Ambil produk yang dinilai keduanya
    rated_a = matrix.loc[user_a].dropna()
    rated_b = matrix.loc[user_b].dropna()
    common  = rated_a.index.intersection(rated_b.index)

    if len(common) < 1:          # minimal 2 item bersama
        return 0.0

    vec_a = rated_a[common].values.astype(float)
    vec_b = rated_b[common].values.astype(float)

    # Mean-center
    mean_a = vec_a.mean()
    mean_b = vec_b.mean()
    dev_a  = vec_a - mean_a
    dev_b  = vec_b - mean_b

    numerator   = np.dot(dev_a, dev_b)
    denominator = np.sqrt(np.sum(dev_a**2)) * np.sqrt(np.sum(dev_b**2))

    if denominator == 0:
        return 0.0

    corr = numerator / denominator
    # Clamp ke [-1, 1] untuk menghindari floating-point error
    return float(np.clip(corr, -1.0, 1.0))


# ────────────────────────────────────────────────────────────
#  STEP 3: Cari K Neighbor Terdekat
# ────────────────────────────────────────────────────────────
def _find_neighbors(matrix: pd.DataFrame, active_user: int, k: int) -> list[tuple[int, float]]:
    """
    Mengembalikan list (user_id, similarity) dari K neighbor
    dengan similarity tertinggi (positif) terhadap active_user.
    """
    similarities = []
    for uid in matrix.index:
        if uid == active_user:
            continue
        sim = _pearson_similarity(matrix, active_user, uid)
        if sim != 0.0:  # buang hanya yang benar-benar 0 (tidak ada korelasi)
            similarities.append((uid, sim))


    # Urutkan descending berdasarkan similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:k]


# ────────────────────────────────────────────────────────────
#  STEP 4 & 5: Prediksi Rating + Top-N
# ────────────────────────────────────────────────────────────
def _predict_ratings(
    matrix: pd.DataFrame,
    active_user: int,
    neighbors: list[tuple[int, float]]
) -> dict[int, float]:
    """
    Prediksi rating untuk produk yang BELUM dinilai active_user.

    Formula (Resnick, 1994):
      pred(a, i) = mean_a + Σ[sim(a,n) * (r_n,i - mean_n)]
                             ───────────────────────────────
                                    Σ |sim(a,n)|
    """
    if active_user not in matrix.index:
        return {}

    mean_active = matrix.loc[active_user].mean(skipna=True)

    # Produk yang sudah dinilai active user
    rated_by_active = set(matrix.loc[active_user].dropna().index)

    # Semua produk yang dinilai minimal satu neighbor
    candidate_items: set[int] = set()
    for neighbor_id, _ in neighbors:
        candidate_items.update(matrix.loc[neighbor_id].dropna().index)
    candidate_items -= rated_by_active   # buang yang sudah dinilai

    predictions: dict[int, float] = {}
    for item in candidate_items:
        numerator   = 0.0
        denominator = 0.0

        for neighbor_id, sim in neighbors:
            if item in matrix.columns and not pd.isna(matrix.loc[neighbor_id, item]):
                r_ni    = matrix.loc[neighbor_id, item]
                mean_n  = matrix.loc[neighbor_id].mean(skipna=True)
                numerator   += sim * (r_ni - mean_n)
                denominator += abs(sim)

        if denominator > 0:
            pred = mean_active + (numerator / denominator)
            # Clamp ke skala rating [1, 5]
            predictions[int(item)] = float(np.clip(pred, 1.0, 5.0))

    return predictions


# ────────────────────────────────────────────────────────────
#  PUBLIC API
# ────────────────────────────────────────────────────────────
def get_recommendations(user_id: int) -> dict:
    """
    Mengembalikan dict berisi:
      - recommendations : list produk rekomendasi (detail + similarity_score)
      - neighbors       : list neighbor yang dipakai
      - debug           : info tambahan untuk laporan TA
    """
    db = get_db()

    # Bangun matrix
    matrix = _fetch_rating_matrix()
    if matrix.empty:
        return {"recommendations": [], "neighbors": [], "debug": "Belum ada data rating."}

    # Validasi user ada di matrix
    if user_id not in matrix.index:
        return {
            "recommendations": [],
            "neighbors": [],
            "debug": f"User {user_id} belum memberikan rating apapun."
        }

    # Cari neighbor
    neighbors = _find_neighbors(matrix, user_id, K_NEIGHBORS)
    if not neighbors:
        return {
            "recommendations": [],
            "neighbors": [],
            "debug": "Tidak ditemukan neighbor yang cukup mirip."
        }

    # Prediksi rating
    predictions = _predict_ratings(matrix, user_id, neighbors)
    if not predictions:
        return {
            "recommendations": [],
            "neighbors": neighbors,
            "debug": "Tidak ada produk baru yang bisa direkomendasikan."
        }

    # Ambil Top-N produk_id
    top_items = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
    top_ids   = [item[0] for item in top_items]

    # Ambil detail produk dari DB
    resp = (
        db.table("produk")
        .select("id, nama, harga, gambar_url, rating_avg, kategori_id")
        .in_("id", top_ids)
        .execute()
    )
    produk_map = {p["id"]: p for p in resp.data}

    # Ambil nama kategori
    kat_resp = db.table("kategori").select("id, nama").execute()
    kat_map  = {k["id"]: k["nama"] for k in kat_resp.data}

    # Susun hasil rekomendasi
    recommendations = []
    for produk_id, pred_rating in top_items:
        if produk_id not in produk_map:
            continue
        p = produk_map[produk_id]

        BASE_IMG = "https://web-production-aa9b5.up.railway.app/static/uploads/"
        recommendations.append({
            "produk_id"        : produk_id,
            "nama"             : p["nama"],
            "harga"            : float(p["harga"]),
            "gambar_url"       : p["gambar_url"],
            "rating_avg"       : float(p["rating_avg"] or 0),
            "kategori"         : kat_map.get(p["kategori_id"], "-"),
            "predicted_rating" : round(pred_rating, 3),
            # Similarity score: rata-rata similarity neighbor (untuk UI score bar)
            "similarity_score" : round(
                np.mean([s for _, s in neighbors]), 3
            ),
        })

    # Info neighbor untuk debug/laporan
    neighbor_info = []
    for nid, sim in neighbors:
        n_resp = db.table("users").select("nama").eq("id", nid).execute()
        nama   = n_resp.data[0]["nama"] if n_resp.data else f"User {nid}"
        neighbor_info.append({
            "user_id"    : nid,
            "nama"       : nama,
            "similarity" : round(sim, 4),
        })

    return {
        "recommendations": recommendations,
        "neighbors"       : neighbor_info,
        "debug": {
            "active_user"  : user_id,
            "k_neighbors"  : K_NEIGHBORS,
            "top_n"        : TOP_N,
            "matrix_shape" : list(matrix.shape),
            "total_ratings": int(matrix.count().sum()),
        }
    }


def get_similarity_matrix() -> dict:
    """
    Mengembalikan matriks similarity lengkap antar semua user.
    Berguna untuk visualisasi di laporan TA.
    """
    matrix = _fetch_rating_matrix()
    if matrix.empty:
        return {}

    users = list(matrix.index)
    sim_matrix = {}

    for ua in users:
        sim_matrix[int(ua)] = {}
        for ub in users:
            if ua == ub:
                sim_matrix[int(ua)][int(ub)] = 1.0
            else:
                sim = _pearson_similarity(matrix, ua, ub)
                sim_matrix[int(ua)][int(ub)] = round(sim, 4)

    return sim_matrix
