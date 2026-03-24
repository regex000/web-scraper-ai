# 🌐 Web Summary & Data Extractor — AI-Powered Website Intelligence in Your Browser

> *Extract, summarize, and deeply analyze any website in seconds — even JavaScript-heavy SPAs — using free AI models and smart multi-page crawling.*

---

## The Problem I Was Solving

You've been there. You land on a website and want to quickly understand:

- What does this company actually do?
- What products or prices are listed?
- What's the contact information?
- Can you summarize this entire site in one paragraph?

Manually reading through pages is slow. Copy-pasting into ChatGPT is tedious. And most scraping tools fail the moment a site is built with React or Next.js.

I built **Web Summary & Data Extractor** to solve exactly this — a clean, intelligent tool that visits a website (or its entire link structure), extracts the real content, and sends it to a powerful AI model to answer your questions accurately.

---

## What It Does

At its core, this is a **Streamlit web app** that combines two powerful ideas:

1. **Smart Web Scraping** — uses [Jina AI Reader](https://jina.ai/reader/) to render JavaScript-heavy pages that BeautifulSoup alone can't handle
2. **AI Analysis via OpenRouter** — routes your content to any of 27+ free LLM models to summarize or answer custom questions

### Key Features

| Feature | Description |
|---|---|
| 🕷️ **Multi-Page Crawl Mode** | Discovers and visits internal links — finds `/contact`, `/about`, `/products` automatically |
| 🤖 **27+ Free AI Models** | Includes Llama 3.3 70B, Gemma 3, Mistral, Qwen, NVIDIA Nemotron and more |
| 📝 **Summary Mode** | Structured breakdown: what the site is, products/services, key details |
| 🎯 **Custom Prompt Mode** | Ask anything — *"find the phone number"*, *"list all prices"*, *"what stack do they use?"* |
| 📥 **PDF & TXT Export** | Download your results as a formatted PDF or plain text file |
| 🔍 **Scraped Content Preview** | See exactly what the AI received — full transparency |

---

## How It Works

```
User enters URL
      │
      ▼
┌─────────────────────────────────┐
│   Jina AI Reader                │  ← Renders JS, returns clean text
│   r.jina.ai/https://your-url   │     (free, no API key needed)
└─────────────────────────────────┘
      │
      │  (if Crawl Mode ON)
      ▼
┌─────────────────────────────────┐
│   Link Discovery                │  ← Static HTML scrape for <a> tags
│   Visits up to 10 sub-pages     │     then fetches each via Jina
└─────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────┐
│   OpenRouter API                │  ← Sends scraped content + prompt
│   Your chosen free LLM model   │     to AI for analysis
└─────────────────────────────────┘
      │
      ▼
   Results + PDF/TXT Download
```

### Why Jina AI Reader?

Most modern websites — e-commerce stores, portfolios, SaaS landing pages — are built with React, Vue, or Next.js. Their HTML source is just `<div id="root"></div>` until JavaScript runs. BeautifulSoup (the classic Python scraper) sees nothing.

[Jina AI Reader](https://r.jina.ai/) solves this by rendering the page on their servers and returning clean, readable text. The best part? It's **completely free**, requires **no API key**, and works with a simple HTTP GET:

```
GET https://r.jina.ai/https://yourwebsite.com
```

No Selenium. No Playwright. No headless Chrome to manage. Just a plain `requests.get()`.

### Why OpenRouter?

[OpenRouter](https://openrouter.ai) is an API aggregator that gives you access to dozens of AI models — including many **completely free** ones — through a single unified API endpoint. No need to sign up separately for Groq, Together AI, or Hugging Face.

Free models available include:
- `meta-llama/llama-3.3-70b-instruct:free` *(great for reasoning)*
- `google/gemma-3-27b-it:free`
- `mistralai/mistral-small-3.1-24b-instruct:free`
- `qwen/qwen-3-coder-480b-a35b:free`
- And 23 more...

---

## Live Demo: Real Results

Here's what happens when you run **Crawl Mode** on `https://rokonai.me/` with the prompt *"find the phone number and email"*:

**Without Crawl Mode** (homepage only):
> *"No phone number or email address present on this page."*
> *(The homepage doesn't have contact info — correct, but incomplete)*

**With Crawl Mode** (visits `/contact` automatically):
> *"Phone: +8801646617990 | Email: mdrokon@hotmail.com"*
> *(Found on the /contact page)*

That's the difference between scraping one page and crawling a website.

---

## Tech Stack

```
Backend        Python 3.x
UI Framework   Streamlit
Web Scraping   Jina AI Reader (primary) + BeautifulSoup4 (fallback)
AI Models      OpenRouter API (27+ free models)
PDF Export     ReportLab
Deployment     Streamlit Community Cloud
```

**Dependencies** (`requirements.txt`):
```
streamlit==1.55.0
beautifulsoup4==4.14.3
requests==2.32.5
reportlab==4.4.10
```

No Selenium. No Playwright. No headless browser. The entire scraping pipeline runs on just `requests` and `beautifulsoup4`.

---

## Running It Locally

### 1. Clone the repo

```bash
git clone https://github.com/regex000/web-scraper-ai.git
cd web-scraper-ai
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add your OpenRouter API key

Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys), then create:

```toml
# .streamlit/secrets.toml
OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
```

Or just paste it directly into the **🔑 API Key** field in the app sidebar.

### 4. Run the app

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501` 🎉

---

## Deploying to Streamlit Community Cloud

This app is **production-ready** for [Streamlit Community Cloud](https://share.streamlit.io) — free hosting for public Streamlit apps.

### Steps

1. Push your code to GitHub (the `.gitignore` already protects `secrets.toml`)
2. Go to [share.streamlit.io/deploy](https://share.streamlit.io/deploy)
3. Select your repo → branch `main` → file `app.py`
4. Click **Advanced settings → Secrets** and paste:

```toml
OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
```

5. Click **Deploy** — your app goes live in ~60 seconds ✅

> ⚠️ **Security Note:** Never commit your API key to GitHub. This repo uses `.gitignore` to exclude `.streamlit/secrets.toml`. On Streamlit Cloud, set the key via the Secrets UI — it's encrypted and never exposed in logs.

---

## Project Structure

```
web-scraper-ai/
├── app.py              # Main Streamlit UI + routing logic
├── scraper.py          # Jina AI Reader + BeautifulSoup scraper + crawler
├── processor.py        # OpenRouter API client + prompt formatting
├── config.py           # Models list, prompts, API key loader
├── pdf_generator.py    # ReportLab PDF export
├── requirements.txt    # Python dependencies
├── .gitignore          # Protects secrets, venv, __pycache__
└── .streamlit/
    └── secrets.toml    # Local API key (gitignored — never pushed)
```

---

## Design Decisions

### Why not Selenium/Playwright?

Headless browsers are heavyweight. They require binary installations (Chrome/Firefox), don't work out-of-the-box on many hosted platforms, and are overkill for content extraction. Jina AI Reader gives you **rendered HTML via a single HTTP call** with zero setup — perfect for a hosted lightweight app.

### Why Streamlit over Flask/FastAPI?

Streamlit lets you build a fully interactive data app with Python only — no HTML/CSS/JS templates, no frontend/backend split. For a tool like this, where the UX is entirely about inputs and results, Streamlit is the leanest path to a great UI.

### Why OpenRouter over direct Model APIs?

A single API key. A single endpoint. 27+ free models. If one model is rate-limited or down, switch in one click. OpenRouter abstracts away all provider-specific authentication and formatting.

---

## What's Next

Here are features planned for future versions:

- [ ] **Scheduled monitoring** — re-scrape a URL on a schedule and alert on changes
- [ ] **Multiple URL batch mode** — analyze a list of URLs at once
- [ ] **Competitor analysis template** — compare two companies side by side
- [ ] **JSON / CSV export** — structured data output for developers
- [ ] **Chat mode** — ask follow-up questions about the scraped content

---

## Source Code

📦 **GitHub:** [github.com/regex000/web-scraper-ai](https://github.com/regex000/web-scraper-ai)

🚀 **Live App:** Deployed on [Streamlit Community Cloud](https://share.streamlit.io)

---

*Built with ❤️ by [Md. Rokon](https://rokonai.me) — Software Engineer & AI Developer based in Dhaka, Bangladesh.*

*Feel free to fork, use, and improve. If you find it useful, a ⭐ on GitHub goes a long way!*
