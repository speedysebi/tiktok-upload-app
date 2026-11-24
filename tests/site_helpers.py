"""Shared helpers: parse the site's pages with the standard library only."""

from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"
PAGES = ["index.html", "terms.html", "privacy.html"]
ISSUES_URL = "https://github.com/speedysebi/tiktok-upload-app/issues"


class Page(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.styles: list[str] = []
        self.meta: dict[str, str] = {}
        self.lang = None
        self.title = ""
        self.h1: list[str] = []
        self.text: list[str] = []
        self._in = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "a" and "href" in a:
            self.links.append(a["href"])
        elif tag == "link" and a.get("rel") == "stylesheet":
            self.styles.append(a["href"])
        elif tag == "meta":
            if "charset" in a:
                self.meta["charset"] = a["charset"]
            elif "name" in a:
                self.meta[a["name"]] = a.get("content", "")
        if tag in ("title", "h1"):
            self._in = tag

    def handle_endtag(self, tag):
        if tag == self._in:
            self._in = None

    def handle_data(self, data):
        self.text.append(data)
        if self._in == "title":
            self.title += data
        elif self._in == "h1":
            self.h1.append(data.strip())


def load(name: str) -> tuple[str, Page]:
    html = (SITE / name).read_text(encoding="utf-8")
    return html, Page(html)


def internal(href: str) -> str | None:
    """The site file an internal link points to, or None for external/anchor links."""
    if href.startswith(("http://", "https://", "mailto:", "#")):
        return None
    path = href.split("#")[0]
    return "index.html" if path in ("", "./", "/") else path
