"""Domain layer: validation plus CRUD operations for contacts."""

from __future__ import annotations

from typing import Any

METHOD_KINDS = ("phone", "email", "wechat", "address", "other")
MAX_METHODS_PER_CONTACT = 30


class ValidationError(ValueError):
    """Raised when the payload sent by a client cannot be stored."""


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def normalise_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalise a contact payload coming from the web layer."""
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")

    name = _clean(payload.get("name"))
    if not name:
        raise ValidationError("Contact name is required.")
    if len(name) > 60:
        raise ValidationError("Contact name must be 60 characters or fewer.")

    methods = []
    for item in payload.get("methods") or []:
        if not isinstance(item, dict):
            raise ValidationError("Each contact method must be an object.")
        kind = _clean(item.get("kind")).lower()
        if kind not in METHOD_KINDS:
            raise ValidationError("Unsupported contact method kind: %s" % kind)
        value = _clean(item.get("value"))
        if not value:
            continue
        methods.append(
            {"kind": kind, "label": _clean(item.get("label")), "value": value}
        )

    if len(methods) > MAX_METHODS_PER_CONTACT:
        raise ValidationError(
            "A contact cannot hold more than %d methods." % MAX_METHODS_PER_CONTACT
        )

    return {
        "name": name,
        "company": _clean(payload.get("company")),
        "title": _clean(payload.get("title")),
        "notes": _clean(payload.get("notes")),
        "is_favorite": 1 if payload.get("is_favorite") else 0,
        "methods": methods,
    }


def _insert_methods(connection, contact_id: int, methods: list[dict[str, Any]]) -> None:
    rows = [
        (contact_id, method["kind"], method["label"], method["value"], index)
        for index, method in enumerate(methods)
    ]
    if rows:
        connection.executemany(
            "INSERT INTO contact_methods (contact_id, kind, label, value, sort_order)"
            " VALUES (?, ?, ?, ?, ?)",
            rows,
        )


def _fetch_methods(connection, contact_ids: list[int]) -> dict[int, list[dict[str, Any]]]:
    if not contact_ids:
        return {}
    placeholders = ",".join("?" for _ in contact_ids)
    rows = connection.execute(
        "SELECT * FROM contact_methods WHERE contact_id IN (%s)"
        " ORDER BY sort_order, id" % placeholders,
        contact_ids,
    ).fetchall()
    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["contact_id"], []).append(
            {
                "id": row["id"],
                "kind": row["kind"],
                "label": row["label"],
                "value": row["value"],
            }
        )
    return grouped


def _to_contact(row, methods: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "company": row["company"],
        "title": row["title"],
        "notes": row["notes"],
        "is_favorite": bool(row["is_favorite"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "methods": methods,
    }


def list_contacts(connection, keyword: str = "", favorite_only: bool = False):
    """Return every contact, with optional keyword and favorite filtering."""
    where = []
    params: list[Any] = []

    keyword = (keyword or "").strip()
    if keyword:
        like = "%" + keyword + "%"
        where.append(
            "(name LIKE ? OR company LIKE ? OR title LIKE ? OR notes LIKE ?"
            " OR id IN (SELECT contact_id FROM contact_methods WHERE value LIKE ?))"
        )
        params.extend([like, like, like, like, like])
    if favorite_only:
        where.append("is_favorite = 1")

    sql = "SELECT * FROM contacts"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY is_favorite DESC, name COLLATE NOCASE ASC"

    rows = connection.execute(sql, params).fetchall()
    grouped = _fetch_methods(connection, [row["id"] for row in rows])
    return [_to_contact(row, grouped.get(row["id"], [])) for row in rows]


def get_contact(connection, contact_id: int):
    row = connection.execute(
        "SELECT * FROM contacts WHERE id = ?", (contact_id,)
    ).fetchone()
    if row is None:
        return None
    methods = _fetch_methods(connection, [contact_id]).get(contact_id, [])
    return _to_contact(row, methods)


def find_contact_by_name(connection, name: str):
    row = connection.execute(
        "SELECT * FROM contacts WHERE name = ? COLLATE NOCASE ORDER BY id LIMIT 1",
        (name,),
    ).fetchone()
    if row is None:
        return None
    return get_contact(connection, row["id"])


def create_contact(connection, payload: dict[str, Any]):
    data = normalise_payload(payload)
    with connection:
        cursor = connection.execute(
            "INSERT INTO contacts (name, company, title, notes, is_favorite)"
            " VALUES (?, ?, ?, ?, ?)",
            (data["name"], data["company"], data["title"], data["notes"], data["is_favorite"]),
        )
        _insert_methods(connection, cursor.lastrowid, data["methods"])
    return get_contact(connection, cursor.lastrowid)


def update_contact(connection, contact_id: int, payload: dict[str, Any]):
    data = normalise_payload(payload)
    with connection:
        connection.execute(
            "UPDATE contacts SET name = ?, company = ?, title = ?, notes = ?,"
            " is_favorite = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (
                data["name"],
                data["company"],
                data["title"],
                data["notes"],
                data["is_favorite"],
                contact_id,
            ),
        )
        connection.execute(
            "DELETE FROM contact_methods WHERE contact_id = ?", (contact_id,)
        )
        _insert_methods(connection, contact_id, data["methods"])
    return get_contact(connection, contact_id)


def delete_contact(connection, contact_id: int) -> bool:
    with connection:
        cursor = connection.execute(
            "DELETE FROM contacts WHERE id = ?", (contact_id,)
        )
    return cursor.rowcount > 0


def set_favorite(connection, contact_id: int, favorite):
    """Set the bookmark flag. Passing None toggles the current value."""
    row = connection.execute(
        "SELECT is_favorite FROM contacts WHERE id = ?", (contact_id,)
    ).fetchone()
    if row is None:
        return None
    value = (0 if row["is_favorite"] else 1) if favorite is None else int(bool(favorite))
    with connection:
        connection.execute(
            "UPDATE contacts SET is_favorite = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (value, contact_id),
        )
    return get_contact(connection, contact_id)


def count_contacts(connection) -> dict[str, int]:
    total = connection.execute("SELECT COUNT(*) AS n FROM contacts").fetchone()["n"]
    favorites = connection.execute(
        "SELECT COUNT(*) AS n FROM contacts WHERE is_favorite = 1"
    ).fetchone()["n"]
    methods = connection.execute(
        "SELECT COUNT(*) AS n FROM contact_methods"
    ).fetchone()["n"]
    return {"contacts": total, "favorites": favorites, "methods": methods}
