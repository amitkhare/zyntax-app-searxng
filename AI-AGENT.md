# SearXNG — AI Agent Web Search Provider

This SearXNG instance is configured to be usable by AI agents as a web search provider.

## Server

- URL: `http://127.0.0.1:8888` (bound to all interfaces, `0.0.0.0:8888`)
- Health check: `http://127.0.0.1:8888/healthz`
- Start: `SEARXNG_SETTINGS_PATH=<project>/searxng python3 searxng_wsgi.py`

## JSON API (the standard way agents query SearXNG)

```bash
curl 'http://127.0.0.1:8888/search?q=<QUERY>&format=json&language=en'
```

Returns structured JSON: `query`, `results[]` (title, url, content, engine,
publishedDate, score), `infoboxes`, `suggestions`, `answers`, `corrections`,
`unresponsive_engines`.

### Parameters agents commonly use
- `q` — search query (required)
- `format=json|rss|csv|html` — output format (json enabled)
- `language=en|de|...` — restrict results to a language
- `categories=general|news|images|...` — category to search
- `engines=google,bing,...` — only use specific engines
- `pageno=2` — pagination
- `safesearch=0|1|2` — safe search level
- `time_range=day|week|month|year` — temporal filter

### Bits used by popular agent tools
- **Open WebUI**: set *SearXNG JSON API* engine to
  `http://127.0.0.1:8888/search`.
- **LangChain / LangGraph**: use the `SearchApi`/`SearxngSearchWrapper`
  integration pointing at this base URL.
- **n8n**: HTTP Request node → GET this endpoint with `format=json`.
- **Custom agents**: plain `GET` with `format=json` (CORS enabled so
  browser-based agents work too).

## MCP (Model Context Protocol)

The official `searxng-mcp` PyPI package needs `cryptography` which does not
build on this Android environment, so the MCP bridge cannot run locally. The
JSON API above is the fallback that MCP tooling and agent frameworks use to
talk to SearXNG.

## CORS

Enabled for all origins (`Access-Control-Allow-Origin: *`) via
`searxng_wsgi.py`, so browser-based agents on other ports/origins can query
the API directly.

## Configuration

- `searxng/settings.yml` — local settings (json format enabled, binding)
- `searxng_wsgi.py` — WSGI entry with CORS middleware

## Engines

Search engines are the defaults from `searx/settings.yml`. Some engines
(google, duckduckgo, startpage, brave) may rate-limit or CAPTCHA from this
device/IP; SearXNG degrades gracefully and returns whatever engines succeed.
Relevant engines for agent use include `google cse`, `bing`, `brave` (when
not rate limited), `wikipedia`, `wikidata`, and the news/image engines.