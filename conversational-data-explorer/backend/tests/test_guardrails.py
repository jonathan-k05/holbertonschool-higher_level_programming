import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from guardrails import validate_sql, GuardrailViolation


# ---------------------------------------------------------------------------
# These are the adversarial cases the project spec explicitly calls out.
# Do not weaken these tests to make them pass.
# ---------------------------------------------------------------------------

def test_blocks_delete_all_users():
    with pytest.raises(GuardrailViolation):
        validate_sql("delete all users")


def test_blocks_drop_table():
    with pytest.raises(GuardrailViolation):
        validate_sql("DROP TABLE orders")


def test_blocks_stacked_statements():
    with pytest.raises(GuardrailViolation):
        validate_sql("SELECT * FROM orders; DROP TABLE orders;")


def test_blocks_stacked_statements_no_trailing_semicolon():
    with pytest.raises(GuardrailViolation):
        validate_sql("SELECT * FROM orders; DELETE FROM orders")


def test_blocks_insert():
    with pytest.raises(GuardrailViolation):
        validate_sql("INSERT INTO orders (id) VALUES (1)")


def test_blocks_update():
    with pytest.raises(GuardrailViolation):
        validate_sql("UPDATE customers SET name = 'x'")


def test_blocks_alter():
    with pytest.raises(GuardrailViolation):
        validate_sql("ALTER TABLE orders ADD COLUMN hacked TEXT")


def test_blocks_empty_sql():
    with pytest.raises(GuardrailViolation):
        validate_sql("")


def test_blocks_write_hidden_in_cte():
    with pytest.raises(GuardrailViolation):
        validate_sql("WITH x AS (DELETE FROM orders RETURNING *) SELECT * FROM x")


def test_comment_smuggling_is_neutralised_not_leaked():
    # The write attempt lives inside a comment. It must be stripped, and
    # the remaining statement must still be a plain, safe SELECT.
    result = validate_sql("SELECT * FROM orders -- ; DELETE FROM orders")
    assert "DELETE" not in result.upper()
    assert result.upper().startswith("SELECT")


# ---------------------------------------------------------------------------
# Things that SHOULD be allowed to run.
# ---------------------------------------------------------------------------

def test_allows_plain_select():
    result = validate_sql("SELECT * FROM orders")
    assert result.upper().startswith("SELECT")
    assert "LIMIT" in result.upper()


def test_adds_default_limit_when_missing():
    result = validate_sql("SELECT * FROM customers")
    assert "LIMIT 200" in result


def test_keeps_reasonable_existing_limit():
    result = validate_sql("SELECT * FROM customers LIMIT 10")
    assert "LIMIT 10" in result


def test_clamps_oversized_limit():
    result = validate_sql("SELECT * FROM customers LIMIT 999999")
    assert "LIMIT 1000" in result


def test_strips_markdown_fences():
    result = validate_sql("```sql\nSELECT * FROM orders\n```")
    assert result.upper().startswith("SELECT")


def test_case_insensitive_select():
    result = validate_sql("select * from orders")
    assert result.lower().startswith("select")
