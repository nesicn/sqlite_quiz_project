#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite ile Quiz Veri Tabanı - Veri Bütünlüğü Test Betiği (test_integrity.py)
Proje dokümanı Bölüm 3 Madde 5 gereksinimlerini doğrulamak için tasarlanmıştır:
1. Olmayan kullanıcı için cevap engelleme (Foreign Key)
2. Olmayan soru için cevap engelleme (Foreign Key)
3. Oturumda yer almayan bir soruya cevap vermeyi engelleme (Bileşik Foreign Key: oturum_id, soru_id)
4. Tekrar cevap verilmesini engelleme (UNIQUE Constraint)
5. Aynı oturuma aynı sorunun iki kez eklenmesini engelleme (PRIMARY / UNIQUE Key)
6. Geçersiz email veya negatif süre kısıtlamaları (CHECK Constraints)
"""

import os
import sys
import sqlite3

# Fix Windows console encoding
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), "quiz.db")

def run_test(test_name, test_fn):
    print(f"\n[TEST] {test_name}")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        test_fn(conn)
        print("  ❌ HATA: Kısıtlama ihlali bekleniyordu ancak sorgu BAŞARIYLA çalıştı!")
        conn.close()
        return False
    except sqlite3.IntegrityError as e:
        print(f"  [OK] BEKLENEN DAVRANIŞ SAĞLANDI! SQLite Kısıtlama Yakalandı: {e}")
        conn.rollback()
        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ Beklenmeyen Hata: {type(e).__name__} - {e}")
        conn.rollback()
        conn.close()
        return False

# Test Senaryoları
def test_nonexistent_user(conn):
    # Olmayan kullanıcı ID = 99999 ile cevap girme denemesi
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id)
        VALUES (1, 99999, 1, 1, 1);
    """)

def test_nonexistent_question(conn):
    # Olmayan soru ID = 99999 ile cevap girme denemesi
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id)
        VALUES (1, 1, 1, 99999, 1);
    """)

def test_question_not_in_session(conn):
    # Soru ID = 90 sistemde var (sorular tablosunda) ancak Oturum 1'de tanımlı değil!
    # Bileşik Foreign Key (oturum_id, soru_id) -> oturum_sorulari(oturum_id, soru_id) bunu engellemelidir.
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id)
        VALUES (1, 1, 1, 90, 1);
    """)

def test_duplicate_answer(conn):
    # Kullanıcı 1, Oturum 1, Soru 1 için zaten cevap vermişti. İkinci cevap girme denemesi!
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id)
        VALUES (1, 1, 1, 1, 2);
    """)

def test_duplicate_question_in_session(conn):
    # Soru 1 zaten Oturum 1'e eklendi. Tekrar ekleme denemesi.
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO oturum_sorulari (oturum_id, soru_id, soru_sirasi)
        VALUES (1, 1, 99);
    """)

def test_duplicate_session_sequence(conn):
    # Oturum 1'de 1. sıradaki soru zaten var. Başka bir soruyu yine 1. sıraya koyma denemesi.
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO oturum_sorulari (oturum_id, soru_id, soru_sirasi)
        VALUES (1, 90, 1);
    """)

def test_invalid_email_check(conn):
    # CHECK (eposta LIKE '%@%.%') kısıtını ihlal eden geçersiz eposta
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO kullanicilar (kullanici_adi, eposta, ad_soyad)
        VALUES ('invaliduser', 'gecersiz-eposta-adresi', 'Gecersiz Kullanici');
    """)

def test_invalid_duration_check(conn):
    # CHECK (sure_dakika > 0) kısıtını ihlal eden negatif süre
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO oturumlar (baslik, sure_dakika)
        VALUES ('Negatif Sureli Oturum', -15);
    """)

def main():
    print("==========================================================================")
    print("  SQLITE QUIZ VERİ TABANI - VERİ BÜTÜNLÜĞÜ VE KISITLAMA TEST SUITI")
    print("==========================================================================")
    
    if not os.path.exists(DB_PATH):
        print("HATA: quiz.db bulunamadı! Lütfen önce seed.py betiğini çalıştırın.")
        sys.exit(1)
        
    tests = [
        ("1. Olmayan Kullanıcıya Cevap Girme Engeli (FK)", test_nonexistent_user),
        ("2. Olmayan Soruya Cevap Girme Engeli (FK)", test_nonexistent_question),
        ("3. Oturumda Bulunmayan Soruya Cevap Girme Engeli (Bileşik FK)", test_question_not_in_session),
        ("4. Aynı Soruya Tekrar Cevap Verme Engeli (UNIQUE Constraint)", test_duplicate_answer),
        ("5. Aynı Sorunun Oturuma 2 Kez Eklenmesi Engeli (PRIMARY KEY)", test_duplicate_question_in_session),
        ("6. Aynı Sıra Numarasına 2 Soru Eklenme Engeli (UNIQUE Constraint)", test_duplicate_session_sequence),
        ("7. Geçersiz E-Posta Formatı Engeli (CHECK Constraint)", test_invalid_email_check),
        ("8. Negatif Oturum Süresi Engeli (CHECK Constraint)", test_invalid_duration_check)
    ]
    
    passed_count = 0
    total_count = len(tests)
    
    for title, fn in tests:
        if run_test(title, fn):
            passed_count += 1
            
    print("\n==========================================================================")
    print(f" TEST SONUCU: {passed_count}/{total_count} Veri Bütünlüğü Testi BAŞARIYLA Geçti!")
    print("==========================================================================")

if __name__ == "__main__":
    main()
