import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter
import re
import base64
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import html as _html


# ✅ set_page_config ПЕРВЫМ
st.set_page_config(
    page_title="SDU Angime Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
MODEL_CHAT = "compound-beta-mini"

# ═══════════════════════════════════════════════════════════════
# ЗАЩИТА ПАРОЛЕМ
# ═══════════════════════════════════════════════════════════════
def img_to_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def check_password():
    if st.session_state.get("authenticated", False):
        return True

    img1 = img_to_b64("IMG_2289.JPG")
    img2 = img_to_b64("photo_2026-03-12 02.06.08.jpeg")

    img1_html = f'<img src="data:image/jpeg;base64,{img1}" style="width:110px;height:110px;object-fit:cover;border-radius:50%;border:3px solid #6366f1;box-shadow:0 4px 20px rgba(99,102,241,0.3);">' if img1 else "🎓"
    img2_html = f'<img src="data:image/jpeg;base64,{img2}" style="width:110px;height:110px;object-fit:cover;border-radius:50%;border:3px solid #818cf8;box-shadow:0 4px 20px rgba(99,102,241,0.2);">' if img2 else ""

    # Центрируем через колонки Streamlit
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(f"""
        <style>
        .stApp {{ background: linear-gradient(135deg,#f0f4ff 0%,#faf5ff 50%,#f0f9ff 100%) !important; }}
        header[data-testid="stHeader"] {{ display:none !important; }}
        section[data-testid="stSidebar"] {{ display:none !important; }}
        .block-container {{ padding-top: 60px !important; }}
        /* Кнопка Войти — indigo */
        div[data-testid="stButton"] > button[kind="primary"] {{
            background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
            border: none !important;
            border-radius: 12px !important;
            font-size: 15px !important;
            font-weight: 700 !important;
            padding: 12px !important;
            box-shadow: 0 4px 16px rgba(99,102,241,0.35) !important;
        }}
        div[data-testid="stButton"] > button[kind="primary"]:hover {{
            background: linear-gradient(135deg, #4f46e5, #3730a3) !important;
            transform: translateY(-1px) !important;
        }}
        </style>

        <!-- Фото -->
        <div style="display:flex;gap:24px;align-items:center;
                    justify-content:center;margin-bottom:24px;">
            {img1_html}
            <div style="width:2px;height:80px;background:linear-gradient(
                to bottom,transparent,#6366f1,transparent);"></div>
            {img2_html}
        </div>

        <!-- Заголовок -->
        <div style="text-align:center;margin-bottom:28px;">
            <div style="font-size:12px;font-weight:700;color:#6366f1;
                        text-transform:uppercase;letter-spacing:3px;margin-bottom:8px;">
                Analytics Dashboard
            </div>
            <div style="font-size:30px;font-weight:900;color:#1e1b4b;line-height:1.2;">
                SDU Angime
            </div>
            <div style="font-size:15px;color:#64748b;margin-top:6px;">
                Telegram Channel Intelligence
            </div>
            <div style="width:50px;height:3px;
                        background:linear-gradient(to right,#6366f1,#a78bfa);
                        border-radius:2px;margin:16px auto 0;"></div>
        </div>

       
        """, unsafe_allow_html=True)

        password = st.text_input("", type="password",
                                  placeholder="Введите пароль…",
                                  label_visibility="collapsed",
                                  key="login_password")

        if st.button("Войти →", use_container_width=True, type="primary"):
            correct = os.getenv("APP_PASSWORD", "")
            if not correct:
                try:
                    correct = st.secrets.get("APP_PASSWORD", "")
                except Exception:
                    correct = ""
            if password == correct:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Неверный пароль")

        st.markdown("</div>", unsafe_allow_html=True)

        # Футер
        st.markdown("""
        <div style="text-align:center;margin-top:28px;">
            <div style="display:inline-flex;align-items:center;gap:12px;
                        background:white;border-radius:50px;padding:12px 28px;
                        box-shadow:0 2px 16px rgba(99,102,241,0.10);
                        border:1px solid #e0e7ff;">
                <span style="font-size:11px;color:#6366f1;font-weight:700;
                             text-transform:uppercase;letter-spacing:1.5px;">
                    18 Nauryz 2026
                </span>
                <span style="color:#c7d2fe;font-size:14px;">•</span>
                <span style="font-size:13px;color:#1e40af;font-weight:700;">
                    SDU University
                </span>
                <span style="color:#c7d2fe;font-size:14px;">•</span>
                <span style="font-size:13px;color:#15803d;font-weight:700;">
                    MADRID Lab × Data Science
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return False

if not check_password():
    st.stop()
# ═══════════════════════════════════════════════════════════════
# СТИЛИ
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Golos Text', sans-serif;
}

/* ── Светлый фон ───────────────────────────────────────────── */
.stApp {
    background: #f4f6fb;
}
.block-container { padding: 1.8rem 2.2rem !important; max-width: 1500px; }

/* ── Сайдбар ───────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #1e1b4b !important;
    border-right: none;
    box-shadow: 2px 0 16px rgba(30,27,75,0.12);
}
section[data-testid="stSidebar"] * { color: #c7d2fe !important; }
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e0e7ff !important;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 18px 0 8px 0;
    opacity: 0.65;
}

/* ── Метрики ───────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px 22px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    transition: border-color .2s, transform .2s, box-shadow .2s;
}
[data-testid="metric-container"]:hover {
    border-color: #6366f1;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(99,102,241,0.14);
}
/* Подпись метрики (label) */
[data-testid="metric-container"] label,
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] div {
    color: #334155 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: .7px;
}
/* Главное значение метрики */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: #1e1b4b !important;
    font-size: 28px !important;
    font-weight: 800 !important;
}
/* Delta (подзначение) */
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] div {
    color: #6366f1 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDeltaIcon"] { display: none; }

/* ── Убрать чёрную шапку Streamlit ────────────────────────── */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
}
[data-testid="stDecoration"] { display: none !important; }

/* ── Заголовки страниц ─────────────────────────────────────── */
.page-title {
    font-size: 26px; font-weight: 900; color: #1e1b4b;
    margin-bottom: 2px;
}
.page-sub { font-size: 13px; color: #94a3b8; margin-bottom: 20px; }

/* ── Карточки ──────────────────────────────────────────────── */
.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

/* ── Пост-карточки ─────────────────────────────────────────── */
.post-card {
    background: #ffffff;
    border: 1px solid #e8eef6;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: border-color .15s, box-shadow .15s;
}
.post-card:hover {
    border-color: #6366f1;
    box-shadow: 0 4px 14px rgba(99,102,241,0.1);
}
.post-meta { font-size: 11px; color: #94a3b8; margin-bottom: 7px; }
.post-text { font-size: 14px; color: #334155; line-height: 1.7; }

/* ── Badges ────────────────────────────────────────────────── */
.badge {
    display: inline-block; padding: 2px 9px;
    border-radius: 20px; font-size: 11px; font-weight: 600; margin-right: 5px;
}
.b-critical { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.b-high     { background:#fff7ed; color:#ea580c; border:1px solid #fed7aa; }
.b-medium   { background:#fefce8; color:#ca8a04; border:1px solid #fde68a; }
.b-low      { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.b-positive { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.b-negative { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.b-neutral  { background:#f8fafc; color:#64748b; border:1px solid #e2e8f0; }

/* ── Section labels ────────────────────────────────────────── */
.sec {
    font-size: 11px; font-weight: 700; color: #6366f1;
    text-transform: uppercase; letter-spacing: 1.1px;
    margin: 22px 0 10px 0;
}

/* ── Divider ───────────────────────────────────────────────── */
hr { border-color: #e2e8f0 !important; margin: 18px 0 !important; }

/* ── Banners ───────────────────────────────────────────────── */
.banner-info {
    background: #eef2ff; border: 1px solid #c7d2fe;
    border-radius: 10px; padding: 11px 16px; color: #4338ca;
    font-size: 13px; margin-bottom: 14px;
}
.banner-warn {
    background: #fff7ed; border: 1px solid #fed7aa;
    border-radius: 10px; padding: 11px 16px; color: #c2410c;
    font-size: 13px; margin-bottom: 14px;
}

/* ── Spike card ────────────────────────────────────────────── */
.spike-card {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-left: 4px solid #f97316;
    border-radius: 12px; padding: 14px 18px; margin-bottom: 10px;
}

/* ── Tabs ──────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff; border-radius: 12px; padding: 4px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; color: #94a3b8 !important; font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
    background: #eef2ff !important;
    color: #4338ca !important;
    font-weight: 600 !important;
}

/* ── Метрики — не обрезать текст ──────────────────────────── */
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] div {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    font-size: 11px !important;
}

/* ── Scrollbar ─────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #c7d2fe; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ ИЗ НОУТБУКА
# ═══════════════════════════════════════════════════════════════
CAT_RU = {
    "exams": "Экзамены", "academics": "Учёба", "teachers": "Преподаватели",
    "food": "Еда/Асхана", "dorms": "Общежитие", "infrastructure": "Инфраструктура",
    "scholarship": "Стипендия", "career": "Карьера", "relationships": "Отношения",
    "mental_health": "Психология", "events": "События",
    "admin": "Администрация", "humor": "Юмор", "other": "Другое",
}
SENT_RU  = {"positive": "Позитивный", "neutral": "Нейтральный", "negative": "Негативный"}
URG_RU   = {"low": "Низкий", "medium": "Средний", "high": "Высокий", "critical": "Критичный"}
LANG_RU  = {"ru": "Русский", "kk": "Казахский", "mixed_kk_ru": "Смешанный", "en": "Английский", "unknown": "Неизвестный"}

# Цвета — светлая тема (white + indigo sidebar)
C_BG   = "#f4f6fb"; C_CARD = "#ffffff"; C_BORDER = "#e2e8f0"
C_TEXT = "#1e293b"; C_MUTED = "#94a3b8"
C_BLUE = "#6366f1"; C_GREEN = "#16a34a"; C_RED = "#dc2626"
C_ORANGE = "#ea580c"; C_YELLOW = "#ca8a04"; C_PURPLE = "#7c3aed"

def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

SENT_C = {"positive": C_GREEN, "neutral": C_MUTED, "negative": C_RED}
URG_C  = {"low": C_GREEN, "medium": C_YELLOW, "high": C_ORANGE, "critical": C_RED}
CAT_C  = {
    "exams": C_BLUE, "academics": C_PURPLE, "teachers": "#0891b2",
    "food": C_ORANGE, "dorms": C_GREEN, "infrastructure": C_RED,
    "scholarship": "#4f46e5", "career": "#15803d", "relationships": "#be185d",
    "mental_health": "#7c3aed", "events": "#0284c7",
    "admin": "#c2410c", "humor": C_YELLOW, "other": C_MUTED,
}

DAYS_MAP = {
    0: "Дүйсенбі",
    1: "Сейсенбі",
    2: "Сәрсенбі",
    3: "Бейсенбі",
    4: "Жұма",
    5: "Сенбі",
    6: "Жексенбі",
}
DAYS_ORDER = ["Дүйсенбі", "Сейсенбі", "Сәрсенбі", "Бейсенбі", "Жұма", "Сенбі", "Жексенбі"]
PERIODS_KK = ["Таң", "Түс", "Кеш", "Түн"]   
VALID_DEPARTMENTS = [
    "Деканат", "Общежитие", "Административный отдел",
    "IT департамент", "Финансовый отдел", "AC Catering",
    "Служба безопасности", "Библиотека"
]
VALID_CATEGORIES = list(CAT_RU.keys())

# ═══════════════════════════════════════════════════════════════
# ЦЕНЗУРА
# ═══════════════════════════════════════════════════════════════
CENSOR_WORDS = {
    "хуй","хуя","хуе","хую","хуев","хуйня","ебанут","сыктым","cиктим","cікт","впизду","ебучи",
    "пизда","пизде","пизды","пиздец","пиздить","пиздёж",
    "ебать","ебёт","ебал","ебут","еблан","ебало","ёбаный","ебанный",
    "блядь","блять","Бля","блядский","долбаеб","далбое",
    "сука","суки","сучка","сучий",
    "мудак","мудаки","мудила", "пидор","пидорас","пидр", "шлюха","шлюхи","ублюдок",
    "уёбок","долбоёб","ёбнутый", "охуеть","охуел","охуела", "нахуй","нахуя","похуй",
    "заебать","заебал","заебись","далбаеб","далбаебтер","далбаебтар",
    "шешел","шешелерын","көтақ","қотақ","секс", "хуе", "трах"
}


# ── Функции цензуры ────────────────────────────────────────────
def censor_text(text: str) -> tuple:
    if not isinstance(text, str):
        return text, False
    found  = False
    result = text
    for word in CENSOR_WORDS:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        if pattern.search(result):
            found  = True
            result = pattern.sub("*" * len(word), result)
    return result, found

def render_post_text(text: str, is_expanded: bool = False) -> tuple:
    censored, has_profanity = censor_text(text)
    if not is_expanded:
        show = (censored[:300] + "…") if len(censored) > 300 else censored
    else:
        show = censored
    return show, has_profanity

# ═══════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ═══════════════════════════════════════════════════════════════
BASE = "data/analyzed"

@st.cache_data(ttl=300, show_spinner=False)
def load_data():
    paths = {
        "main": f"{BASE}/classified_posts.csv",
        "suggestions": f"{BASE}/student_suggestions.csv",
        "critical":f"{BASE}/critical_posts.csv",
        "spikes":f"{BASE}/spike_explanations.csv",
    }
    dfs = {}
    for key, path in paths.items():
        p = Path(path)
        if p.exists():
            df = pd.read_csv(path, low_memory=False)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            dfs[key] = df
        else:
            dfs[key] = pd.DataFrame()

    # Добавляем вычисляемые колонки к главному датафрейму
    df = dfs["main"]
    if not df.empty and "date" in df.columns:
        df["date_day"] = df["date"].dt.strftime("%Y-%m-%d")
        df["month_str"] = df["date"].dt.strftime("%Y-%m")
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["week_num"] = df["date"].dt.isocalendar().week.astype(int)
        df["day_of_week_num"] = df["date"].dt.weekday          
        df["day_of_week"] = df["day_of_week_num"].map(DAYS_MAP)
        if "hour" not in df.columns:
            df["hour"] = df["date"].dt.hour

        def _period(h):
            if  6 <= h < 12: return "Таң"
            if 12 <= h < 18: return "Түс"
            if 18 <= h < 24: return "Кеш"
            return "Түн"
        df["period"] = df["hour"].apply(_period)

        if "semester" not in df.columns:
            def _sem(dt):
                if pd.isna(dt): return "unknown"
                m = dt.month
                if m in (9,10,11,12): return f"Fall {dt.year}"
                if m in (1,2,3,4,5):  return f"Spring {dt.year}"
                return f"Summer {dt.year}"
            df["semester"] = df["date"].apply(_sem)
    dfs["main"] = df
    return dfs

data = load_data()
df = data["main"]
df_sugg = data["suggestions"]
df_crit = data["critical"]
df_spikes = data["spikes"]

DATA_OK = not df.empty

# ═══════════════════════════════════════════════════════════════
# ПРИМЕНЕНИЕ ФИЛЬТРОВ
# ═══════════════════════════════════════════════════════════════
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    ss = st.session_state

    # Дата
    dr = ss.get("f_date")
    if dr and len(dr) == 2 and "date" in df.columns:
        d0, d1 = pd.Timestamp(dr[0]), pd.Timestamp(dr[1])
        df = df[(df["date"] >= d0) & (df["date"] <= d1)]

    # Семестр
    sems = ss.get("f_sems", [])
    if sems and "semester" in df.columns:
        df = df[df["semester"].isin(sems)]

    # Месяцы
    months = ss.get("f_months", [])
    if months and "month" in df.columns:
        df = df[df["month"].isin(months)]

    # Дни недели — фильтруем по казахским названиям из DAYS_MAP
    days = ss.get("f_days", [])
    if days and "day_of_week" in df.columns:
        df = df[df["day_of_week"].isin(days)]

    # Время суток — фильтруем по колонке period (Таң/Түс/Кеш/Түн)
    tod = ss.get("f_time", [])
    if tod and "period" in df.columns:
        df = df[df["period"].isin(tod)]

    # Департаменты
    depts = ss.get("f_depts", [])
    if depts and "responsible_dept" in df.columns:
        df = df[df["responsible_dept"].isin(depts)]

    # Категории
    cats = ss.get("f_cats", [])
    if cats and "llm_category" in df.columns:
        df = df[df["llm_category"].isin(cats)]

    # Срочность
    urgs = ss.get("f_urgency", [])
    if urgs and "llm_urgency" in df.columns:
        df = df[df["llm_urgency"].isin(urgs)]

    # Тональность
    sents = ss.get("f_sentiment", [])
    if sents and "llm_sentiment" in df.columns:
        df = df[df["llm_sentiment"].isin(sents)]

    # Только конструктив
    if ss.get("f_constructive", False) and "is_constructive" in df.columns:
        df = df[df["is_constructive"] == True]

    return df.copy()

# ═══════════════════════════════════════════════════════════════
# HELPER: базовый layout для Plotly
# ═══════════════════════════════════════════════════════════════
def _pl(fig, h=320, title="", ml=50, mr=20, mt=30, mb=40):
    fig.update_layout(
        height=h,
        **({"title": dict(text=title, font=dict(color=C_TEXT, size=14))} if title else {}),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fafbff",
        font=dict(color=C_MUTED, size=12, family="Golos Text, sans-serif"),
        margin=dict(t=mt if title else 16, r=mr, b=mb, l=ml),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=C_BORDER, borderwidth=1,
                    font=dict(color=C_MUTED, size=11)),
        xaxis=dict(gridcolor="#eef2ff", linecolor=C_BORDER, tickfont=dict(color=C_MUTED)),
        yaxis=dict(gridcolor="#eef2ff", linecolor=C_BORDER, tickfont=dict(color=C_MUTED)),
        hovermode="x unified",
    )
    return fig


CFG = {"displayModeBar": False}

# ═══════════════════════════════════════════════════════════════
# БОКОВАЯ ПАНЕЛЬ
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Навигация СВЕРХУ ─────────────────────────────────────
    page = st.radio("", ["OVERVIEW", "TOPICS", "SENTIMENT",
                          "AI SEARCH", "AI INSIGHTS & REPORTS"],
                     label_visibility="collapsed", key="nav")

    st.divider()
    st.toggle("🔞 **ЦЕНЗУРА**", key="f_censor", value=True)

    # ── Фото по центру ───────────────────────────────────────
    logo_path = Path("photo_2026-03-12 02.06.08.jpeg")
    if logo_path.exists():
        col_l, col_m, col_r = st.columns([1, 3, 1])
        with col_m:
            st.image(str(logo_path), width=180)
    
    # ── Подпись ──────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center;margin-top:8px;margin-bottom:4px'>
        <div style='font-size:15px;font-weight:800;color:#e0e7ff;
                    letter-spacing:.3px'>🎓 SDU Angime</div>
        <div style='font-size:11px;color:#818cf8;margin-top:2px'>
            telegram channel
        </div>
    </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Данные ───────────────────────────────────────────────
    if DATA_OK:
        dmin = df["date"].min().date()
        dmax = df["date"].max().date()
        st.markdown(f"""
        <div style='text-align:center;margin-bottom:10px'>
            <div style='font-size:13px;font-weight:700;
                        color:#c7d2fe;margin-bottom:4px'>
                • {dmin} → {dmax}
            </div>
            <div style='font-size:13px;font-weight:700;color:#c7d2fe'>
                • {len(df):,} постов
            </div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Фильтры — сворачиваемые ──────────────────────────────
    with st.expander("Фильтры", expanded=False):

        with st.expander("📅 Временные фильтры", expanded=False):
            if DATA_OK:
                st.date_input("Период", value=(dmin, dmax),
                              min_value=dmin, max_value=dmax, key="f_date",
                              label_visibility="collapsed")
                sems_all = sorted(df["semester"].dropna().unique().tolist(), reverse=True)
                st.multiselect("Семестр", sems_all, key="f_sems",
                               placeholder="Все семестры")
            st.multiselect("Месяц", list(range(1, 13)),
                            format_func=lambda m: ["Янв","Фев","Мар","Апр","Май","Июн",
                                                    "Июл","Авг","Сен","Окт","Ноя","Дек"][m-1],
                            key="f_months", placeholder="Все месяцы")
            st.multiselect("Күн", DAYS_ORDER, key="f_days",
                           placeholder="Барлық күндер")
            st.multiselect("Тәулік мезгілі", PERIODS_KK,
                            format_func=lambda p: {
                                "Таң": "🌅 Таң (06–12)",
                                "Түс": "☀️ Түс (12–18)",
                                "Кеш": "🌆 Кеш (18–24)",
                                "Түн": "🌙 Түн (00–06)",
                            }.get(p, p),
                            key="f_time", placeholder="Кез келген уақыт")

        with st.expander("🏷 Тематика", expanded=False):
            st.multiselect("Департамент", VALID_DEPARTMENTS,
                            key="f_depts", placeholder="Все департаменты")
            st.multiselect("Категория",
                            [CAT_RU[c] for c in VALID_CATEGORIES],
                            key="_cats_ru", placeholder="Все категории")
            CAT_EN = {v: k for k, v in CAT_RU.items()}
            st.session_state["f_cats"] = [CAT_EN.get(c, c)
                                           for c in st.session_state.get("_cats_ru", [])]

        with st.expander("⚡ Статус", expanded=False):
            st.multiselect("Срочность", ["critical","high","medium","low"],
                            format_func=lambda x: URG_RU.get(x, x),
                            key="f_urgency", placeholder="Любая срочность")
            st.multiselect("Тональность", ["positive","neutral","negative"],
                            format_func=lambda x: SENT_RU.get(x, x),
                            key="f_sentiment", placeholder="Любая тональность")
            st.toggle("💡 Только конструктивные", key="f_constructive")

# ═══════════════════════════════════════════════════════════════
# ПРИМЕНЯЕМ ФИЛЬТР
# ═══════════════════════════════════════════════════════════════
df_f = apply_filters(df) if DATA_OK else pd.DataFrame()

# Иконки
URG_ICO  = {"low":"🟢","medium":"🟡","high":"🟠","critical":"🔴"}
SENT_ICO = {"positive":"😊","neutral":"😐","negative":"😠"}


def post_card(row, border_col=None, key_prefix="pc"):
    urg   = row.get("llm_urgency", "low")
    sent  = row.get("llm_sentiment", "neutral")
    cat   = CAT_RU.get(row.get("llm_category", ""), row.get("llm_category", ""))
    dept  = str(row.get("responsible_dept", "")) if pd.notna(row.get("responsible_dept", "")) else "—"
    vir   = float(row.get("virality_score", 0))
    views = int(row.get("views", 0)) if pd.notna(row.get("views", 0)) else 0
    bc    = border_col or URG_C.get(urg, C_MUTED)

  
    raw       = str(row.get("message_clean", ""))
    text_full = re.sub(r"<[^>]+>", " ", raw)
    text_full = re.sub(r"\s+", " ", text_full).strip()
    text_safe = _html.escape(text_full)
    

    # ── Уникальный ключ — ПОСЛЕ text_full ─────────────────────
    row_id      = str(row.get("message_id", abs(hash(text_full[:30]))))
    state_key   = f"{key_prefix}_{row_id}_expanded"
    is_expanded = st.session_state.get(state_key, False)

    # ── Цензура ────────────────────────────────────────────────
    censor_on = st.session_state.get("f_censor", True)
    if censor_on:
        text_show, has_profanity = render_post_text(text_safe, is_expanded)
    else:
        has_profanity = False
        text_show = text_safe if is_expanded else (
            (text_safe[:300] + "…") if len(text_safe) > 300 else text_safe
        )

    show_btn = len(text_full) > 300

    # ── Бейдж мата ─────────────────────────────────────────────
    profanity_badge = (
        "<span style='background:#fef9c3;color:#854d0e;border:1px solid #fde68a;"
        "border-radius:6px;padding:1px 7px;font-size:10px;font-weight:600;"
        "margin-left:6px'>⚠ ненормативная лексика</span>"
    ) if has_profanity and censor_on else ""

    # Изменение здесь: {profanity_badge} теперь на одной строке с остальным текстом
    st.markdown(f"""
    <div class="post-card" style="border-left:3px solid {bc}">
        <div class="post-meta">
            {URG_ICO.get(urg, '')}
            <span class="badge b-{urg}">{URG_RU.get(urg, urg)}</span>
            <span class="badge b-{sent}">{SENT_ICO.get(sent, '')} {SENT_RU.get(sent, sent)}</span>
            <b style="color:#6b8fb8">{cat}</b> · 🏢 {dept} · 👁 {views:,} · ⚡ {vir:.0f} {profanity_badge}
        </div>
        <div class="post-text">{text_show}</div>
    </div>""", unsafe_allow_html=True)

    if show_btn:
        btn_label = "▲ Свернуть" if is_expanded else "▼ Читать полностью"
        if st.button(btn_label, key=f"btn_{state_key}", use_container_width=False):
            st.session_state[state_key] = not is_expanded
            st.rerun()

    return ""









# ═══════════════════════════════════════════════════════════════
# ══════════════════ СТРАНИЦА 1: OVERVIEW ═══════════════════════
# ═══════════════════════════════════════════════════════════════
if page == "OVERVIEW":
    dmin_s = df["date"].min().strftime("%d.%m.%Y") if DATA_OK else "—"
    dmax_s = df["date"].max().strftime("%d.%m.%Y") if DATA_OK else "—"
    st.markdown(f"<div class='page-title'>SDU ANGIME OVERVIEW</div>"
                f"<div class='page-sub'>Данные с {dmin_s} по {dmax_s} | {len(df_f):,} постов в выборке</div>",
                unsafe_allow_html=True)

    if not DATA_OK:
        st.error("❌ Файл classified_posts.csv не найден. Проверь путь.")
        st.stop()

    # ── KPI ────────────────────────────────────────────────────
    total       = len(df_f)
    neg_pct     = (df_f["llm_sentiment"]=="negative").mean()*100 if total else 0
    avg_vir     = df_f["virality_score"].mean() if total else 0
    constructiv = int(df_f["is_constructive"].sum()) if "is_constructive" in df_f.columns else 0
    critical_n  = int((df_f["llm_urgency"]=="critical").sum())
    top_dept    = df_f["responsible_dept"].dropna().value_counts()
    top_dept_nm = top_dept.index[0] if len(top_dept) else "—"

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("📨 Всего постов",        f"{total:,}")
    c2.metric("😰 Индекс тревожности",  f"{neg_pct:.1f}%")
    c3.metric("⚡ Avg Virality",         f"{avg_vir:.0f}")
    c4.metric("🚨 Критичных",           f"{critical_n}")
    c5.metric("💡 Идей студентов",      f"{constructiv}")
    c6.metric("🏢 Топ отдел",           top_dept_nm, f"{top_dept.iloc[0] if len(top_dept) else 0} упом.")

    st.divider()

    # ── Stacked area timeline ──────────────────────────────────
    st.markdown("<div class='sec'>📈 Динамика активности по сентименту</div>", unsafe_allow_html=True)
    freq_map = {"По неделям":"W","По месяцам":"M","По дням":"D"}
    freq_ch  = st.select_slider("", list(freq_map.keys()), value="По неделям",
                                  label_visibility="collapsed", key="ov_freq")
    freq = freq_map[freq_ch]

    ts = df_f.copy()
    ts["period"] = ts["date"].dt.to_period(freq).dt.to_timestamp()
    ts_grp = ts.groupby(["period","llm_sentiment"]).size().reset_index(name="n")

    fig_tl = go.Figure()
    for s in ["negative","neutral","positive"]:
        sub = ts_grp[ts_grp["llm_sentiment"]==s]
        fig_tl.add_trace(go.Scatter(
            x=sub["period"], y=sub["n"],
            name=SENT_RU[s], stackgroup="one", mode="lines",
            line=dict(width=0.5, color=SENT_C[s]),
            fillcolor=rgba(SENT_C[s], 0.33),
            hovertemplate=f"{SENT_RU[s]}: %{{y}}<extra></extra>",
        ))
    fig_tl = _pl(fig_tl, 260)
    st.plotly_chart(fig_tl, use_container_width=True, config=CFG)

    # ── Heatmap + Lang bar ─────────────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("<div class='sec'>🕐 Heatmap активности (день × час)</div>", unsafe_allow_html=True)
        pivot = (df_f.groupby(["day_of_week","hour"]).size()
                      .reset_index(name="n")
                      .pivot(index="day_of_week", columns="hour", values="n")
                      .reindex(DAYS_ORDER).fillna(0))
        fig_hm = go.Figure(go.Heatmap(
            z=pivot.values, x=[f"{h}:00" for h in range(24)], y=pivot.index.tolist(),
            colorscale=[[0,"#f8f9ff"],[0.4,"#c7d2fe"],[1,C_BLUE]],
            showscale=False,
            hovertemplate="<b>%{y} %{x}</b><br>Постов: %{z}<extra></extra>",
        ))
        fig_hm.update_layout(yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"))
        fig_hm = _pl(fig_hm, 230, ml=40, mb=30)
        st.plotly_chart(fig_hm, use_container_width=True, config=CFG)

    with col2:
        st.markdown("<div class='sec'>🌐 Языки постов</div>", unsafe_allow_html=True)
        lang_c = df_f["language"].value_counts()
        lang_labels = [LANG_RU.get(l,l) for l in lang_c.index]
        lang_colors = [{"ru":C_BLUE,"kk":C_GREEN,"mixed_kk_ru":C_PURPLE,
                         "en":"#0891b2","unknown":C_MUTED}.get(l,C_MUTED) for l in lang_c.index]
        fig_lang = go.Figure(go.Bar(
            x=lang_c.values, y=lang_labels, orientation="h",
            marker_color=lang_colors,
            text=[f"{v}  ({v/lang_c.sum()*100:.0f}%)" for v in lang_c.values],
            textposition="outside", textfont=dict(color=C_TEXT, size=11),
            hovertemplate="%{y}: %{x}<extra></extra>",
        ))
        fig_lang.update_layout(yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
                                xaxis=dict(showgrid=False))
        fig_lang = _pl(fig_lang, 230, ml=10, mr=80, mb=30)
        st.plotly_chart(fig_lang, use_container_width=True, config=CFG)

    st.divider()

    # ── Доля сентимента на всю ширину ─────────────────────────
    st.markdown("<div class='sec'>💬 Доля сентимента по времени</div>", unsafe_allow_html=True)
    freq_map2 = {"Годы":"Y","Кварталы":"Q","Месяцы":"M","Недели":"W"}
    fc2 = st.select_slider("", list(freq_map2.keys()), value="Месяцы",
                              label_visibility="collapsed", key="sent_freq")
    ts2 = df_f.copy()
    ts2["period"] = ts2["date"].dt.to_period(freq_map2[fc2]).dt.to_timestamp()
    grp2 = ts2.groupby(["period","llm_sentiment"]).size().unstack(fill_value=0)
    tot2 = grp2.sum(axis=1)
    pct2 = grp2.divide(tot2, axis=0) * 100

    fig_sb2 = go.Figure()
    for s in ["negative","neutral","positive"]:
        if s in pct2.columns:
            fig_sb2.add_trace(go.Bar(
                x=pct2.index, y=pct2[s], name=SENT_RU[s],
                marker_color=SENT_C[s],
                hovertemplate=f"{SENT_RU[s]}: %{{y:.1f}}%<extra></extra>",
            ))
    fig_sb2.update_layout(barmode="stack", bargap=0.1)
    fig_sb2 = _pl(fig_sb2, 320)
    st.plotly_chart(fig_sb2, use_container_width=True, config=CFG)

    st.divider()

    # ── Топ постов по virality ─────────────────────────────────
    st.markdown("<div class='sec'>🔥 Топ постов по Virality Score</div>", unsafe_allow_html=True)
    n_top = st.slider("Показать", 5, 30, 10, key="ov_n", label_visibility="collapsed")
    for _, r in df_f.nlargest(n_top, "virality_score").iterrows():
        post_card(r, key_prefix="ov_top")

    st.divider()

    # ── Упоминания по департаментам — stacked по срочности ────
    st.markdown("<div class='sec'>🏢 Упоминания по департаментам</div>", unsafe_allow_html=True)

    top_depts  = df_f["responsible_dept"].dropna().value_counts().head(8).index.tolist()
    dept_sent  = (df_f[df_f["responsible_dept"].isin(top_depts)]
                .groupby(["responsible_dept", "llm_sentiment"])
                .size().reset_index(name="n"))
    dept_total = dept_sent.groupby("responsible_dept")["n"].sum()
    dept_order = dept_total.sort_values(ascending=True).index.tolist()

    fig_dept = go.Figure()
    for s in ["negative", "neutral", "positive"]:
        sub = (dept_sent[dept_sent["llm_sentiment"] == s]
            .set_index("responsible_dept")
            .reindex(dept_order, fill_value=0)
            .reset_index())
        fig_dept.add_trace(go.Bar(
            x=sub["n"],
            y=sub["responsible_dept"],
            name=SENT_RU[s],
            orientation="h",
            marker=dict(color=SENT_C[s], opacity=0.85, line=dict(width=0)),
            hovertemplate=f"<b>%{{y}}</b><br>{SENT_RU[s]}: %{{x}}<extra></extra>",
        ))
    fig_dept.update_layout(
        barmode="stack",
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=12, color="#334155")),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(color="#94a3b8")),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center",
                    font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
        bargap=0.35,
    )
    fig_dept = _pl(fig_dept, 340, ml=10, mr=20, mb=50)
    st.plotly_chart(fig_dept, use_container_width=True, config=CFG)

    # ── Карточки отделов ──────────────────────────────────────
    SENT_BG = {"negative": C_RED, "neutral": C_MUTED, "positive": C_GREEN}
    card_cols = st.columns(4)

    for i, dept in enumerate(reversed(dept_order)):
        total_d = int(dept_total.get(dept, 0))

        sent_counts = {s: int(dept_sent[
            (dept_sent["responsible_dept"] == dept) &
            (dept_sent["llm_sentiment"] == s)]["n"].sum())
            for s in ["negative", "neutral", "positive"]}

        neg_pct_d = sent_counts["negative"] / total_d * 100 if total_d else 0
        bar_color = C_RED if neg_pct_d > 40 else C_ORANGE if neg_pct_d > 25 else C_GREEN
        bar_w     = int(neg_pct_d)

        badges_html = "".join([
            f"<span style='background:{SENT_BG[s]};color:#fff;"
            f"border-radius:6px;padding:3px 9px;font-size:12px;"
            f"font-weight:600;margin-right:5px'>"
            f"{SENT_ICO[s]} {sent_counts[s]}</span>"
            for s in ["negative", "neutral", "positive"] if sent_counts[s] > 0
        ])

        with card_cols[i % 4]:
            st.markdown(f"""
            <div style='padding:14px 16px;background:#ffffff;
                        border:1px solid #e8eef6;border-radius:12px;
                        box-shadow:0 1px 4px rgba(0,0,0,0.05);margin-bottom:6px'>
                <div style='font-size:12px;font-weight:700;color:#1e1b4b;
                            margin-bottom:6px'>{dept}</div>
                <div style='font-size:22px;font-weight:800;color:#1e1b4b;
                            margin-bottom:8px'>{total_d:,}</div>
                <div style='margin-bottom:8px'>{badges_html}</div>
                <div style='font-size:11px;color:{C_RED};font-weight:600;
                            margin-bottom:6px'>😠 {neg_pct_d:.0f}% негатива</div>
                <div style='background:#f1f5f9;border-radius:4px;height:4px'>
                    <div style='background:{bar_color};width:{bar_w}%;
                                height:4px;border-radius:4px'></div>
                </div>
            </div>""", unsafe_allow_html=True)

            # Кликабельные кнопки
            b1, b2, b3 = st.columns(3)
            active = st.session_state.get("dept_filter")

            for col, s, ico in [(b1, "negative", "😠"), (b2, "neutral", "😐"), (b3, "positive", "😊")]:
                btn_key  = f"dept_{dept}_{s}"
                is_active = active == btn_key
                label    = f"{'✓ ' if is_active else ''}{ico} {sent_counts[s]}"
                if col.button(label, key=btn_key, use_container_width=True):
                    if is_active:
                        st.session_state["dept_filter"] = None
                    else:
                        st.session_state["dept_filter"]      = btn_key
                        st.session_state["dept_filter_dept"] = dept
                        st.session_state["dept_filter_sent"] = s
                    st.rerun()

    # ── Панель постов ──────────────────────────────────────────
    if st.session_state.get("dept_filter"):
        sel_dept   = st.session_state["dept_filter_dept"]
        sel_sent   = st.session_state["dept_filter_sent"]
        sent_color = SENT_C[sel_sent]

        # Топ-20 по virality — одна выборка для показа И для AI
        matched = df_f[
            (df_f["responsible_dept"] == sel_dept) &
            (df_f["llm_sentiment"]    == sel_sent)
        ].nlargest(20, "virality_score")

        total_count = len(df_f[
            (df_f["responsible_dept"] == sel_dept) &
            (df_f["llm_sentiment"]    == sel_sent)
        ])

        st.markdown(f"""
        <div style='background:#f8faff;border:1px solid #c7d2fe;
                    border-left:4px solid {sent_color};border-radius:12px;
                    padding:16px 20px;margin:16px 0 12px 0'>
            <span style='font-size:15px;font-weight:800;color:#1e1b4b'>
                🏢 {sel_dept}
            </span>
            <span style='font-size:13px;color:{sent_color};font-weight:700;margin-left:10px'>
                {SENT_ICO[sel_sent]} {SENT_RU[sel_sent]}
            </span>
            <span style='font-size:12px;color:{C_MUTED};margin-left:8px'>
                · показано топ-{len(matched)} из {total_count} постов · по virality
            </span>
        </div>""", unsafe_allow_html=True)

        # ── AI анализ по центру ────────────────────────────────
        if groq_client:
            ai_key = f"ai_dept_{sel_dept}_{sel_sent}"

            col_l, col_c, col_r = st.columns([2, 3, 2])
            if col_c.button(
                f"🤖 AI анализ топ-20 постов",
                key=f"ai_btn_{sel_dept}_{sel_sent}",
                use_container_width=True
            ):
                # AI анализирует ровно те же 20 постов что показываются
                top_texts = matched["message_clean"].fillna("").tolist()

                prompt = (
                    f"Студенты SDU написали эти {SENT_RU[sel_sent].lower()} посты "
                    f"об отделе «{sel_dept}» (топ-20 по популярности из {total_count} всего):\n\n" +
                    "\n".join([f"- {t[:200]}" for t in top_texts]) +
                    "\n\nДай краткий анализ (3-4 предложения): "
                    "в чём главные проблемы/темы и что рекомендуешь руководству?"
                )

                with st.spinner("Анализирую топ-20 постов…"):
                    try:
                        resp = groq_client.chat.completions.create(
                            model=MODEL_CHAT,
                            max_tokens=400,
                            messages=[
                                {"role": "system",
                                 "content": "Аналитик постов студентов SDU Университета. Кратко и по делу на русском."},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        st.session_state[ai_key] = resp.choices[0].message.content
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

            if st.session_state.get(ai_key):
                st.markdown(f"""
                <div style='background:#eef2ff;border:1px solid #c7d2fe;
                            border-radius:10px;padding:14px 18px;
                            color:#3730a3;font-size:14px;line-height:1.8;
                            margin-bottom:16px'>
                    🤖 {st.session_state[ai_key]}
                </div>""", unsafe_allow_html=True)

        # ── Посты (те же 20 что анализировал AI) ──────────────
        for _, r in matched.iterrows():
            post_card(r, key_prefix=f"dept_{sel_dept}_{sel_sent}")
# ═══════════════════════════════════════════════════════════════
# ══════════════════ СТРАНИЦА 2: TOPICS ═════════════════════════
# ═══════════════════════════════════════════════════════════════
elif page == "TOPICS":
    st.markdown("<div class='page-title'>🌌 Topics</div>"
                "<div class='page-sub'>Структура тем, динамика и детализация по топикам</div>",
                unsafe_allow_html=True)

    if not DATA_OK:
        st.error("❌ Нет данных."); st.stop()

# ── Распределение категорий + тональность ─────────────────
    st.markdown("<div class='sec'>📊 Распределение категорий</div>", unsafe_allow_html=True)

    cat_c = df_f["llm_category"].value_counts().reset_index()
    cat_c.columns = ["cat", "n"]
    cat_c["pct"]    = cat_c["n"] / len(df_f) * 100
    cat_c["cat_ru"] = cat_c["cat"].map(CAT_RU).fillna(cat_c["cat"])
    cat_c["color"]  = cat_c["cat"].map(CAT_C).fillna(C_MUTED)

    # Считаем тональность по каждой категории
    cat_sent_pivot = (df_f.groupby(["llm_category", "llm_sentiment"])
                      .size().unstack(fill_value=0))
    cat_sent_pivot["tot"] = cat_sent_pivot.sum(axis=1)
    for s in ["negative", "neutral", "positive"]:
        if s not in cat_sent_pivot.columns:
            cat_sent_pivot[s] = 0
        cat_sent_pivot[f"pct_{s}"] = (cat_sent_pivot[s] / cat_sent_pivot["tot"] * 100).round(0).astype(int)

    bar_h = max(400, len(cat_c) * 42)
    fig_cbar = go.Figure(go.Bar(
        x=cat_c["n"], y=cat_c["cat_ru"], orientation="h",
        marker_color=cat_c["color"].tolist(),
        text=[f"  {r['n']}  ({r['pct']:.1f}%)" for _, r in cat_c.iterrows()],
        textposition="outside",
        textfont=dict(color=C_TEXT, size=12, family="Golos Text, sans-serif"),
        hovertemplate="<b>%{y}</b><br>%{x} постов<extra></extra>",
    ))
    fig_cbar.update_layout(
        yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)",
                   tickfont=dict(size=13, color=C_TEXT)),
        xaxis=dict(showgrid=False),
    )
    fig_cbar = _pl(fig_cbar, bar_h, ml=10, mr=140, mb=20)
    st.plotly_chart(fig_cbar, use_container_width=True, config=CFG)

    # ── Мини-карточки тональности под графиком ────────────────
    cols_per_row = 4
    rows = [cat_c.iloc[i:i+cols_per_row] for i in range(0, len(cat_c), cols_per_row)]

    for row_df in rows:
        cols = st.columns(cols_per_row)
        for col_idx, (_, r) in enumerate(row_df.iterrows()):
            cat_en = r["cat"]
            cat_ru = r["cat_ru"]
            color  = r["color"]
            total  = r["n"]

            if cat_en in cat_sent_pivot.index:
                neg_p = cat_sent_pivot.loc[cat_en, "pct_negative"]
                neu_p = cat_sent_pivot.loc[cat_en, "pct_neutral"]
                pos_p = cat_sent_pivot.loc[cat_en, "pct_positive"]
            else:
                neg_p = neu_p = pos_p = 0

            cols[col_idx].markdown(f"""
            <div style='background:#fff;border:1px solid {C_BORDER};
                        border-left:3px solid {color};border-radius:10px;
                        padding:10px 12px;margin-bottom:8px'>
                <div style='font-size:11px;font-weight:700;color:{C_TEXT};
                            margin-bottom:7px;white-space:nowrap;
                            overflow:hidden;text-overflow:ellipsis'
                     title='{cat_ru}'>{cat_ru}</div>
                <div style='font-size:11px;color:{C_MUTED};
                            margin-bottom:7px'>📨 {total:,} постов</div>
                <div style='display:flex;gap:4px'>
                    <div style='flex:1;text-align:center;background:#fef2f2;
                                border-radius:6px;padding:5px 2px'>
                        <div style='font-size:14px;font-weight:800;
                                    color:{C_RED}'>{neg_p}%</div>
                        <div style='font-size:9px;color:{C_MUTED}'>😠</div>
                    </div>
                    <div style='flex:1;text-align:center;background:#f8fafc;
                                border-radius:6px;padding:5px 2px'>
                        <div style='font-size:14px;font-weight:800;
                                    color:{C_MUTED}'>{neu_p}%</div>
                        <div style='font-size:9px;color:{C_MUTED}'>😐</div>
                    </div>
                    <div style='flex:1;text-align:center;background:#f0fdf4;
                                border-radius:6px;padding:5px 2px'>
                        <div style='font-size:14px;font-weight:800;
                                    color:{C_GREEN}'>{pos_p}%</div>
                        <div style='font-size:9px;color:{C_MUTED}'>😊</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.divider()
    # ── Динамика категорий ─────────────────────────────────────
    st.markdown("<div class='sec'>📈 Динамика топ-7 категорий по месяцам</div>", unsafe_allow_html=True)
    top7 = df_f["llm_category"].value_counts().head(7).index.tolist()
    dyn  = (df_f[df_f["llm_category"].isin(top7)].copy()
            .assign(month_ts=lambda d: d["date"].dt.to_period("M").dt.to_timestamp())
            .groupby(["month_ts","llm_category"]).size().reset_index(name="n"))

    fig_dyn = go.Figure()
    for cat in top7:
        sub = dyn[dyn["llm_category"]==cat]
        fig_dyn.add_trace(go.Scatter(
            x=sub["month_ts"], y=sub["n"],
            name=CAT_RU.get(cat,cat), mode="lines",
            line=dict(color=CAT_C.get(cat,C_MUTED), width=2.5),
            hovertemplate=f"{CAT_RU.get(cat,'')}: %{{y}}<extra></extra>",
        ))
    fig_dyn.update_layout(hovermode="x unified")
    fig_dyn = _pl(fig_dyn, 300)
    st.plotly_chart(fig_dyn, use_container_width=True, config=CFG)

    st.divider()

    # ── Drill-down по КАТЕГОРИИ ────────────────────────────────
    st.markdown("<div class='sec'>🔬 Детализация по категории</div>", unsafe_allow_html=True)

    cats_available = df_f["llm_category"].dropna().unique().tolist()
    cats_ru_list   = [CAT_RU.get(c, c) for c in sorted(cats_available)]

    col_s, col_sort = st.columns([3, 2])
    sel_cat_ru = col_s.selectbox("Выбери категорию", cats_ru_list, key="tp_cat_sel")
    sort_tp    = col_sort.selectbox("Сортировать по", ["virality_score","views","reactions_total"],
                                     key="tp_sort")
    # Обратный маппинг: русское → английское
    CAT_EN_MAP = {v: k for k, v in CAT_RU.items()}
    sel_cat_en = CAT_EN_MAP.get(sel_cat_ru, sel_cat_ru)
    tp_df = df_f[df_f["llm_category"] == sel_cat_en]

    # ── KPI ─────────────────────────────────────────────────────
    cat_color = CAT_C.get(sel_cat_en, C_BLUE)
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("📨 Постов",        f"{len(tp_df):,}")
    k2.metric("📊 % от выборки",  f"{len(tp_df)/len(df_f)*100:.1f}%" if len(df_f) else "—")
    k3.metric("😠 Негативных",    f"{(tp_df['llm_sentiment']=='negative').mean()*100:.1f}%" if len(tp_df) else "—")
    k4.metric("⚡ Avg virality",   f"{tp_df['virality_score'].mean():.0f}" if len(tp_df) else "—")

    # ── Сентимент + ключевые слова ─────────────────────────────
    col_tp1, col_tp2 = st.columns([2, 3])
    with col_tp1:
        sc = tp_df["llm_sentiment"].value_counts()
        fig_tp = go.Figure(go.Pie(
            labels=[SENT_RU.get(l,l) for l in sc.index], values=sc.values,
            marker=dict(colors=[SENT_C.get(l,C_MUTED) for l in sc.index],
                        line=dict(color="#ffffff", width=2)),
            textinfo="percent+label",
            textfont=dict(size=13, color="#1e293b"),
            hole=0.5,
        ))
        fig_tp.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=260,
                              margin=dict(t=8,r=8,b=8,l=8), showlegend=False)
        st.plotly_chart(fig_tp, use_container_width=True, config=CFG)

    with col_tp2:
        st.markdown(
            f"<div style='font-size:11px;font-weight:700;color:{C_BLUE};"
            f"text-transform:uppercase;letter-spacing:1px;margin-bottom:12px'>Ключевые слова</div>",
            unsafe_allow_html=True)

        # Используем лемматизированный текст если есть, иначе message_clean
        text_col = "text_lemma" if "text_lemma" in tp_df.columns else (
                   "text_nostop" if "text_nostop" in tp_df.columns else "message_clean")

        STOP = {
            # русские служебные
            "это","что","как","для","при","или","но","да","нет","так","уже","ещё",
            "все","его","они","мне","вас","нас","там","тут","где","когда","если",
            "то","же","не","по","на","с","из","к","о","а","и","у","от","за","со",
            "бы","ли","ни","ну","ой","эй","ах","ух","ведь","вот","тоже","очень",
            "всё","этот","свой","такой","который","можно","нужно","надо","хотеть",
            "быть","иметь","стать","идти","делать","сказать","знать","мочь","сам",
            "один","два","три","год","раз","день","человек","время","рубль",
            # технический мусор
            "nan","none","url","user","http","https","www","com","sdu","edu",
            # казахские служебные
            "бар","жоқ","деп","бол","кел","кет","алу","беру","қой",
        }

        # ── TF-IDF: слова характерные ДЛЯ ЭТОЙ категории ─────
        # Категория = target, остальное = background
        target_texts = tp_df[text_col].dropna().tolist()
        all_texts    = df_f[text_col].dropna().tolist()

        def tokenize(texts):
            result = Counter()
            for t in texts:
                tokens = re.findall(r'\b[а-яёәіңғүұқөһa-z]{3,}\b', str(t).lower())
                result.update(w for w in tokens if w not in STOP)
            return result

        cat_freq = tokenize(target_texts)
        all_freq = tokenize(all_texts)

        N_all = len(all_texts) or 1
        N_cat = len(target_texts) or 1

        # Score = частота в категории / частота во всём корпусе (нормированная)
        # Минимум 3 вхождения в категории
        scored = {}
        for word, cnt in cat_freq.items():
            if cnt < 3: continue
            cat_rate = cnt / N_cat
            all_rate = (all_freq.get(word, 0) + 1) / N_all
            scored[word] = (cat_rate / all_rate, cnt)

        # Топ-18 по distinctiveness
        kws = sorted(scored.items(), key=lambda x: x[1][0], reverse=True)[:18]

        if not kws:
            # Fallback: просто топ по частоте
            kws = [(w, (1.0, c)) for w, c in cat_freq.most_common(18)]

        # Размер шрифта пропорционален score (визуальное облако)
        max_score = kws[0][1][0] if kws else 1
        kw_html = " ".join([
            f"<span style='"
            f"background:#eef2ff;"
            f"border:1.5px solid #c7d2fe;"
            f"border-radius:8px;"
            f"padding:5px 12px;"
            f"margin:3px;"
            f"font-size:{int(11 + min(score/max_score * 5, 5))}px;"
            f"color:#3730a3;"
            f"font-weight:600;"
            f"display:inline-block;cursor:default'>"
            f"{w} <span style='color:{cat_color};font-weight:700'>{cnt}</span></span>"
            for w, (score, cnt) in kws
        ])
        st.markdown(f"<div style='margin-top:4px;line-height:2.4'>{kw_html}</div>",
                    unsafe_allow_html=True)


    # ── Посты с подсвеченным топиком ──────────────────────────
    st.markdown(f"<div class='sec'>Посты в категории «{sel_cat_ru}»</div>", unsafe_allow_html=True)
    c_n, c_sf = st.columns([1, 2])
    n_tp = c_n.slider("Кол-во постов", 5, 50, 15, key="tp_n")
    col_filter_sent = c_sf.multiselect("Фильтр тональности", ["positive","neutral","negative"],
                                        format_func=lambda x: SENT_RU[x],
                                        key="tp_sent_f", placeholder="Все")
    tp_show = tp_df.copy()
    if col_filter_sent:
        tp_show = tp_show[tp_show["llm_sentiment"].isin(col_filter_sent)]
    if sort_tp in tp_show.columns:
        tp_show = tp_show.nlargest(n_tp, sort_tp)
    else:
        tp_show = tp_show.head(n_tp)

    for _, r in tp_show.iterrows():
         post_card(r, key_prefix=f"tp_{sel_cat_en}")

# ═══════════════════════════════════════════════════════════════════════════
# SDU Angime — Улучшенные страницы: SENTIMENT, AI SEARCH, AI INSIGHTS
# Вставь эти блоки в app.py вместо соответствующих elif секций
# ═══════════════════════════════════════════════════════════════════════════
#
# Дополнительные импорты — добавь в начало app.py:
#
#   from groq import Groq
#   from sentence_transformers import SentenceTransformer, util
#
# Groq клиент — добавь после импортов:
#
#   import os
#   GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
#   groq_client  = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
#   MODEL_CHAT   = "groq/compound-mini"
#
# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# ══════════════════ СТРАНИЦА 3: SENTIMENT ══════════════════════
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# ИЗМЕНЕНИЕ 1: SENTIMENT страница — убрать тренд и тональность по отделам
# Новая структура страницы SENTIMENT:
# ═══════════════════════════════════════════════════════════════
#
# УБРАТЬ:
#   - 📈 Тренд тональности по времени (stacked bar)
#   - 🏢 Тональность по отделам (дублирует Overview)
#   - 🏷 Тональность по категориям (переезжает в Topics)
#
# ОСТАВИТЬ И УЛУЧШИТЬ:
#   - KPI метрики (5 штук)
#   - 📅 По семестрам + карточки с дельтой
#   - 🕐 Когда негативно (дни недели + время суток)
#   - 💥 Sentiment × Virality scatter
#   - 🩹 Pain Points + кнопки + посты + AI анализ (улучшить)
# ═══════════════════════════════════════════════════════════════

elif page == "SENTIMENT":
    st.markdown("<div class='page-title'>🎭 Sentiment</div>"
                "<div class='page-sub'>Тональность · Pain Points · Когда · Virality</div>",
                unsafe_allow_html=True)

    if not DATA_OK: st.error("❌ Нет данных."); st.stop()

    # ── KPI ────────────────────────────────────────────────────
    total   = len(df_f)
    pos_pct = (df_f["llm_sentiment"] == "positive").mean() * 100 if total else 0
    neu_pct = (df_f["llm_sentiment"] == "neutral").mean()  * 100 if total else 0
    neg_pct = (df_f["llm_sentiment"] == "negative").mean() * 100 if total else 0
    neg_vir = df_f[df_f["llm_sentiment"] == "negative"]["virality_score"].mean() if total else 0
    pos_vir = df_f[df_f["llm_sentiment"] == "positive"]["virality_score"].mean() if total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("😊 Позитивных",        f"{pos_pct:.1f}%")
    c2.metric("😐 Нейтральных",       f"{neu_pct:.1f}%")
    c3.metric("😠 Негативных",        f"{neg_pct:.1f}%")
    c4.metric("⚡ Virality негатива",  f"{neg_vir:.0f}" if total else "—")
    c5.metric("⚡ Virality позитива",  f"{pos_vir:.0f}" if total else "—",
              delta=f"{pos_vir - neg_vir:+.0f} vs негатив" if total else None)

    st.divider()

    # ── По семестрам + карточки ────────────────────────────────
    st.markdown("<div class='sec'>📅 Тональность по семестрам</div>", unsafe_allow_html=True)
    sg = df_f.groupby(["semester", "llm_sentiment"]).size().reset_index(name="n")
    st_ = df_f.groupby("semester").size().reset_index(name="tot")
    sg  = sg.merge(st_, on="semester")
    sg["pct"] = sg["n"] / sg["tot"] * 100
    sems_sorted = sorted(df_f["semester"].dropna().unique())

    fig_sem = go.Figure()
    for s in ["negative", "neutral", "positive"]:
        sub = sg[sg["llm_sentiment"] == s].set_index("semester").reindex(sems_sorted).reset_index()
        fig_sem.add_trace(go.Bar(
            x=sub["semester"], y=sub["pct"], name=SENT_RU[s],
            marker_color=SENT_C[s],
            hovertemplate=f"{SENT_RU[s]}: %{{y:.1f}}%<extra></extra>",
        ))
    fig_sem.update_layout(barmode="stack", bargap=0.25)
    fig_sem = _pl(fig_sem, 260)
    st.plotly_chart(fig_sem, use_container_width=True, config=CFG)

    # Карточки по семестрам
    if len(sems_sorted) > 0:
        sem_cols = st.columns(len(sems_sorted))
        for i, sem in enumerate(sems_sorted):
            sem_df  = df_f[df_f["semester"] == sem]
            tot_sem = len(sem_df)
            if tot_sem == 0:
                continue
            neg_s = (sem_df["llm_sentiment"] == "negative").mean() * 100
            pos_s = (sem_df["llm_sentiment"] == "positive").mean() * 100
            neu_s = (sem_df["llm_sentiment"] == "neutral").mean()  * 100
            vir_s = sem_df["virality_score"].mean() if "virality_score" in sem_df.columns else 0

            delta_str = ""
            if i > 0:
                prev_df  = df_f[df_f["semester"] == sems_sorted[i - 1]]
                if len(prev_df) > 0:
                    prev_neg = (prev_df["llm_sentiment"] == "negative").mean() * 100
                    diff     = neg_s - prev_neg
                    arrow    = "↑" if diff > 0 else "↓"
                    color    = C_RED if diff > 0 else C_GREEN
                    delta_str = (
                        f"<div style='font-size:11px;color:{color};"
                        f"font-weight:600;margin-top:6px'>"
                        f"{arrow} {diff:+.1f}% негатива vs {sems_sorted[i-1]}</div>"
                    )

            border_c = C_RED if neg_s > 35 else C_ORANGE if neg_s > 25 else C_GREEN
            sem_cols[i].markdown(f"""
            <div style='background:#fff;border:1px solid {C_BORDER};
                        border-top:3px solid {border_c};
                        border-radius:12px;padding:14px 16px;margin-bottom:12px'>
                <div style='font-size:11px;font-weight:700;color:{C_MUTED};
                            text-transform:uppercase;letter-spacing:.8px;
                            margin-bottom:10px'>{sem}</div>
                <div style='display:flex;gap:8px;margin-bottom:8px'>
                    <div style='text-align:center;flex:1;background:#fef2f2;
                                border-radius:8px;padding:8px 4px'>
                        <div style='font-size:22px;font-weight:800;color:{C_RED}'>{neg_s:.0f}%</div>
                        <div style='font-size:10px;color:{C_MUTED}'>😠 Негатив</div>
                    </div>
                    <div style='text-align:center;flex:1;background:#f8fafc;
                                border-radius:8px;padding:8px 4px'>
                        <div style='font-size:22px;font-weight:800;color:{C_MUTED}'>{neu_s:.0f}%</div>
                        <div style='font-size:10px;color:{C_MUTED}'>😐 Нейтрал</div>
                    </div>
                    <div style='text-align:center;flex:1;background:#f0fdf4;
                                border-radius:8px;padding:8px 4px'>
                        <div style='font-size:22px;font-weight:800;color:{C_GREEN}'>{pos_s:.0f}%</div>
                        <div style='font-size:10px;color:{C_MUTED}'>😊 Позитив</div>
                    </div>
                </div>
                <div style='font-size:11px;color:{C_MUTED}'>
                    ⚡ <b style='color:{C_TEXT}'>{vir_s:.0f}</b> avg virality
                    &nbsp;·&nbsp; 📨 {tot_sem:,} постов
                </div>
                {delta_str}
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Когда пишут негативно ──────────────────────────────────
    st.markdown("<div class='sec'>🕐 Когда студенты пишут негативно?</div>",
                unsafe_allow_html=True)
    col_wd, col_tod = st.columns(2)

    with col_wd:
        wd_sent = df_f.groupby(["day_of_week", "llm_sentiment"]).size().reset_index(name="n")
        wd_tot  = df_f.groupby("day_of_week").size().reset_index(name="tot")
        wd_sent = wd_sent.merge(wd_tot, on="day_of_week")
        wd_sent["pct"] = wd_sent["n"] / wd_sent["tot"] * 100
        neg_wd  = (wd_sent[wd_sent["llm_sentiment"] == "negative"]
                   .set_index("day_of_week").reindex(DAYS_ORDER).reset_index())

        fig_wd = go.Figure(go.Bar(
            x=neg_wd["day_of_week"], y=neg_wd["pct"],
            marker_color=[C_RED if v > neg_wd["pct"].mean() else C_MUTED
                          for v in neg_wd["pct"].fillna(0)],
            text=neg_wd["pct"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(size=11, color=C_TEXT),
            hovertemplate="%{x}: %{y:.1f}% негатива<extra></extra>",
        ))
        fig_wd.add_hline(y=neg_wd["pct"].mean(), line_dash="dot",
                         line_color=C_MUTED, line_width=1)
        fig_wd = _pl(fig_wd, 240, ml=20)
        st.plotly_chart(fig_wd, use_container_width=True, config=CFG)

    with col_tod:
        tod_sent = df_f.groupby(["period", "llm_sentiment"]).size().reset_index(name="n")
        tod_tot  = df_f.groupby("period").size().reset_index(name="tot")
        tod_sent = tod_sent.merge(tod_tot, on="period")
        tod_sent["pct"] = tod_sent["n"] / tod_sent["tot"] * 100
        neg_tod  = (tod_sent[tod_sent["llm_sentiment"] == "negative"]
                    .set_index("period").reindex(PERIODS_KK).reset_index())

        fig_tod = go.Figure(go.Bar(
            x=neg_tod["period"], y=neg_tod["pct"],
            marker_color=[C_RED if v > neg_tod["pct"].mean() else C_MUTED
                          for v in neg_tod["pct"].fillna(0)],
            text=neg_tod["pct"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(size=11, color=C_TEXT),
            hovertemplate="%{x}: %{y:.1f}% негатива<extra></extra>",
        ))
        fig_tod.add_hline(y=neg_tod["pct"].mean(), line_dash="dot",
                          line_color=C_MUTED, line_width=1)
        fig_tod = _pl(fig_tod, 240, ml=20)
        st.plotly_chart(fig_tod, use_container_width=True, config=CFG)

    st.divider()


    # ═══════════════════════════════════════════════════════════
    # ИЗМЕНЕНИЕ 5: Pain Points — добавить слайдер кол-ва постов,
    # кнопку "Читать полностью" и AI анализ
    # ═══════════════════════════════════════════════════════════
    st.markdown("<div class='sec'>🩹 Топ Pain Points из негативных постов</div>",
                unsafe_allow_html=True)

    col_pp, col_pp2 = st.columns([2, 1])

    with col_pp:
        if "pain_point" in df_f.columns:
            pain_df = df_f[df_f["pain_point"].notna() & (df_f["llm_sentiment"] == "negative")]
            pc      = pain_df["pain_point"].value_counts().head(20)

            if not pc.empty:
                fig_pp = go.Figure(go.Bar(
                    x=pc.values, y=pc.index, orientation="h",
                    marker=dict(
                        color=[C_RED if i < 5 else C_ORANGE if i < 10 else C_MUTED
                               for i in range(len(pc))],
                    ),
                    text=pc.values, textposition="outside",
                    textfont=dict(color=C_TEXT, size=11),
                    hovertemplate="%{y}: %{x} упоминаний<extra></extra>",
                ))
                fig_pp.update_layout(
                    yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
                    xaxis=dict(showgrid=False),
                )
                fig_pp = _pl(fig_pp, 480, ml=10, mr=60, mb=20)
                st.plotly_chart(fig_pp, use_container_width=True, config=CFG)

                # Кнопки топ-10
                st.markdown(
                    f"<div style='font-size:11px;font-weight:700;color:{C_BLUE};"
                    f"text-transform:uppercase;letter-spacing:1px;"
                    f"margin:14px 0 8px 0'>🔍 Нажми чтобы увидеть посты:</div>",
                    unsafe_allow_html=True
                )

                selected_pain = st.session_state.get("selected_pain", None)
                btn_cols = st.columns(5)
                for j, (pain_txt, cnt) in enumerate(pc.head(10).items()):
                    is_active = selected_pain == pain_txt
                    label     = f"{'✓ ' if is_active else ''}{pain_txt} ({cnt})"
                    if btn_cols[j % 5].button(label, key=f"pain_btn_{j}",
                                              use_container_width=True):
                        st.session_state["selected_pain"] = None if is_active else pain_txt
                        st.rerun()

    with col_pp2:
        st.markdown("<div class='sec'>Топ pain по категории</div>", unsafe_allow_html=True)
        if "pain_point" in df_f.columns and "llm_category" in df_f.columns:
            CAT_EN_MAP = {v: k for k, v in CAT_RU.items()}
            pain_cat_ru = st.selectbox(
                "Категория",
                [CAT_RU.get(c, c) for c in sorted(df_f["llm_category"].dropna().unique())],
                key="pp_cat_sel"
            )
            pain_cat_en = CAT_EN_MAP.get(pain_cat_ru, pain_cat_ru)

            pain_cat_df = df_f[
                (df_f["llm_category"] == pain_cat_en) &
                (df_f["pain_point"].notna()) &
                (df_f["llm_sentiment"] == "negative")
            ]["pain_point"].value_counts().head(10)

            total_cat_neg = len(df_f[
                (df_f["llm_category"] == pain_cat_en) &
                (df_f["llm_sentiment"] == "negative")
            ])
            st.markdown(f"""
            <div style='font-size:11px;color:{C_MUTED};margin-bottom:8px'>
                😠 {total_cat_neg} негативных постов · {pain_cat_ru}
            </div>""", unsafe_allow_html=True)

            # Кнопка AI — только кнопка, результат снизу
            if groq_client:
                ai_cat_key = f"ai_cat_{pain_cat_en}"
                if st.button(
                    f"🤖 AI анализ · {pain_cat_ru}",
                    key=f"ai_cat_btn_{pain_cat_en}",
                    use_container_width=True
                ):
                    cat_top_posts = df_f[
                        (df_f["llm_category"] == pain_cat_en) &
                        (df_f["llm_sentiment"] == "negative")
                    ].nlargest(15, "virality_score")["message_clean"].fillna("").tolist()

                    prompt = (
                        f"Студенты SDU написали {total_cat_neg} негативных постов "
                        f"в категории «{pain_cat_ru}». Топ-{len(cat_top_posts)} по популярности:\n\n" +
                        "\n".join([f"- {t[:200]}" for t in cat_top_posts]) +
                        "\n\nДай анализ (3-4 предложения): "
                        "какие главные проблемы в этой категории и что рекомендуешь руководству?"
                    )
                    with st.spinner("Анализирую…"):
                        try:
                            resp = groq_client.chat.completions.create(
                                model=MODEL_CHAT,
                                max_tokens=350,
                                messages=[
                                    {"role": "system",
                                    "content": "Аналитик постов студентов SDU Университета. Кратко и по делу на русском."},
                                    {"role": "user", "content": prompt}
                                ]
                            )
                            st.session_state[ai_cat_key] = resp.choices[0].message.content
                        except Exception as e:
                            st.error(f"Ошибка: {e}")

            # Список pain points
            selected_pain = st.session_state.get("selected_pain", None)
            for j, (pain_txt, cnt) in enumerate(pain_cat_df.items()):
                is_sel = selected_pain == pain_txt
                bg_c   = "#fde8e8" if is_sel else "#fef2f2"
                fw     = "700" if is_sel else "500"
                prefix = "✓ " if is_sel else ""

                c_txt, c_arrow = st.columns([4, 1])
                c_txt.markdown(f"""
                <div style='background:{bg_c};border-left:3px solid {C_RED};
                            border-radius:8px;padding:10px 14px;margin-bottom:6px'>
                    <div style='font-size:13px;color:{C_TEXT};font-weight:{fw}'>
                        {prefix}{pain_txt}
                    </div>
                    <div style='font-size:11px;color:{C_MUTED};margin-top:3px'>
                        {cnt} упоминаний
                    </div>
                </div>""", unsafe_allow_html=True)

                safe_key = f"cp_{pain_cat_en[:8]}_{j}_{pain_txt[:8]}"
                if c_arrow.button("→", key=safe_key, use_container_width=True):
                    st.session_state["selected_pain"] = None if is_sel else pain_txt
                    st.rerun()

    # ── AI результат — на всю ширину, перед постами ────────────
    _cat_ru = st.session_state.get("pp_cat_sel", "")
    _cat_en = {v: k for k, v in CAT_RU.items()}.get(_cat_ru, "")
    _ai_key = f"ai_cat_{_cat_en}"
    if _cat_en and st.session_state.get(_ai_key):
        st.markdown(f"""
        <div style='background:#fef2f2;border:1px solid #fecaca;
                    border-left:4px solid {C_RED};border-radius:12px;
                    padding:20px 24px;color:{C_TEXT};
                    font-size:14px;line-height:1.9;margin:12px 0 16px 0'>
            <div style='font-size:11px;font-weight:700;color:{C_RED};
                        text-transform:uppercase;letter-spacing:.8px;
                        margin-bottom:10px'>
                🤖 AI анализ · {_cat_ru}
            </div>
            {st.session_state[_ai_key]}
        </div>""", unsafe_allow_html=True)

    # ── Посты по выбранному pain point — на всю ширину ─────────
    selected_pain = st.session_state.get("selected_pain", None)
    if selected_pain and "pain_point" in df_f.columns:
        pain_df_full = df_f[df_f["pain_point"].notna() & (df_f["llm_sentiment"] == "negative")]
        matched_pain = pain_df_full[pain_df_full["pain_point"] == selected_pain].nlargest(20, "virality_score")
        total_pain   = len(matched_pain)

        st.markdown(f"""
        <div style='background:#eef2ff;border:1px solid #c7d2fe;
                    border-radius:10px;padding:12px 16px;margin:0 0 8px 0'>
            <span style='font-size:13px;font-weight:700;color:{C_BLUE}'>
                🩹 «{selected_pain}»
            </span>
            <span style='font-size:11px;color:{C_MUTED};margin-left:8px'>
                {total_pain} постов · по virality
            </span>
        </div>""", unsafe_allow_html=True)

        n_pain_posts = st.slider(
            "Показать постов", 5, min(20, total_pain), 10,
            key="pain_n_posts", label_visibility="collapsed"
        ) if total_pain > 5 else total_pain

        for _, r in matched_pain.head(n_pain_posts).iterrows():
            post_card(r, key_prefix=f"pain_{selected_pain}")


# ═══════════════════════════════════════════════════════════════
# ══════════════════ СТРАНИЦА 4: AI SEARCH ══════════════════════
# ═══════════════════════════════════════════════════════════════
elif page == "AI SEARCH":
    st.markdown("<div class='page-title'>🔍 AI Search</div>"
                "<div class='page-sub'>Поиск по смыслу (Semantic) или точному совпадению (Текстовый)</div>",
                unsafe_allow_html=True)

    EMB_PATH = Path("data/processed/embeddings.npy")
    IDX_PATH = Path("data/processed/embeddings_index.csv")
    real_mode = EMB_PATH.exists() and IDX_PATH.exists()

    @st.cache_resource(show_spinner="⏳ Загружаем модель эмбеддингов…")
    def load_embeddings():
        from sentence_transformers import SentenceTransformer, util as st_util
        model      = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
        embeddings = np.load(str(EMB_PATH))
        emb_index  = pd.read_csv(str(IDX_PATH))
        return model, embeddings, st_util, emb_index

    if real_mode:
        try:
            emb_model, embeddings, st_util, emb_index = load_embeddings()
        except Exception as e:
            real_mode = False
            st.markdown(f"<div class='banner-warn'>⚠ Embeddings не загрузились: {e}</div>",
                        unsafe_allow_html=True)

    # ── Режим поиска ───────────────────────────────────────────
    col_mode, col_k = st.columns([4, 1])
    with col_mode:
        if real_mode:
            search_mode = st.radio(
                "Режим поиска",
                ["Semantic (по смыслу)", "Текстовый (по словам)"],
                horizontal=True, key="search_mode"
            )
        else:
            search_mode = "Текстовый (по словам)"
            st.markdown("<div class='banner-warn'>⚠ embeddings.npy не найден → только Текстовый режим</div>",
                        unsafe_allow_html=True)

    top_k = col_k.number_input("Top-K", 5, 100, 15, 5)

    # ── Поисковая строка ───────────────────────────────────────
    # ✅ Примеры пишут напрямую в search_query
    if "search_query_set" in st.session_state:
        default_query = st.session_state.pop("search_query_set")
    else:
        default_query = st.session_state.get("search_query_val", "")

    query = st.text_input(
        "", placeholder="Введите запрос для поиска: интернет, асхана, стипендия, стресс…",
        label_visibility="collapsed",
        key="search_query_val",
        value=default_query
    )

    # ── Фильтры ────────────────────────────────────────────────
    f1, f2, f3, f4 = st.columns(4)
    CAT_EN = {v: k for k, v in CAT_RU.items()}
    f_sc = f1.multiselect("Категория", [CAT_RU[c] for c in VALID_CATEGORIES],
                           key="s_cat", placeholder="Все")
    f_ss = f2.multiselect("Тональность", ["positive", "neutral", "negative"],
                           format_func=lambda x: SENT_RU[x],
                           key="s_sent", placeholder="Все")
    f_su = f3.multiselect("Приоритет", ["critical", "high", "medium", "low"],
                           format_func=lambda x: URG_RU[x],
                           key="s_urg", placeholder="Все")
    sort_s = f4.selectbox("Сортировка",
                           ["По релевантности", "По virality", "По дате"])

    # ── Пул с фильтрами ────────────────────────────────────────
    pool = df_f[df_f["message_clean"].notna()].copy().reset_index(drop=True)
    if f_sc:
        pool = pool[pool["llm_category"].isin([CAT_EN.get(c, c) for c in f_sc])]
    if f_ss:
        pool = pool[pool["llm_sentiment"].isin(f_ss)]
    if f_su:
        pool = pool[pool["llm_urgency"].isin(f_su)]
    pool = pool.reset_index(drop=True)

    if query.strip():
        with st.spinner("Ищем…"):

            if search_mode == "Semantic (по смыслу)" and real_mode:
                # ── Semantic поиск ─────────────────────────────
                idx_col = "message_id"
                pool_merged = pool.merge(
                    emb_index[[idx_col]].reset_index().rename(columns={"index": "emb_pos"}),
                    on=idx_col, how="inner"
                ).reset_index(drop=True)

                if len(pool_merged) == 0:
                    st.warning("Нет совпадений между пулом и индексом эмбеддингов.")
                    st.stop()

                q_vec    = emb_model.encode([query], normalize_embeddings=True)
                pool_emb = embeddings[pool_merged["emb_pos"].values]
                scores   = st_util.dot_score(q_vec, pool_emb)[0].numpy()
                pool_merged["_score"] = scores
                pool_copy = pool_merged.copy()
                method_label = "🧠 Semantic"

            else:
                # ── Текстовый поиск ────────────────────────────
                words = [w for w in query.lower().split() if len(w) > 1]

                def text_score(text):
                    t = str(text).lower()
                    return sum(t.count(w) for w in words)

                pool_copy = pool.copy()
                pool_copy["_score"] = pool_copy["message_clean"].apply(text_score)
                # Оставляем только где есть хоть одно совпадение
                pool_copy = pool_copy[pool_copy["_score"] > 0]
                method_label = "🔤 Текстовый"

        # ── Сортировка ─────────────────────────────────────────
        if sort_s == "По релевантности":
            result = pool_copy.nlargest(top_k, "_score")
        elif sort_s == "По virality":
            result = pool_copy.nlargest(top_k, "virality_score")
        else:
            result = pool_copy.sort_values("date", ascending=False).head(top_k)

        # ── Счётчик ────────────────────────────────────────────
        st.markdown(
            f"<div style='font-size:13px;color:{C_MUTED};margin-bottom:12px'>"
            f"{method_label} · Найдено "
            f"<b style='color:{C_TEXT}'>{len(result)}</b> постов "
            f"из пула <b style='color:{C_TEXT}'>{len(pool):,}</b></div>",
            unsafe_allow_html=True
        )

        if len(result) == 0:
            st.info("Ничего не найдено. Попробуй другой запрос или режим поиска.")
        else:
            # ── AI интерпретация ───────────────────────────────
            if groq_client and len(result) >= 3:
                with st.expander("🤖 AI интерпретация результатов", expanded=False):
                    ai_search_key = f"ai_search_{query[:30]}"
                    if st.button("Проанализировать найденные посты",
                                 key="search_ai_btn"):
                        top_texts = result.head(10)["message_clean"].fillna("").tolist()
                        with st.spinner("Анализирую…"):
                            try:
                                resp = groq_client.chat.completions.create(
                                    model=MODEL_CHAT, max_tokens=300,
                                    messages=[{"role": "user", "content":
                                        f"Студенты SDU University написали эти посты по теме «{query}»:\n\n" +
                                        "\n".join([f"- {t[:150]}" for t in top_texts]) +
                                        "\n\nКратко (3-4 предложения): суть проблемы и рекомендации для администрации университета касательно этой проблемы?"
                                    }]
                                )
                                st.session_state[ai_search_key] = resp.choices[0].message.content
                            except Exception as e:
                                st.error(f"Ошибка: {e}")

                    if st.session_state.get(ai_search_key):
                        st.markdown(f"""
                        <div style='background:#eef2ff;border:1px solid #c7d2fe;
                                    border-radius:12px;padding:16px 20px;
                                    color:#3730a3;font-size:14px;line-height:1.8'>
                            🤖 {st.session_state[ai_search_key]}
                        </div>""", unsafe_allow_html=True)

            # ── Посты через post_card (цензура работает) ───────
            for _, r in result.iterrows():
                post_card(r, key_prefix="srch")

    else:
        # ── Стартовый экран ────────────────────────────────────
        st.markdown("<div class='sec'>💡 Попробуй эти запросы</div>",
                    unsafe_allow_html=True)

        examples = [
            ("🌐 Интернет / Мудл", "интернет мудл портал"),
            ("🍽 Еда в столовой", "еда асхана дорого"),
            ("💰 Стипендия", "стипендия задержали"),
            ("🥶 Общежитие", "общежитие жатақхана дорм"),
            ("📝 Экзамены",  "экзамен квиз retake"),
            ("🎉 Мероприятия", "велком пати event концерт"),
            ("😔 Психология", "стресс выгорание депрессия"),
            ("🏫 Деканат", "деканат расписание GPA"),
        ]
        cols = st.columns(4)
        for i, (lbl, q) in enumerate(examples):
            if cols[i % 4].button(lbl, key=f"ex_{i}", use_container_width=True):
                # ✅ Записываем через отдельный ключ чтобы не конфликтовать
                st.session_state["search_query_set"] = q
                st.rerun()

        st.divider()

        mode_label = "🧠 Semantic" if (real_mode and st.session_state.get("search_mode","").startswith("🧠")) \
                     else "🔤 Текстовый"
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("📨 Постов в пуле", f"{len(pool):,}")
        k2.metric("🔍 Режим",         mode_label)
        k3.metric("🌐 Языков",
                  pool["language"].nunique() if "language" in pool.columns else "—")
        k4.metric("😠 Негативных",
                  f"{(pool['llm_sentiment'] == 'negative').sum():,}")

# ═══════════════════════════════════════════════════════════════
# ══════════════ СТРАНИЦА 5: AI INSIGHTS & REPORTS ══════════════
# ═══════════════════════════════════════════════════════════════
elif page == "AI INSIGHTS & REPORTS":
    st.markdown("<div class='page-title'>💡 AI Insights & Reports</div>"
                "<div class='page-sub'>Executive Summary · Критичные посты · Spike Explainer · Банк идей</div>",
                unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🚨 Критичные посты", "📈 Spike Explainer", "🛠 Банк Идей", "📄 Executive Summary"]
    )


    # ═══════════════════════════════════════════════════════════
    # TAB 1: КРИТИЧНЫЕ ПОСТЫ
    # ═══════════════════════════════════════════════════════════
    with tab1:
        st.markdown("<div class='sec'>🚨 Критичные и высокоприоритетные посты</div>",
                    unsafe_allow_html=True)

        # ✅ df_crit имеет другие колонки — используем df_f напрямую
        src_crit = df_f[df_f["llm_urgency"].isin(["high", "critical"])] \
           .sort_values("virality_score", ascending=False).copy()

        if src_crit.empty:
            st.info("Нет данных.")
        else:
            c_s1, c_s2, c_s3 = st.columns(3)
            sort_cr = c_s1.selectbox(
                "Сортировать", ["virality_score", "views", "reactions_total"], key="cr_sort"
            )
            # ✅ Без default= — показывает все high+critical
            urg_cr = c_s2.multiselect(
                "Приоритет", ["critical", "high", "medium", "low"],
                format_func=lambda x: URG_RU.get(x, x),
                key="cr_urg", placeholder="Все приоритеты"
            )
            dept_cr = c_s3.multiselect(
                "Отдел",
                sorted(src_crit["responsible_dept"].dropna().unique().tolist())
                if "responsible_dept" in src_crit.columns else [],
                key="cr_dept", placeholder="Все отделы"
            )

            if urg_cr:
                src_crit = src_crit[src_crit["llm_urgency"].isin(urg_cr)]
            if dept_cr:
                src_crit = src_crit[src_crit["responsible_dept"].isin(dept_cr)]
            src_crit = src_crit.nlargest(30, sort_cr) if sort_cr in src_crit.columns \
                       else src_crit.head(30)

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("🔴 Критичных",
                      int((src_crit["llm_urgency"] == "critical").sum())
                      if "llm_urgency" in src_crit.columns else 0)
            k2.metric("🟠 Высоких",
                      int((src_crit["llm_urgency"] == "high").sum())
                      if "llm_urgency" in src_crit.columns else 0)
            k3.metric("⚡ Avg Virality",
                      f"{src_crit['virality_score'].mean():.0f}"
                      if "virality_score" in src_crit.columns else "—")
            k4.metric("🏢 Топ отдел",
                      src_crit["responsible_dept"].dropna().value_counts().index[0]
                      if "responsible_dept" in src_crit.columns and len(src_crit) > 0 else "—")

            if groq_client:
                ai_crit_key = "ai_crit_summary"
                col_l, col_c, col_r = st.columns([2, 3, 2])
                if col_c.button("🤖 AI Summary", key="crit_ai_btn", use_container_width=True):
                    texts = src_crit.head(15)["message_clean"].fillna("").tolist()
                    n_crit = int((src_crit["llm_urgency"] == "critical").sum())
                    n_high = int((src_crit["llm_urgency"] == "high").sum())
                    with st.spinner("Анализирую…"):
                        try:
                            resp = groq_client.chat.completions.create(
                                model=MODEL_CHAT, max_tokens=400,
                                messages=[
                                    {"role": "system",
                                    "content": "Аналитик постов студентов SDU Университета. Кратко и по делу на русском."},
                                    {"role": "user", "content":
                                        f"Критичных постов: {n_crit}, высоких: {n_high}.\n\n"
                                        "Топ посты студентов SDU:\n\n" +
                                        "\n".join([f"- {t[:200]}" for t in texts]) +
                                        "\n\nОтчёт для администрации университета (4-5 предл.): "
                                        "что происходит, какие отделы, что сделать срочно?"
                                    }
                                ]
                            )
                            st.session_state[ai_crit_key] = resp.choices[0].message.content
                        except Exception as e:
                            st.error(f"Ошибка: {e}")

                if st.session_state.get(ai_crit_key):
                    st.markdown(f"""
                    <div style='background:#fef2f2;border:1px solid #fecaca;
                                border-left:4px solid {C_RED};border-radius:12px;
                                padding:16px 20px;color:{C_TEXT};
                                font-size:14px;line-height:1.8;margin-bottom:16px'>
                        🚨 <b>AI анализ:</b><br><br>{st.session_state[ai_crit_key]}
                    </div>""", unsafe_allow_html=True)

            for _, r in src_crit.iterrows():
                post_card(r, key_prefix="crit")
                
                
    # ═══════════════════════════════════════════════════════════
    # TAB 2: SPIKE EXPLAINER — объяснитель сверху, все спайки
    # ═══════════════════════════════════════════════════════════
    with tab2:
        st.markdown("<div class='sec'>📈 Аномалии активности</div>", unsafe_allow_html=True)

        if not DATA_OK:
            st.info("Нет данных.")
        else:
            daily = df_f.groupby("date_day").size().reset_index(name="count")
            daily["date_day"] = pd.to_datetime(daily["date_day"])
            avg_daily = daily["count"].mean()

            spikes_auto = daily[daily["count"] > avg_daily * 2.2].copy()
            spikes_auto["spike_pct"] = (spikes_auto["count"] - avg_daily) / avg_daily * 100
            spikes_auto = spikes_auto.sort_values("count", ascending=False)

            # ── 🤖 Объяснить произвольный день — СВЕРХУ ───────
            if groq_client:
                st.markdown("<div class='sec'>🤖 Объяснить произвольный день</div>",
                            unsafe_allow_html=True)
                col_d1, col_d2, col_d3 = st.columns([2, 2, 1])
                spike_date = col_d1.date_input("Выбери день", key="spike_date_sel")
                col_d3.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
                if col_d2.button("🔍 Объяснить", key="spike_explain_btn",
                                 use_container_width=True):
                    day_str   = spike_date.strftime("%Y-%m-%d")
                    day_posts = df_f[df_f["date_day"] == day_str].nlargest(15, "virality_score")
                    if len(day_posts) == 0:
                        st.warning("В этот день нет постов в текущей выборке.")
                    else:
                        posts_text = "\n- ".join(day_posts["message_clean"].fillna("").tolist()[:12])
                        day_count  = len(day_posts)
                        avg_c      = daily["count"].mean()
                        pct_diff   = (day_count - avg_c) / avg_c * 100
                        with st.spinner("Анализирую…"):
                            try:
                                resp = groq_client.chat.completions.create(
                                    model=MODEL_CHAT, max_tokens=300,
                                    messages=[{"role": "user", "content":
                                        f"В Telegram канале студентов SDU {day_str} было {day_count} постов "
                                        f"({pct_diff:+.0f}% от среднего {avg_c:.0f}/день).\n\n"
                                        f"Топ посты:\n- {posts_text}\n\n"
                                        f"Объясни в 2-3 предложениях: что произошло в этот день?"
                                    }]
                                )
                                st.session_state["spike_day_result"] = (
                                    day_str, day_count, pct_diff,
                                    resp.choices[0].message.content
                                )
                            except Exception as e:
                                st.error(f"Ошибка: {e}")

                if st.session_state.get("spike_day_result"):
                    d_str, d_cnt, d_pct, d_expl = st.session_state["spike_day_result"]
                    color = C_RED if d_pct > 100 else C_ORANGE if d_pct > 50 else C_MUTED
                    st.markdown(f"""
                    <div class="spike-card">
                        <div class="post-meta">
                            📅 <b style="color:{C_TEXT}">{d_str}</b>
                            &nbsp;·&nbsp;
                            <span style="color:{color};font-weight:700">{d_cnt} постов ({d_pct:+.0f}%)</span>
                        </div>
                        <div class="post-text" style="margin-top:8px">🤖 {d_expl}</div>
                    </div>""", unsafe_allow_html=True)

            st.divider()

            # ── График активности ──────────────────────────────
            fig_sp = go.Figure()
            fig_sp.add_trace(go.Scatter(
                x=daily["date_day"], y=daily["count"],
                mode="lines", name="Посты/день",
                line=dict(color=C_BLUE, width=1.5),
                fill="tozeroy", fillcolor=rgba(C_BLUE, 0.09),
                hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y} постов<extra></extra>",
            ))
            fig_sp.add_hline(y=avg_daily, line_dash="dot", line_color=C_MUTED, line_width=1,
                             annotation_text=f"Среднее: {avg_daily:.0f}",
                             annotation_position="right")
            if len(spikes_auto):
                fig_sp.add_trace(go.Scatter(
                    x=spikes_auto["date_day"], y=spikes_auto["count"],
                    mode="markers", name="Spike",
                    marker=dict(color=C_RED, size=12, symbol="star",
                                line=dict(color=C_TEXT, width=1)),
                    hovertemplate="<b>SPIKE +%{text}%</b><br>%{x|%d %b}<extra></extra>",
                    text=spikes_auto["spike_pct"].round(0).astype(int).astype(str),
                ))
            fig_sp = _pl(fig_sp, 280)
            st.plotly_chart(fig_sp, use_container_width=True, config=CFG)

            # ── KPI спайков ────────────────────────────────────
            if len(spikes_auto):
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("📈 Аномальных дней",  len(spikes_auto))
                k2.metric("🔥 Макс. пик",        f"+{spikes_auto['spike_pct'].max():.0f}%")
                k3.metric("📅 Самый активный",
                          spikes_auto.iloc[0]["date_day"].strftime("%d.%m.%Y"))
                k4.metric("📊 Порог аномалии",   f">{avg_daily*2.2:.0f} постов/день")

            st.divider()

            # ── Все аномальные дни ─────────────────────────────
            src_spk = df_spikes if not df_spikes.empty else spikes_auto

            if not src_spk.empty:
                st.markdown(
                    f"<div class='sec'>Все аномальные дни · {len(src_spk)} событий</div>",
                    unsafe_allow_html=True
                )
                # Показываем ВСЕ спайки (не head(8))
                for _, r in src_spk.iterrows():
                    pct  = float(r.get("spike_pct", 0))
                    date = str(r.get("date_day", ""))
                    cnt  = int(r.get("count", 0))
                    expl = str(r.get("explanation", "")) \
                           if pd.notna(r.get("explanation", "")) else None
                    color = C_RED if pct > 150 else C_ORANGE if pct > 75 else C_MUTED
                    st.markdown(f"""
                    <div class="spike-card">
                        <div class="post-meta" style="display:flex;justify-content:space-between">
                            <div>
                                📅 <b style="color:{C_TEXT}">{date}</b>
                                &nbsp;·&nbsp;
                                <span style="color:{color};font-weight:700">
                                    +{pct:.0f}% активности
                                </span>
                                &nbsp;·&nbsp; {cnt} постов
                            </div>
                            <span style="font-size:11px;color:{C_MUTED}">
                                {'🔴 критично' if pct > 150 else '🟠 высокий' if pct > 75 else '🟡 умеренный'}
                            </span>
                        </div>
                        <div class="post-text" style="white-space:pre-wrap;margin-top:8px">
                            {expl if expl and expl not in ('None', 'nan')
                              else f'<span style="color:{C_MUTED};font-style:italic">'
                                   f'Объяснение не сгенерировано — выбери день выше и нажми 🔍 Объяснить</span>'}
                        </div>
                    </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # TAB 3: БАНК ИДЕЙ
    # ═══════════════════════════════════════════════════════════
    with tab3:
        st.markdown("<div class='sec'>🛠 Конструктивные предложения студентов</div>",
                    unsafe_allow_html=True)
 
        src_sugg = df_sugg if not df_sugg.empty else (
            df_f[df_f.get("is_constructive", pd.Series(dtype=bool)) == True]
            [["message_clean", "suggestion", "llm_category", "responsible_dept", "virality_score"]]
            .nlargest(50, "virality_score") if "is_constructive" in df_f.columns else pd.DataFrame()
        )
 
        if src_sugg.empty:
            st.info("Нет конструктивных предложений.")
        else:
            CAT_EN_loc = {v: k for k, v in CAT_RU.items()}
 
            col_f1, col_f2 = st.columns(2)
            depts_sugg = sorted(src_sugg["responsible_dept"].dropna().unique().tolist()) \
                if "responsible_dept" in src_sugg.columns else []
            cats_sugg  = sorted([CAT_RU.get(c, c) for c in
                                  src_sugg["llm_category"].dropna().unique().tolist()]) \
                if "llm_category" in src_sugg.columns else []

            f_dept_s = col_f1.multiselect("🏢 Отдел", depts_sugg,
                                           key="sugg_dept", placeholder="Все отделы")
            f_cat_s  = col_f2.multiselect("🏷 Категория", cats_sugg,
                                           key="sugg_cat", placeholder="Все категории")

            # ✅ OR логика — пост попадает если подходит ПО ЛЮБОМУ из фильтров
            if f_dept_s or f_cat_s:
                cats_en = [CAT_EN_loc.get(c, c) for c in f_cat_s]

                mask_dept = src_sugg["responsible_dept"].isin(f_dept_s) if f_dept_s \
                            else pd.Series(False, index=src_sugg.index)
                mask_cat  = src_sugg["llm_category"].isin(cats_en) if f_cat_s \
                            else pd.Series(False, index=src_sugg.index)

                src_sugg = src_sugg[mask_dept | mask_cat]
 
            # KPI
            ks1, ks2, ks3, ks4 = st.columns(4)
            ks1.metric("💡 Идей всего",        len(src_sugg))
            ks2.metric("🏢 Отделов затронуто", src_sugg["responsible_dept"].nunique()
                       if "responsible_dept" in src_sugg.columns else "—")
            ks3.metric("⚡ Avg virality",        f"{src_sugg['virality_score'].mean():.0f}"
                       if "virality_score" in src_sugg.columns else "—")
            ks4.metric("🔝 Топ отдел",          src_sugg["responsible_dept"].value_counts().index[0]
                       if "responsible_dept" in src_sugg.columns and len(src_sugg) > 0 else "—")
 
            # AI Summary
            if groq_client:
                ai_sugg_key = "ai_sugg_summary"
                col_l, col_c, col_r = st.columns([2, 3, 2])
                if col_c.button("🤖 AI Summary идей студентов",
                                key="sugg_ai_btn", use_container_width=True):
                    suggestions = src_sugg["suggestion"].dropna().head(20).tolist()
                    with st.spinner("Анализирую…"):
                        try:
                            resp = groq_client.chat.completions.create(
                                model=MODEL_CHAT, max_tokens=400,
                                messages=[
                                    {"role": "system",
                                     "content": "Аналитик постов студентов SDU Университета. Кратко и структурированно на русском."},
                                    {"role": "user", "content":
                                        "Студенты SDU предложили улучшения:\n\n" +
                                        "\n".join([f"- {s}" for s in suggestions]) +
                                        "\n\nСгруппируй по темам и напиши отчёт (5-6 предложений): "
                                        "что студенты хотят улучшить в первую очередь?"
                                    }
                                ]
                            )
                            st.session_state[ai_sugg_key] = resp.choices[0].message.content
                        except Exception as e:
                            st.error(f"Ошибка: {e}")
 
                if st.session_state.get(ai_sugg_key):
                    st.markdown(f"""
                    <div style='background:#f0fdf4;border:1px solid #bbf7d0;
                                border-left:4px solid {C_GREEN};border-radius:12px;
                                padding:16px 20px;color:{C_TEXT};
                                font-size:14px;line-height:1.8;margin-bottom:16px'>
                        💡 <b>AI Summary:</b><br><br>{st.session_state[ai_sugg_key]}
                    </div>""", unsafe_allow_html=True)
 
            # Карточки идей с кнопкой читать полностью
            for idx, r in enumerate(src_sugg.head(30).itertuples()):
                sugg      = str(r.suggestion) if pd.notna(r.suggestion) else ""
                cat       = CAT_RU.get(r.llm_category, "") if hasattr(r, "llm_category") else ""
                dept      = str(r.responsible_dept) if pd.notna(r.responsible_dept) else "—" \
                            if hasattr(r, "responsible_dept") else "—"
                vir       = float(r.virality_score) if hasattr(r, "virality_score") else 0
                text_full = str(r.message_clean) if hasattr(r, "message_clean") else ""
                row_id    = str(getattr(r, "message_id", abs(hash(text_full[:30]))))
                state_key = f"sugg_{row_id}_expanded"
                is_exp    = st.session_state.get(state_key, False)
                text_show = text_full if is_exp else (
                    (text_full[:280] + "…") if len(text_full) > 280 else text_full
                )
 
                st.markdown(f"""
                <div class="post-card" style="border-left:3px solid {C_GREEN}">
                    <div class="post-meta">
                        💡 <b style="color:{C_GREEN}">Предложение</b>
                        &nbsp;·&nbsp; {cat} · 🏢 {dept} · ⚡ {vir:.0f}
                    </div>
                    <div class="post-text">{text_show}</div>
                    {f'<div style="margin-top:10px;padding:10px 14px;background:#f0fdf4;'
                      f'border-radius:8px;font-size:13px;color:{C_GREEN};font-weight:500">'
                      f'→ {sugg}</div>' if sugg and sugg != 'nan' else ''}
                </div>""", unsafe_allow_html=True)
 
                if len(text_full) > 280:
                    btn_label = "▲ Свернуть" if is_exp else "▼ Читать полностью"
                    if st.button(btn_label, key=f"btn_{state_key}"):
                        st.session_state[state_key] = not is_exp
                        st.rerun()
    # ═══════════════════════════════════════════════════════════
    # TAB 4: EXECUTIVE SUMMARY — расширенный фокус + категории
    # ═══════════════════════════════════════════════════════════
    with tab4:
        st.markdown("<div class='sec'>📄 Executive Summary для руководства</div>",
                    unsafe_allow_html=True)

        SUMM_PATH = Path("data/analyzed/executive_summary.txt")
        if SUMM_PATH.exists():
            with open(SUMM_PATH, encoding="utf-8") as f:
                txt = f.read()
            st.markdown(f"""
            <div style='background:{C_CARD};border:1px solid {C_BORDER};border-radius:14px;
                        padding:26px;color:{C_TEXT};font-size:15px;line-height:1.85;
                        white-space:pre-wrap'>{txt}</div>""", unsafe_allow_html=True)
            st.divider()

        if DATA_OK:
            # ── Быстрая статистика ─────────────────────────────
            neg_p   = (df_f["llm_sentiment"] == "negative").mean() * 100
            crit_n  = int((df_f["llm_urgency"] == "critical").sum())
            high_n  = int((df_f["llm_urgency"] == "high").sum())
            top_c   = df_f["llm_category"].value_counts().index[0] if len(df_f) else "—"
            top_d   = df_f["responsible_dept"].dropna().value_counts()
            top_d_n = top_d.index[0] if len(top_d) else "—"
            ideas   = int(df_f["is_constructive"].sum()) if "is_constructive" in df_f.columns else 0

            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("🚨 Critical",  crit_n)
            k2.metric("🔴 High",      high_n)
            k3.metric("😠 Негатив",   f"{neg_p:.1f}%")
            k4.metric("💡 Идеи",      ideas)
            k5.metric("📨 Всего",     f"{len(df_f):,}")

            st.divider()

        # ── AI Executive Summary ───────────────────────────────
        if groq_client and DATA_OK:
            st.markdown("<div class='sec'>🤖 AI Executive Summary</div>", unsafe_allow_html=True)

            col_opt1, col_opt2, col_opt3 = st.columns(3)

            # ✅ Расширенный список фокусов включая категории
            focus_options = [
                "📊 Общий обзор",
                "🚨 Критичные проблемы",
                "🏫 Учёба и экзамены",
                "🍽 Еда и столовая (AC Catering)",
                "🏠 Общежитие",
                "🌐 IT инфраструктура и Moodle",
                "💰 Стипендии и финансы",
                "👩‍🏫 Преподаватели",
                "😔 Психологический климат",
                "🏢 Администрация и Деканат",
                "💼 Карьера и трудоустройство",
                "💡 Конструктивные идеи студентов",
                "📅 Анализ по семестрам",
                "🔥 Топ вирусных постов",
            ]
            summary_focus = col_opt1.selectbox(
                "Фокус отчёта", focus_options, key="summ_focus"
            )
            summary_len = col_opt2.select_slider(
                "Длина",
                ["Кратко (3 предл.)", "Средний (5-6 предл.)", "Детальный (8-10 предл.)"],
                value="Средний (5-6 предл.)",
                key="summ_len"
            )
            summary_lang = col_opt3.selectbox(
                "Язык отчёта", ["Русский", "Казахский", "English"],
                key="summ_lang"
            )

            if st.button("📝 Сгенерировать Executive Summary",
                         key="exec_summ_btn", use_container_width=True):

                len_map = {
                    "Кратко (3 предл.)":       "3 предложения",
                    "Средний (5-6 предл.)":    "5-6 предложений",
                    "Детальный (8-10 предл.)": "8-10 предложений, структурированно"
                }
                lang_map = {
                    "Русский": "строго на русском языке",
                    "Казахский": "строго на казахском языке (қазақша)",
                    "English": "strictly in English"
                }

                # Собираем расширенный контекст
                neg_pct_f   = (df_f["llm_sentiment"] == "negative").mean() * 100
                pos_pct_f   = (df_f["llm_sentiment"] == "positive").mean() * 100
                crit_f      = int((df_f["llm_urgency"] == "critical").sum())
                high_f      = int((df_f["llm_urgency"] == "high").sum())
                top_cats_f  = df_f["llm_category"].value_counts().head(5).to_dict()
                top_dept_f  = df_f["responsible_dept"].dropna().value_counts().head(5).to_dict()
                top_pain_f  = df_f["pain_point"].dropna().value_counts().head(10).to_dict() \
                              if "pain_point" in df_f.columns else {}
                top_posts   = df_f.nlargest(8, "virality_score")["message_clean"].fillna("").tolist()
                sem_stats   = df_f.groupby("semester")["llm_sentiment"].apply(
                    lambda x: (x == "negative").mean() * 100
                ).round(1).to_dict() if "semester" in df_f.columns else {}
                ideas_f     = int(df_f["is_constructive"].sum()) \
                              if "is_constructive" in df_f.columns else 0

                # Специфический контекст по фокусу
                focus_context = ""
                focus_lower   = summary_focus.lower()
                if "еда" in focus_lower or "catering" in focus_lower:
                    food_df = df_f[df_f["llm_category"] == "food"]
                    food_neg = (food_df["llm_sentiment"] == "negative").mean() * 100 if len(food_df) else 0
                    food_pain = food_df["pain_point"].dropna().value_counts().head(5).to_dict() \
                                if "pain_point" in food_df.columns else {}
                    focus_context = f"\nДетали по еде: {len(food_df)} постов, {food_neg:.0f}% негатива. Боли: {food_pain}"
                elif "общеж" in focus_lower:
                    dorm_df = df_f[df_f["llm_category"] == "dorms"]
                    dorm_neg = (dorm_df["llm_sentiment"] == "negative").mean() * 100 if len(dorm_df) else 0
                    focus_context = f"\nДетали по общежитию: {len(dorm_df)} постов, {dorm_neg:.0f}% негатива."
                elif "it" in focus_lower or "moodle" in focus_lower or "инфра" in focus_lower:
                    it_df = df_f[df_f["llm_category"] == "infrastructure"]
                    it_neg = (it_df["llm_sentiment"] == "negative").mean() * 100 if len(it_df) else 0
                    focus_context = f"\nДетали по IT/Moodle: {len(it_df)} постов, {it_neg:.0f}% негатива."
                elif "стипенд" in focus_lower or "финанс" in focus_lower:
                    sch_df = df_f[df_f["llm_category"] == "scholarship"]
                    sch_neg = (sch_df["llm_sentiment"] == "negative").mean() * 100 if len(sch_df) else 0
                    focus_context = f"\nДетали по стипендиям: {len(sch_df)} постов, {sch_neg:.0f}% негатива."
                elif "преподав" in focus_lower:
                    tch_df = df_f[df_f["llm_category"] == "teachers"]
                    tch_neg = (tch_df["llm_sentiment"] == "negative").mean() * 100 if len(tch_df) else 0
                    focus_context = f"\nДетали по преподавателям: {len(tch_df)} постов, {tch_neg:.0f}% негатива."
                elif "семестр" in focus_lower:
                    focus_context = f"\nСтатистика по семестрам (% негатива): {sem_stats}"
                elif "идеи" in focus_lower or "конструктив" in focus_lower:
                    top_sugg = df_f["suggestion"].dropna().head(10).tolist() \
                               if "suggestion" in df_f.columns else []
                    focus_context = f"\nТоп предложений студентов: {top_sugg}"

                with st.spinner("Генерирую Executive Summary…"):
                    try:
                        resp = groq_client.chat.completions.create(
                            model=MODEL_CHAT, max_tokens=700,
                            messages=[
                                {"role": "system",
                                 "content": f"Ты старший аналитик данных SDU (Казахстан). "
                                            f"Пиши {lang_map[summary_lang]}."},
                                {"role": "user", "content":
                                    f"Данные Telegram канала SDU Angime ({len(df_f):,} постов):\n"
                                    f"- Негативных: {neg_pct_f:.1f}%, Позитивных: {pos_pct_f:.1f}%\n"
                                    f"- Критичных: {crit_f}, Высоких: {high_f}\n"
                                    f"- Идей студентов: {ideas_f}\n"
                                    f"- Топ категории: {top_cats_f}\n"
                                    f"- Топ отделы: {top_dept_f}\n"
                                    f"- Главные боли: {top_pain_f}"
                                    f"{focus_context}\n\n"
                                    f"Самые резонансные посты:\n" +
                                    "\n".join([f"- {t[:180]}" for t in top_posts]) +
                                    f"\n\nФокус: {summary_focus}\n"
                                    f"Напиши Executive Summary ({len_map[summary_len]}) для администрации университета.\n"
                                    f"Называй конкретные отделы, % и рекомендации. "
                                    f"Используй структуру: Ситуация → Проблемы → Рекомендации по решению."
                                }
                            ]
                        )
                        st.session_state["exec_summary_text"]   = resp.choices[0].message.content
                        st.session_state["exec_summary_focus"]  = summary_focus
                        st.session_state["exec_summary_lang"]   = summary_lang
                    except Exception as e:
                        st.error(f"Ошибка: {e}")

            if st.session_state.get("exec_summary_text"):
                summary_text  = st.session_state["exec_summary_text"]
                summary_focus = st.session_state.get("exec_summary_focus", "—")
                summary_lang  = st.session_state.get("exec_summary_lang", "Русский")

                st.markdown(f"""
                <div style='background:{C_CARD};border:1px solid {C_BORDER};
                            border-left:4px solid {C_BLUE};border-radius:14px;
                            padding:26px;color:{C_TEXT};font-size:15px;
                            line-height:1.9;white-space:pre-wrap;margin-bottom:12px'>
                    <div style='font-size:11px;color:{C_MUTED};margin-bottom:14px;
                                text-transform:uppercase;letter-spacing:.8px'>
                        🤖 AI · {summary_focus} · {summary_lang} · {len(df_f):,} постов
                    </div>
                    {summary_text}
                </div>""", unsafe_allow_html=True)

                c_dl1, c_dl2 = st.columns(2)
                c_dl1.download_button(
                    "💾 Скачать .txt",
                    data=summary_text,
                    file_name=f"sdu_summary_{summary_focus[:20].replace(' ','_')}.txt",
                    mime="text/plain",
                    key="download_summary"
                )
                if c_dl2.button("🔄 Сбросить", key="reset_summary"):
                    st.session_state.pop("exec_summary_text", None)
                    st.rerun()

        # ── Два доната рядом ──────────────────────────────────
        if DATA_OK:
            st.divider()
            st.markdown("<div class='sec'>📊 Итоговые показатели выборки</div>",
                        unsafe_allow_html=True)
            col_do, col_urg = st.columns(2)
            with col_do:
                sent_c = df_f["llm_sentiment"].value_counts()
                fig_s  = go.Figure(go.Pie(
                    labels=[SENT_RU.get(s, s) for s in sent_c.index],
                    values=sent_c.values,
                    marker=dict(colors=[SENT_C.get(s, C_MUTED) for s in sent_c.index],
                                line=dict(color=C_BG, width=2)),
                    hole=0.6, textinfo="label+percent",
                    textfont=dict(size=12, color=C_TEXT),
                ))
                fig_s.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=280,
                                    margin=dict(t=10, r=10, b=10, l=10), showlegend=False)
                st.plotly_chart(fig_s, use_container_width=True, config=CFG)

            with col_urg:
                urg_c  = df_f["llm_urgency"].value_counts()
                fig_u  = go.Figure(go.Pie(
                    labels=[URG_RU.get(u, u) for u in urg_c.index],
                    values=urg_c.values,
                    marker=dict(colors=[URG_C.get(u, C_MUTED) for u in urg_c.index],
                                line=dict(color=C_BG, width=2)),
                    hole=0.6, textinfo="label+percent",
                    textfont=dict(size=12, color=C_TEXT),
                ))
                fig_u.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=280,
                                    margin=dict(t=10, r=10, b=10, l=10), showlegend=False)
                st.plotly_chart(fig_u, use_container_width=True, config=CFG)