"""
guardrails.py
Safety checks applied to every SQL statement BEFORE it touches the database.

Rule of the project: a question can only ever result in ONE read-only
SELECT statement. Nothing else is allowed to run, no matter what the
model returns and no matter what the user's question says.
"""

import re
import sqlparse

# Statement types that must never run, whatever the model proposes.
FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "GRANT", "REVOKE", "ATTACH", "DETACH",
    "PRAGMA", "VACUUM", "REINDEX", "EXEC", "EXECUTE", "CALL",
]

DEFAULT_ROW_LIMIT = 200
MAX_ROW_LIMIT = 1000


class GuardrailViolation(Exception):
    """Raised when a proposed SQL statement fails a safety check."""
    def __init__(self, reason: str, sql: str = ""):
        self.reason = reason
        self.sql = sql
        super().__init__(reason)


def _strip_wrapping(sql: str) -> str:
    """Remove markdown code fences / stray whitespace the model might add."""
    sql = sql.strip()
    sql = re.sub(r"^```(sql)?", "", sql, flags=re.IGNORECASE).strip()
    sql = re.sub(r"```$", "", sql).strip()
    return sql


def _strip_comments(sql: str) -> str:
    """
    Remove SQL comments using sqlparse (handles -- and /* */ correctly,
    unlike a naive string split which breaks on comments inside strings).
    """
    return sqlparse.format(sql, strip_comments=True).strip()


def _split_statements(sql: str):
    """Split into individual statements, dropping empty trailing pieces."""
    raw_statements = sqlparse.split(sql)
    return [s.strip() for s in raw_statements if s.strip() and s.strip() != ";"]


def validate_sql(sql: str) -> str:
    """
    Validate a proposed SQL string against the safety policy.
    Returns the single, safe, LIMIT-bounded SQL statement to execute.
    Raises GuardrailViolation if the statement is not allowed.
    """
    if not sql or not sql.strip():
        raise GuardrailViolation("Empty SQL was returned by the model.", sql)

    cleaned = _strip_wrapping(sql)
    cleaned = _strip_comments(cleaned)

    if not cleaned.strip():
        raise GuardrailViolation(
            "SQL was empty after removing comments (nothing left to run).", sql
        )

    # --- Rule 1: exactly one statement ---
    statements = _split_statements(cleaned)
    if len(statements) == 0:
        raise GuardrailViolation("No statement found.", sql)
    if len(statements) > 1:
        raise GuardrailViolation(
            "Multiple SQL statements detected. Only one statement is allowed.",
            sql,
        )

    statement = statements[0].rstrip(";").strip()
    parsed = sqlparse.parse(statement)
    if not parsed:
        raise GuardrailViolation("Could not parse SQL.", sql)

    stmt_type = parsed[0].get_type()  # e.g. 'SELECT', 'INSERT', 'UNKNOWN'

    # --- Rule 2: must start with SELECT ---
    first_token = statement.strip().split(None, 1)[0].upper() if statement.strip() else ""
    if stmt_type != "SELECT" or first_token != "SELECT":
        raise GuardrailViolation(
            f"Only SELECT statements are allowed (got: {stmt_type or first_token}).",
            sql,
        )

    # --- Rule 3: no forbidden keywords anywhere in the statement ---
    # Catches injected sub-clauses too, e.g. a SELECT that smuggles a
    # CTE calling a write (WITH ... AS (DELETE ...) SELECT ...).
    upper_statement = statement.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_statement):
            raise GuardrailViolation(
                f"Forbidden keyword '{keyword}' found in statement.", sql
            )

    # --- Rule 4: no semicolons left inside (stacked statement smuggling) ---
    if ";" in statement:
        raise GuardrailViolation(
            "Stray semicolon found inside statement.", sql
        )

    # --- Rule 5: enforce a LIMIT ---
    statement = _enforce_limit(statement)

    return statement


def _enforce_limit(statement: str) -> str:
    """
    Add a LIMIT if none is present. If a LIMIT is present but above the
    hard cap, clamp it down.
    """
    match = re.search(r"\bLIMIT\s+(\d+)\b", statement, flags=re.IGNORECASE)
    if match:
        current_limit = int(match.group(1))
        if current_limit > MAX_ROW_LIMIT:
            statement = (
                statement[: match.start(1)]
                + str(MAX_ROW_LIMIT)
                + statement[match.end(1):]
            )
        return statement

    return f"{statement} LIMIT {DEFAULT_ROW_LIMIT}"
