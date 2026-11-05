# Reel: portfolio chatbot for Kirran Suleman

Flask (Python 3.11.9) backend, OpenRouter API, plain HTML/CSS/JS frontend.

## Run it in VS Code (Windows)

1. Install Python 3.11.9 and open this folder in VS Code (File > Open Folder).
2. Open the terminal (Ctrl+`) and create a virtual environment:
   ```
   py -3.11 -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   On macOS/Linux: `python3.11 -m venv .venv && source .venv/bin/activate`.
3. Press Ctrl+Shift+P, choose **Python: Select Interpreter**, and pick `.venv`.
4. Copy `.env.example` to `.env` and paste your OpenRouter key (https://openrouter.ai/keys).
5. Run `python app.py` (or press F5) and open http://127.0.0.1:5000

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Flask server, streams replies from OpenRouter |
| `knowledge.py` | Portfolio data and system prompt. Edit `PROFILE` to update what Reel knows |
| `static/index.html` | Chat page |
| `static/style.css` | Theme (colors are variables at the top; light and dark modes) |
| `static/script.js` | Chat logic, streaming, theme toggle |

## Customizing

- **Colors:** change `--primary` and `--accent` at the top of `static/style.css` to your portfolio's exact hex values.
- **Model:** set `OPENROUTER_MODEL` in `.env` (any slug from https://openrouter.ai/models).
- **Knowledge:** add details (email, rates, new projects, experience dates) to `PROFILE` in `knowledge.py`. Reel will not invent anything that is not there.
