# SearXNG

[SearXNG](https://searxng.org) is a free, privacy-respecting metasearch engine.
It aggregates results from dozens of search engines (Google, Bing, Brave,
Wikipedia, Wikidata, DuckDuckGo, …) without tracking or profiling its users.

This checkout is configured as an **AI-agent-friendly SearXNG instance**: the
JSON API is enabled, CORS is open to all origins, and a small WSGI wrapper
(`searxng_wsgi.py`) makes it easy to point agent tools (Open WebUI, LangChain,
n8n, custom agents) at it.

## What's in this repo

| Path | Purpose |
| --- | --- |
| `searx/` | The SearXNG application itself (engines, webapp, templates) |
| `searx/settings.yml` | Default upstream settings |
| `searxng/settings.yml` | Local settings: port `8888`, JSON API enabled, limiter off |
| `searxng_wsgi.py` | CORS-enabled WSGI entry point (`application`) + dev runner |
| `AI-AGENT.md` | How to wire AI agents to this instance (JSON API, MCP notes) |
| `requirements.txt` | Python runtime dependencies |
| `requirements-server.txt` | Optional production server (Granian) |

## How to run it

### Prerequisites

- Python 3.11+ (developed and tested here on Python 3.14)
- `pip`

### 1. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

For the optional Granian production server:

```bash
python3 -m pip install -r requirements-server.txt
```

### 2. Start the server (development)

From the project root:

```bash
SEARXNG_SETTINGS_PATH=searxng python3 searxng_wsgi.py
```

- `SEARXNG_SETTINGS_PATH=searxng` loads the local `searxng/settings.yml`
  (port `8888`, `bind_address: 0.0.0.0`, JSON API enabled).
  Without it, SearXNG falls back to the defaults in `searx/settings.yml`.
- The dev runner serves through the CORS middleware, threaded, on
  **`http://0.0.0.0:8888`**.

### 3. Verify it's up

```bash
curl http://127.0.0.1:8888/healthz          # health check
curl http://127.0.0.1:8888/                 # HTML UI
```

### 4. Try a search

HTML UI — open <http://127.0.0.1:8888/> in a browser.

JSON API (what AI agents use):

```bash
curl 'http://127.0.0.1:8888/search?q=searxng&format=json&language=en'
```

Common parameters:

| Parameter | Example | Meaning |
| --- | --- | --- |
| `q` | `q=metasearch` | Query (required) |
| `format` | `format=json` | `json`, `rss`, `csv`, `html` |
| `language` | `language=en` | Restrict results to a language |
| `categories` | `categories=general` | `general`, `news`, `images`, … |
| `engines` | `engines=google,bing` | Only use specific engines |
| `pageno` | `pageno=2` | Pagination |
| `safesearch` | `safesearch=1` | `0`, `1`, `2` |
| `time_range` | `time_range=week` | `day`, `week`, `month`, `year` |

The JSON response includes `query`, `results[]` (title, url, content, engine,
publishedDate, score), `infoboxes`, `suggestions`, `answers`, `corrections`,
and `unresponsive_engines`.

### Production (optional)

Serve the WSGI app `searxng_wsgi:application` with a real WSGI server, e.g.
with the bundled Granian:

```bash
python3 -m granian --interface wsgi --host 0.0.0.0 --port 8888 searxng_wsgi:application
```

or any other WSGI server (gunicorn, uwsgi, waitress) pointed at the same
target. Put nginx/apache in front of it if you need TLS and a public URL.

## Notes

- Some engines (Google, DuckDuckGo, Startpage, Brave) may rate-limit or
  CAPTCHA depending on the outgoing IP. SearXNG degrades gracefully and
  returns whatever engines succeed; check the server logs for
  `unresponsive_engines` details.
- Rate-limiting (`server.limiter`), secret key, and binding are configured in
  `searxng/settings.yml`. Generate a proper random `secret_key` before
  exposing the instance publicly.
- Upstream installation and configuration guides:
  <https://docs.searxng.org/admin/installation.html>

## License

GNU Affero General Public License v3.0 — see [LICENSE](LICENSE).