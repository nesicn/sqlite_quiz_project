"""
SQLite Quiz - öğrenci quiz akışı ve hoca oturum paneli.

Kullanım:
    streamlit run streamlit_app.py

Hoca panelini açmak için QUIZ_TEACHER_PASSWORD ortam değişkenini veya
Streamlit secrets içindeki QUIZ_TEACHER_PASSWORD anahtarını ayarlayın.
Öğrenci erişimi, öğretmenin paylaştığı oturum kodu ve görünen ad ile çalışır.
Bu kimlik yöntemi ders demosu içindir; gerçek öğrenci verisiyle kullanılacaksa
kurumsal kimlik doğrulama ile değiştirilmelidir.
"""

from __future__ import annotations

import hmac
import os
import secrets
import sqlite3
import string
from contextlib import contextmanager
from datetime import datetime, timedelta
from html import escape
from typing import Any, Iterator

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="SQLite Quiz | Oturum Yönetimi",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB_PATH = os.environ.get(
    "QUIZ_DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz.db"),
)
TEACHER_PASSWORD_SECRET = "QUIZ_TEACHER_PASSWORD"
WRONG_ANSWER_PENALTY = 2.5
LIVE_REFRESH_SECONDS = 5
STUDENT_REFRESH_SECONDS = 1


CUSTOM_CSS = """
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        "Helvetica Neue", Arial, sans-serif;
    color: #CBD5E1;
}
.stApp { background: #0B1120; color: #CBD5E1; }
.block-container { max-width: 1220px; padding-top: 1.4rem; padding-bottom: 3rem; }
h1, h2, h3, h4, h5, h6 { color: #F8FAFC !important; letter-spacing: -0.02em; }
.hero-banner {
    background: linear-gradient(135deg, #131D31 0%, #1A263D 100%);
    border: 1px solid rgba(148,163,184,.18); border-radius: 12px;
    padding: 20px 24px; margin-bottom: 18px;
    box-shadow: 0 5px 22px rgba(0,0,0,.24);
}
.hero-title { font-size: 22px; font-weight: 750; color: #F8FAFC; margin: 0; }
.hero-subtitle { color: #94A3B8; font-size: 13px; margin-top: 5px; }
.dashboard-card {
    background: #131D31; border: 1px solid rgba(148,163,184,.16);
    border-radius: 10px; padding: 18px 20px; margin: 10px 0 16px;
    box-shadow: 0 4px 16px rgba(0,0,0,.18);
}
.card-heading { color: #F8FAFC; font-weight: 650; font-size: 15px; margin-bottom: 10px; }
.metric-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
    gap: 12px; margin: 10px 0 18px;
}
.stat-box {
    min-height: 82px; box-sizing: border-box;
    background: linear-gradient(145deg, #131D31 0%, #1A263D 100%);
    border: 1px solid rgba(148,163,184,.16); border-radius: 9px; padding: 14px 16px;
}
.stat-label { color: #94A3B8; font-size: 11px; font-weight: 650; letter-spacing: .06em; text-transform: uppercase; }
.stat-value { color: #F8FAFC; font-size: 25px; font-weight: 750; margin-top: 5px; line-height: 1.15; }
.tag-badge {
    display: inline-block; padding: 4px 9px; border-radius: 999px;
    font-size: 11px; font-weight: 700; letter-spacing: .02em;
}
.tag-green { color: #A7F3D0; background: rgba(16,185,129,.16); border: 1px solid rgba(16,185,129,.28); }
.tag-blue { color: #BAE6FD; background: rgba(14,165,233,.15); border: 1px solid rgba(14,165,233,.28); }
.tag-gray { color: #CBD5E1; background: rgba(148,163,184,.12); border: 1px solid rgba(148,163,184,.22); }
.tag-red { color: #FECACA; background: rgba(239,68,68,.14); border: 1px solid rgba(239,68,68,.25); }
.stTabs [data-baseweb="tab-list"] {
    gap: 7px; background: #131D31; padding: 6px 8px; border-radius: 9px;
    border: 1px solid rgba(148,163,184,.16); margin-bottom: 16px;
}
.stTabs [data-baseweb="tab"] { height: 42px; padding: 7px 15px; border-radius: 6px; }
.stTabs [data-baseweb="tab"] p { color: #AAB8CA; font-size: 13px; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1E293B 0%, #2563EB 100%) !important;
    box-shadow: 0 2px 10px rgba(37,99,235,.28);
}
.stButton > button, .stFormSubmitButton > button {
    border-radius: 7px; border: 1px solid rgba(96,165,250,.34);
    background: linear-gradient(135deg, #2563EB, #4F46E5);
    color: white; font-weight: 650; min-height: 40px;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    border-color: #60A5FA; color: white; filter: brightness(1.08);
}
div[data-testid="stDataFrame"] { border: 1px solid rgba(148,163,184,.14); border-radius: 8px; }
div[data-testid="stAlert"] { border-radius: 8px; }
@media (max-width: 700px) {
    .block-container { padding: 1rem .75rem 2rem; }
    .hero-banner { padding: 16px; }
    .hero-title { font-size: 19px; }
    .dashboard-card { padding: 14px; }
    .metric-grid { grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap: 8px; }
    .stat-value { font-size: 22px; }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
    """Açık bağlantıda FK denetimini ve yazma çakışmaları için beklemeyi aç."""
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 15000;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ensure_runtime_schema() -> None:
    """Davet kodları için geriye uyumlu, ek bir tablo oluştur."""
    if not os.path.isfile(DB_PATH):
        raise FileNotFoundError(
            "quiz.db bulunamadı. Önce proje klasöründe python seed.py çalıştırın."
        )
    with db_connection() as conn:
        required = {
            "kullanicilar",
            "oturumlar",
            "sorular",
            "secenekler",
            "oturum_sorulari",
            "katilimlar",
            "cevaplar",
        }
        present = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table';"
            )
        }
        missing = sorted(required - present)
        if missing:
            raise RuntimeError(
                "Veritabanında beklenen tablolar eksik: " + ", ".join(missing)
            )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS oturum_erisimleri (
                oturum_id INTEGER PRIMARY KEY,
                katilim_kodu TEXT NOT NULL UNIQUE,
                FOREIGN KEY (oturum_id)
                    REFERENCES oturumlar(oturum_id) ON DELETE CASCADE
            );
            """
        )
        active_sessions = conn.execute(
            "SELECT oturum_id FROM oturumlar WHERE durum = 'devam_ediyor';"
        ).fetchall()
        for row in active_sessions:
            ensure_join_code(conn, int(row["oturum_id"]))


def ensure_join_code(
    conn: sqlite3.Connection, session_id: int
) -> str:
    row = conn.execute(
        "SELECT katilim_kodu FROM oturum_erisimleri WHERE oturum_id = ?;",
        (session_id,),
    ).fetchone()
    if row:
        return str(row["katilim_kodu"])

    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    for _ in range(10):
        code = "".join(secrets.choice(alphabet) for _ in range(7))
        try:
            conn.execute(
                "INSERT INTO oturum_erisimleri (oturum_id, katilim_kodu) VALUES (?, ?);",
                (session_id, code),
            )
            return code
        except sqlite3.IntegrityError:
            continue
    raise RuntimeError("Benzersiz oturum kodu üretilemedi.")


def rows(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with db_connection() as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def get_sessions() -> list[dict[str, Any]]:
    return rows(
        """
        SELECT o.oturum_id, o.baslik, o.aciklama, o.durum,
               o.baslangic_zaman, o.bitis_zaman, o.sure_dakika, o.gecme_notu,
               COUNT(DISTINCT os.soru_id) AS soru_sayisi,
               COUNT(DISTINCT k.katilim_id) AS katilimci_sayisi,
               COUNT(DISTINCT c.cevap_id) AS cevap_sayisi,
               e.katilim_kodu
        FROM oturumlar o
        LEFT JOIN oturum_sorulari os ON os.oturum_id = o.oturum_id
        LEFT JOIN katilimlar k ON k.oturum_id = o.oturum_id
        LEFT JOIN cevaplar c ON c.katilim_id = k.katilim_id
                             AND c.soru_id = os.soru_id
        LEFT JOIN oturum_erisimleri e ON e.oturum_id = o.oturum_id
        GROUP BY o.oturum_id
        ORDER BY o.oturum_id DESC;
        """
    )


def get_question_bank() -> list[dict[str, Any]]:
    return rows(
        """
        SELECT s.soru_id, s.soru_metni, s.kategori, s.zorluk_seviyesi,
               s.puan_degeri, COUNT(DISTINCT sec.secenek_id) AS secenek_sayisi,
               COUNT(DISTINCT os.oturum_id) AS oturum_sayisi
        FROM sorular s
        LEFT JOIN secenekler sec ON sec.soru_id = s.soru_id
        LEFT JOIN oturum_sorulari os ON os.soru_id = s.soru_id
        GROUP BY s.soru_id
        ORDER BY s.soru_id DESC;
        """
    )


def create_session(
    title: str,
    description: str,
    duration_minutes: int,
    pass_score: float,
    question_ids: list[int],
) -> tuple[int, str]:
    if len(title.strip()) < 3:
        raise ValueError("Oturum başlığı en az 3 karakter olmalı.")
    if not question_ids:
        raise ValueError("Oturuma en az bir soru atayın.")
    if duration_minutes < 1:
        raise ValueError("Sınav süresi en az 1 dakika olmalı.")
    if not 0 <= pass_score <= 100:
        raise ValueError("Geçme puanı 0 ile 100 arasında olmalı.")

    with db_connection() as conn:
        existing = {
            int(row["soru_id"])
            for row in conn.execute(
                "SELECT soru_id FROM sorular WHERE soru_id IN ({})".format(
                    ",".join("?" for _ in question_ids)
                ),
                tuple(question_ids),
            ).fetchall()
        }
        if existing != set(question_ids):
            raise ValueError("Seçilen sorulardan bazıları soru bankasında bulunamadı.")

        cursor = conn.execute(
            """
            INSERT INTO oturumlar
                (baslik, aciklama, durum, sure_dakika, gecme_notu)
            VALUES (?, ?, 'planlandi', ?, ?);
            """,
            (title.strip(), description.strip(), duration_minutes, pass_score),
        )
        session_id = int(cursor.lastrowid)
        conn.executemany(
            """
            INSERT INTO oturum_sorulari (oturum_id, soru_id, soru_sirasi)
            VALUES (?, ?, ?);
            """,
            [
                (session_id, question_id, order)
                for order, question_id in enumerate(question_ids, start=1)
            ],
        )
        code = ensure_join_code(conn, session_id)
    return session_id, code


def change_session_status(session_id: int, new_status: str) -> None:
    with db_connection() as conn:
        session = conn.execute(
            "SELECT durum FROM oturumlar WHERE oturum_id = ?;", (session_id,)
        ).fetchone()
        if not session:
            raise ValueError("Oturum bulunamadı.")

        current = str(session["durum"])
        if new_status == "devam_ediyor":
            if current != "planlandi":
                raise ValueError("Yalnızca planlanmış oturum başlatılabilir.")
            question_count = conn.execute(
                "SELECT COUNT(*) FROM oturum_sorulari WHERE oturum_id = ?;",
                (session_id,),
            ).fetchone()[0]
            if question_count == 0:
                raise ValueError("Başlatmadan önce oturuma soru atayın.")
            ensure_join_code(conn, session_id)
            conn.execute(
                """
                UPDATE oturumlar
                SET durum = 'devam_ediyor',
                    baslangic_zaman = datetime('now', 'localtime'),
                    bitis_zaman = NULL
                WHERE oturum_id = ?;
                """,
                (session_id,),
            )
        elif new_status == "tamamlandi":
            if current != "devam_ediyor":
                raise ValueError("Yalnızca devam eden oturum kapatılabilir.")
            conn.execute(
                """
                UPDATE oturumlar
                SET durum = 'tamamlandi',
                    bitis_zaman = datetime('now', 'localtime')
                WHERE oturum_id = ?;
                """,
                (session_id,),
            )
            conn.execute(
                """
                UPDATE katilimlar
                SET tamamlandi_mi = 1,
                    tamamlama_zaman = COALESCE(
                        tamamlama_zaman, datetime('now', 'localtime')
                    )
                WHERE oturum_id = ? AND tamamlandi_mi = 0;
                """,
                (session_id,),
            )
        else:
            raise ValueError("Desteklenmeyen oturum durumu.")


def add_question(
    question_text: str,
    options: list[str],
    correct_label: str,
    category: str,
    difficulty: str,
    points: float,
) -> int:
    if len(question_text.strip()) == 0:
        raise ValueError("Soru metni boş olamaz.")
    if len(options) < 2 or any(not option.strip() for option in options):
        raise ValueError("En az iki dolu seçenek girin.")
    if points <= 0:
        raise ValueError("Soru puanı sıfırdan büyük olmalı.")
    if correct_label not in string.ascii_uppercase[: len(options)]:
        raise ValueError("Doğru seçenek, girilen seçeneklerden biri olmalı.")

    difficulty_value = {
        "Kolay": "kolay",
        "Orta": "orta",
        "Zor": "zor",
    }[difficulty]
    with db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sorular
                (soru_metni, kategori, zorluk_seviyesi, puan_degeri)
            VALUES (?, ?, ?, ?);
            """,
            (
                question_text.strip(),
                category.strip() or "Genel",
                difficulty_value,
                points,
            ),
        )
        question_id = int(cursor.lastrowid)
        conn.executemany(
            """
            INSERT INTO secenekler
                (soru_id, secenek_etiketi, secenek_metni, dogru_mu)
            VALUES (?, ?, ?, ?);
            """,
            [
                (
                    question_id,
                    string.ascii_uppercase[index],
                    option.strip(),
                    int(string.ascii_uppercase[index] == correct_label),
                )
                for index, option in enumerate(options)
            ],
        )
    return question_id


def delete_unassigned_question(question_id: int) -> None:
    with db_connection() as conn:
        assigned = conn.execute(
            "SELECT 1 FROM oturum_sorulari WHERE soru_id = ? LIMIT 1;",
            (question_id,),
        ).fetchone()
        if assigned:
            raise ValueError(
                "Bu soru oturumlarda kullanılıyor; geçmiş kayıtları korumak için silinmedi."
            )
        conn.execute("DELETE FROM sorular WHERE soru_id = ?;", (question_id,))


def create_guest_participation(
    join_code: str, display_name: str
) -> tuple[int, int, str]:
    clean_name = " ".join(display_name.split())
    if len(clean_name) < 2:
        raise ValueError("Görünen ad en az 2 karakter olmalı.")
    normalized_code = "".join(join_code.upper().split())
    if not normalized_code:
        raise ValueError("Oturum kodunu girin.")

    with db_connection() as conn:
        session = conn.execute(
            """
            SELECT o.oturum_id, o.baslik, o.durum
            FROM oturum_erisimleri e
            JOIN oturumlar o ON o.oturum_id = e.oturum_id
            WHERE e.katilim_kodu = ?;
            """,
            (normalized_code,),
        ).fetchone()
        if not session:
            raise ValueError("Bu kodla eşleşen bir oturum bulunamadı.")
        if session["durum"] != "devam_ediyor":
            raise ValueError("Bu oturum şu anda katılıma açık değil.")

        token = secrets.token_hex(6)
        cursor = conn.execute(
            """
            INSERT INTO kullanicilar (kullanici_adi, eposta, ad_soyad, durum)
            VALUES (?, ?, ?, 'aktif');
            """,
            (f"guest_{token}", f"guest_{token}@demo.local", clean_name),
        )
        user_id = int(cursor.lastrowid)
        cursor = conn.execute(
            """
            INSERT INTO katilimlar (kullanici_id, oturum_id)
            VALUES (?, ?);
            """,
            (user_id, int(session["oturum_id"])),
        )
        participation_id = int(cursor.lastrowid)
    return user_id, participation_id, str(session["baslik"])


def get_student_attempt(
    user_id: int, session_id: int
) -> dict[str, Any] | None:
    with db_connection() as conn:
        attempt = conn.execute(
            """
            SELECT k.katilim_id, k.kullanici_id, k.oturum_id,
                   k.katilim_zaman, k.tamamlandi_mi, k.tamamlama_zaman,
                   u.ad_soyad, o.baslik, o.durum AS oturum_durumu,
                   o.sure_dakika, o.gecme_notu
            FROM katilimlar k
            JOIN kullanicilar u ON u.kullanici_id = k.kullanici_id
            JOIN oturumlar o ON o.oturum_id = k.oturum_id
            WHERE k.kullanici_id = ? AND k.oturum_id = ?;
            """,
            (user_id, session_id),
        ).fetchone()
        if not attempt:
            return None

        questions = conn.execute(
            """
            SELECT os.soru_id, os.soru_sirasi, s.soru_metni, s.kategori,
                   s.zorluk_seviyesi, s.puan_degeri,
                   c.cevap_id, c.secenek_id AS verilen_secenek_id,
                   sec.dogru_mu AS verilen_cevap_dogru
            FROM oturum_sorulari os
            JOIN sorular s ON s.soru_id = os.soru_id
            LEFT JOIN cevaplar c
                ON c.katilim_id = ? AND c.soru_id = os.soru_id
            LEFT JOIN secenekler sec ON sec.secenek_id = c.secenek_id
            WHERE os.oturum_id = ?
            ORDER BY os.soru_sirasi;
            """,
            (int(attempt["katilim_id"]), session_id),
        ).fetchall()
        options: dict[int, list[dict[str, Any]]] = {}
        for question in questions:
            options[int(question["soru_id"])] = [
                dict(option)
                for option in conn.execute(
                    """
                    SELECT secenek_id, secenek_etiketi, secenek_metni
                    FROM secenekler
                    WHERE soru_id = ?
                    ORDER BY secenek_etiketi;
                    """,
                    (int(question["soru_id"]),),
                ).fetchall()
            ]
    result = dict(attempt)
    result["questions"] = [dict(question) for question in questions]
    result["options"] = options
    return result


def finish_participation(participation_id: int) -> None:
    with db_connection() as conn:
        conn.execute(
            """
            UPDATE katilimlar
            SET tamamlandi_mi = 1,
                tamamlama_zaman = COALESCE(
                    tamamlama_zaman, datetime('now', 'localtime')
                )
            WHERE katilim_id = ?;
            """,
            (participation_id,),
        )


def save_student_answer(
    attempt: dict[str, Any], question_id: int, option_id: int
) -> bool:
    with db_connection() as conn:
        session = conn.execute(
            "SELECT durum FROM oturumlar WHERE oturum_id = ?;",
            (attempt["oturum_id"],),
        ).fetchone()
        if not session or session["durum"] != "devam_ediyor":
            raise ValueError("Öğretmen bu oturumu kapattı; cevap kaydedilmedi.")
        if attempt["tamamlama_zaman"] or int(attempt["tamamlandi_mi"]):
            raise ValueError("Bu sınav denemesi tamamlanmış.")
        assigned = conn.execute(
            """
            SELECT 1 FROM oturum_sorulari
            WHERE oturum_id = ? AND soru_id = ?;
            """,
            (attempt["oturum_id"], question_id),
        ).fetchone()
        if not assigned:
            raise ValueError("Bu soru seçili oturuma ait değil.")
        option = conn.execute(
            """
            SELECT 1 FROM secenekler
            WHERE secenek_id = ? AND soru_id = ?;
            """,
            (option_id, question_id),
        ).fetchone()
        if not option:
            raise ValueError("Seçilen seçenek bu soruya ait değil.")

        joined_at = datetime.fromisoformat(str(attempt["katilim_zaman"]))
        deadline = joined_at + timedelta(minutes=int(attempt["sure_dakika"]))
        if datetime.now() >= deadline:
            conn.execute(
                """
                UPDATE katilimlar
                SET tamamlandi_mi = 1,
                    tamamlama_zaman = COALESCE(
                        tamamlama_zaman, datetime('now', 'localtime')
                    )
                WHERE katilim_id = ?;
                """,
                (attempt["katilim_id"],),
            )
            return False

        conn.execute(
            """
            INSERT INTO cevaplar
                (katilim_id, kullanici_id, oturum_id, soru_id, secenek_id)
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                attempt["katilim_id"],
                attempt["kullanici_id"],
                attempt["oturum_id"],
                question_id,
                option_id,
            ),
        )
        answered = conn.execute(
            "SELECT COUNT(*) FROM cevaplar WHERE katilim_id = ?;",
            (attempt["katilim_id"],),
        ).fetchone()[0]
        total = conn.execute(
            "SELECT COUNT(*) FROM oturum_sorulari WHERE oturum_id = ?;",
            (attempt["oturum_id"],),
        ).fetchone()[0]
        if total > 0 and answered >= total:
            conn.execute(
                """
                UPDATE katilimlar
                SET tamamlandi_mi = 1,
                    tamamlama_zaman = datetime('now', 'localtime')
                WHERE katilim_id = ?;
                """,
                (attempt["katilim_id"],),
            )
    return True


def get_attempt_result(user_id: int, session_id: int) -> dict[str, Any] | None:
    result_rows = rows(
        """
        SELECT k.katilim_id, k.tamamlandi_mi, k.tamamlama_zaman,
               o.baslik, o.durum AS oturum_durumu, o.gecme_notu,
               COUNT(DISTINCT os.soru_id) AS toplam_soru,
               COUNT(DISTINCT c.cevap_id) AS cevaplanan,
               COUNT(DISTINCT CASE
                   WHEN sec.dogru_mu = 1 THEN c.cevap_id END) AS dogru,
               COUNT(DISTINCT CASE
                   WHEN c.secenek_id IS NOT NULL AND sec.dogru_mu = 0
                   THEN c.cevap_id END) AS yanlis,
               COALESCE(SUM(CASE
                   WHEN c.cevap_id IS NULL THEN 0
                   WHEN sec.dogru_mu = 1 THEN s.puan_degeri
                   ELSE -2.5
               END), 0) AS puan
        FROM katilimlar k
        JOIN oturumlar o ON o.oturum_id = k.oturum_id
        LEFT JOIN oturum_sorulari os ON os.oturum_id = o.oturum_id
        LEFT JOIN sorular s ON s.soru_id = os.soru_id
        LEFT JOIN cevaplar c
            ON c.katilim_id = k.katilim_id AND c.soru_id = os.soru_id
        LEFT JOIN secenekler sec ON sec.secenek_id = c.secenek_id
        WHERE k.kullanici_id = ? AND k.oturum_id = ?
        GROUP BY k.katilim_id;
        """,
        (user_id, session_id),
    )
    return result_rows[0] if result_rows else None


def get_teacher_results() -> list[dict[str, Any]]:
    return rows(
        """
        SELECT k.katilim_id, k.oturum_id, o.baslik AS oturum,
               u.kullanici_id, u.ad_soyad, u.eposta,
               COUNT(DISTINCT os.soru_id) AS soru,
               COUNT(DISTINCT c.cevap_id) AS cevaplanan,
               COUNT(DISTINCT CASE
                   WHEN sec.dogru_mu = 1 THEN c.cevap_id END) AS dogru,
               COUNT(DISTINCT CASE
                   WHEN c.secenek_id IS NOT NULL AND sec.dogru_mu = 0
                   THEN c.cevap_id END) AS yanlis,
               MAX(0, COUNT(DISTINCT os.soru_id)
                       - COUNT(DISTINCT c.cevap_id)) AS bos,
               ROUND(COALESCE(SUM(CASE
                   WHEN c.cevap_id IS NULL THEN 0
                   WHEN sec.dogru_mu = 1 THEN s.puan_degeri
                   ELSE -2.5
               END), 0), 2) AS puan,
               CASE WHEN COALESCE(SUM(CASE
                   WHEN c.cevap_id IS NULL THEN 0
                   WHEN sec.dogru_mu = 1 THEN s.puan_degeri
                   ELSE -2.5
               END), 0) >= o.gecme_notu
               THEN 'BAŞARILI' ELSE 'BAŞARISIZ' END AS sonuc
        FROM katilimlar k
        JOIN oturumlar o ON o.oturum_id = k.oturum_id
        JOIN kullanicilar u ON u.kullanici_id = k.kullanici_id
        LEFT JOIN oturum_sorulari os ON os.oturum_id = o.oturum_id
        LEFT JOIN sorular s ON s.soru_id = os.soru_id
        LEFT JOIN cevaplar c
            ON c.katilim_id = k.katilim_id AND c.soru_id = os.soru_id
        LEFT JOIN secenekler sec ON sec.secenek_id = c.secenek_id
        WHERE k.tamamlandi_mi = 1
        GROUP BY k.katilim_id
        ORDER BY o.oturum_id DESC, puan DESC;
        """
    )


def get_live_progress() -> list[dict[str, Any]]:
    return rows(
        """
        SELECT o.baslik AS oturum, u.ad_soyad,
               COUNT(DISTINCT os.soru_id) AS toplam_soru,
               COUNT(DISTINCT c.cevap_id) AS yanitlanan,
               MAX(0, COUNT(DISTINCT os.soru_id)
                       - COUNT(DISTINCT c.cevap_id)) AS kalan,
               ROUND(CASE WHEN COUNT(DISTINCT os.soru_id) = 0 THEN 0
                   ELSE 100.0 * COUNT(DISTINCT c.cevap_id)
                       / COUNT(DISTINCT os.soru_id) END, 1) AS ilerleme
        FROM katilimlar k
        JOIN oturumlar o ON o.oturum_id = k.oturum_id
        JOIN kullanicilar u ON u.kullanici_id = k.kullanici_id
        LEFT JOIN oturum_sorulari os ON os.oturum_id = o.oturum_id
        LEFT JOIN cevaplar c
            ON c.katilim_id = k.katilim_id AND c.soru_id = os.soru_id
        WHERE o.durum = 'devam_ediyor'
        GROUP BY k.katilim_id
        ORDER BY ilerleme DESC, u.ad_soyad;
        """
    )


def get_hard_questions() -> list[dict[str, Any]]:
    return rows(
        """
        SELECT s.soru_id, s.soru_metni, s.kategori,
               COUNT(c.cevap_id) AS yanit_sayisi,
               SUM(CASE WHEN sec.dogru_mu = 1 THEN 1 ELSE 0 END) AS dogru,
               SUM(CASE WHEN sec.dogru_mu = 0 THEN 1 ELSE 0 END) AS yanlis,
               ROUND(100.0 * SUM(CASE WHEN sec.dogru_mu = 0 THEN 1 ELSE 0 END)
                     / NULLIF(COUNT(c.cevap_id), 0), 1) AS hata_orani
        FROM sorular s
        JOIN cevaplar c ON c.soru_id = s.soru_id
        JOIN secenekler sec ON sec.secenek_id = c.secenek_id
        GROUP BY s.soru_id
        HAVING COUNT(c.cevap_id) > 0
        ORDER BY hata_orani DESC, yanit_sayisi DESC
        LIMIT 10;
        """
    )


def get_teacher_password() -> str | None:
    value = os.environ.get(TEACHER_PASSWORD_SECRET)
    if value:
        return value
    try:
        value = st.secrets.get(TEACHER_PASSWORD_SECRET)
    except Exception:
        value = None
    return str(value) if value else None


def render_metric_cards(metrics: list[tuple[str, Any]]) -> None:
    cards = []
    for label, value in metrics:
        cards.append(
            "<div class='stat-box'>"
            f"<div class='stat-label'>{escape(str(label))}</div>"
            f"<div class='stat-value'>{escape(str(value))}</div>"
            "</div>"
        )
    st.markdown(
        "<div class='metric-grid'>" + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    label, css = {
        "planlandi": ("PLANLANDI", "tag-gray"),
        "devam_ediyor": ("DEVAM EDİYOR", "tag-blue"),
        "tamamlandi": ("TAMAMLANDI", "tag-green"),
        "iptal": ("İPTAL", "tag-red"),
    }.get(status, (status.upper(), "tag-gray"))
    return f"<span class='tag-badge {css}'>{escape(label)}</span>"


def render_header() -> str:
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">Quiz Sistemi Veri Tabanı Yönetim Paneli</div>
            <div class="hero-subtitle">
                Oturum yönetimi, kalıcı cevap kaydı ve SQLite canlı takibi
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return st.selectbox(
        "Görünüm",
        ["Öğrenci / Katılımcı", "Hoca Paneli"],
        key="app_view",
        help="Hoca görünümü parolayla korunur. Öğrenci görünümü oturum koduyla çalışır.",
    )


def teacher_login() -> bool:
    expected_password = get_teacher_password()
    if not expected_password:
        st.warning(
            "Hoca paneli kilitli. Güvenli erişim için Streamlit secrets veya "
            "ortam değişkeninde QUIZ_TEACHER_PASSWORD tanımlayın."
        )
        st.code(
            '[secrets.toml]\nQUIZ_TEACHER_PASSWORD = "uzun-ve-tahmin-edilemez-bir-parola"',
            language="toml",
        )
        return False

    if st.session_state.get("teacher_authenticated", False):
        left, right = st.columns([5, 1])
        with left:
            st.caption("Hoca paneli açık")
        with right:
            if st.button("Oturumu Kapat", key="teacher_logout"):
                st.session_state.teacher_authenticated = False
                st.rerun()
        return True

    with st.form("teacher_login_form"):
        password = st.text_input("Hoca paneli parolası", type="password")
        submitted = st.form_submit_button("Hoca Paneline Gir", use_container_width=True)
    if submitted:
        if hmac.compare_digest(password, expected_password):
            st.session_state.teacher_authenticated = True
            st.rerun()
        else:
            st.error("Parola doğru değil.")
    return False


def render_teacher_overview() -> None:
    sessions = get_sessions()
    results = get_teacher_results()
    active_count = sum(row["durum"] == "devam_ediyor" for row in sessions)
    total_participants = sum(int(row["katilimci_sayisi"]) for row in sessions)
    average = (
        sum(float(row["puan"]) for row in results) / len(results)
        if results
        else 0.0
    )
    render_metric_cards(
        [
            ("Oturum Sayısı", len(sessions)),
            ("Devam Eden Oturum", active_count),
            ("Toplam Katılım", total_participants),
            ("Tamamlanan Deneme Ortalaması", f"{average:.1f}"),
        ]
    )
    st.markdown(
        "<div class='dashboard-card'><div class='card-heading'>"
        "Öğrenci Sonuçları</div></div>",
        unsafe_allow_html=True,
    )
    session_choices = {"Tüm oturumlar": None}
    session_choices.update(
        {f"{row['oturum_id']} · {row['baslik']}": row["oturum_id"] for row in sessions}
    )
    c1, c2 = st.columns([2, 1])
    with c1:
        chosen_label = st.selectbox(
            "Oturum filtresi", list(session_choices), key="results_session_filter"
        )
    with c2:
        status_filter = st.selectbox(
            "Sonuç filtresi",
            ["Tümü", "BAŞARILI", "BAŞARISIZ"],
            key="results_status_filter",
        )
    filtered = results
    selected_session_id = session_choices[chosen_label]
    if selected_session_id is not None:
        filtered = [r for r in filtered if r["oturum_id"] == selected_session_id]
    if status_filter != "Tümü":
        filtered = [r for r in filtered if r["sonuc"] == status_filter]

    if filtered:
        frame = pd.DataFrame(filtered)
        frame = frame.rename(
            columns={
                "ad_soyad": "Öğrenci",
                "oturum": "Oturum",
                "soru": "Soru",
                "cevaplanan": "Cevaplanan",
                "dogru": "Doğru",
                "yanlis": "Yanlış",
                "bos": "Boş",
                "puan": "Puan",
                "sonuc": "Sonuç",
            }
        )
        visible_columns = [
            "Öğrenci", "Oturum", "Soru", "Cevaplanan",
            "Doğru", "Yanlış", "Boş", "Puan", "Sonuç",
        ]
        st.dataframe(
            frame[visible_columns],
            use_container_width=True,
            hide_index=True,
            column_config={"Puan": st.column_config.NumberColumn(format="%.2f")},
        )
    else:
        st.info("Bu filtrelere göre tamamlanmış sınav sonucu bulunmuyor.")


def render_live_monitor() -> None:
    sessions = get_sessions()
    active_sessions = [row for row in sessions if row["durum"] == "devam_ediyor"]
    st.markdown(
        "<div class='card-heading'>Oturum İlerleme ve Canlı Takip</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        f"Son veritabanı okuması: {datetime.now().strftime('%H:%M:%S')} · "
        f"{LIVE_REFRESH_SECONDS} saniyede bir yenilenir"
    )
    if not active_sessions:
        st.info("Şu anda devam eden oturum yok. Oturumlar sekmesinden bir sınav başlatın.")
    for session in active_sessions:
        total = int(session["soru_sayisi"])
        answers = int(session["cevap_sayisi"])
        possible = int(session["katilimci_sayisi"]) * total
        progress = min(1.0, answers / possible) if possible else 0.0
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(
                    f"**{session['baslik']}**  {status_badge(session['durum'])}",
                    unsafe_allow_html=True,
                )
            with right:
                st.caption(
                    f"{session['sure_dakika']} dk · geçme puanı "
                    f"{session['gecme_notu']}"
                )
            render_metric_cards(
                [
                    ("Katılımcı", session["katilimci_sayisi"]),
                    ("Soru", total),
                    ("Kaydedilen Cevap", answers),
                    ("Genel İlerleme", f"%{progress * 100:.1f}"),
                ]
            )
            st.progress(progress)

    active_rows = get_live_progress()
    if active_rows:
        st.markdown("#### Katılımcı ilerlemesi")
        frame = pd.DataFrame(active_rows).rename(
            columns={
                "oturum": "Oturum",
                "ad_soyad": "Katılımcı",
                "toplam_soru": "Soru",
                "yanitlanan": "Yanıtlanan",
                "kalan": "Kalan",
                "ilerleme": "İlerleme (%)",
            }
        )
        st.dataframe(
            frame[["Oturum", "Katılımcı", "Soru", "Yanıtlanan", "Kalan", "İlerleme (%)"]],
            use_container_width=True,
            hide_index=True,
        )


def render_session_management() -> None:
    st.markdown("### Oturumlar")
    questions = get_question_bank()
    if not questions:
        st.warning("Önce Soru Bankası sekmesinden soru ekleyin.")
    else:
        question_labels = {
            f"{row['soru_id']} · {row['soru_metni'][:95]}": int(row["soru_id"])
            for row in questions
        }
        with st.form("create_session_form"):
            st.markdown("#### Yeni sınav oturumu")
            title = st.text_input("Oturum başlığı")
            description = st.text_area("Açıklama", height=70)
            c1, c2 = st.columns(2)
            with c1:
                duration = st.number_input(
                    "Sınav süresi (dakika)", min_value=1, max_value=360, value=30
                )
            with c2:
                pass_score = st.number_input(
                    "Geçme puanı", min_value=0.0, max_value=100.0, value=50.0, step=5.0
                )
            selected_labels = st.multiselect(
                "Oturuma atanacak sorular",
                list(question_labels),
                help="Soru sırası seçtiğiniz sıraya göre kaydedilir.",
            )
            create_clicked = st.form_submit_button(
                "Oturumu Oluştur", use_container_width=True
            )
        if create_clicked:
            try:
                question_ids = [question_labels[label] for label in selected_labels]
                session_id, join_code = create_session(
                    title, description, int(duration), float(pass_score), question_ids
                )
                st.success(f"Oturum {session_id} oluşturuldu ve planlandı.")
                st.markdown("Öğrenciler sınav başlatıldıktan sonra bu kodla katılabilir:")
                st.code(join_code)
            except (ValueError, sqlite3.Error, RuntimeError) as exc:
                st.error(str(exc))

    st.markdown("---")
    st.markdown("#### Oturum durumu")
    sessions = get_sessions()
    if not sessions:
        st.info("Henüz oturum bulunmuyor.")
        return

    for session in sessions:
        with st.container(border=True):
            top, action = st.columns([4, 1.25])
            with top:
                st.markdown(
                    f"**{session['baslik']}**  {status_badge(session['durum'])}",
                    unsafe_allow_html=True,
                )
                st.caption(
                    f"{session['soru_sayisi']} soru · {session['sure_dakika']} dk · "
                    f"geçme puanı {session['gecme_notu']} · "
                    f"{session['katilimci_sayisi']} katılımcı · "
                    f"{session['cevap_sayisi']} kayıtlı cevap"
                )
                if session["baslangic_zaman"]:
                    st.caption(
                        f"Başlangıç: {session['baslangic_zaman']} · "
                        f"Bitiş: {session['bitis_zaman'] or 'devam ediyor'}"
                    )
                if session["durum"] in ("planlandi", "devam_ediyor"):
                    st.caption("Katılım kodu")
                    st.code(session["katilim_kodu"] or "Kod oluşturulamadı")
            with action:
                if session["durum"] == "planlandi":
                    if st.button(
                        "Sınavı Başlat",
                        key=f"start_{session['oturum_id']}",
                        disabled=int(session["soru_sayisi"]) == 0,
                        use_container_width=True,
                    ):
                        try:
                            change_session_status(
                                int(session["oturum_id"]), "devam_ediyor"
                            )
                            st.success("Sınav başlatıldı.")
                            st.rerun()
                        except (ValueError, sqlite3.Error, RuntimeError) as exc:
                            st.error(str(exc))
                elif session["durum"] == "devam_ediyor":
                    if st.button(
                        "Sınavı Kapat",
                        key=f"close_{session['oturum_id']}",
                        use_container_width=True,
                    ):
                        try:
                            change_session_status(
                                int(session["oturum_id"]), "tamamlandi"
                            )
                            st.success(
                                "Sınav kapatıldı. Eksik denemeler de tamamlandı olarak işaretlendi."
                            )
                            st.rerun()
                        except (ValueError, sqlite3.Error) as exc:
                            st.error(str(exc))


def render_analytics() -> None:
    st.markdown("### En çok yanlış yapılan sorular")
    questions = get_hard_questions()
    if not questions:
        st.info("Analiz için henüz cevap kaydı bulunmuyor.")
        return
    frame = pd.DataFrame(questions).rename(
        columns={
            "soru_id": "Soru ID",
            "soru_metni": "Soru",
            "kategori": "Kategori",
            "yanit_sayisi": "Yanıt",
            "dogru": "Doğru",
            "yanlis": "Yanlış",
            "hata_orani": "Hata oranı (%)",
        }
    )
    st.dataframe(frame, use_container_width=True, hide_index=True)


def render_question_bank() -> None:
    st.markdown("### Soru Bankası")
    with st.form("add_question_form", clear_on_submit=True):
        text = st.text_area("Soru metni")
        category = st.text_input("Konu", value="SQL Temelleri")
        difficulty = st.selectbox("Zorluk", ["Kolay", "Orta", "Zor"], index=1)
        points = st.number_input(
            "Doğru cevap puanı", min_value=0.5, max_value=100.0, value=10.0, step=0.5
        )
        option_count = st.selectbox("Seçenek sayısı", [2, 3, 4], index=2)
        options = [
            st.text_input(f"Seçenek {string.ascii_uppercase[i]}", key=f"new_option_{i}")
            for i in range(int(option_count))
        ]
        correct = st.selectbox(
            "Doğru seçenek", list(string.ascii_uppercase[: int(option_count)])
        )
        submitted = st.form_submit_button("Soruyu Kaydet", use_container_width=True)
    if submitted:
        try:
            question_id = add_question(
                text, options, correct, category, difficulty, float(points)
            )
            st.success(f"Soru {question_id} kaydedildi.")
        except (ValueError, sqlite3.Error) as exc:
            st.error(str(exc))

    questions = get_question_bank()
    st.markdown("#### Kayıtlı sorular")
    if questions:
        frame = pd.DataFrame(questions).rename(
            columns={
                "soru_id": "ID",
                "soru_metni": "Soru",
                "kategori": "Konu",
                "zorluk_seviyesi": "Zorluk",
                "puan_degeri": "Puan",
                "secenek_sayisi": "Seçenek",
                "oturum_sayisi": "Atandığı oturum",
            }
        )
        st.dataframe(frame, use_container_width=True, hide_index=True)
        removable = [row for row in questions if int(row["oturum_sayisi"]) == 0]
        if removable:
            st.markdown("#### Kullanılmayan soruyu sil")
            delete_options = {
                f"{row['soru_id']} · {row['soru_metni'][:90]}": int(row["soru_id"])
                for row in removable
            }
            with st.form("delete_question_form"):
                label = st.selectbox("Soru", list(delete_options))
                confirmed = st.checkbox("Bu sorunun silinmesini onaylıyorum")
                delete_clicked = st.form_submit_button("Kullanılmayan Soruyu Sil")
            if delete_clicked:
                if not confirmed:
                    st.error("Silme işlemini onaylayın.")
                else:
                    try:
                        delete_unassigned_question(delete_options[label])
                        st.success("Soru silindi.")
                        st.rerun()
                    except (ValueError, sqlite3.Error) as exc:
                        st.error(str(exc))
        else:
            st.caption("Tüm sorular en az bir oturuma atanmış; geçmişi korumak için silme kapalı.")
    else:
        st.info("Soru bankası boş.")


def teacher_view() -> None:
    if not teacher_login():
        return
    tabs = st.tabs(
        ["Genel Bakış", "Oturumlar", "Soru Analitiği", "Soru Bankası"]
    )
    with tabs[0]:
        if hasattr(st, "fragment"):
            st.fragment(run_every=f"{LIVE_REFRESH_SECONDS}s")(render_teacher_overview)()
        else:
            render_teacher_overview()
            st.button("Verileri Yenile", key="refresh_overview")
    with tabs[1]:
        render_session_management()
    with tabs[2]:
        if hasattr(st, "fragment"):
            st.fragment(run_every=f"{LIVE_REFRESH_SECONDS}s")(render_analytics)()
        else:
            render_analytics()
    with tabs[3]:
        render_question_bank()


def display_attempt_result(user_id: int, session_id: int) -> None:
    result = get_attempt_result(user_id, session_id)
    if not result:
        st.error("Sınav sonucu bulunamadı.")
        return
    score = float(result["puan"])
    passed = score >= float(result["gecme_notu"])
    render_metric_cards(
        [
            ("Toplam Soru", result["toplam_soru"]),
            ("Doğru", result["dogru"]),
            ("Yanlış", result["yanlis"]),
            ("Boş", max(0, int(result["toplam_soru"]) - int(result["cevaplanan"]))),
            ("Puan", f"{score:.2f}"),
        ]
    )
    if passed:
        st.success(f"Sınav tamamlandı: başarılı. Geçme puanı {result['gecme_notu']}.")
    else:
        st.info(f"Sınav tamamlandı. Geçme puanı {result['gecme_notu']}.")
    st.caption(
        f"Puanlama: doğru cevap soru puanını kazandırır, yanlış cevap "
        f"{WRONG_ANSWER_PENALTY:g} puan düşürür, boş cevap 0 puandır."
    )


def render_student_attempt() -> None:
    user_id = int(st.session_state.student_user_id)
    session_id = int(st.session_state.student_session_id)
    attempt = get_student_attempt(user_id, session_id)
    if not attempt:
        st.error("Katılım kaydı bulunamadı.")
        st.session_state.pop("student_user_id", None)
        st.session_state.pop("student_session_id", None)
        return

    st.markdown(
        f"<div class='dashboard-card'><div class='card-heading'>"
        f"{escape(str(attempt['baslik']))}</div>"
        f"<div>Katılımcı: <strong>{escape(str(attempt['ad_soyad']))}</strong></div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    total = len(attempt["questions"])
    answered = sum(1 for question in attempt["questions"] if question["cevap_id"])
    if total == 0:
        st.error("Bu oturuma henüz soru atanmadı. Öğretmene bildirin.")
        return

    joined_at = datetime.fromisoformat(str(attempt["katilim_zaman"]))
    deadline = joined_at + timedelta(minutes=int(attempt["sure_dakika"]))
    remaining_seconds = max(0, int((deadline - datetime.now()).total_seconds()))

    if (
        remaining_seconds == 0
        or attempt["oturum_durumu"] != "devam_ediyor"
        or int(attempt["tamamlandi_mi"])
    ):
        if not int(attempt["tamamlandi_mi"]):
            finish_participation(int(attempt["katilim_id"]))
        st.info(
            "Sınav süresi doldu." if remaining_seconds == 0
            else "Oturum öğretmen tarafından kapatıldı."
            if attempt["oturum_durumu"] != "devam_ediyor"
            else "Sınavı tamamladınız."
        )
        display_attempt_result(user_id, session_id)
        return

    progress = answered / total
    c1, c2 = st.columns([3, 1])
    with c1:
        st.progress(progress, text=f"İlerleme: {answered}/{total} soru")
    with c2:
        minutes, seconds = divmod(remaining_seconds, 60)
        st.metric("Kalan süre", f"{minutes:02d}:{seconds:02d}")

    if answered >= total:
        finish_participation(int(attempt["katilim_id"]))
        display_attempt_result(user_id, session_id)
        return

    question = next(
        row for row in attempt["questions"] if not row["cevap_id"]
    )
    qid = int(question["soru_id"])
    st.markdown(
        f"<div class='dashboard-card'><div class='card-heading'>"
        f"Soru {question['soru_sirasi']} / {total}</div>"
        f"<div style='font-size:17px;line-height:1.55;color:#F8FAFC'>"
        f"{escape(str(question['soru_metni']))}</div>"
        f"<div style='margin-top:10px;color:#94A3B8;font-size:12px'>"
        f"{escape(str(question['kategori']))} · "
        f"{escape(str(question['zorluk_seviyesi']))} · "
        f"{question['puan_degeri']} puan</div></div>",
        unsafe_allow_html=True,
    )
    options = attempt["options"].get(qid, [])
    if not options:
        st.error("Bu sorunun seçenekleri eksik; cevap kaydedilemiyor.")
        return
    option_by_label = {
        f"{option['secenek_etiketi']}) {option['secenek_metni']}": int(
            option["secenek_id"]
        )
        for option in options
    }
    with st.form(f"answer_form_{session_id}_{qid}"):
        selected = st.radio(
            "Cevabınızı seçin",
            list(option_by_label),
            key=f"answer_{session_id}_{qid}",
        )
        submitted = st.form_submit_button(
            "Cevabı Kaydet ve Devam Et", use_container_width=True
        )
    if submitted:
        try:
            saved = save_student_answer(
                attempt, qid, option_by_label[selected]
            )
            if saved:
                st.success("Cevabınız kaydedildi.")
            else:
                st.warning("Süreniz dolduğu için cevap kaydedilmedi.")
            st.rerun()
        except (ValueError, sqlite3.Error) as exc:
            st.error(str(exc))


def student_view() -> None:
    if "student_user_id" not in st.session_state:
        st.markdown(
            "<div class='dashboard-card'><div class='card-heading'>"
            "Aktif sınava katıl</div>"
            "<div style='color:#94A3B8'>Öğretmeninizin paylaştığı oturum kodunu "
            "ve sınavda görünecek adınızı girin.</div></div>",
            unsafe_allow_html=True,
        )
        with st.form("join_session_form"):
            join_code = st.text_input("Oturum kodu", max_chars=12)
            display_name = st.text_input("Görünen ad", max_chars=80)
            joined = st.form_submit_button("Sınava Katıl", use_container_width=True)
        if joined:
            try:
                user_id, session_id, session_title = create_guest_participation(
                    join_code, display_name
                )
                st.session_state.student_user_id = user_id
                st.session_state.student_session_id = session_id
                st.success(f"{session_title} oturumuna katıldınız.")
                st.rerun()
            except (ValueError, sqlite3.Error) as exc:
                st.error(str(exc))
        st.caption(
            "Oturum kodu yalnızca başlatılmış sınavlarda geçerlidir. "
            "Bu ders demosu oturum bazlı geçici öğrenci kaydı oluşturur."
        )
        return

    if st.button("Bu oturum ekranından çık", key="leave_student_attempt"):
        st.session_state.pop("student_user_id", None)
        st.session_state.pop("student_session_id", None)
        st.rerun()

    if hasattr(st, "fragment"):
        st.fragment(run_every=f"{STUDENT_REFRESH_SECONDS}s")(render_student_attempt)()
    else:
        render_student_attempt()
        st.caption("Sayaç otomatik yenilemesi için Streamlit 1.37 veya üzeri gerekir.")


def main() -> None:
    try:
        ensure_runtime_schema()
    except (OSError, sqlite3.Error, RuntimeError) as exc:
        st.error(f"Veritabanı başlatılamadı: {exc}")
        st.stop()

    selected_view = render_header()
    if selected_view == "Hoca Paneli":
        teacher_view()
    else:
        student_view()


if __name__ == "__main__":
    main()
