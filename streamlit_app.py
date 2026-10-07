"""
Quiz Sistemi Veritabanı Yönetimi ve Kullanıcı Arayüzü
Kurumsal ve Minimalist Streamlit Uygulaması (Hoca ve Öğrenci Modları)
"""

import os
import random
import sqlite3
import streamlit as st

# Sayfa Yapılandırması (Sıfır Emoji)
st.set_page_config(
    page_title="Quiz Sistemi Veri Tabanı Yönetimi",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_PATH = os.path.join(os.path.dirname(__file__), "quiz.db")

# -----------------------------------------------------------------------------
# ÖZEL KURUMSAL VE MİNİMALİST CSS (MONOKROM PALET)
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* Global Sayfa Arka Planı ve Tipografi */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1E293B;
}

.stApp {
    background-color: #F8F9FA;
}

/* Başlıklar */
h1, h2, h3, h4, h5, h6 {
    color: #0F172A;
    font-weight: 600;
    letter-spacing: -0.01em;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1160px;
}

/* Üst Başlık Şeridi */
.app-header {
    margin-bottom: 1.25rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #E2E8F0;
}

.app-title {
    font-size: 20px;
    font-weight: 700;
    color: #0F172A;
    margin: 0;
    padding: 0;
}

.app-subtitle {
    font-size: 13px;
    color: #64748B;
    margin-top: 4px;
    margin-bottom: 0;
}

/* Sekmeler (Tabs) */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 2px;
}

.stTabs [data-baseweb="tab"] {
    height: 40px;
    padding: 6px 16px;
    background-color: transparent;
    color: #64748B;
    font-weight: 500;
    font-size: 13px;
    border: none;
    border-radius: 4px 4px 0 0;
}

.stTabs [aria-selected="true"] {
    color: #2563EB !important;
    border-bottom: 2px solid #2563EB !important;
    font-weight: 600 !important;
    background-color: transparent !important;
}

/* Kurumsal Butonlar */
.stButton > button {
    background-color: #2563EB;
    color: #FFFFFF;
    border: 1px solid #1D4ED8;
    border-radius: 5px;
    padding: 0.45rem 1rem;
    font-weight: 500;
    font-size: 13px;
    box-shadow: none;
    transition: background-color 0.15s ease-in-out;
}

.stButton > button:hover {
    background-color: #1D4ED8;
    border-color: #1E40AF;
    color: #FFFFFF;
}

.stButton > button:active {
    background-color: #1E40AF;
}

/* Kart Yapıları */
.card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 16px 20px;
    margin-bottom: 14px;
}

.card-title {
    font-size: 15px;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 10px;
}

/* İstatistik Metrik Kutuları */
.metric-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 12px;
}

.metric-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748B;
    font-weight: 600;
    margin-bottom: 2px;
}

.metric-val {
    font-size: 20px;
    font-weight: 700;
    color: #0F172A;
}

/* Soft Bildirim Kutuları */
.alert-box {
    padding: 12px 16px;
    border-radius: 5px;
    font-size: 13px;
    line-height: 1.5;
    margin-top: 10px;
    margin-bottom: 10px;
}

.alert-success {
    background-color: #F0FDF4;
    border: 1px solid #BBF7D0;
    color: #166534;
}

.alert-error {
    background-color: #FEF2F2;
    border: 1px solid #FECACA;
    color: #991B1B;
}

.alert-info {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    color: #334155;
}

/* Rozetler (Badges) */
.badge {
    display: inline-block;
    padding: 2px 7px;
    font-size: 11px;
    font-weight: 500;
    border-radius: 3px;
    margin-right: 6px;
}

.badge-blue {
    background-color: #EFF6FF;
    color: #1D4ED8;
    border: 1px solid #DBEAFE;
}

.badge-gray {
    background-color: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
}

.badge-green {
    background-color: #F0FDF4;
    color: #166534;
    border: 1px solid #BBF7D0;
}

.badge-red {
    background-color: #FEF2F2;
    color: #991B1B;
    border: 1px solid #FECACA;
}

/* Form Elemanları */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    font-size: 13px;
    color: #1E293B;
}

/* Üst Menü ve Altbilgi Gizleme */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VERİ TABANI YÖNETİMİ
# -----------------------------------------------------------------------------
def get_db_connection():
    """SQLite veritabanı bağlantısı açar ve FK kısıtlamalarını etkinleştirir."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database():
    """Uygulama açılışında questions tablosunu oluşturur ve gerekirse veri aktarır."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL CHECK(length(trim(question_text)) > 0),
            option_a TEXT NOT NULL CHECK(length(trim(option_a)) > 0),
            option_b TEXT NOT NULL CHECK(length(trim(option_b)) > 0),
            option_c TEXT NOT NULL CHECK(length(trim(option_c)) > 0),
            option_d TEXT NOT NULL CHECK(length(trim(option_d)) > 0),
            correct_option TEXT NOT NULL CHECK(correct_option IN ('A', 'B', 'C', 'D')),
            category TEXT NOT NULL DEFAULT 'Genel',
            difficulty TEXT NOT NULL DEFAULT 'Orta' CHECK(difficulty IN ('Kolay', 'Orta', 'Zor')),
            created_at DATETIME NOT NULL DEFAULT (datetime('now', 'localtime'))
        );
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM questions;")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sorular';")
        has_sorular = cursor.fetchone()

        if has_sorular:
            cursor.execute("""
                SELECT 
                    s.soru_metni,
                    COALESCE(MAX(CASE WHEN sec.secenek_etiketi = 'A' THEN sec.secenek_metni END), 'Seçenek A') AS opt_a,
                    COALESCE(MAX(CASE WHEN sec.secenek_etiketi = 'B' THEN sec.secenek_metni END), 'Seçenek B') AS opt_b,
                    COALESCE(MAX(CASE WHEN sec.secenek_etiketi = 'C' THEN sec.secenek_metni END), 'Seçenek C') AS opt_c,
                    COALESCE(MAX(CASE WHEN sec.secenek_etiketi = 'D' THEN sec.secenek_metni END), 'Seçenek D') AS opt_d,
                    COALESCE(MAX(CASE WHEN sec.dogru_mu = 1 THEN sec.secenek_etiketi END), 'A') AS correct_opt,
                    s.kategori,
                    CASE s.zorluk_seviyesi 
                        WHEN 'kolay' THEN 'Kolay' 
                        WHEN 'zor' THEN 'Zor' 
                        ELSE 'Orta' 
                    END AS zorluk
                FROM sorular s
                LEFT JOIN secenekler sec ON s.soru_id = sec.soru_id
                GROUP BY s.soru_id;
            """)
            imported_rows = cursor.fetchall()
            if imported_rows:
                cursor.executemany("""
                    INSERT INTO questions (question_text, option_a, option_b, option_c, option_d, correct_option, category, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, imported_rows)
                conn.commit()

    conn.close()


init_database()


# -----------------------------------------------------------------------------
# VERİ GETİRME FONKSİYONLARI
# -----------------------------------------------------------------------------
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM questions ORDER BY category;")
    cats = [r[0] for r in cursor.fetchall() if r[0]]
    conn.close()
    return cats


def get_filtered_questions(category_filter=None, difficulty_filter=None, search_query=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, question_text, option_a, option_b, option_c, option_d, correct_option, category, difficulty, created_at FROM questions WHERE 1=1"
    params = []

    if category_filter and category_filter != "Tüm Konular":
        query += " AND category = ?"
        params.append(category_filter)

    if difficulty_filter and difficulty_filter != "Tüm Zorluklar":
        query += " AND difficulty = ?"
        params.append(difficulty_filter)

    if search_query and search_query.strip():
        query += " AND question_text LIKE ?"
        params.append(f"%{search_query.strip()}%")

    query += " ORDER BY id DESC;"
    cursor.execute(query, params)
    cols = ["id", "question_text", "option_a", "option_b", "option_c", "option_d", "correct_option", "category", "difficulty", "created_at"]
    rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
    conn.close()
    return rows


def insert_new_question(text, opt_a, opt_b, opt_c, opt_d, correct, category, difficulty):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO questions (question_text, option_a, option_b, option_c, option_d, correct_option, category, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (text.strip(), opt_a.strip(), opt_b.strip(), opt_c.strip(), opt_d.strip(), correct, category.strip(), difficulty))

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sorular';")
        if cursor.fetchone():
            cursor.execute("""
                INSERT INTO sorular (soru_metni, kategori, zorluk_seviyesi, puan_degeri)
                VALUES (?, ?, ?, 10.0);
            """, (text.strip(), category.strip(), difficulty.lower()))
            new_soru_id = cursor.lastrowid

            opts = [
                ('A', opt_a.strip(), 1 if correct == 'A' else 0),
                ('B', opt_b.strip(), 1 if correct == 'B' else 0),
                ('C', opt_c.strip(), 1 if correct == 'C' else 0),
                ('D', opt_d.strip(), 1 if correct == 'D' else 0)
            ]
            for etiket, mtn, dogru in opts:
                cursor.execute("""
                    INSERT INTO secenekler (soru_id, secenek_etiketi, secenek_metni, dogru_mu)
                    VALUES (?, ?, ?, ?);
                """, (new_soru_id, etiket, mtn, dogru))

        conn.commit()
        return True, "Soru başarıyla veritabanına kaydedildi."
    except Exception as e:
        conn.rollback()
        return False, f"Veritabanı hatası: {e}"
    finally:
        conn.close()


def delete_question_by_id(question_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM questions WHERE id = ?;", (question_id,))
        conn.commit()
        return True, f"Soru (ID: {question_id}) veritabanından silindi."
    except Exception as e:
        conn.rollback()
        return False, f"Silme işlemi başarısız: {e}"
    finally:
        conn.close()


def get_student_results_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            k.oturum_id,
            o.baslik AS oturum_basligi,
            u.kullanici_id,
            u.ad_soyad,
            u.eposta,
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
                ), 2), 0.0) >= o.gecme_notu THEN 'BASARILI'
                ELSE 'BASARISIZ'
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
    """)
    cols = [
        "oturum_id", "oturum_basligi", "kullanici_id", "ad_soyad", "eposta",
        "toplam_soru", "cevaplanan_soru", "dogru_sayisi", "yanlis_sayisi",
        "bos_sayisi", "toplam_puan", "durum_sonucu"
    ]
    rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_live_sessions_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            o.oturum_id,
            o.baslik AS oturum_basligi,
            o.durum AS oturum_durumu,
            o.baslangic_zaman,
            o.bitis_zaman,
            o.sure_dakika,
            o.gecme_notu,
            COUNT(DISTINCT os.soru_id) AS toplam_soru,
            COUNT(DISTINCT k.katilim_id) AS katilan_kullanici,
            COUNT(c.cevap_id) AS toplam_cevap,
            ROUND(
                CASE 
                    WHEN (COUNT(DISTINCT k.katilim_id) * COUNT(DISTINCT os.soru_id)) = 0 THEN 0.0
                    ELSE (CAST(COUNT(c.cevap_id) AS REAL) / (COUNT(DISTINCT k.katilim_id) * COUNT(DISTINCT os.soru_id))) * 100.0
                END, 1
            ) AS tamamlanma_orani
        FROM oturumlar o
        LEFT JOIN oturum_sorulari os ON o.oturum_id = os.oturum_id
        LEFT JOIN katilimlar k ON o.oturum_id = k.oturum_id
        LEFT JOIN cevaplar c ON k.katilim_id = c.katilim_id AND os.soru_id = c.soru_id
        GROUP BY o.oturum_id
        ORDER BY o.oturum_id;
    """)
    cols = [
        "oturum_id", "oturum_basligi", "oturum_durumu", "baslangic_zaman",
        "bitis_zaman", "sure_dakika", "gecme_notu", "toplam_soru",
        "katilan_kullanici", "toplam_cevap", "tamamlanma_orani"
    ]
    rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_hardest_questions_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.soru_id,
            s.soru_metni,
            s.kategori,
            s.zorluk_seviyesi,
            COUNT(c.cevap_id) AS toplam_yanitlanma,
            SUM(CASE WHEN sec.dogru_mu = 1 THEN 1 ELSE 0 END) AS dogru_sayisi,
            SUM(CASE WHEN sec.dogru_mu = 0 THEN 1 ELSE 0 END) AS yanlis_sayisi,
            ROUND(
                (CAST(SUM(CASE WHEN sec.dogru_mu = 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(c.cevap_id)) * 100.0, 
                1
            ) AS yanlis_orani
        FROM sorular s
        JOIN cevaplar c ON s.soru_id = c.soru_id
        JOIN secenekler sec ON c.secenek_id = sec.secenek_id
        GROUP BY s.soru_id
        HAVING toplam_yanitlanma >= 5
        ORDER BY yanlis_orani DESC
        LIMIT 10;
    """)
    cols = [
        "soru_id", "soru_metni", "kategori", "zorluk_seviyesi",
        "toplam_yanitlanma", "dogru_sayisi", "yanlis_sayisi", "yanlis_orani"
    ]
    rows = [dict(zip(cols, r)) for r in cursor.fetchall()]
    conn.close()
    return rows


# -----------------------------------------------------------------------------
# SESSION STATE YÖNETİMİ
# -----------------------------------------------------------------------------
if "quiz_active_id" not in st.session_state:
    st.session_state.quiz_active_id = None

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_user_answer" not in st.session_state:
    st.session_state.quiz_user_answer = None

if "quiz_stats" not in st.session_state:
    st.session_state.quiz_stats = {"total": 0, "correct": 0, "wrong": 0}


# -----------------------------------------------------------------------------
# ÜST BAŞLIK VE GÖRÜNÜM / ROL SEÇİCİSİ
# -----------------------------------------------------------------------------
col_header_title, col_header_role = st.columns([2.5, 1.5])

with col_header_title:
    st.markdown("""
    <div class="app-header">
        <div class="app-title">Quiz Sistemi Veri Tabanı Yönetimi</div>
        <div class="app-subtitle">İlişkisel Veri Katmanı, Öğrenci Takibi ve Test Paneli | SQLite3</div>
    </div>
    """, unsafe_allow_html=True)

with col_header_role:
    selected_view = st.selectbox(
        "Kullanıcı Rolü / Görünüm Modu",
        ["Eğitmen / Hoca Paneli", "Öğrenci (Quiz Çözümü)"],
        index=0,
        help="Hoca ekranı ile öğrenci sınav çözme ekranı arasında geçiş yapabilirsiniz."
    )


# =============================================================================
# EĞİTMEN / HOCA PANELİ
# =============================================================================
if selected_view == "Eğitmen / Hoca Paneli":
    tab_students, tab_sessions, tab_analytics, tab_questions = st.tabs([
        "Öğrenci ve Sınav Sonuçları",
        "Oturum ve Canlı İlerleme",
        "Soru Analitiği",
        "Soru Yönetimi ve Kısıtlar"
    ])

    # -------------------------------------------------------------------------
    # HOCA PANELİ - 1. SEKME: ÖĞRENCİ VE SINAV SONUÇLARI
    # -------------------------------------------------------------------------
    with tab_students:
        all_results = get_student_results_data()

        # Üst Özet Kartları
        total_enrollments = len(all_results)
        passed_count = sum(1 for r in all_results if r["durum_sonucu"] == "BASARILI")
        failed_count = sum(1 for r in all_results if r["durum_sonucu"] == "BASARISIZ")
        avg_score = (sum(r["toplam_puan"] for r in all_results) / total_enrollments) if total_enrollments > 0 else 0.0

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Toplam Sınav Katılımı</div>
                <div class="metric-val">{total_enrollments}</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Başarılı (Geçti)</div>
                <div class="metric-val" style="color: #166534;">{passed_count}</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Başarısız (Kaldı)</div>
                <div class="metric-val" style="color: #991B1B;">{failed_count}</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Ortalama Puan</div>
                <div class="metric-val">{avg_score:.1f}</div>
            </div>
            """, unsafe_allow_html=True)

        # Filtreleme Alanı
        col_f_sess, col_f_status, col_f_search = st.columns([1.5, 1, 2])
        session_titles = ["Tüm Oturumlar"] + sorted(list({r["oturum_basligi"] for r in all_results}))

        with col_f_sess:
            f_sess = st.selectbox("Oturum Filtresi", session_titles, key="admin_sess_filter")
        with col_f_status:
            f_status = st.selectbox("Durum Filtresi", ["Tümü", "BASARILI", "BASARISIZ"], key="admin_stat_filter")
        with col_f_search:
            f_search = st.text_input("Öğrenci Ara", placeholder="Öğrenci adı veya e-posta...", key="admin_stud_search")

        # Filtre Uygulama
        filtered_results = all_results
        if f_sess != "Tüm Oturumlar":
            filtered_results = [r for r in filtered_results if r["oturum_basligi"] == f_sess]
        if f_status != "Tümü":
            filtered_results = [r for r in filtered_results if r["durum_sonucu"] == f_status]
        if f_search.strip():
            filtered_results = [r for r in filtered_results if f_search.strip().lower() in r["ad_soyad"].lower() or f_search.strip().lower() in r["eposta"].lower()]

        st.markdown(f"<div style='font-size: 13px; color: #64748B; margin-bottom: 8px;'>Listelenen Öğrenci Kaydı: <strong>{len(filtered_results)}</strong></div>", unsafe_allow_html=True)

        # Tablo Formatlama
        table_rows = []
        for r in filtered_results:
            table_rows.append({
                "Öğrenci ID": r["kullanici_id"],
                "Ad Soyad": r["ad_soyad"],
                "E-Posta": r["eposta"],
                "Oturum": r["oturum_basligi"],
                "Soru": r["toplam_soru"],
                "Doğru": r["dogru_sayisi"],
                "Yanlış": r["yanlis_sayisi"],
                "Boş": r["bos_sayisi"],
                "Net Puan": r["toplam_puan"],
                "Durum": r["durum_sonucu"]
            })

        st.dataframe(table_rows, use_container_width=True, hide_index=True)

        # Öğrenci Detay Karnesi (Transkript İnceleme)
        st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">Öğrenci Sınav Karnesi ve Cevap Detayları</div>', unsafe_allow_html=True)

        if filtered_results:
            student_options = [f"ID {r['kullanici_id']} - {r['ad_soyad']} ({r['oturum_basligi'][:30]}...)" for r in filtered_results]
            selected_student_label = st.selectbox("İncelemek İstediğiniz Öğrenciyi Seçin:", student_options)

            selected_idx = student_options.index(selected_student_label)
            target_record = filtered_results[selected_idx]

            # Öğrencinin o oturumdaki soru bazlı cevaplarını çek
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    os.soru_sirasi,
                    s.soru_id,
                    s.soru_metni,
                    sec.secenek_etiketi,
                    sec.secenek_metni,
                    COALESCE(sec.dogru_mu, 0) AS dogru_mu,
                    CASE 
                        WHEN c.secenek_id IS NULL THEN 0.0
                        WHEN sec.dogru_mu = 1 THEN s.puan_degeri
                        ELSE -2.5
                    END AS alinan_puan,
                    c.cevaplama_zamani
                FROM oturum_sorulari os
                JOIN sorular s ON os.soru_id = s.soru_id
                LEFT JOIN cevaplar c ON os.oturum_id = c.oturum_id AND os.soru_id = c.soru_id AND c.kullanici_id = ?
                LEFT JOIN secenekler sec ON c.secenek_id = sec.secenek_id
                WHERE os.oturum_id = ?
                ORDER BY os.soru_sirasi;
            """, (target_record["kullanici_id"], target_record["oturum_id"]))

            answer_rows = cursor.fetchall()
            conn.close()

            detail_table = []
            for ar in answer_rows:
                sira = ar[0]
                metin = ar[2][:85] + ("..." if len(ar[2]) > 85 else "")
                cevap = f"{ar[3]}) {ar[4]}" if ar[3] else "BOŞ (Cevaplanmadı)"
                durum = "[DOGRU]" if ar[5] == 1 else ("[BOS]" if ar[3] is None else "[YANLIS]")
                puan = ar[6]

                detail_table.append({
                    "Sıra": sira,
                    "Soru Metni": metin,
                    "Verilen Cevap": cevap,
                    "Durum": durum,
                    "Alınan Puan": puan
                })

            st.dataframe(detail_table, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # HOCA PANELİ - 2. SEKME: OTURUM VE CANLI İLERLEME
    # -------------------------------------------------------------------------
    with tab_sessions:
        st.markdown('<div class="card-title">Oturum İlerleme ve Canlı Takip Raporu</div>', unsafe_allow_html=True)
        sessions_data = get_live_sessions_data()

        for s_row in sessions_data:
            durum_str = s_row["oturum_durumu"].upper()
            badge_class = "badge-green" if durum_str == "TAMAMLANDI" else ("badge-blue" if durum_str == "DEVAM_EDIYOR" else "badge-gray")

            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span class="badge {badge_class}">Oturum {s_row['oturum_id']} | {durum_str}</span>
                        <strong style="font-size: 15px; color: #0F172A;">{s_row['oturum_basligi']}</strong>
                    </div>
                    <div style="font-size: 12px; color: #64748B;">
                        Süre: {s_row['sure_dakika']} dk | Baraj: {s_row['gecme_notu']} Puan
                    </div>
                </div>
                <div style="display: flex; gap: 24px; font-size: 13px; color: #475569; margin-bottom: 10px;">
                    <div>Katılan Öğrenci: <strong>{s_row['katilan_kullanici']}</strong></div>
                    <div>Atanan Soru: <strong>{s_row['toplam_soru']}</strong></div>
                    <div>Verilen Toplam Cevap: <strong>{s_row['toplam_cevap']}</strong></div>
                    <div>Tamamlanma Oranı: <strong>%{s_row['tamamlanma_orani']}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(float(s_row["tamamlanma_orani"]) / 100.0)

        # Devam Eden Oturum Canlı İlerleyişi
        st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">Devam Eden Oturumda Anlık Kullanıcı İlerlemesi</div>', unsafe_allow_html=True)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                o.oturum_id,
                o.baslik AS oturum_basligi,
                u.kullanici_id,
                u.ad_soyad,
                (SELECT COUNT(*) FROM oturum_sorulari os WHERE os.oturum_id = o.oturum_id) AS oturum_soru_sayisi,
                COUNT(c.cevap_id) AS yanitlanan_soru,
                ((SELECT COUNT(*) FROM oturum_sorulari os WHERE os.oturum_id = o.oturum_id) - COUNT(c.cevap_id)) AS kalan_soru,
                ROUND(
                    (CAST(COUNT(c.cevap_id) AS REAL) / (SELECT COUNT(*) FROM oturum_sorulari os WHERE os.oturum_id = o.oturum_id)) * 100.0, 
                    1
                ) AS ilerleme_yuzdesi
            FROM katilimlar kt
            JOIN oturumlar o ON kt.oturum_id = o.oturum_id
            JOIN kullanicilar u ON kt.kullanici_id = u.kullanici_id
            LEFT JOIN cevaplar c ON kt.katilim_id = c.katilim_id
            WHERE o.durum = 'devam_ediyor'
            GROUP BY o.oturum_id, u.kullanici_id, u.ad_soyad
            ORDER BY ilerleme_yuzdesi DESC;
        """)
        live_active_rows = cursor.fetchall()
        conn.close()

        if live_active_rows:
            live_table = [{
                "Öğrenci ID": r[2],
                "Ad Soyad": r[3],
                "Oturum Soru Sayısı": r[4],
                "Yanıtlanan": r[5],
                "Kalan": r[6],
                "İlerleme (%)": f"%{r[7]}"
            } for r in live_active_rows]
            st.dataframe(live_table, use_container_width=True, hide_index=True)
        else:
            st.markdown("<div class='alert-box alert-info'>Şu anda 'devam_ediyor' durumunda aktif oturum bulunmamaktadır.</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # HOCA PANELİ - 3. SEKME: SORU ANALİTİĞİ
    # -------------------------------------------------------------------------
    with tab_analytics:
        st.markdown('<div class="card-title">En Çok Zorlanılan ve Yanlış Yapılan Sorular Analizi</div>', unsafe_allow_html=True)
        st.markdown("<div style='font-size: 13px; color: #64748B; margin-bottom: 12px;'>Öğrencilerin sınavlar genelinde en çok yanlış yanıt verdiği ilk 10 soru listelenmektedir:</div>", unsafe_allow_html=True)

        hard_questions = get_hardest_questions_data()
        if hard_questions:
            hq_table = [{
                "Soru ID": r["soru_id"],
                "Soru Metni": r["soru_metni"][:70] + "...",
                "Kategori": r["kategori"],
                "Zorluk": r["zorluk_seviyesi"],
                "Toplam Yanıt": r["toplam_yanitlanma"],
                "Doğru": r["dogru_sayisi"],
                "Yanlış": r["yanlis_sayisi"],
                "Hata Oranı (%)": f"%{r['yanlis_orani']}"
            } for r in hard_questions]
            st.dataframe(hq_table, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # HOCA PANELİ - 4. SEKME: SORU YÖNETİMİ VE KISITLAR
    # -------------------------------------------------------------------------
    with tab_questions:
        st.markdown('<div class="card-title">Yeni Quiz Sorusu Ekleme</div>', unsafe_allow_html=True)

        with st.form("add_question_form", clear_on_submit=True):
            new_q_text = st.text_area("Soru Metni", placeholder="Örn: SQL'de verileri silmek için kullanılan komut hangisidir?")

            col_a, col_b = st.columns(2)
            with col_a:
                new_opt_a = st.text_input("Seçenek A", placeholder="A şıkkı metni")
                new_opt_c = st.text_input("Seçenek C", placeholder="C şıkkı metni")
            with col_b:
                new_opt_b = st.text_input("Seçenek B", placeholder="B şıkkı metni")
                new_opt_d = st.text_input("Seçenek D", placeholder="D şıkkı metni")

            col_meta_1, col_meta_2, col_meta_3 = st.columns(3)
            with col_meta_1:
                new_correct = st.selectbox("Doğru Seçenek", ["A", "B", "C", "D"])
            with col_meta_2:
                new_category = st.text_input("Kategori / Konu", value="SQL Temelleri")
            with col_meta_3:
                new_difficulty = st.selectbox("Zorluk Derecesi", ["Kolay", "Orta", "Zor"], index=1)

            submitted_new_q = st.form_submit_button("Soruyu Veritabanına Kaydet")

            if submitted_new_q:
                if not new_q_text.strip() or not new_opt_a.strip() or not new_opt_b.strip() or not new_opt_c.strip() or not new_opt_d.strip():
                    st.markdown("<div class='alert-box alert-error'>Lütfen soru metnini ve tüm seçenekleri (A, B, C, D) eksiksiz doldurunuz.</div>", unsafe_allow_html=True)
                else:
                    success, msg = insert_new_question(
                        new_q_text, new_opt_a, new_opt_b, new_opt_c, new_opt_d,
                        new_correct, new_category, new_difficulty
                    )
                    alert_cls = "alert-success" if success else "alert-error"
                    st.markdown(f"<div class='alert-box {alert_cls}'>{msg}</div>", unsafe_allow_html=True)

        st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)

        # Soru Silme ve Yönetim
        st.markdown('<div class="card-title">Mevcut Sorular ve Silme İşlemi</div>', unsafe_allow_html=True)
        all_q_list = get_filtered_questions()

        if all_q_list:
            col_del_select, col_del_btn = st.columns([3, 1])
            with col_del_select:
                q_options_list = [f"ID {row['id']}: {row['question_text'][:80]}..." for row in all_q_list]
                selected_del_label = st.selectbox("Silinecek Soruyu Seçiniz", q_options_list)
                del_id = int(selected_del_label.split(":")[0].replace("ID ", "").strip())

            with col_del_btn:
                st.write("")
                st.write("")
                if st.button("Seçili Soruyu Sil", use_container_width=True):
                    del_success, del_msg = delete_question_by_id(del_id)
                    alert_cls = "alert-success" if del_success else "alert-error"
                    st.markdown(f"<div class='alert-box {alert_cls}'>{del_msg}</div>", unsafe_allow_html=True)
                    st.rerun()

        # Sistem Bütünlüğü Kısıt Denetimi
        with st.expander("Sistem Durumu ve Veri Bütünlüğü Kısıt Denetimi"):
            st.markdown("<div style='font-size: 13px; color: #475569; margin-bottom: 12px;'>SQLite PRAGMA foreign_keys, Composite Foreign Key, UNIQUE ve CHECK kısıtlamalarını doğrular.</div>", unsafe_allow_html=True)

            if st.button("Veri Bütünlüğü Testlerini Çalıştır"):
                test_conn = sqlite3.connect(DB_PATH)
                test_conn.execute("PRAGMA foreign_keys = ON;")
                test_results = []

                # 1. Olmayan kullanıcı FK testi
                try:
                    test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 99999, 1, 1, 1);")
                    test_results.append(("1. Olmayan Kullanıcıya Cevap Engeli (FK)", False, "Kısıtlama tetiklenmedi"))
                except sqlite3.IntegrityError:
                    test_results.append(("1. Olmayan Kullanıcıya Cevap Engeli (FK)", True, "FOREIGN KEY kısıtlaması işlemi engelledi"))

                # 2. Olmayan soru FK testi
                try:
                    test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 1, 1, 99999, 1);")
                    test_results.append(("2. Olmayan Soruya Cevap Engeli (FK)", False, "Kısıtlama tetiklenmedi"))
                except sqlite3.IntegrityError:
                    test_results.append(("2. Olmayan Soruya Cevap Engeli (FK)", True, "FOREIGN KEY kısıtlaması işlemi engelledi"))

                # 3. Oturumda yer almayan soruya cevap (Bileşik FK)
                try:
                    test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 1, 1, 90, 1);")
                    test_results.append(("3. Oturumda Bulunmayan Soruya Cevap Engeli (Bileşik FK)", False, "Kısıtlama tetiklenmedi"))
                except sqlite3.IntegrityError:
                    test_results.append(("3. Oturumda Bulunmayan Soruya Cevap Engeli (Bileşik FK)", True, "Bileşik FOREIGN KEY (oturum_id, soru_id) işlemi engelledi"))

                # 4. Soruya ait olmayan seçenek (Bileşik FK: soru_id, secenek_id)
                try:
                    test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 50, 1, 1, 7);")
                    test_results.append(("4. Başka Soruya Ait Seçeneğe Cevap Verme Engeli (Bileşik FK)", False, "Kısıtlama tetiklenmedi"))
                except sqlite3.IntegrityError:
                    test_results.append(("4. Başka Soruya Ait Seçeneğe Cevap Verme Engeli (Bileşik FK)", True, "Bileşik FOREIGN KEY (soru_id, secenek_id) işlemi engelledi"))

                # 5. Tekrar cevap verme engeli (UNIQUE)
                try:
                    test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 1, 1, 1, 2);")
                    test_results.append(("5. Aynı Soruya Tekrar Cevap Verme Engeli (UNIQUE)", False, "Kısıtlama tetiklenmedi"))
                except sqlite3.IntegrityError:
                    test_results.append(("5. Aynı Soruya Tekrar Cevap Verme Engeli (UNIQUE)", True, "UNIQUE (kullanici_id, oturum_id, soru_id) işlemi engelledi"))

                # 6. Aynı sorunun oturuma 2 kez eklenmesi (PK)
                try:
                    test_conn.execute("INSERT INTO oturum_sorulari (oturum_id, soru_id, soru_sirasi) VALUES (1, 1, 99);")
                    test_results.append(("6. Aynı Sorunun Oturuma 2 Kez Eklenmesi Engeli (PK)", False, "Kısıtlama tetiklenmedi"))
                except sqlite3.IntegrityError:
                    test_results.append(("6. Aynı Sorunun Oturuma 2 Kez Eklenmesi Engeli (PK)", True, "PRIMARY KEY (oturum_id, soru_id) işlemi engelledi"))

                # 7. Geçersiz e-posta CHECK testi
                try:
                    test_conn.execute("INSERT INTO kullanicilar (kullanici_adi, eposta, ad_soyad) VALUES ('denemeuser', 'hatali-eposta', 'Test Ad');")
                    test_results.append(("7. Geçersiz E-Posta Formatı Engeli (CHECK)", False, "Kısıtlama tetiklenmedi"))
                except sqlite3.IntegrityError:
                    test_results.append(("7. Geçersiz E-Posta Formatı Engeli (CHECK)", True, "CHECK (eposta LIKE '%@%.%') işlemi engelledi"))

                # 8. Negatif süre CHECK testi
                try:
                    test_conn.execute("INSERT INTO oturumlar (baslik, sure_dakika) VALUES ('Test Oturum', -20);")
                    test_results.append(("8. Negatif Süre Engeli (CHECK)", False, "Kısıtlama tetiklenmedi"))
                except sqlite3.IntegrityError:
                    test_results.append(("8. Negatif Süre Engeli (CHECK)", True, "CHECK (sure_dakika > 0) işlemi engelledi"))

                test_conn.rollback()
                test_conn.close()

                passed_all = all(r[1] for r in test_results)
                if passed_all:
                    st.markdown("<div class='alert-box alert-success'>Tüm veri bütünlüğü ve kısıt testleri (8/8) başarıyla doğrulandı. SQLite motoru referansel bütünlüğü korumaktadır.</div>", unsafe_allow_html=True)

                for title, passed, detail in test_results:
                    status_label = "[GECTI]" if passed else "[HATA]"
                    st.markdown(f"<div style='font-size: 13px; padding: 4px 0; color: #1E293B;'><strong>{status_label}</strong> {title} — <span style='color: #64748B;'>{detail}</span></div>", unsafe_allow_html=True)


# =============================================================================
# ÖĞRENCİ (QUIZ ÇÖZÜMÜ) GÖRÜNÜMÜ
# =============================================================================
else:
    categories = ["Tüm Konular"] + get_categories()

    col_filter_cat, col_filter_diff, col_action = st.columns([2, 1, 1])
    with col_filter_cat:
        selected_category = st.selectbox("Konu Filtresi", categories, index=0, key="std_cat_select")
    with col_filter_diff:
        selected_difficulty = st.selectbox("Zorluk", ["Tüm Zorluklar", "Kolay", "Orta", "Zor"], index=0, key="std_diff_select")
    with col_action:
        st.write("")
        st.write("")
        if st.button("Yeni Soru Getir", use_container_width=True):
            st.session_state.quiz_active_id = None
            st.session_state.quiz_submitted = False
            st.session_state.quiz_user_answer = None
            st.rerun()

    df_pool = get_filtered_questions(category_filter=selected_category, difficulty_filter=selected_difficulty)

    if not df_pool:
        st.markdown("<div class='alert-box alert-info'>Belirtilen kriterlere uygun soru bulunamadı. Lütfen filtreleri değiştiriniz.</div>", unsafe_allow_html=True)
    else:
        pool_ids = [r["id"] for r in df_pool]
        if st.session_state.quiz_active_id is None or st.session_state.quiz_active_id not in pool_ids:
            selected_row = random.choice(df_pool)
            st.session_state.quiz_active_id = int(selected_row["id"])
            st.session_state.quiz_submitted = False
            st.session_state.quiz_user_answer = None
        else:
            selected_row = next(r for r in df_pool if r["id"] == st.session_state.quiz_active_id)

        q_id = int(selected_row["id"])
        q_text = str(selected_row["question_text"])
        opt_a = str(selected_row["option_a"])
        opt_b = str(selected_row["option_b"])
        opt_c = str(selected_row["option_c"])
        opt_d = str(selected_row["option_d"])
        correct_opt = str(selected_row["correct_option"])
        q_category = str(selected_row["category"])
        q_difficulty = str(selected_row["difficulty"])

        st.markdown(f"""
        <div class="card">
            <div style="margin-bottom: 10px;">
                <span class="badge badge-blue">Soru ID: {q_id}</span>
                <span class="badge badge-gray">{q_category}</span>
                <span class="badge badge-gray">Zorluk: {q_difficulty}</span>
            </div>
            <div style="font-size: 16px; font-weight: 600; color: #0F172A; line-height: 1.5;">
                {q_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

        options_dict = {
            f"A) {opt_a}": "A",
            f"B) {opt_b}": "B",
            f"C) {opt_c}": "C",
            f"D) {opt_d}": "D"
        }

        user_choice_label = st.radio(
            "Seçeneğinizi işaretleyin:",
            list(options_dict.keys()),
            key=f"radio_q_{q_id}",
            disabled=st.session_state.quiz_submitted
        )
        selected_code = options_dict[user_choice_label]

        col_btn_submit, col_btn_next, _ = st.columns([1.5, 1.5, 3])
        with col_btn_submit:
            if st.button("Cevabı Kontrol Et", disabled=st.session_state.quiz_submitted, use_container_width=True):
                st.session_state.quiz_submitted = True
                st.session_state.quiz_user_answer = selected_code
                st.session_state.quiz_stats["total"] += 1

                if selected_code == correct_opt:
                    st.session_state.quiz_stats["correct"] += 1
                else:
                    st.session_state.quiz_stats["wrong"] += 1
                st.rerun()

        with col_btn_next:
            if st.button("Sonraki Soru", use_container_width=True):
                st.session_state.quiz_active_id = None
                st.session_state.quiz_submitted = False
                st.session_state.quiz_user_answer = None
                st.rerun()

        if st.session_state.quiz_submitted:
            user_ans = st.session_state.quiz_user_answer
            correct_text = {
                "A": f"A) {opt_a}",
                "B": f"B) {opt_b}",
                "C": f"C) {opt_c}",
                "D": f"D) {opt_d}"
            }[correct_opt]

            if user_ans == correct_opt:
                st.markdown(f"""
                <div class="alert-box alert-success">
                    <strong>Doğru Yanıt</strong><br>
                    Tebrikler. İşaretlediğiniz seçenek ({user_ans}) doğrudur.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-box alert-error">
                    <strong>Yanlış Yanıt</strong><br>
                    Seçtiğiniz seçenek: {user_ans}. Doğru seçenek: <strong>{correct_text}</strong>.
                </div>
                """, unsafe_allow_html=True)

    # İstatistikler
    st.write("")
    st.markdown('<div class="card-title">Test İstatistikleri</div>', unsafe_allow_html=True)
    stats = st.session_state.quiz_stats
    total_ans = stats["total"]
    corr = stats["correct"]
    wrg = stats["wrong"]
    rate = (corr / total_ans * 100) if total_ans > 0 else 0.0

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"<div class='metric-container'><div class='metric-label'>Toplam Çözülen</div><div class='metric-val'>{total_ans}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-container'><div class='metric-label'>Doğru Sayısı</div><div class='metric-val' style='color: #166534;'>{corr}</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='metric-container'><div class='metric-label'>Yanlış Sayısı</div><div class='metric-val' style='color: #991B1B;'>{wrg}</div></div>", unsafe_allow_html=True)
    with m4:
        st.markdown(f"<div class='metric-container'><div class='metric-label'>Başarı Oranı</div><div class='metric-val'>%{rate:.1f}</div></div>", unsafe_allow_html=True)
    with m5:
        st.write("")
        if st.button("İstatistikleri Sıfırla", use_container_width=True):
            st.session_state.quiz_stats = {"total": 0, "correct": 0, "wrong": 0}
            st.rerun()
