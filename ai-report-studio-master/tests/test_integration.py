from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_full_workflow():
    csv_content = b"month,sales\nJan,10000\nFeb,12000\nMar,11000"
    upload = client.post(
        "/datasets", files={"file": ("sales.csv", csv_content, "text/csv")}
    )
    assert upload.status_code == 200
    dataset_id = upload.json()["id"]

    assert client.get(f"/datasets/{dataset_id}").status_code == 200
    assert len(client.get("/templates").json()["templates"]) >= 3

    report = client.post(
        "/reports", json={"dataset_id": dataset_id, "template_name": "executive_summary"}
    )
    assert report.status_code == 200
    report_id = report.json()["id"]

    exported = client.get(f"/reports/{report_id}/export?format=md")
    assert exported.status_code == 200
    assert "Executive Summary" in exported.text
