"""
nl2sql.py
Turns a plain-English question into SQL (grounded in the live schema),
and turns query results back into a one-sentence written answer.

This file only PROPOSES SQL. It never runs it. guardrails.py decides
whether the proposal is allowed to execute.
"""

import re
from ai import call_model

SQL_SYSTEM_PROMPT = """You are a SQL generator for a read-only analytics tool.

Rules you must always follow:
- Use ONLY the tables and columns given in the schema below. Never invent tables or columns.
- Output EXACTLY ONE SQL statement, and it MUST be a SELECT. Never write INSERT, UPDATE, DELETE, DROP, ALTER, or any statement that changes data.
- Never write more than one statement (no semicolons chaining statements).
- Do not include comments.
- Do not include any explanation, markdown formatting, or code fences. Output raw SQL only.
- If the question cannot be answered with the given schema, output exactly: SELECT 'unanswerable' AS error LIMIT 1

Database schema:
{schema}
"""

ANSWER_SYSTEM_PROMPT = """You write one short, plain-English sentence that answers a
user's question using ONLY the data given to you below. Never invent numbers that are
not present in the data. If the data is empty, say no matching results were found.
Do not mention SQL or databases. Be concise: one sentence."""


def generate_sql(question: str, schema_description: str) -> str:
    system_prompt = SQL_SYSTEM_PROMPT.format(schema=schema_description)
    raw = call_model(system_prompt, question, temperature=0.0)
    return _clean_sql_text(raw)


def _clean_sql_text(raw: str) -> str:
    """Strip markdown fences the model may add despite instructions."""
    text = raw.strip()
    text = re.sub(r"^```(sql)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_answer(question: str, columns, rows) -> str:
    """
    Ask the model for a one-sentence answer grounded only in the actual
    rows returned. If there are no rows, skip the model call entirely
    to guarantee we never hallucinate a number.
    """
    if not rows:
        return "No matching results were found for that question."

    preview_rows = rows[:20]  # keep the prompt small; the table shows the rest
    data_block = _rows_to_text(columns, preview_rows)

    user_prompt = (
        f"Question: {question}\n\n"
        f"Data (columns: {', '.join(columns)}):\n{data_block}"
    )
    return call_model(ANSWER_SYSTEM_PROMPT, user_prompt, temperature=0.0)


def _rows_to_text(columns, rows) -> str:
    lines = [", ".join(columns)]
    for row in rows:
        lines.append(", ".join(str(row.get(c, "")) for c in columns))
    return "\n".join(lines)
