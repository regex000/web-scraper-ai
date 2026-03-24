import streamlit as st
from config import ProcessMode, FREE_MODELS, DEFAULT_MODEL
from scraper import WebScraper
from processor import AIProcessor
from pdf_generator import PDFGenerator
from datetime import datetime

st.set_page_config(
    page_title="Web Summary & Data Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { padding: 2rem; }
    .result-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        line-height: 1.7;
    }
    .crawl-info {
        background: #1e3a5f;
        border-left: 4px solid #4ea8de;
        padding: 0.8rem 1.2rem;
        border-radius: 4px;
        margin: 0.5rem 0;
        color: #cce4f7;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 Web Summary & Data Extractor")
st.markdown("Extract and summarize web content using AI-powered analysis")

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    mode = st.radio(
        "Processing Mode",
        [ProcessMode.SUMMARY.value, ProcessMode.CUSTOM.value],
        format_func=lambda x: "📝 Summary" if x == "summary" else "🎯 Custom Prompt"
    )

    st.divider()
    st.markdown("**🕷️ Crawl Mode**")
    crawl_enabled = st.toggle(
        "Crawl entire website",
        value=False,
        help="Scrape multiple pages of the site (finds subpages like /contact, /about, etc.)"
    )
    if crawl_enabled:
        max_pages = st.slider(
            "Max pages to crawl",
            min_value=2, max_value=10, value=5, step=1,
            help="How many pages to visit (more = slower but more complete)"
        )
    else:
        max_pages = 1

    st.divider()
    model = st.selectbox(
        "AI Model",
        FREE_MODELS,
        index=0,
        help="Select from available free models"
    )

    st.divider()
    st.markdown("**About**")
    st.info(
        "Uses **Jina AI Reader** for JS-rendered pages + "
        "BeautifulSoup fallback.\n\n"
        "Enable **Crawl Mode** to scan multiple pages of a website."
    )

# ── Main content ────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    url = st.text_input(
        "🔗 Website URL",
        placeholder="https://example.com",
        help="Enter the URL of the website to analyze",
        value=""
    )

with col2:
    st.write("")
    st.write("")
    process_button = st.button("🚀 Process", use_container_width=True)

# Custom prompt
if mode == ProcessMode.CUSTOM.value:
    custom_prompt = st.text_area(
        "📝 Custom Prompt",
        placeholder="What would you like to extract or analyze from this website?",
        height=100
    )
else:
    custom_prompt = None

# ── Crawl info banner ───────────────────────────────────────────────────────
if crawl_enabled:
    st.markdown(
        f'<div class="crawl-info">🕷️ <b>Crawl Mode ON</b> — will visit up to '
        f'<b>{max_pages} pages</b> of the website (homepage + internal links)</div>',
        unsafe_allow_html=True
    )

# ── Processing logic ─────────────────────────────────────────────────────────
if process_button:
    if not url or url.strip() == "":
        st.error("❌ Please enter a URL to process")
    else:
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            scraper = WebScraper()
            processor = AIProcessor(model)
            pdf_gen = PDFGenerator()

            # ── Scrape ──────────────────────────────────────────────────
            if crawl_enabled:
                with st.spinner(f"🕷️ Crawling website (up to {max_pages} pages)…"):
                    content = scraper.crawl_website(url, max_pages=max_pages)
            else:
                with st.spinner("📥 Fetching page content…"):
                    content = scraper.fetch_content(url)

            metadata = scraper.get_metadata(url)

            # ── Content validation ───────────────────────────────────────
            if not content or len(content.strip()) < 80:
                st.warning(
                    "⚠️ Very little content could be scraped. "
                    "The site may block scrapers or be fully client-side rendered. "
                    "Try enabling Crawl Mode or a different URL."
                )

            # ── AI Processing ────────────────────────────────────────────
            with st.spinner("🤖 Analyzing with AI…"):
                mode_enum = ProcessMode.CUSTOM if mode == ProcessMode.CUSTOM.value else ProcessMode.SUMMARY
                result = processor.process(content, mode_enum, custom_prompt)

            st.success("✅ Processing complete!")

            # ── Scraped content preview ──────────────────────────────────
            with st.expander("🔍 View Scraped Content (what AI received)", expanded=False):
                st.text_area(
                    "Raw scraped content:",
                    value=content if content else "(No content extracted)",
                    height=250,
                    disabled=True
                )
                st.caption(f"Total characters scraped: {len(content)}")

            # ── Metadata ─────────────────────────────────────────────────
            st.markdown("### 📋 Source Information")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Title:** {metadata['title']}")
            with col2:
                st.markdown(f"**Model:** {model}")

            st.divider()

            # ── Results ──────────────────────────────────────────────────
            st.markdown("### 📊 Results")
            st.markdown(f"""
            <div class="result-box">
                {result.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            # ── Downloads ─────────────────────────────────────────────────
            col1, col2, col3 = st.columns(3)

            with col1:
                pdf_bytes = pdf_gen.generate(metadata['title'], url, result, mode)
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            with col2:
                txt_content = f"""Web Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
URL: {url}
Mode: {mode.upper()}{'  [Crawl: ' + str(max_pages) + ' pages]' if crawl_enabled else ''}
Model: {model}

RESULTS:
{result}"""
                st.download_button(
                    label="📄 Download TXT",
                    data=txt_content,
                    file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with col3:
                st.info("✨ More formats coming soon!")

        except Exception as e:
            st.error(f"❌ Error processing URL: {str(e)}")

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.9rem; margin-top: 2rem;'>
    <p>Web Summary v2.0 | Powered by Jina AI Reader + OpenRouter API</p>
</div>
""", unsafe_allow_html=True)
