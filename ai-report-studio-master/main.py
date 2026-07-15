import csv
import glob
import html
import io
import json
import os
import re
from datetime import date

import uuid

from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from stats import compute_summary_stats
from ai import generate_report as ai_generate_report

app = FastAPI(title="AI Report Studio")

# Allow the frontend to call the API whether it is served from this backend
# (http://localhost:8000 / http://127.0.0.1:8000) or opened directly as a
# file:// page. Local single-user dev tool, so localhost + the "null" (file://)
# origin are permitted.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "null",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

datasets = {}
reports_store = {}


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI Report Studio is running"}


@app.post("/datasets")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".csv", ".json")):
        raise HTTPException(
            status_code=400, detail="Only CSV and JSON files are supported"
        )

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413, detail="File too large (max 10 MB)"
        )

    text = content.decode("utf-8")

    if file.filename.lower().endswith(".csv"):
        try:
            reader = csv.DictReader(io.StringIO(text))
            rows = [dict(row) for row in reader]
            columns = list(reader.fieldnames or [])
        except (UnicodeDecodeError, csv.Error) as exc:
            print(f"Failed to parse CSV file: {exc}")
            raise HTTPException(
                status_code=400, detail="Failed to parse CSV file"
            )
    else:  # .json
        try:
            data = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"Failed to parse JSON file: {exc}")
            raise HTTPException(
                status_code=400, detail="Failed to parse JSON file"
            )
        if not isinstance(data, list):
            raise HTTPException(
                status_code=400, detail="JSON must be an array of objects"
            )
        if not all(isinstance(item, dict) for item in data):
            raise HTTPException(
                status_code=400, detail="JSON must be an array of objects"
            )
        if not data:
            rows = []
            columns = []
        else:
            rows = data
            columns = sorted({k for row in rows for k in row.keys()})

    file_id = str(uuid.uuid4())
    datasets[file_id] = {
        "filename": file.filename,
        "content_type": file.content_type,
        "rows": rows,
        "columns": columns,
    }

    return {
        "id": file_id,
        "filename": file.filename,
        "columns": columns,
        "row_count": len(rows),
    }


@app.get("/datasets/{file_id}")
def get_dataset(file_id: str):
    dataset = datasets.get(file_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {
        "id": file_id,
        "filename": dataset["filename"],
        "columns": dataset["columns"],
        "rows": dataset["rows"],
    }


@app.get("/templates")
def get_templates():
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    if not os.path.isdir(templates_dir):
        return {"templates": []}

    results = []
    for path in glob.glob(os.path.join(templates_dir, "*.txt")):
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8") as fh:
            results.append({"name": name, "content": fh.read()})

    results.sort(key=lambda t: t["name"])
    return {"templates": results}


@app.post("/reports")
def generate_report(payload: dict):
    dataset_id = payload.get("dataset_id")
    template_name = payload.get("template_name")

    if not dataset_id or not template_name:
        raise HTTPException(
            status_code=400, detail="dataset_id and template_name are required"
        )

    dataset = datasets.get(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if (
        not template_name
        or "/" in template_name
        or "\\" in template_name
        or ".." in template_name
    ):
        raise HTTPException(status_code=400, detail="Invalid template name")

    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    template_path = os.path.join(templates_dir, f"{template_name}.txt")
    if not os.path.isfile(template_path):
        raise HTTPException(
            status_code=404, detail=f"Template '{template_name}' not found"
        )

    with open(template_path, "r", encoding="utf-8") as fh:
        template_text = fh.read()

    rows = dataset["rows"]
    stats = compute_summary_stats(rows)

    # Primary numeric column = first key in stats (or None if empty).
    primary_column = next(iter(stats), None)

    # Build replacements for every numeric column's aggregate placeholders.
    replacements = {}
    for col, col_stats in stats.items():
        replacements[f"sum_{col}"] = str(col_stats["sum"])
        replacements[f"avg_{col}"] = str(round(col_stats["mean"], 2))
        replacements[f"min_{col}"] = str(col_stats["min"])
        replacements[f"max_{col}"] = str(col_stats["max"])
        replacements[f"current_{col}"] = str(round(col_stats["mean"], 2))
        replacements[f"expected_{col}"] = str(round(col_stats["mean"], 2))

    # Base replacements.
    replacements["date"] = str(date.today())
    replacements["total_records"] = str(len(rows))
    replacements["filename"] = dataset["filename"]
    replacements["deviation_percentage"] = "0"
    replacements["severity_level"] = "Low"

    if primary_column is not None:
        replacements["numeric_column"] = primary_column
    else:
        replacements["numeric_column"] = "(none)"
        # No numeric column: leftover aggregate placeholders are scrubbed to
        # "N/A" below.

    # Two-pass plain string replacement (NOT str.format, which crashes on
    # nested braces like {sum_{numeric_column}}).
    content = template_text.replace("{numeric_column}", replacements["numeric_column"])
    for key, value in replacements.items():
        if key == "numeric_column":
            continue
        content = content.replace(f"{{{key}}}", value)

    # Log any placeholders that were never resolved so missing keys surface.
    unresolved = re.findall(r"\{[^}]*\}", content)
    if unresolved:
        print(f"Warning: unresolved placeholders in report: {unresolved}")

    # Replace any remaining {placeholder} leftovers with N/A to avoid raw braces.
    content = re.sub(r"\{[^}]*\}", "N/A", content)

    # Ask the language model to write the prose, using ONLY the already-computed
    # statistics as facts. Python owns the numbers; the model owns the language.
    # On any failure we keep the templated `content` as a graceful fallback.
    try:
        facts_lines = [
            f"Dataset filename: {dataset['filename']}",
            f"Total records: {len(rows)}",
        ]
        for col, col_stats in stats.items():
            facts_lines.append(
                f"Column '{col}': sum={col_stats['sum']}, "
                f"avg={round(col_stats['mean'], 2)}, "
                f"min={col_stats['min']}, max={col_stats['max']}"
            )
        facts = "\n".join(facts_lines)

        ai_prompt = (
            f"Write a professional report in Markdown in the STYLE of the "
            f"'{template_name}' template.\n\n"
            f"Use ONLY the following dataset facts. Never invent, recompute, or "
            f"estimate any numbers — repeat the provided figures verbatim and "
            f"write the prose around them.\n\n"
            f"DATASET FACTS:\n{facts}\n"
        )

        ai_text = ai_generate_report(ai_prompt)
        if ai_text and ai_text.strip():
            content = ai_text
        else:
            print("AI returned empty content; falling back to templated report")
    except Exception as exc:
        print(f"AI report generation failed; using templated fallback: {exc}")

    report_id = str(uuid.uuid4())
    reports_store[report_id] = {
        "dataset_id": dataset_id,
        "template_name": template_name,
        "content": content,
    }

    return {
        "id": report_id,
        "dataset_id": dataset_id,
        "template_name": template_name,
        "content": content,
    }


@app.get("/reports/{report_id}/export")
def export_report(report_id: str, format: str = "md"):
    report = reports_store.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    if format not in ("md", "html", "pdf"):
        raise HTTPException(
            status_code=400, detail=f"Unsupported format: {format}"
        )

    content = report["content"]

    # File extension used in the Content-Disposition download filename. pdf is
    # served as HTML (see below), so it uses the html extension.
    ext = "md" if format == "md" else "html"
    disposition = f'attachment; filename="report_{report_id}.{ext}"'

    if format == "md":
        return Response(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": disposition},
        )

    # html and pdf both render the markdown content to HTML. NOTE: pdf is a
    # scaffolding stub -- it returns HTML (so the frontend "Export PDF" button
    # works) rather than a real PDF. A production implementation would render a
    # true PDF here using weasyprint (or similar).
    try:
        import markdown

        rendered = markdown.markdown(content)
    except ImportError:
        # Escape the raw content to prevent HTML injection in the fallback.
        rendered = f"<pre>{html.escape(content)}</pre>"

    return Response(
        content=rendered,
        media_type="text/html",
        headers={"Content-Disposition": disposition},
    )


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


@app.get("/style.css")
def serve_style():
    return FileResponse(os.path.join(BASE_DIR, "style.css"))


@app.get("/app.js")
def serve_app_js():
    return FileResponse(os.path.join(BASE_DIR, "app.js"))
