"""Unit tests: page structure, links and the content TikTok's app review looks for."""

import re

import pytest

from site_helpers import ISSUES_URL, PAGES, SITE, internal, load


@pytest.mark.parametrize("name", PAGES)
def test_page_basics(name):
    html, p = load(name)
    assert html.lower().startswith("<!doctype html>")
    assert p.lang == "en"
    assert p.meta.get("charset", "").lower() == "utf-8"
    assert "width=device-width" in p.meta.get("viewport", "")
    assert p.meta.get("description")
    assert "Clip Relay" in p.title
    assert len(p.h1) == 1 and p.h1[0]


@pytest.mark.parametrize("name", PAGES)
def test_internal_links_and_assets_exist(name):
    _, p = load(name)
    for href in p.links + p.styles:
        target = internal(href)
        if target:
            assert (SITE / target).is_file(), f"{name}: broken link {href}"


@pytest.mark.parametrize("name", PAGES)
def test_every_page_links_terms_and_privacy(name):
    _, p = load(name)
    assert "terms.html" in p.links and "privacy.html" in p.links


@pytest.mark.parametrize("name", PAGES)
def test_external_links_are_https(name):
    _, p = load(name)
    assert all(not h.startswith("http://") for h in p.links)


@pytest.mark.parametrize("name", ["terms.html", "privacy.html"])
def test_policies_have_date_and_contact(name):
    _, p = load(name)
    text = " ".join(p.text)
    assert re.search(r"Last updated: [A-Z][a-z]+ \d{1,2}, \d{4}", text)
    assert ISSUES_URL in p.links


def test_privacy_names_the_scopes_and_storage():
    _, p = load("privacy.html")
    text = " ".join(p.text)
    for must in ("user.info.basic", "video.upload", "does not sell", "owner's own computer"):
        assert must in text


def test_terms_say_drafts_only_and_not_tiktok():
    _, p = load("terms.html")
    text = " ".join(" ".join(p.text).split())
    assert "never publishes anything by itself" in text
    assert "not made, endorsed or supported by TikTok" in text


@pytest.mark.parametrize("name", PAGES)
def test_no_drafts_placeholders_or_personal_data(name):
    html, _ = load(name)
    assert "[date" not in html and "Draft" not in html and "TODO" not in html
    assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", html), "no email addresses on the public site"


def test_app_name_has_no_tiktok():
    _, p = load("index.html")
    assert "tiktok" not in p.h1[0].lower()


def test_site_has_nojekyll_and_no_trackers():
    assert (SITE / ".nojekyll").exists()
    for name in PAGES:
        html, _ = load(name)
        assert "<script" not in html.lower()
