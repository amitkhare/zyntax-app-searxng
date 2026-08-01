#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
"""AI-agent friendly WSGI wrapper around the SearXNG Flask app.

Adds permissive CORS headers so browser-based AI agents (e.g. Open WebUI,
local agent UIs) can call this SearXNG instance directly from other origins.

Run with:  python3 searxng_wsgi.py
Or serve with any WSGI server:  module=searxng_wsgi:application
"""

from searx.webapp import app

_ALLOW_ORIGIN = "*"


class CorsMiddleware:
    """WSGI middleware that appends CORS headers to every response."""

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        def cors_headers(status, headers, exc_info=None):
            headers = list(headers)
            headers.extend(
                [
                    ("Access-Control-Allow-Origin", _ALLOW_ORIGIN),
                    ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
                    ("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With"),
                    ("Access-Control-Max-Age", "86400"),
                ]
            )
            return start_response(status, headers, exc_info)

        if environ.get("REQUEST_METHOD") == "OPTIONS":
            # Preflight request: answer immediately.
            start_response("204 No Content", [("Access-Control-Allow-Origin", _ALLOW_ORIGIN),
                                              ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
                                              ("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With"),
                                              ("Access-Control-Max-Age", "86400"),
                                              ("Content-Length", "0")])
            return [b""]

        return self.wsgi_app(environ, cors_headers)


application = CorsMiddleware(app)

if __name__ == "__main__":
    # Local development runner that serves through the CORS middleware.
    # Use a real WSGI server (e.g. gunicorn/uwsgi: searxng_wsgi:application) in production.
    from werkzeug.serving import run_simple

    run_simple("0.0.0.0", 8888, application, threaded=True)
