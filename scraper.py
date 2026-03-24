import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

JINA_READER_BASE = "https://r.jina.ai/"


class WebScraper:
    def __init__(self, timeout=20):
        self.timeout = timeout
        self.static_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.jina_headers = {
            "Accept": "text/plain",
            "X-Return-Format": "text",
            "X-Timeout": "15",
        }

    # ------------------------------------------------------------------ #
    #  PUBLIC: fetch_content  (single page)                               #
    # ------------------------------------------------------------------ #
    def fetch_content(self, url: str) -> str:
        """Fetch a single page via Jina AI Reader (handles JS/SPAs). Falls back to static."""
        content = self._fetch_via_jina(url)
        if content and len(content.strip()) >= 100:
            return content[:8000]

        fallback = self._fetch_static_text(url)
        if fallback and len(fallback.strip()) >= 50:
            return ("[Static HTML only — JS content may be missing]\n\n" + fallback)[:8000]

        return ""

    # ------------------------------------------------------------------ #
    #  PUBLIC: crawl_website  (multi-page crawl)                         #
    # ------------------------------------------------------------------ #
    def crawl_website(self, root_url: str, max_pages: int = 5) -> str:
        """
        Crawl root_url + discover and scrape its internal links.
        Returns combined content from all scraped pages (up to max_pages).
        """
        root_domain = urlparse(root_url).netloc
        visited = set()
        pages_data = []

        # Internal queue — start with root + explicitly known sub-pages
        queue = [root_url]

        # Discover internal links from the static HTML of root (fast, no Jina needed)
        internal_links = self._discover_links(root_url, root_domain)
        for link in internal_links:
            if link not in queue:
                queue.append(link)

        for url in queue:
            if url in visited:
                continue
            if len(pages_data) >= max_pages:
                break

            visited.add(url)
            content = self.fetch_content(url)
            if content and len(content.strip()) > 50:
                path = urlparse(url).path or "/"
                pages_data.append(f"=== PAGE: {path} ===\n{content}")

        if not pages_data:
            return ""

        combined = "\n\n".join(pages_data)
        return combined[:12000]  # Generous limit for multi-page

    # ------------------------------------------------------------------ #
    #  INTERNAL LINK DISCOVERY                                            #
    # ------------------------------------------------------------------ #
    def _discover_links(self, url: str, root_domain: str) -> list:
        """
        Fetch static HTML of a page and return same-domain internal links.
        Uses static HTML because it's faster and link discovery doesn't need JS.
        """
        found = []
        try:
            response = requests.get(url, headers=self.static_headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, "html.parser")

            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                # Skip anchors, mailto, tel, javascript
                if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                    continue
                absolute = urljoin(url, href)
                parsed = urlparse(absolute)
                # Keep only same-domain HTTP(S) links
                if parsed.netloc == root_domain and parsed.scheme in ("http", "https"):
                    # Normalize: strip query/fragment for deduplication
                    clean = parsed._replace(query="", fragment="").geturl()
                    if clean not in found and clean != url:
                        found.append(clean)
        except Exception:
            pass

        return found

    # ------------------------------------------------------------------ #
    #  JINA AI READER  (primary: handles JS-rendered SPAs)               #
    # ------------------------------------------------------------------ #
    def _fetch_via_jina(self, url: str) -> str:
        """Call https://r.jina.ai/<url> — renders JS, returns clean text. Free & keyless."""
        try:
            response = requests.get(
                JINA_READER_BASE + url,
                headers=self.jina_headers,
                timeout=self.timeout,
            )
            if response.status_code == 200:
                text = response.text.strip()
                # Strip Jina header lines (Title:, URL:, Description:)
                skip = ("Title:", "URL:", "Published Time:", "Description:", "Warning:")
                lines = [
                    l for l in text.split("\n")
                    if not any(l.strip().startswith(p) for p in skip)
                ]
                return self._clean_text("\n".join(lines))
        except Exception:
            pass
        return ""

    # ------------------------------------------------------------------ #
    #  BEAUTIFULSOUP FALLBACK                                             #
    # ------------------------------------------------------------------ #
    def _fetch_static_text(self, url: str) -> str:
        """Classic static HTML scrape — fallback when Jina fails."""
        try:
            response = requests.get(url, headers=self.static_headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            parts = []
            title = soup.find("title")
            if title and title.string:
                parts.append(f"Title: {title.string.strip()}")

            for meta in soup.find_all("meta"):
                name = meta.get("name", "").lower()
                content = meta.get("content", "").strip()
                if content and name in ("description", "keywords"):
                    parts.append(f"Meta {name}: {content}")

            for tag in soup(["script", "style", "noscript", "iframe", "svg"]):
                tag.decompose()

            body = soup.find("body")
            if body:
                parts.append(self._clean_text(body.get_text(separator="\n", strip=True)))

            return "\n\n".join(parts)
        except Exception:
            return ""

    # ------------------------------------------------------------------ #
    #  METADATA                                                           #
    # ------------------------------------------------------------------ #
    def get_metadata(self, url: str) -> dict:
        """Extract page title and description."""
        title, description = "No title", ""
        try:
            response = requests.get(
                JINA_READER_BASE + url, headers=self.jina_headers, timeout=self.timeout
            )
            if response.status_code == 200:
                for line in response.text.split("\n")[:15]:
                    s = line.strip()
                    if s.startswith("Title:"):
                        title = s[len("Title:"):].strip()
                    elif s.startswith("Description:"):
                        description = s[len("Description:"):].strip()
                if title and title != "No title":
                    return {"title": title, "description": description, "url": url}
        except Exception:
            pass

        try:
            response = requests.get(url, headers=self.static_headers, timeout=self.timeout)
            soup = BeautifulSoup(response.content, "html.parser")
            t = soup.find("title")
            og = soup.find("meta", attrs={"property": "og:title"})
            md = soup.find("meta", attrs={"name": "description"})
            title = (og.get("content") if og else None) or \
                    (t.string.strip() if t and t.string else "No title")
            description = md.get("content", "") if md else ""
        except Exception:
            pass
        return {"title": title, "description": description, "url": url}

    # ------------------------------------------------------------------ #
    #  HELPERS                                                            #
    # ------------------------------------------------------------------ #
    def _clean_text(self, text: str) -> str:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        deduped, prev = [], None
        for line in lines:
            if line != prev:
                deduped.append(line)
                prev = line
        return "\n".join(deduped)
