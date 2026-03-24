import os
import pathlib
from enum import Enum


def get_api_key() -> str:
    """
    Load OpenRouter API key via 3 methods (in priority order):
      1. st.secrets["OPENROUTER_API_KEY"]  — Streamlit Cloud / local secrets.toml
      2. Direct read of .streamlit/secrets.toml — reliable local fallback
      3. OPENROUTER_API_KEY environment variable
    """
    # ── 1. Streamlit secrets ─────────────────────────────────────────────
    try:
        import streamlit as st
        key = st.secrets.get("OPENROUTER_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    # ── 2. Read secrets.toml directly (most reliable for local dev) ──────
    try:
        secrets_path = pathlib.Path(__file__).parent / ".streamlit" / "secrets.toml"
        if secrets_path.exists():
            content = secrets_path.read_text()
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY"):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key:
                        return key
    except Exception:
        pass

    # ── 3. Environment variable ──────────────────────────────────────────
    return os.environ.get("OPENROUTER_API_KEY", "")



class ProcessMode(Enum):
    SUMMARY = "summary"
    CUSTOM = "custom"


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Available free models on OpenRouter
FREE_MODELS = [
    "arcee-ai/trinity-large-preview:free",
    "arcee-ai/trinity-mini:free",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "google/gemma-3-12b-it:free",
    "google/gemma-3-27b-it:free",
    "google/gemma-3-4b-it:free",
    "google/gemma-3n-e2b-it:free",
    "google/gemma-3n-e4b-it:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "minimax/minimax-m2.5:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "openai/gpt-oss-120b:free",
    "openai/gpt-oss-20b:free",
    "qwen/qwen-3-4b:free",
    "qwen/qwen-3-coder-480b-a35b:free",
    "qwen/qwen-3-next-80b-a3b-instruct:free",
    "stepfun/step-3.5-flash:free",
    "venice/uncensored:free",
    "z-ai/glm-4.5-air:free",
]

DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

SUMMARY_PROMPT = """You are a web analyst. You have been given the real, scraped content from a website below.
Your job is to analyze ONLY this content and provide a factual, accurate summary.

IMPORTANT RULES:
- Use ONLY the information present in the content below. Do NOT guess, assume, or fabricate anything.
- If the content is about an e-commerce store, mention the actual products, brand names, prices, and categories visible.
- If the content is a blog, summarize the actual articles or topics listed.
- If the content is a service or corporate site, describe the actual services offered.
- Do NOT say generic things like "the website appears to be..." or "likely has..."
- Be specific and factual based on what you actually see in the scraped content.

Provide your summary in this structure:
1. **What This Website Is** (1-2 sentences, be specific)
2. **Main Products / Services / Topics** (list actual items found)
3. **Key Details** (prices, brands, categories, contact info, or whatever is relevant)
4. **Notable Features or Information**

SCRAPED WEBSITE CONTENT:
---
{content}
---

Now provide your factual summary based strictly on the content above."""

CUSTOM_PROMPT_TEMPLATE = """You are a web analyst. You have been given the real, scraped content from a website below.
The user wants you to: {custom_prompt}

IMPORTANT RULES:
- Use ONLY the information present in the scraped content below. Do NOT guess, assume, or fabricate anything.
- Be specific, accurate, and factual. Reference actual data from the content.
- Do NOT produce generic or placeholder answers like "[insert purpose here]" or "the website likely...".
- If the content does not contain enough information to answer the request, say exactly what you CAN see and explain what is missing.

SCRAPED WEBSITE CONTENT:
---
{content}
---

Now respond to the user's request based strictly on the content above."""
