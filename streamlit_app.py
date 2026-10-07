"""
Quiz Sistemi Veritabanı Yönetimi ve Kullanıcı Arayüzü
Kurumsal ve Minimalist Streamlit Uygulaması
"""

import os
import random
import sqlite3
import pandas as pd
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
# Renk Paleti:
# - Arka Plan: #F8F9FA
# - Metin ve Başlıklar: #0F172A ve #1E293B
# - Vurgu ve Butonlar: #2563EB (Hover: #1D4ED8)
# - Kenarlıklar: #E2E8F0
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

/* Streamlit Varsayılan Başlık Boşluklarını Düzenleme */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

/* Üst Başlık Şeridi */
.app-header {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #E2E8F0;
}

.app-title {
    font-size: 22px;
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
    gap: 12px;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 2px;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    padding: 8px 18px;
    background-color: transparent;
    color: #64748B;
    font-weight: 500;
    font-size: 14px;
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
    padding: 0.45rem 1.1rem;
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

/* İkincil Butonlar */
button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #334155 !important;
    border: 1px solid #CBD5E1 !important;
}

button[kind="secondary"]:hover {
    background-color: #F1F5F9 !important;
    color: #0F172A !important;
}

/* Kurumsal Kart Yapıları */
.card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 20px;
    margin-bottom: 16px;
}

.card-title {
    font-size: 15px;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 12px;
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

/* Radio Seçenekleri Düzenleme */
.stRadio [role="radiogroup"] {
    gap: 8px;
}

.stRadio label {
    font-size: 14px;
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
# VERİ TABANI YÖNETİMİ & TABLO BAŞLATMA
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

    # 1. Questions Tablosu Tanımı
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

    # 2. Eğer questions tablosu boşsa ve veritabanında sorular tablosu varsa aktarım yap
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
# VERİ TABANI YARDIMCI FONKSİYONLARI
# -----------------------------------------------------------------------------
def get_categories():
    """Veritabanında kayıtlı benzersiz kategorileri döndürür."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT DISTINCT category FROM questions ORDER BY category;", conn)
    conn.close()
    return list(df["category"].dropna().values)


def get_filtered_questions(category_filter=None, difficulty_filter=None, search_query=None):
    """Filtrelere göre soruları DataFrame formatında çeker."""
    conn = get_db_connection()
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
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def insert_new_question(text, opt_a, opt_b, opt_c, opt_d, correct, category, difficulty):
    """Yeni soruyu questions tablosuna ekler (ve varsa sorular/secenekler tablosuna da kaydeder)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO questions (question_text, option_a, option_b, option_c, option_d, correct_option, category, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (text.strip(), opt_a.strip(), opt_b.strip(), opt_c.strip(), opt_d.strip(), correct, category.strip(), difficulty))
        
        # Eğer sorular ve secenekler tablosu da mevcutsa veri senkronizasyonu sağla
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
    """Soruyu ID değerine göre veritabanından siler."""
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
# ARAYÜZ ÜST BİLGİ ALANI
# -----------------------------------------------------------------------------
st.markdown("""
<div class="app-header">
    <div class="app-title">Quiz Sistemi Veri Tabanı Yönetimi</div>
    <div class="app-subtitle">İlişkisel Veri Katmanı ve Test Paneli | SQLite3</div>
</div>
""", unsafe_allow_html=True)


# İki Temel Ekran / Sekme
tab_quiz, tab_admin = st.tabs(["Quiz Arayüzü", "Soru Yönetimi"])


# =============================================================================
# 1. SEKME: QUIZ ARAYÜZÜ (KULLANICI)
# =============================================================================
with tab_quiz:
    categories = ["Tüm Konular"] + get_categories()

    # Üst Filtre ve Ayar Çubuğu
    col_filter_cat, col_filter_diff, col_action = st.columns([2, 1, 1])

    with col_filter_cat:
        selected_category = st.selectbox(
            "Konu Filtresi",
            categories,
            index=0,
            key="quiz_cat_select"
        )

    with col_filter_diff:
        selected_difficulty = st.selectbox(
            "Zorluk",
            ["Tüm Zorluklar", "Kolay", "Orta", "Zor"],
            index=0,
            key="quiz_diff_select"
        )

    with col_action:
        st.write("")
        st.write("")
        if st.button("Yeni Soru Getir", use_container_width=True):
            st.session_state.quiz_active_id = None
            st.session_state.quiz_submitted = False
            st.session_state.quiz_user_answer = None
            st.rerun()

    # İlgili kriterlere uyan soruları sorgula
    df_pool = get_filtered_questions(
        category_filter=selected_category,
        difficulty_filter=selected_difficulty
    )

    if df_pool.empty:
        st.markdown("""
        <div class="alert-box alert-info">
            Belirtilen kriterlere uygun soru bulunamadı. Lütfen filtreleri değiştirin veya Soru Yönetimi sekmesinden yeni soru ekleyin.
        </div>
        """, unsafe_allow_html=True)
    else:
        # Aktif soru belirleme
        if st.session_state.quiz_active_id is None or st.session_state.quiz_active_id not in df_pool["id"].values:
            selected_row = df_pool.sample(n=1).iloc[0]
            st.session_state.quiz_active_id = int(selected_row["id"])
            st.session_state.quiz_submitted = False
            st.session_state.quiz_user_answer = None
        else:
            selected_row = df_pool[df_pool["id"] == st.session_state.quiz_active_id].iloc[0]

        q_id = int(selected_row["id"])
        q_text = str(selected_row["question_text"])
        opt_a = str(selected_row["option_a"])
        opt_b = str(selected_row["option_b"])
        opt_c = str(selected_row["option_c"])
        opt_d = str(selected_row["option_d"])
        correct_opt = str(selected_row["correct_option"])
        q_category = str(selected_row["category"])
        q_difficulty = str(selected_row["difficulty"])

        # Soru Kartı
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

        # Seçenekler
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

        # Butonlar
        col_btn_submit, col_btn_next, col_space = st.columns([1.5, 1.5, 3])

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

        # Sonuç Değerlendirme Bildirimi
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

    # Oturum Performans Özeti (Alt Metrik Çubuğu)
    st.write("")
    st.markdown('<div class="card-title">Test İstatistikleri</div>', unsafe_allow_html=True)

    stats = st.session_state.quiz_stats
    total_answered = stats["total"]
    correct_count = stats["correct"]
    wrong_count = stats["wrong"]
    success_rate = (correct_count / total_answered * 100) if total_answered > 0 else 0.0

    m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1])

    with m1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Toplam Çözülen</div>
            <div class="metric-val">{total_answered}</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Doğru Sayısı</div>
            <div class="metric-val" style="color: #166534;">{correct_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Yanlış Sayısı</div>
            <div class="metric-val" style="color: #991B1B;">{wrong_count}</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Başarı Oranı</div>
            <div class="metric-val">%{success_rate:.1f}</div>
        </div>
        """, unsafe_allow_html=True)

    with m5:
        st.write("")
        if st.button("İstatistikleri Sıfırla", use_container_width=True):
            st.session_state.quiz_stats = {"total": 0, "correct": 0, "wrong": 0}
            st.rerun()


# =============================================================================
# 2. SEKME: SORU YÖNETİMİ (ADMIN)
# =============================================================================
with tab_admin:
    st.markdown('<div class="card-title">Yeni Soru Ekleme</div>', unsafe_allow_html=True)

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
                st.markdown("""
                <div class="alert-box alert-error">
                    Lütfen soru metnini ve tüm seçenekleri (A, B, C, D) eksiksiz doldurunuz.
                </div>
                """, unsafe_allow_html=True)
            else:
                success, msg = insert_new_question(
                    new_q_text, new_opt_a, new_opt_b, new_opt_c, new_opt_d,
                    new_correct, new_category, new_difficulty
                )
                if success:
                    st.markdown(f"""
                    <div class="alert-box alert-success">
                        {msg}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="alert-box alert-error">
                        {msg}
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #E2E8F0; margin: 2rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    # Mevcut Soruları Listeleme ve Arama
    st.markdown('<div class="card-title">Mevcut Sorular ve Yönetim</div>', unsafe_allow_html=True)

    col_search, col_f_cat, col_f_diff = st.columns([2, 1, 1])
    with col_search:
        admin_search = st.text_input("Soru Arama", placeholder="Soru metninde geçen anahtar kelime...")
    with col_f_cat:
        admin_cat_filter = st.selectbox("Kategoriye Göre Filtrele", ["Tüm Konular"] + get_categories(), key="admin_cat_filt")
    with col_f_diff:
        admin_diff_filter = st.selectbox("Zorluğa Göre Filtrele", ["Tüm Zorluklar", "Kolay", "Orta", "Zor"], key="admin_diff_filt")

    df_admin_questions = get_filtered_questions(
        category_filter=admin_cat_filter,
        difficulty_filter=admin_diff_filter,
        search_query=admin_search
    )

    st.markdown(f"""
    <div style="font-size: 13px; color: #64748B; margin-bottom: 8px;">
        Kayıtlı Soru Sayısı: <strong>{len(df_admin_questions)}</strong>
    </div>
    """, unsafe_allow_html=True)

    # Tablo Gösterimi
    display_df = df_admin_questions.rename(columns={
        "id": "ID",
        "question_text": "Soru Metni",
        "option_a": "A",
        "option_b": "B",
        "option_c": "C",
        "option_d": "D",
        "correct_option": "Doğru",
        "category": "Kategori",
        "difficulty": "Zorluk",
        "created_at": "Kayıt Tarihi"
    })

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn(width="small"),
            "Soru Metni": st.column_config.TextColumn(width="large"),
            "Doğru": st.column_config.TextColumn(width="small"),
            "Kategori": st.column_config.TextColumn(width="medium"),
            "Zorluk": st.column_config.TextColumn(width="small")
        }
    )

    # Soru Silme Bölümü
    if not df_admin_questions.empty:
        col_del_select, col_del_btn = st.columns([3, 1])
        with col_del_select:
            q_options_list = [f"ID {row['id']}: {row['question_text'][:80]}..." for _, row in df_admin_questions.iterrows()]
            selected_del_label = st.selectbox("Silinecek Soruyu Seçiniz", q_options_list)
            del_id = int(selected_del_label.split(":")[0].replace("ID ", "").strip())

        with col_del_btn:
            st.write("")
            st.write("")
            if st.button("Seçili Soruyu Sil", use_container_width=True):
                del_success, del_msg = delete_question_by_id(del_id)
                if del_success:
                    st.markdown(f"""
                    <div class="alert-box alert-success">
                        {del_msg}
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown(f"""
                    <div class="alert-box alert-error">
                        {del_msg}
                    </div>
                    """, unsafe_allow_html=True)

    # Sistem ve Veri Bütünlüğü Denetimi (Ödev Desteği & Testler)
    with st.expander("Sistem Durumu ve Veri Bütünlüğü Kısıt Denetimi"):
        st.markdown("""
        <div style="font-size: 13px; color: #475569; margin-bottom: 12px;">
            SQLite PRAGMA foreign_keys, Composite Foreign Key, UNIQUE ve CHECK kısıtlamalarını doğrular.
        </div>
        """, unsafe_allow_html=True)

        if st.button("Veri Bütünlüğü Testlerini Çalıştır"):
            test_conn = sqlite3.connect(DB_PATH)
            test_conn.execute("PRAGMA foreign_keys = ON;")

            test_results = []

            # 1. Olmayan kullanıcı FK testi
            try:
                test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 99999, 1, 1, 1);")
                test_results.append(("1. Olmayan Kullanıcıya Cevap Engeli (FK)", False, "Kısıtlama tetiklenmedi"))
            except sqlite3.IntegrityError:
                test_results.append(("1. Olmayan Kullanıcıya Cevap Engeli (FK)", True, "FOREIGN KEY kısıtlaması işlemi reddetti"))

            # 2. Olmayan soru FK testi
            try:
                test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 1, 1, 99999, 1);")
                test_results.append(("2. Olmayan Soruya Cevap Engeli (FK)", False, "Kısıtlama tetiklenmedi"))
            except sqlite3.IntegrityError:
                test_results.append(("2. Olmayan Soruya Cevap Engeli (FK)", True, "FOREIGN KEY kısıtlaması işlemi reddetti"))

            # 3. Oturumda yer almayan soruya cevap (Bileşik FK)
            try:
                test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 1, 1, 90, 1);")
                test_results.append(("3. Oturumda Bulunmayan Soruya Cevap Engeli (Bileşik FK)", False, "Kısıtlama tetiklenmedi"))
            except sqlite3.IntegrityError:
                test_results.append(("3. Oturumda Bulunmayan Soruya Cevap Engeli (Bileşik FK)", True, "Bileşik FOREIGN KEY (oturum_id, soru_id) işlemi reddetti"))

            # 4. Soruya ait olmayan seçenek (Bileşik FK: soru_id, secenek_id)
            try:
                test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 50, 1, 1, 7);")
                test_results.append(("4. Başka Soruya Ait Seçeneğe Cevap Verme Engeli (Bileşik FK)", False, "Kısıtlama tetiklenmedi"))
            except sqlite3.IntegrityError:
                test_results.append(("4. Başka Soruya Ait Seçeneğe Cevap Verme Engeli (Bileşik FK)", True, "Bileşik FOREIGN KEY (soru_id, secenek_id) işlemi reddetti"))

            # 5. Tekrar cevap verme engeli (UNIQUE)
            try:
                test_conn.execute("INSERT INTO cevaplar (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id) VALUES (1, 1, 1, 1, 2);")
                test_results.append(("5. Aynı Soruya Tekrar Cevap Verme Engeli (UNIQUE)", False, "Kısıtlama tetiklenmedi"))
            except sqlite3.IntegrityError:
                test_results.append(("5. Aynı Soruya Tekrar Cevap Verme Engeli (UNIQUE)", True, "UNIQUE (kullanici_id, oturum_id, soru_id) işlemi reddetti"))

            # 6. Aynı sorunun oturuma 2 kez eklenmesi (PK)
            try:
                test_conn.execute("INSERT INTO oturum_sorulari (oturum_id, soru_id, soru_sirasi) VALUES (1, 1, 99);")
                test_results.append(("6. Aynı Sorunun Oturuma 2 Kez Eklenmesi Engeli (PK)", False, "Kısıtlama tetiklenmedi"))
            except sqlite3.IntegrityError:
                test_results.append(("6. Aynı Sorunun Oturuma 2 Kez Eklenmesi Engeli (PK)", True, "PRIMARY KEY (oturum_id, soru_id) işlemi reddetti"))

            # 7. Geçersiz e-posta CHECK testi
            try:
                test_conn.execute("INSERT INTO kullanicilar (kullanici_adi, eposta, ad_soyad) VALUES ('denemeuser', 'hatali-eposta', 'Test Ad');")
                test_results.append(("7. Geçersiz E-Posta Formatı Engeli (CHECK)", False, "Kısıtlama tetiklenmedi"))
            except sqlite3.IntegrityError:
                test_results.append(("7. Geçersiz E-Posta Formatı Engeli (CHECK)", True, "CHECK (eposta LIKE '%@%.%') işlemi reddetti"))

            # 8. Negatif süre CHECK testi
            try:
                test_conn.execute("INSERT INTO oturumlar (baslik, sure_dakika) VALUES ('Test Oturum', -20);")
                test_results.append(("8. Negatif Süre Engeli (CHECK)", False, "Kısıtlama tetiklenmedi"))
            except sqlite3.IntegrityError:
                test_results.append(("8. Negatif Süre Engeli (CHECK)", True, "CHECK (sure_dakika > 0) işlemi reddetti"))

            test_conn.rollback()
            test_conn.close()

            passed_all = all(r[1] for r in test_results)
            if passed_all:
                st.markdown("""
                <div class="alert-box alert-success">
                    Tüm veri bütünlüğü ve kısıt testleri (8/8) başarıyla doğrulandı. SQLite motoru referansel bütünlüğü korumaktadır.
                </div>
                """, unsafe_allow_html=True)

            for title, passed, detail in test_results:
                status_label = "[GECTI]" if passed else "[HATA]"
                st.markdown(f"""
                <div style="font-size: 13px; padding: 4px 0; color: #1E293B;">
                    <strong>{status_label}</strong> {title} — <span style="color: #64748B;">{detail}</span>
                </div>
                """, unsafe_allow_html=True)
