-- ============================================================================
-- SQL / VERİ TABANI DERSİ HAFTALIK PROJE: SQLITE ILE QUIZ VERİ TABANI
-- DOSYA: queries.sql
-- AÇIKLAMA: Canlı takip, oturum sonuçları, liderlik tablosu ve analitik sorgular
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- 1. SORGU: CANLI OTURUM TAKİBİ VE İLERLEME RAPORU
-- Amaç: Tüm oturumların durumunu (planlandı, devam ediyor, tamamlandı, iptal),
-- katılan kullanıcı sayısını, atanan soru sayısını ve genel tamamlama yüzdesini gösterir.
-- ============================================================================
SELECT 
    o.oturum_id,
    o.baslik AS oturum_basligi,
    o.durum AS oturum_durumu,
    o.baslangic_zaman,
    o.bitis_zaman,
    COUNT(DISTINCT os.soru_id) AS toplam_soru_sayisi,
    COUNT(DISTINCT k.katilim_id) AS katilan_kullanici_sayisi,
    COUNT(c.cevap_id) AS toplam_verilen_cevap,
    (COUNT(DISTINCT k.katilim_id) * COUNT(DISTINCT os.soru_id)) AS beklenen_toplam_cevap,
    ROUND(
        CASE 
            WHEN (COUNT(DISTINCT k.katilim_id) * COUNT(DISTINCT os.soru_id)) = 0 THEN 0.0
            ELSE (CAST(COUNT(c.cevap_id) AS REAL) / (COUNT(DISTINCT k.katilim_id) * COUNT(DISTINCT os.soru_id))) * 100.0
        END, 2
    ) AS tamamlanma_yuzdesi
FROM oturumlar o
LEFT JOIN oturum_sorulari os ON o.oturum_id = os.oturum_id
LEFT JOIN katilimlar k ON o.oturum_id = k.oturum_id
LEFT JOIN cevaplar c ON k.katilim_id = c.katilim_id AND os.soru_id = c.soru_id
GROUP BY o.oturum_id, o.baslik, o.durum, o.baslangic_zaman, o.bitis_zaman
ORDER BY o.oturum_id;


-- ============================================================================
-- 2. SORGU: ANLIK DEVAM EDEN OTURUMDA KULLANICI İLERLEMESİ (CANLI TAKİP DETAYI)
-- Amaç: Şu an devam eden (durum = 'devam_ediyor') oturumlardaki her kullanıcının
-- kaç soru yanıtladığını, kaç soru kaldığını ve anlık tamamlama oranını listeler.
-- ============================================================================
SELECT 
    o.oturum_id,
    o.baslik AS oturum_basligi,
    u.kullanici_id,
    u.ad_soyad,
    (SELECT COUNT(*) FROM oturum_sorulari os WHERE os.oturum_id = o.oturum_id) AS oturum_soru_sayisi,
    COUNT(c.cevap_id) AS yanitlanan_soru_sayisi,
    ((SELECT COUNT(*) FROM oturum_sorulari os WHERE os.oturum_id = o.oturum_id) - COUNT(c.cevap_id)) AS kalan_soru_sayisi,
    ROUND(
        (CAST(COUNT(c.cevap_id) AS REAL) / (SELECT COUNT(*) FROM oturum_sorulari os WHERE os.oturum_id = o.oturum_id)) * 100.0, 
        2
    ) AS kullanici_ilerleme_yuzdesi
FROM katilimlar kt
JOIN oturumlar o ON kt.oturum_id = o.oturum_id
JOIN kullanicilar u ON kt.kullanici_id = u.kullanici_id
LEFT JOIN cevaplar c ON kt.katilim_id = c.katilim_id
WHERE o.durum = 'devam_ediyor'
GROUP BY o.oturum_id, u.kullanici_id, u.ad_soyad
ORDER BY kullanici_ilerleme_yuzdesi DESC;


-- ============================================================================
-- 3. SORGU: OTURUM SONUÇLARI VE DETAYLI PUAN HESAPLAMA
-- Amaç: Belirli veya tüm oturumlarda kullanıcıların doğru, yanlış, boş sayılarını
-- ve hesaplanan net puanlarını (Doğru: +Puan, Yanlış: -2.5 Puan, Boş: 0 Puan) listeler.
-- ============================================================================
SELECT 
    k.oturum_id,
    o.baslik AS oturum_baslik,
    u.kullanici_id,
    u.ad_soyad,
    (SELECT COUNT(*) FROM oturum_sorulari os WHERE os.oturum_id = k.oturum_id) AS toplam_soru,
    COUNT(c.cevap_id) AS cevaplanan_soru,
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
        ), 2), 0.0) >= o.gecme_notu THEN 'PASSED (BAŞARILI)'
        ELSE 'FAILED (BAŞARISIZ)'
    END AS durum_sonucu
FROM katilimlar k
JOIN oturumlar o ON k.oturum_id = o.oturum_id
JOIN kullanicilar u ON k.kullanici_id = u.kullanici_id
LEFT JOIN oturum_sorulari os ON k.oturum_id = os.oturum_id
LEFT JOIN sorular s ON os.soru_id = s.soru_id
LEFT JOIN cevaplar c ON k.katilim_id = c.katilim_id AND os.soru_id = c.soru_id
LEFT JOIN secenekler sec ON c.secenek_id = sec.secenek_id
GROUP BY k.katilim_id, k.oturum_id, k.kullanici_id
ORDER BY k.oturum_id ASC, toplam_puan DESC;


-- ============================================================================
-- 4. SORGU: OTURUM BAZLI LİDERLİK TABLOSU (DENSE_RANK İLE İLERİ SQL)
-- Amaç: Her oturum içinde en yüksek puan alan ilk 5 kullanıcıyı sıralar.
-- Windows Fonksiyonu (DENSE_RANK) kullanarak derece verir.
-- ============================================================================
WITH OturumSkorlari AS (
    SELECT 
        k.oturum_id,
        o.baslik AS oturum_baslik,
        u.kullanici_id,
        u.ad_soyad,
        SUM(CASE WHEN sec.dogru_mu = 1 THEN 1 ELSE 0 END) AS dogru_sayisi,
        COALESCE(ROUND(SUM(
            CASE 
                WHEN c.secenek_id IS NULL THEN 0.0
                WHEN sec.dogru_mu = 1 THEN s.puan_degeri
                ELSE -2.5
            END
        ), 2), 0.0) AS net_puan,
        DENSE_RANK() OVER (
            PARTITION BY k.oturum_id 
            ORDER BY COALESCE(ROUND(SUM(
                CASE 
                    WHEN c.secenek_id IS NULL THEN 0.0
                    WHEN sec.dogru_mu = 1 THEN s.puan_degeri
                    ELSE -2.5
                END
            ), 2), 0.0) DESC
        ) AS sira
    FROM katilimlar k
    JOIN oturumlar o ON k.oturum_id = o.oturum_id
    JOIN kullanicilar u ON k.kullanici_id = u.kullanici_id
    LEFT JOIN oturum_sorulari os ON k.oturum_id = os.oturum_id
    LEFT JOIN sorular s ON os.soru_id = s.soru_id
    LEFT JOIN cevaplar c ON k.katilim_id = c.katilim_id AND os.soru_id = c.soru_id
    LEFT JOIN secenekler sec ON c.secenek_id = sec.secenek_id
    GROUP BY k.oturum_id, k.kullanici_id
)
SELECT 
    oturum_id,
    oturum_baslik,
    sira,
    kullanici_id,
    ad_soyad,
    dogru_sayisi,
    net_puan
FROM OturumSkorlari
WHERE sira <= 5
ORDER BY oturum_id, sira;


-- ============================================================================
-- 5. SORGU: GENEL SİSTEM EN YÜKSEK PUANLI KULLANICILAR (GLOBAL LEADERBOARD)
-- Amaç: Tüm oturumlar genelinde en çok puan toplayan ve en çok quiz tamamlayan
-- en başarılı ilk 10 kullanıcıyı listeler.
-- ============================================================================
SELECT 
    u.kullanici_id,
    u.ad_soyad,
    u.eposta,
    COUNT(DISTINCT k.oturum_id) AS katilinan_oturum_sayisi,
    SUM(CASE WHEN sec.dogru_mu = 1 THEN 1 ELSE 0 END) AS toplam_dogru_cevap,
    ROUND(SUM(
        CASE 
            WHEN c.secenek_id IS NULL THEN 0.0
            WHEN sec.dogru_mu = 1 THEN s.puan_degeri
            ELSE -2.5
        END
    ), 2) AS genel_toplam_puan
FROM kullanicilar u
JOIN katilimlar k ON u.kullanici_id = k.kullanici_id
JOIN oturum_sorulari os ON k.oturum_id = os.oturum_id
JOIN sorular s ON os.soru_id = s.soru_id
LEFT JOIN cevaplar c ON k.katilim_id = c.katilim_id AND os.soru_id = c.soru_id
LEFT JOIN secenekler sec ON c.secenek_id = sec.secenek_id
GROUP BY u.kullanici_id, u.ad_soyad, u.eposta
ORDER BY genel_toplam_puan DESC
LIMIT 10;


-- ============================================================================
-- 6. SORGU: EN ÇOK ZORLANILAN (YANLIŞ YAPILAN) SORULAR İSTATİSTİĞİ
-- Amaç: Soruların zorluk seviyesine ve yanlış cevaplanma oranlarına göre analizi.
-- ============================================================================
SELECT 
    s.soru_id,
    SUBSTR(s.soru_metni, 1, 60) || '...' AS soru_ozeti,
    s.kategori,
    s.zorluk_seviyesi,
    COUNT(c.cevap_id) AS toplam_yanitlanma,
    SUM(CASE WHEN sec.dogru_mu = 1 THEN 1 ELSE 0 END) AS dogru_yanit_sayisi,
    SUM(CASE WHEN sec.dogru_mu = 0 THEN 1 ELSE 0 END) AS yanlis_yanit_sayisi,
    ROUND(
        (CAST(SUM(CASE WHEN sec.dogru_mu = 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(c.cevap_id)) * 100.0, 
        2
    ) AS yanlis_yapilma_orani_yuzde
FROM sorular s
JOIN cevaplar c ON s.soru_id = c.soru_id
JOIN secenekler sec ON c.secenek_id = sec.secenek_id
GROUP BY s.soru_id
HAVING toplam_yanitlanma >= 5
ORDER BY yanlis_yapilma_orani_yuzde DESC
LIMIT 10;


-- ============================================================================
-- 7. SORGU: VERİ MODELİ VE HEDEF DOĞRULAMA SORGUSU (SAYISAL KONTROL)
-- Amaç: Proje gereksinimlerinde istenen sayısal hedeflerin (>=50 Kullanıcı, 
-- 5 Oturum, >=100 Soru) karşılandığını tek bir SQL tablosunda doğrular.
-- ============================================================================
SELECT 'Kullanıcı Kayıt Sayısı (Hedef: >= 50)' AS Metrik, COUNT(*) AS Deger, CASE WHEN COUNT(*) >= 50 THEN 'BAŞARILI' ELSE 'YETERSİZ' END AS Durum FROM kullanicilar
UNION ALL
SELECT 'Oturum Sayısı (Hedef: = 5)' AS Metrik, COUNT(*) AS Deger, CASE WHEN COUNT(*) = 5 THEN 'BAŞARILI' ELSE 'YETERSİZ' END AS Durum FROM oturumlar
UNION ALL
SELECT 'Benzersiz Soru Sayısı (Hedef: >= 100)' AS Metrik, COUNT(*) AS Deger, CASE WHEN COUNT(*) >= 100 THEN 'BAŞARILI' ELSE 'YETERSİZ' END AS Durum FROM sorular
UNION ALL
SELECT 'Toplam Seçenek Sayısı' AS Metrik, COUNT(*) AS Deger, 'BİLGİ' AS Durum FROM secenekler
UNION ALL
SELECT 'Oturum-Soru Atama Sayısı' AS Metrik, COUNT(*) AS Deger, 'BİLGİ' AS Durum FROM oturum_sorulari
UNION ALL
SELECT 'Katılım Kaydı Sayısı' AS Metrik, COUNT(*) AS Deger, 'BİLGİ' AS Durum FROM katilimlar
UNION ALL
SELECT 'Kullanıcı Cevap Sayısı' AS Metrik, COUNT(*) AS Deger, 'BİLGİ' AS Durum FROM cevaplar;
