-- ============================================================
--  UMKM Kerajinan — Supabase Schema
--  Jalankan di Supabase SQL Editor (urutan penting!)
-- ============================================================

-- 1. TABEL USERS (autentikasi manual, bukan Supabase Auth)
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    nama        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,          -- bcrypt hash
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 2. TABEL KATEGORI
CREATE TABLE IF NOT EXISTS kategori (
    id    SERIAL PRIMARY KEY,
    nama  VARCHAR(80) UNIQUE NOT NULL
);

-- 3. TABEL PRODUK
CREATE TABLE IF NOT EXISTS produk (
    id           SERIAL PRIMARY KEY,
    nama         VARCHAR(200) NOT NULL,
    deskripsi    TEXT,
    harga        NUMERIC(12,2) NOT NULL,
    stok         INTEGER DEFAULT 0,
    gambar_url   TEXT,
    kategori_id  INTEGER REFERENCES kategori(id) ON DELETE SET NULL,
    rating_avg   NUMERIC(3,2) DEFAULT 0,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 4. TABEL RATING (inti UBCF)
CREATE TABLE IF NOT EXISTS rating (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    produk_id   INTEGER NOT NULL REFERENCES produk(id) ON DELETE CASCADE,
    nilai       SMALLINT NOT NULL CHECK (nilai BETWEEN 1 AND 5),
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, produk_id)           -- satu rating per user per produk
);

-- 5. TABEL WISHLIST
CREATE TABLE IF NOT EXISTS wishlist (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    produk_id  INTEGER NOT NULL REFERENCES produk(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, produk_id)
);

-- 6. TABEL KERANJANG
CREATE TABLE IF NOT EXISTS keranjang (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    produk_id  INTEGER NOT NULL REFERENCES produk(id) ON DELETE CASCADE,
    jumlah     INTEGER DEFAULT 1 CHECK (jumlah > 0),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, produk_id)
);

-- ============================================================
--  SEED DATA — Kategori
-- ============================================================
INSERT INTO kategori (nama) VALUES
    ('Anyaman'),
    ('Batik'),
    ('Gerabah'),
    ('Ukiran'),
    ('Tenun'),
    ('Aksesoris')
ON CONFLICT (nama) DO NOTHING;

-- ============================================================
--  SEED DATA — Produk (20 produk)
-- ============================================================
INSERT INTO produk (nama, deskripsi, harga, stok, gambar_url, kategori_id, rating_avg) VALUES
-- Anyaman (id kategori = 1)
('Tas Anyam Pandan Premium', 'Tas anyam dari daun pandan pilihan, tahan lama dan ramah lingkungan. Cocok untuk belanja atau pantai.', 185000, 15, 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=400', 1, 4.5),
('Keranjang Rotan Motif Klasik', 'Keranjang rotan buatan tangan pengrajin Cirebon, motif klasik, ideal untuk dekorasi rumah.', 220000, 10, 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400', 1, 4.2),
('Tikar Anyam Bambu', 'Tikar anyam bambu tipis, segar dan nyaman, cocok untuk piknik atau alas meditasi.', 95000, 25, 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', 1, 4.0),

-- Batik (id kategori = 2)
('Batik Tulis Mega Mendung', 'Batik tulis khas Cirebon motif mega mendung, kain primisima, pewarna alami.', 450000, 8, 'https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400', 2, 4.8),
('Kain Batik Cap Parang', 'Kain batik cap motif parang, cocok untuk kemeja formal maupun kasual.', 275000, 20, 'https://images.unsplash.com/photo-1558618047-f4e533c0cf3c?w=400', 2, 4.3),
('Selendang Batik Kawung', 'Selendang batik motif kawung, serbaguna sebagai aksesori atau penutup kepala.', 130000, 30, 'https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=400', 2, 4.1),

-- Gerabah (id kategori = 3)
('Pot Gerabah Etnik Lombok', 'Pot gerabah khas Lombok dengan ukiran etnik, cocok untuk tanaman hias indoor.', 165000, 12, 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=400', 3, 4.4),
('Set Mangkuk Gerabah Alami', 'Set 4 mangkuk gerabah tanpa glasir, nuansa natural, aman untuk makanan.', 210000, 9, 'https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=400', 3, 4.6),
('Guci Gerabah Dekorasi', 'Guci gerabah tinggi 40 cm, finishing smoky, cocok untuk pojok ruang tamu.', 320000, 6, 'https://images.unsplash.com/photo-1596993100471-c3905dafa78e?w=400', 3, 4.7),

-- Ukiran (id kategori = 4)
('Topeng Kayu Jepara', 'Topeng ukir kayu jati Jepara, detail halus, cocok sebagai koleksi atau dekorasi dinding.', 380000, 7, 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400', 4, 4.9),
('Pigura Ukir Motif Bunga', 'Pigura foto kayu dengan ukiran motif bunga tropis, ukuran 20×25 cm.', 145000, 18, 'https://images.unsplash.com/photo-1553322835-b4c7e6a91b6a?w=400', 4, 4.2),
('Nampan Kayu Ukir Bali', 'Nampan kayu sengon ukiran Bali, fungsional sekaligus artistik.', 195000, 14, 'https://images.unsplash.com/photo-1599619351208-3e6c839d6828?w=400', 4, 4.3),

-- Tenun (id kategori = 5)
('Kain Tenun Ikat NTT', 'Kain tenun ikat asli NTT, motif tradisional, dikerjakan oleh penenun lokal.', 520000, 5, 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', 5, 4.8),
('Sarung Tenun Bugis', 'Sarung tenun sutra Bugis motif kotak-kotak, warna kaya dan tahan lama.', 410000, 8, 'https://images.unsplash.com/photo-1573461160327-f450ebe38ea4?w=400', 5, 4.5),
('Selimut Tenun Flores', 'Selimut tenun dari Flores, tebal dan hangat, motif geometris khas Ende.', 350000, 10, 'https://images.unsplash.com/photo-1582738411706-bfc8e691d1c2?w=400', 5, 4.4),

-- Aksesoris (id kategori = 6)
('Gelang Tembaga Etnik', 'Gelang tembaga tempa motif batik, anti karat, cocok untuk pria maupun wanita.', 85000, 40, 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400', 6, 4.3),
('Kalung Manik Kayu Cendana', 'Kalung manik dari kayu cendana asli, harum alami, tali rami.', 110000, 22, 'https://images.unsplash.com/photo-1599643477877-530eb83abc8e?w=400', 6, 4.5),
('Anting Perak Filigri', 'Anting perak filigri khas Yogyakarta, ringan, elegan untuk acara formal.', 175000, 16, 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=400', 6, 4.7),
('Cincin Perak Motif Naga', 'Cincin perak 925 motif naga, bisa request ukuran, produksi Celuk Bali.', 230000, 20, 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=400', 6, 4.6),
('Bando Rotan Bohemian', 'Bando berbahan rotan dan kain batik, tampilan bohemian-chic, ringan di kepala.', 65000, 35, 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400', 6, 4.1)
ON CONFLICT DO NOTHING;

-- ============================================================
--  SEED DATA — Users (password semua: "password123")
--  Hash bcrypt dari "password123"
-- ============================================================
INSERT INTO users (nama, email, password) VALUES
('Andi Saputra',   'andi@demo.com',   '$2b$12$LQv3c1yqBWVHxkd0LQ4YC.jzMsJBBdAdCHw5bQ3R8YxO0G3Lk9GNa'),
('Budi Santoso',   'budi@demo.com',   '$2b$12$LQv3c1yqBWVHxkd0LQ4YC.jzMsJBBdAdCHw5bQ3R8YxO0G3Lk9GNa'),
('Citra Dewi',     'citra@demo.com',  '$2b$12$LQv3c1yqBWVHxkd0LQ4YC.jzMsJBBdAdCHw5bQ3R8YxO0G3Lk9GNa'),
('Dian Rahayu',    'dian@demo.com',   '$2b$12$LQv3c1yqBWVHxkd0LQ4YC.jzMsJBBdAdCHw5bQ3R8YxO0G3Lk9GNa'),
('Eko Prasetyo',   'eko@demo.com',    '$2b$12$LQv3c1yqBWVHxkd0LQ4YC.jzMsJBBdAdCHw5bQ3R8YxO0G3Lk9GNa'),
('Fitri Handayani','fitri@demo.com',  '$2b$12$LQv3c1yqBWVHxkd0LQ4YC.jzMsJBBdAdCHw5bQ3R8YxO0G3Lk9GNa'),
('Galih Wicaksono','galih@demo.com',  '$2b$12$LQv3c1yqBWVHxkd0LQ4YC.jzMsJBBdAdCHw5bQ3R8YxO0G3Lk9GNa'),
('Hani Pertiwi',   'hani@demo.com',   '$2b$12$LQv3c1yqBWVHxkd0LQ4YC.jzMsJBBdAdCHw5bQ3R8YxO0G3Lk9GNa'),
('Irwan Kusuma',   'irwan@demo.com',  '$2b$12$LQv3c1yqBWVHxkd0LQ4YC.jzMsJBBdAdCHw5bQ3R8YxO0G3Lk9GNa'),
('Joko Widodo',    'joko@demo.com',   '$2b$12$LQv3c1yqBWVHxkd0LQ4YC.jzMsJBBdAdCHw5bQ3R8YxO0G3Lk9GNa')
ON CONFLICT (email) DO NOTHING;

-- ============================================================
--  SEED DATA — Rating (data interaksi untuk UBCF)
--  Format: (user_id, produk_id, nilai)
-- ============================================================
INSERT INTO rating (user_id, produk_id, nilai) VALUES
-- Andi (user 1): suka anyaman & aksesoris
(1, 1, 5), (1, 2, 4), (1, 3, 3), (1, 16, 4), (1, 17, 5), (1, 18, 4),
-- Budi (user 2): suka batik & tenun
(2, 4, 5), (2, 5, 4), (2, 6, 4), (2, 13, 5), (2, 14, 4), (2, 15, 3),
-- Citra (user 3): suka anyaman & aksesoris (mirip Andi)
(3, 1, 4), (3, 2, 5), (3, 16, 5), (3, 17, 4), (3, 19, 3), (3, 20, 4),
-- Dian (user 4): suka gerabah & ukiran
(4, 7, 5), (4, 8, 4), (4, 9, 5), (4, 10, 4), (4, 11, 3), (4, 12, 4),
-- Eko (user 5): suka batik & ukiran
(5, 4, 4), (5, 5, 5), (5, 10, 4), (5, 11, 5), (5, 12, 3), (5, 15, 4),
-- Fitri (user 6): suka semua, tapi favorit tenun & gerabah
(6, 7, 5), (6, 8, 5), (6, 13, 5), (6, 14, 4), (6, 15, 5), (6, 9, 4),
-- Galih (user 7): mirip Eko (batik & ukiran)
(7, 4, 5), (7, 5, 4), (7, 6, 3), (7, 10, 5), (7, 11, 4), (7, 12, 5),
-- Hani (user 8): suka aksesoris semua
(8, 16, 5), (8, 17, 5), (8, 18, 4), (8, 19, 5), (8, 20, 4), (8, 1, 3),
-- Irwan (user 9): suka gerabah & anyaman
(9, 3, 4), (9, 7, 4), (9, 8, 5), (9, 9, 3), (9, 1, 5), (9, 2, 4),
-- Joko (user 10): suka ukiran & tenun
(10, 10, 5), (10, 11, 4), (10, 12, 5), (10, 13, 4), (10, 14, 5), (10, 15, 4)
ON CONFLICT (user_id, produk_id) DO NOTHING;

-- ============================================================
--  INDEX untuk performa query
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_rating_user    ON rating(user_id);
CREATE INDEX IF NOT EXISTS idx_rating_produk  ON rating(produk_id);
CREATE INDEX IF NOT EXISTS idx_produk_kategori ON produk(kategori_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_user  ON wishlist(user_id);
CREATE INDEX IF NOT EXISTS idx_keranjang_user ON keranjang(user_id);

-- ============================================================
--  VIEW: rating_avg per produk (opsional, bisa di-trigger)
-- ============================================================
CREATE OR REPLACE VIEW v_produk_rating AS
SELECT
    p.id,
    p.nama,
    p.harga,
    k.nama AS kategori,
    ROUND(AVG(r.nilai)::NUMERIC, 2) AS rating_avg,
    COUNT(r.id) AS jumlah_rating
FROM produk p
LEFT JOIN rating r ON r.produk_id = p.id
LEFT JOIN kategori k ON k.id = p.kategori_id
GROUP BY p.id, p.nama, p.harga, k.nama;
