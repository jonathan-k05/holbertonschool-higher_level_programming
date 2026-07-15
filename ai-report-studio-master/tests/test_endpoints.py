import unittest.mock as mock

from fastapi.testclient import TestClient

from main import app, reports_store

client = TestClient(app)


def test_upload_csv_file():
    csv_content = b"name,value\nAlice,100\nBob,200\nCharlie,300"
    response = client.post(
        "/datasets",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["columns"] == ["name", "value"]
    assert data["row_count"] == 3
    assert data["filename"] == "data.csv"
    assert "id" in data


def test_upload_json_file():
    json_content = b'[{"name":"Alice","value":100},{"name":"Bob","value":200}]'
    response = client.post(
        "/datasets",
        files={"file": ("data.json", json_content, "application/json")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["columns"] == ["name", "value"]
    assert data["row_count"] == 2


def test_upload_invalid_file_type():
    response = client.post(
        "/datasets",
        files={"file": ("data.txt", b"some text", "text/plain")},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Only CSV and JSON files are supported"}


def test_upload_uppercase_extension():
    csv_content = b"name,value\nAlice,100\nBob,200"
    response = client.post(
        "/datasets",
        files={"file": ("TEST.CSV", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["columns"] == ["name", "value"]
    assert data["row_count"] == 2
    assert data["filename"] == "TEST.CSV"


def test_upload_malformed_csv():
    # A single field larger than csv's field-size limit triggers csv.Error,
    # exercising the safe 400 path (csv.DictReader is otherwise lenient).
    response = client.post(
        "/datasets",
        files={"file": ("data.csv", b"a\n" + b"x" * 140000, "text/csv")},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed to parse CSV file"}


def test_upload_malformed_json():
    response = client.post(
        "/datasets",
        files={"file": ("data.json", b"{not valid json", "application/json")},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed to parse JSON file"}


def test_upload_json_object_not_array():
    response = client.post(
        "/datasets",
        files={"file": ("data.json", b'{"a":1}', "application/json")},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "JSON must be an array of objects"}


def test_upload_too_large():
    payload = b"x" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/datasets",
        files={"file": ("big.csv", payload, "text/csv")},
    )
    assert response.status_code == 413
    assert response.json() == {"detail": "File too large (max 10 MB)"}


def test_json_columns_union():
    json_content = b'[{"a":1,"b":2},{"a":3,"c":4}]'
    response = client.post(
        "/datasets",
        files={"file": ("data.json", json_content, "application/json")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["columns"] == ["a", "b", "c"]
    assert data["row_count"] == 2


def test_get_dataset_by_id():
    csv_content = b"name,value\nAlice,100\nBob,200\nCharlie,300"
    upload = client.post(
        "/datasets",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert upload.status_code == 200
    file_id = upload.json()["id"]

    response = client.get(f"/datasets/{file_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == file_id
    assert data["filename"] == "data.csv"
    assert data["columns"] == ["name", "value"]
    assert len(data["rows"]) == 3
    assert data["rows"][0]["name"] == "Alice"


def test_get_nonexistent_dataset():
    response = client.get("/datasets/nonexistent-id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Dataset not found"}


def test_get_templates():
    response = client.get("/templates")
    assert response.status_code == 200
    data = response.json()
    assert "templates" in data
    assert isinstance(data["templates"], list)
    names = [t["name"] for t in data["templates"]]
    assert "weekly_digest" in names
    assert "executive_summary" in names
    assert "incident_report" in names


def test_get_specific_template_content():
    response = client.get("/templates")
    assert response.status_code == 200
    data = response.json()
    weekly = next(
        (t for t in data["templates"] if t["name"] == "weekly_digest"), None
    )
    assert weekly is not None
    assert "Weekly Digest Report" in weekly["content"]
    assert "{total_records}" in weekly["content"]


def test_generate_report():
    csv_content = b"name,sales\nAlice,100\nBob,200\nCharlie,150"
    upload = client.post(
        "/datasets",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert upload.status_code == 200
    dataset_id = upload.json()["id"]

    response = client.post(
        "/reports",
        json={"dataset_id": dataset_id, "template_name": "weekly_digest"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "content" in data
    assert "Weekly Digest Report" in data["content"]
    assert any(
        v in data["content"] for v in ("100", "200", "150")
    )


def test_generate_report_invalid_dataset():
    response = client.post(
        "/reports",
        json={"dataset_id": "x", "template_name": "weekly_digest"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Dataset not found"}


def test_generate_report_invalid_template():
    csv_content = b"name,sales\nAlice,100\nBob,200\nCharlie,150"
    upload = client.post(
        "/datasets",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert upload.status_code == 200
    dataset_id = upload.json()["id"]

    response = client.post(
        "/reports",
        json={"dataset_id": dataset_id, "template_name": "nope"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Template 'nope' not found"}


def test_generate_report_fills_placeholders():
    csv_content = b"name,sales\nAlice,100\nBob,200"
    upload = client.post(
        "/datasets",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert upload.status_code == 200
    dataset_id = upload.json()["id"]

    response = client.post(
        "/reports",
        json={"dataset_id": dataset_id, "template_name": "executive_summary"},
    )
    assert response.status_code == 200
    data = response.json()
    content = data["content"]
    assert "Executive Summary" in content
    # "100" must not remain as a leftover placeholder like "{100}"
    assert "{100}" not in content
    # nested placeholders like {sum_sales} must be resolved, not left raw
    assert "{sum_" not in content


def test_generate_report_no_numeric_column():
    csv_content = b"name,region\nAlice,North\nBob,South"
    upload = client.post(
        "/datasets",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert upload.status_code == 200
    dataset_id = upload.json()["id"]

    response = client.post(
        "/reports",
        json={"dataset_id": dataset_id, "template_name": "weekly_digest"},
    )
    assert response.status_code == 200
    data = response.json()
    content = data["content"]
    # Graceful handling of a dataset with no numeric column: the numeric
    # column placeholder resolves to "(none)" (or leftover braces to "N/A").
    assert ("(none)" in content) or ("N/A" in content)


def test_generate_report_incident_template():
    csv_content = b"name,sales\nAlice,100\nBob,200"
    upload = client.post(
        "/datasets",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert upload.status_code == 200
    dataset_id = upload.json()["id"]

    response = client.post(
        "/reports",
        json={"dataset_id": dataset_id, "template_name": "incident_report"},
    )
    assert response.status_code == 200
    data = response.json()
    content = data["content"]
    assert "Incident Report" in content
    assert "deviation" in content.lower()


def test_generate_report_missing_keys():
    response = client.post("/reports", json={})
    assert response.status_code == 400
    assert "required" in response.json()["detail"]


def test_generate_report_traversal_rejected():
    csv_content = b"name,sales\nAlice,100\nBob,200"
    upload = client.post(
        "/datasets",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert upload.status_code == 200
    dataset_id = upload.json()["id"]

    response = client.post(
        "/reports",
        json={"dataset_id": dataset_id, "template_name": "../etc/passwd"},
    )
    assert response.status_code == 400
    assert "Invalid template name" in response.json()["detail"]


def _generate_report_id():
    """Upload a CSV and generate a weekly_digest report, returning its id."""
    csv_content = b"name,sales\nAlice,100\nBob,200\nCharlie,150"
    upload = client.post(
        "/datasets",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert upload.status_code == 200
    dataset_id = upload.json()["id"]

    response = client.post(
        "/reports",
        json={"dataset_id": dataset_id, "template_name": "weekly_digest"},
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_export_report_markdown():
    report_id = _generate_report_id()
    response = client.get(f"/reports/{report_id}/export?format=md")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "Weekly Digest Report" in response.text


def test_export_report_html():
    report_id = _generate_report_id()
    response = client.get(f"/reports/{report_id}/export?format=html")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    # With markdown installed, the content must actually be converted to HTML,
    # not left as plain text inside the <pre> fallback.
    assert ("<p>" in response.text) or ("<pre>" in response.text)
    assert "text/html" in response.headers["content-type"]


def test_export_report_pdf():
    report_id = _generate_report_id()
    response = client.get(f"/reports/{report_id}/export?format=pdf")
    assert response.status_code == 200
    # pdf is scaffolding: it returns HTML (so the frontend "Export PDF" button
    # works) rather than a real application/pdf document.
    assert response.headers["content-type"].startswith("text/html")
    assert "content-disposition" in response.headers
    assert "report_" in response.headers["content-disposition"]


def test_export_report_content_disposition():
    report_id = _generate_report_id()
    response = client.get(f"/reports/{report_id}/export?format=md")
    assert response.status_code == 200
    assert "content-disposition" in response.headers
    cd = response.headers["content-disposition"]
    assert "report_" in cd
    assert ".md" in cd


def test_export_report_unsupported_format():
    report_id = _generate_report_id()
    response = client.get(f"/reports/{report_id}/export?format=txt")
    assert response.status_code == 400
    assert response.json() == {"detail": "Unsupported format: txt"}


def test_export_report_not_found():
    response = client.get("/reports/doesnotexist/export")
    assert response.status_code == 404
    assert response.json() == {"detail": "Report not found"}


def test_reports_store_populated():
    csv_content = b"name,sales\nAlice,100\nBob,200\nCharlie,150"
    upload = client.post(
        "/datasets",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert upload.status_code == 200
    dataset_id = upload.json()["id"]

    response = client.post(
        "/reports",
        json={"dataset_id": dataset_id, "template_name": "weekly_digest"},
    )
    assert response.status_code == 200
    data = response.json()
    report_id = data["id"]
    assert report_id in reports_store
    assert reports_store[report_id]["content"] == data["content"]


def test_generate_report_uses_ai_when_available():
    csv_content = b"name,sales\nAlice,100\nBob,200\nCharlie,150"
    ds = client.post("/datasets", files={"file": ("data.csv", csv_content, "text/csv")}).json()["id"]
    with mock.patch("main.ai_generate_report", return_value="AI WROTE THIS REPORT"):
        resp = client.post("/reports", json={"dataset_id": ds, "template_name": "weekly_digest"})
    assert resp.status_code == 200
    assert resp.json()["content"] == "AI WROTE THIS REPORT"


def test_generate_report_falls_back_when_ai_fails():
    csv_content = b"name,sales\nAlice,100\nBob,200\nCharlie,150"
    ds = client.post("/datasets", files={"file": ("data.csv", csv_content, "text/csv")}).json()["id"]
    with mock.patch("main.ai_generate_report", side_effect=Exception("boom")):
        resp = client.post("/reports", json={"dataset_id": ds, "template_name": "weekly_digest"})
    assert resp.status_code == 200
    content = resp.json()["content"]
    # Falls back to the templated report containing the stats.
    assert "Weekly Digest Report" in content
    assert "100" in content


def test_serve_index():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "AI Report Studio" in resp.text


def test_serve_static_assets():
    assert client.get("/app.js").status_code == 200
    assert client.get("/style.css").status_code == 200


def test_cors_allows_file_origin_on_upload():
    resp = client.post(
        "/datasets",
        files={"file": ("t.csv", b"name,sales\nAlice,100\nBob,200", "text/csv")},
        headers={"Origin": "null"},
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "null"


def test_cors_preflight_for_reports():
    resp = client.options(
        "/reports",
        headers={
            "Origin": "null",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "null"
    assert "POST" in (resp.headers.get("access-control-allow-methods") or "")
