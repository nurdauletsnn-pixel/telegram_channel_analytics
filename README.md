# 🎓 SDU Angime Analytics

> **AI-powered analytics dashboard for a student Telegram community — turning raw student chatter into data-driven decisions for the university.**

**SDU Angime Analytics** is an interactive [Streamlit](https://streamlit.io/) dashboard that analyzes posts from the **SDU (Suleyman Demirel University) student Telegram channel "SDU Angime"**. It combines classic NLP (language detection, sentiment, TF‑IDF, embeddings) with **LLM processing (Groq)** to surface critical posts, recurring pain points, sentiment dynamics, and student-generated ideas — helping the university administration identify growth opportunities and make effective, evidence-based decisions.

*Built with a **Data-Driven** mindset: every chart, KPI and AI summary is derived from real student posts.*

https://sdu-angime-analytics.streamlit.app
---

## 📖 Table of Contents

- [Overview](#-overview)
- [Why this project exists](#-why-this-project-exists)
- [Key features](#-key-features)
- [Architecture](#-architecture)
- [Repository structure](#-repository-structure)
- [Data pipeline](#-data-pipeline)
- [Data schema](#-data-schema)
- [Tech stack](#-tech-stack)
- [Getting started](#-getting-started)
- [Dashboard pages walkthrough](#-dashboard-pages-walkthrough)
- [Configuration & secrets](#-configuration--secrets)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [License & contact](#-license--contact)

---

## 🔭 Overview

The SDU Telegram community ("SDU Angime") is where students openly discuss exams, teachers, dorms, food, scholarships, IT infrastructure, mental health and more. This stream of unstructured, multilingual (Russian / Kazakh / English / mixed), often emotional text is a **goldmine of honest feedback** — but it is impossible to read manually.

**SDU Angime Analytics** ingests that data and turns it into a decision-support tool for the university administration:

- **Detects critical & high-priority posts** that need an urgent response.
- **Separates real pain points** from noise, and maps each one to the **responsible department** (Dean's office, Dorms, IT, Finance / Scholarship, AC Catering, Security, Library, etc.).
- **Tracks sentiment over time** (by day, week, month, semester) to spot worsening trends.
- **Surfaces constructive student ideas** (the "Idea Bank") before they turn into complaints.
- **Explains activity spikes** (e.g. an event or incident that triggered a burst of posts).
- **Generates executive summaries** with concrete recommendations, in Russian, Kazakh or English.

The dashboard is fully **filterable** (date, semester, month, weekday, time-of-day, department, category, urgency, sentiment) and every AI insight is grounded in the currently selected slice of data.

---

## 💡 Why this project exists

Universities usually rely on anecdotal feedback (suggestion boxes, informal chats) to understand student satisfaction. This project applies a **DATA-DRIVEN approach** that:

1. **Quantifies** the student voice instead of guessing it.
2. **Prioritizes** problems by severity and virality, so leadership focuses on what actually matters.
3. **Connects** every pain point to an **owner department**, enabling accountability.
4. **Suggests growth opportunities** by highlighting recurring requests (e.g. "more events", "better Wi-Fi", "fix Moodle").

The end goal is simple: **help the university and its structural units make efficient, effective decisions based on evidence, not intuition.**


---

## ✨ Key features

| Feature | Description |
|---|---|
| 🔐 **Password-protected access** | The dashboard is gated behind a login screen (`APP_PASSWORD` via env var or `st.secrets`). |
| 📊 **Executive KPIs** | Total posts, "anxiety index" (% negative), average virality, critical count, student ideas, top department. |
| 🍩 **Sentiment analytics** | Positive / neutral / negative distribution over time, by semester, by day-of-week, by time-of-day. |
| 🕐 **Activity heatmap** | Day × hour heatmap to find when students are most active (and most negative). |
| 🏢 **Department intelligence** | Mentions per responsible department with sentiment breakdown drilling down to the top-20 posts + AI analysis. |
| 🌌 **Topic / category analysis** | 14 categories (`exams`, `academics`, `teachers`, `food`, `dorms`, `infrastructure`, `scholarship`, `career`, `relationships`, `mental_health`, `events`, `admin`, `humor`, `other`) with category-specific keyword extraction. |
| 🧠 **Semantic AI Search** | Free-text search over post embeddings (`paraphrase-multilingual-MiniLM-L12-v2`) **or** keyword search, with category / sentiment / urgency filters. |
| 🩹 **Pain-point detection** | Groups negative posts into concrete pain points per category, each clickable to reveal the top posts + AI recommendations. |
| 📈 **Spike Explainer** | Automatically detects anomalous days (`> 2.2 × average`) and uses the LLM to explain what happened. |
| 🛠 **Idea Bank** | Collects constructive student suggestions and summarizes them by theme. |
| 📄 **AI Executive Summary** | On-demand management report with configurable **focus**, **length** and **language** (RU / KZ / EN), downloadable as `.txt`. |
| 🤖 **Groq LLM integration** | On-demand AI summaries for critical posts, departments, categories, spikes and search results — each grounded in the current data slice. |
| 🔞 **Profanity censorship** | Built-in multilingual profanity filter with an optional "reveal" toggle. |
| 🌐 **Multilingual** | Handles Russian, Kazakh, English and mixed RU/KZ posts. |

---

## 🏗 Architecture

The dashboard is intentionally a **single-file Streamlit application** (`app.py`) — simple to deploy and easy to iterate on. Its logical layers are:

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (app.py)                          │
│                                                                        │
│  ┌────────────┐   ┌─────────────────────────────────────────────────┐ │
│  │  Auth gate │ → │  Sidebar navigation + global filters            │ │
│  │ (password) │   │  (date, semester, month, day, time, dept, cat)  │ │
│  └────────────┘   └─────────────────────────────────────────────────┘ │
│                                    │                                   │
│        ┌───────────────┬───────────┼───────────────┬───────────────┐   │
│        ▼               ▼           ▼               ▼               ▼   │
│   OVERVIEW         TOPICS      SENTIMENT       AI SEARCH    AI INSIGHTS │
│   (KPIs,          (categories  (pain points,   (semantic /  (critical,  │
│    timeline,       + TF-IDF)    when, virality) keyword)     spikes,    │
│    heatmap)                                                  ideas, exec)│
│                                                                        │
│  Shared components: post_card(), censor_text(), _pl() (Plotly theme)   │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│              Data layer (pd.read_csv + @st.cache_data TTL 300s)        │
│  data/analyzed/classified_posts.csv  (main, 49 columns)                │
│  data/analyzed/student_suggestions.csv                                 │
│  data/analyzed/critical_posts.csv                                      │
│  data/analyzed/spike_explanations.csv                                  │
│  data/processed/embeddings.npy + embeddings_index.csv (semantic search)│
└──────────────────────────────────────────────────────────────────────┘

External services:
  • Groq API (model `compound-beta-mini`) → on-demand LLM summaries/reports
  • sentence-transformers (MiniLM, CPU)   → query embeddings for semantic search
```

**Design notes**

- **Caching:** `load_data()` uses `@st.cache_data(ttl=300)`; the embedding model uses `@st.cache_resource`.
- **Filtering:** All filters are stored in `st.session_state` and applied in one central `apply_filters()` function, so every page sees the same, consistently filtered dataframe (`df_f`).
- **Graceful degradation:** If `GROQ_API_KEY` is missing, the AI buttons are hidden; if `embeddings.npy` is missing, search falls back to keyword mode.
- **Reusable rendering:** Posts are rendered through a single `post_card()` helper (urgency, sentiment, category, department, views, virality, censorship, expand/collapse).


---

## 📂 Repository structure

```
telegram_channel_analytics/
├── app.py                         # ⭐ The entire Streamlit dashboard (2479 lines)
├── requirements.txt               # Python dependencies
├── .env                           # GROQ_API_KEY + APP_PASSWORD (not committed)
├── .devcontainer/
│   └── devcontainer.json          # GitHub Codespaces / VS Code Dev Container setup
├── .streamlit/
│   └── secrets.toml               # Optional alternative to .env (not committed)
├── IMG_2289.JPG                   # Login screen avatar #1
├── photo_2026-03-12 02.06.08.jpeg # Login screen avatar #2 + sidebar logo
│
└── data/
    ├── processed/                 # Output of the cleaning / NLP pipeline
    │   ├── final_cleaned_v2.csv       # Cleaned + enriched posts (master, ~16k rows)
    │   ├── sentiment_mechanical.csv   # Posts + rule-based/rubert-tiny2 sentiment
    │   ├── sentiment_llm_queue.csv    # Rows queued for LLM sentiment labelling
    │   ├── embeddings.npy             # (N × 384) float32 MiniLM embeddings
    │   ├── embeddings_index.csv       # Maps embedding row → message_id
    │   └── top_ngrams.csv             # Most frequent n-grams across the corpus
    │
    └── analyzed/                  # Output of the LLM classification pipeline
        ├── classified_posts.csv       # ⭐ MAIN dataset consumed by the app
        ├── critical_posts.csv         # High-priority posts extract
        ├── student_suggestions.csv    # Constructive ideas (Idea Bank)
        └── spike_explanations.csv     # Anomalous days + LLM explanations
```

> **Note:** The upstream data-collection / NLP pipeline is developed in a separate notebook (`sduang.ipynb`, ignored via `.gitignore`). This repository contains the **dashboard plus the already-processed datasets** it consumes.

---

## 🔄 Data pipeline

The dashboard is the final layer of a larger data pipeline that transforms raw Telegram messages into structured, LLM-enriched data:

```
1.  Telegram channel export (raw messages, views, forwards, reactions)
              │
              ▼
2.  Cleaning & enrichment  ──►  data/processed/final_cleaned_v2.csv
    • text normalisation, stop-word removal, lemmatisation
    • language detection (ru / kk / en / mixed)
    • feature engineering: length, word_count, emoji_count,
      is_question, is_complaint, virality_score
    • temporal features: year, month, week, hour, day_of_week,
      period (Таң/Түс/Кеш/Түн), semester
              │
              ▼
3.  Sentiment (mechanical)  ──►  data/processed/sentiment_mechanical.csv
    • rule-based / RuBERT-tiny2 sentiment label + score
    • rows flagged for LLM review → sentiment_llm_queue.csv
              │
              ▼
4.  Embeddings             ──►  data/processed/embeddings.npy
                                 data/processed/embeddings_index.csv
    • sentence-transformers: paraphrase-multilingual-MiniLM-L12-v2 (384-dim)
              │
              ▼
5.  LLM classification (Groq)  ──►  data/analyzed/classified_posts.csv
    • llm_category, llm_urgency, llm_sentiment, llm_topic
    • responsible_dept, pain_point, is_constructive, suggestion
              │
              ├──►  critical_posts.csv        (high/critical urgency extract)
              ├──►  student_suggestions.csv   (constructive ideas)
              └──►  spike_explanations.csv    (anomalous days explained)
              │
              ▼
6.  Streamlit dashboard (app.py)  ──►  interactive, filterable UX
```

**Virality score** (a core ranking signal) is derived from engagement metrics (views, forwards, reactions) to highlight the posts that resonated most with the community, regardless of team size.


---

## 🗃 Data schema

### `data/analyzed/classified_posts.csv` — main dataset (49 columns)

| Group | Columns |
|---|---|
| **Identity** | `id`, `message_id` |
| **Time** | `date`, `year`, `month`, `week_num`, `hour`, `day_of_week`, `day_of_week_num`, `period`, `period_en`, `semester` |
| **Content** | `message`, `media_type`, `reply_to`, `is_text_post`, `has_media`, `is_reply` |
| **Engagement** | `views`, `forwards`, `reactions_total`, `reactions_count`, `reactions_positive`, `reactions_negative`, `virality_score` |
| **Text processing** | `message_clean`, `text_norm`, `text_nostop`, `text_lemma`, `text_for_embedding`, `language`, `text_length`, `word_count`, `emoji_count`, `has_emoji` |
| **Signals** | `is_question`, `is_complaint` |
| **Sentiment (mechanical)** | `sentiment_label`, `sentiment_score`, `sentiment_source`, `sentiment_needs_llm` |
| **LLM output** | `llm_category`, `llm_urgency`, `llm_sentiment`, `llm_topic`, `responsible_dept`, `pain_point`, `is_constructive`, `suggestion` |

**Enumerations**

- `llm_category`: `exams`, `academics`, `teachers`, `food`, `dorms`, `infrastructure`, `scholarship`, `career`, `relationships`, `mental_health`, `events`, `admin`, `humor`, `other`
- `llm_urgency`: `low`, `medium`, `high`, `critical`
- `llm_sentiment`: `positive`, `neutral`, `negative`
- `responsible_dept`: `Деканат`, `Общежитие`, `Административный отдел`, `IT департамент`, `Финансовый отдел`, `AC Catering`, `Служба безопасности`, `Библиотека` (+ free-form values)
- `language`: `ru`, `kk`, `en`, `mixed_kk_ru`, `other`

### Other datasets

| File | Columns |
|---|---|
| `student_suggestions.csv` | `message_clean`, `suggestion`, `llm_category`, `responsible_dept`, `virality_score` |
| `critical_posts.csv` | `message_clean`, `llm_category`, `responsible_dept`, `pain_point`, `sentiment_label`, `virality_score` |
| `spike_explanations.csv` | `date_day`, `count`, `avg_count`, `spike_pct`, `explanation` |
| `embeddings_index.csv` | `id`, `message_id` (row position ↔ embedding index) |
| `embeddings.npy` | `(9456 × 384) float32` |

---

## 🧰 Tech stack

| Layer | Technology |
|---|---|
| **UI framework** | [Streamlit](https://streamlit.io/) |
| **Data processing** | [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/) |
| **Visualisation** | [Plotly](https://plotly.com/python/) (`plotly.express`, `plotly.graph_objects`) |
| **LLM** | [Groq](https://groq.com/) Python SDK — model `compound-beta-mini` |
| **Semantic search** | [sentence-transformers](https://www.sbert.net/) — `paraphrase-multilingual-MiniLM-L12-v2` (CPU) |
| **Classical NLP** | [scikit-learn](https://scikit-learn.org/) (TF-IDF), custom keyword extraction |
| **Config** | [python-dotenv](https://pypi.org/project/python-dotenv/) (`.env`) and `st.secrets` |


---

## 🚀 Getting started

### Prerequisites

- **Python 3.11+** (the Dev Container pins `python:1-3.11-bookworm`)
- A **Groq API key** (free tier available at <https://console.groq.com/>) — required only for the AI features
- ~2 GB free RAM (the embedding model + datasets are loaded into memory)

### 1. Clone the repository

```bash
git clone <your-repo-url> telegram_channel_analytics
cd telegram_channel_analytics
```

### 2. Create a virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt`:

```
streamlit
pandas
numpy
plotly
groq
scikit-learn
sentence-transformers
python-dotenv
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```dotenv
# --- Required for AI features (critical posts, executive summary, etc.) ---
GROQ_API_KEY=your_groq_api_key_here

# --- Required to log into the dashboard ---
APP_PASSWORD=your_dashboard_password_here
```

> The dashboard reads `APP_PASSWORD` from the environment **or** from `.streamlit/secrets.toml`
> (key `APP_PASSWORD`). Both `.env` and `.streamlit/secrets.toml` are git-ignored.

`.streamlit/secrets.toml` (alternative):

```toml
APP_PASSWORD = "your_dashboard_password_here"
GROQ_API_KEY = "your_groq_api_key_here"
```

### 4. Run the app

```bash
streamlit run app.py
```

Then open <http://localhost:8501> and log in with the `APP_PASSWORD` you configured.

> **Data is expected at `data/analyzed/` and `data/processed/`** (relative to the working directory).
> Run Streamlit **from the project root** so these relative paths resolve correctly.

---

## 🖥 Dashboard pages walkthrough

Navigation lives in the sidebar (radio: `OVERVIEW · TOPICS · SENTIMENT · AI SEARCH · AI INSIGHTS & REPORTS`). A global **🔞 ЦЕНЗУРА** toggle applies profanity masking everywhere.

### 1. OVERVIEW
The executive landing page.
- **KPIs:** total posts, anxiety index (% negative), average virality, critical count, student ideas, top department.
- **Sentiment timeline** — stacked area (by day / week / month).
- **Activity heatmap** — day × hour, to reveal behavioural patterns.
- **Language distribution** — RU / KZ / EN / mixed.
- **Sentiment-share over time** — 100% stacked bar (year/quarter/month/week).
- **Top posts by Virality Score.**
- **Department mentions** — stacked bars by sentiment + per-department cards with clickable sentiment buttons that reveal the top-20 posts and an **AI analysis** of that department.

### 2. TOPICS
Understand *what* students talk about.
- Horizontal **category distribution** with per-category sentiment mini-cards (positive / neutral / negative %).
- **Top-7 category dynamics** over time.
- **Category drill-down**: pick a category → see its KPIs, sentiment pie, and **distinctive keywords** extracted with a category-vs-corpus TF-IDF-style score, plus the posts in that category.

### 3. SENTIMENT
Focus on the emotional temperature and **pain points**.
- **KPIs:** % positive / neutral / negative, virality of negative vs positive posts.
- **Sentiment by semester** with delta cards (↑/↓ vs previous semester).
- **"When do students post negatively?"** — by weekday and by time-of-day.
- **Sentiment × Virality scatter.**
- **Pain Points:** top negative pain points per category, each clickable → top posts + an **AI recommendation** grounded in those posts.

### 4. AI SEARCH
Find anything across the corpus.
- **Semantic mode** (embeddings cosine similarity) or **keyword mode** (exact matches).
- Filters: category, sentiment, urgency, and sort by relevance / virality / date.
- **AI interpretation** of the search results (summarises the issue + recommendations).
- Curated example queries (Internet/Moodle, food, scholarships, dorms, exams, events, stress, dean's office).

### 5. AI INSIGHTS & REPORTS
The reporting workbench (4 tabs).
- **🚨 Critical posts** — all `high` + `critical` urgency posts, filterable, with an **AI Summary** for management.
- **📈 Spike Explainer** — auto-detected anomalous days (`> 2.2 ×` average) plus an interactive "explain any day" tool powered by the LLM.
- **🛠 Idea Bank** — constructive student suggestions (`student_suggestions.csv`), filterable by department/category, with an **AI thematic summary**.
- **📄 Executive Summary** — generate a management report on demand: choose **focus** (14 options incl. food, dorms, IT/Moodle, scholarships, teachers, mental health, etc.), **length** (short / medium / detailed) and **language** (RU / KZ / EN). Result is shown in-page and downloadable as `.txt`.


---

## ⚙️ Configuration & secrets

| Variable / Secret | Where used | Required | Purpose |
|---|---|---|---|
| `GROQ_API_KEY` | `os.getenv("GROQ_API_KEY")` | For AI features | Authenticates the Groq LLM client |
| `APP_PASSWORD` | `os.getenv("APP_PASSWORD")` → fallback `st.secrets["APP_PASSWORD"]` | Yes | Login password for the dashboard |

- If `GROQ_API_KEY` is **not** set, `groq_client` is `None` and every AI button/panel is hidden — the rest of the dashboard still works.
- If `APP_PASSWORD` is **not** set, the password check compares against an empty string (i.e. an empty password would log in). **Always set it in production.**

---

## 📦 Deployment

### GitHub Codespaces / VS Code Dev Container

The repository ships a ready-to-use `.devcontainer/devcontainer.json`:
- Base image: `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`
- Installs `requirements.txt` + Streamlit automatically on content update.
- Auto-runs the app on attach:
  ```bash
  streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
  ```
- Forwards port **8501** and opens the preview automatically.

### Streamlit Community Cloud
1. Push the repo to GitHub (ensure `data/analyzed/*` and `data/processed/*` are committed or otherwise available).
2. On <https://share.streamlit.io/>, create an app pointing to `app.py`.
3. Add secrets in **App settings → Secrets**:
   ```toml
   APP_PASSWORD = "your_password"
   GROQ_API_KEY = "your_key"
   ```

### Self-hosting (VM / Docker)
Run behind a reverse proxy (e.g. Nginx) with HTTPS. Remember to set both environment variables in the process environment.

---

## 🛠 Troubleshooting

### 🔴 Problems with Streamlit or the login password

If you run into **any issues starting Streamlit** (app won't launch, blank page, port problems) or have **trouble with the login / password** (can't log in, forgot the password, need access), please **send an email to**:

> ## 📧 **nurdauletsnn@gmail.com**

Please include: a short description of the problem, the exact error message (if any), and your environment (OS, Python version). This is the fastest way to get help with access and Streamlit setup.

### Other common issues

| Symptom | Likely cause & fix |
|---|---|
| `❌ Файл classified_posts.csv не найден` | Run Streamlit from the project root so `data/analyzed/classified_posts.csv` resolves. |
| AI buttons missing | `GROQ_API_KEY` not set — add it to `.env` and restart. |
| `⚠ embeddings.npy не найден → только Текстовый режим` | `data/processed/embeddings.npy` is missing; semantic search is disabled, keyword search still works. |
| Slow first load | The MiniLM embedding model is downloaded & cached on first use (`@st.cache_resource`). |
| Data looks stale | `load_data()` is cached for `ttl=300` seconds (5 min); wait or restart the app. |

---

## 🗺 Roadmap

- [ ] Pull the data-collection / NLP notebook into the repo for a fully reproducible pipeline.
- [ ] Move the single-file `app.py` into a modular package (`pages/`, `core/`, `components/`).
- [ ] Add automated tests for `apply_filters()`, `censor_text()` and the data loaders.
- [ ] Export reports to PDF / add scheduled (weekly) digest emails.
- [ ] Add topic modelling (BERTopic) alongside the current keyword extraction.
- [ ] Add role-based access (admin vs. department viewer).

---

## 📄 License & contact

This project is developed for **SDU University** — *MADRID Lab × Data Science*.

For questions, access requests, or issues with **Streamlit / the login password**, contact:

> **📧 nurdauletsnn@gmail.com**

---

<p align="center"><b>🎓 SDU Angime Analytics</b> — from student chatter to data-driven decisions.</p>

