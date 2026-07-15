"""
main.py
FastAPI app: wires together db.py, nl2sql.py, guardrails.py, ai.py.

Endpoints:
  GET  /health    - liveness check
  GET  /schema    - live, introspected schema
  POST /ask       - natural language question -> safe SQL -> answer
  GET  /history   - past Q&A this session
  POST /seed      - (re)seed the sample database
"""

from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
import nl2sql
from guardrails import validate_sql, GuardrailViolation
from ai import AIError

app = FastAPI(title="Conversational Data Explorer")

# The frontend is a static page served separately (or opened as a file),
# so we allow cross-origin calls to the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory history is fine for this project; swap for a DB table if you
# need it to survive a restart.
HISTORY: List[dict] = []


@app.on_event("startup")
def on_startup():
    db.init_db()


# ---------------------------------------------------------------------------
# Schemas (API request/response shapes)
# ---------------------------------------------------------------------------

class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sql: str
    columns: List[str]
    rows: List[dict]
    row_count: int
    is_read_only: bool = True
    timestamp: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/schema")
def schema():
    return db.get_schema_json()


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    schema_description = db.get_schema_description()

    # 1. Ask the model to propose SQL grounded in the real schema.
    try:
        proposed_sql = nl2sql.generate_sql(question, schema_description)
    except AIError as e:
        raise HTTPException(status_code=502, detail=f"Model error: {e}")

    # 2. Guardrails decide whether that SQL is allowed to run. This check
    #    is not optional and cannot be bypassed by anything in `question`
    #    or in the model's output.
    try:
        safe_sql = validate_sql(proposed_sql)
    except GuardrailViolation as e:
        raise HTTPException(
            status_code=422,
            detail=f"Generated SQL was rejected by safety checks: {e.reason}",
        )

    # 3. Run the validated, read-only query.
    try:
        columns, rows = db.run_readonly_query(safe_sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {e}")

    # 4. Turn the actual rows into a one-sentence answer. Never invents
    #    numbers: it only ever sees the rows that came back.
    try:
        answer_text = nl2sql.generate_answer(question, columns, rows)
    except AIError:
        answer_text = "Here are the results (a written summary could not be generated)."

    record = AskResponse(
        question=question,
        answer=answer_text,
        sql=safe_sql,
        columns=columns,
        rows=rows,
        row_count=len(rows),
        is_read_only=True,
        timestamp=datetime.utcnow().isoformat(),
    )
    HISTORY.append(record.model_dump())
    return record


@app.get("/history")
def history():
    return {"history": HISTORY}


@app.post("/seed")
def reseed():
    """Convenience endpoint so a reviewer can reset to a known sample state."""
    import os
    db.engine.dispose()
    if db.DATABASE_URL.startswith("sqlite"):
        path = db.DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(path):
            os.remove(path)
    db.init_db()
    return {"status": "reseeded"}
