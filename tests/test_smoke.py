"""Smoke test: serve the site over HTTP and fetch every page and internal link.

SITE_URL=https://... runs the same checks against the deployed site instead of a local server.
"""

import functools
import http.server
import os
import threading
import urllib.request
from urllib.parse import urljoin

import pytest

from site_helpers import PAGES, SITE, Page, internal


@pytest.fixture(scope="module")
def base_url():
    if os.environ.get("SITE_URL"):
        yield os.environ["SITE_URL"].rstrip("/") + "/"
        return
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    handler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}/"
    srv.shutdown()


def fetch(url: str):
    with urllib.request.urlopen(url, timeout=20) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read().decode("utf-8")


@pytest.mark.parametrize("name", ["", *PAGES])
def test_page_served(base_url, name):
    status, ctype, body = fetch(urljoin(base_url, name))
    assert status == 200 and ctype.startswith("text/html")
    assert "Clip Relay" in body


@pytest.mark.parametrize("name", PAGES)
def test_links_resolve_over_http(base_url, name):
    _, _, body = fetch(urljoin(base_url, name))
    p = Page(body)
    for href in p.links + p.styles:
        if internal(href):
            status, _, _ = fetch(urljoin(urljoin(base_url, name), href))
            assert status == 200, href


def test_stylesheet_served(base_url):
    status, ctype, _ = fetch(urljoin(base_url, "style.css"))
    assert status == 200 and "css" in ctype
