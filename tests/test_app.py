"""Automated tests for the address book API (pytest)."""

from __future__ import annotations

import io

import pytest
from openpyxl import Workbook, load_workbook

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    with app.test_client() as test_client:
        yield test_client


def make_contact(name="Alice Chen", favorite=False, methods=None):
    return {
        "name": name,
        "company": "Fuzhou University",
        "title": "Lecturer",
        "notes": "Lab contact",
        "is_favorite": favorite,
        "methods": methods
        if methods is not None
        else [
            {"kind": "phone", "label": "mobile", "value": "13800000001"},
            {"kind": "phone", "label": "office", "value": "0592-0000002"},
            {"kind": "email", "label": "", "value": "alice@example.edu"},
        ],
    }


def test_index_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Address Book" in body
    assert "id=\"contact-form\"" in body


def test_create_and_list_contact(client):
    created = client.post("/api/contacts", json=make_contact())
    assert created.status_code == 201
    contact = created.get_json()
    assert contact["name"] == "Alice Chen"
    assert len(contact["methods"]) == 3

    listing = client.get("/api/contacts").get_json()
    assert listing["stats"]["contacts"] == 1
    assert listing["stats"]["methods"] == 3
    assert listing["contacts"][0]["methods"][0]["kind"] == "phone"


def test_validation_rejects_empty_name(client):
    response = client.post("/api/contacts", json={"name": "   "})
    assert response.status_code == 400
    assert "required" in response.get_json()["error"]


def test_favorite_toggle(client):
    contact = client.post("/api/contacts", json=make_contact()).get_json()
    toggled = client.post(
        "/api/contacts/%d/favorite" % contact["id"], json={"favorite": True}
    ).get_json()
    assert toggled["is_favorite"] is True

    filtered = client.get("/api/contacts?favorite=1").get_json()
    assert len(filtered["contacts"]) == 1

    client.post("/api/contacts/%d/favorite" % contact["id"], json={"favorite": False})
    assert client.get("/api/contacts?favorite=1").get_json()["contacts"] == []


def test_search_matches_contact_methods(client):
    client.post("/api/contacts", json=make_contact())
    client.post("/api/contacts", json=make_contact(name="Bob Liu", methods=[]))

    found = client.get("/api/contacts?q=13800000001").get_json()
    assert [item["name"] for item in found["contacts"]] == ["Alice Chen"]

    found = client.get("/api/contacts?q=Bob").get_json()
    assert [item["name"] for item in found["contacts"]] == ["Bob Liu"]


def test_update_contact_replaces_methods(client):
    contact = client.post("/api/contacts", json=make_contact()).get_json()
    payload = make_contact(name="Alice Chen Updated", favorite=True, methods=[
        {"kind": "wechat", "label": "", "value": "alice_fzu"},
    ])
    updated = client.put("/api/contacts/%d" % contact["id"], json=payload).get_json()
    assert updated["name"] == "Alice Chen Updated"
    assert updated["is_favorite"] is True
    assert [item["kind"] for item in updated["methods"]] == ["wechat"]


def test_delete_contact(client):
    contact = client.post("/api/contacts", json=make_contact()).get_json()
    response = client.delete("/api/contacts/%d" % contact["id"])
    assert response.status_code == 200
    assert client.get("/api/contacts").get_json()["contacts"] == []


def test_export_layout_one_row_per_contact_and_one_column_per_type(client):
    client.post("/api/contacts", json=make_contact())
    client.post("/api/contacts", json=make_contact(name="Bob Liu", methods=[
        {"kind": "email", "label": "", "value": "bob@example.edu"},
    ]))

    response = client.get("/api/export")
    assert response.status_code == 200
    workbook = load_workbook(io.BytesIO(response.data))
    sheet = workbook.active
    headers = [cell.value for cell in sheet[1]]
    assert headers[:5] == ["Name", "Company", "Title", "Notes", "Favorite"]
    assert headers[5:7] == ["Phone 1", "Phone 2"]
    assert "Email 1" in headers
    assert sheet.max_row == 3
    assert sheet["A2"].value == "Alice Chen"


def test_import_round_trip(client):
    client.post("/api/contacts", json=make_contact())
    exported = client.get("/api/export").data
    assert client.delete("/api/contacts/1").status_code == 200

    response = client.post(
        "/api/import",
        data={"file": (io.BytesIO(exported), "contacts.xlsx")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert response.get_json()["imported"] == 1

    restored = client.get("/api/contacts").get_json()["contacts"][0]
    assert restored["name"] == "Alice Chen"
    assert len(restored["methods"]) == 3


def test_import_merges_existing_contact(client):
    client.post("/api/contacts", json=make_contact())
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Name", "Company", "Favorite", "Phone 1", "WeChat 1"])
    sheet.append(["Alice Chen", "Fuzhou University", "Yes", "13800000009", "alice_new"])
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    result = client.post(
        "/api/import",
        data={"file": (buffer, "more.xlsx")},
        content_type="multipart/form-data",
    ).get_json()
    assert result["merged"] == 1

    contact = client.get("/api/contacts").get_json()["contacts"][0]
    values = sorted(item["value"] for item in contact["methods"])
    assert "13800000009" in values
    assert "alice_new" in values


def test_import_skips_rows_without_name(client):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Name", "Phone 1"])
    sheet.append(["", "13800000000"])
    sheet.append(["Grace Wang", "13800000005"])
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    result = client.post(
        "/api/import",
        data={"file": (buffer, "contacts.xlsx")},
        content_type="multipart/form-data",
    ).get_json()
    assert result["imported"] == 1
    assert result["skipped"] == 1


def test_import_rejects_unknown_columns(client):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Foo", "Bar"])
    sheet.append(["x", "y"])
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    response = client.post(
        "/api/import",
        data={"file": (buffer, "bad.xlsx")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert "recognizable columns" in response.get_json()["error"]
