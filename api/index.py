"""Vercel serverless entry point for the Tic-Tac-Toe API."""

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from server import BadRequest, handle_play


def app(environ, start_response):
    """WSGI application used by Vercel's Python runtime."""
    if environ.get("REQUEST_METHOD") != "POST":
        return _response(start_response, "405 Method Not Allowed",
                         {"error": "method not allowed."})

    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
        data = json.loads(environ["wsgi.input"].read(length) or b"{}")
        payload = handle_play(data)
        return _response(start_response, "200 OK", payload)
    except BadRequest as error:
        return _response(start_response, "400 Bad Request", {"error": str(error)})
    except (ValueError, TypeError, json.JSONDecodeError):
        return _response(start_response, "400 Bad Request",
                         {"error": "request body must be valid JSON."})


def _response(start_response, status, payload):
    body = json.dumps(payload).encode("utf-8")
    start_response(status, [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store"),
    ])
    return [body]
