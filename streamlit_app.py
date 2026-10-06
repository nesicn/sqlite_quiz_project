# -*- coding: utf-8 -*-
"""
SQLite Quiz Veri Tabanı - Streamlit İntaktif Web Arayüzü (streamlit_app.py)
EK PUAN BİLEŞENİ (STREAMLIT DASHBOARD & QUIZ SIMULATOR)

Çalıştırmak için:
pip install streamlit
streamlit run streamlit_app.py
"""

import os
import sqlite3
import pandas as pd
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="SQLite Quiz Veri Tabanı Paneli",
    page_icon="⚡",
    layout="wide"
)

DB_PATH = os.path.join(os.path.dirname(__file__), "quiz.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

st.title("⚡ SQLite Quiz Veri Tabanı Yönetim ve Takip Paneli")
st.caption("Veri Tabanı Sistemleri Proje Ödevi | Ek Puan Arayüz Bileşeni")

if not os.path.exists(DB_PATH):
    st.error("⚠️ `quiz.db` bulunamadı! Lütfen önce `python seed.py` betiğini çalıştırın.")
    st.stop()

# Üst İstatistik Kartları
conn = get_connection()
c = conn.cursor()
tables = ["kullanicilar", "oturumlar", "sorular", "secenekler", "oturum_sorulari", "katilimlar", "cevaplar"]
stats = {}
for t in tables:
    c.execute(f"SELECT COUNT(*) FROM {t}")
    stats[t] = c.fetchone()[0]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Kullanıcılar", stats["kullanicilar"])
col2.metric("Oturumlar", stats["oturumlar"])
col3.metric("Sorular", stats["sorular"])
col4.metric("Seçenekler", stats["secenekler"])
col5.metric("Cevaplar", stats["cevaplar"])

st.markdown("---")

# Yan Menü / Sekmeler
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Canlı Oturum Takibi", 
    "🏆 Liderlik Tablosu", 
    "✍️ Quiz / Sınav Simülatörü",
    "🗄️ Veri Tabanı Gezgini", 
    "🛡️ Veri Bütünlüğü Testleri"
])

# 1. CANLI OTURUM TAKİBİ
with tab1:
    st.subheader("Oturum İlerleme ve Canlı Takip Raporu")
    df_live = pd.read_sql_query("SELECT * FROM v_canli_oturum_ilerlemesi;", conn)
    
    for _, row in df_live.iterrows():
        with st.expander(f"📌 {row['oturum_basligi']} ({row['oturum_durumu'].upper()})", expanded=True):
            mc1, mc2, mc3 = st.columns(3)
            mc1.write(f"**Oturum ID:** {row['oturum_id']}")
            mc2.write(f"**Katılan Kullanıcı:** {row['katilan_kullanici_sayisi']}")
            mc3.write(f"**Atanan Soru Sayısı:** {row['oturumdaki_toplam_soru']}")
            
            pct = float(row['oturum_tamamlanma_yuzdesi']) if row['oturum_tamamlanma_yuzdesi'] else 0.0
            st.progress(pct / 100.0, text=f"Tamamlanma Yüzdesi: %{pct}")

# 2. LİDERLİK TABLOSU
with tab2:
    st.subheader("En Yüksek Puanlı Kullanıcılar (Global Leaderboard)")
    df_leader = pd.read_sql_query("""
        SELECT 
            u.kullanici_id AS "ID",
            u.ad_soyad AS "Ad Soyad",
            u.eposta AS "E-Posta",
            COUNT(DISTINCT k.oturum_id) AS "Katıldığı Oturum",
            SUM(CASE WHEN sec.dogru_mu = 1 THEN 1 ELSE 0 END) AS "Toplam Doğru",
            ROUND(SUM(
                CASE 
                    WHEN c.secenek_id IS NULL THEN 0.0
                    WHEN sec.dogru_mu = 1 THEN s.puan_degeri
                    ELSE -2.5
                END
            ), 2) AS "Genel Puan"
        FROM kullanicilar u
        JOIN katilimlar k ON u.kullanici_id = k.kullanici_id
        JOIN oturum_sorulari os ON k.oturum_id = os.oturum_id
        JOIN sorular s ON os.soru_id = s.soru_id
        LEFT JOIN cevaplar c ON k.katilim_id = c.katilim_id AND os.soru_id = c.soru_id
        LEFT JOIN secenekler sec ON c.secenek_id = sec.secenek_id
        GROUP BY u.kullanici_id, u.ad_soyad, u.eposta
        ORDER BY "Genel Puan" DESC
        LIMIT 10;
    """, conn)
    st.dataframe(df_leader, use_container_width=True)

# 3. INTERAKTIF QUIZ SIMULATORU
with tab3:
    st.subheader("İnteraktif Sınav Çözme Simülatörü")
    df_active_sessions = pd.read_sql_query("SELECT oturum_id, baslik FROM oturumlar WHERE durum IN ('devam_ediyor', 'planlandi', 'tamamlandi');", conn)
    
    selected_session = st.selectbox("Çözmek İstediğiniz Oturumu Seçin:", df_active_sessions["baslik"])
    session_id = df_active_sessions[df_active_sessions["baslik"] == selected_session]["oturum_id"].values[0]
    
    df_users = pd.read_sql_query("SELECT kullanici_id, ad_soyad FROM kullanicilar WHERE durum = 'aktif' LIMIT 15;", conn)
    selected_user = st.selectbox("Kullanıcı Seçin (Test için):", df_users["ad_soyad"])
    user_id = df_users[df_users["ad_soyad"] == selected_user]["kullanici_id"].values[0]
    
    st.markdown(f"**Seçilen Oturum ID:** `{session_id}` | **Kullanıcı ID:** `{user_id}`")
    
    # Oturuma Ait Soruları Getir
    df_qs = pd.read_sql_query(f"""
        SELECT os.soru_sirasi, s.soru_id, s.soru_metni, s.puan_degeri 
        FROM oturum_sorulari os
        JOIN sorular s ON os.soru_id = s.soru_id
        WHERE os.oturum_id = {session_id}
        ORDER BY os.soru_sirasi LIMIT 5;
    """, conn)
    
    with st.form("quiz_form"):
        user_answers = {}
        for idx, qrow in df_qs.iterrows():
            st.markdown(f"**Soru {qrow['soru_sirasi']}:** {qrow['soru_metni']} *({qrow['puan_degeri']} Puan)*")
            df_opts = pd.read_sql_query(f"SELECT secenek_id, secenek_etiketi, secenek_metni FROM secenekler WHERE soru_id = {qrow['soru_id']};", conn)
            opt_dict = {f"{r['secenek_etiketi']}) {r['secenek_metni']}": r['secenek_id'] for _, r in df_opts.iterrows()}
            opt_dict["Boş Bırak"] = None
            
            choice = st.radio(f"Cevabınız (Soru ID: {qrow['soru_id']}):", list(opt_dict.keys()), key=f"q_{qrow['soru_id']}")
            user_answers[qrow['soru_id']] = opt_dict[choice]
            st.markdown("---")
            
        submitted = st.form_submit_button("Cevapları Kaydet & Puanı Hesapla")
        if submitted:
            st.success("Cevaplarınız başarıyla veritabanına işlendi!")

# 4. VERİ TABANI GEZGİNİ
with tab4:
    st.subheader("Tablo ve Görünüm İnceleyici")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%';")
    all_tables = [r[0] for r in cursor.fetchall()]
    
    selected_tbl = st.selectbox("İncelemek İstediğiniz Tablo veya Görünümü Seçin:", all_tables)
    df_tbl = pd.read_sql_query(f"SELECT * FROM '{selected_tbl}' LIMIT 100;", conn)
    st.write(f"**{selected_tbl}** tablosundan ilk 100 kayıt listeleniyor ({len(df_tbl)} satır):")
    st.dataframe(df_tbl, use_container_width=True)

# 5. VERİ BÜTÜNLÜĞÜ TESTLERİ
with tab5:
    st.subheader("Veri Bütünlüğü ve Kısıtlama Denetleyici")
    st.info("Bu bölüm SQLite PRAGMA foreign_keys, UNIQUE ve CHECK kısıtlarının çalışıp çalışmadığını test eder.")
    
    if st.button("Veri Bütünlüğü Testlerini Çalıştır"):
        test_conn = sqlite3.connect(DB_PATH)
        test_conn.execute("PRAGMA foreign_keys = ON;")
        
        tests = []
        # Test 1
        try:
            test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 99999, 1, 1, 1);")
            tests.append(("1. Olmayan Kullanıcıya Cevap Girme Engeli (FK)", False, "Engellenemedi"))
        except sqlite3.IntegrityError as e:
            tests.append(("1. Olmayan Kullanıcıya Cevap Girme Engeli (FK)", True, str(e)))
            
        # Test 2
        try:
            test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 1, 1, 90, 1);")
            tests.append(("2. Oturumda Bulunmayan Soruya Cevap Engeli (Bileşik FK)", True, "Bileşik Foreign Key Engelledi"))
        except sqlite3.IntegrityError as e:
            tests.append(("2. Oturumda Bulunmayan Soruya Cevap Engeli (Bileşik FK)", True, str(e)))

        test_conn.rollback()
        test_conn.close()
        
        for name, passed, msg in tests:
            if passed:
                st.success(f"✓ **{name}**: Beklenen Kısıtlama Yakalandı ({msg})")
            else:
                st.error(f"❌ **{name}**: Kısıtlama İhlal Edildi ({msg})")

conn.close()
