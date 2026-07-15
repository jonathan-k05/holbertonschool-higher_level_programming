# AI Report Studio — Code Review

Final review of the completed implementation, against the approved design spec.
Full pytest suite: **45 passed** (runs fully offline; AI degrades gracefully).
Verdict: **SHIP-WITH-NOTES** — every spec requirement is met; no blockers.

## What's done well (spec coverage confirmed)

- **Incremental endpoint flow** matches the spec exactly: `POST /datasets`,
  `GET /datasets/{id}`, `GET /templates`, `POST /reports`, `GET /reports/{id}/export`
  (md / html / pdf).
- **Core principle honored**: the Gemini prompt is built ONLY from
  `compute_summary_stats` output — raw data rows are never sent to the model.
  Python does the math, the model does the language.
- **AI is genuinely wired in**: `/reports` calls `ai.generate_report`, and on any
  failure (no key / offline / API error) falls back to the templated report and
  returns HTTP 200. No raw stack traces reach the client.
- **Security**: `.env` is gitignored and not tracked (only `.env.example` is);
  uploads validated by extension + 10 MB limit and parsed defensively; template
  path-traversal is blocked; the in-app report view uses `textContent` (XSS-safe).
- **Stats are correct**: `stats.py` rejects NaN / inf / bool / None, handles empty
  data and the no-numeric-column case, and unifies CSV-string vs JSON-native types.
- **Tests** cover units, endpoints, the AI abstraction (both success and fallback),
  the frontend, health, and an end-to-end integration flow. The `conftest.py`
  autouse fixture forces the AI fallback so tests are deterministic and never hit
  the network.

## Findings

### F1 — Model output rendered to HTML with raw-HTML passthrough (security-adjacent)
- **Severity:** MINOR
- **Where:** `main.py` — `markdown.markdown(content)` in the html/pdf export path.
- **Issue:** `markdown` passes raw HTML from the (untrusted) model output straight
  through. The export is served as an attachment (downloaded, not rendered inline)
  and the in-app view uses `textContent`, so the normal path is safe. But a user who
  opens the downloaded HTML in a browser could have injected `<script>`/`<img
  onerror>` run in the `localhost:8000` origin.
- **Fix:** sanitize the rendered HTML (e.g. `bleach.clean(...)`) before returning, or
  use a markdown renderer that strips raw HTML. **Worth doing only if the app is ever
  used beyond a single local user.**

### F2 — 10 MB size check happens after the file is fully read
- **Severity:** MINOR
- **Where:** `main.py` — `content = await file.read()` then the length check.
- **Issue:** the upload is buffered into memory before the limit is enforced.
- **Fix:** check `file.size` / `Content-Length` first, or stream with a byte budget.
  Cosmetic at a 10 MB cap. **Optional.**

### F3 — README lists an `uploads/` scratch dir the code never uses
- **Severity:** NIT (doc inaccuracy, fixed)
- **Issue:** the backend stores datasets and reports in memory; `uploads/` exists
  only as a `.gitkeep`. README updated to note this honestly.

### F4 — `google.generativeai` is deprecated
- **Severity:** NIT
- **Issue:** the package is end-of-life (emits a FutureWarning); Google recommends
  `google.genai`. Still functions. **Leave for a later pass.**

### F5 — Redundant `current_`/`expected_` replacement values
- **Severity:** NIT — both equal `avg_{col}`. Harmless duplication. No action.

### F6 — AI prompt sends the template name, not its body
- **Severity:** MINOR (defensible by design)
- **Issue:** the model is told to write "in the style of" the template but never sees
  the template's section layout, so it produces free-form Markdown rather than
  following the skeleton. README frames it as "style of," so it's consistent.
  **Optional polish:** include the template text / headings in the prompt.

### F7 — `/reports` is a synchronous endpoint doing blocking network I/O
- **Severity:** NIT — works via FastAPI's threadpool. Irrelevant at this scale.

### F8 — Upload filename is placed into the model prompt
- **Severity:** NIT (prompt-injection surface, low impact) — the filename is
  user-controlled and included in the facts sent to the model. Impact is low; the
  model cannot reach other data from here. Acceptable to leave.

## Decision

Ship as-is. Only F1 merits follow-up, and only if the app leaves single-user local
use. F2/F3 are cheap polish already partly addressed. F4–F8 are non-blocking notes.
