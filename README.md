# Clip Relay site

Public website, Terms of Service and Privacy Policy for **Clip Relay**, the owner's private tool that uploads
their own edited clips to their own TikTok accounts as inbox drafts (TikTok Content Posting API, `video.upload`).
TikTok's developer portal links to these pages.

| Page | URL |
|---|---|
| Website | https://speedysebi.github.io/tiktok-upload-app/ |
| Terms of Service | https://speedysebi.github.io/tiktok-upload-app/terms.html |
| Privacy Policy | https://speedysebi.github.io/tiktok-upload-app/privacy.html |

The pages are plain HTML in `site/` (no scripts, cookies or trackers).

## CI/CD (`.github/workflows/ci.yml`)

Every push and pull request:
- **lint**: `ruff check`, `ruff format --check` (tests) and `htmlhint` (pages, rules in `.htmlhintrc`)
- **test**: unit tests (`tests/test_site.py`: structure, links, required policy content, no email addresses or
  draft leftovers) and a local smoke test (`tests/test_smoke.py`: serves `site/` over HTTP, fetches every page/link)

On `main`, after both pass:
- **deploy**: publishes `site/` to GitHub Pages
- **smoke-live**: runs the smoke test against the live site

## Run locally

```sh
uv venv && uv pip install -r requirements-dev.txt   # or: python -m venv .venv && pip install -r requirements-dev.txt
.venv/bin/ruff check . && .venv/bin/ruff format --check .
npx --yes htmlhint@1.1.4 site/*.html
.venv/bin/pytest -v
SITE_URL=https://speedysebi.github.io/tiktok-upload-app/ .venv/bin/pytest tests/test_smoke.py   # live check
```

## Editing the policies

Change the page, update its "Last updated" date (a test checks the format), push to `main`.
