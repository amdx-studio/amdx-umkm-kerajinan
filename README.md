# 🏺 UMKM Kerajinan — Backend Flask + UBCF

Backend sistem rekomendasi produk kerajinan UMKM berbasis **User-Based Collaborative Filtering (UBCF)** dengan **Pearson Correlation Similarity**.

---

## 🗂️ Struktur Proyek

```
umkm-backend/
├── app.py                   ← Entry point Flask
├── db.py                    ← Koneksi Supabase
├── requirements.txt
├── .env.example             ← Template konfigurasi
├── schema.sql               ← DDL + Seed data Supabase
├── api.js                   ← Helper fetch untuk frontend
│
├── routes/
│   ├── auth_routes.py       ← /api/auth/*
│   ├── produk_routes.py     ← /api/produk/*
│   ├── rating_routes.py     ← /api/rating/*
│   ├── ubcf_routes.py       ← /api/rekomendasi/*
│   ├── wishlist_routes.py   ← /api/wishlist/*
│   └── keranjang_routes.py  ← /api/keranjang/*
│
└── services/
    ├── ubcf_service.py      ← Algoritma UBCF (inti TA)
    └── auth_service.py      ← Registrasi & login
```

---

## ⚙️ Setup (Langkah demi Langkah)

### 1. Persiapkan Supabase
1. Buka [supabase.com](https://supabase.com) → buat project baru
2. Masuk ke **SQL Editor**
3. Copy-paste isi `schema.sql` → klik **Run**
4. Data seed (10 user, 20 produk, 60+ rating) otomatis terisi

### 2. Ambil Kredensial Supabase
Di dashboard Supabase → **Settings → API**:
- `Project URL` → isi ke `SUPABASE_URL`
- `anon public key` → isi ke `SUPABASE_KEY`

### 3. Konfigurasi .env
```bash
cp .env.example .env
# Edit .env dan isi SUPABASE_URL, SUPABASE_KEY, JWT_SECRET_KEY
```

### 4. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Jalankan Server
```bash
python app.py
# Server berjalan di http://localhost:5000
```

---

## 📡 Daftar Endpoint API

### Auth
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/auth/register` | Daftar akun baru |
| POST | `/api/auth/login` | Login, dapat JWT token |
| GET | `/api/auth/me` | Info user yang login 🔒 |

### Produk
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/produk/` | Semua produk (filter: `?kategori=Batik&q=tas&sort=harga_asc`) |
| GET | `/api/produk/<id>` | Detail satu produk |
| GET | `/api/produk/kategori/list` | Daftar kategori |

### Rating *(semua perlu login* 🔒*)*
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/rating/` | Beri / update rating `{produk_id, nilai}` |
| GET | `/api/rating/user` | Rating milik user login |
| GET | `/api/rating/produk/<id>` | Rating untuk satu produk |

### Rekomendasi UBCF 🔒
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/rekomendasi/` | **Top-N rekomendasi + info neighbor** |
| GET | `/api/rekomendasi/matrix` | Matriks similarity antar user |
| GET | `/api/rekomendasi/debug` | User-item rating matrix + sparsity |

### Wishlist & Keranjang 🔒
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET/POST | `/api/wishlist/` | Lihat / tambah wishlist |
| DELETE | `/api/wishlist/<id>` | Hapus dari wishlist |
| GET/POST | `/api/keranjang/` | Lihat / tambah keranjang |
| PATCH | `/api/keranjang/<id>` | Update jumlah |
| DELETE | `/api/keranjang/<id>` | Hapus item |

---

## 🧠 Cara Kerja Algoritma UBCF

### Formula Pearson Correlation Similarity
```
        Σ (r_a,i - r̄_a)(r_n,i - r̄_n)
sim(a,n) = ─────────────────────────────────────────
           √Σ(r_a,i - r̄_a)² · √Σ(r_n,i - r̄_n)²
```

### Formula Prediksi Rating (Resnick, 1994)
```
                    Σ sim(a,n) · (r_n,i - r̄_n)
pred(a,i) = r̄_a + ────────────────────────────────
                           Σ |sim(a,n)|
```

### Alur Proses
```
1. Buat User-Item Rating Matrix dari DB
2. Hitung Pearson Similarity: active user vs semua user lain
3. Pilih K=3 neighbor dengan similarity tertinggi (positif)
4. Prediksi rating produk yang belum dinilai active user
5. Kembalikan Top-N=4 produk dengan prediksi rating tertinggi
```

---

## 🔌 Integrasi ke Frontend

Salin `api.js` ke folder `js/` frontend, lalu gunakan:

```javascript
// Login
const res = await apiLogin("andi@demo.com", "password123");

// Ambil rekomendasi UBCF
const rek = await apiGetRekomendasi();
rek.recommendations.forEach(produk => {
  console.log(produk.nama, "→", produk.predicted_rating);
  console.log("Similarity score:", produk.similarity_score);
});

// Beri rating
await apiRate(5, 4);  // produk_id=5, nilai=4

// Tambah ke keranjang
await apiAddKeranjang(3, 2);  // produk_id=3, jumlah=2
```

### Contoh Response `/api/rekomendasi/`
```json
{
  "success": true,
  "user_id": 1,
  "recommendations": [
    {
      "produk_id": 19,
      "nama": "Cincin Perak Motif Naga",
      "harga": 230000,
      "predicted_rating": 4.612,
      "similarity_score": 0.847,
      "kategori": "Aksesoris"
    }
  ],
  "neighbors": [
    { "user_id": 3, "nama": "Citra Dewi", "similarity": 0.924 },
    { "user_id": 8, "nama": "Hani Pertiwi", "similarity": 0.771 }
  ],
  "debug": {
    "k_neighbors": 3,
    "top_n": 4,
    "matrix_shape": [10, 20]
  }
}
```

---

## 🧪 Akun Demo
Semua akun menggunakan password: **`password123`**

| Nama | Email |
|------|-------|
| Andi Saputra | andi@demo.com |
| Budi Santoso | budi@demo.com |
| Citra Dewi | citra@demo.com |
| Dian Rahayu | dian@demo.com |
| Eko Prasetyo | eko@demo.com |

---

## 📚 Referensi Algoritma (untuk Daftar Pustaka TA)

- Resnick, P., et al. (1994). GroupLens: An Open Architecture for Collaborative Filtering of Netnews. *CSCW '94*.
- Su, X., & Khoshgoftaar, T. M. (2009). A Survey of Collaborative Filtering Techniques. *Advances in AI*.
- Sarwar, B., et al. (2001). Item-based Collaborative Filtering Recommendation Algorithms. *WWW '01*.
