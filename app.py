"""Reel: portfolio chatbot backend (Flask + OpenRouter), Render-ready.

Local:   python app.py   then open http://127.0.0.1:5000
Render:  gunicorn app:app  (see render.yaml)
"""

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_from_directory, stream_with_context
from flask_cors import CORS

from knowledge import BOT_NAME, PORTFOLIO_URL, SYSTEM_PROMPT

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip()

# Comma-separated list of sites allowed to call this API from a browser.
# Example: https://kirransuleman-portfolio.netlify.app
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "https://kirransuleman-portfolio.netlify.app,http://127.0.0.1:5000,http://localhost:5000",
    ).split(",")
    if o.strip()
]

MAX_HISTORY = 12  # most recent messages sent to the model
MAX_CHARS = 2000  # per message

app = Flask(__name__, static_folder=str(BASE_DIR / "static"), static_url_path="/static")
CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    """Used by Render's health check."""
    return jsonify(status="ok")


@app.get("/api/info")
def info():
    return jsonify(name=BOT_NAME, model=MODEL, configured=bool(API_KEY))


def clean_history(raw):
    """Keep only well-formed user/assistant messages, trimmed in size and count."""
    if not isinstance(raw, list):
        return []
    messages = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        role, content = item.get("role"), item.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content.strip()[:MAX_CHARS]})
    return messages[-MAX_HISTORY:]


ERROR_HINTS = {
    401: "The OpenRouter API key was rejected. Check OPENROUTER_API_KEY in your Render environment variables.",
    402: "Your OpenRouter account is out of credits. Add credits or switch to a free model.",
    404: "That model was not found. Check OPENROUTER_MODEL in your Render environment variables.",
    429: "OpenRouter is rate limiting requests. Wait a moment and try again.",
}


@app.post("/api/chat")
def chat():
    if not API_KEY:
        return jsonify(error="No API key found. Add OPENROUTER_API_KEY in Render environment variables and redeploy."), 500

    payload = request.get_json(silent=True) or {}
    history = clean_history(payload.get("messages"))
    if not history or history[-1]["role"] != "user":
        return jsonify(error="Send at least one user message."), 400

    body = {
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *history],
        "stream": True,
        "temperature": 0.6,
        "max_tokens": 600,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": PORTFOLIO_URL,
        "X-Title": f"{BOT_NAME} - portfolio assistant",
    }

    try:
        upstream = requests.post(OPENROUTER_URL, headers=headers, json=body, stream=True, timeout=60)
    except requests.RequestException:
        return jsonify(error="Could not reach OpenRouter. Please try again."), 502

    if upstream.status_code != 200:
        message = ERROR_HINTS.get(upstream.status_code)
        if not message:
            try:
                message = upstream.json().get("error", {}).get("message", "OpenRouter returned an error.")
            except ValueError:
                message = "OpenRouter returned an error."
        upstream.close()
        return jsonify(error=message), 502

    def generate():
        try:
            for raw_line in upstream.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8", errors="replace")
                if not line.startswith("data:"):
                    continue  # skips OpenRouter keep-alive comments
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if "error" in chunk:
                    yield "\n\n(The response was interrupted. Please try again.)"
                    break
                choices = chunk.get("choices") or [{}]
                delta = (choices[0].get("delta") or {}).get("content")
                if delta:
                    yield delta
        except requests.RequestException:
            yield "\n\n(Connection lost. Please try again.)"
        finally:
            upstream.close()

    return Response(
        stream_with_context(generate()),
        mimetype="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    # Local development only. On Render, gunicorn runs the app instead.
    if not API_KEY:
        print("Warning: OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your key.")
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=os.getenv("FLASK_DEBUG", "1") == "1")
