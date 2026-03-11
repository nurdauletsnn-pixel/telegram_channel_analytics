import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter
import re
from groq import Groq
from dotenv import load_dotenv
load_dotenv()  
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
groq_client  = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
MODEL_CHAT   = "compound-beta-mini" 

st.set_page_config(
    page_title="SDU Angime Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
LANG_RU  = {"ru": "Русский", "kk": "Казахский", "mixed_kk_ru": "Смешанный",
             "en": "Английский", "unknown": "Неизвестный"}

# Цвета — светлая тема (white + indigo sidebar)
C_BG   = "#f4f6fb"; C_CARD = "#ffffff"; C_BORDER = "#e2e8f0"
C_TEXT = "#1e293b"; C_MUTED = "#94a3b8"
C_BLUE = "#6366f1"; C_GREEN = "#16a34a"; C_RED = "#dc2626"
C_ORANGE = "#ea580c"; C_YELLOW = "#ca8a04"; C_PURPLE = "#7c3aed"

def rgba(hex_color: str, alpha: float) -> str:
    """Convert #rrggbb to rgba(r,g,b,alpha) — Plotly не принимает 8-символьный hex"""
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

# Дни недели — точно как в ноутбуке (казахские названия)
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

# Время суток — точно как в ноутбуке (get_day_period)
PERIODS_KK = ["Таң", "Түс", "Кеш", "Түн"]   # Таң=06-12, Түс=12-18, Кеш=18-24, Түн=00-06

VALID_DEPARTMENTS = [
    "Деканат", "Общежитие", "Административный отдел",
    "IT департамент", "Финансовый отдел", "AC Catering",
    "Служба безопасности", "Библиотека"
]
VALID_CATEGORIES = list(CAT_RU.keys())

# ═══════════════════════════════════════════════════════════════
# ЗАГРУЗКА ДАННЫХ
# ═══════════════════════════════════════════════════════════════
BASE = "data/analyzed"

@st.cache_data(ttl=300, show_spinner=False)
def load_data():
    paths = {
        "main":        f"{BASE}/classified_posts.csv",
        "suggestions": f"{BASE}/student_suggestions.csv",
        "critical":    f"{BASE}/critical_posts.csv",
        "spikes":      f"{BASE}/spike_explanations.csv",
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
        df["date_day"]       = df["date"].dt.strftime("%Y-%m-%d")
        df["month_str"]      = df["date"].dt.strftime("%Y-%m")
        df["year"]           = df["date"].dt.year
        df["month"]          = df["date"].dt.month
        df["week_num"]       = df["date"].dt.isocalendar().week.astype(int)
        df["day_of_week_num"] = df["date"].dt.weekday          # 0=Пн … 6=Вс
        # Казахские названия — точно как в ноутбуке
        df["day_of_week"]    = df["day_of_week_num"].map(DAYS_MAP)
        if "hour" not in df.columns:
            df["hour"] = df["date"].dt.hour

        # Период суток — точно как get_day_period() в ноутбуке
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
df        = data["main"]
df_sugg   = data["suggestions"]
df_crit   = data["critical"]
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
    logo_path = Path("photo_2026-03-12 02.06.08.jpeg")
    if logo_path.exists():
        st.image(str(logo_path), width=140)
    else:
        st.markdown("### 🎓 SDU Angime")

    if DATA_OK:
        dmin = df["date"].min().date()
        dmax = df["date"].max().date()
        st.markdown(f"<div style='font-size:11px;color:{C_MUTED};margin-bottom:12px'>"
                    f"📅 Данные: {dmin} → {dmax} · {len(df):,} постов</div>",
                    unsafe_allow_html=True)

    # ── Временные фильтры ────────────────────────────────────
    with st.expander("📅 Временные фильтры", expanded=True):
        if DATA_OK:
            st.date_input("Период", value=(dmin, dmax),
                          min_value=dmin, max_value=dmax, key="f_date",
                          label_visibility="collapsed")
            sems_all = sorted(df["semester"].dropna().unique().tolist(), reverse=True)
            st.multiselect("Семестр", sems_all, key="f_sems", placeholder="Все семестры")
        st.multiselect("Месяц", list(range(1,13)),
                        format_func=lambda m: ["Янв","Фев","Мар","Апр","Май","Июн",
                                                "Июл","Авг","Сен","Окт","Ноя","Дек"][m-1],
                        key="f_months", placeholder="Все месяцы")
        st.multiselect("Күн", DAYS_ORDER, key="f_days", placeholder="Барлық күндер")
        st.multiselect("Тәулік мезгілі", PERIODS_KK,
                        format_func=lambda p: {
                            "Таң": "🌅 Таң (06–12)",
                            "Түс": "☀️ Түс (12–18)",
                            "Кеш": "🌆 Кеш (18–24)",
                            "Түн": "🌙 Түн (00–06)",
                        }.get(p, p),
                        key="f_time", placeholder="Кез келген уақыт")

    # ── Тематика ─────────────────────────────────────────────
    st.markdown("### Тематика")
    st.multiselect("Департамент", VALID_DEPARTMENTS,
                    key="f_depts", placeholder="Все департаменты")
    st.multiselect("Категория",
                    [CAT_RU[c] for c in VALID_CATEGORIES],
                    key="_cats_ru", placeholder="Все категории")
    # конвертируем обратно в английские ключи
    CAT_EN = {v: k for k, v in CAT_RU.items()}
    st.session_state["f_cats"] = [CAT_EN.get(c, c)
                                   for c in st.session_state.get("_cats_ru", [])]

    # ── Статус ───────────────────────────────────────────────
    st.markdown("### Статус")
    st.multiselect("Срочность", ["critical","high","medium","low"],
                    format_func=lambda x: URG_RU.get(x, x),
                    key="f_urgency", placeholder="Любая срочность")
    st.multiselect("Тональность", ["positive","neutral","negative"],
                    format_func=lambda x: SENT_RU.get(x, x),
                    key="f_sentiment", placeholder="Любая тональность")
    st.toggle("💡 Только конструктивные предложения", key="f_constructive")

    st.divider()
    page = st.radio("", ["OVERVIEW", "TOPICS", "SENTIMENT",
                          "AI SEARCH", "AI INSIGHTS & REPORTS"],
                     label_visibility="collapsed", key="nav")

# ═══════════════════════════════════════════════════════════════
# ПРИМЕНЯЕМ ФИЛЬТР
# ═══════════════════════════════════════════════════════════════
df_f = apply_filters(df) if DATA_OK else pd.DataFrame()

# Иконки
URG_ICO  = {"low":"🟢","medium":"🟡","high":"🟠","critical":"🔴"}
SENT_ICO = {"positive":"😊","neutral":"😐","negative":"😠"}

def post_card(row, border_col=None):
    urg   = row.get("llm_urgency","low")
    sent  = row.get("llm_sentiment","neutral")
    cat   = CAT_RU.get(row.get("llm_category",""), row.get("llm_category",""))
    dept  = str(row.get("responsible_dept","")) if pd.notna(row.get("responsible_dept","")) else "—"
    vir   = float(row.get("virality_score",0))
    views = int(row.get("views",0)) if pd.notna(row.get("views",0)) else 0
    text  = str(row.get("message_clean",""))
    text  = (text[:290] + "…") if len(text) > 290 else text
    bc    = border_col or URG_C.get(urg, C_MUTED)
    return f"""
    <div class="post-card" style="border-left:3px solid {bc}">
        <div class="post-meta">
            {URG_ICO.get(urg,'')}
            <span class="badge b-{urg}">{URG_RU.get(urg,urg)}</span>
            <span class="badge b-{sent}">{SENT_ICO.get(sent,'')} {SENT_RU.get(sent,sent)}</span>
            <b style="color:#6b8fb8">{cat}</b> · 🏢 {dept} · 👁 {views:,} · ⚡ {vir:.0f}
        </div>
        <div class="post-text">{text}</div>
    </div>"""

# ═══════════════════════════════════════════════════════════════
# ══════════════════ СТРАНИЦА 1: OVERVIEW ═══════════════════════
# ═══════════════════════════════════════════════════════════════
if page == "OVERVIEW":
    dmin_s = df["date"].min().strftime("%d.%m.%Y") if DATA_OK else "—"
    dmax_s = df["date"].max().strftime("%d.%m.%Y") if DATA_OK else "—"
    st.markdown(f"<div class='page-title'>📊 Пульс SDU</div>"
                f"<div class='page-sub'>Данные с {dmin_s} по {dmax_s} · {len(df_f):,} постов в выборке</div>",
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
        st.markdown(post_card(r), unsafe_allow_html=True)

    st.divider()

    # ── Упоминания по департаментам — stacked по срочности ────
    st.markdown("<div class='sec'>🏢 Упоминания по департаментам</div>", unsafe_allow_html=True)

    # Спокойная пастельная палитра по срочности
    URG_CALM = {
        "low":      "#a8d5ba",   # мятный
        "medium":   "#aec6e8",   # пыльно-голубой
        "high":     "#f0c27f",   # персиковый
        "critical": "#e8a0a0",   # пудровый красный
    }

    top_depts = (df_f["responsible_dept"].dropna()
                 .value_counts().head(8).index.tolist())
    dept_urg  = (df_f[df_f["responsible_dept"].isin(top_depts)]
                 .groupby(["responsible_dept","llm_urgency"])
                 .size().reset_index(name="n"))
    dept_total = dept_urg.groupby("responsible_dept")["n"].sum()
    dept_order = dept_total.sort_values(ascending=True).index.tolist()

    # График на всю ширину
    if True:
        fig_dept = go.Figure()
        for urg in ["low", "medium", "high", "critical"]:
            sub = (dept_urg[dept_urg["llm_urgency"] == urg]
                   .set_index("responsible_dept")
                   .reindex(dept_order, fill_value=0)
                   .reset_index())
            fig_dept.add_trace(go.Bar(
                x=sub["n"],
                y=sub["responsible_dept"],
                name=URG_RU.get(urg, urg),
                orientation="h",
                marker=dict(color=URG_CALM[urg], line=dict(width=0)),
                hovertemplate=f"<b>%{{y}}</b><br>{URG_RU.get(urg,'')}: %{{x}}<extra></extra>",
            ))
        fig_dept.update_layout(
            barmode="stack",
            yaxis=dict(gridcolor="rgba(0,0,0,0)",
                       tickfont=dict(size=12, color="#334155")),
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9",
                       tickfont=dict(color="#94a3b8")),
            legend=dict(
                orientation="h", y=-0.18, x=0.5, xanchor="center",
                font=dict(size=12, color="#475569"),
                bgcolor="rgba(0,0,0,0)", borderwidth=0,
            ),
            bargap=0.35,
        )
        fig_dept = _pl(fig_dept, 340, ml=10, mr=20, mb=50)
        st.plotly_chart(fig_dept, use_container_width=True, config=CFG)

    # ── Карточки отделов снизу — все уровни срочности ─────────
    card_cols = st.columns(4)
    for i, dept in enumerate(reversed(dept_order)):
        total_d = int(dept_total.get(dept, 0))
        bar_w   = int(total_d / dept_total.max() * 100)

        # Кол-во по каждой срочности
        urg_counts = {urg: int(dept_urg[
            (dept_urg["responsible_dept"]==dept) &
            (dept_urg["llm_urgency"]==urg)]["n"].sum())
            for urg in ["low","medium","high","critical"]}

        badges = "".join([
            f"<span style='background:{URG_CALM[u]};color:#334155;"
            f"border-radius:5px;padding:2px 7px;font-size:11px;"
            f"font-weight:600;margin-right:4px'>"
            f"{URG_RU[u][0]} {urg_counts[u]}</span>"
            for u in ["low","medium","high","critical"] if urg_counts[u] > 0
        ])

        card_cols[i % 4].markdown(f"""
        <div style='padding:14px 16px;background:#ffffff;
                    border:1px solid #e8eef6;border-radius:12px;
                    box-shadow:0 1px 4px rgba(0,0,0,0.05);margin-bottom:12px'>
            <div style='font-size:12px;font-weight:700;color:#1e1b4b;
                        margin-bottom:8px'>{dept}</div>
            <div style='font-size:22px;font-weight:800;color:#1e1b4b;
                        margin-bottom:6px'>{total_d:,}</div>
            <div style='margin-bottom:8px'>{badges}</div>
            <div style='background:#f1f5f9;border-radius:4px;height:4px'>
                <div style='background:#aec6e8;width:{bar_w}%;
                            height:4px;border-radius:4px'></div>
            </div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# ══════════════════ СТРАНИЦА 2: TOPICS ═════════════════════════
# ═══════════════════════════════════════════════════════════════
elif page == "TOPICS":
    st.markdown("<div class='page-title'>🌌 Topics</div>"
                "<div class='page-sub'>Структура тем, динамика и детализация по топикам</div>",
                unsafe_allow_html=True)

    if not DATA_OK:
        st.error("❌ Нет данных."); st.stop()

    # ── Только горизонтальный бар на всю ширину ───────────────
    st.markdown("<div class='sec'>📊 Распределение категорий</div>", unsafe_allow_html=True)
    cat_c = df_f["llm_category"].value_counts().reset_index()
    cat_c.columns = ["cat","n"]
    cat_c["pct"]    = cat_c["n"] / len(df_f) * 100
    cat_c["cat_ru"] = cat_c["cat"].map(CAT_RU).fillna(cat_c["cat"])
    cat_c["color"]  = cat_c["cat"].map(CAT_C).fillna(C_MUTED)

    # Высота зависит от кол-ва категорий — 40px на строку, минимум 400
    bar_h = max(400, len(cat_c) * 42)
    fig_cbar = go.Figure(go.Bar(
        x=cat_c["n"], y=cat_c["cat_ru"], orientation="h",
        marker_color=cat_c["color"].tolist(),
        text=[f"  {r['n']}  ({r['pct']:.1f}%)" for _, r in cat_c.iterrows()],
        textposition="outside", textfont=dict(color=C_TEXT, size=12, family="Golos Text, sans-serif"),
        hovertemplate="<b>%{y}</b><br>%{x} постов<extra></extra>",
    ))
    fig_cbar.update_layout(
        yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)",
                   tickfont=dict(size=13, color=C_TEXT)),
        xaxis=dict(showgrid=False),
    )
    fig_cbar = _pl(fig_cbar, bar_h, ml=10, mr=140, mb=20)
    st.plotly_chart(fig_cbar, use_container_width=True, config=CFG)

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
        urg   = r.get("llm_urgency","low")
        sent  = r.get("llm_sentiment","neutral")
        dept  = str(r.get("responsible_dept","")) if pd.notna(r.get("responsible_dept","")) else "—"
        vir   = float(r.get("virality_score",0))
        views = int(r.get("views",0)) if pd.notna(r.get("views",0)) else 0
        text  = str(r.get("message_clean",""))
        text  = (text[:290] + "…") if len(text) > 290 else text
        # Топик — яркая цветная плашка
        topic_val = str(r.get("llm_topic","")) if pd.notna(r.get("llm_topic","")) else ""
        topic_badge = (
            f"<span style='background:{cat_color};color:#fff;border-radius:6px;"
            f"padding:3px 10px;font-size:11px;font-weight:700;margin-right:6px;"
            f"letter-spacing:.3px'>🏷 {topic_val}</span>"
            if topic_val and topic_val not in ("nan","None","") else ""
        )
        urg_c = URG_C.get(urg, C_MUTED)
        st.markdown(f"""
        <div class="post-card" style="border-left:3px solid {urg_c}">
            <div class="post-meta" style="margin-bottom:9px">
                {URG_ICO.get(urg,'')}
                <span class="badge b-{urg}">{URG_RU.get(urg,urg)}</span>
                <span class="badge b-{sent}">{SENT_ICO.get(sent,'')} {SENT_RU.get(sent,sent)}</span>
                {topic_badge}
                🏢 {dept} · 👁 {views:,} · ⚡ {vir:.0f}
            </div>
            <div class="post-text">{text}</div>
        </div>""", unsafe_allow_html=True)

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
elif page == "SENTIMENT":
    st.markdown("<div class='page-title'>🎭 Sentiment</div>"
                "<div class='page-sub'>Тональность · Pain Points · Отделы · Virality</div>",
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
    c1.metric("😊 Позитивных",         f"{pos_pct:.1f}%")
    c2.metric("😐 Нейтральных",        f"{neu_pct:.1f}%")
    c3.metric("😠 Негативных",         f"{neg_pct:.1f}%")
    c4.metric("⚡ Virality негатива",   f"{neg_vir:.0f}" if total else "—")
    c5.metric("⚡ Virality позитива",   f"{pos_vir:.0f}" if total else "—",
              delta=f"{pos_vir - neg_vir:+.0f} vs негатив" if total else None)

    st.divider()

    # ── Тренд + Donut рядом ────────────────────────────────────
    col_tr, col_do = st.columns([3, 1])

    with col_tr:
        st.markdown("<div class='sec'>📈 Тренд тональности по времени</div>",
                    unsafe_allow_html=True)
        f_map = {"Недели": "W", "Месяцы": "M", "Кварталы": "Q"}
        f_ch  = st.select_slider("", list(f_map.keys()), value="Месяцы",
                                   label_visibility="collapsed", key="sent_tr")
        ts3 = df_f.copy()
        ts3["period"] = ts3["date"].dt.to_period(f_map[f_ch]).dt.to_timestamp()
        g3  = ts3.groupby(["period", "llm_sentiment"]).size().unstack(fill_value=0)
        t3  = g3.sum(axis=1)
        p3  = g3.divide(t3, axis=0) * 100

        fig_tr = go.Figure()
        for s in ["negative", "neutral", "positive"]:
            if s in p3.columns:
                fig_tr.add_trace(go.Bar(
                    x=p3.index, y=p3[s], name=SENT_RU[s],
                    marker_color=SENT_C[s],
                    hovertemplate=f"{SENT_RU[s]}: %{{y:.1f}}%<extra></extra>",
                ))
        fig_tr.update_layout(barmode="stack", bargap=0.12)
        fig_tr = _pl(fig_tr, 280)
        st.plotly_chart(fig_tr, use_container_width=True, config=CFG)

    with col_do:
        st.markdown("<div class='sec'>Общее</div>", unsafe_allow_html=True)
        sc_do = df_f["llm_sentiment"].value_counts()
        fig_do = go.Figure(go.Pie(
            labels=[SENT_RU.get(l, l) for l in sc_do.index],
            values=sc_do.values,
            marker=dict(colors=[SENT_C.get(l, C_MUTED) for l in sc_do.index],
                        line=dict(color="#ffffff", width=3)),
            textinfo="percent",
            textfont=dict(size=13, color="#1e293b"),
            hole=0.62,
        ))
        fig_do.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=280,
                              margin=dict(t=8, r=8, b=8, l=8),
                              showlegend=True,
                              legend=dict(orientation="v", font=dict(size=11)))
        st.plotly_chart(fig_do, use_container_width=True, config=CFG)

    st.divider()

    # ── По семестрам ───────────────────────────────────────────
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

            # Дельта vs предыдущий семестр
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

    # ── Sentiment по категориям + по отделам рядом ─────────────
    col_cat, col_dept = st.columns(2)

    with col_cat:
        st.markdown("<div class='sec'>🏷 Тональность по категориям</div>",
                    unsafe_allow_html=True)
        cg = df_f.groupby(["llm_category", "llm_sentiment"]).size().reset_index(name="n")
        ct = df_f.groupby("llm_category").size().reset_index(name="tot")
        cg = cg.merge(ct, on="llm_category")
        cg["pct"]    = cg["n"] / cg["tot"] * 100
        cg["cat_ru"] = cg["llm_category"].map(CAT_RU).fillna(cg["llm_category"])
        neg_order = (cg[cg["llm_sentiment"] == "negative"]
                     .sort_values("pct", ascending=False)["cat_ru"].tolist())

        fig_cg = go.Figure()
        for s in ["negative", "neutral", "positive"]:
            sub = (cg[cg["llm_sentiment"] == s]
                   .set_index("cat_ru").reindex(neg_order).reset_index())
            fig_cg.add_trace(go.Bar(
                x=sub["pct"], y=sub["cat_ru"], name=SENT_RU[s],
                orientation="h", marker_color=SENT_C[s],
                hovertemplate=f"{SENT_RU[s]}: %{{x:.1f}}%<extra></extra>",
            ))
        fig_cg.update_layout(barmode="stack")
        fig_cg = _pl(fig_cg, 400, ml=10)
        st.plotly_chart(fig_cg, use_container_width=True, config=CFG)

    with col_dept:
        st.markdown("<div class='sec'>🏢 Тональность по отделам</div>",
                    unsafe_allow_html=True)
        dg = (df_f[df_f["responsible_dept"].notna()]
              .groupby(["responsible_dept", "llm_sentiment"]).size().reset_index(name="n"))
        dt = (df_f[df_f["responsible_dept"].notna()]
              .groupby("responsible_dept").size().reset_index(name="tot"))
        dg = dg.merge(dt, on="responsible_dept")
        dg["pct"] = dg["n"] / dg["tot"] * 100
        dept_neg_order = (dg[dg["llm_sentiment"] == "negative"]
                          .sort_values("pct", ascending=False)["responsible_dept"].tolist())

        fig_dg = go.Figure()
        for s in ["negative", "neutral", "positive"]:
            sub = (dg[dg["llm_sentiment"] == s]
                   .set_index("responsible_dept").reindex(dept_neg_order).reset_index())
            fig_dg.add_trace(go.Bar(
                x=sub["pct"], y=sub["responsible_dept"], name=SENT_RU[s],
                orientation="h", marker_color=SENT_C[s],
                hovertemplate=f"{SENT_RU[s]}: %{{x:.1f}}%<extra></extra>",
            ))
        fig_dg.update_layout(barmode="stack", showlegend=False)
        fig_dg = _pl(fig_dg, 400, ml=10)
        st.plotly_chart(fig_dg, use_container_width=True, config=CFG)

    st.divider()

    # ── Sentiment по дням недели и времени суток ───────────────
    st.markdown("<div class='sec'>🕐 Когда студенты пишут негативно?</div>",
                unsafe_allow_html=True)
    col_wd, col_tod = st.columns(2)

    with col_wd:
        wd_sent = (df_f.groupby(["day_of_week", "llm_sentiment"])
                   .size().reset_index(name="n"))
        wd_tot  = df_f.groupby("day_of_week").size().reset_index(name="tot")
        wd_sent = wd_sent.merge(wd_tot, on="day_of_week")
        wd_sent["pct"] = wd_sent["n"] / wd_sent["tot"] * 100

        neg_wd = (wd_sent[wd_sent["llm_sentiment"] == "negative"]
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
        tod_sent = (df_f.groupby(["period", "llm_sentiment"])
                    .size().reset_index(name="n"))
        tod_tot  = df_f.groupby("period").size().reset_index(name="tot")
        tod_sent = tod_sent.merge(tod_tot, on="period")
        tod_sent["pct"] = tod_sent["n"] / tod_sent["tot"] * 100

        neg_tod = (tod_sent[tod_sent["llm_sentiment"] == "negative"]
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

    


    st.divider()
    st.markdown("<div class='sec'>🩹 Топ Pain Points из негативных постов</div>",
                unsafe_allow_html=True)

    col_pp, col_pp2 = st.columns([2, 1])

    with col_pp:
        if "pain_point" in df_f.columns:
            pain_df = df_f[df_f["pain_point"].notna() & (df_f["llm_sentiment"] == "negative")]
            pc      = pain_df["pain_point"].value_counts().head(20)

            if not pc.empty:
                # График
                fig_pp = go.Figure(go.Bar(
                    x=pc.values, y=pc.index, orientation="h",
                    marker=dict(
                        color=[C_RED if i < 5 else C_ORANGE if i < 10 else C_MUTED
                               for i in range(len(pc))],
                    ),
                    text=pc.values, textposition="outside",
                    textfont=dict(color=C_TEXT, size=11),
                    hovertemplate="%{y}: %{x} упоминаний — нажми кнопку ниже<extra></extra>",
                ))
                fig_pp.update_layout(
                    yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
                    xaxis=dict(showgrid=False),
                )
                fig_pp = _pl(fig_pp, 480, ml=10, mr=60, mb=20)
                st.plotly_chart(fig_pp, use_container_width=True, config=CFG)

                # ── Кнопки топ-10 pain points ──────────────────
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

                # ── Посты по выбранному pain point ─────────────
                selected_pain = st.session_state.get("selected_pain", None)
                if selected_pain:
                    matched = (pain_df[pain_df["pain_point"] == selected_pain]
                               .nlargest(15, "virality_score"))

                    st.markdown(f"""
                    <div style='background:#eef2ff;border:1px solid #c7d2fe;
                                border-radius:10px;padding:12px 16px;margin:12px 0 10px 0'>
                        <span style='font-size:13px;font-weight:700;color:{C_BLUE}'>
                            🩹 «{selected_pain}»
                        </span>
                        <span style='font-size:11px;color:{C_MUTED};margin-left:8px'>
                            {len(matched)} постов · по virality
                        </span>
                    </div>""", unsafe_allow_html=True)

                    for _, r in matched.iterrows():
                        urg   = r.get("llm_urgency", "low")
                        sent  = r.get("llm_sentiment", "neutral")
                        cat   = CAT_RU.get(r.get("llm_category", ""), "")
                        dept  = str(r.get("responsible_dept", "")) if pd.notna(r.get("responsible_dept", "")) else "—"
                        vir   = float(r.get("virality_score", 0))
                        date  = str(r.get("date", ""))[:10]
                        text  = str(r.get("message_clean", ""))[:300]
                        urg_c = URG_C.get(urg, C_MUTED)
                        st.markdown(f"""
                        <div class="post-card" style="border-left:3px solid {urg_c}">
                            <div class="post-meta">
                                {URG_ICO.get(urg, '')}
                                <span class="badge b-{urg}">{URG_RU.get(urg, urg)}</span>
                                <span class="badge b-{sent}">{SENT_ICO.get(sent, '')} {SENT_RU.get(sent, sent)}</span>
                                <b style="color:#6b8fb8">{cat}</b>
                                · 🏢 {dept} · 📅 {date} · ⚡ {vir:.0f}
                            </div>
                            <div class="post-text">{text}</div>
                        </div>""", unsafe_allow_html=True)

    with col_pp2:
        st.markdown("<div class='sec'>Топ pain по отделу</div>", unsafe_allow_html=True)
        if "pain_point" in df_f.columns and "responsible_dept" in df_f.columns:
            dept_pp   = st.selectbox("Отдел",
                                     df_f["responsible_dept"].dropna().unique().tolist(),
                                     key="pp_dept")
            pain_dept = df_f[
                (df_f["responsible_dept"] == dept_pp) &
                (df_f["pain_point"].notna()) &
                (df_f["llm_sentiment"] == "negative")
            ]["pain_point"].value_counts().head(8)

            selected_pain = st.session_state.get("selected_pain", None)

            for pain_txt, cnt in pain_dept.items():
                is_sel   = selected_pain == pain_txt
                bg_c     = "#fde8e8" if is_sel else "#fef2f2"
                fw       = "700" if is_sel else "500"
                prefix   = "✓ " if is_sel else ""

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

                safe_key = f"dp_{dept_pp[:8]}_{pain_txt[:12]}"
                if c_arrow.button("→", key=safe_key, use_container_width=True):
                    st.session_state["selected_pain"] = None if is_sel else pain_txt
                    st.rerun()


# ═══════════════════════════════════════════════════════════════
# ══════════════════ СТРАНИЦА 4: AI SEARCH ══════════════════════
# ═══════════════════════════════════════════════════════════════
elif page == "AI SEARCH":
    st.markdown("<div class='page-title'>🔍 AI Search</div>"
                "<div class='page-sub'>Семантический поиск по смыслу · Работает на ru/kk/en</div>",
                unsafe_allow_html=True)

    EMB_PATH = Path("data/processed/embeddings.npy")
    IDX_PATH = Path("embeddings_index.csv")
    real_mode = EMB_PATH.exists() and IDX_PATH.exists()

    # ── Загрузка модели и эмбеддингов ─────────────────────────
    @st.cache_resource(show_spinner="⏳ Загружаем модель эмбеддингов…")
    def load_embeddings():
        from sentence_transformers import SentenceTransformer, util as st_util
        emb_model  = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
        embeddings = np.load(str(EMB_PATH))
        return emb_model, embeddings, st_util

    if real_mode:
        try:
            emb_model, embeddings, st_util = load_embeddings()
            st.markdown(
                f"<div class='banner-info'>✅ Semantic Search активен "
                f"· {embeddings.shape[0]:,} постов · multilingual MiniLM</div>",
                unsafe_allow_html=True
            )
        except Exception as e:
            real_mode = False
            st.markdown(
                f"<div class='banner-warn'>⚠ Не удалось загрузить embeddings: {e}</div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            "<div class='banner-warn'>⚠ embeddings.npy не найден → TF-IDF режим. "
            "Сохрани <code>data/processed/embeddings.npy</code> для семантического поиска.</div>",
            unsafe_allow_html=True
        )

    # ── Поисковая строка ───────────────────────────────────────
    c_q, c_k = st.columns([5, 1])
    query = c_q.text_input(
        "", placeholder="Введи запрос на любом языке: интернет, асхана, стипендия…",
        label_visibility="collapsed", key="search_query"
    )
    top_k = c_k.number_input("Top-K", 5, 100, 15, 5)

    # ── Фильтры поиска ─────────────────────────────────────────
    f1, f2, f3, f4 = st.columns(4)
    f_sc   = f1.multiselect("Категория",   [CAT_RU[c] for c in VALID_CATEGORIES],
                             key="s_cat", placeholder="Все")
    f_ss   = f2.multiselect("Тональность", ["positive", "neutral", "negative"],
                             format_func=lambda x: SENT_RU[x],
                             key="s_sent", placeholder="Все")
    f_su   = f3.multiselect("Приоритет",   ["critical", "high", "medium", "low"],
                             format_func=lambda x: URG_RU[x],
                             key="s_urg", placeholder="Все")
    sort_s = f4.selectbox("Сортировка",
                          ["По релевантности", "По virality", "По дате"])

    # ── Пул для поиска ─────────────────────────────────────────
    CAT_EN = {v: k for k, v in CAT_RU.items()}
    pool   = df_f[df_f["message_clean"].notna()].reset_index(drop=True)
    if f_sc:
        pool = pool[pool["llm_category"].isin([CAT_EN.get(c, c) for c in f_sc])]
    if f_ss:
        pool = pool[pool["llm_sentiment"].isin(f_ss)]
    if f_su:
        pool = pool[pool["llm_urgency"].isin(f_su)]

    # ── TF-IDF fallback ────────────────────────────────────────
    @st.cache_resource(show_spinner="Строим TF-IDF индекс…")
    def build_tfidf(pool_hash):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.preprocessing import normalize
        texts = pool["message_clean"].fillna("").tolist()
        vec   = TfidfVectorizer(max_features=20000, ngram_range=(1, 2), min_df=2)
        mat   = normalize(vec.fit_transform(texts), norm="l2")
        return vec, mat

    if query.strip():
        with st.spinner("Ищем…"):
            if real_mode:
                # ── Семантический поиск через embeddings ──────
                q_vec  = emb_model.encode([query], normalize_embeddings=True)
                # Фильтруем embeddings только по пулу
                pool_indices = pool.index.tolist()
                if len(pool_indices) < len(embeddings):
                    pool_emb = embeddings[pool_indices]
                else:
                    pool_emb = embeddings

                scores      = st_util.dot_score(q_vec, pool_emb)[0].numpy()
                pool_copy   = pool.copy().reset_index(drop=True)
                pool_copy["_score"] = scores
            else:
                # ── TF-IDF fallback ───────────────────────────
                from sklearn.preprocessing import normalize as norm_fn
                vec, mat    = build_tfidf(hash(tuple(pool["message_clean"].fillna("").tolist()[:50])))
                q_v         = norm_fn(vec.transform([query]), norm="l2")
                scores      = (mat @ q_v.T).toarray().flatten()
                pool_copy   = pool.copy()
                pool_copy["_score"] = scores

        # Сортировка
        if sort_s == "По релевантности":
            result = pool_copy.nlargest(top_k, "_score")
        elif sort_s == "По virality":
            result = pool_copy.nlargest(top_k, "virality_score")
        else:
            result = pool_copy.sort_values("date", ascending=False).head(top_k)

        # ── AI интерпретация результатов ──────────────────────
        if "groq_client" in dir() and groq_client and len(result) >= 3:
            with st.expander("🤖 AI интерпретация результатов", expanded=True):
                if st.button("Проанализировать найденные посты", key="search_ai_btn"):
                    top_texts = result.head(10)["message_clean"].tolist()
                    ai_prompt = (
                        f"Студенты SDU (Казахстан) написали эти посты по теме «{query}»:\n\n" +
                        "\n".join([f"- {t[:150]}" for t in top_texts]) +
                        "\n\nКратко (3-4 предложения): в чём суть проблемы и что рекомендуешь руководству?"
                    )
                    with st.spinner("Анализирую…"):
                        try:
                            resp = groq_client.chat.completions.create(
                                model=MODEL_CHAT,
                                max_tokens=300,
                                messages=[{"role": "user", "content": ai_prompt}]
                            )
                            ai_text = resp.choices[0].message.content
                            st.markdown(f"""
                            <div style='background:#eef2ff;border:1px solid #c7d2fe;
                                        border-radius:12px;padding:16px 20px;
                                        color:#3730a3;font-size:14px;line-height:1.8'>
                                🤖 {ai_text}
                            </div>""", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Ошибка LLM: {e}")

        # ── Результаты ─────────────────────────────────────────
        method_label = "🧠 Semantic" if real_mode else "🔤 TF-IDF"
        st.markdown(
            f"<div style='font-size:13px;color:{C_MUTED};margin-bottom:12px'>"
            f"{method_label} · Найдено <b style='color:{C_TEXT}'>{len(result)}</b> постов "
            f"из пула <b style='color:{C_TEXT}'>{len(pool):,}</b></div>",
            unsafe_allow_html=True
        )

        for _, r in result.iterrows():
            sc    = float(r.get("_score", 0))
            bar   = max(int(sc * 150), 2)
            date  = str(r.get("date", ""))[:10]
            urg   = r.get("llm_urgency", "low")
            sent  = r.get("llm_sentiment", "neutral")
            cat   = CAT_RU.get(r.get("llm_category", ""), "")
            dept  = str(r.get("responsible_dept", "")) if pd.notna(r.get("responsible_dept", "")) else "—"
            vir   = float(r.get("virality_score", 0))
            lang  = r.get("language", "")
            text  = str(r.get("message_clean", ""))[:350]
            urg_c = URG_C.get(urg, C_MUTED)

            # Подсветка слов запроса в тексте
            query_words = query.lower().split()
            for word in query_words:
                if len(word) > 2:
                    text = re.sub(
                        f"({re.escape(word)})",
                        f"<mark style='background:#fef08a;border-radius:3px;padding:0 2px'>\\1</mark>",
                        text, flags=re.IGNORECASE
                    )

            st.markdown(f"""
            <div class="post-card" style="border-left:3px solid {urg_c}">
                <div class="post-meta" style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        {URG_ICO.get(urg, '')}
                        <span class="badge b-{urg}">{URG_RU.get(urg, urg)}</span>
                        <span class="badge b-{sent}">{SENT_ICO.get(sent, '')} {SENT_RU.get(sent, sent)}</span>
                        <b style="color:#6b8fb8">{cat}</b>
                        · 🏢 {dept} · 🌐 {lang} · 📅 {date} · ⚡ {vir:.0f}
                    </div>
                    <div style="display:flex;align-items:center;gap:7px;flex-shrink:0">
                        <div style="width:{bar}px;height:5px;background:{C_BLUE};border-radius:3px"></div>
                        <span style="color:{C_BLUE};font-size:11px;font-weight:600">{sc:.3f}</span>
                    </div>
                </div>
                <div class="post-text" style="margin-top:8px">{text}</div>
            </div>""", unsafe_allow_html=True)

    else:
        # ── Стартовый экран поиска ─────────────────────────────
        st.markdown("<div class='sec'>💡 Попробуй эти запросы</div>", unsafe_allow_html=True)
        examples = [
            ("🌐 Интернет / Canvas",  "интернет не работает canvas упал"),
            ("🍽 Еда в столовой",     "плохая еда асхана дорого невкусно"),
            ("💰 Стипендия",          "стипендия задержали не пришла"),
            ("🥶 Общежитие",          "холодно общежитие батарея"),
            ("📝 Экзамены",           "квиз мидterm retake дедлайн"),
            ("🎉 Мероприятия",        "велком пати концерт события"),
            ("😔 Психология",         "стресс выгорание депрессия тяжело"),
            ("🏫 Деканат",            "деканат расписание посещаемость GPA"),
        ]
        cols = st.columns(4)
        for i, (lbl, q) in enumerate(examples):
            # Кнопки-примеры — нажимаемые
            if cols[i % 4].button(f"{lbl}", key=f"ex_{i}", use_container_width=True):
                st.session_state["search_query"] = q
                st.rerun()

        st.divider()

        # Статистика пула
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("📨 Постов в пуле",  f"{len(pool):,}")
        k2.metric("🔍 Режим поиска",   "Semantic 🧠" if real_mode else "TF-IDF 🔤")
        k3.metric("🌐 Языков",         pool["language"].nunique() if "language" in pool.columns else "—")
        k4.metric("😠 Негативных",     f"{(pool['llm_sentiment'] == 'negative').sum():,}")


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

        src_crit = df_crit if not df_crit.empty else (
            df_f[df_f["llm_urgency"].isin(["high", "critical"])].nlargest(50, "virality_score")
            if DATA_OK else pd.DataFrame()
        )

        if src_crit.empty:
            st.info("Нет данных о критичных постах.")
        else:
            # Фильтры
            c_s1, c_s2, c_s3 = st.columns(3)
            sort_cr  = c_s1.selectbox("Сортировать", ["virality_score", "views", "reactions_total"],
                                       key="cr_sort")
            urg_cr   = c_s2.multiselect("Приоритет", ["critical", "high"],
                                         default=["critical", "high"], key="cr_urg")
            dept_cr  = c_s3.multiselect(
                "Отдел",
                src_crit["responsible_dept"].dropna().unique().tolist()
                if "responsible_dept" in src_crit.columns else [],
                key="cr_dept", placeholder="Все отделы"
            )

            if urg_cr and "llm_urgency" in src_crit.columns:
                src_crit = src_crit[src_crit["llm_urgency"].isin(urg_cr)]
            if dept_cr and "responsible_dept" in src_crit.columns:
                src_crit = src_crit[src_crit["responsible_dept"].isin(dept_cr)]
            if sort_cr in src_crit.columns:
                src_crit = src_crit.nlargest(30, sort_cr)

            # KPI критичных
            k1, k2, k3 = st.columns(3)
            k1.metric("🔴 Критичных",  (src_crit.get("llm_urgency", pd.Series()) == "critical").sum()
                       if "llm_urgency" in src_crit.columns else len(src_crit))
            k2.metric("🟠 Высоких",    (src_crit.get("llm_urgency", pd.Series()) == "high").sum()
                       if "llm_urgency" in src_crit.columns else 0)
            k3.metric("⚡ Avg Virality", f"{src_crit['virality_score'].mean():.0f}"
                       if "virality_score" in src_crit.columns else "—")

            # AI Summary по критичным постам
            if "groq_client" in dir() and groq_client:
                if st.button("🤖 Сгенерировать AI Summary критичных постов", key="crit_ai_btn"):
                    top_crit_texts = src_crit.head(15)["message_clean"].tolist()
                    ai_prompt = (
                        "Эти посты студентов SDU помечены как критичные и требуют немедленного внимания:\n\n" +
                        "\n".join([f"- {t[:200]}" for t in top_crit_texts]) +
                        "\n\nДай краткий отчёт (4-5 предложений) для ректора: "
                        "что происходит, какие отделы виноваты, что нужно сделать срочно?"
                    )
                    with st.spinner("Анализирую критичные посты…"):
                        try:
                            resp = groq_client.chat.completions.create(
                                model=MODEL_CHAT,
                                max_tokens=400,
                                messages=[
                                    {"role": "system",
                                     "content": "Ты аналитик SDU. Пиши кратко и по делу на русском."},
                                    {"role": "user", "content": ai_prompt}
                                ]
                            )
                            ai_crit = resp.choices[0].message.content
                            st.markdown(f"""
                            <div style='background:#fef2f2;border:1px solid #fecaca;
                                        border-left:4px solid {C_RED};border-radius:12px;
                                        padding:16px 20px;color:{C_TEXT};
                                        font-size:14px;line-height:1.8;margin-bottom:16px'>
                                🚨 <b>AI Анализ критичных постов:</b><br><br>{ai_crit}
                            </div>""", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Ошибка LLM: {e}")

            # Посты
            for _, r in src_crit.iterrows():
                urg  = r.get("llm_urgency", "high")
                pain = str(r.get("pain_point", "")) if pd.notna(r.get("pain_point", "")) else ""
                text = str(r.get("message_clean", ""))[:320]
                vir  = float(r.get("virality_score", 0))
                cat  = CAT_RU.get(r.get("llm_category", ""), r.get("llm_category", ""))
                dept = str(r.get("responsible_dept", "")) if pd.notna(r.get("responsible_dept", "")) else "—"
                urg_c = URG_C.get(urg, C_MUTED)
                st.markdown(f"""
                <div class="post-card" style="border-left:4px solid {urg_c}">
                    <div class="post-meta">
                        {URG_ICO.get(urg, '')}
                        <span class="badge b-{urg}" style="font-size:12px;font-weight:700">
                            {URG_RU.get(urg, urg).upper()}
                        </span>
                        {cat} · 🏢 {dept} · ⚡ {vir:.0f}
                        {f"&nbsp;·&nbsp; 🩹 <i>{pain}</i>" if pain and pain != 'nan' else ""}
                    </div>
                    <div class="post-text">{text}</div>
                </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # TAB 2: SPIKE EXPLAINER
    # ═══════════════════════════════════════════════════════════
    with tab2:
        st.markdown("<div class='sec'>📈 Аномалии активности</div>", unsafe_allow_html=True)

        if DATA_OK:
            daily     = df_f.groupby("date_day").size().reset_index(name="count")
            daily["date_day"] = pd.to_datetime(daily["date_day"])
            avg_daily = daily["count"].mean()

            spikes_auto = daily[daily["count"] > avg_daily * 2.2].copy()
            spikes_auto["spike_pct"] = (spikes_auto["count"] - avg_daily) / avg_daily * 100

            # График активности
            fig_sp = go.Figure()
            fig_sp.add_trace(go.Scatter(
                x=daily["date_day"], y=daily["count"],
                mode="lines", name="Посты/день",
                line=dict(color=C_BLUE, width=1.5),
                fill="tozeroy", fillcolor=rgba(C_BLUE, 0.09),
                hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y} постов<extra></extra>",
            ))
            # Линия среднего
            fig_sp.add_hline(y=avg_daily, line_dash="dot",
                             line_color=C_MUTED, line_width=1,
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
            fig_sp = _pl(fig_sp, 260)
            st.plotly_chart(fig_sp, use_container_width=True, config=CFG)

            # Метрики спайков
            if len(spikes_auto):
                k1, k2, k3 = st.columns(3)
                k1.metric("📈 Аномальных дней",   len(spikes_auto))
                k2.metric("🔥 Макс. пик",         f"+{spikes_auto['spike_pct'].max():.0f}%")
                k3.metric("📅 Самый активный день",
                          spikes_auto.loc[spikes_auto["count"].idxmax(), "date_day"].strftime("%d.%m.%Y"))

        # Карточки объяснений
        src_spk = df_spikes if not df_spikes.empty else (
            spikes_auto if DATA_OK else pd.DataFrame()
        )

        if not src_spk.empty:
            st.markdown("<div class='sec'>Объяснения пиков</div>", unsafe_allow_html=True)
            for _, r in src_spk.head(8).iterrows():
                pct  = float(r.get("spike_pct", 0))
                date = str(r.get("date_day", ""))
                cnt  = int(r.get("count", 0))
                expl = str(r.get("explanation", "")) if pd.notna(r.get("explanation", "")) else None

                st.markdown(f"""
                <div class="spike-card">
                    <div class="post-meta">
                        📅 <b style="color:{C_TEXT}">{date}</b>
                        &nbsp;·&nbsp;
                        <span style="color:{C_ORANGE};font-weight:700">+{pct:.0f}% активности</span>
                        &nbsp;·&nbsp; {cnt} постов
                    </div>
                    <div class="post-text" style="white-space:pre-wrap;margin-top:8px">
                        {expl if expl and expl not in ('None', 'nan')
                          else f'<span style="color:{C_MUTED}">LLM-объяснение появится после запуска Spike Explainer из ноутбука</span>'}
                    </div>
                </div>""", unsafe_allow_html=True)

            # AI объяснение на лету для нового периода
            if "groq_client" in dir() and groq_client and DATA_OK:
                st.markdown("<div class='sec'>🤖 Объяснить произвольный период</div>",
                            unsafe_allow_html=True)
                col_d1, col_d2 = st.columns(2)
                spike_date = col_d1.date_input("Выбери день", key="spike_date_sel")
                if col_d2.button("Объяснить этот день", key="spike_explain_btn"):
                    day_str   = spike_date.strftime("%Y-%m-%d")
                    day_posts = df_f[df_f["date_day"] == day_str].nlargest(15, "virality_score")
                    if len(day_posts) == 0:
                        st.warning("В этот день нет постов в текущей выборке.")
                    else:
                        posts_text = "\n- ".join(day_posts["message_clean"].fillna("").tolist()[:12])
                        day_count  = len(day_posts)
                        ai_prompt  = (
                            f"В канале SDU {day_str} было {day_count} постов.\n\n"
                            f"Топ посты:\n- {posts_text}\n\n"
                            f"Объясни в 2-3 предложениях: что произошло и почему студенты так активны?"
                        )
                        with st.spinner("Анализирую день…"):
                            try:
                                resp = groq_client.chat.completions.create(
                                    model=MODEL_CHAT,
                                    max_tokens=250,
                                    messages=[{"role": "user", "content": ai_prompt}]
                                )
                                st.markdown(f"""
                                <div class="spike-card">
                                    <div class="post-meta">📅 <b>{day_str}</b> · {day_count} постов</div>
                                    <div class="post-text" style="margin-top:8px">
                                        🤖 {resp.choices[0].message.content}
                                    </div>
                                </div>""", unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Ошибка: {e}")

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
            col_f1, col_f2 = st.columns(2)
            depts_sugg = src_sugg["responsible_dept"].dropna().unique().tolist() \
                if "responsible_dept" in src_sugg.columns else []
            f_dept_s = col_f1.multiselect("Фильтр по отделу", depts_sugg,
                                           key="sugg_dept", placeholder="Все отделы")
            f_cat_s  = col_f2.multiselect(
                "Фильтр по категории",
                [CAT_RU.get(c, c) for c in src_sugg["llm_category"].dropna().unique().tolist()]
                if "llm_category" in src_sugg.columns else [],
                key="sugg_cat", placeholder="Все категории"
            )

            if f_dept_s:
                src_sugg = src_sugg[src_sugg["responsible_dept"].isin(f_dept_s)]
            if f_cat_s:
                src_sugg = src_sugg[
                    src_sugg["llm_category"].isin([CAT_EN.get(c, c) for c in f_cat_s])
                ]

            # KPI
            ks1, ks2, ks3, ks4 = st.columns(4)
            ks1.metric("💡 Идей всего",         len(src_sugg))
            ks2.metric("🏢 Отделов затронуто",  src_sugg["responsible_dept"].nunique()
                        if "responsible_dept" in src_sugg.columns else "—")
            ks3.metric("⚡ Avg virality",         f"{src_sugg['virality_score'].mean():.0f}"
                        if "virality_score" in src_sugg.columns else "—")
            ks4.metric("🔝 Топ отдел",           src_sugg["responsible_dept"].value_counts().index[0]
                        if "responsible_dept" in src_sugg.columns and len(src_sugg) > 0 else "—")

            # AI Summary идей по кнопке
            if "groq_client" in dir() and groq_client:
                if st.button("🤖 Сгенерировать отчёт по идеям студентов", key="sugg_ai_btn"):
                    suggestions = src_sugg["suggestion"].dropna().head(20).tolist()
                    ai_prompt   = (
                        "Студенты SDU предложили следующие улучшения:\n\n" +
                        "\n".join([f"- {s}" for s in suggestions]) +
                        "\n\nСгруппируй идеи по темам и напиши краткий отчёт (5-6 предложений) "
                        "для руководства: что студенты хотят улучшить в первую очередь?"
                    )
                    with st.spinner("Анализирую предложения…"):
                        try:
                            resp = groq_client.chat.completions.create(
                                model=MODEL_CHAT,
                                max_tokens=400,
                                messages=[
                                    {"role": "system",
                                     "content": "Аналитик SDU. Пиши кратко и структурированно на русском."},
                                    {"role": "user", "content": ai_prompt}
                                ]
                            )
                            st.markdown(f"""
                            <div style='background:#f0fdf4;border:1px solid #bbf7d0;
                                        border-left:4px solid {C_GREEN};border-radius:12px;
                                        padding:16px 20px;color:{C_TEXT};
                                        font-size:14px;line-height:1.8;margin-bottom:16px'>
                                💡 <b>AI Summary идей студентов:</b><br><br>
                                {resp.choices[0].message.content}
                            </div>""", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Ошибка LLM: {e}")

            # Карточки идей
            for _, r in src_sugg.head(30).iterrows():
                sugg = str(r.get("suggestion", "")) if pd.notna(r.get("suggestion", "")) else ""
                cat  = CAT_RU.get(r.get("llm_category", ""), "")
                dept = str(r.get("responsible_dept", "")) if pd.notna(r.get("responsible_dept", "")) else "—"
                text = str(r.get("message_clean", ""))[:280]
                vir  = float(r.get("virality_score", 0))
                st.markdown(f"""
                <div class="post-card" style="border-left:3px solid {C_GREEN}">
                    <div class="post-meta">
                        💡 <b style="color:{C_GREEN}">Предложение</b>
                        &nbsp;·&nbsp; {cat} · 🏢 {dept} · ⚡ {vir:.0f}
                    </div>
                    <div class="post-text">{text}</div>
                    {f'<div style="margin-top:10px;padding:10px 14px;background:#f0fdf4;'
                      f'border-radius:8px;font-size:13px;color:{C_GREEN};font-weight:500">'
                      f'→ {sugg}</div>' if sugg and sugg != 'nan' else ''}
                </div>""", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # TAB 4: EXECUTIVE SUMMARY
    # ═══════════════════════════════════════════════════════════
    with tab4:
        st.markdown("<div class='sec'>📄 Executive Summary для руководства</div>",
                    unsafe_allow_html=True)

        SUMM_PATH = Path("/Users/nurdaulet/Documents/NYPDAYLET/SDU/data/analyzed/executive_summary.txt")

        if SUMM_PATH.exists():
            with open(SUMM_PATH, encoding="utf-8") as f:
                txt = f.read()
            st.markdown(f"""
            <div style='background:{C_CARD};border:1px solid {C_BORDER};border-radius:14px;
                        padding:26px;color:{C_TEXT};font-size:15px;line-height:1.85;
                        white-space:pre-wrap'>{txt}</div>""", unsafe_allow_html=True)

        elif DATA_OK:
            # Авто-summary из данных
            neg_p   = (df_f["llm_sentiment"] == "negative").mean() * 100
            crit_n  = (df_f["llm_urgency"] == "critical").sum()
            high_n  = (df_f["llm_urgency"] == "high").sum()
            top_c   = df_f["llm_category"].value_counts().index[0] if len(df_f) else "—"
            top_d   = df_f["responsible_dept"].dropna().value_counts()
            top_d_n = top_d.index[0] if len(top_d) else "—"
            ideas   = int(df_f["is_constructive"].sum()) if "is_constructive" in df_f.columns else 0

            st.markdown(f"""
            <div style='background:{C_CARD};border:1px solid {C_BORDER};border-radius:14px;padding:26px'>
                <div style='font-size:20px;font-weight:800;color:{C_TEXT};margin-bottom:20px'>
                    📊 Аналитический отчёт SDU Angime
                </div>
                <p style='color:{C_TEXT};line-height:1.85'>
                    Проанализировано <b style='color:{C_BLUE}'>{len(df_f):,}</b> анонимных постов
                    студентов SDU. Доля негативных обращений: <b style='color:{C_RED}'>{neg_p:.1f}%</b>.
                    Критических обращений: <b style='color:{C_RED}'>{crit_n}</b>,
                    высокоприоритетных: <b style='color:{C_ORANGE}'>{high_n}</b>.
                </p>
                <p style='color:{C_TEXT};line-height:1.85'>
                    Наиболее частая тема: <b style='color:{C_BLUE}'>{CAT_RU.get(top_c, top_c)}</b>.
                    Отдел с наибольшим числом обращений: <b style='color:{C_ORANGE}'>{top_d_n}</b>.
                    Студенты внесли <b style='color:{C_GREEN}'>{ideas}</b> конструктивных предложений.
                </p>
            </div>""", unsafe_allow_html=True)

        st.divider()

        # AI Summary по кнопке с контекстом фильтров
        if "groq_client" in dir() and groq_client and DATA_OK:
            st.markdown("<div class='sec'>🤖 AI Executive Summary</div>", unsafe_allow_html=True)

            col_opt1, col_opt2 = st.columns(2)
            summary_focus = col_opt1.selectbox(
                "Фокус отчёта",
                ["Общий обзор", "Критичные проблемы", "Инфраструктура", "Еда и столовая",
                 "Психологический климат", "Конструктивные идеи"],
                key="summ_focus"
            )
            summary_len = col_opt2.select_slider(
                "Длина отчёта",
                ["Кратко (3 предл.)", "Средний (5-6 предл.)", "Детальный (8-10 предл.)"],
                value="Средний (5-6 предл.)",
                key="summ_len"
            )

            if st.button("📝 Сгенерировать Executive Summary", key="exec_summ_btn",
                         use_container_width=True):
                # Собираем контекст
                neg_pct_f  = (df_f["llm_sentiment"] == "negative").mean() * 100
                crit_f     = (df_f["llm_urgency"] == "critical").sum()
                top_cats_f = df_f["llm_category"].value_counts().head(5).to_dict()
                top_dept_f = df_f["responsible_dept"].dropna().value_counts().head(5).to_dict()
                top_pain_f = df_f["pain_point"].dropna().value_counts().head(10).to_dict() \
                    if "pain_point" in df_f.columns else {}
                top_posts  = df_f.nlargest(8, "virality_score")["message_clean"].tolist()

                len_map = {
                    "Кратко (3 предл.)":        "3 предложения",
                    "Средний (5-6 предл.)":     "5-6 предложений",
                    "Детальный (8-10 предл.)":  "8-10 предложений"
                }

                ai_prompt = f"""Ты аналитик данных SDU (Казахстан). Пиши строго на русском.

Данные за выбранный период ({len(df_f):,} постов):
- Негативных: {neg_pct_f:.1f}%
- Критичных: {crit_f}
- Топ категории: {top_cats_f}
- Топ отделы по обращениям: {top_dept_f}
- Главные боли студентов: {top_pain_f}

Самые резонансные посты:
{chr(10).join([f"- {t[:180]}" for t in top_posts[:6]])}

Фокус отчёта: {summary_focus}
Напиши Executive Summary длиной {len_map[summary_len]} для ректора SDU.
Будь конкретным: называй отделы, проблемы и рекомендации."""

                with st.spinner("Генерирую Executive Summary…"):
                    try:
                        resp = groq_client.chat.completions.create(
                            model=MODEL_CHAT,
                            max_tokens=600,
                            messages=[
                                {"role": "system",
                                 "content": "Ты старший аналитик данных университета. "
                                            "Пишешь чёткие, конкретные отчёты для руководства."},
                                {"role": "user", "content": ai_prompt}
                            ]
                        )
                        summary_text = resp.choices[0].message.content

                        st.markdown(f"""
                        <div style='background:{C_CARD};border:1px solid {C_BORDER};
                                    border-left:4px solid {C_BLUE};border-radius:14px;
                                    padding:26px;color:{C_TEXT};font-size:15px;
                                    line-height:1.85;white-space:pre-wrap'>
                            <div style='font-size:13px;color:{C_MUTED};margin-bottom:12px'>
                                🤖 Сгенерировано AI · Фокус: {summary_focus}
                                · {len(df_f):,} постов в выборке
                            </div>
                            {summary_text}
                        </div>""", unsafe_allow_html=True)

                        # Кнопка сохранения
                        st.download_button(
                            "💾 Скачать как .txt",
                            data=summary_text,
                            file_name=f"executive_summary_{summary_focus.replace(' ', '_')}.txt",
                            mime="text/plain",
                            key="download_summary"
                        )
                    except Exception as e:
                        st.error(f"Ошибка генерации: {e}")

        # Итоговые KPI
        st.markdown("<div class='sec'>📊 Итоговые показатели</div>", unsafe_allow_html=True)
        if DATA_OK:
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("🚨 Critical",  (df_f["llm_urgency"] == "critical").sum())
            k2.metric("🔴 High",      (df_f["llm_urgency"] == "high").sum())
            k3.metric("😠 Негатив",   f'{(df_f["llm_sentiment"] == "negative").mean() * 100:.1f}%')
            k4.metric("💡 Идеи",      df_f["is_constructive"].sum()
                       if "is_constructive" in df_f.columns else 0)
            k5.metric("📨 Всего",     f"{len(df_f):,}")

            # Urgency donut
            urg_c   = df_f["llm_urgency"].value_counts()
            fig_urg = go.Figure(go.Pie(
                labels=[URG_RU.get(u, u) for u in urg_c.index],
                values=urg_c.values,
                marker=dict(colors=[URG_C.get(u, C_MUTED) for u in urg_c.index],
                            line=dict(color=C_BG, width=2)),
                hole=0.6, textinfo="label+percent",
                textfont=dict(size=12, color=C_TEXT),
            ))
            fig_urg.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=300,
                                   margin=dict(t=10, r=10, b=10, l=10),
                                   showlegend=False)
            st.plotly_chart(fig_urg, use_container_width=True, config=CFG)