# AI Report Studio

Upload a CSV/JSON dataset and generate an AI-written report from a template.

## What it does

AI Report Studio turns a raw data file into a readable Markdown report in three
steps:

1. **You upload data** — a CSV or JSON file.
2. **Python computes the facts** — the app calculates summary statistics
   (count, sum, average, minimum, maximum) for every numeric column in your
   data.
3. **A Gemini model writes the prose** — those statistics are sent to Google's
   Gemini model, which writes a professional Markdown report in the style of the
   template you chose.

The guiding principle is: **Python does the facts, the model does the language.**
The numbers are always computed deterministically in Python, and the language
model only writes the surrounding narrative — it never invents or recomputes
figures.

If the AI is unavailable (no API key set, or the call fails), the app
**gracefully falls back** to a templated report built directly from the
computed statistics, so you always get a usable report.

## Setup

You need Python 3.10+ installed.

1. Create and activate a virtual environment:

   ```powershell
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\activate
   ```

   ```bash
   # macOS / Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure your API key. Copy the example environment file and edit it:

   ```bash
   cp .env.example .env
   ```

   Then open `.env` and set your key:

   ```
   GEMINI_API_KEY=your_real_key_here
   MODEL_NAME=gemini-1.5-flash   # optional, this is the default
   ```

   The `.env` file is **gitignored** and should never be committed. You can run
   the app without a key — it will use the templated fallback instead of the AI.

## Run

Start the backend server:

```bash
uvicorn main:app --reload
```

The backend serves the frontend, so the easiest way to open the app is at
**`http://localhost:8000`** in your browser — the `main.py` app serves
`index.html` at `/`, along with `style.css` and `app.js`. You can also open
`index.html` directly as a `file://` page; the API has CORS enabled for
`localhost`, `127.0.0.1`, and `file://` origins, so either way works. The
frontend JavaScript calls the API at `http://localhost:8000` via `fetch`.
**The backend must be running** for the UI to work — uploads, template loading,
and report generation will fail until the API is up on that port.

## Usage (web UI)

1. **Upload a dataset** — click *Upload* and choose a `.csv` or `.json` file.
   You'll see the filename and row count once it's accepted.
2. **Choose a template** — pick one of the available templates from the
   dropdown (e.g. `executive_summary`, `incident_report`, `weekly_digest`).
3. **Generate** — click *Generate*. The app computes statistics, asks the model
   to write the report (or uses the template fallback), and displays it.
4. **Export** — use the buttons to download the report as **Markdown**,
   **HTML**, or **PDF**.

## API endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET`  | `/health` | Health check. Returns `{"status": "ok", ...}`. |
| `POST` | `/datasets` | Upload a dataset. Multipart `file` field; accepts CSV or JSON; max **10 MB**. Returns an `id`. |
| `GET`  | `/datasets/{id}` | Retrieve a stored dataset (metadata + rows) by `id`. |
| `GET`  | `/templates` | List available report templates. Returns `{"templates": [...]}`. |
| `POST` | `/reports` | Generate a report. Body: `{"dataset_id": "...", "template_name": "..."}`. Returns an `id` and the report `content`. |
| `GET`  | `/reports/{id}/export?format=md\|html\|pdf` | Export a generated report. `format` is one of `md`, `html`, or `pdf`. |

> **Note on PDF:** the `pdf` export is a scaffolding stub. It currently returns
> the report **as HTML** (so the "Export PDF" button works), not a real rendered
> PDF. A production build would render a true PDF here (e.g. with WeasyPrint).

## Testing

Run the test suite with:

```bash
pytest
```

All tests run **fully offline** — no API key or network access is required. The
test suite forces the AI call to fail so the code paths use the deterministic
template fallback, which means the AI call degrades gracefully and tests stay
fast and reliable.

## Security notes

- **API key stays local.** Your `GEMINI_API_KEY` lives only in `.env`, which is
  gitignored and never committed.
- **Uploads are untrusted.** Files you upload are parsed defensively; only CSV
  and JSON are accepted, and oversized files are rejected.
- **Only computed statistics are sent to the model.** Raw row data is never
  forwarded to Gemini — just the aggregate numbers (sum, avg, min, max, counts).
- **Model output is treated as untrusted.** Generated report text is rendered
  safely and is not executed or blindly trusted as code.

## Project layout

```
ai-report-studio/
├── main.py              # FastAPI app: endpoints, report generation, export
├── ai.py                # Gemini model wrapper (generate_report)
├── stats.py             # Summary statistics computation (the "facts")
├── app.js               # Frontend controller (calls the API via fetch)
├── index.html           # Frontend page (served at / by the backend)
├── style.css            # Frontend styling
├── templates/           # Report templates (*.txt)
│   ├── executive_summary.txt
│   ├── incident_report.txt
│   └── weekly_digest.txt
├── tests/               # pytest test suite (all offline)
├── uploads/             # Gitignored scratch dir (kept for layout; runtime state is in-memory)
├── requirements.txt     # Python dependencies
├── .env.example         # Template for your local .env
└── .gitignore
```

> **Notes / limitations:** Data and generated reports are held **in memory**
> only (no database), so they reset when the server restarts. There is **no
> authentication** — this is intended for local/demo use. PDF export is a stub
> (returns HTML).
