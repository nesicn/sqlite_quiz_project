-- SQLite ile Quiz Veri Tabanı Şeması
-- Veri Tabanı Sistemleri Proje Ödevi

PRAGMA foreign_keys = ON;

-- Var olan tabloları ve görünümleri temizle
DROP VIEW IF EXISTS v_oturum_sonuclari;
DROP VIEW IF EXISTS v_cevap_detaylari;
DROP VIEW IF EXISTS v_canli_oturum_ilerlemesi;

DROP TABLE IF EXISTS cevaplar;
DROP TABLE IF EXISTS katilimlar;
DROP TABLE IF EXISTS oturum_sorulari;
DROP TABLE IF EXISTS secenekler;
DROP TABLE IF EXISTS sorular;
DROP TABLE IF EXISTS oturumlar;
DROP TABLE IF EXISTS kullanicilar;

-- 1. KULLANICILAR TABLOSU
CREATE TABLE kullanicilar (
    kullanici_id INTEGER PRIMARY KEY AUTOINCREMENT,
    kullanici_adi TEXT NOT NULL UNIQUE CHECK(length(trim(kullanici_adi)) >= 3),
    eposta TEXT NOT NULL UNIQUE CHECK(eposta LIKE '%@%.%'),
    ad_soyad TEXT NOT NULL CHECK(length(trim(ad_soyad)) >= 2),
    kayit_tarihi DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    durum TEXT NOT NULL DEFAULT 'aktif' CHECK(durum IN ('aktif', 'pasif', 'engelli'))
);

-- 2. OTURUMLAR TABLOSU
CREATE TABLE oturumlar (
    oturum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    baslik TEXT NOT NULL CHECK(length(trim(baslik)) >= 3),
    aciklama TEXT,
    durum TEXT NOT NULL DEFAULT 'planlandi' CHECK(durum IN ('planlandi', 'devam_ediyor', 'tamamlandi', 'iptal')),
    baslangic_zaman DATETIME,
    bitis_zaman DATETIME,
    sure_dakika INTEGER NOT NULL DEFAULT 30 CHECK(sure_dakika > 0),
    gecme_notu REAL NOT NULL DEFAULT 50.0 CHECK(gecme_notu BETWEEN 0 AND 100),
    olusturma_tarihi DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    CHECK (bitis_zaman IS NULL OR baslangic_zaman IS NULL OR bitis_zaman >= baslangic_zaman)
);

-- 3. SORULAR TABLOSU (Normalize Soru Bankası)
CREATE TABLE sorular (
    soru_id INTEGER PRIMARY KEY AUTOINCREMENT,
    soru_metni TEXT NOT NULL CHECK(length(trim(soru_metni)) > 0),
    kategori TEXT NOT NULL DEFAULT 'Genel',
    zorluk_seviyesi TEXT NOT NULL DEFAULT 'orta' CHECK(zorluk_seviyesi IN ('kolay', 'orta', 'zor')),
    puan_degeri REAL NOT NULL DEFAULT 10.0 CHECK(puan_degeri > 0),
    olusturma_tarihi DATETIME NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 4. SECENEKLER TABLOSU (Esnek N-Seçenek Altyapısı - 3NF)
CREATE TABLE secenekler (
    secenek_id INTEGER PRIMARY KEY AUTOINCREMENT,
    soru_id INTEGER NOT NULL,
    secenek_etiketi TEXT NOT NULL CHECK(length(trim(secenek_etiketi)) >= 1),
    secenek_metni TEXT NOT NULL CHECK(length(trim(secenek_metni)) > 0),
    dogru_mu INTEGER NOT NULL DEFAULT 0 CHECK(dogru_mu IN (0, 1)),
    FOREIGN KEY (soru_id) REFERENCES sorular(soru_id) ON DELETE CASCADE,
    UNIQUE(soru_id, secenek_etiketi)
);

-- 5. OTURUM_SORULARI TABLOSU (Çoktan Çoğa İlişki & Sıralama)
CREATE TABLE oturum_sorulari (
    oturum_id INTEGER NOT NULL,
    soru_id INTEGER NOT NULL,
    soru_sirasi INTEGER NOT NULL CHECK(soru_sirasi > 0),
    PRIMARY KEY (oturum_id, soru_id),
    FOREIGN KEY (oturum_id) REFERENCES oturumlar(oturum_id) ON DELETE CASCADE,
    FOREIGN KEY (soru_id) REFERENCES sorular(soru_id) ON DELETE CASCADE,
    UNIQUE(oturum_id, soru_sirasi)
);

-- 6. KATILIMLAR TABLOSU (Oturum Katılımcı Kayıtları)
CREATE TABLE katilimlar (
    katilim_id INTEGER PRIMARY KEY AUTOINCREMENT,
    kullanici_id INTEGER NOT NULL,
    oturum_id INTEGER NOT NULL,
    katilim_zaman DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    tamamlama_zaman DATETIME,
    tamamlandi_mi INTEGER NOT NULL DEFAULT 0 CHECK(tamamlandi_mi IN (0, 1)),
    FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(kullanici_id) ON DELETE CASCADE,
    FOREIGN KEY (oturum_id) REFERENCES oturumlar(oturum_id) ON DELETE CASCADE,
    UNIQUE(kullanici_id, oturum_id)
);

-- 7. CEVAPLAR TABLOSU (Verilen Cevaplar & Veri Bütünlüğü Kısıtları)
CREATE TABLE cevaplar (
    cevap_id INTEGER PRIMARY KEY AUTOINCREMENT,
    katilim_id INTEGER NOT NULL,
    kullanici_id INTEGER NOT NULL,
    oturum_id INTEGER NOT NULL,
    soru_id INTEGER NOT NULL,
    secenek_id INTEGER, -- NULL = Boş / Cevaplanmamış
    cevaplama_zamani DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (katilim_id) REFERENCES katilimlar(katilim_id) ON DELETE CASCADE,
    FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(kullanici_id) ON DELETE CASCADE,
    FOREIGN KEY (secenek_id) REFERENCES secenekler(secenek_id) ON DELETE SET NULL,
    -- BİLEŞİK YABANCI ANAHTAR: Cevabın yalnızca o oturuma atanmış soruya verilmesini zorunlu kılar!
    FOREIGN KEY (oturum_id, soru_id) REFERENCES oturum_sorulari(oturum_id, soru_id) ON DELETE CASCADE,
    UNIQUE(kullanici_id, oturum_id, soru_id)
);

-- İNDEKS TASARIMI (Sorgu Performansı Optimizasyonu)
CREATE INDEX idx_secenekler_soru_id ON secenekler(soru_id);
CREATE INDEX idx_oturum_sorulari_oturum_id ON oturum_sorulari(oturum_id);
CREATE INDEX idx_oturum_sorulari_soru_id ON oturum_sorulari(soru_id);
CREATE INDEX idx_katilimlar_kullanici_oturum ON katilimlar(kullanici_id, oturum_id);
CREATE INDEX idx_cevaplar_katilim ON cevaplar(katilim_id);
CREATE INDEX idx_cevaplar_kullanici_oturum ON cevaplar(kullanici_id, oturum_id);
CREATE INDEX idx_cevaplar_oturum_soru ON cevaplar(oturum_id, soru_id);

-- GÖRÜNÜMLER (VIEWS)

-- 1. Görünüm: Canlı Oturum İlerlemesi
CREATE VIEW v_canli_oturum_ilerlemesi AS
SELECT 
    o.oturum_id,
    o.baslik AS oturum_basligi,
    o.durum AS oturum_durumu,
    o.baslangic_zaman,
    o.bitis_zaman,
    COUNT(DISTINCT os.soru_id) AS oturumdaki_toplam_soru,
    COUNT(DISTINCT k.katilim_id) AS katilan_kullanici_sayisi,
    COUNT(c.cevap_id) AS toplam_verilen_cevap_sayisi,
    ROUND(
        CASE 
            WHEN COUNT(DISTINCT k.katilim_id) * COUNT(DISTINCT os.soru_id) = 0 THEN 0.0
            ELSE (CAST(COUNT(c.cevap_id) AS REAL) / (COUNT(DISTINCT k.katilim_id) * COUNT(DISTINCT os.soru_id))) * 100.0
        END, 2
    ) AS oturum_tamamlanma_yuzdesi
FROM oturumlar o
LEFT JOIN oturum_sorulari os ON o.oturum_id = os.oturum_id
LEFT JOIN katilimlar k ON o.oturum_id = k.oturum_id
LEFT JOIN cevaplar c ON k.katilim_id = c.katilim_id AND os.soru_id = c.soru_id
GROUP BY o.oturum_id;

-- 2. Görünüm: Detaylı Cevap Listesi
CREATE VIEW v_cevap_detaylari AS
SELECT 
    c.cevap_id,
    c.katilim_id,
    c.kullanici_id,
    u.ad_soyad AS kullanici_adi,
    c.oturum_id,
    o.baslik AS oturum_baslik,
    c.soru_id,
    s.soru_metni,
    s.puan_degeri AS soru_puani,
    c.secenek_id,
    sec.secenek_etiketi,
    sec.secenek_metni AS secilen_cevap,
    COALESCE(sec.dogru_mu, 0) AS dogru_mu,
    CASE 
        WHEN c.secenek_id IS NULL THEN 0.0
        WHEN sec.dogru_mu = 1 THEN s.puan_degeri
        ELSE -2.5
    END AS alinan_puan,
    c.cevaplama_zamani
FROM cevaplar c
JOIN kullanicilar u ON c.kullanici_id = u.kullanici_id
JOIN oturumlar o ON c.oturum_id = o.oturum_id
JOIN sorular s ON c.soru_id = s.soru_id
LEFT JOIN secenekler sec ON c.secenek_id = sec.secenek_id;

-- 3. Görünüm: Oturum ve Kullanıcı Puan Sonuçları
CREATE VIEW v_oturum_sonuclari AS
SELECT 
    k.katilim_id,
    k.oturum_id,
    o.baslik AS oturum_baslik,
    k.kullanici_id,
    u.ad_soyad,
    u.eposta,
    (SELECT COUNT(*) FROM oturum_sorulari os WHERE os.oturum_id = k.oturum_id) AS toplam_soru_sayisi,
    COUNT(c.cevap_id) AS cevaplanan_soru_sayisi,
    SUM(CASE WHEN sec.dogru_mu = 1 THEN 1 ELSE 0 END) AS dogru_sayisi,
    SUM(CASE WHEN c.secenek_id IS NOT NULL AND sec.dogru_mu = 0 THEN 1 ELSE 0 END) AS yanlis_sayisi,
    ((SELECT COUNT(*) FROM oturum_sorulari os WHERE os.oturum_id = k.oturum_id) - COUNT(c.cevap_id)) AS bos_sayisi,
    COALESCE(ROUND(SUM(
        CASE 
            WHEN c.secenek_id IS NULL THEN 0.0
            WHEN sec.dogru_mu = 1 THEN s.puan_degeri
            ELSE -2.5
        END
    ), 2), 0.0) AS toplam_puan,
    CASE 
        WHEN COALESCE(ROUND(SUM(
            CASE 
                WHEN c.secenek_id IS NULL THEN 0.0
                WHEN sec.dogru_mu = 1 THEN s.puan_degeri
                ELSE -2.5
            END
        ), 2), 0.0) >= o.gecme_notu 
        THEN 'BAŞARILI' 
        ELSE 'BAŞARISIZ' 
    END AS durum_sonucu
FROM katilimlar k
JOIN oturumlar o ON k.oturum_id = o.oturum_id
JOIN kullanicilar u ON k.kullanici_id = u.kullanici_id
LEFT JOIN oturum_sorulari os ON k.oturum_id = os.oturum_id
LEFT JOIN sorular s ON os.soru_id = s.soru_id
LEFT JOIN cevaplar c ON k.katilim_id = c.katilim_id AND os.soru_id = c.soru_id
LEFT JOIN secenekler sec ON c.secenek_id = sec.secenek_id
GROUP BY k.katilim_id, k.oturum_id, k.kullanici_id;
